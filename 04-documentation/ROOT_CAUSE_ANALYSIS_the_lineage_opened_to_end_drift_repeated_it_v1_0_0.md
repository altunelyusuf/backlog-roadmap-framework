# Root-cause analysis — the lineage opened to end drift repeated it (v1.0.0)

Owner's instruction, 2026-10-06: Lineage_2 was opened to prevent shallow development (no grooming, no SDLC, no
modelling, no refinement) and fell into the same trap; find the root cause and build preventive mechanisms: hooks,
rulings, enforcement and best practice. Ruling G101. Evidence base: an adopting project at `cbc0a89`, read through the repository
connection on 2026-10-06 (its `.claude/settings.json`, `ci-tests.yml`, drift log, the order-check and pipeline-verify
output quoted in its handover). Anything not re-run is marked.

## What the evidence shows
- **Its only hook auto-allows every permission request.** `.claude/settings.json` holds one hook, `PermissionRequest`,
  which answers `allow`. Nothing sits between an agent and a commit.
- **Its CI never reads the register.** `ci-tests.yml` runs the app test suite, two behaviour gates, a SHACL check of the
  business-configuration ontology and the shape-drift check. It runs "the Lineage_2 specs (merged worker streams)": tests
  written for ledger-driven work, so green CI was evidence of the off-register work, not a check on it.
- **The drift log is a series of prose rules.** Twenty dated entries (counted), eighteen of which carry a "Standing ..."
  paragraph. The 2026-09-23 directive ("an incompliance is found and built, not disclosed and accepted") is the same
  family as 2026-10-06, which happened afterwards. A rule that exists only as text did not hold against throughput.
- **The coordinator's own practice sentence is itself prose again**: "the coordinator checks `items>0` ... before
  assigning any worker". Nothing makes it.
- **Every pipeline tool printed PASS on the empty set**: the verifier said "4 of 5 outputs, Stage_Backlog absent, PASS", the
  order check said ORDERED with `items=0`.

## Root causes (each tied to evidence and to what now answers it)
| # | Root cause | Answered by |
|---|---|---|
| 1 | No positive start condition. Every gate asked "did something go wrong among the items that exist"; none asked "may work start". | Start gate `backlog_execution_ready` (v1.331.0, now a callable function), `AWAITING_BACKLOG` in the order check |
| 2 | Safeguards were prose or after the act; none stood in the path of the act (an edit, a commit, a push, a merge). | The work guard, four layers (below) |
| 3 | A second system of record was allowed to feed work: a 454-row ledger outside the register, and CI that tested it. Nothing traces a code change to a register item. | `Work-Item:` trailer on every work commit, checked against the register at commit and in CI; the ledger is a view, never a source |
| 4 | A green verdict was read as compliance, without its examined count. | `INCOMPLETE` verdict and `--require-complete` in the pipeline verifier (v1_7_0); the order check already prints nothing-examined (v1.331.0); rule G101 |
| 5 | Closing a stage creates no "next required act". Objective closed 2026-09-28; the proposal said "the Backlog stage" and nothing made anyone take it. | SessionStart prints state and NEXT REQUIRED ACT at every session start and after every compaction |
| 6 | A correction was filed as prose, so it decayed across sessions and compactions. | G101: a correction is closed only by a check that fails; a "standing practice" without one is an open finding |
| 7 | Parallel workers were dispatched from the ledger and each worker's checkout had no hooks (git hooks do not travel with a clone). | The SessionStart hook re-arms the git hooks in every clone; project `.claude/settings.json` travels; CI is the layer a worker cannot skip |

## Classification (L-114)
Would the outcome have occurred without the safeguards that existed? Yes: with every one of them present, 398 rows were
executed outside the register. So this is a **genuine gap**, in two places: the gates (causes 1, 4: this package) and the
project's practice and enforcement (causes 2, 3, 5, 6, 7: the guard is the answer; installing it is the project's act).
It is not a safeguard working.

## Dispositions of what the owner named (L-113)
| Asked | Disposition |
|---|---|
| Hooks | Built and proven on a real repository: Claude Code SessionStart and PreToolUse hooks; git commit-msg and pre-push hooks |
| Rulings | G101 (discipline v72_0_0) |
| Enforcement | Built: CI range check (the layer `--no-verify` cannot skip), `--require-complete`, guard that fails closed and cannot pass over nothing |
| Best practices | Written: `WORK_GUARD_ADOPTION_GUIDE`, including coordinator and worker practice and what the ledger may be |
| Other | Declined, with reason: a lint over a project's drift log (project-specific; the rule in G101 is the control); retrofitting examined counts into every gate (only the two tools that read the empty set were changed; the other tools are not shown to) |

## What is not claimed
- Whether Claude Code applies project hooks inside delegated worker sessions is not verified here. The commit hook
  (re-armed at session start) and CI do not depend on it.
- The Bash-write detection is a heuristic. A write that evades it is caught at the commit and in CI.
- The guard stops work that is not in the register. It cannot judge whether the grooming in the register is good: the
  shapes do that, after the fact, and a ready item can still be shallow. That is the residual risk.
- Installing it in an adopting project, and marking the CI job required, are the adopting project's and the owner's acts; nothing here edits
  their repository.
