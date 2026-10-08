#!/usr/bin/env python3
"""backlog_split_proof_probe v1.2.0 -- the split proof, shown to fire on a known-bad tree and stay silent on a known-good one.

Builds, from the real package, two throwaway trees: one identical to it, one with a single real statement removed. Asserts that
backlog_split_proof certifies the first (exit 0) and refuses the second (exit 2) naming the removed statement, and that a tree
with a statement added is refused unless --allow-added is given. Prints every case. Exit 0 all cases hold, 1 any does not.

Usage: backlog_split_proof_probe_v1_1_0.py [PACKAGE_DIR]   (default: the package this script sits in)
"""
import os, shutil, subprocess, sys, tempfile
from rdflib import Graph, RDF, OWL, URIRef, Literal

HERE = os.path.dirname(os.path.abspath(__file__))
_ARGS = [a for a in sys.argv[1:] if a != "--deps"]
PKG = os.path.abspath(_ARGS[0]) if _ARGS else os.path.dirname(HERE)
PROOF = sorted(__import__("glob").glob(os.path.join(HERE, "backlog_split_proof_v*.py")), key=lambda p: [int(x) for x in __import__("re").findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]])[-1]


def run(a, b, *extra):
    r = subprocess.run([sys.executable, PROOF, a, b, *extra], capture_output=True, text=True)
    return r.returncode, r.stdout


def copy(dst):
    for d in ("01-ontologies", "02-shacl-safeguards"):
        shutil.copytree(os.path.join(PKG, d), os.path.join(dst, d))


def mutate(root, fn):
    path = os.path.join(root, "01-ontologies", sorted(f for f in os.listdir(os.path.join(root, "01-ontologies")) if f.startswith("backlog_abox_v"))[-1])
    g = Graph().parse(path, format="turtle")
    hdr = set(g.subjects(RDF.type, OWL.Ontology))
    t = [x for x in sorted(g) if isinstance(x[0], URIRef) and x[0] not in hdr][100]
    fn(g, t)
    g.serialize(path, format="turtle")
    return t


if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(PROOF)
    import glob as _g
    for d in ("01-ontologies", "02-shacl-safeguards"):
        for f in sorted(_g.glob(os.path.join(PKG, d, "**", "*.ttl"), recursive=True)):
            print(f)
    sys.exit(0)


def main():
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        same, gone, plus = (os.path.join(tmp, n) for n in ("same", "gone", "plus"))
        for d in (same, gone, plus):
            os.makedirs(d); copy(d)
        t = mutate(gone, lambda g, t: g.remove(t))
        mutate(plus, lambda g, t: g.add((t[0], t[1], Literal("an added statement"))))
        cases = [
            ("identical tree is certified", run(PKG, same), 0, "IDENTICAL"),
            ("a tree with one statement removed is refused", run(PKG, gone), 2, str(t[0]).split("#")[-1]),
            ("a tree with one statement added is refused", run(PKG, plus), 2, "an added statement"),
            ("a tree with one statement added passes under --allow-added", run(PKG, plus, "--allow-added"), 0, "IDENTICAL"),
        ]
        for name, (code, out), want, needle in cases:
            good = code == want and needle in out
            ok = ok and good
            print(("  ok    " if good else "  FAIL  ") + f"{name} (exit {code}, wanted {want})")
    print("VERDICT: " + ("every case holds" if ok else "a case did not hold"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
