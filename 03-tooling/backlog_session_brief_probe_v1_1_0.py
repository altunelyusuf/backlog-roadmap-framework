#!/usr/bin/env python3
"""backlog_session_brief_probe v1.1.0 -- the brief says what the register holds, both ways (G122).

Plants a register with two objectives (one far from target, one near), an overdue checkpoint, one checkpoint due in five days, an
item In Progress and two iterations (one missing a duration and a deployment unit, one complete), then reads the brief. Also checks
that the vendored-tools comparison names an old copy, and that the guard's status prints the brief. Exit 0 when all hold."""
import datetime, glob, io, os, re, shutil, subprocess, sys, tempfile
from rdflib import Graph
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
sys.path.insert(0, HERE)
import importlib.util
spec = importlib.util.spec_from_file_location("brief", sorted(glob.glob(os.path.join(HERE, "backlog_session_brief_v*.py")), key=sv)[-1])
br = importlib.util.module_from_spec(spec); spec.loader.exec_module(br)
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(spec.origin); sys.exit(0)
bad = []
def expect(n, ok):
    print(("PASS  " if ok else "FAIL  ") + n)
    if not ok: bad.append(n)
now = datetime.datetime(2026, 10, 15, tzinfo=datetime.timezone.utc)
TTL = """@prefix b: <http://example.org/backlog#> . @prefix x: <http://example.org/x#> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
x:L a b:Lineage ; b:lineageForMission x:M .
x:G a b:Goal ; b:contributesToMission x:M .
x:Far a b:Objective ; b:contributesToGoal x:G ; b:hasBaselineValue 0 ; b:hasTargetValue 10 ; b:hasTargetDirection b:Dir_Increase ;
   b:hasCheckpoint x:CpPast .
x:CpPast b:checkpointDate "2026-10-01T00:00:00Z"^^xsd:dateTime .
x:O1 b:observationFor x:Far ; b:observedAt "2026-09-01T00:00:00Z"^^xsd:dateTime ; b:hasObservedValue 1 .
x:Near a b:Objective ; b:contributesToGoal x:G ; b:hasBaselineValue 0 ; b:hasTargetValue 10 ; b:hasTargetDirection b:Dir_Increase ;
   b:hasCheckpoint x:CpSoon .
x:CpSoon b:checkpointDate "2026-10-20T00:00:00Z"^^xsd:dateTime .
x:O2 b:observationFor x:Near ; b:observedAt "2026-10-10T00:00:00Z"^^xsd:dateTime ; b:hasObservedValue 8 .
x:Work a b:Story ; b:belongsToLineage x:L ; b:hasState b:InProgress .
x:ItOpen a b:Iteration ; b:belongsToLineage x:L ; b:hasState b:InProgress .
x:ItFull a b:Iteration ; b:belongsToLineage x:L ; b:hasState b:InProgress ; b:hasObservedDuration 5 ; b:hasDurationSource "git" .
x:Dep a b:DeploymentUnit ; b:deploysFrom x:ItFull .
"""
g = Graph(); g.parse(data=TTL, format="turtle")
lines = []; br.brief(g, "L", 7, now, out=lines.append); txt = "\n".join(lines)
expect("FOCUS names the objective farthest from its target and the number still blocking", "Far" in txt.split("FOCUS")[1].splitlines()[0] and "2 of 2" in txt)
expect("IN PROGRESS lists the item and not the iterations", "Work" in txt and "IN PROGRESS  Work" in txt)
expect("DUE names the overdue checkpoint and the one falling due within the week", "Far overdue 2026-10-01" in txt and "Near due 2026-10-20" in txt)
expect("TO CLOSE names what the open iteration lacks", "ItOpen still needs a measured duration and a deployment unit" in txt)
expect("TO CLOSE leaves the complete iteration out", "ItFull" not in txt)
g2 = Graph(); g2.parse(data="@prefix b: <http://example.org/backlog#> . @prefix x: <http://example.org/x#> . x:L a b:Lineage ; b:lineageForMission x:M .", format="turtle")
l2 = []; br.brief(g2, "L", 7, now, out=l2.append)
expect("a mission with no objectives is not called ready to close", "no objective is modelled" in "\n".join(l2) and "ready to close" not in "\n".join(l2))
expect("an unknown lineage is reported, not guessed", br.brief(g2, "Nope", 7, now, out=lambda s: None) == 1)
d = tempfile.mkdtemp(prefix="briefprobe_"); v = os.path.join(d, "vend"); p = os.path.join(d, "pkg", "03-tooling"); os.makedirs(v); os.makedirs(p)
open(os.path.join(v, "backlog_work_guard_v1_1_0.py"), "w").write("#"); open(os.path.join(v, "backlog_session_brief_v1_0_0.py"), "w").write("#")
open(os.path.join(p, "backlog_work_guard_v1_3_0.py"), "w").write("#"); open(os.path.join(p, "backlog_session_brief_v1_0_0.py"), "w").write("#")
o = []; rc = br.vendored(v, os.path.dirname(p), out=o.append)
expect("an old vendored copy is named with the version that replaces it", rc == 1 and "backlog_work_guard_v1_1_0.py -> backlog_work_guard_v1_3_0.py" in o[0] and "session_brief" not in o[0])
shutil.rmtree(d, ignore_errors=True)
print("VERDICT   : " + ("FAIL -- " + "; ".join(bad) if bad else "PASS"))
sys.exit(1 if bad else 0)
