#!/usr/bin/env python3
"""backlog_recording_integrity_probe v1.0.0 -- re-runnable proof of the four routes G115 closes (shapes v1.165.0).

Each scenario is a tiny graph judged by the CURRENT validator; the probe reads only the named shape's own message.
  First move     fires: the earliest recorded move leaves Ready (Proposed jumped to In Progress); leaves In Progress   silent: begins at Proposed; absence reason stated
  Unstarted      fires: a Proposed item with startedAt; a Ready, In Progress or Suspended item with finishedAt        silent: Ready with startedAt (after a return); Done and Cancelled with finishedAt
  Two values     fires: two different finishedAt; two different startedAt                                              silent: one value; one instant written in two time zones
  Equal span     fires: start = finish; a span under the adopter's shortSpanThreshold                                  silent: no threshold and a short span; an explanation; an absence reason; a long span
  Scope          silent: rule sets not adopted; a lineage adopts and the item belongs to another lineage
  Gap message    fires with the NAMES of the skipped states (checked in probe backlog_status_history_probe)
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
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/recording-integrity-probe#> .\n"
REG = lambda rs, extra="": f"x:Reg a backlog:Backlog ; backlog:isRegisterRoot true ; backlog:adoptsRuleSet backlog:{rs} {extra}.\n"
LIN = lambda rs: f"x:L1 a backlog:Lineage ; backlog:adoptsRuleSet backlog:{rs} .\nx:L2 a backlog:Lineage .\n"
H = "x:P a backlog:Executor_IndividualHuman .\n"
D = lambda hh, day="14": f"2026-10-{day}T{hh}Z"
dt = lambda v: f'"{v}"^^xsd:dateTime'
def ev(n, tr, at):
    return f'x:E{n} a backlog:TransitionEvent ; backlog:transitionedItem x:W ; backlog:viaTransition backlog:{tr} ; backlog:transitionedAt {dt(at)} .\n'
def item(state, starts=(), fins=(), extra="", lineage=None):
    t = f"x:W a backlog:Task ; backlog:hasState backlog:{state} ; backlog:responsible x:P"
    for s in starts: t += f" ; backlog:startedAt {dt(s)}"
    for f in fins: t += f" ; backlog:finishedAt {dt(f)}"
    if lineage: t += f" ; backlog:belongsToLineage x:{lineage}"
    return t + (" ; " + extra if extra else "") + " .\n"
SH, FP = "RS_StatusHistoryRecorded", "RS_FlowPointsRecorded"
FM, UNS, TWO, EQ = ("G115: the earliest recorded move", "G115: this work item carries a startedAt or finishedAt that its state cannot have",
                    "G115: this work item has two different values", "G115: this work item's startedAt equals its finishedAt")
A, B, C = D("09:00:00"), D("11:00:00"), D("11:00:01")
Z = '"x"' ; why = 'backlog:statusHistoryAbsenceReason "found under way"'
SCEN = {
  "first move leaves Ready (probe C)":        (REG(SH) + H + item("Done", [A], [B]) + ev(1, "T_Start", A) + ev(2, "T_Complete", B), FM, 1),
  "first move leaves In Progress":            (REG(SH) + H + item("Done", [A], [B]) + ev(2, "T_Complete", B), FM, 1),
  "history begins at Proposed":               (REG(SH) + H + item("Done", [A], [B]) + ev(1, "T_Refine", D("08:00:00")) + ev(2, "T_Start", A) + ev(3, "T_Complete", B), FM, 0),
  "first move at Ready, reason stated":       (REG(SH) + H + item("Done", [A], [B], extra=why) + ev(1, "T_Start", A) + ev(2, "T_Complete", B), FM, 0),
  "no moves at all":                          (REG(SH) + H + item("Proposed"), FM, 0),
  "Proposed carries startedAt":               (REG(FP) + H + item("Proposed", [A]), UNS, 1),
  "Ready carries finishedAt":                 (REG(FP) + H + item("Ready", [A], [B]), UNS, 1),
  "In Progress carries finishedAt":           (REG(FP) + H + item("InProgress", [A], [B]), UNS, 1),
  "Suspended carries finishedAt":             (REG(FP) + H + item("Suspended", [A], [B]), UNS, 1),
  "Ready keeps startedAt after a return":     (REG(FP) + H + item("Ready", [A]), UNS, 0),
  "Done with both":                           (REG(FP) + H + item("Done", [A], [B]), UNS, 0),
  "Cancelled with finishedAt":                (REG(FP) + H + item("Cancelled", [A], [B]), UNS, 0),
  "two different finishedAt":                 (REG(FP) + H + item("Done", [A], [B, C]), TWO, 1),
  "two different startedAt":                  (REG(FP) + H + item("Done", [A, B], [C]), TWO, 1),
  "one value of each":                        (REG(FP) + H + item("Done", [A], [B]), TWO, 0),
  "one instant in two time zones":            (REG(FP) + H + item("Done", [A], ["2026-10-14T11:00:00Z", "2026-10-14T14:00:00+03:00"]), TWO, 0),
  "start equals finish":                      (REG(FP) + H + item("Done", [B], [B]), EQ, 1),
  "span under the stated threshold":          (REG(FP, '; backlog:shortSpanThreshold "PT2M"^^xsd:dayTimeDuration ') + H + item("Done", [B], [C]), EQ, 1),
  "short span, no threshold stated":          (REG(FP) + H + item("Done", [B], [C]), EQ, 0),
  "equal pair with an explanation":           (REG(FP) + H + item("Done", [B], [B], extra='backlog:shortSpanExplanation "scripted rename"'), EQ, 0),
  "equal pair with an absence reason":        (REG(FP) + H + item("Done", [B], [B], extra='backlog:flowPointAbsenceReason "start unknown"'), EQ, 0),
  "span above the stated threshold":          (REG(FP, '; backlog:shortSpanThreshold "PT2M"^^xsd:dayTimeDuration ') + H + item("Done", [A], [B]), EQ, 0),
  "not adopted":                              (H + item("Proposed", [A], [B]), UNS, 0),
  "lineage adopts, other lineage":            (H + LIN(FP) + item("Proposed", [A], lineage="L2"), UNS, 0),
  "lineage adopts, item belongs":             (H + LIN(FP) + item("Proposed", [A], lineage="L1"), UNS, 1),
}
bad = []
with tempfile.TemporaryDirectory() as d:
    for name, (body, key, want) in SCEN.items():
        f = os.path.join(d, "s.ttl"); open(f, "w").write(HEAD + body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=600).stdout
        got = sum(1 for ln in out.splitlines() if "[Violation]" in ln and key in ln)
        print(f"{name:42} expected {want} got {got}")
        if got != want: bad.append(f"{name}: expected {want}, got {got}")
print("validator :", os.path.basename(val)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
