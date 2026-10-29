#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe reads no record of the framework register; the validator keeps only the controlled individuals)
"""backlog_executor_subclass_probe v1.0.0 -- re-runnable proof that the executor rules see subclasses (shapes v1.167.0, G117).

  A class declared a subclass of an executor kind is treated as that kind by the collective-on-atomic rule, the overseer rule and OrganisationIsTeamShape.
Exit 0 when every expectation holds, 1 otherwise.
"""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    for pat in ("03-tooling/backlog_validate_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl", "01-ontologies/backlog_abox_v*.ttl"):
        print(latest(pat))
    print(os.path.abspath(__file__)); sys.exit(0)
val = sorted(glob.glob(os.path.join(HERE, "backlog_validate_v*.py")), key=sv)[-1]
bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix x: <http://example.org/subclass-probe#> .\nx:MyTeam rdfs:subClassOf backlog:Executor_AgentTeam .\nx:MyAgent rdfs:subClassOf backlog:Executor_SingleAgent .\nx:MyPerson rdfs:subClassOf backlog:Executor_IndividualHuman .\nx:MyHumans rdfs:subClassOf backlog:Executor_HumanTeam .\n"
def item(resp, **rel):
    r = "".join(f" ; backlog:{k} x:{v}" for k, v in rel.items())
    return f"x:W a backlog:Task ; backlog:hasState backlog:InProgress ; backlog:responsible x:{resp}{r} .\n"
REG = "x:Reg a backlog:Backlog ; backlog:isRegisterRoot true ; backlog:adoptsRuleSet backlog:RS_HumanOversight .\n"
ATOMIC, OV, ORGK = "L3: this work item is atomic", "G111: the Executor named as overseer", "G116: isOrganisation is stated"
SCEN = {
  "subclass of agent team responsible for an atomic item":  ("x:T a x:MyTeam ; backlog:hasController x:P ; backlog:hasExecutorMember x:P .\nx:P a backlog:Executor_IndividualHuman .\n" + item("T"), ATOMIC, 1),
  "subclass of single agent responsible for an atomic item (control)": ("x:A a x:MyAgent .\n" + item("A"), ATOMIC, 0),
  "subclass of individual human as overseer":  (REG + "x:H a x:MyPerson .\nx:P a backlog:Executor_IndividualHuman .\n" + item("P", overseenBy="H"), OV, 0),
  "subclass of human team as overseer":        (REG + "x:H a x:MyHumans ; backlog:hasController x:P ; backlog:hasExecutorMember x:P .\nx:P a backlog:Executor_IndividualHuman .\n" + item("P", overseenBy="H"), OV, 0),
  "subclass of single agent as overseer (control)": (REG + "x:A a x:MyAgent .\nx:P a backlog:Executor_IndividualHuman .\n" + item("P", overseenBy="A"), OV, 1),
  "isOrganisation on a subclass of human team": ("x:H a x:MyHumans ; backlog:isOrganisation true ; backlog:hasController x:P ; backlog:hasExecutorMember x:P .\nx:P a backlog:Executor_IndividualHuman .\n", ORGK, 0),
  "isOrganisation on a subclass of single agent (control)": ("x:A a x:MyAgent ; backlog:isOrganisation true .\n", ORGK, 1),
}
with tempfile.TemporaryDirectory() as d:
    for name, (body, key, want) in SCEN.items():
        f = os.path.join(d, "s.ttl"); open(f, "w").write(HEAD + body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=600).stdout
        if True:
            got = sum(1 for ln in out.splitlines() if "[Violation]" in ln and key in ln)
        expect(f"{name}: expected {want}, got {got}", got == want)
print("validator :", os.path.basename(val)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
