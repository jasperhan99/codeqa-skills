# CodeCopilot

Two portable coding skills for **Codex and Claude Code**.

| Skill | Behavior | Independent QA |
| --- | --- | --- |
| `codecopilot` — default | Continuous coordinator, implementation, necessary tests, compact evidence, fresh review | Yes |
| `codecopilotlight` — light | Direct implementation and necessary tests | No |
| No invocation | Ordinary task; neither skill is activated | Not imposed by these skills |

[中文说明](README.zh-CN.md) · [Setup and migration](docs/GUIDE.md)

Both skills are explicit-only. “Default” means the reviewed mode when selected, not automatic activation. A new task without either invocation uses neither skill.

## Invoke

**Claude Code**

```text
/codecopilot Add pagination to this endpoint.
/codecopilotlight Fix the incorrect empty-state text and run relevant checks.
```

**Codex**

```text
$codecopilot Add pagination to this endpoint.
$codecopilotlight Fix the incorrect empty-state text and run relevant checks.
```

Codex also offers `/skills`. A custom skill does not register an arbitrary native
`/codecopilot` command in Codex. Both hosts load the same `SKILL.md` files.

## Install these two skills

Each directory under `skills/` is self-contained. Link the folders, not just the
SKILL.md files, into your host's discovery directory. From this repository:

```sh
mkdir -p ~/.agents/skills ~/.claude/skills
ln -s "$PWD/skills/codecopilot" ~/.agents/skills/codecopilot
ln -s "$PWD/skills/codecopilotlight" ~/.agents/skills/codecopilotlight
ln -s "$PWD/skills/codecopilot" ~/.claude/skills/codecopilot
ln -s "$PWD/skills/codecopilotlight" ~/.claude/skills/codecopilotlight
```

If a name already exists, inspect it instead of overwriting it. Reload/restart the
host if the skills do not appear. Light mode needs no pi installation. Default
mode uses pi for independent QA and reports a blocker if it is unavailable.

## Consolidate existing personal skills

To create a separate local `agent-skills` Git repository, import your current
personal skills, retain host-specific variants, and point both hosts to it:

```sh
python3 scripts/manage_skills.py plan --repo /path/to/agent-skills
python3 scripts/manage_skills.py apply --repo /path/to/agent-skills
python3 scripts/manage_skills.py verify --repo /path/to/agent-skills
```

Use this **instead of** the manual links above when consolidating for the first
time. It refuses existing conflicting `codecopilot` skills and nonempty destinations.
Existing directories are backed up outside the discovery roots. The command
prints the backup path; see the guide for restoration and source-update behavior.
System/plugin-managed skills stay under their own managers. Cloud-synced trees
keep separate host locations inside the shared repo. x-cmd skill0 is snapshotted;
its upstream install remains intact. The tool neither creates a GitHub repo nor
publishes any imported files.

## Models and permissions

A skill keeps the current host's coordinator/developer model; it does not switch
Codex or Claude Code to another model. The bundled independent reviewer default
is **pi / openai-codex / gpt-6-astra / medium**, unless the project or the task
specifies another choice. Configure a different host model in the host itself.

Both modes preserve explicit project constraints and unrelated work. Neither
skill grants merge, push, deployment or destructive-operation authorization.
`codecopilot` never silently drops QA; `codecopilotlight` never silently adds it.

## Repository layout

- `skills/codecopilot/`: default skill and optimized workflow reference.
- `skills/codecopilotlight/`: lightweight skill.
- `scripts/manage_skills.py`: inspect, migrate, verify and restore local skill links.
- `tests/`: migration preservation and restoration tests.
- `docs/legacy/`: prior v3.2 documentation and optional pi adapter, for reference.
- `WORKFLOW.md`, `WORKFLOW.optimized.md`: compatibility entry points to the skills.

Run `python3 -m unittest discover -s tests -v` to check the migration tool.
The earlier timing experiment found only a modest improvement: about 244 seconds
versus 223 seconds across two paired runs. That is not a general performance
promise; see [the experiment summary](docs/BENCHMARK.md).

Repository: [codecopilot-skills](https://github.com/jasperhan99/codecopilot-skills). Use **agent-skills** for your separate
personal collection. Renaming a remote repository is not part of installing skills.

## License

[MIT](LICENSE) for this package. Imported personal/third-party skills retain their
own licenses; the shared collection does not relicense them.
