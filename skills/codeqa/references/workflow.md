# Development Workflow — Continuous Coordinator

Experimental v0.1 · Alternative to WORKFLOW.md v3.2; not an automatic replacement.

**Loop:** scope → implement and check → independent review → verify findings → finish.
Reply in the human's language. Keep one coordinator context for the life of a task;
independent reviewers always start fresh. Preserve a small file record for recovery.

## Authorization and scope

- For a clear, reversible task, a direct user request authorizes planning and
  implementation within that scope. State a short plan and proceed unless the
  user or project explicitly requires a separate approval. Record the authorization.
- Ask before unresolved product requirements, consequential security/privacy
  choices, major architecture, breaking APIs, migrations, irreversible actions or
  new paid services. Routine local implementation choices are yours to make.
- Never merge, push, tag, deploy, force-push or destroy work without explicit
  authorization for that action. QA PASS is not release authorization.
- Read instructions, relevant code and Git status. Preserve unrelated work. If
  task files have conflicting uncommitted edits, clarify ownership before editing.
- One writer per checkout. Stage named files only. Do not use git add -A,
  reset --hard, clean or force push. Never record secrets.

## Roles and model calls

- **Coordinator/developer:** keep the current context across scope, implementation,
  findings and finish. For a bounded task, implement directly in that context.
  Delegate implementation only when isolation, specialization or task size merits
  another context; do not create separate model calls just for plan or finish.
- **Reviewer:** fresh independent context, read-only, never the code author's
  context. At most three review rounds per task; otherwise report blocked.
- Use the project's configured provider, model and thinking explicitly. Use explicit package defaults from SKILL.md when configured; ask once
  if neither project nor package defines the role. Do not silently switch models or providers. The coordinator's host
  model is not implicitly selected by a delegated-role table.
- Use pi CLI for delegated model work. Check installed CLI/options and model/auth
  availability once per working session, then reuse that successful preflight
  unless configuration changes or a call fails. No recursive delegation.
- A coordinator implemented through pi may use one named session across stages.
  This is coordinator continuity, not reviewer continuity. Review calls must use
  `--print --no-session --no-extensions --tools read,grep,find,ls`, explicit
  `--provider`, `--model`, and configured `--thinking`; never resume/fork a review.
- Keep raw commands, exit codes and outputs in an audit log when available.
  Reference that log from the task record instead of transcribing it. A failed
  process, missing output or exit 0 without a verdict is not PASS. If pi is
  unavailable, report the blocker; manual independent review requires permission.

## Scope, implement and check

1. Create `workflow/T-NNN-short-name.md` with the compact template below. State
   goal, boundaries and acceptance/checks in a few lines. Create a task branch
   and record its base SHA. Follow project branch naming conventions.
2. Implement the accepted scope. Add tests that address meaningful risks.
3. Run the required checks and record actual results, candidate code SHA and
   environment. A result can be reused only when its tested inputs, dependencies,
   configuration and relevant environment are unchanged. A change to code or
   tests invalidates affected results. Run broad regression when impact is unclear.
4. Commit the candidate. Prepare full base-to-candidate diff, changed/new file
   list, exact SHAs, requirements, environment and check evidence for the reviewer.
   Keep temporary evidence under `workflow/tmp/`, out of commits. Use deterministic
   tooling for collecting evidence rather than a separate model call.

## Independent review and finding verification

Review criteria do not shrink with task size: acceptance, correctness, relevant
security/error paths, maintainability and tests. Restrict blockers to demonstrated
or well-supported defects, unmet acceptance criteria or missing required evidence.
Style preferences and speculative improvements are optional and do not force changes.

The reviewer returns `PASS`, `CHANGES_REQUESTED` or `BLOCKED` on the first line,
then concise per-criterion evidence, numbered findings and verification limits.
For each blocking finding include severity, file/line, violated requirement,
assumed environment, trigger and expected/actual behavior or a clear static proof.
Distinguish observed failures from unexecuted hypotheses. With no shell, request
a minimal reproduction from the coordinator instead of claiming it was executed.

On CHANGES_REQUESTED, the existing coordinator context handles findings:

1. Reproduce the claimed failure in the supported environment, or validate its
   static proof. Do not require executing unsafe actions to prove a security bug.
2. If supported, fix it and rerun affected checks; record regression evidence and
   commit a new candidate. Do not weaken tests to obtain PASS.
3. If not reproduced or applicable only to an unspecified environment, record the
   exact command/input, runtime, expected and actual results. Do not change code
   merely to silence the finding. Send that evidence to a fresh reviewer for
   adjudication. The author cannot override a blocked verdict or self-approve.
4. Fresh follow-up review receives the full candidate context, previous findings,
   repair diff and verification evidence. Prioritize the fixes and affected paths,
   preserving required regression/security checks. Code changes require re-review.

All review/adjudication calls count toward the three-round cap. At the cap,
record unresolved findings and hand control back to the human; never infer PASS.

## Finish and recover

- After independent PASS and all required checks pass, update the existing task
  record and report outcome, checks, candidate SHA and limitations in the same
  coordinator context. Do not launch a worker solely to restate results.
- No automatic merge/push. If requested, apply explicit authorization only to
  reviewed content. If the target base changed, integrate it, rerun affected
  checks and review the new candidate before release. Verify the remote SHA.
- When recovering, read the open task record, audit references and actual Git
  state. Recover facts from files; never invent prior approvals or results.
- Durable build/architecture conventions belong in AGENTS.md or README.

## Compact task record

```markdown
# T-NNN — Title
Status: in-progress | in-review | done | blocked | cancelled
Branch: ... | Base: ... | Candidate: ...
Goal/boundaries: ...
Authorization: user request or explicit approval; date; release authorization separately
Acceptance/checks: ...
Environment: runtime/dependency/configuration facts relevant to the checks
Checks: actual command/result + tested SHA or artifact; audit-log reference if available
Decisions/findings: material decision; reproduction or static evidence; disposition
Review: round, reviewer provider/model/thinking, candidate, verdict, evidence reference
Model calls: audit-log reference, or concise command/exit/result entries if no log exists
Release: NONE, or exact authorization/action/SHA/remote/date
```

Update at meaningful transitions, not after every tool call. A reference must
resolve to durable evidence. If the log is missing, preserve essential evidence
in the record. Concision must not erase decisions, failed checks or unresolved risks.
