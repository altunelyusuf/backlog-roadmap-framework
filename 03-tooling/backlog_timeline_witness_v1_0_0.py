#!/usr/bin/env python3
"""backlog_timeline_witness v1.0.0 -- a Done item cannot have finished before the artifact that evidences it existed (G107).

The handover that asked for this found 24 Done items published with invented start and finish times chosen to look plausible, and nothing in the register
to contradict them. The repository can: a file's first commit is the earliest moment it existed. For every Done work item that carries ArtifactEvidence
with a path, this tool takes the first commit time of that path in the workspace's git history and reports the item when its finishedAt is EARLIER.
Only that is claimed: a finish time later than the first commit proves nothing either way, and a path with no history is reported as not measured.

  backlog_timeline_witness_v1_0_0.py REGISTER.ttl --workspace DIR      exit 0 no contradiction, 1 at least one, 2 not a git workspace
A finishedAt without a zone is read as UTC.
"""
import argparse, datetime, glob, os, subprocess, sys
from rdflib import Graph, Namespace, RDF
BL = Namespace("http://example.org/backlog#")
def utc(x):
    d = datetime.datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=datetime.timezone.utc)
def first_commit(ws, path):
    r = subprocess.run(["git", "-C", ws, "log", "--format=%cI", "--reverse", "--", path], capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    return utc(lines[0]) if lines else None
def main():
    if sys.argv[1:] == ["--deps"]: print(os.path.abspath(__file__)); return 0
    ap = argparse.ArgumentParser(); ap.add_argument("register"); ap.add_argument("--workspace", required=True); a = ap.parse_args()
    if subprocess.run(["git", "-C", a.workspace, "rev-parse", "--git-dir"], capture_output=True).returncode != 0:
        print("not a git workspace"); return 2
    g = Graph().parse(a.register); bad = checked = unmeasured = 0
    for item in sorted(set(g.subjects(BL.hasState, BL.Done)), key=str):
        fin = g.value(item, BL.finishedAt)
        if fin is None: continue
        for ev in g.objects(item, BL.hasEvidence):
            path = g.value(ev, BL.hasArtifactPath)
            if path is None: continue
            t0 = first_commit(a.workspace, str(path))
            if t0 is None: unmeasured += 1; print(f"NOT MEASURED  {item.split('#')[-1]}: {path} has no history in this workspace"); continue
            checked += 1
            if utc(fin) < t0:
                bad += 1; print(f"CONTRADICTED  {item.split('#')[-1]}: finished {fin}, but its evidence {path} first existed at {t0.isoformat()}")
    print(f"timeline witness: {checked} measured, {unmeasured} not measured, {bad} contradicted")
    return 1 if bad else 0
sys.exit(main())
