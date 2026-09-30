# Guide: how the workflow works, and why

This guide is for humans. It explains the design behind [WORKFLOW.md](../WORKFLOW.md): how to configure and choose models, why delegated model calls go through pi CLI, and what that buys you on long tasks and token spend. The rules themselves live only in WORKFLOW.md. If this guide and WORKFLOW.md ever disagree, WORKFLOW.md wins.

## Contents

1. [The shape of the workflow](#1-the-shape-of-the-workflow)
2. [Configuring models](#2-configuring-models)
3. [Choosing models](#3-choosing-models)
4. [Why pi CLI](#4-why-pi-cli)
5. [Why it holds up on long tasks](#5-why-it-holds-up-on-long-tasks)
6. [Where the token savings come from](#6-where-the-token-savings-come-from)
7. [Trade-offs and limits](#7-trade-offs-and-limits)
8. [Troubleshooting](#8-troubleshooting)

## 1. The shape of the workflow

```text
 you ──request──▶ Coordinator (your host agent: Claude Code, Codex, Cursor, …)
                    │  writes workflow/T-NNN-*.md, shows a plan
 you ──"ok"──────▶  │
                    ├─ pi --print --no-session ──▶ Implementer (model A, can edit)
                    │      returns: files changed, check results, candidate SHA
                    ├─ runs checks itself, records real results
                    ├─ pi --print --no-session ──▶ Reviewer (model B, read-only)
                    │      returns: PASS / CHANGES_REQUESTED / BLOCKED
                    │  (repeat implement → review, at most 3 rounds)
 you ◀─"merge and push?"─┘
```

Four roles, each with one job:

| Role | Where it runs | Tools | Keeps state? |
| --- | --- | --- | --- |
| Human | you | approvals and decisions | — |
| Coordinator | the agent you are talking to | everything your host allows | yes, in the task file |
| Implementer | a fresh pi session, or the coordinator itself | read, grep, find, ls, bash, edit, write | no, one call per round |
| Reviewer | always a fresh pi session | read, grep, find, ls | no, one call per round |

Everything that must survive — plan, approval, decisions, check results, model calls, review verdicts, release — is written to `workflow/T-NNN-short-name.md`. Git holds the code; the task file holds the story. No role depends on another role's memory.

## 2. Configuring models

### Where the choice lives

Put a small table in your project's `AGENTS.md` (or `CLAUDE.md`, `GEMINI.md`, whichever file your agent reads):

```markdown
## Workflow models
| Role | Provider | Model | Thinking |
| --- | --- | --- | --- |
| Implementer | anthropic | claude-sonnet-5-5 | medium |
| Reviewer | openai-codex | gpt-6-sol | high |
```

The coordinator reads this table and passes every value explicitly:

```bash
pi --provider anthropic --model claude-sonnet-5-5 --thinking medium --print --no-session ...
```

It never relies on pi's own default model (`defaultProvider` / `defaultModel` in `~/.pi/agent/settings.json`). That default is for your interactive use; the workflow wants the choice visible in the repository and in each task file.

If the table is missing, the coordinator asks you on the first task, shows `pi --list-models` as the menu, and offers to add the table for you. It never picks a model silently, and it never falls back to a different model when the configured one fails. It reports a blocker instead.

### Setting pi up once

```bash
pi --version
```

```bash
pi --list-models
```

`--list-models` shows every provider and model pi can reach with your current credentials, along with context window, max output and thinking support. Log in to a provider the way pi documents it (API key in the environment, or OAuth for subscription providers), then check a specific pair:

```bash
pi auth check --provider anthropic --model claude-sonnet-5-5
```

The coordinator runs these same checks before its first delegated call.

### Thinking levels

`--thinking` accepts `off`, `minimal`, `low`, `medium`, `high`, `xhigh` and `max` (see `pi --help`). Higher levels cost more output tokens and time. A reasonable default is `medium` for implementation and `high` for review. Leave the column empty to use pi's default for that model.

### One-off overrides

Say "review this one with gpt-6-sol at xhigh" and the coordinator uses that for the current task only, and records it in the task file. Changing the table in AGENTS.md is a durable change, and the coordinator asks before making it.

## 3. Choosing models

Pick by role, not by favourite.

**Implementer: good, fast, affordable.** Most of the tokens in a task are spent here: reading code, editing, running tests, fixing. The plan has already been approved and the scope is fixed, so you rarely need the most expensive model. A strong mid-tier coding model with medium thinking is usually the best value.

**Reviewer: at least as capable, and ideally different.** The reviewer reads a diff and a handful of files, so it uses far fewer tokens than the implementer. That makes it the right place to spend on a stronger model and higher thinking. Prefer a different model family from the implementer: models from the same family tend to share blind spots, and a reviewer that "thinks like" the author is more likely to wave the same mistake through.

**Coordinator: whatever you are already using.** The table does not choose it. The coordinator mostly plans, reads short reports and writes the task file, so it does not need to be the biggest model either.

Example setups (model IDs are from one `pi --list-models` output; use what yours shows):

| Situation | Implementer | Reviewer | Why |
| --- | --- | --- | --- |
| Two providers, balanced | `anthropic / claude-sonnet-5-5`, medium | `openai-codex / gpt-6-sol`, high | cross-family review, strong model spent where tokens are few |
| One provider only | `anthropic / claude-sonnet-5-5`, medium | `anthropic / claude-opus-5-5`, high | still a fresh context and a stronger reviewer |
| Tight budget | a flash / highspeed model, low | a mid-tier model from another family, medium | cheap bulk work, independent check at the gate |
| High-risk change (auth, payments, migrations) | a strong model, high | the strongest model from another family, xhigh | pay for certainty where mistakes are expensive |

Also check the context window column. The reviewer must fit WORKFLOW.md, the task file, the diff and the changed files in one call; for large diffs, pick a reviewer with a large context or split the task.

If you only have one model, the workflow still works: a fresh `--no-session` call with read-only tools is independent of the context that wrote the code. The task file notes that the same model reviewed.

## 4. Why pi CLI

The workflow needs three things from whatever makes the delegated calls: any model, a guaranteed fresh context, and enforceable tool limits. pi gives all three through one command line, whichever host agent you run.

**One interface for many providers.** pi talks to Anthropic, OpenAI (including Codex subscriptions), Google, Chinese providers such as Zhipu, and gateways, all with the same `--provider` and `--model` flags. The coordinator doesn't need to know each vendor's SDK, and you can switch the reviewer to another family by editing one table row.

**Works from any host.** Claude Code, Codex, Cursor, Gemini CLI and Copilot all have a shell. Native subagents differ between hosts, and most run only their own vendor's models. A shell command is the lowest common denominator, so the same WORKFLOW.md works everywhere.

**Freshness you can see.** `--print --no-session` starts with no history and saves nothing. The workflow forbids `--continue`, `--resume`, `--session`, `--session-id` and `--fork` for reviews, so a reviewer can't inherit the implementer's reasoning, even by accident. With a host's native subagent, you usually have to trust that its context is clean.

**Tool limits on the command line.** `--tools read,grep,find,ls` gives the reviewer no shell and no edit tools. `--no-extensions` stops project or user extensions from adding tools back. These limits are enforced by pi, not by the model's good behaviour. They are not an OS sandbox, though; see [Trade-offs](#7-trade-offs-and-limits).

**Auditable.** Each call is one command line. The task file records role, provider, model, thinking level, command (no secrets), exit status and result. Months later you can see exactly which model approved which SHA.

**Uses the credentials you already have.** pi reuses its stored OAuth logins and environment API keys, and `pi auth check` confirms they work before the first call. Secrets never go into prompts or task files.

**Why not call provider APIs directly?** You would have to rebuild the tool loop (read files, grep, edit, run commands), per-vendor auth, and tool restrictions, which is exactly what pi already is. **Why not the host's native subagents?** They lock you to one host and usually one vendor, and their context and tool boundaries vary. pi keeps the workflow portable.

## 5. Why it holds up on long tasks

Long tasks usually fail in a single agent session in a few predictable ways. The context fills up and gets compacted, early decisions are lost, the model starts reviewing its own assumptions, and a crash or closed laptop loses everything. The workflow is built around those failures.

**State lives in files, not in a conversation.** The plan, approval, decisions, check results and every review verdict are in `workflow/T-NNN-*.md`; the code is in Git on `task/T-NNN-*`. A new session, a different host agent or a different person can read them and continue. See the **Resuming** section of WORKFLOW.md.

**Each worker starts clean.** Every implementer and reviewer call begins with the same small, curated input: WORKFLOW.md, the task file and a role prompt (plus the diff for review). Round 3 of a review is exactly as sharp as round 1, because no conversation history has built up and nothing has been compacted.

**The coordinator's context grows slowly.** The coordinator gets a short report back from each call (files changed, check results, verdict), not the implementer's full transcript of file reads, test logs and retries. It can run many rounds, or several tasks in a row, before its own context gets crowded.

**Bounded loops.** At most three review rounds, then the task becomes `blocked` and comes back to you. A long task can't turn into an endless fix-and-review cycle that burns tokens without converging.

**Interruptions are cheap.** If a pi call fails, times out or returns nothing, that is recorded as a blocker, not taken as success. Rerun that one step; you don't restart the task.

**Big work splits naturally.** Because tasks are separate files with separate branches, a large feature becomes T-012, T-013, T-014, each planned, reviewed and merged on its own. The workflow allows one writer per checkout, so run parallel tasks in separate worktrees.

## 6. Where the token savings come from

In a chat-style agent session, every turn sends the whole conversation back to the model. As a task goes on, each new step costs more than the last, because it carries all the earlier file reads, tool output and discussion with it. Prompt caching lowers the price of that repeated prefix, but it still takes up context, and compaction throws information away to make room.

The workflow cuts that cost in five ways:

1. **No shared history between workers.** The implementer's hundreds of tool calls stay inside its own call and are thrown away (`--no-session`). The reviewer never pays for them, and neither does the coordinator.
2. **The reviewer reads evidence, not the story.** It gets the diff, the changed-file list and the check results as files, and opens only what it needs. That is much smaller than the conversation that produced the code.
3. **Expensive models only where input is small.** Put the strong model on review (small input, high value) and a cheaper one on implementation (large input, routine work). You pay premium rates on the fewest tokens.
4. **Short hand-offs.** Each role returns a structured summary. The coordinator's context grows by a few lines per round, not by a whole transcript.
5. **Fewer wasted rounds.** An approved plan with "will not do" and "done when" lines keeps the implementer from drifting into work you didn't ask for. The three-round limit stops runaway loops.

Where it does not save:

- Every fresh call pays again for its fixed input (WORKFLOW.md, the task file, the prompt), and the reviewer reads the changed files again. For a one-line fix, a single agent is cheaper. The workflow pays off as tasks get longer, riskier or span several sessions.
- Higher thinking levels on the reviewer cost output tokens. That is usually a good trade, but it is a cost.

To see your actual numbers, compare your provider's usage dashboard across a few tasks run both ways. The task file's **Model calls** table shows which model made each call.

## 7. Trade-offs and limits

- **Instructions, not enforcement.** WORKFLOW.md tells the agent what to do; it cannot force it. Use branch protection, required CI and scoped credentials for real guarantees.
- **Tool limits are not a sandbox.** pi enforces `--tools`, but the process still runs as your user. Don't give workers credentials they don't need.
- **One more dependency.** You need pi installed and authenticated. If it is missing, the workflow stops with a blocker rather than silently reviewing its own work. A manual fresh-session review is allowed only if you explicitly approve it.
- **The implementer shares your checkout.** While a delegated implementer runs, the coordinator (and you) should not edit the same checkout.
- **Model IDs change.** Examples here will age. Trust `pi --list-models` over this page.

## 8. Troubleshooting

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| "pi not found" blocker | pi not installed or not on `PATH` | install pi, then check `pi --version` |
| Model not listed | provider not logged in, or wrong ID | `pi --list-models`, then `pi auth check --provider P --model M` |
| Review returns BLOCKED "missing diff" | the evidence files weren't passed | the coordinator must pass `review.diff`, the changed-file list and check results with `@` |
| Review output is empty | call failed or timed out | recorded as a blocker; rerun that review, not the whole task |
| Reviewer runs out of context | diff too large for its model | pick a reviewer with a larger context window, or split the task |
| Same model reviewed its own code | only one model configured | acceptable if fresh, and noted in the task file; add a second provider when you can |
