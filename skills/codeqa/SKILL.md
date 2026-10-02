---
name: codeqa
description: Default coding workflow with necessary tests and independent QA. Use for /codeqa, $codeqa, or an explicit request for reviewed implementation. Use codeqa-light when the user requests lightweight development without independent review.
---

# CodeQA — default

Implement the user's task with the optimized continuous-coordinator workflow in
[references/workflow.md](references/workflow.md). Read that reference when this
skill is selected. It is bundled with this skill; do not require a target project
to install a separate WORKFLOW.md.

- Take the requirement from the user's invocation. If it is absent, ask for the
  task rather than inventing work.
- Keep planning, implementation and finish in the current coordinator context.
  Ordinary scoped, reversible work is authorized by the request. Preserve
  stricter applicable project rules and ask about consequential unresolved choices.
- Run meaningful checks and obtain an independent, fresh, read-only QA verdict.
  Do not claim a model call's successful exit is a QA PASS.
- Verify blocking findings before fixing them; send disputed evidence to a fresh
  independent reviewer. Count adjudication toward the three-round limit.
- Do not silently downgrade to codeqa-light if QA is unavailable. Report the
  blocker. Switching modes requires the user's instruction.
- Report the result, real checks, review verdict and remaining limitations briefly.
  Merge, push and deployment still need their own authorization.

## Models and review setup

The current host model remains the coordinator/developer; a skill cannot switch
Codex or Claude Code's active model. Keep that context rather than spawning a new
worker solely to obtain a different model. Honor an explicitly requested worker
model by delegating only when required; disclose the loss of coordinator-as-author
continuity. Never silently substitute a requested model.

For delegated roles, use project configuration first, then an explicit task
choice. A task-specific choice overrides the project default. If neither exists,
this package's reviewer default is `openai-codex / gpt-6-astra / medium` via pi.
Mention that default on first use. No implementer delegation is required by default.

Read [references/pi-review.md](references/pi-review.md) when preparing independent
QA. Keep the user's scope and existing authorization intact.
