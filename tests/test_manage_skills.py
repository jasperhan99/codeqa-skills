import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import subprocess

SPEC = importlib.util.spec_from_file_location('manage', Path(__file__).resolve().parents[1] / 'scripts/manage_skills.py')
manage = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(manage)

class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.home = self.root / 'home'; self.repo = self.root / 'repo'; self.package = self.root / 'package'
        self.home.mkdir()
        for name in ('codecopilot', 'codecopilotlight'):
            self.skill(self.package / 'skills' / name, name)
        self.skill(self.home / '.agents/skills/custom', 'codex version')
        self.skill(self.home / '.claude/skills/custom', 'claude version')
        self.skill(self.home / '.codex/skills/.system/keep', 'system')
        upstream = self.root / 'upstream'; self.skill(upstream, 'vendor'); (upstream / 'references').mkdir(); (upstream / 'references/example.txt').write_text('resource')
        (self.home / '.agents/skills/skill0').symlink_to(upstream, target_is_directory=True)
        self.skill(self.home / '.agents/skills/synced/account/memo', 'codex cloud')
        self.skill(self.home / '.claude/skills/synced/account/memo', 'claude cloud')
    def skill(self, path, value):
        path.mkdir(parents=True); (path / 'SKILL.md').write_text(value)
    def test_roundtrip_preserves_conflicts_vendor_and_system(self):
        result = manage.apply(self.home, self.repo, self.package)
        self.assertEqual(manage.verify(self.home, self.repo), [])
        self.assertEqual((self.home / '.agents/skills/custom/SKILL.md').read_text(), 'codex version')
        self.assertEqual((self.home / '.claude/skills/custom/SKILL.md').read_text(), 'claude version')
        self.assertEqual((self.home / '.agents/skills/skill0/references/example.txt').read_text(), 'resource')
        self.assertFalse((self.home / '.codex/skills/.system').is_symlink())
        self.assertEqual((self.home / '.agents/skills/codecopilot').resolve(), (self.home / '.claude/skills/codecopilot').resolve())
        self.assertEqual(manage.apply(self.home, self.repo, self.package)['status'], 'already-installed')
        manage.restore(Path(result['backup']))
        self.assertFalse((self.home / '.agents/skills/custom').is_symlink())
        self.assertTrue((self.home / '.agents/skills/skill0').is_symlink())
        self.assertFalse((self.home / '.agents/skills/codecopilot').exists())
    def test_changed_link_blocks_restore_before_any_mutation(self):
        result = manage.apply(self.home, self.repo, self.package)
        link = self.home / '.claude/skills/codecopilot'; link.unlink(); link.mkdir(); (link / 'user.txt').write_text('keep')
        with self.assertRaises(ValueError):manage.restore(Path(result['backup']))
        self.assertEqual((link / 'user.txt').read_text(), 'keep')
        self.assertTrue((self.home / '.agents/skills/custom').is_symlink())
        self.assertIn(str(link), manage.verify(self.home, self.repo))
    def test_existing_named_skill_never_overwritten(self):
        self.skill(self.home / '.agents/skills/codecopilot', 'user version')
        with self.assertRaises(ValueError):manage.apply(self.home, self.repo, self.package)
        self.assertEqual((self.home / '.agents/skills/codecopilot/SKILL.md').read_text(), 'user version')
        self.assertFalse(self.repo.exists())
    def test_modified_shared_skill_not_replaced_on_reinstall(self):
        manage.apply(self.home, self.repo, self.package)
        (self.repo / 'skills/codecopilot/SKILL.md').write_text('local customization')
        with self.assertRaises(ValueError):manage.apply(self.home, self.repo, self.package)
        self.assertEqual((self.repo / 'skills/codecopilot/SKILL.md').read_text(), 'local customization')
    def test_cloud_variants_keep_their_own_writable_targets(self):
        manage.apply(self.home, self.repo, self.package)
        c = self.home / '.claude/skills/synced/account/memo/SKILL.md'
        a = self.home / '.agents/skills/synced/account/memo/SKILL.md'
        c.write_text('cloud update')
        self.assertEqual(a.read_text(), 'codex cloud')
        self.assertEqual((self.repo / 'managed/claude/synced/account/memo/SKILL.md').read_text(), 'cloud update')
    def test_destination_inside_source_rejected_before_mutation(self):
        nested = self.home / '.agents/skills/custom/shared-repo'
        with self.assertRaises(ValueError):manage.apply(self.home, nested, self.package)
        self.assertFalse(nested.exists())
        self.assertFalse((self.home / '.agents/skills/custom').is_symlink())
    def test_external_resource_link_rejected_but_internal_link_preserved(self):
        source = self.home / '.agents/skills/custom'
        (self.home / '.agents/skills/external.txt').write_text('outside dependency')
        (source / 'external').symlink_to('../external.txt')
        with self.assertRaises(ValueError):manage.apply(self.home, self.repo, self.package)
        self.assertFalse(self.repo.exists())
        (source / 'external').unlink(); (self.home / '.agents/skills/external.txt').unlink()
        (source / 'alias').symlink_to('SKILL.md')
        manage.apply(self.home, self.repo, self.package)
        self.assertEqual((source / 'alias').read_text(), 'codex version')
        self.assertEqual((source / 'alias').resolve(), (self.repo / 'skills/custom/SKILL.md').resolve())
    def test_executable_difference_is_not_deduplicated(self):
        for root, mode in [('.agents', 0o755), ('.claude', 0o644)]:
            source = self.home / root / 'skills/custom'
            (source / 'SKILL.md').write_text('same content')
            (source / 'run.sh').write_text('#!/bin/sh\nexit 0\n'); (source / 'run.sh').chmod(mode)
        manage.apply(self.home, self.repo, self.package)
        a = self.home / '.agents/skills/custom/run.sh'; c = self.home / '.claude/skills/custom/run.sh'
        self.assertNotEqual(a.resolve().parent, c.resolve().parent)
        self.assertEqual(a.stat().st_mode & 0o777, 0o755); self.assertEqual(c.stat().st_mode & 0o777, 0o644)
    def test_journal_write_failure_rolls_back_from_memory(self):
        original = manage.atomic_json
        def fail_journal(path, data):
            if path.name == 'links.json':raise OSError('simulated disk failure')
            original(path, data)
        with mock.patch.object(manage, 'atomic_json', side_effect=fail_journal):
            with self.assertRaises(OSError):manage.apply(self.home, self.repo, self.package)
        self.assertFalse((self.home / '.agents/skills/custom').is_symlink())
        self.assertEqual((self.home / '.agents/skills/custom/SKILL.md').read_text(), 'codex version')
        self.assertFalse((self.home / '.agents/skills/codecopilot').exists())
    def test_git_init_failure_does_not_change_discovery_roots(self):
        with mock.patch.object(manage.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, ['git', 'init'])):
            with self.assertRaises(subprocess.CalledProcessError):manage.apply(self.home, self.repo, self.package)
        self.assertFalse((self.home / '.agents/skills/custom').is_symlink())
        self.assertFalse((self.home / '.agents/skills/codecopilot').exists())
    def test_missing_git_marker_never_reports_already_installed(self):
        manage.apply(self.home, self.repo, self.package)
        (self.repo / '.git').rename(self.repo / 'saved-git')
        with self.assertRaises(ValueError):manage.apply(self.home, self.repo, self.package)
    def test_file_contents_cannot_impersonate_another_hash_record(self):
        a = self.home / '.agents/skills/custom'; b = self.home / '.claude/skills/custom'
        (a / 'SKILL.md').write_text('xF:z:420:y')
        (b / 'SKILL.md').write_text('x'); (b / 'z').write_text('y')
        for p in (a / 'SKILL.md', b / 'SKILL.md', b / 'z'):p.chmod(0o644)
        self.assertNotEqual(manage.digest(a), manage.digest(b))
        manage.apply(self.home, self.repo, self.package)
        self.assertNotEqual(a.resolve(), b.resolve())
        self.assertEqual((a / 'SKILL.md').read_text(), 'xF:z:420:y')
        self.assertEqual((b / 'z').read_text(), 'y')

if __name__ == '__main__':unittest.main()
