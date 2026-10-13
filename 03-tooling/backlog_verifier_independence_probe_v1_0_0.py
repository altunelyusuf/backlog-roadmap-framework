#!/usr/bin/env python3
"""backlog_verifier_independence_probe v1.0.0 -- re-runnable proof of VerifierIndependenceShape and DoneWithoutVerifierShape (shapes v1.160.0, G109).

Each scenario is a tiny register judged by the CURRENT validator; the probe reads only the two shapes' own messages.
  VerifierIndependenceShape (holds in every register)
    fires   verifier = the responsible Executor; verifier is a member of the responsible team; verifier is a member two levels down; the verifier is a team that contains the responsible Executor
    silent  an unrelated individual; an unrelated team; a team that shares no member with the responsible Executor
  DoneWithoutVerifierShape (only a register that adopted RS_IndependentVerification, G89 and G91)
    fires   Done, adopted, no verifier
    silent  Done, adopted, with a verifier; Done, not adopted; InProgress, adopted
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
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/verifier-independence-probe#> .\n"
ADOPT = "x:Reg a backlog:Backlog ; backlog:isRegisterRoot true ; backlog:adoptsRuleSet backlog:RS_IndependentVerification .\n"
H = lambda n: f"x:H{n} a backlog:Executor_IndividualHuman .\n"
def item(n, resp, ver=None, state="InProgress"):
    return f"x:W{n} a backlog:Task ; backlog:hasState backlog:{state} ; backlog:responsible x:{resp}" + (f" ; backlog:verifiedBy x:{ver}" if ver else "") + " .\n"
IND = "G109: the Executor named as verifier"
MISS = "names no verifiedBy"
SCEN = {
  "verifier is the executor":              (H(1) + item(1, "H1", "H1"), IND, 1),
  "verifier is a member of the team":      (H(2) + "x:T2 a backlog:Executor_HumanTeam ; backlog:hasExecutorMember x:H2 .\n" + item(2, "T2", "H2"), IND, 1),
  "verifier is a member two levels down":  (H(3) + "x:T3a a backlog:Executor_HumanTeam ; backlog:hasExecutorMember x:H3 .\nx:T3 a backlog:Executor_HumanTeam ; backlog:hasExecutorMember x:T3a .\n" + item(3, "T3", "H3"), IND, 1),
  "verifier is a team over the executor":  (H(4) + "x:T4 a backlog:Executor_HumanTeam ; backlog:hasExecutorMember x:H4 .\n" + item(4, "H4", "T4"), IND, 1),
  "unrelated individual":                  (H(5) + H(55) + item(5, "H5", "H55"), IND, 0),
  "unrelated team":                        (H(6) + H(66) + "x:T6 a backlog:Executor_HumanTeam ; backlog:hasExecutorMember x:H66 .\n" + item(6, "H6", "T6"), IND, 0),
  "two teams sharing no member":           (H(7) + H(77) + "x:T7a a backlog:Executor_HumanTeam ; backlog:hasExecutorMember x:H7 .\nx:T7b a backlog:Executor_HumanTeam ; backlog:hasExecutorMember x:H77 .\n" + item(7, "T7a", "T7b"), IND, 0),
  "Done, adopted, no verifier":            (ADOPT + H(8) + item(8, "H8", None, "Done"), MISS, 1),
  "Done, adopted, with a verifier":        (ADOPT + H(9) + H(99) + item(9, "H9", "H99", "Done"), MISS, 0),
  "Done, not adopted, no verifier":        (H(10) + item(10, "H10", None, "Done"), MISS, 0),
  "InProgress, adopted, no verifier":      (ADOPT + H(11) + item(11, "H11"), MISS, 0),
}
bad = []
with tempfile.TemporaryDirectory() as d:
    for name, (body, key, want) in SCEN.items():
        f = os.path.join(d, "s.ttl"); open(f, "w").write(HEAD + body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=600).stdout
        got = sum(1 for ln in out.splitlines() if "[Violation]" in ln and key in ln)
        print(f"{name:40} expected {want} got {got}")
        if got != want: bad.append(f"{name}: expected {want}, got {got}")
print("validator :", os.path.basename(val)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
