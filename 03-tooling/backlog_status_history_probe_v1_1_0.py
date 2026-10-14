#!/usr/bin/env python3
"""backlog_status_history_probe v1.1.0 -- re-runnable proof of the status-history obligation (shapes v1.163.0, G113).

Each scenario is a tiny graph judged by the CURRENT validator; the probe reads only the named shape's own message.
  Unrecorded     fires: In Progress with no recorded move; Suspended with no recorded move   silent: Proposed with no move; a stated absence reason; recorded move into the current state
  No start       fires: Done with only the move into Done                                      silent: Start and Complete both recorded
  Gap            fires: Decompose (to Refined), then a Start that leaves Ready (the move into Ready is missing)   silent: the full chain; a suspend and resume cycle
  Moment         fires: a move stamped exactly midnight                                        silent: a move stamped at 09:30
  Flow points    fires: startedAt differs from the first move into In Progress; startedAt missing; finishedAt differs from the Done move
                 silent: both equal the moves
  Scope          silent: the rule set not adopted; a lineage adopts and the item belongs to another lineage
  Workflow       silent: a workflow written before Suspended (it covers the six old states only) is not made inconsistent by the new state
v1.1.0 (G115): the gap message names the skipped states (leaves X, previous move entered Y); the probe asserts the names.
Exit 0 when every expectation holds, 1 otherwise.
"""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    for pat in ("03-tooling/backlog_validate_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl", "01-ontologies/backlog_abox_v*.ttl"):
        print(latest(pat))
    print(os.path.abspath(__file__)); sys.exit(0)
val = sorted(glob.glob(os.path.join(HERE, "backlog_validate_v*.py")), key=sv)[-1]
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/status-history-probe#> .\n"
RS = "RS_StatusHistoryRecorded"
REG = f"x:Reg a backlog:Backlog ; backlog:isRegisterRoot true ; backlog:adoptsRuleSet backlog:{RS} .\n"
LIN = lambda rs=RS: f"x:L1 a backlog:Lineage ; backlog:adoptsRuleSet backlog:{rs} .\nx:L2 a backlog:Lineage .\n"
H = "x:P a backlog:Executor_IndividualHuman .\n"
D = lambda hh: f"2026-10-14T{hh}Z"
def ev(n, tr, at):
    return f'x:E{n} a backlog:TransitionEvent ; backlog:transitionedItem x:W ; backlog:viaTransition backlog:{tr} ; backlog:transitionedAt "{at}"^^xsd:dateTime .\n'
def item(state, start=None, fin=None, why=None, lineage=None):
    t = f"x:W a backlog:Task ; backlog:hasState backlog:{state} ; backlog:responsible x:P"
    if start: t += f' ; backlog:startedAt "{start}"^^xsd:dateTime'
    if fin: t += f' ; backlog:finishedAt "{fin}"^^xsd:dateTime'
    if why: t += f' ; backlog:statusHistoryAbsenceReason "{why}"'
    if lineage: t += f" ; backlog:belongsToLineage x:{lineage}"
    return t + " .\n"
UN, NS, GAP, MOM, MIS = "no recorded move (TransitionEvent) enters its current state", "no recorded move enters In Progress", "leaves a state that the previous recorded move did not enter", "is stamped exactly midnight", "differs from the instant of its first recorded move into In Progress, or its finishedAt"
UN, MIS = "G113: this work item has left Proposed", "G113: this work item's startedAt is missing"
NS, GAP, MOM = "G113: this work item is In Progress, Suspended or Done but no recorded move", "G113: a recorded move of this work item leaves http://example.org/backlog#Ready, but the previous recorded move entered http://example.org/backlog#Refined", "G113: a recorded move of this work item is stamped exactly midnight"
S1, S2, S3, S4 = D("08:00:00"), D("09:30:00"), D("11:00:00"), D("13:00:00")
CHAIN_START = ev(1, "T_Refine", S1) + ev(3, "T_Start", S3)
WF = "x:Wf a backlog:Workflow ; backlog:hasTransition backlog:T_Refine , backlog:T_RefinedToReady , backlog:T_Start , backlog:T_Complete , backlog:T_Return , backlog:T_Defer , backlog:T_WithdrawProposed , backlog:T_WithdrawReady , backlog:T_WithdrawInProgress , backlog:T_Decompose .\n"
WFS = "workflow written before Suspended"
SCEN = {
  "unrecorded: In Progress, no move":      (REG + H + item("InProgress"), UN, 1),
  "unrecorded: Suspended, no move":        (REG + H + item("Suspended"), UN, 1),
  "Proposed, no move":                     (REG + H + item("Proposed"), UN, 0),
  "absence reason stated":                 (REG + H + item("InProgress", why="moved before the obligation began"), UN, 0),
  "recorded move into the current state":  (REG + H + item("InProgress", start=S3) + CHAIN_START, UN, 0),
  "no start: only the Done move":          (REG + H + item("Done", fin=S4) + ev(1, "T_Complete", S4), NS, 1),
  "start and complete recorded":           (REG + H + item("Done", start=S3, fin=S4) + CHAIN_START + ev(4, "T_Complete", S4), NS, 0),
  "gap: Ready move missing":               (REG + H + item("InProgress", start=S3) + ev(1, "T_Decompose", S1) + ev(3, "T_Start", S3), GAP, 1),
  "full chain":                            (REG + H + item("InProgress", start=S3) + CHAIN_START, GAP, 0),
  "suspend and resume cycle":              (REG + H + item("InProgress", start=S3) + CHAIN_START + ev(4, "T_Suspend", S4) + ev(5, "T_Resume", D("15:00:00")), GAP, 0),
  "suspended, recorded":                   (REG + H + item("Suspended", start=S3) + CHAIN_START + ev(4, "T_Suspend", S4), UN, 0),
  "midnight move":                         (REG + H + item("InProgress", start=D("00:00:00")) + ev(1, "T_Refine", D("00:00:00")), MOM, 1),
  "move at 09:30":                         (REG + H + item("Ready") + ev(1, "T_Refine", S2), MOM, 0),
  "startedAt differs from the move":       (REG + H + item("InProgress", start=S2) + CHAIN_START, MIS, 1),
  "startedAt missing":                     (REG + H + item("InProgress") + CHAIN_START, MIS, 1),
  "finishedAt differs from the Done move": (REG + H + item("Done", start=S3, fin=S3) + CHAIN_START + ev(4, "T_Complete", S4), MIS, 1),
  "flow points equal the moves":           (REG + H + item("Done", start=S3, fin=S4) + CHAIN_START + ev(4, "T_Complete", S4), MIS, 0),
  "rule set not adopted":                  (H + item("InProgress"), UN, 0),
  "lineage adopts, other lineage":         (H + LIN() + item("InProgress", lineage="L2"), UN, 0),
  "lineage adopts, item belongs":          (H + LIN() + item("InProgress", lineage="L1"), UN, 1),
  WFS:                                     (H + WF, "leaves a lifecycle state unreachable and unleavable", 0),
}
bad = []
with tempfile.TemporaryDirectory() as d:
    for name, (body, key, want) in SCEN.items():
        f = os.path.join(d, "s.ttl"); open(f, "w").write(HEAD + body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=600).stdout
        got = sum(1 for ln in out.splitlines() if "[Violation]" in ln and key in ln)
        print(f"{name:40} expected {want} got {got}")
        if got != want: bad.append(f"{name}: expected {want}, got {got}")
print("validator :", os.path.basename(val)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
