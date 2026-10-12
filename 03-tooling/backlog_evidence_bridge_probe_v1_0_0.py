#!/usr/bin/env python3
"""backlog_evidence_bridge_probe v1.0.0 -- the evidence bridge verifies a file inside its workspace and refuses one outside it (G107).
Plants a workspace holding one file and a second file beside it (another package), then records ArtifactEvidence for:
  inside the workspace                      -> verified
  '../other/secret.txt' (a sibling package) -> NOT verified
  an absolute path to the sibling file      -> NOT verified
  a link inside the workspace to the sibling -> NOT verified
Exit 0 when all four hold.   --deps prints the files it reads."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
tool = sorted(glob.glob(os.path.join(HERE, "backlog_evidence_bridge_v*.py")), key=sv)[-1]
if sys.argv[1:] == ["--deps"]: print(os.path.abspath(__file__)); print(tool); sys.exit(0)
bad = []
with tempfile.TemporaryDirectory() as d:
    ws = os.path.join(d, "pkg"); other = os.path.join(d, "other"); os.makedirs(ws); os.makedirs(other)
    open(os.path.join(ws, "mine.txt"), "w").write("mine"); open(os.path.join(other, "secret.txt"), "w").write("not mine")
    os.symlink(os.path.join(other, "secret.txt"), os.path.join(ws, "link.txt"))
    cases = [("inside", "mine.txt", True), ("dotdot", "../other/secret.txt", False), ("absolute", os.path.join(other, "secret.txt"), False), ("link", "link.txt", False)]
    ttl = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/bridge-probe#> .\n"
    for n, p, _ in cases: ttl += f'x:{n} a backlog:ArtifactEvidence ; backlog:hasArtifactPath "{p}" .\n'
    reg = os.path.join(d, "r.ttl"); open(reg, "w").write(ttl)
    r = subprocess.run([sys.executable, "-B", tool, reg, "--workspace", ws, "-o", os.path.join(d, "o.ttl")], capture_output=True, text=True)
    from rdflib import Graph, URIRef, Literal
    g = Graph().parse(os.path.join(d, "o.ttl"))
    for n, p, want in cases:
        v = g.value(URIRef("http://example.org/bridge-probe#" + n), URIRef("http://example.org/backlog#evidenceVerified"))
        got = bool(v.toPython()) if v is not None else None
        print(f"{n:10} expected {want} got {got}")
        if got != want: bad.append(n)
print("VERDICT   :", "PASS" if not bad else "FAIL " + ",".join(bad)); sys.exit(1 if bad else 0)
