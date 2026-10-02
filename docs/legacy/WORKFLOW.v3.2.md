# Development Workflow

Version 3.2 · Source and updates: https://github.com/jasperhan99/multi-agents-workflow

This file is the complete rule set. Any AI coding agent that reads it can follow it without other rule files or plugins. Delegated model calls require pi CLI. Reply in the human's language.

**Loop:** plan → human approves → implement + real checks → independent review (max 3 rounds) → human authorizes merge/push.

## Roles

- **Human**: approves plans, makes high-risk decisions, authorizes merge and push.
- **Coordinator** (you, the main agent): writes the plan, keeps the task record, runs checks, arranges review, reports.
- **Implementer**: writes the code. The coordinator itself, or a separate model session invoked through pi CLI.
- **Reviewer**: independent, read-only, fresh context. Never the context that wrote the code.

## Model configuration

The project's AGENTS.md (or the instruction file the coordinator reads) records which model each delegated role uses:

```markdown
## Workflow models
| Role | Provider | Model | Thinking |
| --- | --- | --- | --- |
| Implementer | anthropic | claude-sonnet-5-5 | medium |
| Reviewer | openai-codex | gpt-6-sol | high |
```

- If the table is missing, ask the human on the first task which provider and model to use for each role, show the output of `pi --list-models` as the options, and offer to add the table to AGENTS.md. Never pick a model silently.
- The reviewer should be at least as capable as the implementer. Prefer a different model family from the one that wrote the code, so blind spots are less likely to be shared. If only one model is available, a fresh session of the same model is still acceptable; note it in the task file.
- Thinking is optional; omit it to use pi's default. Valid levels are those in `pi --help` (for example `low`, `medium`, `high`).
- A one-off override from the human ("review this one with X") applies to that task only; record it in the task file. Changing the table itself is a durable change and needs the human's agreement.
- The coordinator is whatever host agent the human is using; this table does not choose it.

## Model calls through pi CLI

- Use **pi CLI** whenever the coordinator delegates implementation, review or another model task. The coordinator may run in any host agent; this rule governs the model calls it initiates. Do not substitute direct provider API calls or the host's native subagents.
- Before the first call, check `pi --version`, `pi --help`, `pi --list-models` and `pi auth check --provider PROVIDER --model MODEL_ID`. Use the models from **Model configuration**, and pass them explicitly with `--provider`, `--model` and, if set, `--thinking`. Do not rely on pi's default model. If pi, credentials or the requested model are unavailable, report the blocker; do not silently switch providers or models.
- Run from the project root. Use `--print --no-session` for a fresh, non-interactive call, and pass WORKFLOW.md, the task file and the role prompt as context. Give each call only what its role needs; the task file, not the coordinator's conversation, carries the state between calls. Never use `--continue`, `--resume`, `--session`, `--session-id` or `--fork` for an independent review.
- For reviewers, disable extensions and allow only `read,grep,find,ls`. Supply the diff, changed/new file list and real check results as files because the reviewer has no shell. These tool restrictions are not an OS sandbox.
- Record the provider, model, role, command (without secrets), exit status and result in the task file. A successful process exit alone is not a review PASS. Missing output or a failed call is a blocker, not evidence of success. Use pi's existing authentication or environment variables; never put credentials in prompts or task records.
- The optional pi adapter may wrap these calls, provided it preserves fresh review context and the same tool restrictions. Delegated workers must not recursively start other agents.

Example reviewer invocation (replace the provider, model and file paths with the actual values; `review-prompt.md` contains the reviewer prompt below with the task path and SHAs filled in):

```bash
pi --provider "PROVIDER" --model "MODEL_ID" --thinking high \
  --print --no-session --no-extensions --tools read,grep,find,ls \
  @WORKFLOW.md @workflow/T-NNN-short-name.md @review-prompt.md \
  @review.diff @changed-files.txt @check-results.txt
```

Example implementer invocation (the implementer needs a shell and edit tools; `implement-prompt.md` names the task file, branch and base SHA and asks for the **Implement** section only):

```bash
pi --provider "PROVIDER" --model "MODEL_ID" --thinking medium \
  --print --no-session --no-extensions --tools read,grep,find,ls,bash,edit,write \
  @WORKFLOW.md @workflow/T-NNN-short-name.md @implement-prompt.md
```

Put the prompt and evidence files (`review-prompt.md`, `review.diff` and so on) in `workflow/tmp/` and never stage them; the task file records their results.

## 1. Plan

1. Read the project's instructions (AGENTS.md, CLAUDE.md, README), the relevant code and `git status`.
2. Stop and ask if there is no Git repository or first commit, or if files this task will touch have uncommitted changes. Leave other uncommitted changes untouched and mention them.
3. Create `workflow/T-NNN-short-name.md` from the template below, using the next unused number.
4. Show the human a plan of five to eight lines: goal, will do, will not do, done when, checks to run, branch.
5. Wait for explicit approval. A reply such as "ok", in any language, approves this exact plan. Any change request means revise and ask again. The request itself, or silence, is not approval. Record the reply in the task file.

Skipping approval: if the human says so with the request (for example "no need to confirm" or `--yes`), you may continue without waiting, but only for a small task where none of the **stop-and-ask** items below apply. Otherwise say why and wait. It covers only that request, unless the project's AGENTS.md grants it for all small tasks.

## 2. Implement

- Create `task/T-NNN-short-name` from the base commit. Record the base SHA.
- Change only the approved scope. Preserve unrelated and untracked work. Stage named files only; never `git add -A`, `reset --hard`, `clean` or force push.
- **Stop and ask** before any of: product or scope changes, security/privacy choices, major architecture, breaking APIs, data migrations, irreversible actions, new paid services, or anything you had to guess. Present options, trade-offs and a recommendation. Record the answer in the task file. Unrelated safe work may continue.
- Run the planned checks. Record each command and its real result: PASS, FAIL or NOT RUN (with reason). Never invent results. Never weaken a test or requirement to make it pass.
- Commit on the task branch. That commit is the **candidate SHA**.

## 3. Review

Give the reviewer: the task file, base SHA, candidate SHA, `git diff <base>..<candidate>`, the full list of changed and new files, and the check results.

- Start a fresh pi CLI session with read-only tools, using the reviewer prompt below and the model-call rules above.
- If pi cannot run, report the blocker. A manual fresh-session review is allowed only if the human explicitly authorizes that fallback; record the decision.
- Never review your own work in the same context. If no independent review is possible, say so and let the human decide; record the decision.

The reviewer returns one verdict:

- **PASS**: every acceptance criterion is supported by evidence.
- **CHANGES_REQUESTED**: numbered findings with file/line and why.
- **BLOCKED**: missing decision, evidence or files.

On CHANGES_REQUESTED: fix, rerun checks, commit a new candidate and send it to a *fresh* review. At most **3 review rounds**; after that, set status `blocked` and hand it to the human. Any code change after a PASS needs a new review.

## 4. Finish

On PASS with all required checks passing, set status `done` and report in a few lines: changed files, check results, verdict, candidate SHA. Then ask exactly one question, naming the real branch and remote, for example:

> Merge `task/T-001-login` into `main` and push to `origin`? (push / merge only / no)

Only after the human answers:

- If the base branch has not moved, fast-forward it to the reviewed SHA. If it moved, bring the new base into the task branch, rerun checks and review, then ask again. Never push unreviewed content.
- Push only the named branch. Never force push. Confirm the remote ref equals the reviewed SHA; if a push fails, inspect the state before retrying.
- Record the merged/pushed SHA and the date in the task file.

Tags, releases and deployment happen only if the human asks for them separately.

## Resuming

In a new session, trust the files and Git, not memory. Read `workflow/T-*.md`, check branches and `git status`, and report each open task's status and the next step. Re-confirm an old approval if the code or scope has changed since.

## Hard rules

- No code before an approved plan. No merge, push, tag, deploy, force push or destructive Git command without explicit human permission for that exact action.
- A review PASS is not permission to merge or push.
- One writer per checkout at a time.
- Report checks honestly. Unrun is NOT RUN, not PASS.
- Never commit secrets or credentials.
- Durable project facts (build commands, architecture, conventions) belong in the project's AGENTS.md or README, not in task files.

## Task file template

```markdown
# T-NNN — Title

Status: planned | approved | in-progress | in-review | done | blocked | cancelled
Branch: task/T-NNN-short-name
Base SHA:

## Plan
- Goal:
- Will do:
- Will not do:
- Done when:
- Checks:
- Risks:

## Approval
(who, when, exact reply)

## Decisions
(question, answer, date — or NONE)

## Checks
| Command | Result |
| --- | --- |

## Model calls
| Role | Provider / model / thinking | Command (no secrets) | Exit status | Result |
| --- | --- | --- | --- | --- |

## Reviews
- Round 1 — candidate `<sha>` — PASS / CHANGES_REQUESTED / BLOCKED — findings

## Release
(authorization reply, merged/pushed SHA, remote, date — or NONE)
```

## Reviewer prompt

```text
You are an independent code reviewer. Do not edit files or run commands that change anything.
Read WORKFLOW.md and the task file <path>. Review candidate <sha> against base <sha>.
Inspect the diff and every changed or new file yourself; do not trust the implementer's summary.
Check each acceptance criterion against the evidence, plus security, error paths, edge cases, simplicity and test coverage.
If the diff, files or check results are missing, answer BLOCKED.
Reply with exactly one verdict — PASS, CHANGES_REQUESTED or BLOCKED — then:
per-criterion assessment, numbered findings (severity, file:line, reason, what to recheck), and what you did not verify.
```
