# Work guard — adoption guide (v1.0.0)

Rule: **no change to governed work without a registered, groomed, admitted item.** Four layers, because each alone has
been argued past. Ruling G101.

## Install (one command, idempotent)
```
python3 <tools>/backlog_guard_install_v1_0_0.py REPO --tooling-dir <tools relative to REPO> \
    --register <register.ttl relative to REPO> --lineage <active lineage> \
    --work-path 'app/**' [--work-path ...] [--exempt-path 'app/README.md']
```
Commit the files it writes, then mark the CI job **Backlog work guard** a required status check (a person does this).
The tools must be vendored inside the repository; the hooks run them from there.

| Layer | When | Stops | Can be skipped by |
|---|---|---|---|
| SessionStart | session start, after compaction | nothing; puts state and NEXT REQUIRED ACT in front of the session, re-arms git hooks in the clone | not a stop |
| PreToolUse | before an edit or a Bash write to a governed path | work on a lineage that is not READY | a session without project hooks |
| commit-msg, pre-push | before a commit, before a push | a work commit with no ready `Work-Item:`; a push holding one | `--no-verify`, a clone whose hooks are not armed |
| CI range check | every push and pull request | any work commit in the range outside the register | nobody, once required |

## Configuration (`.backlog-guard.json`)
`register`, `active_lineage`, `work_paths`, `exempt_paths`, `governed_from` (the commit before which history is not
examined: set at install, reset to the restart commit after a recovery). The guard fails closed on an empty `work_paths`,
a work path that matches no tracked file, a missing or empty register, or a lineage that is not configured: a guard over
nothing is the failure it exists to stop.

## Practice
- **Coordinator.** Before any assignment run `backlog_execution_ready … --lineage L --item I` and read the examined
  counts before the verdict. A worker brief names the `Work-Item` it serves; a brief without one is not dispatched.
- **Worker.** Every commit that changes governed work carries `Work-Item: NAME` (several allowed). A worker that finds
  work with no item stops and reports; it does not create the item to unblock itself.
- **The ledger** is a view over the register (what is done, what is open). It may not be a source of work, and a test suite
  for ledger-driven work is not evidence of conformance.
- **Closing a stage** names the next required act. `AWAITING_BACKLOG`, `INCOMPLETE` and `NOT READY` are stop signs, not
  advisories.
- **A drift entry is closed by a check that fails,** not by a standing practice (G101). If none exists, say so and open a
  handover to the framework.

## Limits
Hook behaviour inside delegated worker sessions is not verified here; the commit hook and CI do not depend on it. The
Bash-write detection is a heuristic. The guard cannot judge the quality of grooming: a ready item can still be shallow.
