# Installation and migration guide

## Choose a mode

`codecopilotlight` means direct implementation plus necessary tests, with **no independent
review**. `codecopilot` means the default optimized workflow with independent review.
Do not use the old “read WORKFLOW.md before every task” rule alongside an explicit
light invocation; replace it with “Use a CodeCopilot skill only when explicitly invoked” when adopting
these entry points. Existing stronger project constraints still apply.

The skill package is portable. It does not require copying workflow files into
new target projects, does not change the active host model and does not grant
release authorization. Details are inside the selected skill.

Without an explicit invocation, neither skill applies to a new task. Claude Code uses
`disable-model-invocation: true`; Codex uses `policy.allow_implicit_invocation: false`.
Mentioning the skill in documentation or asking to edit it does not activate it.

## Shared collection

The migration tool requires Python 3 and Git. A destination must be new/empty.
It reads non-hidden user skill entries from `~/.agents/skills`, `~/.claude/skills`
and legacy `~/.codex/skills`. Hidden system locations and plugin caches are not moved.

1. `plan --repo PATH` prints the proposed sources and links without modifying them.
2. `apply --repo PATH` copies and hashes resources including permissions, preserves conflicting variants,
   backs up existing entries, replaces them with directory links and initializes Git.
3. `verify --repo PATH` checks that every managed link still resolves correctly.

Original directories/links live in the printed backup directory under
`~/.local/share/agent-skills-backups/`. Restore with:

```sh
python3 scripts/manage_skills.py restore --backup /exact/printed/backup/path
```

Restore preflights every installed link and refuses to overwrite paths changed
by another process. It does not delete the shared repo or discard changes stored
there. Inspect those changes before restoring if you have edited shared skills.

An existing migration is idempotent. If a package skill or managed link has changed,
reinstallation refuses to overwrite it. Compare and synchronize deliberately;
this tool is not an automatic upstream updater.

## What is shared

`skills/` holds common personal skills. `variants/` preserves host-specific personal
versions. `managed/codex/synced` and `managed/claude/synced` preserve their original
nested account layout; each application's sync can still write to its own target.
`vendor/skill0` preserves the installed x-cmd skill content and supporting files.
The manifest records original paths, hashes and upstream link targets.

The shared repo is local and may contain imported third-party content. No remote,
publishing or blanket relicensing is performed. The tool rejects destinations nested inside source/discovery trees, and rejects
absolute or external resource symlinks before changing live entries. Internal
relative resource links are retained.

System and plugin skills retain
their software-managed lifecycle. A future cloud/x-cmd update may replace a link;
run verification afterward rather than assuming links are permanent.

## Validate discovery

Codex: open `/skills` or mention `$codecopilot` / `$codecopilotlight`.
Claude Code: type `/codecopilot` or `/codecopilotlight`.
If newly installed skills are missing, restart the host. Finding a skill locally
is separate from authenticating a model or successfully running QA.

Official references:
- [Codex skill locations and invocation](https://learn.chatgpt.com/docs/build-skills)
- [Claude Code skill locations and slash commands](https://code.claude.com/docs/en/skills)

Local tests: `python3 -m unittest discover -s tests -v`.
