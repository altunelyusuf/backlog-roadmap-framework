#!/usr/bin/env python3
"""backlog_open_lineage_probe v1.0.0 -- proof that the opening block carries the profile's rule sets and that the shape holds a lineage to them (G155)."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
tool = latest("03-tooling/backlog_open_lineage_v*.py"); val = latest("03-tooling/backlog_validate_v*.py")
if sys.argv[1:] == ["--deps"]:
    for x in (tool, val, latest("01-ontologies/backlog_abox_v*.ttl"), latest("02-shacl-safeguards/backlog_shacl_v*.ttl")): print(x)
    print(os.path.abspath(__file__)); sys.exit(0)
bad = []
def expect(n, ok):
    print(("PASS  " if ok else "FAIL  ") + n)
    if not ok: bad.append(n)
run = lambda *a: subprocess.run([sys.executable, tool, *a], capture_output=True, text=True)
ag = run("--profile", "Profile_Agentic", "--lineage", "L", "--prefix", "x").stdout
st = run("--profile", "Profile_Standard", "--lineage", "L", "--prefix", "x").stdout
expect("the agentic block adopts the accountability rule set and the recording pair", all(k in ag for k in ("RS_AgentAccountability", "RS_StatusHistoryRecorded", "RS_FlowPointsRecorded")) and "adoptionRecordedAtOpen true" in ag)
expect("the standard block does not adopt the accountability rule set", "RS_AgentAccountability" not in st and "RS_RepairReprioritises" in st)
expect("an unknown profile is refused", run("--profile", "Profile_Nope", "--lineage", "L").returncode == 2)
ls = run("--list").stdout
expect("--list names both profiles", "Profile_Agentic" in ls and "Profile_Standard" in ls)
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/open-probe#> .\nx:L a backlog:Lineage .\n"
PROF = "backlog:Profile_Agentic a backlog:OpeningProfile ; backlog:profileIncludes " + " , ".join("backlog:" + m for m in re.findall(r"backlog:(RS_\w+)", ag)) + " .\n"
def count(body):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(HEAD + PROF + body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=900).stdout
    return sum(1 for ln in out.splitlines() if "[Violation]" in ln and "G155:" in ln)
expect("a lineage that wrote the tool's block entire draws no profile finding", count(ag) == 0)
expect("the same block with one rule set left out draws the finding", count(ag.replace("RS_AgentAccountability", "RS_StatusHistoryRecorded", 1)) == 1)
print("VERDICT   :", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
