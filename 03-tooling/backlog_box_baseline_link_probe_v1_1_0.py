#!/usr/bin/env python3
"""Probe of how the box tool finds the base plan of a box (box 53, IPage handover C1 to C7): by the link `baselineFor` and `isCurrentBaseline true`, under any name and prefix, not by the tool's own name.
Usage: probe [--tool PATH]  (--tool runs the probe on another copy of the tool, for the planted-fault check)."""
import glob, re, subprocess, sys, tempfile, os
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", p)[0]]
STEP = sorted(glob.glob(PKG + "/03-tooling/backlog_box_step_v*.py"), key=sv)[-1]
if "--tool" in sys.argv:
    STEP = sys.argv[sys.argv.index("--tool") + 1]
PFX = {"fw": "http://example.org/backlog-framework-register#", "ip": "http://example.org/ipage-register#"}
def register(p, pb):
    """Boxes 1-3 delivered 2, 3 and 2 points; box 4 is open with 3.5 points; PB is the text of the base plan statements of box 4 (prefix p)."""
    r = ("@prefix backlog: <http://example.org/backlog#> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> . @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> . @prefix %s: <%s> .\n" % (p, PFX[p])
         + "%s:L_T a backlog:Lineage .\n" % p)
    for i, (h, e, st) in enumerate([(0, 2, "Done"), (1, 3, "Done"), (3, 2, "Done"), (4, 3.5, "InProgress")], 1):
        r += ('%s:It_T_%d a backlog:Iteration ; backlog:belongsToLineage %s:L_T ; backlog:hasIdentifier "T-BOX-%d" ; backlog:iterationStart "2026-11-01T0%d:00:00Z"^^xsd:dateTime .\n'
              '%s:S%d a backlog:Story ; backlog:hasEffort %s ; backlog:hasState backlog:%s .\n%s:Ev%d backlog:plannedInto %s:It_T_%d ; backlog:plansItem %s:S%d .\n') % (p, i, p, i, h, p, i, float(e), st, p, i, p, i, p, i)
    return r + pb
def pbs(p, name, target, current="true", split=False):
    head = "%s:%s a backlog:PlanBaseline ; backlog:baselineFor %s:%s ; backlog:baselinedAt \"2026-11-01T03:00:00Z\"^^xsd:dateTime" % (p, name, p, target)
    cur = "backlog:isCurrentBaseline %s" % current
    return (head + " .\n%s:%s %s .\n" % (p, name, cur)) if split else (head + " ; " + cur + " .\n")
def run(reg_text, call, p="fw"):
    with tempfile.TemporaryDirectory() as d:
        rp = d + "/r.ttl"; open(rp, "w").write(reg_text)
        code = ("import importlib.util;sp=importlib.util.spec_from_file_location('st',%r);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);"
                "reg=m.Reg(%r,%r,'T');it=m.resolve_it_id(reg,'T',4,reg.L);" % (STEP, rp, p + ":L_T" if p != "fw" else "L_T")) + call
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=PKG + "/03-tooling")
        return r.stdout + r.stderr, open(rp).read()
HAS = "print('HAS', m.has_base_plan(reg,'T',4,it))"
BASE = "m.cmd_baseline(reg,4)"
CASES = []
def case(name, ok):
    CASES.append((name, ok)); print(("PASS  " if ok else "FAIL  ") + name)
# C2: another name, same prefix; C2b: another prefix (an adopting register); C2c: the link in a statement apart from the type
o, _ = run(register("fw", pbs("fw", "BasePlan_Box4_Planned", "It_T_4")), HAS); case("C2 other name under fw: found", "HAS True" in o)
o, _ = run(register("ip", pbs("ip", "Planned4", "It_T_4")), HAS, "ip"); case("C2b other name under another prefix found", "HAS True" in o)
o, _ = run(register("fw", pbs("fw", "Planned4", "It_T_4", split=True)), HAS); case("C2c the current flag in a separate statement found", "HAS True" in o)
# C3: baseline n refuses and writes nothing
o, t = run(register("fw", pbs("fw", "Planned4", "It_T_4")), BASE); case("C3 baseline refuses, says a base plan exists, writes none", "already has a base plan" in o and "Rebaseline" in o and "PB_T_4" not in t)
o, t = run(register("ip", pbs("ip", "Planned4", "It_T_4")), BASE, "ip"); case("C3b the same under another prefix", "already has a base plan" in o and "PB_T_4" not in t)
# C4: another box's base plan, or one that is not current, is not box 4's
o, _ = run(register("fw", pbs("fw", "Planned3", "It_T_3")), HAS); case("C4 a base plan of another box is not taken", "HAS False" in o)
o, _ = run(register("fw", pbs("fw", "Old4", "It_T_4", current="false")), HAS); case("C4b a base plan that is not current is not taken", "HAS False" in o)
o, t = run(register("fw", pbs("fw", "Old4", "It_T_4", current="false")), BASE); case("C4c with only a superseded one, baseline writes a new current one", "PB_T_4" in t and "isCurrentBaseline true" in t)
# C5: no linked base plan: written under the tool's own name, as before
o, t = run(register("fw", ""), BASE); case("C5 none linked: one is written under the tool's name", "PB_T_4" in t and "baselineFor fw:It_T_4" in t)
o, _ = run(register("fw", "fw:PB_T_4 a backlog:PlanBaseline ; backlog:baselineFor fw:It_T_4 .\n"), HAS); case("C5b the tool's own name still counts when it carries no flag", "HAS True" in o)
# C1 (review defect D1): `open` of a planned box whose base plan sits under another name says the base plan stands, writes no second one and does not reach the pace refusal
import json, shutil
MON = sorted(glob.glob(PKG + "/03-tooling/backlog_agent_monitor_v*.py"), key=sv)[-1]
OPEN_TTL = """@prefix pcl: <http://example.org/ipage-register#> .
@prefix backlog: <http://example.org/backlog#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
<http://example.org/ipage> owl:versionInfo "0.1.0" .
pcl:D1 a backlog:Lineage ; backlog:hasLineageStatus backlog:LS_InProgress .
pcl:KO a backlog:KickOff ; backlog:kicksOffLineage pcl:D1 .
pcl:Story4_D1 a backlog:Story ; backlog:hasIdentifier "4" ; backlog:hasState backlog:Proposed ; backlog:hasEffort 2.0 ;
    backlog:memberOfContainer pcl:It4_1 ; backlog:belongsToLineage pcl:D1 ; backlog:producedByStage pcl:Out_B .
pcl:AC_D1_Story4_D1 a backlog:AcceptanceCriterion ; backlog:hasGherkinText "Given a, When b, Then c." .
pcl:Story4_D1 backlog:hasAcceptanceCriterion pcl:AC_D1_Story4_D1 .
pcl:It4_1 a backlog:Iteration ; backlog:hasIdentifier "D1-BOX-1" ; backlog:hasTitle "planned" ; backlog:hasSprintGoal "g" ;
    backlog:hasState backlog:Proposed ; backlog:hasCapacity 3.0 ; backlog:belongsToLineage pcl:D1 .
pcl:PB4_1 a backlog:PlanBaseline ; backlog:baselineFor pcl:It4_1 ; backlog:isCurrentBaseline true ;
    backlog:hasBaselineStart "2026-01-01T00:00:00Z"^^xsd:dateTime ; backlog:hasBaselineEnd "2026-01-01T04:00:00Z"^^xsd:dateTime .
"""
def open_case():
    work = tempfile.mkdtemp(); pk = os.path.join(work, "pkg")
    os.makedirs(pk + "/01-ontologies"); os.makedirs(pk + "/03-tooling")
    for fl in (STEP, MON): shutil.copy(fl, pk + "/03-tooling/" + os.path.basename(fl))
    reg = pk + "/01-ontologies/ipage_abox_v0_1_0.ttl"; open(reg, "w").write(OPEN_TTL)
    g = lambda *a: subprocess.run(["git", "-C", pk] + list(a), capture_output=True, text=True)
    g("init", "-q"); open(pk + "/03-tooling/other.py", "w").write("x = 1\n"); g("add", "-A")
    g("-c", "user.email=p@p", "-c", "user.name=p", "commit", "-qm", "p"); g("update-ref", "refs/remotes/origin/main", "HEAD")
    r = subprocess.run([sys.executable, pk + "/03-tooling/" + os.path.basename(STEP), reg, "--lineage", "pcl:D1", "--prefix", "D1", "open", "1", "t", "g", "Story4_D1", "--capacity", "3"], capture_output=True, text=True)
    out, final = r.stdout + r.stderr, open(reg).read()
    shutil.rmtree(work, ignore_errors=True)
    return r.returncode, out, final
rc, out, final = open_case()
case("C1 open of a planned box with its base plan under another name: says it stands, no 'no base plan' line, no pace refusal, one PlanBaseline",
     rc == 0 and "its base plan stands" in out and "no base plan: one is recorded now" not in out and "NO BASE PLAN" not in out and final.count("a backlog:PlanBaseline") == 1 and "PB_D1_1" not in final)
# a box number that is the start of another box's identifier is not taken for it (box 4 against a base plan of It_T_41)
o, _ = run(register("fw", pbs("fw", "Planned41", "It_T_41")), HAS); case("C4d the base plan of It_T_41 is not box 4's", "HAS False" in o)
print("%d/%d held" % (sum(1 for _, k in CASES if k), len(CASES)))
sys.exit(0 if all(k for _, k in CASES) else 1)
