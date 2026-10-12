#!/usr/bin/env python3
"""backlog_state_evidence_probe v1.0.0 -- re-runnable proof of EvidencedWorkStillUnstartedShape (shapes v1.159.0, G107).

Each scenario is a tiny register judged by the CURRENT validator; the probe reads only this shape's own message ("carries evidence the bridge verified").
  fires   an item at Proposed (and at Refined) with verified evidence, in a register that adopted RS_StateReflectsEvidence
  silent  the same item in a register that did not adopt it (G89, G91); an item already InProgress or Done; unverified evidence; no evidence at all
Exit 0 when every expectation holds, 1 otherwise. The fixture_negative case EVID_UNSTARTED is the shape's declared proof.
"""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
if sys.argv[1:] == ["--deps"]:
    pkg = os.path.dirname(HERE)
    for pat in ("03-tooling/backlog_validate_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl"):
        print(sorted(glob.glob(os.path.join(pkg, pat)), key=sv)[-1])
    print(os.path.abspath(__file__)); sys.exit(0)
val = sorted(glob.glob(os.path.join(HERE, "backlog_validate_v*.py")), key=sv)[-1]
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/state-evidence-probe#> .\n"
ADOPT = "x:Reg a backlog:Backlog ; backlog:isRegisterRoot true ; backlog:adoptsRuleSet backlog:RS_StateReflectsEvidence .\n"
def item(n, state, ev=None):
    t = f"x:{n} a backlog:Task ; backlog:hasState backlog:{state}" + (f" ; backlog:hasEvidence x:{n}E" if ev is not None else "") + " .\n"
    if ev is not None: t += f"x:{n}E a backlog:ArtifactEvidence ; backlog:evidenceVerified {'true' if ev else 'false'} .\n"
    return t
SCEN = {
  "Proposed, verified, adopted": (ADOPT + item("A", "Proposed", True), 1),
  "Refined, verified, adopted": (ADOPT + item("B", "Refined", True), 1),
  "Proposed, verified, NOT adopted": (item("C", "Proposed", True), 0),
  "InProgress, verified": (ADOPT + item("D", "InProgress", True), 0),
  "Done, verified": (ADOPT + item("E", "Done", True), 0),
  "Proposed, evidence unverified": (ADOPT + item("F", "Proposed", False), 0),
  "Proposed, no evidence": (ADOPT + item("G", "Proposed"), 0),
}
bad = []
with tempfile.TemporaryDirectory() as d:
    for name, (body, want) in SCEN.items():
        f = os.path.join(d, "s.ttl"); open(f, "w").write(HEAD + body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=600).stdout
        got = sum(1 for ln in out.splitlines() if "[Violation]" in ln and "carries evidence the bridge verified" in ln)
        print(f"{name:32} expected {want} got {got}")
        if got != want: bad.append(f"{name}: expected {want}, got {got}")
print("validator :", os.path.basename(val)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
