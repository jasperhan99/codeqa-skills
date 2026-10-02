# CodeQA entry points

The default workflow is now the portable **codeqa** skill.

- Default: read [skills/codeqa/SKILL.md](skills/codeqa/SKILL.md).
- Explicit lightweight mode: read [skills/codeqa-light/SKILL.md](skills/codeqa-light/SKILL.md).

Claude Code: `/codeqa <task>` or `/codeqa-light <task>`.
Codex: `$codeqa <task>` or `$codeqa-light <task>` (also available through `/skills`).

Default mode retains necessary tests and independent QA; light mode implements
directly with necessary tests and no independent QA. Follow the selected skill,
not both. The legacy v3.2 rules are archived in
[docs/legacy/WORKFLOW.v3.2.md](docs/legacy/WORKFLOW.v3.2.md).
