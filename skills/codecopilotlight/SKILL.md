---
name: codecopilotlight
description: Direct implementation and necessary tests, without independent QA. Use only when the user explicitly invokes /codecopilotlight or $codecopilotlight, or selects this skill in the host skill picker. Never activate for ordinary coding requests.
disable-model-invocation: true
---

# CodeCopilot Light

## Explicit invocation only

Apply this workflow only to a task explicitly started with /codecopilotlight, $codecopilotlight,
or this skill selected in the host picker. Mentioning or editing this skill is not
an invocation. Follow-ups may continue that same task; a new task without an explicit
invocation uses neither CodeCopilot skill. Do not infer activation from task complexity,
requests for testing/review, or a prior completed task. “Default” names the reviewed
mode after invocation; it never means automatic activation.


Implement the task in the current agent context and run the checks necessary to
support the result. This mode intentionally has **no independent QA stage**.
Do not load codecopilot or its full workflow merely because the task involves code.

1. Read applicable project instructions, relevant code and working-tree status.
   Take the requirement from the user's invocation; ask if no task was supplied.
2. For clear, reversible work, state a brief approach when useful and proceed.
   Ordinary implementation details are yours to decide. Clarify consequential
   ambiguity involving product scope, security/privacy, major architecture,
   breaking APIs, migrations, paid services or irreversible actions.
3. Implement directly. Preserve unrelated and uncommitted work; resolve conflicting
   ownership before editing. Do not delegate implementation or review solely to
   follow this skill. Keep the current host model unless the user requests otherwise.
4. Run relevant existing checks and add focused regression tests when they provide
   meaningful assurance. Do not manufacture tests for trivial reversible edits.
   Report actual PASS, FAIL or NOT RUN with reasons; never weaken tests to pass.
5. Briefly report changes, checks and limitations. State that independent QA was
   not performed when reporting review status; do not label self-checks as QA PASS.

This skill adds no mandatory plan-approval round, task record, branch, commit or
release step. Follow explicit user/project requirements where they do apply.
Do not automatically switch to codecopilot because work is difficult; explain any
consequential limitation and let the user choose a mode change. An explicit
request for QA authorizes that additional work.

Merge, push, deployment and destructive operations still require the appropriate
user authorization. Never expose secrets, overwrite unrelated work or treat this
skill invocation as permission for extra external actions.
