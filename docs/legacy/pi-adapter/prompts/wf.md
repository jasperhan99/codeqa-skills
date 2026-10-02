---
description: Run WORKFLOW.md for one requirement, with pi-dev as Implementer and a fresh pi-qa as Reviewer.
argument-hint: "<requirement> [--yes]"
---
Read WORKFLOW.md at the project root and follow it for this requirement: $@

`--yes` means the human pre-approves the plan, subject to WORKFLOW.md's limits. Use the `pi-dev` subagent as Implementer and a fresh `pi-qa` subagent for every review round; pi-qa cannot run commands, so give it the diff, file list and check results. If either subagent is unavailable, stop and tell the human instead of reviewing your own work.
