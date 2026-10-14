# Root-cause analysis — an item is registered at completion, and its times are typed afterwards (v1.0.0)

Asked for by a handover of the agentic-systems session (2026-10-14), prompted by the owner's instruction to find the root cause of equal and implausible start and finish times. Ruling G115. Cases: that session's register (measured by that session; planted probes re-run here on v1.393.0), and this package's own archive register (measured here with `backlog_flow_point_git_trace`). Anything not re-run is marked.

## The class
A work item is written into the register after the work is done, already Done, and its `startedAt`, `finishedAt` and state are typed from memory. The states between Proposed and Done never exist in any commit.

## Case 1 — the agentic-systems register (their measurement; probes C, F, H and I reproduced here on v1.393.0)
83 items reached Done. 55 were only ever committed as Done, 18 went Proposed to Done in one commit, 10 passed through In Progress or Ready. 29 finishes lay later than the commit that first recorded the item Done (typed round times, some seven weeks ahead); 23 items carried two `finishedAt`; 2 had start equal to finish; 4 spans were under two minutes; 52 starts were midnight.

## Case 2 — this package's archive register (measured here, read-only)
`backlog_framework_archive_abox`, 298 items: 288 first seen in a commit as Done and 10 as Cancelled (no item was ever committed In Progress); 0 finishes later than the commit that recorded them; 0 items with two values; 7 with finish not after start (5 equal, 2 earlier than the start); 11 with a midnight point. The package's own practice did not type finishes into the future, which the later rules (G112, G113) had already been written against; it did register items at completion, which is the class.
*Limit of the evidence:* the archive was assembled from the live register in bulk, so "first seen as Done" partly measures the archiving, not the practice. The comparison is therefore a lower bound on the first cause and says nothing against the second.

## Root causes
| # | Cause | Evidence | Answered by |
|---|---|---|---|
| 1 | Items are written at the end of the work, not when it is planned, started and finished. | Case 1: 55 of 83 only ever Done; Case 2: 288 of 298 | `FirstMoveLeavesProposedShape`; the start gate asks for the recording rule sets before the first item starts (`backlog_execution_ready` v1.2.0) |
| 2 | An instant is typed from memory, not read from a clock at the moment of the change. | 29 finishes after their commit; 52 midnights | `backlog_flow_point_git_trace` (the witness is the history, run as a gate); G113 midnight rule; no in-data bound (see G115 Q4) |
| 3 | A correction adds a value instead of replacing one. | 23 items with two finishes | `SingleValuedFlowPointShape` |
| 4 | An equal or very short span passes without a cause. | EP32 and its story (one instant typed twice); Case 2: 5 equal | `EqualSpanShape` (`shortSpanExplanation`) |
| 5 | A start or finish sits on work that has not reached it. | probe H: a Proposed item carrying both | `FlowPointsOnlyWhenStartedShape` |
| 6 | Recording was an opt-in rule, and a new lineage opened without it. | the register went a month without the obligation | the start gate (cause 1) and `recordingRuleSetsDeclinedReason`: a lineage that has not started either adopts or says why not |
| 7 | The first recorded move could leave any state, so Ready and Proposed were skippable with a plausible `T_Start` and `T_Complete`. | probe C | `FirstMoveLeavesProposedShape` |

## Classification (L-114)
Would the outcome have occurred without the safeguards that existed? Yes, in both cases: with G112 and G113 present a session that typed a plausible `T_Start` and `T_Complete` passed every rule. A genuine gap in the framework (causes 3 to 7) on top of a practice (causes 1 and 2) that no register rule can fully remove, because the clock is the session's.

## What is not claimed
Git author dates are the working session's clock; a commit time is the latest instant a change can have been made, not when the work happened. The tool shows an impossible date; it cannot prove a plausible one. Two cases from two registers of one owner are not a population: other projects may have other causes or none. The probes were planted on single items; combinations (several lineages, successions, the severity audit) were not tried.

## Best practice that follows (the lessons the discipline asks to be reused)
1. Register the item when it is planned (Proposed), move it when it is refined, ready, started, suspended and done, each move with its instant.
2. Take the instant from a clock at the moment of the move; never reconstruct one from memory or round it.
3. Replace a value, never add one beside it.
4. Explain an equal or very short pair before committing; an equal pair is a signal to open an analysis, never to pass.
5. For work already under way when it is registered, say so (`statusHistoryAbsenceReason`) and state the start as the earliest instant the history allows, flagged as an upper limit.
6. Run `backlog_flow_point_git_trace` on a register that has history, before adopting the rule sets and at every release.
