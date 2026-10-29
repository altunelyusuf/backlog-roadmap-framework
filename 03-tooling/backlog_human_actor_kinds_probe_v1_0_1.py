#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe reads no record of the framework register; the validator keeps only the controlled individuals)
"""backlog_human_actor_kinds_probe v1.0.0 -- re-runnable proof of the human-actor ruling (T-Box v1.131.0, G116).

  Vocabulary (real files)  isOrganisation is a boolean on Executor_HumanTeam and there is no Executor_Organisation class; the closed set of five Executor kinds is unchanged
                           (AllDisjointClasses still lists five); holdsRole is declared from Executor to Role; the framework's own owner individual holds the Owner role.
  Behaviour (validator)    an organisation (a human team with isOrganisation true) is treated exactly as a human team:
                             responsible for an atomic item   fires the collective-on-atomic rule (as a team does; an individual does not)
                             overseer under RS_HumanOversight silent (a single agent overseer fires, as the control)
                             holdsRole on an individual       raises nothing about that individual
                           isOrganisation on an individual  fires OrganisationIsTeamShape; on a team it is silent
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
from rdflib import Graph, Namespace, RDF, RDFS, OWL
B = Namespace("http://example.org/backlog#")
tb = Graph().parse(latest("01-ontologies/backlog_tbox_v*.ttl"), format="turtle")
ab = Graph().parse(latest("01-ontologies/backlog_abox_v*.ttl"), format="turtle")
expect("isOrganisation is a boolean on Executor_HumanTeam, and there is no Executor_Organisation class", (B.isOrganisation, RDFS.domain, B.Executor_HumanTeam) in tb and (B.Executor_Organisation, RDF.type, OWL.Class) not in tb)
five = {B.Executor_IndividualHuman, B.Executor_HumanTeam, B.Executor_SingleAgent, B.Executor_AgentTeam, B.Executor_AgentFederation}
found = False
for s in tb.subjects(RDF.type, OWL.AllDisjointClasses):
    lst = tb.value(s, OWL.members)
    members = set(tb.items(lst)) if lst is not None else set()
    if five <= members and B.Executor_Organisation not in members and len(members) == 5: found = True
expect("the closed set of five Executor kinds is unchanged", found)
expect("holdsRole runs from Executor to Role", (B.holdsRole, RDFS.domain, B.Executor) in tb and (B.holdsRole, RDFS.range, B.Role) in tb)
expect("the framework's own owner holds the Owner role", (B.Executor_YusufAltunel, B.holdsRole, B.Owner) in ab)
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/human-actor-probe#> .\n"
def item(resp, **rel):
    r = "".join(f" ; backlog:{k} x:{v}" for k, v in rel.items())
    return f"x:W a backlog:Task ; backlog:hasState backlog:InProgress ; backlog:responsible x:{resp}{r} .\n"
P = "x:P a backlog:Executor_IndividualHuman .\n"
ORG = "x:O a backlog:Executor_HumanTeam ; backlog:isOrganisation true ; backlog:hasController x:P ; backlog:hasExecutorMember x:P .\n"
TEAM = "x:T a backlog:Executor_HumanTeam ; backlog:hasController x:P ; backlog:hasExecutorMember x:P .\n"
REG = "x:Reg a backlog:Backlog ; backlog:isRegisterRoot true ; backlog:adoptsRuleSet backlog:RS_HumanOversight .\n"
ATOMIC, OV, ORGK = "L3: this work item is atomic", "G111: the Executor named as overseer", "G116: isOrganisation is stated"
SCEN = {
  "organisation responsible for an atomic item":  (P + ORG + item("O"), ATOMIC, 1),
  "team responsible for an atomic item (control)": (P + TEAM + item("T"), ATOMIC, 1),
  "individual responsible for an atomic item":     (P + item("P"), ATOMIC, 0),
  "organisation as overseer":                      (REG + P + ORG + item("P", overseenBy="O"), OV, 0),
  "single agent as overseer (control)":            (REG + P + "x:AG a backlog:Executor_SingleAgent .\n" + item("P", overseenBy="AG"), OV, 1),
  "holdsRole on an individual":                    (P + "x:P backlog:holdsRole backlog:Owner .\n", "x:P", 0),
  "isOrganisation on an individual":               (P + "x:P backlog:isOrganisation true .\n", ORGK, 1),
  "isOrganisation on a team":                      (P + ORG, ORGK, 0),
}
with tempfile.TemporaryDirectory() as d:
    for name, (body, key, want) in SCEN.items():
        f = os.path.join(d, "s.ttl"); open(f, "w").write(HEAD + body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=600).stdout
        if key == "x:P":
            got = sum(1 for ln in out.splitlines() if "[Violation]" in ln and re.search(r"\] P\s", ln))
        else:
            got = sum(1 for ln in out.splitlines() if "[Violation]" in ln and key in ln)
        expect(f"{name}: expected {want}, got {got}", got == want)
print("validator :", os.path.basename(val)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
