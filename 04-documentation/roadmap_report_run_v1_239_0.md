<!-- Retained roadmap report run, backlog-roadmap-framework v1.239.0, brsf-session 2026-09-09. Written by backlog_roadmap_report_v1_6_0.py on register v9.68.0 (pre-release state), retained under configuration:RoadmapReportConvention as the first Role_ProgressReport artifact of fw:RegisterPackage_v1_239_0. -->

roadmap report  : computed 2026-09-09T07:33:34
register        : backlog_framework_register_abox_v9_68_0.ttl
method          : http://example.org/backlog#Method_WSJF
tooling         : rdflib 7.6.0, backlog_roadmap_report v1.6.0

== 1. NEXT (throughput model) ==
  nothing startable and scored

== 2. NEXT (launch-scoped model) ==
  no launch gate open — scope collapsed to the whole register (R3)
  nothing startable and scored inside the active gate

== 3. Full ranked backlog — COMPUTED ordering by score ==
     Position here is derived from hasScoreValue at run time. It is NOT
     backlog:hasRoadmapRank; nothing in this section is an assertion in the
     register. Ties in this ordering are ties in the SCORE, and carry none of
     the uniqueness obligation a declared roadmap rank does.
     declared roadmap ranks in this register: 0
  BRF-EP21   Done         score   8.00  startable
  BRF-EP22   Done         score   6.00  startable
  BRF-EP23   Done         score   6.00  startable
  BRF-EP26   Done         score   5.00  startable
  BRF-EP24   Done         score   4.00  startable
  BRF-EP25   Done         score   3.00  startable

== 4. Flagged items (not yet scoreable) ==
  BRF-EP_Rulings_S1 Scored at epic level; scoring a decomposition child alongside its scored parent double-counts.
  BRF-EP_Rulings_S2 Scored at epic level; scoring a decomposition child alongside its scored parent double-counts.
  BRF-EP_CodeTables_S1 Scored at epic level; scoring a decomposition child alongside its scored parent double-counts.
  BRF-EP_CodeTables_S2 Scored at epic level; scoring a decomposition child alongside its scored parent double-counts.
  BRF-EP_RuleExec_S1 Scored at epic level; scoring a decomposition child alongside its scored parent double-counts.
  BRF-EP_RuleExec_S2 Scored at epic level; scoring a decomposition child alongside its scored parent double-counts.
  BRF-EP_ScriptDecisions_S1 Scored at epic level; scoring a decomposition child alongside its scored parent double-counts.
  BRF-EP_StandardRows_S1 Scored at epic level; scoring a decomposition child alongside its scored parent double-counts.
  BRF-EP_StandardRows_S2 Scored at epic level; scoring a decomposition child alongside its scored parent double-counts.
  BRF-PKG-GOV A package is a grouping; its members carry the scores.
  BRF-PKG-EXEC A package is a grouping; its members carry the scores.
  BRF-S_Tables_B1 Scored at epic level.
  BRF-S_Tables_B2 Scored at epic level.
  BRF-S_Tables_B3 Scored at epic level.
  BRF-S_Tables_B4 Scored at epic level.
  BRF-S_Tables_B5 Scored at epic level.
  BRF-S_Tables_B6 Scored at epic level.
  BRF-PKG-CD A package is a grouping; its members carry the scores.

== 10. Flow and forecast — COMPUTED, nothing here is stored ==
  cycle time    : 38 finished item(s); median 0.02 d, range 0.02-0.77 d
  item age      : nothing started and unfinished
  velocity      : 8.00 item(s) per iteration over 6 closed iteration(s)
      It7          7 completed
      It8          15 completed
      It9          8 completed
      It10         12 completed
      It11         4 completed
      It_CD1       2 completed
  remaining     : 0 open item(s) -> 0.0 iteration(s) at the observed rate
                  This is arithmetic, not a Forecast. A Forecast is an artifact
                  that must carry its assumptions; see backlog:Forecast.

  measurement-confirmed progress:
      BRF-EP22                 -> Obj_TablesExported       : MOVED 23.0 -> 0.0
      BRF-EP22                 -> Obj_NoNewClasses         : MOVED 0.0 -> 0
      BRF-EP22                 -> Obj_NoProseLost          : MOVED 0.0 -> 0
      BRF-EP23                 -> Obj_RulesDecidedInCode   : MOVED 3.0 -> 0.0
      BRF-EP23                 -> Obj_NoNewClasses         : MOVED 0.0 -> 0
      BRF-EP23                 -> Obj_NoProseLost          : MOVED 0.0 -> 0
      BRF-EP21                 -> Obj_RulingsQueryable     : MOVED 18.0 -> 0
      BRF-EP21                 -> Obj_NoNewClasses         : MOVED 0.0 -> 0
      BRF-EP21                 -> Obj_NoProseLost          : MOVED 0.0 -> 0
      BRF-EP24                 -> Obj_CodeDecisions        : MOVED 3.0 -> 0.0
      BRF-EP24                 -> Obj_NoNewClasses         : MOVED 0.0 -> 0
      BRF-EP24                 -> Obj_NoProseLost          : MOVED 0.0 -> 0
      BRF-EP25                 -> Obj_RowsUnchecked        : MOVED 186.0 -> 15.0
      BRF-EP25                 -> Obj_NoNewClasses         : MOVED 0.0 -> 0
      BRF-EP25                 -> Obj_NoProseLost          : MOVED 0.0 -> 0
      BRF-INIT01               -> Obj_BRSFConformanceHeld  : MOVED 0.0 -> 0
      CD-S01                   -> Obj_CD_NoOutOfScopeWork  : MOVED 0 -> 0
      BRF-S-RQ01               -> Obj_RulingsQueryable     : MOVED 25 -> 0

== 5. Silent-gap check ==
  silent gaps: 0 (must read zero)

== 6. Launch readiness by package ==
  no launch gates declared

== 7. Package-level ranking (multi-factor, non-capabilities excluded) ==
  no container carries a judged score

== 8. Orphan and package-coverage check ==
  orphan items      : 6 BRF-REL-It11, BRF-REL-It9, BRF-REL-It_CD1, BRF-REL-It10, BRF-REL-It8, BRF-REL-It7
  empty containers  : 0 

== 9. Lifecycle and workflow ==
  item states  : Proposed 0, Ready 0, InProgress 0, Done 44, Cancelled 2
  workflow Workflow_Default permits:
    complete   InProgress   -> Done         guard: ASK { ?h backlog:harnessFor ?i ; backlog:harnessComplete t
    defer      Ready        -> Proposed     guard: ASK { } # unguarded: readiness decays when the item's assu
    refine     Proposed     -> Ready        guard: ASK { ?i backlog:hasAcceptanceCriterion ?a . ?r backlog:re
    return     InProgress   -> Ready        guard: ASK { } # unguarded: work may always be put back down, and
    start      Ready        -> InProgress   guard: ASK { ?i backlog:dependsOn ?d . ?d backlog:hasState ?s . F
    withdraw   InProgress   -> Cancelled    guard: ASK { ?i backlog:hasRationale ?r } # must return true for 
    withdraw   Proposed     -> Cancelled    guard: ASK { ?i backlog:hasRationale ?r } # must return true for 
    withdraw   Ready        -> Cancelled    guard: ASK { ?i backlog:hasRationale ?r } # must return true for 
  states not explained by recorded history: 0 

report individual emitted: /tmp/rr.ttl
