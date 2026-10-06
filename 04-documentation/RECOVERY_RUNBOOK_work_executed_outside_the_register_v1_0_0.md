# Recovery runbook — work executed outside the register (v1.0.0)

Applies when real work was done on a lineage that had no Backlog stage output or no registered items
(Lineage_2 at an adopting project is the precedent; ruling G100). Do not decide per instance; follow the steps.

## Prevention first
Before every assignment run `backlog_execution_ready_v1_0_0.py REGISTER.ttl --lineage NAME [--item NAME]`
(exit 0 READY, 2 NOT READY). Run the order check with `--no-empty-pass`; `AWAITING_BACKLOG` exits 2.

## Steps
1. **Stop.** No further work on the lineage.
2. **Register truthfully.** One Story per real unit of work (the Story definition's grain), real dates,
   Done only where evidence exists, nothing invented. Release streams are Iterations; releases are DeploymentUnits.
3. **Registration commit alone.** The order check reads BYPASS. That verdict is the finding.
4. **Record the bypass in a separate commit.** `LineageBypass` is emitted by the tool from git, never by hand;
   freeze the lineage (`lineageFrozen`). The owner may append.
5. **Restart by the owner**, in its own later commit (`LineageRestart`): every output is retracted
   (`outputRetracted`), items are flagged `preLineageItem`, rebuild from Mission.
6. **Rebuild one commit per stage** (Mission, Scope, Goal, Objective, Backlog); parts of one stage share a commit.
   The owner re-affirms the Mission (G14).
7. **Admit.** The active Backlog output admits the flagged items (`admittedByOutput`).
8. **What stays required** on admitted items: evidence, criterion, harness, `lastAuditedAt`, finish point,
   modality. **Exempt:** concern declaration and planning event (the two act-record shapes).
9. **Groom** the open rows in the rebuilt Backlog.
10. **Verify:** order check, pipeline verify, start gate, validator.

## Strategy decision table (RecoveryStrategy)
| Situation | Strategy |
|---|---|
| A ScopeChange removes an unserved deliverable first | TransformSimplify |
| ORDERED template lineage | TransformReduce |
| Single-deliverable partition, too large for one restart | DivideAndConquer (items spanning several deliverables stay with the parent; if most do, the registration grain is wrong) |
| Otherwise | DecreaseByOne (default) |
