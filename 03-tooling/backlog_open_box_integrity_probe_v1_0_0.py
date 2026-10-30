#!/usr/bin/env python3
"""backlog_open_box_integrity_probe v1.0.0 -- a register with a box open is whole (Lineage 23, D2).

The plan of a box names the deployment unit that will ship (G170); the unit is written when the box closes, because it may not carry unfinished work. The archive integrity check must not call that name
dangling while the box is InProgress, and must still call it dangling once the box is Done with no unit. Exit 0 when every expectation holds."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
TOOL, ARC = latest("03-tooling/backlog_archive_integrity_v*.py"), latest("01-ontologies/archive/backlog_framework_archive_abox_v*.ttl")
if sys.argv[1:] == ["--deps"]:
    print("\n".join([TOOL, ARC, os.path.abspath(__file__)])); sys.exit(0)
bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
T = "@prefix fw: <http://example.org/backlog-framework-register#> .\n@prefix backlog: <http://example.org/backlog#> .\nfw:It a backlog:Iteration ; backlog:hasState backlog:%s .\nfw:DP a backlog:DeploymentPlan ; backlog:deploymentPlanForBox fw:It ; backlog:plansDeploymentUnit fw:Rel .\n"
def run(state):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "r.ttl"); open(f, "w").write(T % state)
        return subprocess.run([sys.executable, TOOL, "--register", f, "--archive", ARC], capture_output=True, text=True, cwd=PKG).returncode
expect("a plan naming a unit not yet written, for a box in progress, is not dangling", run("InProgress") == 0)
expect("the same name for a box that is Done is dangling", run("Done") == 2)
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
