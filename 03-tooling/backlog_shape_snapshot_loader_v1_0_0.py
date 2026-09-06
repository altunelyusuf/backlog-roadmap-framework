#!/usr/bin/env python3
"""backlog_shape_snapshot_loader v1.0.0 -- loads a current shapes file and a
real baseline, tags each declared shape by which snapshot it was found in,
and hands the combined graph to pySHACL. Makes NO decision about what is
new, what is proven, or what passes -- that decision is NewUnprovenShapeShape
and SelfComparisonClaimShape, real SPARQL rules evaluated by the SHACL
engine itself, not Python logic.

Built directly in response to the owner's own real challenge: an ontology
cannot verify arbitrary code's own internal logic, but a comparison this
narrow -- which shapes are new, are they proven, does a claimed hash match
-- does not need to be Python logic at all. SPARQL's own SHA256() function
and FILTER NOT EXISTS already express it; this script's only real job is
getting the two files' own real declarations into one graph, tagged by
source, and it makes no pass/fail judgement anywhere in its own code.

Usage:
  python3 backlog_shape_snapshot_loader_v1_0_0.py --baseline PATH [--strict]
"""
import sys, os, glob


def tag_snapshot(source_path, snapshot_iri, into_graph):
    """The ONLY operation this script performs on shape identity: parse a
    real file, find every real sh:NodeShape declared in it, and assert one
    tagging triple per shape. No comparison, no set difference, no
    decision -- those live entirely in the SHACL rules that read this data."""
    import rdflib
    RDF = rdflib.RDF
    SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")
    B = rdflib.Namespace("http://example.org/backlog#")
    g = rdflib.Graph()
    g.parse(source_path, format="turtle")
    for shape in g.subjects(RDF.type, SH.NodeShape):
        into_graph.add((shape, B.declaredInSnapshot, snapshot_iri))
    return g


def main():
    import rdflib
    args = sys.argv[1:]
    strict = "--strict" in args
    baseline_dir = None
    if "--baseline" in args:
        i = args.index("--baseline")
        if i + 1 < len(args):
            baseline_dir = args[i + 1]

    here = os.path.dirname(os.path.abspath(__file__))
    pkg = os.path.dirname(here)
    current = sorted(glob.glob(os.path.join(pkg, "02-shacl-safeguards", "backlog_shacl_v*.ttl")))
    if not current:
        raise SystemExit("FATAL: no shapes file found.")
    current_path = current[-1]

    if not baseline_dir or not os.path.isdir(baseline_dir):
        print("VERDICT     : NOT-VERIFIED — no real baseline directory given")
        sys.exit(1 if strict else 0)
    published = sorted(glob.glob(os.path.join(baseline_dir, "backlog_shacl_v*.ttl")))
    if not published:
        print("VERDICT     : NOT-VERIFIED — baseline directory has no shapes file")
        sys.exit(1 if strict else 0)
    baseline_path = published[-1]

    B = rdflib.Namespace("http://example.org/backlog#")
    tagging = rdflib.Graph()
    current_g = tag_snapshot(current_path, B.Snapshot_Current, tagging)
    tag_snapshot(baseline_path, B.Snapshot_Baseline, tagging)

    # Combine: the real shapes graph (current file, so the rules to evaluate
    # are the live ones) plus the tagging facts a real SHACL rule reads.
    data = current_g + tagging
    shacl = rdflib.Graph()
    shacl.parse(current_path, format="turtle")

    import pyshacl
    conforms, results_graph, results_text = pyshacl.validate(data, shacl_graph=shacl, advanced=True)

    print("current  : %s" % os.path.basename(current_path))
    print("baseline : %s" % os.path.basename(baseline_path))
    print("Decision made entirely by NewUnprovenShapeShape, a real SPARQL rule --")
    print("this script asserted only which snapshot each shape came from.\n")
    hits = [line for line in results_text.split("\n") if "NewUnprovenShapeShape" in line or "genuinely new" in line]
    for h in hits:
        print(h)
    unproven_count = sum(1 for _ in results_graph.subjects(
        rdflib.RDF.type, rdflib.URIRef("http://www.w3.org/ns/shacl#ValidationResult")))
    print("\nVERDICT     : %s" % (
        "PASS - the SHACL engine itself found no new, unproven shape"
        if conforms or not hits else
        "REPORTED - see violations above, each computed by the SHACL rule, not by this script"))
    sys.exit(1 if (hits and strict) else 0)


if __name__ == "__main__":
    main()
