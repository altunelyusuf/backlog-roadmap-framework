#!/usr/bin/env python3
"""backlog_competency_inheritance_probe v1.0.0 -- re-runnable proof of the finer competency level and CompetencyMatchShape's inherit rule (shapes v1.160.0, T-Box v1.125.0, G109).

Each scenario is a tiny register judged by the CURRENT validator; the probe reads only this shape's own message ("requires a Competency its responsible Executor's own CompetencyProfile").
A requirement of a skill is met by the skill or by any finer skill below it; a requirement of a finer skill is met only by that skill.
  silent  parent required, a child listed (the case the v1.159.0 rule got wrong); same child required and listed; an ordinary leaf required and listed; two children listed, parent required
  fires   child required, only the parent listed; child required, a sibling child listed; parent required, nothing listed; ordinary leaf required, a finer skill of another leaf listed
Exit 0 when every expectation holds, 1 otherwise.
"""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
if sys.argv[1:] == ["--deps"]:
    pkg = os.path.dirname(HERE)
    for pat in ("03-tooling/backlog_validate_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl", "01-ontologies/backlog_abox_v*.ttl"):
        print(sorted(glob.glob(os.path.join(pkg, pat)), key=sv)[-1])
    print(os.path.abspath(__file__)); sys.exit(0)
val = sorted(glob.glob(os.path.join(HERE, "backlog_validate_v*.py")), key=sv)[-1]
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/competency-inheritance-probe#> .\n"
def scen(n, requires, listed):
    caps = " ; ".join(f"backlog:hasCapability backlog:{c}" for c in listed)
    prof = f"x:P{n} a backlog:CompetencyProfile" + (f" ; {caps}" if caps else "") + " .\n"
    return (prof + f"x:E{n} a backlog:Executor_IndividualHuman ; backlog:hasCompetencyProfile x:P{n} .\n"
            f"x:W{n} a backlog:Task ; backlog:hasState backlog:InProgress ; backlog:responsible x:E{n} ; backlog:requiresCompetency backlog:{requires} .\n")
SCEN = {
  "parent required, child listed":            (scen(1, "Comp_SystemModelling", ["Comp_ModelValidation"]), 0),
  "parent required, two children listed":     (scen(2, "Comp_SystemModelling", ["Comp_Simulation", "Comp_StructuralModelling"]), 0),
  "child required, same child listed":        (scen(3, "Comp_Simulation", ["Comp_Simulation"]), 0),
  "ordinary leaf required and listed":        (scen(4, "Comp_Coding", ["Comp_Coding"]), 0),
  "child required, only parent listed":       (scen(5, "Comp_Simulation", ["Comp_SystemModelling"]), 1),
  "child required, sibling child listed":     (scen(6, "Comp_Simulation", ["Comp_ModelValidation"]), 1),
  "parent required, nothing listed":          (scen(7, "Comp_SystemModelling", []), 1),
  "other leaf required, modelling child listed": (scen(8, "Comp_OntologyModeling", ["Comp_StructuralModelling"]), 1),
}
bad = []
with tempfile.TemporaryDirectory() as d:
    for name, (body, want) in SCEN.items():
        f = os.path.join(d, "s.ttl"); open(f, "w").write(HEAD + body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=600).stdout
        got = sum(1 for ln in out.splitlines() if "[Violation]" in ln and "requires a Competency its responsible Executor" in ln)
        print(f"{name:46} expected {want} got {got}")
        if got != want: bad.append(f"{name}: expected {want}, got {got}")
print("validator :", os.path.basename(val)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
