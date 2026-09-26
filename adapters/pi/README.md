# pi adapter (optional)

Thin wrappers that let [pi coding agent](https://github.com/earendil-works/pi/tree/main/packages/coding-agent) run [WORKFLOW.md](../../WORKFLOW.md) with a separate implementer and a read-only reviewer. The rules live only in WORKFLOW.md; these files just point to it. pi CLI is required for delegated model calls; only this adapter and its subagent plugin are optional. Configure the provider/model explicitly for each worker and preserve the fresh-session and read-only restrictions in WORKFLOW.md.

From your project root, after WORKFLOW.md is in place:

```bash
base=https://raw.githubusercontent.com/jasperhan99/multi-agents-workflow/main/adapters/pi
mkdir -p .pi/agents .pi/prompts
curl -fsSL "$base/agents/pi-dev.md" -o .pi/agents/pi-dev.md
curl -fsSL "$base/agents/pi-qa.md" -o .pi/agents/pi-qa.md
curl -fsSL "$base/prompts/wf.md" -o .pi/prompts/wf.md
pi install -l npm:pi-subagents@0.71.0
```

Restart pi (or `/reload`), then:

```text
/wf Implement login and persistent sessions
```

Tested with pi 0.86.1 and pi-subagents 0.71.0. Tool allowlists are enforced by the plugin, not the OS.
