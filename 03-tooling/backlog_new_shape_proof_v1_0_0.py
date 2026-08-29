#!/usr/bin/env python3
"""backlog_new_shape_proof_v1_0_0.py — every NEWLY authored shape declares its proof.

#1 of the mitigation plan. A2 (provenByFixture) is proven and shallow: 6 of
238 shapes declare it, 2.5%. Backfilling the other 232 would assert 232 links
this checker did not verify were true when authored — the defect G21 names,
one layer along.

The fix is forward-only, and SHACL cannot express "forward" on its own — a
SPARQL clause has no memory of the previous release. This checker supplies
that memory the same way backlog_distribution_drift_check does: by comparing
the CURRENT shapes file against the last PUBLISHED one. A shape present now
and absent from the published copy is new; a new shape must declare
provenByFixture, or it ships the way every prior unproven clause did.

Once a shape is published it is grandfathered permanently — this never asks
for backfill, only for the next one.

Reports by default; --strict fails.
"""
import sys, os, glob

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

def main():
    strict = "--strict" in sys.argv
    here = os.path.dirname(os.path.abspath(__file__))
    pkg = os.path.dirname(here)
    current = sorted(glob.glob(os.path.join(pkg, "02-shacl-safeguards", "backlog_shacl_v*.ttl")))
    if not current:
        raise SystemExit("FATAL: no shapes file found. Refusing to report on nothing.")
    published_root = os.path.join(os.path.dirname(pkg), "..", "Ontologies",
                                  "backlog-roadmap-framework", "02-shacl-safeguards")
    published = sorted(glob.glob(os.path.join(published_root, "backlog_shacl_v*.ttl")))
    cur_names, cur_g = shape_names(current[-1])
    if not published:
        print("no published baseline found — treating all shapes as grandfathered")
        pub_names = cur_names
    else:
        pub_names, _ = shape_names(published[-1])
    new_shapes = sorted(cur_names - pub_names)
    unproven = [n for n in new_shapes if not proven(n, cur_g)]
    print("shapes in current file   : %d" % len(cur_names))
    print("shapes already published : %d" % len(pub_names & cur_names))
    print("NEW since last publish   : %d" % len(new_shapes))
    for n in unproven:
        print("   UNPROVEN NEW SHAPE  %s" % n.split("#")[-1])
    print("VERDICT     : %s" % (
        "PASS - every newly authored shape declares its proof"
        if not unproven else
        "REPORTED - %d new shape(s) ship without provenByFixture" % len(unproven)))
    sys.exit(1 if (unproven and strict) else 0)

if __name__ == "__main__":
    main()
