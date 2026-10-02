#!/usr/bin/env python3
"""Consolidate local skills into a shared Git repository without losing originals."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parents[1]
ROOTS = ('.agents/skills', '.claude/skills', '.codex/skills')

def digest(path):
    path = path.resolve(strict=True)
    records = [['D', '', stat.S_IMODE(path.stat().st_mode)]]
    for p in sorted(path.rglob('*')):
        rel = p.relative_to(path).as_posix()
        if p.is_symlink():
            records.append(['L', rel, os.readlink(p)])
        elif p.is_file():
            records.append(['F', rel, stat.S_IMODE(p.stat().st_mode), hashlib.sha256(p.read_bytes()).hexdigest()])
        elif p.is_dir():
            records.append(['D', rel, stat.S_IMODE(p.stat().st_mode)])
    return hashlib.sha256(json.dumps(records, ensure_ascii=True, separators=(',', ':')).encode()).hexdigest()

def validate_location(home, repo):
    roots = [home / root for root in ROOTS]
    if repo == home or any(repo == root or root in repo.parents or
                           repo == root.resolve() or root.resolve() in repo.parents for root in roots):
        raise ValueError('Shared repository must be outside all discovery roots.')

def validate_source(source, repo):
    source = source.resolve(strict=True)
    if repo == source or source in repo.parents:
        raise ValueError(f'Repository would be nested inside source: {source}')
    for p in source.rglob('*'):
        if p.is_symlink():
            target = p.resolve(strict=True)
            if os.path.isabs(os.readlink(p)) or (target != source and source not in target.parents):
                raise ValueError(f'Unsupported absolute/external resource symlink; preserve its dependency explicitly first: {p}')

def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as f:
            temporary = Path(f.name)
            json.dump(data, f, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()

def valid_git_repository(repo):
    if not (repo / '.git').exists():
        return False
    result = subprocess.run(['git', '-C', str(repo), 'rev-parse', '--show-toplevel'], capture_output=True, text=True)
    return result.returncode == 0 and Path(result.stdout.strip()).resolve() == repo.resolve()

def build_plan(home, repo, package=PACKAGE):
    validate_location(home, repo)
    sources, links, by_hash, shared = [], [], {}, {}
    for root in ROOTS:
        host = 'claude' if root.startswith('.claude') else 'codex'
        directory = home / root
        if not directory.exists():
            continue
        for source in sorted(directory.iterdir()):
            if source.name.startswith('.'):
                continue
            if not source.is_dir():
                raise ValueError(f'Unexpected non-directory skill entry: {source}')
            if source.name in ('codecopilot', 'codecopilotlight'):
                raise ValueError(f'Existing {source.name} needs explicit conflict resolution: {source}')
            validate_source(source, repo)
            fingerprint = digest(source)
            if source.name == 'synced':
                destination = f'managed/{host}/synced'
            elif fingerprint in by_hash:
                destination = by_hash[fingerprint]
            elif source.name == 'skill0':
                destination = 'vendor/skill0' if 'skill0' not in shared else f'variants/{host}/skill0'
            elif source.name not in shared:
                destination = f'skills/{source.name}'
            else:
                destination = f'variants/{host}/{source.name}'
            if any(x['destination'] == destination and x['digest'] != fingerprint for x in sources):
                raise ValueError(f'Conflicting migration destination: {destination}')
            sources.append({'source': str(source), 'destination': destination, 'digest': fingerprint,
                            'upstream_link': os.readlink(source) if source.is_symlink() else None})
            by_hash[fingerprint] = destination
            if source.name != 'synced':
                shared.setdefault(source.name, destination)
            links.append({'path': str(source.relative_to(home)), 'target': destination})
    for name in ('codecopilot', 'codecopilotlight'):
        source = package / 'skills' / name
        validate_source(source, repo)
        sources.append({'source': str(source), 'destination': f'skills/{name}', 'digest': digest(source), 'upstream_link': None})
        shared[name] = f'skills/{name}'
    # Fill missing shared personal skills for both modern Codex and Claude Code.
    existing = {x['path'] for x in links}
    for root in ROOTS[:2]:
        for name, target in shared.items():
            relative = f'{root}/{name}'
            if relative not in existing:
                links.append({'path': relative, 'target': target}); existing.add(relative)
    return {'schema': 3, 'digest_algorithm': 'sha256-records-v3', 'home': str(home), 'repository': str(repo), 'sources': sources, 'links': links,
            'preserved_managed_locations': ['~/.codex/skills/.system', '~/.codex/plugins', '~/.claude/plugins'],
            'notes': ['Cloud synced trees retain separate host variants and may be updated by their host.',
                      'skill0 is a snapshot; original x-cmd installation remains intact. Reinstallation by x-cmd may replace links.',
                      'Git is local only. No remote repository or publishing is performed.']}

def verify(home, repo):
    manifest = json.loads((repo / 'manifest.json').read_text())
    problems = []
    for link in manifest['links']:
        p, target = home / link['path'], repo / link['target']
        if not p.is_symlink() or not target.is_dir() or p.resolve() != target.resolve():
            problems.append(str(p))
    return problems

def restore_entries(journal):
    # Preflight the entire restore: never unlink a path another process replaced.
    for entry in journal:
        p = Path(entry['path'])
        if not p.is_symlink() or os.readlink(p) != entry['installed_link']:
            raise ValueError(f'Refusing to replace changed path: {p}')
    for entry in reversed(journal):
        p = Path(entry['path']); p.unlink()
        if entry['backup']:
            Path(entry['backup']).rename(p)
    return len(journal)

def restore(backup):
    return restore_entries(json.loads((backup / 'links.json').read_text()))

def apply(home, repo, package=PACKAGE):
    validate_location(home, repo)
    if (repo / 'manifest.json').exists():
        if not valid_git_repository(repo):
            raise ValueError(f'Migration destination is not an initialized Git repository: {repo}')
        problems = verify(home, repo)
        if problems:
            raise ValueError('Existing migration has changed links; inspect before updating: ' + ', '.join(problems))
        for name in ('codecopilot', 'codecopilotlight'):
            if digest(package / 'skills' / name) != digest(repo / 'skills' / name):
                raise ValueError(f'{name} differs from the shared copy; review and synchronize explicitly, not by overwriting.')
        return {'status': 'already-installed', 'repository': str(repo)}
    if repo.exists() and any(repo.iterdir()):
        raise ValueError(f'Destination must be new or empty: {repo}')
    plan = build_plan(home, repo, package)
    repo.mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', 'init', '-q', str(repo)], check=True)
    for source in plan['sources']:
        dest = repo / source['destination']
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(Path(source['source']).resolve(), dest, symlinks=True)
        if digest(dest) != source['digest']:
            raise ValueError(f'Copied bytes differ: {dest}')
    atomic_json(repo / 'manifest.json', plan)
    (repo / '.gitignore').write_text('.DS_Store\n__pycache__/\n*.pyc\n.env\n.env.*\n.local/\n')
    (repo / 'README.md').write_text('''# Agent Skills

Shared local skills repository for Codex and Claude Code.

- `skills/`: shared personal skills, including CodeCopilot and CodeCopilot Light.
- `variants/`: existing host-specific differences, preserved without rewriting.
- `managed/`: host-specific synced skill trees; the original host may update them.
- `vendor/skill0`: an x-cmd skill0 snapshot; upstream remains in its managed install.
- `manifest.json`: original locations, byte hashes, sources and installed links.

Codex reads the links under `~/.agents/skills`; Claude Code reads
`~/.claude/skills`. Legacy Codex entries are also linked where they already existed.
System and plugin skills remain managed by their applications.

Claude Code: `/codecopilot <task>`, `/codecopilotlight <task>`.
Codex: `$codecopilot <task>`, `$codecopilotlight <task>` or `/skills`.

Neither skill activates without an explicit invocation.
CodeCopilot is reviewed development; Light is direct development with necessary tests
and no independent QA. Skills do not change the host model. The package QA default
is pi / openai-codex / gpt-6-astra / medium unless overridden.

This repository is local. It has not been published. Imported content retains its
original license and provenance; no blanket license is asserted over third-party skills.

Edit the shared personal skills here. For CodeCopilot package updates, compare the source
package and this copy before replacing it; the installer refuses conflicting updates.
Cloud sync or x-cmd installers can replace links: run the source package's
`scripts/manage_skills.py verify --repo PATH` after those tools update.
''')
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup = home / '.local/share/agent-skills-backups' / stamp
    backup.mkdir(parents=True)
    journal = []
    try:
        # Recheck source trees before moving them in case cloud sync raced the copy.
        for source in plan['sources']:
            if digest(Path(source['source'])) != source['digest']:
                raise ValueError(f'Source changed during migration: {source["source"]}')
        for link in plan['links']:
            p = home / link['path']; target = repo / link['target']; p.parent.mkdir(parents=True, exist_ok=True)
            saved = None
            if p.exists() or p.is_symlink():
                saved = backup / link['path']; saved.parent.mkdir(parents=True, exist_ok=True); p.rename(saved)
            try:
                p.symlink_to(target, target_is_directory=True)
            except Exception:
                if saved:
                    saved.rename(p)
                raise
            journal.append({'path': str(p), 'installed_link': str(target), 'backup': str(saved) if saved else None})
            atomic_json(backup / 'links.json', journal)
        problems = verify(home, repo)
        if problems:
            raise ValueError('Link verification failed: ' + ', '.join(problems))
        atomic_json(repo / '.local/migration.json', {'backup': str(backup), 'links': len(journal)})
    except Exception:
        if journal:
            restore_entries(journal)
        raise
    return {'status': 'installed', 'repository': str(repo), 'backup': str(backup), 'links': len(journal),
            'sources': len(plan['sources'])}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['plan', 'apply', 'verify', 'restore'])
    parser.add_argument('--repo', type=Path)
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--backup', type=Path)
    args = parser.parse_args(); home = args.home.expanduser().resolve()
    try:
        if args.action == 'restore':
            if not args.backup:
                parser.error('restore requires --backup')
            result = {'restored_links': restore(args.backup.expanduser().resolve())}
        else:
            if not args.repo:
                parser.error('--repo is required')
            repo = args.repo.expanduser().resolve()
            validate_location(home, repo)
            if args.action == 'plan':
                result = build_plan(home, repo)
            elif args.action == 'apply':
                result = apply(home, repo)
            else:
                failures = verify(home, repo); result = {'valid': not failures, 'broken_links': failures}
                if failures:
                    print(json.dumps(result, indent=2)); return 1
        print(json.dumps(result, indent=2)); return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f'error: {exc}', file=sys.stderr); return 1

if __name__ == '__main__':
    sys.exit(main())
