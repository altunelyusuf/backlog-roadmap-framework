#!/usr/bin/env python3
"""Probe of backlog_date_report (G188) on a planted register whose dates are computed by hand: box 1 planned 00:00-01:00 and finished 02:00 (+1.0 h, LATE); box 2 open, planned to end 05:00.
O1 (base 06:00): movers in box 1, box 2 and in no box -> updated 05:00 (-1.0 h), one mover in no box; observation 0 at 03:00 reaches its target (decrease) -> finished 03:00 (-3.0 h).
O2 (base 04:00): mover in box 2 -> updated 05:00 (+1.0 h, LATE); no observation -> open."""
import glob, re, subprocess, sys, tempfile, os
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", p)[0]]
TOOL = sorted(glob.glob(PKG + "/03-tooling/backlog_date_report_v*.py"), key=sv)[-1]
X = "^^xsd:dateTime"
T = lambda h: '"2026-11-02T%s:00:00Z"%s' % (h, X)
REG = f"""@prefix backlog: <http://example.org/backlog#> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> . @prefix fw: <http://example.org/rp#> .
fw:L a backlog:Lineage .
fw:It1 a backlog:Iteration ; backlog:belongsToLineage fw:L ; backlog:hasState backlog:Done ; backlog:iterationStart {T('00')} ; backlog:iterationEnd {T('02')} .
fw:PB1 backlog:baselineFor fw:It1 ; backlog:isCurrentBaseline true ; backlog:hasBaselineStart {T('00')} ; backlog:hasBaselineEnd {T('01')} .
fw:It2 a backlog:Iteration ; backlog:belongsToLineage fw:L ; backlog:hasState backlog:InProgress ; backlog:iterationStart {T('02')} .
fw:PB2 backlog:baselineFor fw:It2 ; backlog:isCurrentBaseline true ; backlog:hasBaselineStart {T('02')} ; backlog:hasBaselineEnd {T('05')} .
fw:E1 backlog:plansItem fw:S1 ; backlog:plannedInto fw:It1 . fw:E2 backlog:plansItem fw:S2 ; backlog:plannedInto fw:It2 .
fw:O1 a backlog:Objective ; backlog:belongsToLineage fw:L ; backlog:hasCheckpoint fw:C1 ; backlog:metricMovableBy fw:S1 , fw:S2 , fw:S3 ; backlog:hasTargetValue 0 ; backlog:hasTargetDirection backlog:Dir_Decrease .
fw:C1 a backlog:ObjectiveCheckpoint ; backlog:checkpointDate {T('06')} .
fw:Ob1 backlog:observationFor fw:O1 ; backlog:hasObservedValue 4 ; backlog:observedAt {T('01')} .
fw:Ob2 backlog:observationFor fw:O1 ; backlog:hasObservedValue 0 ; backlog:observedAt {T('03')} .
fw:O2 a backlog:Objective ; backlog:belongsToLineage fw:L ; backlog:hasCheckpoint fw:C2 ; backlog:metricMovableBy fw:S2 ; backlog:hasTargetValue 0 ; backlog:hasTargetDirection backlog:Dir_Decrease .
fw:C2 a backlog:ObjectiveCheckpoint ; backlog:checkpointDate {T('04')} .
fw:O3 a backlog:Objective ; backlog:belongsToLineage fw:L ; backlog:hasCheckpoint fw:C3 ; backlog:hasTargetValue 0 ; backlog:hasTargetDirection backlog:Dir_Hold .
fw:C3 a backlog:ObjectiveCheckpoint ; backlog:checkpointDate {T('06')} .
fw:Oa backlog:observationFor fw:O3 ; backlog:hasObservedValue 0 ; backlog:observedAt {T('01')} . fw:Ob backlog:observationFor fw:O3 ; backlog:hasObservedValue 0 ; backlog:observedAt {T('03')} .
fw:O4 a backlog:Objective ; backlog:belongsToLineage fw:L ; backlog:hasCheckpoint fw:C4 ; backlog:hasTargetValue 0 ; backlog:hasTargetDirection backlog:Dir_Hold .
fw:C4 a backlog:ObjectiveCheckpoint ; backlog:checkpointDate {T('06')} .
fw:Oc backlog:observationFor fw:O4 ; backlog:hasObservedValue 0 ; backlog:observedAt {T('01')} . fw:Od backlog:observationFor fw:O4 ; backlog:hasObservedValue 2 ; backlog:observedAt {T('03')} .
fw:O5 a backlog:Objective ; backlog:belongsToLineage fw:L ; backlog:hasCheckpoint fw:C5 ; backlog:hasTargetValue 0 ; backlog:hasTargetDirection backlog:Dir_Decrease .
fw:C5 a backlog:ObjectiveCheckpoint ; backlog:checkpointDate "2026-11-02T08:00:00+02:00"^^xsd:dateTime .
fw:Oe backlog:observationFor fw:O5 ; backlog:hasObservedValue 0 ; backlog:observedAt {T('01')} . fw:Of backlog:observationFor fw:O5 ; backlog:hasObservedValue 3 ; backlog:observedAt {T('02')} .
fw:O6 a backlog:Objective ; backlog:belongsToLineage fw:L ; backlog:hasCheckpoint fw:C6 ; backlog:hasTargetValue 0 ; backlog:hasTargetDirection backlog:Dir_Decrease .
fw:C6 a backlog:ObjectiveCheckpoint ; backlog:checkpointDate "2026-11-02"^^xsd:date .
fw:Og backlog:observationFor fw:O6 ; backlog:hasObservedValue 0 ; backlog:observedAt {T('01')} . fw:Oh backlog:observationFor fw:O6 ; backlog:hasObservedValue 3 ; backlog:observedAt {T('02')} . fw:Oi backlog:observationFor fw:O6 ; backlog:hasObservedValue 0 ; backlog:observedAt {T('03')} .
fw:ImpIn a backlog:Impediment ; backlog:belongsToLineage fw:L ; backlog:hasImpedimentKind backlog:Imp_ToolFault ; backlog:raisedAt {T('01')} ; backlog:resolvedAt {T('03')} .
fw:ImpBefore a backlog:Impediment ; backlog:belongsToLineage fw:L ; backlog:raisedAt "2026-11-01T20:00:00Z"^^xsd:dateTime ; backlog:resolvedAt "2026-11-01T23:00:00Z"^^xsd:dateTime .
fw:ImpOpen a backlog:Impediment ; backlog:belongsToLineage fw:L ; backlog:hasImpedimentKind backlog:Imp_AccessLimit ; backlog:raisedAt {T('03')} .
fw:ImpAfterBox1 a backlog:Impediment ; backlog:belongsToLineage fw:L ; backlog:raisedAt {T('02')} ; backlog:resolvedAt {T('03')} .
"""
fails = 0
def expect(label, ok):
    global fails
    print(("PASS  " if ok else "FAIL  ") + label); fails += (not ok)
with tempfile.TemporaryDirectory() as d:
    rp = d + "/r.ttl"; open(rp, "w").write(REG)
    r = subprocess.run([sys.executable, "-I", TOOL, rp, "--lineage", "L", "--now", "2026-11-02T04:00:00Z"], capture_output=True, text=True)
    o = r.stdout
    l1 = [x for x in o.splitlines() if x.strip().startswith("O1")][0]; l2 = [x for x in o.splitlines() if x.strip().startswith("O2")][0]
    expect("O1: base 06:00, updated 05:00 (-1.0 h), finished 03:00 (-3.0 h), one mover in no box, not late", "base 2026-11-02 06:00Z" in l1 and "updated 2026-11-02 05:00Z -1.0 h" in l1 and "finished 2026-11-02 03:00Z -3.0 h" in l1 and "[1 mover(s) in no box]" in l1 and "LATE" not in l1)
    expect("O2: updated 05:00 is +1.0 h against base 04:00 and marked LATE; no observation reaches the target, so it is open", "updated 2026-11-02 05:00Z +1.0 h" in l2 and "finished open" in l2 and "LATE" in l2)
    l3 = [x for x in o.splitlines() if x.strip().startswith("O3")][0]; l4 = [x for x in o.splitlines() if x.strip().startswith("O4")][0]
    expect("a hold is dated by its latest reading when that reading is the target (O3, 03:00), and is open when the latest reading broke it (O4)", "finished 2026-11-02 03:00Z -3.0 h" in l3 and "finished open" in l4)
    l5 = [x for x in o.splitlines() if x.strip().startswith("O5")][0]; l6 = [x for x in o.splitlines() if x.strip().startswith("O6")][0]
    expect("a decrease that reached its target and was then broken is open (O5); one that reached it again is dated by the first reading of the unbroken run (O6, 03:00)", "finished open" in l5 and "finished 2026-11-02 03:00Z" in l6)
    expect("a date with an offset is printed in UTC (08:00+02:00 is 06:00Z) and a date alone is midnight UTC", "base 2026-11-02 06:00Z" in l5 and "base 2026-11-02 00:00Z" in l6)
    b1 = [x for x in o.splitlines() if x.strip().startswith("It1")][0]; b2 = [x for x in o.splitlines() if x.strip().startswith("It2")][0]
    expect("box 1: planned 00:00 -> 01:00, ended 02:00, +1.0 h, LATE", "plan 2026-11-02 00:00Z -> 2026-11-02 01:00Z" in b1 and "actual end 2026-11-02 02:00Z +1.0 h" in b1 and "LATE" in b1)
    expect("box 2: open, planned to end 05:00, not late", "actual end open" in b2 and "-> 2026-11-02 05:00Z" in b2 and "LATE" not in b2)
    expect("the exit code is 0 without --strict and 1 with it when something is late", r.returncode == 0 and subprocess.run([sys.executable, "-I", TOOL, rp, "--lineage", "L", "--strict"], capture_output=True).returncode == 1)
    expect("an unknown lineage is refused", subprocess.run([sys.executable, "-I", TOOL, rp, "--lineage", "Nope"], capture_output=True).returncode == 2)
    late = subprocess.run([sys.executable, "-I", TOOL, rp, "--lineage", "L", "--now", "2026-11-02T06:00:00Z"], capture_output=True, text=True).stdout
    expect("an open box whose planned end has passed is marked PAST PLAN", "PAST PLAN" in [x for x in late.splitlines() if x.strip().startswith("It2")][0])
    open(rp, "w").write(REG.replace("backlog:hasBaselineEnd " + T('05'), "backlog:foo 1"))
    o2 = subprocess.run([sys.executable, "-I", TOOL, rp, "--lineage", "L"], capture_output=True, text=True).stdout
    expect("a box with no base plan is named, not hidden", "[no base plan]" in o2)
    expect("a mover in a box with no end and no base plan is counted, not dropped", "mover(s) in a box with no end" in o2)
    open(rp, "w").write(REG)
    ob = subprocess.run([sys.executable, "-I", TOOL, rp, "--lineage", "L", "--now", "2026-11-02T06:00:00Z"], capture_output=True, text=True).stdout.split("== Obstacles")[1]
    expect("an impediment open from 01:00 to 03:00 is named under late box 1 (00:00-02:00) with its kind and 2.0 h", "It1" in ob and "ImpIn: Imp_ToolFault, 2.0 h" in ob)
    expect("one that ended before the box began is not named under any box", "ImpBefore" not in ob)
    expect("an impediment still open is named under the box that is PAST PLAN (box 2, 02:00-06:00) with its hours open (3.0 h)", "It2" in ob and "ImpOpen: Imp_AccessLimit, open 3.0 h" in ob)
    expect("one raised at box 1's end and resolved in box 2 is named under box 2 and not under box 1", [l for l in ob.splitlines() if "ImpAfterBox1" in l and l.strip().startswith("It2")] and not [l for l in ob.splitlines() if "ImpAfterBox1" in l and l.strip().startswith("It1")])
    open(rp, "w").write(REG.replace("backlog:hasBaselineEnd " + T('01'), "backlog:hasBaselineEnd " + T('02')))
    nl = subprocess.run([sys.executable, "-I", TOOL, rp, "--lineage", "L", "--now", "2026-11-02T04:00:00Z"], capture_output=True, text=True).stdout.split("== Obstacles")[1]
    expect("when no box is late the section says so and names no impediment", "no late box" in nl and "Imp" not in nl.replace("Obstacles", ""))
    ns = REG.replace("backlog:iterationStart " + T('00') + " ;", "").replace("backlog:hasBaselineStart " + T('00') + " ;", "")
    open(rp, "w").write(ns)
    o3 = subprocess.run([sys.executable, "-I", TOOL, rp, "--lineage", "L", "--now", "2026-11-02T06:00:00Z"], capture_output=True, text=True).stdout.split("== Obstacles")[1]
    expect("a late box with no start is named as having none, and no impediment is placed in it", "no start" in o3 and "It1" in o3)
print("VERDICT   :", "PASS" if not fails else "FAIL"); sys.exit(1 if fails else 0)
