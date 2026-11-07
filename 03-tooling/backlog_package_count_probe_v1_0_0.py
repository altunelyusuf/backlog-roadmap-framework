#!/usr/bin/env python3
"""Probe for backlog_package_count v1.0.0 (Lineage 32, G219): cases and mutants."""
import os, sys, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "backlog_package_count_v1_0_0.py")
if sys.argv[1:] == ["--deps"]:
    print("\n".join([TOOL, os.path.abspath(__file__)])); sys.exit(0)
H = "@prefix backlog: <http://example.org/backlog#> .\n@prefix fw: <http://example.org/backlog-framework-register#> .\n"
BASE = """fw:L a backlog:Lineage .
fw:GM a backlog:Goal ; backlog:hasGoalFacing backlog:Facing_Mission .
fw:GA a backlog:Goal . fw:GB a backlog:Goal .
fw:OM a backlog:Objective ; backlog:contributesToGoal fw:GM .
fw:GM2 a backlog:Goal ; backlog:hasGoalFacing backlog:Facing_Mission .
fw:OM2 a backlog:Objective ; backlog:contributesToGoal fw:GM2 .
fw:OA a backlog:Objective ; backlog:contributesToGoal fw:GA .
fw:OB a backlog:Objective ; backlog:contributesToGoal fw:GB .
fw:D1 a backlog:ScopeDeliverable ; backlog:belongsToLineage fw:L .
fw:D2 a backlog:ScopeDeliverable ; backlog:belongsToLineage fw:L .
fw:S1 a backlog:Story ; backlog:satisfiesDeliverable fw:D1 ; backlog:pursuesObjective fw:OA , fw:OM .
fw:S2 a backlog:Story ; backlog:satisfiesDeliverable fw:D2 ; backlog:pursuesObjective %s , fw:OM2 .
"""
bad = []
def run(text, tool=TOOL):
    with tempfile.NamedTemporaryFile("w", suffix=".ttl", delete=False) as f: f.write(H + text); p = f.name
    r = subprocess.run([sys.executable, tool, p, "--lineage", "fw:L", "--check"], capture_output=True, text=True)
    os.unlink(p); return r.returncode, r.stdout
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
two = BASE % "fw:OB" + "fw:P1 a backlog:Package ; backlog:belongsToLineage fw:L ; backlog:deliversDeliverable fw:D1 .\nfw:P2 a backlog:Package ; backlog:belongsToLineage fw:L ; backlog:deliversDeliverable fw:D2 .\n"
rc, out = run(two); expect("two goals, two packages: measured 2, declared match", rc == 0 and "2 package(s) needed" in out)
one = BASE % "fw:OA" + "fw:P1 a backlog:Package ; backlog:belongsToLineage fw:L ; backlog:deliversDeliverable fw:D1 , fw:D2 .\n"
rc, out = run(one); expect("same goal, one package: measured 1 (simplest form)", rc == 0 and "1 package(s) needed" in out)
rc, out = run(BASE % "fw:OB" + "fw:P1 a backlog:Package ; backlog:belongsToLineage fw:L ; backlog:deliversDeliverable fw:D1 , fw:D2 .\n"); expect("one package over two groups is refused", rc == 1)
rc, out = run(BASE % "fw:OA" + "fw:P1 a backlog:Package ; backlog:belongsToLineage fw:L ; backlog:deliversDeliverable fw:D1 .\nfw:P2 a backlog:Package ; backlog:belongsToLineage fw:L ; backlog:deliversDeliverable fw:D2 .\n"); expect("two packages over one group is refused", rc == 1)
# mutants: a tool that ignores goals, and one that counts the mission goal
src = open(TOOL).read()
for name, m in (("ignores goals", src.replace("goals.add(go)", "pass")), ("counts the mission goal", src.replace("if (go, B.hasGoalFacing, B.Facing_Mission) not in g:", "if True:"))):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f: f.write(m); mp = f.name
    r1, _ = run(two, mp); r2, _ = run(one, mp); os.unlink(mp)
    expect("mutant '%s' is caught" % name, r1 != 0 or r2 != 0)
sys.exit(1 if bad else 0)
