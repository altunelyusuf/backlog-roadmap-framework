#!/usr/bin/env python3
"""backlog_remote_commit_check v1.0.0 -- checks whether the remote has moved
ahead, and if so, whether any new commit touched this package's own real
sovereign path -- decided entirely by CrossProjectCommitAdvisoryShape, a
real SPARQL rule reading touchesPath against fw:Register's own
hasSovereignPathPrefix, not by Python judging file paths.

Built directly from a real, confirmed observation (G76): a parallel
session (agentic-sdlc) consumes this package as its own declared process
methodology and has never, across its full real history, touched a file
under this package's own path. A remote fetch reporting "you are behind"
is not, by itself, evidence of a real conflict -- and treating it as one
every time is real, avoidable session friction. This script's own only
job is running `git diff --name-only` between the local and remote HEAD
and writing down what changed, one touchesPath triple per real path. It
makes no decision about whether any of those paths matter.

Usage:
  python3 backlog_remote_commit_check_v1_0_0.py --repo PATH
"""
import sys, os, subprocess


def main():
    args = sys.argv[1:]
    repo = None
    if "--repo" in args:
        i = args.index("--repo")
        if i + 1 < len(args):
            repo = args[i + 1]
    if not repo or not os.path.isdir(repo):
        print("VERDICT     : NOT-VERIFIED — no real repo path given")
        sys.exit(1)

    def run(cmd):
        return subprocess.run(cmd, cwd=repo, capture_output=True, text=True, timeout=60)

    run(["git", "fetch", "-q", "origin"])
    changed = run(["git", "diff", "--name-only", "HEAD", "origin/main"]).stdout.strip().splitlines()

    here = os.path.dirname(os.path.abspath(__file__))
    pkg = os.path.dirname(here)
    register = None
    import glob
    matches = sorted(glob.glob(os.path.join(pkg, "01-ontologies", "backlog_framework_register_abox_v*.ttl")))
    if matches:
        register = matches[-1]

    import rdflib
    B = rdflib.Namespace("http://example.org/backlog#")
    EX = rdflib.Namespace("http://example.org/remotecheck#")
    data = rdflib.Graph()
    if register:
        data.parse(register, format="turtle")
    commit = EX["RC_" + run(["git", "rev-parse", "origin/main"]).stdout.strip()[:12]]
    for path in changed:
        data.add((commit, rdflib.RDF.type, B.RemoteCommit))
        data.add((commit, B.touchesPath, rdflib.Literal(path)))

    shacl_matches = sorted(glob.glob(os.path.join(pkg, "02-shacl-safeguards", "backlog_shacl_v*.ttl")))
    shacl = rdflib.Graph()
    shacl.parse(shacl_matches[-1], format="turtle")

    import pyshacl
    conforms, results_graph, results_text = pyshacl.validate(data, shacl_graph=shacl, advanced=True)
    print("%d real path(s) changed on the remote" % len(changed))
    hit = "CrossProjectCommitAdvisoryShape" in results_text
    print("VERDICT     : %s" % (
        "REAL RECONCILIATION NEEDED — a changed path is under this package's own sovereign prefix, decided by the SPARQL rule"
        if hit else
        "SAFE TO FAST-FORWARD — no changed path falls under this package's own sovereign prefix, decided by the SPARQL rule"))
    sys.exit(1 if hit else 0)


if __name__ == "__main__":
    main()
