#!/usr/bin/env python3
"""backlog_timeline_witness_probe v1.0.0 -- the timeline witness flags a finish time earlier than the evidence's first commit and stays silent otherwise (G107).
Plants a git repository with one file committed at a fixed time and three Done items: finished before that commit (flagged), after it (silent), and
citing a path never committed (reported as not measured, not as a fault). Exit 0 when all hold."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
tool = sorted(glob.glob(os.path.join(HERE, "backlog_timeline_witness_v*.py")), key=sv)[-1]
if sys.argv[1:] == ["--deps"]: print(os.path.abspath(__file__)); print(tool); sys.exit(0)
bad = []
with tempfile.TemporaryDirectory() as d:
    ws = os.path.join(d, "ws"); os.makedirs(ws)
    env = dict(os.environ, GIT_AUTHOR_NAME="p", GIT_AUTHOR_EMAIL="p@x", GIT_COMMITTER_NAME="p", GIT_COMMITTER_EMAIL="p@x",
               GIT_COMMITTER_DATE="2026-09-16T10:04:00+00:00", GIT_AUTHOR_DATE="2026-09-16T10:04:00+00:00")
    run = lambda *c: subprocess.run(c, cwd=ws, env=env, capture_output=True, check=True)
    run("git", "init", "-q"); open(os.path.join(ws, "a.txt"), "w").write("a"); run("git", "add", "a.txt"); run("git", "commit", "-q", "-m", "a")
    ttl = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/tw#> .\n"
    for n, fin, path in (("Early", "2026-09-16T09:30:00", "a.txt"), ("Late", "2026-09-16T11:00:00", "a.txt"), ("Nohist", "2026-09-16T09:30:00", "b.txt")):
        ttl += f'x:{n} a backlog:Task ; backlog:hasState backlog:Done ; backlog:finishedAt "{fin}"^^<http://www.w3.org/2001/XMLSchema#dateTime> ; backlog:hasEvidence x:{n}E .\nx:{n}E a backlog:ArtifactEvidence ; backlog:hasArtifactPath "{path}" .\n'
    reg = os.path.join(d, "r.ttl"); open(reg, "w").write(ttl)
    r = subprocess.run([sys.executable, "-B", tool, reg, "--workspace", ws], capture_output=True, text=True); out = r.stdout
    print(out.strip())
    if r.returncode != 1: bad.append(f"exit code {r.returncode}, expected 1")
    if "CONTRADICTED  Early" not in out: bad.append("the early finish was not flagged")
    if "Late" in out.replace("Late:", "X") and "CONTRADICTED  Late" in out: bad.append("the late finish was flagged")
    if "NOT MEASURED  Nohist" not in out: bad.append("the path without history was not reported as not measured")
    if "1 contradicted" not in out: bad.append("count of contradictions is not 1")
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]; sys.exit(1 if bad else 0)
