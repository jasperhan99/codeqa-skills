# Independent review through pi

Use the project's reviewer choice or the explicit task override. Otherwise the
package default is provider `openai-codex`, model `gpt-6-astra`, thinking `medium`.
This is a configured default, not permission to substitute another model on failure.

Before the first delegated call in a working session, inspect `pi --version`,
`pi --help`, `pi --list-models`, and `pi auth check --provider PROVIDER --model MODEL`.
Do not print credentials. Reuse successful preflight while configuration is unchanged.

From the target project's root prepare `workflow/tmp/` evidence: full
base-to-candidate diff, changed/new file list, requirement/task record, exact SHAs,
runtime and actual check results. Include test sources needed to assess the evidence.
Do not stage temporary evidence. Quote file paths and pass files with pi's @ syntax.
The skill's workflow reference is located relative to SKILL.md, not to the project.

```sh
pi --provider "PROVIDER" --model "MODEL" --thinking "THINKING" \
  --print --no-session --no-extensions --tools read,grep,find,ls \
  @workflow/tmp/review-prompt.md @workflow/tmp/review.diff \
  @workflow/tmp/changed-files.txt @workflow/tmp/check-results.txt
```

The prompt must name the actual task/requirements, candidate and base, and ask the
reviewer to inspect all changed/new files. Start the response with exactly PASS,
CHANGES_REQUESTED or BLOCKED. Require per-criterion evidence, blocking findings
with severity/file/line/environment/trigger and expected versus actual behavior
(or static proof), optional suggestions separately, and verification limits.
Provide prior findings and reproduction evidence on subsequent rounds, alongside
current full candidate context. A reviewer cannot execute commands with these tools.

Never resume, fork or inherit the author's session for review. Preserve command,
model, exit status and verdict in the task record or referenced audit log. On
failure, missing output or missing evidence, report a blocker; do not self-approve.
