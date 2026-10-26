#!/usr/bin/env python3
"""backlog_g162_probe v1.0.0 -- re-runnable proof of the plan step, the cancelling exit and the supporting change request (G162).

  Each rule fires on its planted case and is silent on a control, through the real validator. Exit 0 when every expectation holds.
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
H = "@prefix backlog: <http://example.org/backlog#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/g162#> .\n"
dt = lambda t: f'"{t}"^^xsd:dateTime'
K = {"PLAN": "no kick-off of the lineage recorded", "REP": "activates no roadmap report", "NOA": "no as-is assessment assesses it", "UNS": "does not sort as accomplished",
     "MIS": "sorts an item against its state", "OBJ": "does not sort as fitted", "MARK": "carries no closure mark", "IMP": "must state the impact", "CHG": "names no objective it supports"}
def plan(adopt=True, kick=None, rep="2026-10-26T08:50:00Z", extra=""):
    t = "x:L a backlog:Lineage " + ("; backlog:adoptsRuleSet backlog:RS_PlanBeforeStart " if adopt else "") + ".\n"
    t += f"x:S a backlog:Story ; backlog:belongsToLineage x:L ; backlog:hasState backlog:InProgress ; backlog:startedAt {dt('2026-10-26T10:00:00Z')} .\n" + extra
    if kick:
        t += f"x:K a backlog:KickOff ; backlog:kicksOffLineage x:L ; backlog:kickedOffAt {dt(kick)} " + (f"; backlog:activatesReport x:R " if rep else "") + ".\n"
        if rep: t += f"x:R a backlog:RoadmapReport ; backlog:hasRunTimestamp {dt(rep)} .\n"
    return t
def cancel(sort="full", mark=True, imp=True):
    t = "x:L a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_CancellationAssessed ; backlog:hasLineageStatus backlog:LS_Abandoned ; backlog:lineageForMission x:M .\nx:M a backlog:Mission .\n"
    t += "x:A a backlog:Story ; backlog:belongsToLineage x:L ; backlog:hasState backlog:Done .\nx:B a backlog:Story ; backlog:belongsToLineage x:L ; backlog:hasState backlog:Ready .\nx:O a backlog:Objective ; backlog:belongsToLineage x:L .\n"
    a = f"x:As a backlog:AsIsAssessment ; backlog:assessesLineage x:L ; backlog:assessedAt {dt('2026-10-26T11:00:00Z')} ; backlog:hasFitGapStatement \"half\" "
    if imp: a += '; backlog:hasImpactStatement "none" '
    if sort == "full": a += "; backlog:accomplishedItem x:A ; backlog:dueItem x:B ; backlog:gapsObjective x:O "
    if sort == "noitem": a += "; backlog:accomplishedItem x:A ; backlog:gapsObjective x:O "
    if sort == "wrong": a += "; backlog:accomplishedItem x:A , x:B ; backlog:gapsObjective x:O "
    if sort == "noobj": a += "; backlog:accomplishedItem x:A ; backlog:dueItem x:B "
    t += a + ".\n"
    t += "x:C a backlog:ClosureReport ; backlog:closesForMission x:M " + ("; backlog:hasClosureMark backlog:Cm_Cancelled ; backlog:citesAssessment x:As " if mark else "") + ".\n"
    return t
SC = [("start with no kick-off", plan(), {"PLAN": 1}),
      ("kick-off before the start, report run before it (control)", plan(kick="2026-10-26T09:00:00Z"), {"PLAN": 0, "REP": 0}),
      ("kick-off after the start", plan(kick="2026-10-26T10:30:00Z"), {"PLAN": 1}),
      ("kick-off activating no report", plan(kick="2026-10-26T09:00:00Z", rep=None), {"REP": 1}),
      ("report run after the kick-off", plan(kick="2026-10-26T09:00:00Z", rep="2026-10-26T09:30:00Z"), {"REP": 1}),
      ("urgent item needs no kick-off", plan(extra="x:U a backlog:UrgentInterruption ; backlog:urgentItem x:S .\n"), {"PLAN": 0}),
      ("a lineage that did not adopt the rule", plan(adopt=False), {"PLAN": 0, "REP": 0}),
      ("abandoned, no assessment", cancel(sort="none").replace("x:As a backlog:AsIsAssessment ; backlog:assessesLineage x:L", "x:As a backlog:AsIsAssessment"), {"NOA": 1}),
      ("abandoned, fully assessed and marked (control)", cancel(), {"NOA": 0, "UNS": 0, "MIS": 0, "OBJ": 0, "MARK": 0, "IMP": 0}),
      ("an item left unsorted", cancel("noitem"), {"UNS": 1}),
      ("an item sorted against its state", cancel("wrong"), {"MIS": 1}),
      ("an objective left unsorted", cancel("noobj"), {"OBJ": 1}),
      ("closure report without mark or citation", cancel(mark=False), {"MARK": 1}),
      ("assessment without impact", cancel(imp=False), {"IMP": 1}),
      ("change request with no objective", "x:L a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_ChangeSupportsMission .\nx:R a backlog:ChangeRequest ; backlog:belongsToLineage x:L .\n", {"CHG": 1}),
      ("change request supporting an objective (control)", "x:L a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_ChangeSupportsMission .\nx:R a backlog:ChangeRequest ; backlog:belongsToLineage x:L ; backlog:supportsObjective x:O .\nx:O a backlog:Objective .\n", {"CHG": 0}),
      ("change request in a lineage that did not adopt the rule", "x:L a backlog:Lineage .\nx:R a backlog:ChangeRequest ; backlog:belongsToLineage x:L .\n", {"CHG": 0})]
with tempfile.TemporaryDirectory() as d:
    for name, body, want in SC:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(H + body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=900).stdout
        for k, n in want.items():
            got = sum(1 for ln in out.splitlines() if "[Violation]" in ln and K[k] in ln)
            expect(f"{name} [{k}]: expected {n}, got {got}", got == n)
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
