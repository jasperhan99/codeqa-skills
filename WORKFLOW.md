# CodeCopilot entry points

The default workflow is now the portable **codecopilot** skill.

- Default: read [skills/codecopilot/SKILL.md](skills/codecopilot/SKILL.md).
- Explicit lightweight mode: read [skills/codecopilotlight/SKILL.md](skills/codecopilotlight/SKILL.md).

Claude Code: `/codecopilot <task>` or `/codecopilotlight <task>`.
Codex: `$codecopilot <task>` or `$codecopilotlight <task>` (also available through `/skills`).

Default mode retains necessary tests and independent QA; light mode implements
directly with necessary tests and no independent QA. Follow the selected skill,
not both. The legacy v3.2 rules are archived in
[docs/legacy/WORKFLOW.v3.2.md](docs/legacy/WORKFLOW.v3.2.md).

Only load a skill after an explicit invocation. Without one, use neither workflow.
