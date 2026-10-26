#!/usr/bin/env python3
"""backlog_route_b_exemption_probe v1.0.0 -- re-runnable proof of the act-record exemption on the change-management route (G160).

  A story the owner's route B admits (a ScopeChange, in a lineage the owner's frozenRuling answers, named by the bypass) is not asked for
  a planning event or a concern declaration it cannot honestly have; the same story with no such answer still is. Exit 0 when all hold.
"""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    for pat in ("03-tooling/backlog_validate_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl", "01-ontologies/backlog_abox_v*.ttl"):
        print(latest(pat))
    print(os.path.abspath(__file__)); sys.exit(0)
val = latest("03-tooling/backlog_validate_v*.py"); bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/rb-probe#> .\nx:L a backlog:Lineage ; backlog:hasLineageStatus backlog:LS_InProgress "
STORY = "x:S a backlog:Story ; backlog:hasState backlog:Done ; backlog:belongsToLineage x:L .\n"
BYP = "x:B a backlog:LineageBypass ; backlog:bypassedItem x:S .\n"
SC = "x:SC a backlog:ScopeChange ; backlog:admitsItem x:S .\n"
DEP = "x:I a backlog:Iteration .\nx:D a backlog:Deployment ; backlog:deploysFrom x:I ; backlog:deploysItem x:S .\n"
K = {"SHIP": "deployment carries an item the iteration never planned", "PLAN": "no PlanningEvent ever took it", "CONC": "neither an applicable design concern"}
SCEN = [("route B: bypassed, admitted by a scope change, owner's ruling", HEAD + '; backlog:frozenBy x:B ; backlog:frozenRuling "route B" .\n' + STORY + BYP + SC, {"PLAN": 0, "CONC": 0}),
        ("same story, no scope change admits it", HEAD + '; backlog:frozenBy x:B ; backlog:frozenRuling "route B" .\n' + STORY + BYP, {"PLAN": 1, "CONC": 1}),
        ("same story, admitted but no owner's ruling", HEAD + "; backlog:frozenBy x:B .\n" + STORY + BYP + SC, {"PLAN": 1, "CONC": 1}),
        ("same story, admitted but never named by a bypass", HEAD + '; backlog:frozenRuling "r" .\n' + STORY + SC, {"PLAN": 1, "CONC": 1})]
SCEN += [("a deployment ships a route B item (iteration planned nothing)", HEAD + '; backlog:frozenBy x:B ; backlog:frozenRuling "route B" .\n' + STORY + BYP + SC + DEP, {"SHIP": 0}),
         ("a deployment ships an ordinary unplanned item", HEAD + ".\n" + STORY + DEP, {"SHIP": 1})]
with tempfile.TemporaryDirectory() as d:
    for name, body, want in SCEN:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=900).stdout
        for k, n in want.items():
            got = sum(1 for ln in out.splitlines() if "[Violation]" in ln and K[k] in ln)
            expect(f"{name} [{k}]: expected {n}, got {got}", got == n)
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
