#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe reads no record of the framework register; the validator keeps only the controlled individuals)
"""backlog_agent_roles_probe v1.0.0 -- re-runnable proof of the agent-role rules (shapes v1.161.0, G111) and of the role vocabulary.

Each scenario is a tiny register judged by the CURRENT validator; the probe reads only the two shapes' own messages.
  HumanOverseerShape (only a register that adopted RS_HumanOversight)
    fires   overseen by a single agent; overseen by an agent team; overseen by a federation
    silent  overseen by an individual human; overseen by a human team; agent overseer in a register that did not adopt
  ManagerialIndependenceShape (only a register that adopted RS_ManagerialIndependence)
    fires   two teams with the same controller; the verifier is the controller of the producing team; the producing team is the controller of the verifier team
    silent  two teams with different controllers; two unrelated individuals; the same shared controller in a register that did not adopt
  Vocabulary (real files): six role concepts in backlog:AgentRoleScheme, each with a definition, a scope note and a source; no Specialist concept.
Exit 0 when every expectation holds, 1 otherwise.
"""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    for pat in ("03-tooling/backlog_validate_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl", "01-ontologies/backlog_abox_v*.ttl"):
        print(latest(pat))
    print(os.path.abspath(__file__)); sys.exit(0)
val = sorted(glob.glob(os.path.join(HERE, "backlog_validate_v*.py")), key=sv)[-1]
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/agent-roles-probe#> .\n"
def reg(rs): return f"x:Reg a backlog:Backlog ; backlog:isRegisterRoot true ; backlog:adoptsRuleSet backlog:{rs} .\n" if rs else ""
H = lambda n: f"x:{n} a backlog:Executor_IndividualHuman .\n"
def item(resp, **rel):
    r = "".join(f" ; backlog:{k} x:{v}" for k, v in rel.items())
    return f"x:W a backlog:Task ; backlog:hasState backlog:InProgress ; backlog:responsible x:{resp}{r} .\n"
def team(n, ctrl=None, members=()):
    return f"x:{n} a backlog:Executor_HumanTeam" + (f" ; backlog:hasController x:{ctrl}" if ctrl else "") + "".join(f" ; backlog:hasExecutorMember x:{m}" for m in members) + " .\n"
OV = "G111: the Executor named as overseer"
MG = "G111: the verifier of this work item shares"
HO, MI = "RS_HumanOversight", "RS_ManagerialIndependence"
AG = "x:AG a backlog:Executor_SingleAgent .\n"
SCEN = {
  "overseer is a single agent":          (reg(HO) + H("P") + AG + item("P", overseenBy="AG"), OV, 1),
  "overseer is an agent team":           (reg(HO) + H("P") + "x:AT a backlog:Executor_AgentTeam .\n" + item("P", overseenBy="AT"), OV, 1),
  "overseer is a federation":            (reg(HO) + H("P") + "x:AF a backlog:Executor_AgentFederation .\n" + item("P", overseenBy="AF"), OV, 1),
  "overseer is an individual human":     (reg(HO) + H("P") + H("Q") + item("P", overseenBy="Q"), OV, 0),
  "overseer is a human team":            (reg(HO) + H("P") + H("Q") + team("T", "Q", ["Q"]) + item("P", overseenBy="T"), OV, 0),
  "agent overseer, rule not adopted":    (H("P") + AG + item("P", overseenBy="AG"), OV, 0),
  "two teams, one controller":           (reg(MI) + H("C") + team("TA", "C", ["C"]) + team("TB", "C", ["C"]) + item("TA", verifiedBy="TB"), MG, 1),
  "verifier controls the producer":      (reg(MI) + H("C") + team("TA", "C", ["C"]) + item("TA", verifiedBy="C"), MG, 1),
  "producer controls the verifier team": (reg(MI) + H("P") + H("C") + team("TB", "P", ["C"]) + item("P", verifiedBy="TB"), MG, 1),
  "two teams, two controllers":          (reg(MI) + H("C1") + H("C2") + team("TA", "C1", ["C1"]) + team("TB", "C2", ["C2"]) + item("TA", verifiedBy="TB"), MG, 0),
  "two unrelated individuals":           (reg(MI) + H("P") + H("Q") + item("P", verifiedBy="Q"), MG, 0),
  "shared controller, rule not adopted": (H("C") + team("TA", "C", ["C"]) + team("TB", "C", ["C"]) + item("TA", verifiedBy="TB"), MG, 0),
}
bad = []
with tempfile.TemporaryDirectory() as d:
    for name, (body, key, want) in SCEN.items():
        f = os.path.join(d, "s.ttl"); open(f, "w").write(HEAD + body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=600).stdout
        got = sum(1 for ln in out.splitlines() if "[Violation]" in ln and key in ln)
        print(f"{name:40} expected {want} got {got}")
        if got != want: bad.append(f"{name}: expected {want}, got {got}")
# vocabulary, read from the real data file
ab = open(latest("01-ontologies/backlog_abox_v*.ttl")).read()
want_roles = ["Orchestrator", "Implementer", "Reviewer", "Verifier", "Supervisor", "Explainer"]
for r in want_roles:
    m = re.search(r"backlog:AgentRole_%s a skos:Concept.*?\.\n\n" % r, ab, re.S)
    ok = bool(m) and all(k in m.group(0) for k in ("skos:definition", "skos:scopeNote", "dcterms:source", "backlog:AgentRoleScheme"))
    print(f"{'role concept ' + r:40} {'complete' if ok else 'MISSING'}")
    if not ok: bad.append(f"role concept {r} missing or incomplete")
if "AgentRole_Specialist" in ab: bad.append("Specialist must not be a role concept (G39)")
print("validator :", os.path.basename(val)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
