#!/usr/bin/env python3
"""backlog_g169_probe v1.1.0 -- re-runnable proof of the planned control, the daily checkpoint and the demo run (G169).

  Plants small registers and expects the validator to refuse a control activity with no box or a kind that is not control, monitoring or reporting, a run with
  no time or result, a checkpoint with no counts or a blocker with no owner, and a demo run with no criterion, no result or a criterion that is not the item's
  own; and to accept each of them when complete. Exit 0 when every expectation holds."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
TB, AB, SH, VAL = (latest("01-ontologies/backlog_tbox_v*.ttl"), latest("01-ontologies/backlog_abox_v*.ttl"), latest("02-shacl-safeguards/backlog_shacl_v*.ttl"), latest("03-tooling/backlog_validate_v*.py"))
if sys.argv[1:] == ["--deps"]:
    print("\n".join([TB, AB, SH, VAL, os.path.abspath(__file__)])); sys.exit(0)
bad = []
def expect(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (" (%s)" % detail if detail else ""))
    if not ok: bad.append(name)
H = "@prefix backlog: <http://example.org/backlog#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/g169#> .\n"
def run(text):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(H + text)
        out = subprocess.run([sys.executable, VAL, f], capture_output=True, text=True, timeout=900).stdout
    return [ln for ln in out.splitlines() if "[Violation]" in ln]
hits = lambda vs, m: [v for v in vs if m in v]
T = '"2026-10-28T10:00:00Z"^^xsd:dateTime'
BOX = 'x:It a backlog:Iteration .\n'
def act(kind="Control", box=True): return BOX + 'x:A a backlog:ControlActivity ; backlog:hasWorkKind backlog:WorkKind_%s %s .\n' % (kind, "; backlog:plannedInBox x:It" if box else "")
expect("a control activity with no box is refused", bool(hits(run(act(box=False)), "name the one box")))
expect("a control activity of the kind execution is refused", bool(hits(run(act("Execution")), "serves control, monitoring or reporting")))
for k in ("Control", "Monitoring", "Reporting"):
    v = run(act(k)); expect("a control activity of the kind %s is accepted" % k.lower(), not hits(v, "name the one box") and not hits(v, "serves control, monitoring") and not hits(v, "exactly one kind"))
expect("a control activity with no kind is refused", bool(hits(run(BOX + 'x:A a backlog:ControlActivity ; backlog:plannedInBox x:It .\n'), "exactly one kind")))
R = act() + 'x:R a backlog:ControlRun ; backlog:runOfActivity x:A %s .\n'
v = run(R % ""); expect("a run with no time and no result is refused", bool(hits(v, "when it ran")) and bool(hits(v, "record its result")))
v = run(R % ('; backlog:ranAt %s ; backlog:hasRunResult "Every check passed."' % T)); expect("a run with a time and a result is accepted", not hits(v, "when it ran") and not hits(v, "record its result") and not hits(v, "planned activity it carried out"))
expect("a run naming no activity is refused", bool(hits(run('x:R a backlog:ControlRun ; backlog:ranAt %s ; backlog:hasRunResult "ok" .\n' % T), "planned activity it carried out")))
CK = BOX + 'x:K a backlog:DailyCheckpoint ; backlog:hasWorkKind backlog:WorkKind_%s ; backlog:checkpointOfBox x:It ; backlog:checkpointAt %s %s .\n'
v = run(BOX + 'x:K a backlog:DailyCheckpoint .\n'); expect("a bare checkpoint is refused: no box, no time, no counts, no kind", all(hits(v, m) for m in ("name the box", "when it was made", "how many items are open", "in progress", "are done", "serves monitoring")))
v = run(CK % ("Monitoring", T, "; backlog:openItemCount 2 ; backlog:inProgressItemCount 1 ; backlog:doneItemCount 3")); expect("a checkpoint with its counts is accepted", not [x for x in v if "G169" in x])
expect("a checkpoint of the kind closure is refused", bool(hits(run(CK % ("Closure", T, "; backlog:openItemCount 2 ; backlog:inProgressItemCount 1 ; backlog:doneItemCount 3")), "serves monitoring")))
IMP = 'x:S a backlog:Story .\nx:B a backlog:Impediment ; backlog:impedes x:S ; backlog:hasImpedimentStatement "Blocked by a missing tool, cleared when it is installed." ; backlog:raisedAt %s .\n'
v = run(IMP % T + CK % ("Monitoring", T, "; backlog:openItemCount 2 ; backlog:inProgressItemCount 1 ; backlog:doneItemCount 3 ; backlog:namesBlocker x:B"))
expect("a checkpoint that names a blocker with no owner is refused (the impediment rule asks the owner)", bool(hits(v, "name the role accountable")))
v = run(IMP % T + CK % ("Monitoring", T, "; backlog:openItemCount 2 ; backlog:inProgressItemCount 1 ; backlog:doneItemCount 3 ; backlog:namesBlocker x:B") + 'x:B backlog:hasImpedimentOwner backlog:Builder .\n')
expect("a checkpoint that names a blocker with an owner is accepted by the impediment rule (asserted, corrected after the post-mortem)", not hits(v, "name the role accountable"))
DM = 'x:S a backlog:Story ; backlog:hasState backlog:Done ; backlog:hasAcceptanceCriterion x:C1 .\nx:C1 a backlog:AcceptanceCriterion .\nx:C2 a backlog:AcceptanceCriterion .\nx:D a backlog:DemoRun ; backlog:hasWorkKind backlog:WorkKind_Control %s .\n'
v = run(DM % ""); expect("a bare demo run is refused: no item, no criterion, no time, nothing shown, no result", all(hits(v, m) for m in ("name the item it showed", "acceptance criterion it showed", "when it took place", "what was shown", "record its result")))
OK = '; backlog:demonstratesItem x:S ; backlog:demonstratedAgainst %s ; backlog:demoAt ' + T + ' ; backlog:hasDemoShown "The item running." ; backlog:hasDemoResult "It met the criterion."'
v = run(DM % (OK % "x:C1")); expect("a demo run of an item against its own criterion with a result is accepted", not [x for x in v if "G169" in x])
expect("a demo run against a criterion that is not the item's own is refused", bool(hits(run(DM % (OK % "x:C2")), "not one of the item's own")))

# post-mortem corrections (G171)
DMD = 'x:S a backlog:Story ; backlog:hasAcceptanceCriterion x:C1 ; backlog:hasState backlog:%s .\nx:C1 a backlog:AcceptanceCriterion .\nx:D a backlog:DemoRun ; backlog:hasWorkKind backlog:WorkKind_Control' + OK % "x:C1" + ' .\n'
expect("a demo run of an item that is not finished is refused", bool(hits(run(DMD % "Proposed"), "not finished")))
expect("a demo run of a Done item is accepted", not hits(run(DMD % "Done"), "not finished"))
RB = 'x:It a backlog:Iteration ; backlog:iterationStart %s .\nx:A a backlog:ControlActivity ; backlog:hasWorkKind backlog:WorkKind_Control ; backlog:plannedInBox x:It .\nx:R a backlog:ControlRun ; backlog:runOfActivity x:A ; backlog:ranAt %s ; backlog:hasRunResult "ok" .\n'
expect("a control run that took place before its box started is refused", bool(hits(run(RB % ('"2026-10-28T12:00:00Z"^^xsd:dateTime', T)), "before the box it controls started")))
expect("a control run after its box started is accepted", not hits(run(RB % ('"2026-10-28T09:00:00Z"^^xsd:dateTime', T)), "before the box it controls started"))
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
