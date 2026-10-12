#!/usr/bin/env python3
"""backlog_vocabulary_probe v1.0.0 -- the vocabulary derivation holds against drift and against an incomplete source (G106).
  1. the derivation from the newest T-Box and A-box is written to a temporary file and that file passes the check
  2. a member of the T-Box's enumerations and the registers' own subjects: the derived file holds 279-style members only (no Lineage, no WorkItem)
  3. the same file with one member's label changed: refused (differs)
  4. a T-Box copy whose enumeration lists a member the A-box does not define: refused (not defined)
Exit 0 when all behave, 3 otherwise.   --deps prints the files it reads."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE); ONT = os.path.join(PKG, "01-ontologies")
def newest(pat, d=ONT): return sorted(glob.glob(os.path.join(d, pat)), key=lambda x: [int(n) for n in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", x)[0]])[-1]
T = sorted(glob.glob(os.path.join(HERE, "backlog_vocabulary_derive_v*.py")), key=lambda x: [int(n) for n in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", x)[0]])[-1]
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(T)
    for pat in ("backlog_tbox_v*.ttl", "backlog_abox_v*.ttl"): print(newest(pat))
    sys.exit(0)
def run(*a): return subprocess.run([sys.executable, "-B", T, *a], capture_output=True, text=True).returncode
bad = []
with tempfile.TemporaryDirectory() as d:
    f = os.path.join(d, "vocab.ttl")
    if run("--write", f) != 0 or run("--check", f) != 0: bad.append("1: the derivation does not pass its own check")
    else:
        from rdflib import Graph, RDF, URIRef
        g = Graph().parse(f); B = "http://example.org/backlog#"
        if any(True for c in ("Lineage", "Story", "Mission", "Backlog") for _ in g.subjects(RDF.type, URIRef(B + c))): bad.append("2: the vocabulary holds register content")
        v = open(f).read(); m = re.search(r'rdfs:label "([^"]+)"@en', v[v.index("backlog:AC_Confirmed"):])
        p = os.path.join(d, "drift.ttl"); open(p, "w").write(v.replace(f'rdfs:label "{m.group(1)}"@en', 'rdfs:label "DRIFT"@en', 1))
        if run("--check", p) == 0: bad.append("3: a drifted vocabulary file was accepted")
    t = open(newest("backlog_tbox_v*.ttl")).read(); m = re.search(r"owl:oneOf \(\s*backlog:(\w+)", t)
    q = os.path.join(d, "backlog_tbox_v9_9_9.ttl"); open(q, "w").write(t.replace(m.group(0), m.group(0) + " backlog:Ghost_Member_Probe", 1))
    if run("--write", os.path.join(d, "g.ttl"), "--tbox", q) == 0: bad.append("4: an enumeration member missing from the A-box was accepted")
for b in bad: print("FAIL", b)
print("vocabulary probe:", "PASS" if not bad else f"{len(bad)} failure(s)"); sys.exit(3 if bad else 0)
