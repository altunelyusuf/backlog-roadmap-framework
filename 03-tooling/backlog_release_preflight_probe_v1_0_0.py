#!/usr/bin/env python3
"""backlog_release_preflight_probe v1.0.0 -- proof that the release tool's preflight sees a handover that arrived on origin, before the gate (G151)."""
import glob, os, re, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
tool = sorted(glob.glob(os.path.join(HERE, "backlog_release_tool_v*.py")), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(tool); sys.exit(0)
bad = []
def expect(n, ok):
    print(("PASS  " if ok else "FAIL  ") + n)
    if not ok: bad.append(n)
def git(d, *a): return subprocess.run(["git", "-c", "user.email=p@p", "-c", "user.name=p", *a], cwd=d, capture_output=True, text=True, check=True).stdout
with tempfile.TemporaryDirectory() as t:
    git(t, "init", "-q", "--bare", "origin.git")
    for who in ("a", "b"):
        git(t, "clone", "-q", "origin.git", who)
    a, b = os.path.join(t, "a"), os.path.join(t, "b")
    pkg = os.path.join(a, "backlog-roadmap-framework")
    os.makedirs(pkg + "/03-tooling"); os.makedirs(pkg + "/07-handover-inbox/pending"); os.makedirs(pkg + "/04-documentation")
    shutil.copy(tool, pkg + "/03-tooling/" + os.path.basename(tool))
    open(pkg + "/07-handover-inbox/pending/README.md", "w").write("r\n"); open(pkg + "/VERSION.txt", "w").write("1.0.0\n"); open(pkg + "/03-tooling/thing_v1_0_0.py", "w").write("a\n")
    open(pkg + "/04-documentation/CHANGELOG_v1_1_0.md", "w").write("## v1.0.1 — x\n")
    git(a, "add", "-A"); git(a, "commit", "-q", "-m", "base"); git(a, "push", "-q", "origin", "HEAD:main")
    run = lambda: subprocess.run([sys.executable, "-B", pkg + "/03-tooling/" + os.path.basename(tool), "preflight", "1.0.1"], capture_output=True, text=True, cwd=pkg).stdout
    out = run()
    expect("no arrival: preflight does not name a handover", "handover(s) on origin" not in out)
    git(b, "pull", "-q", "origin", "main"); os.makedirs(b + "/backlog-roadmap-framework/07-handover-inbox/pending", exist_ok=True)
    open(b + "/backlog-roadmap-framework/07-handover-inbox/pending/HANDOVER_x_to_y_z_v1_0_0.md", "w").write("q\n")
    git(b, "add", "-A"); git(b, "commit", "-q", "-m", "arrives"); git(b, "push", "-q", "origin", "HEAD:main")
    out = run()
    expect("a handover pushed to origin is named, and preflight stops", "HANDOVER_x_to_y_z_v1_0_0.md" in out and "STOP" in out)
    git(a, "pull", "-q", "origin", "main")
    expect("once pulled into the working tree it is no longer an arrival", "HANDOVER_x_to_y_z" not in run().split("preflight")[0])
    os.makedirs(a + "/backlog-roadmap-framework/07-handover-inbox/accepted", exist_ok=True)
    git(a, "mv", "backlog-roadmap-framework/07-handover-inbox/pending/HANDOVER_x_to_y_z_v1_0_0.md", "backlog-roadmap-framework/07-handover-inbox/accepted/HANDOVER_x_to_y_z_v1_0_0.md")
    expect("a handover dispositioned here (moved to accepted/, not yet pushed) is not an arrival", "HANDOVER_x_to_y_z" not in run().split("preflight")[0])
    open(pkg + "/03-tooling/thing_v1_0_0.py", "w").write("changed\n")
    expect("a published versioned file changed under its own name is refused before the gate (BP-D7)", "thing_v1_0_0.py" in run() and "keeps its versioned name" in run())
print("VERDICT   :", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
