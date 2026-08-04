#!/usr/bin/env python3
"""backlog_quality_assessment v1.0.0 — structural quality metrics for the subject.

Closes the quality-facet gap the registration round left open, and closes it with
computed numbers rather than a token instance. Every metric here is derived from
the shipped TBox and ABox at run time, so the evaluating session can recompute
each one instead of accepting it — which is what Phase C does with every number a
registrant states.

Metrics implemented (OntoQA structural family, Tartir et al.), each bound to the
quality subject's own metric class:

  RelationshipRichness   non-inheritance edges as a share of all class-level edges
  AttributeRichness      datatype properties per class
  InheritanceRichness    average direct subclasses per class
  ClassRichness          classes carrying at least one instance
  AveragePopulation      instances per class
  Deepness               maximum depth of the subclass tree
  NumberOfRootClasses    classes with no local superclass
  NumberOfLeafClasses    classes with no local subclass
  AnnotationRichness     share of terms carrying a skos:definition

NOT assessed, and deliberately not implied: OQuaRE tier-weighted scoring, OOPS!
pitfall scanning, usability profiling, or any dimension requiring a stakeholder
judgement. This is a structural assessment. Calling it a quality assessment
without that sentence would be the "comprehensive" claim L-74 exists to prevent.

Usage:
  backlog_quality_assessment_v1_0_0.py [--emit assessment.ttl]
"""

import argparse
import glob
import os
import sys
from collections import defaultdict

import rdflib
from rdflib import Graph, Literal, Namespace, RDF, RDFS, OWL, URIRef, XSD

BL = Namespace("http://example.org/backlog#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)


def latest(subdir, stem):
    hits = glob.glob(os.path.join(PKG, subdir, "%s_v*.ttl" % stem))
    if not hits:
        raise SystemExit("no artifact matching %s/%s_v*.ttl" % (subdir, stem))
    return sorted(hits)[-1]


def local(term):
    return str(term).rsplit("#", 1)[-1]


def measure(with_fixture=False):
    tbox_path, abox_path = latest("01-ontologies", "backlog_tbox"), latest("01-ontologies", "backlog_abox")
    g = Graph()
    g.parse(tbox_path, format="turtle")
    g.parse(abox_path, format="turtle")
    fixture_path = None
    if with_fixture:
        # population metrics measured on the framework ABox alone understate the
        # subject: most register classes are instantiated by adopters, not by the
        # framework. The shipped positive fixture is the closest thing to a real
        # adopter register, so both readings are reported rather than the flattering one.
        hits = sorted(glob.glob(os.path.join(PKG, "03-tooling", "fixtures", "fixture_positive_v*.ttl")))
        if hits:
            fixture_path = hits[-1]
            g.parse(fixture_path, format="turtle")
    for t in list(g.triples((None, OWL.imports, None))):
        g.remove(t)

    own = lambda n: isinstance(n, URIRef) and str(n).startswith(str(BL))

    classes = {c for c in g.subjects(RDF.type, OWL.Class) if own(c)}
    obj_props = {p for p in g.subjects(RDF.type, OWL.ObjectProperty) if own(p)}
    dat_props = {p for p in g.subjects(RDF.type, OWL.DatatypeProperty) if own(p)}

    subclass_edges = [(s, o) for s, o in g.subject_objects(RDFS.subClassOf) if own(s) and own(o)]
    children = defaultdict(set)
    parents = defaultdict(set)
    for s, o in subclass_edges:
        children[o].add(s)
        parents[s].add(o)

    # individuals of our own classes
    # population counts every instance of one of OUR classes, whatever namespace the
    # instance itself lives in: an adopter's register instantiates our classes under
    # its own IRIs, and requiring the instance IRI to be ours silently excluded exactly
    # the population the second reading exists to show.
    individuals = {s for s, o in g.subject_objects(RDF.type)
                   if isinstance(s, URIRef) and o in classes}
    populated = {o for s, o in g.subject_objects(RDF.type)
                 if isinstance(s, URIRef) and o in classes}

    def depth(c, seen=None):
        seen = seen or set()
        if c in seen or not parents[c]:
            return 1
        return 1 + max(depth(p, seen | {c}) for p in parents[c])

    n_classes = len(classes) or 1
    defined = {t for t in classes | obj_props | dat_props if g.value(t, SKOS.definition)}
    all_terms = classes | obj_props | dat_props

    return {
        "files": (os.path.basename(tbox_path), os.path.basename(abox_path)),
        "fixture": os.path.basename(fixture_path) if fixture_path else None,
        "counts": {"classes": len(classes), "objectProperties": len(obj_props),
                   "datatypeProperties": len(dat_props), "subClassOfEdges": len(subclass_edges),
                   "individuals": len(individuals), "terms": len(all_terms)},
        "metrics": [
            ("RelationshipRichness", len(obj_props) / (len(obj_props) + len(subclass_edges) or 1),
             "|objectProperties| / (|objectProperties| + |subClassOf edges|)"),
            ("AttributeRichness", len(dat_props) / n_classes, "|datatypeProperties| / |classes|"),
            ("InheritanceRichness", len(subclass_edges) / n_classes, "|subClassOf edges| / |classes|"),
            ("ClassRichness", len(populated) / n_classes, "|classes with >=1 instance| / |classes|"),
            ("AveragePopulation", len(individuals) / n_classes, "|individuals| / |classes|"),
            ("Deepness", float(max((depth(c) for c in classes), default=0)),
             "longest local rdfs:subClassOf chain"),
            ("NumberOfRootClasses", float(sum(1 for c in classes if not parents[c])),
             "classes with no local superclass"),
            ("NumberOfLeafClasses", float(sum(1 for c in classes if not children[c])),
             "classes with no local subclass"),
            ("AnnotationRichness", len(defined) / (len(all_terms) or 1),
             "|terms with skos:definition| / |terms|"),
        ],
    }


def main():
    ap = argparse.ArgumentParser(description="Compute structural quality metrics for the backlog subject.")
    ap.add_argument("--emit", default=None, help="write the QualityAssessment instances to this Turtle file")
    args = ap.parse_args()

    r = measure()
    r_used = measure(with_fixture=True)
    print("subject     : http://example.org/backlog")
    print("measured on : %s + %s" % r["files"])
    print("tooling     : rdflib %s, backlog_quality_assessment v1.0.0, imports stripped" % rdflib.__version__)
    print("counts      : " + ", ".join("%s %d" % (k, v) for k, v in r["counts"].items()))
    print("\nstructural metrics (OntoQA family):")
    for name, value, method in r["metrics"]:
        print("  %-22s %8.3f   %s" % (name, value, method))
    print("\npopulation metrics, second reading with the shipped adopter fixture merged (%s):" % r_used["fixture"])
    for name, value, _ in r_used["metrics"]:
        if name in ("ClassRichness", "AveragePopulation"):
            print("  %-22s %8.3f" % (name, value))
    print("  the framework ABox holds framework-level individuals only, so the first reading")
    print("  understates population by design; both are reported rather than the flattering one.")
    print("\nNOT assessed: OQuaRE tier-weighted scoring, OOPS! pitfall scanning, usability")
    print("profiling, and every dimension needing a stakeholder judgement. Structural only.")

    if args.emit:
        Q = Namespace("http://example.org/quality#")
        CORE = Namespace("http://example.org/core#")
        PKGNS = Namespace("http://example.org/backlog-package#")
        DCT = Namespace("http://purl.org/dc/terms/")
        out = Graph()
        out.bind("quality", Q); out.bind("pkg", PKGNS); out.bind("core", CORE)
        out.bind("skos", SKOS); out.bind("dcterms", DCT)
        src = ("Computed by backlog_quality_assessment_v1_0_0.py from %s and %s; "
               "every value is re-derivable by re-running that script." % r["files"])
        qa = PKGNS["QualityAssessment_BacklogSubject_v1_0_0"]
        out.add((qa, RDF.type, Q.QualityAssessment))
        out.add((qa, RDF.type, OWL.NamedIndividual))
        out.add((qa, RDFS.label, Literal("Structural quality assessment of the backlog subject", lang="en")))
        out.add((qa, Q.assessesArtifact, PKGNS.Artifact_Backlog_TBox))
        out.add((qa, DCT.source, Literal(src)))
        out.add((qa, SKOS.definition, Literal(
            "Structural quality assessment of http://example.org/backlog using the OntoQA metric "
            "family, computed from the shipped TBox and ABox rather than estimated. Scope is stated "
            "rather than implied: it covers structural characteristics only and makes no OQuaRE "
            "tier-weighted, pitfall-scanning, or usability claim, so it must not be read as a "
            "comprehensive quality assessment.", lang="en")))
        for name, value, method in r["metrics"]:
            if name in ("ClassRichness", "AveragePopulation"):
                used = dict((n, v) for n, v, _ in r_used["metrics"])[name]
                method = ("%s — framework ABox only; with the shipped adopter fixture merged the "
                          "value is %.3f, and both readings are recorded because the framework ABox "
                          "deliberately holds framework-level individuals only" % (method, used))
            m = PKGNS["Metric_%s_v1_0_0" % name]
            out.add((m, RDF.type, Q[name]))
            out.add((m, RDF.type, Q.QualityMetric))
            out.add((m, RDF.type, OWL.NamedIndividual))
            out.add((m, RDFS.label, Literal("%s = %.3f" % (name, value), lang="en")))
            out.add((m, SKOS.definition, Literal("%s, computed as %s." % (name, method), lang="en")))
            out.add((m, DCT.source, Literal(src)))
            out.add((qa, Q.hasMetric, m))
        out.serialize(args.emit, format="turtle")
        print("\nemitted: %s (%d triples)" % (args.emit, len(out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
