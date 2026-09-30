# Multi-agent Development Workflow

[简体中文](README.zh-CN.md)

One file, [WORKFLOW.md](WORKFLOW.md), that any AI coding agent can read and follow:

**plan → you approve → implement + real checks → independent review (max 3 rounds) → you authorize merge/push.**

No installer, no scripts, no required plugins. Delegated model calls use pi CLI, which must be installed and authenticated. Works with Claude Code, Codex, Cursor, Gemini CLI, pi, Copilot and any agent that reads project instruction files.

## Quick start

Open your project in your AI agent and paste:

```text
Set up this workflow in my project: https://github.com/jasperhan99/multi-agents-workflow
```

The agent adds two things (after showing you the change): `WORKFLOW.md` in the project root, and one line in the instruction file it reads. Then just ask for work as usual, e.g. "Add a --verbose flag to the CLI". It plans first and waits for your "ok".

To update later, paste the same line again.

## Setup instructions for AI agents

The human who gave you this link wants this workflow in their current project. Show them the planned changes and get their approval before writing anything.

1. **Get WORKFLOW.md byte-for-byte.** Download it with a shell command such as
   `curl -fsSL https://raw.githubusercontent.com/jasperhan99/multi-agents-workflow/main/WORKFLOW.md -o WORKFLOW.md.new`.
   Do not retype, summarize or translate it. If you cannot download files, give the human that command instead.
2. **Place it in the project root.** If `WORKFLOW.md` does not exist, rename the download to `WORKFLOW.md`. If it exists and is identical, delete the download and keep going. If it differs, show the human the diff and replace it only if they agree.
3. **Point your instruction file to it.** Use the instruction file you load automatically in this project (for example `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`). If none exists, create `AGENTS.md`, or your tool's own file if it does not read `AGENTS.md`. Append this line unless it is already there:

   ```text
   Before any development task, read WORKFLOW.md and follow it.
   ```

4. **Optional, pi only.** If the project uses pi (a `.pi/` directory, or the human says so), offer the [pi adapter](adapters/pi/README.md). Do not install it unless asked.
5. **Stop there.** Do not commit, push, install packages or create `workflow/`; task files are created on the first real task. If the project is not a Git repository, say that the workflow needs one and offer `git init` with a first commit.
6. **Report** the files you created or changed, suggest committing them, and tell the human they can now just ask for a change.

Everything else in this repository is documentation for humans.

## Manual setup

```bash
curl -fsSL https://raw.githubusercontent.com/jasperhan99/multi-agents-workflow/main/WORKFLOW.md -o WORKFLOW.md
```

```bash
echo "Before any development task, read WORKFLOW.md and follow it." >> AGENTS.md
```

Use `CLAUDE.md`, `GEMINI.md` or your tool's file instead of `AGENTS.md` if that is what your agent reads.

## How it works

- **Task files** in `workflow/T-NNN-*.md` hold each task's plan, approval, check results and reviews. They are the source of truth, so a new session can resume from them.
- **Independent review**: the reviewer must not be the context that wrote the code. The coordinator invokes a fresh pi CLI session with read-only tools and an explicit provider/model. If pi is unavailable, it reports a blocker; a manual fresh-session review needs your explicit authorization.
- **You stay in control**: nothing is merged, pushed or deployed without your explicit answer; product, security, architecture and other risky decisions are asked, not assumed.

The workflow is instructions, not enforcement. Use branch protection, CI and scoped credentials where you need real guarantees.

## Models and pi

Pick a model per role in your project's `AGENTS.md`. The coordinator passes these values explicitly to every pi call and asks you if the table is missing:

```markdown
## Workflow models
| Role | Provider | Model | Thinking |
| --- | --- | --- | --- |
| Implementer | anthropic | claude-sonnet-5-5 | medium |
| Reviewer | openai-codex | gpt-6-sol | high |
```

- **Implementer**: a fast, affordable coding model. Most tokens are spent here.
- **Reviewer**: at least as capable, ideally from a different model family so it doesn't share the author's blind spots. It reads only the diff and evidence, so a strong model here costs little.
- Use `pi --list-models` for the IDs available to you, and `pi auth check --provider P --model M` to confirm credentials.

**Why pi:** one CLI reaches many providers with the same flags, works from any host agent that has a shell, and makes the important guarantees visible on the command line: `--no-session` for a truly fresh context and `--tools read,grep,find,ls` for a read-only reviewer.

**Why it helps long tasks and saves tokens:** state lives in the task file and Git, not in a growing conversation. Each worker starts clean, the implementer's long transcript is never replayed to the reviewer or the coordinator, and review rounds are capped at three.

The [guide](docs/GUIDE.md) covers all of this in detail: model selection examples, thinking levels, why pi over native subagents, long-task behaviour, where the tokens go, trade-offs and troubleshooting.

## Adapters (optional)

- [pi](adapters/pi/README.md): `pi-dev` / read-only `pi-qa` subagents and a `/wf` command.

Adapters only point to WORKFLOW.md; they never restate its rules.

## License

[MIT](LICENSE)
