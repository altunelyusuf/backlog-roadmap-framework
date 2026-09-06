#!/usr/bin/env python3
"""backlog_new_shape_proof v1.1.0 -- every NEWLY authored shape declares its
proof, checked against a REAL, distinct baseline -- not silently against
itself.

Real bug fixed (G74): v1.0.0's own "published_root" was a hardcoded
relative path from this script's own directory. In any environment where
the working copy IS the only copy on disk -- exactly this session's own
real layout throughout -- that path resolves back to the same file being
checked, so "new since last publish" was always computed as zero,
regardless of how many real, unproven shapes were actually added. The
checker reported PASS every time this session ran it, without ever once
comparing against a genuinely different snapshot.

Fixed by making the baseline explicit and its absence honest:

  python3 backlog_new_shape_proof_v1_1_0.py --baseline PATH_TO_REAL_CLONE
  python3 backlog_new_shape_proof_v1_1_0.py --strict --baseline PATH

If --baseline is omitted, or the given path does not exist, or it resolves
to the SAME real file as the current shapes file (by content hash, not by
path string, since a path can differ while pointing at an identical
byte-for-byte copy), this prints NOT-VERIFIED and exits nonzero under
--strict -- it never silently reports PASS on an unverified comparison.
Once a shape is published it is grandfathered permanently.
"""
import sys, os, glob, hashlib


def shape_names(path):
    from rdflib import Graph, URIRef, RDF
    SH = "http://www.w3.org/ns/shacl#"
    g = Graph()
    g.parse(path, format="turtle")
    return {str(s) for s in g.subjects(RDF.type, URIRef(SH + "NodeShape"))}, g


def proven(name, g):
    from rdflib import URIRef
    B = "http://example.org/backlog#"
    return any(True for _ in g.triples((URIRef(name), URIRef(B + "provenByFixture"), None)))


def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    strict = "--strict" in sys.argv
    baseline_dir = None
    if "--baseline" in sys.argv:
        i = sys.argv.index("--baseline")
        if i + 1 < len(sys.argv):
            baseline_dir = sys.argv[i + 1]

    here = os.path.dirname(os.path.abspath(__file__))
    pkg = os.path.dirname(here)
    current = sorted(glob.glob(os.path.join(pkg, "02-shacl-safeguards", "backlog_shacl_v*.ttl")))
    if not current:
        raise SystemExit("FATAL: no shapes file found. Refusing to report on nothing.")
    current_path = current[-1]

    if not baseline_dir or not os.path.isdir(baseline_dir):
        print("baseline    : NOT PROVIDED or not a real directory")
        print("VERDICT     : NOT-VERIFIED — no real, distinct baseline given; this run proves nothing about what is new")
        sys.exit(1 if strict else 0)

    published = sorted(glob.glob(os.path.join(baseline_dir, "backlog_shacl_v*.ttl")))
    if not published:
        print("baseline    : %s (no backlog_shacl_v*.ttl found there)" % baseline_dir)
        print("VERDICT     : NOT-VERIFIED — baseline directory has no shapes file to compare against")
        sys.exit(1 if strict else 0)

    if file_hash(published[-1]) == file_hash(current_path):
        print("baseline    : %s -- IDENTICAL BYTES to the current shapes file" % published[-1])
        print("VERDICT     : NOT-VERIFIED — baseline is the same file as current; nothing to compare, this is not a real check")
        sys.exit(1 if strict else 0)

    cur_names, cur_g = shape_names(current_path)
    pub_names, _ = shape_names(published[-1])
    new_shapes = sorted(cur_names - pub_names)
    unproven = [n for n in new_shapes if not proven(n, cur_g)]
    print("current  : %s" % os.path.basename(current_path))
    print("baseline : %s (a real, distinct file, hash-verified different from current)" % os.path.basename(published[-1]))
    print("shapes in current file   : %d" % len(cur_names))
    print("shapes already published : %d" % len(pub_names & cur_names))
    print("NEW since baseline       : %d" % len(new_shapes))
    for n in unproven:
        print("   UNPROVEN NEW SHAPE  %s" % n.split("#")[-1])
    print("VERDICT     : %s" % (
        "PASS - every newly authored shape declares its proof, verified against a real, distinct baseline"
        if not unproven else
        "REPORTED - %d new shape(s) ship without provenByFixture" % len(unproven)))
    sys.exit(1 if (unproven and strict) else 0)


if __name__ == "__main__":
    main()
