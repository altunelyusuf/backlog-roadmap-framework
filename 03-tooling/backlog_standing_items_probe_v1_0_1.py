#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe reads no record of the framework register; the validator keeps only the controlled individuals)
"""backlog_standing_items_probe v1.0.0 -- re-runnable proof of the recurring-activity and estimated-start rules (T-Box v1.134.0, shapes v1.169.0, G120).

  A recurring activity needs an interval and has no state; an estimated start names its basis; an occurrence cannot start after its activity ended; a live
  recurring activity counts as a mover of the metric of an objective and an ended one does not.
Exit 0 when every expectation holds, 1 otherwise.
"""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(sorted(glob.glob(os.path.join(HERE, "fixtures", "fixture_positive_v*.ttl")), key=sv)[-1]); print(sorted(glob.glob(os.path.join(HERE, "backlog_roadmap_report_v*.py")), key=sv)[-1])
    for pat in ("03-tooling/backlog_validate_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl", "01-ontologies/backlog_abox_v*.ttl"):
        print(latest(pat))
    print(os.path.abspath(__file__)); sys.exit(0)
val = sorted(glob.glob(os.path.join(HERE, "backlog_validate_v*.py")), key=sv)[-1]
bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
DT = "^^<http://www.w3.org/2001/XMLSchema#dateTime>"
DU = '"P7D"^^<http://www.w3.org/2001/XMLSchema#duration>'
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/standing-probe#> .\n"
OBJ = ('x:M a backlog:Mission ; backlog:hasMissionOutcome backlog:Out_InFlight .\nx:G a backlog:Goal ; backlog:contributesToMission x:M .\n'
       'x:O a backlog:Objective ; backlog:contributesToGoal x:G ; backlog:hasTargetValue 0 ; backlog:hasTargetDirection backlog:Dir_Decrease%s .\n'
       'x:Obs a backlog:MetricObservation ; backlog:observationFor x:O ; backlog:hasObservedValue 5 ; backlog:observedAt "2026-10-14T08:00:00Z"' + DT + ' .\n')
K = {"INT": "states the longest accepted interval", "STATE": "has no state: it is never In Progress", "BASIS": "does not say what it was taken from", "ENDED": "has no further occurrences", "MOVER": "names no live work item that can actually move it"}
LIVE = 'x:A a backlog:RecurringActivity ; backlog:recurrenceInterval ' + DU + ' .\n'
SCEN = [
 ("a recurring activity without an interval", "x:A a backlog:RecurringActivity .\n", {"INT": 1}),
 ("a recurring activity with an interval", LIVE, {"INT": 0, "STATE": 0}),
 ("a recurring activity with a state", 'x:A a backlog:RecurringActivity ; backlog:recurrenceInterval ' + DU + ' ; backlog:hasState backlog:InProgress .\n', {"STATE": 1}),
 ("an estimated start with no basis", 'x:W a backlog:Task ; backlog:hasState backlog:Done ; backlog:startedAtIsEstimate true ; backlog:startedAt "2026-09-05T00:00:00Z"' + DT + ' .\n', {"BASIS": 1}),
 ("an estimated start with its basis", 'x:W a backlog:Task ; backlog:hasState backlog:Done ; backlog:startedAtIsEstimate true ; backlog:startEstimateBasis "the plan date; a commit of 2026-09-06 holds it In Progress" ; backlog:startedAt "2026-09-05T00:00:00Z"' + DT + ' .\n', {"BASIS": 0}),
 ("a basis with no start", 'x:W a backlog:Task ; backlog:hasState backlog:Done ; backlog:startEstimateBasis "unknown" .\n', {"BASIS": 1}),
 ("an occurrence that started after the activity ended", 'x:A a backlog:RecurringActivity ; backlog:recurrenceInterval ' + DU + ' ; backlog:recurrenceEndedAt "2026-10-01T00:00:00Z"' + DT + ' .\nx:W a backlog:Task ; backlog:hasState backlog:InProgress ; backlog:occurrenceOf x:A ; backlog:startedAt "2026-10-10T08:00:00Z"' + DT + ' .\n', {"ENDED": 1}),
 ("an occurrence that started before the activity ended", 'x:A a backlog:RecurringActivity ; backlog:recurrenceInterval ' + DU + ' ; backlog:recurrenceEndedAt "2026-10-20T00:00:00Z"' + DT + ' .\nx:W a backlog:Task ; backlog:hasState backlog:Done ; backlog:occurrenceOf x:A ; backlog:startedAt "2026-10-10T08:00:00Z"' + DT + ' .\n', {"ENDED": 0}),
 ("an open objective with no mover", OBJ % "", {"MOVER": 1}),
 ("an open objective moved by a Done task", (OBJ % " ; backlog:metricMovableBy x:T") + 'x:T a backlog:Task ; backlog:hasState backlog:Done .\n', {"MOVER": 1}),
 ("an open objective moved by a live recurring activity", (OBJ % " ; backlog:metricMovableBy x:A") + LIVE, {"MOVER": 0}),
 ("an open objective moved by an ended recurring activity", (OBJ % " ; backlog:metricMovableBy x:A") + 'x:A a backlog:RecurringActivity ; backlog:recurrenceInterval ' + DU + ' ; backlog:recurrenceEndedAt "2026-10-01T00:00:00Z"' + DT + ' .\n', {"MOVER": 1}),
]
with tempfile.TemporaryDirectory() as d:
    for name, body, want in SCEN:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(HEAD + body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=900).stdout
        for k, n in want.items():
            got = sum(1 for ln in out.splitlines() if "[Violation]" in ln and K[k] in ln)
            expect(f"{name} [{k}]: expected {n}, got {got}", got == n)

# the roadmap report keeps an estimated start out of the measured cycle time
from rdflib import Graph, URIRef, Literal
Bn = "http://example.org/backlog#"
pos = sorted(glob.glob(os.path.join(HERE, "fixtures", "fixture_positive_v*.ttl")), key=sv)[-1]
rep = sorted(glob.glob(os.path.join(HERE, "backlog_roadmap_report_v*.py")), key=sv)[-1]
gg = Graph().parse(pos, format="turtle")
fin = sorted((s_ for s_ in gg.subjects(URIRef(Bn + "finishedAt"), None) if gg.value(s_, URIRef(Bn + "startedAt"))), key=str)
with tempfile.TemporaryDirectory() as d:
    f0 = os.path.join(d, "plain.ttl"); gg.serialize(f0, format="turtle")
    gg.add((fin[0], URIRef(Bn + "startedAtIsEstimate"), Literal(True))); gg.add((fin[0], URIRef(Bn + "startEstimateBasis"), Literal("probe")))
    f1 = os.path.join(d, "est.ttl"); gg.serialize(f1, format="turtle")
    o0 = subprocess.run([sys.executable, "-B", rep, f0], capture_output=True, text=True).stdout
    o1 = subprocess.run([sys.executable, "-B", rep, f1], capture_output=True, text=True).stdout
    c0 = [l for l in o0.splitlines() if "cycle time" in l]; c1 = [l for l in o1.splitlines() if "cycle time" in l]
    expect("the roadmap report counts one finished item fewer when one start is an estimate", bool(c0) and bool(c1) and c0 != c1 and "not measured" in o1 and "not measured" not in o0)
print("validator :", os.path.basename(val)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
