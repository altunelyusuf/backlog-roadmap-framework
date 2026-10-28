#!/usr/bin/env python3
"""backlog_lineage_steps_probe v1.1.0 -- re-runnable proof of the plan, assess, close and adapt recorders (G162).

  Drives each recorder on a scratch register and the real validator after it: the refusals, the records written, and no G162 violation left.
  The plan recorder runs the real roadmap report on a scratch register. Exit 0 when every expectation holds.
"""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    for pat in ("03-tooling/backlog_validate_v*.py", "03-tooling/backlog_lineage_steps_v*.py", "03-tooling/backlog_roadmap_report_v*.py", "03-tooling/backlog_execution_ready_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl", "01-ontologies/backlog_abox_v*.ttl"):
        print(latest(pat))
    print(os.path.abspath(__file__)); sys.exit(0)
val = latest("03-tooling/backlog_validate_v*.py"); tool = latest("03-tooling/backlog_lineage_steps_v*.py"); bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
N = "http://example.org/steps#"
REG = """@prefix backlog: <http://example.org/backlog#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix x: <http://example.org/steps#> .
x:Reg a backlog:Backlog ; backlog:adoptsRuleSet backlog:RS_CancellationAssessed , backlog:RS_ChangeSupportsMission , backlog:RS_PlanBeforeStart .
x:L a backlog:Lineage ; backlog:hasLineageStatus backlog:LS_InProgress ; backlog:lineageForMission x:M .
x:M a backlog:Mission ; backlog:hasMissionOutcome backlog:Out_InFlight .
x:Sc a backlog:ScopeStatement ; backlog:belongsToLineage x:L .
x:O a backlog:Objective ; backlog:belongsToLineage x:L .
x:O2 a backlog:Objective .
x:A a backlog:Story ; backlog:belongsToLineage x:L ; backlog:hasState backlog:Done ; backlog:pursuesObjective x:O ; backlog:memberOfContainer x:It .
x:B a backlog:Story ; backlog:belongsToLineage x:L ; backlog:hasState backlog:Ready ; backlog:memberOfContainer x:It .
x:E a backlog:Enabler ; backlog:belongsToLineage x:L ; backlog:hasState backlog:Ready ; backlog:hasEffort 3.0 .
x:It a backlog:Iteration .
"""
def run(*a):
    r = subprocess.run([sys.executable, tool, *a], capture_output=True, text=True); return r.returncode, r.stdout + r.stderr
def viol(reg):
    out = subprocess.run([sys.executable, val, reg], capture_output=True, text=True, timeout=900).stdout
    return [l for l in out.splitlines() if "[Violation]" in l and "G162" in l]
with tempfile.TemporaryDirectory() as d:
    reg = os.path.join(d, "r.ttl"); open(reg, "w").write(REG)
    c, o = run("adapt", reg, "--lineage", N + "L", "--scope", N + "Sc", "--objective", N + "O2", "--rationale", "r", "--owner-decision", "ruling", "--admit", N + "E")
    expect("adapt refuses an objective that is not the lineage's", c != 0)
    c, o = run("adapt", reg, "--lineage", N + "L", "--scope", N + "Sc", "--objective", N + "O", "--rationale", "r", "--owner-decision", " ", "--admit", N + "E")
    expect("adapt refuses an empty Owner decision", c != 0)
    c, o = run("adapt", reg, "--lineage", N + "L", "--scope", N + "Sc", "--objective", N + "O", "--rationale", "gap found", "--owner-decision", "standing rule of 2026-10-25", "--admit", N + "E")
    expect("adapt records the request, the computed impact and the scope change", c == 0 and "supportsObjective" in open(reg).read() and "admitsItem" in open(reg).read())
    expect("the impact statement counts the effort the admitted item carries (round 2 correction: it read 0 points for an item with an effort)", "3 point(s)" in o)
    expect("no G162 violation after the adaptation", [v for v in viol(reg) if "names no objective" in v] == [])
    c, o = run("close", reg, "--lineage", N + "L", "--mark", "cancelled", "--rationale", "stopped")
    expect("close is refused without an as-is assessment", c != 0)
    c, o = run("assess", reg, "--lineage", N + "L", "--fit-gap", "one of three delivered", "--impact", "nothing else depends on it")
    expect("assess sorts the items (1 accomplished, 2 due) and the objective", c == 0 and "accomplished 1" in o and "due 2" in o)
    c, o = run("close", reg, "--lineage", N + "L", "--mark", "cancelled", "--rationale", "stopped by the Owner")
    t = open(reg).read()
    expect("close records the marked closure report, the outcome and the status", c == 0 and "Cm_Cancelled" in t and "Out_Abandoned" in t and "LS_Abandoned" in t)
    v = viol(reg)
    expect("no G162 violation after the closure" + ("" if not v else ": " + v[0][:220]), v == [])
    # the plan recorder, on the real roadmap report
    reg2 = os.path.join(d, "r2.ttl"); open(reg2, "w").write(REG)
    gate = latest("03-tooling/backlog_execution_ready_v*.py")
    g0 = subprocess.run([sys.executable, gate, reg2, "--lineage", "L"], capture_output=True, text=True).stdout
    expect("the start gate reports the plan step missing before it is recorded", "FAIL  the plan step is recorded" in g0)
    c, o = run("plan", reg2, "--lineage", N + "L", "--container", N + "It")
    expect("plan computes the roadmap report and records the kick-off that activates it" + ("" if c == 0 else ": " + o[-300:]), c == 0 and "activatesReport" in open(reg2).read())
    g1 = subprocess.run([sys.executable, gate, reg2, "--lineage", "L"], capture_output=True, text=True).stdout
    expect("the start gate accepts the plan step once recorded", "ok    the plan step is recorded" in g1)
    expect("the kick-off activates a report run no later than itself", [v for v in viol(reg2) if "activates no roadmap report" in v] == [])
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
