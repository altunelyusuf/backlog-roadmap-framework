#!/usr/bin/env python3
"""backlog_make_promoted_shapes v1.2.0 -- derive the severity-promotion overlay from the shapes and the audit's own record.

A register that declares
    fw:Register backlog:adoptsRuleSet backlog:RS_SeverityAudit_20260909 .
is validated against the overlay INSTEAD of the base shapes (backlog_validate's promoted_overlay): the base shapes with each
audited shape's severity replaced by the audit's.

v1.2.0 (Lineage 17, OESC-S01; the Mission's "never a second file of the same role"): the overlay is no longer a file the package
ships. Until v1.1.0 it was a full second copy of the shapes, kept in step by a regeneration script and a gate, differing from the
base only in the severity of the audited shapes. What it carried that the shapes did not is, per audited shape, a severity and a
reason; that is now data in the A-Box: one backlog:SeverityPromotion per audited shape (62 at this release). The overlay is derived
from the shapes and those individuals every time it is needed, so it cannot fall behind the shapes (the failure v1.1.0 existed to
fix: an overlay 20 versions and 21 shapes behind) and there is no second file to keep current.

A base shape with no promotion keeps its base severity and is reported as UNAUDITED: promoting it would be a classification
decision, not a derivation. A promotion naming a shape that no longer exists is DROPPED and fails the check.

Usage:
  backlog_make_promoted_shapes_v1_2_0.py                       check: counts, UNAUDITED, DROPPED; exit 2 on a dropped or malformed promotion
  backlog_make_promoted_shapes_v1_2_0.py --write PATH          write the derived overlay to PATH (a throwaway artefact, never shipped)
  backlog_make_promoted_shapes_v1_2_0.py --against FILE ...    also compare the derivation with existing files (repeatable; the migration
                                                               proof: derived == the last shipped overlay plus the rules file it was
                                                               loaded with, ontology headers aside)
"""
import glob, hashlib, os, re, sys
from rdflib import Graph, Namespace, RDF, OWL, BNode, URIRef

HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
B = Namespace("http://example.org/backlog#"); SH = Namespace("http://www.w3.org/ns/shacl#")
RULESET = B.RS_SeverityAudit_20260909
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]


def latest(sub, stem):
    c = sorted(glob.glob(os.path.join(PKG, sub, stem + "_v*.ttl")), key=sv)
    if not c:
        raise SystemExit(f"no {stem} in {sub}")
    return c[-1]


def promotions(abox_graph):
    """{shape IRI: (severity IRI, rationale)} for the severity audit, and a list of malformed promotions."""
    out, bad = {}, []
    for p in abox_graph.subjects(RDF.type, B.SeverityPromotion):
        if (p, B.promotionInRuleSet, RULESET) not in abox_graph:
            continue
        shape, sev = abox_graph.value(p, B.promotesShape), abox_graph.value(p, B.promotedSeverity)
        why = abox_graph.value(p, B.promotionRationale)
        if shape is None or sev is None or why is None or shape in out:
            bad.append(str(p)); continue
        out[shape] = (sev, str(why))
    return out, bad


def derive(shapes_graph, abox_graph):
    """The overlay: a copy of the shapes with each promoted shape's severity replaced. Returns (graph, unaudited, dropped, malformed)."""
    promo, bad = promotions(abox_graph)
    g = Graph()
    for pfx, ns in shapes_graph.namespaces():
        g.bind(pfx, ns)
    for t in shapes_graph:
        g.add(t)
    dropped = []
    for shape, (sev, _) in promo.items():
        if (shape, RDF.type, SH.NodeShape) not in g:
            dropped.append(str(shape)); continue
        for o in list(g.objects(shape, SH.severity)):
            g.remove((shape, SH.severity, o))
        g.add((shape, SH.severity, sev))
    node_shapes = set(g.subjects(RDF.type, SH.NodeShape))
    unaudited = sorted(str(s) for s in node_shapes if s not in promo)
    return g, unaudited, sorted(dropped), bad


def sig(g, skip_headers=True):
    hdr = set(g.subjects(RDF.type, OWL.Ontology)) if skip_headers else set()
    memo = {}
    def h(n):
        if not isinstance(n, BNode):
            return n.n3()
        if n in memo:
            return memo[n]
        memo[n] = "~"
        memo[n] = hashlib.sha1("|".join(sorted(f"{p.n3()} {h(o)}" for p, o in g.predicate_objects(n))).encode()).hexdigest()[:12]
        return memo[n]
    return {f"{h(s)} {p.n3()} {h(o)}" for s, p, o in g if s not in hdr}


def load_live():
    sg = Graph().parse(latest("02-shacl-safeguards", "backlog_shacl"), format="turtle")
    ag = Graph().parse(latest("01-ontologies", "backlog_abox"), format="turtle")
    return sg, ag


def main(argv):
    sg, ag = load_live()
    g, unaudited, dropped, bad = derive(sg, ag)
    promo, _ = promotions(ag)
    print(f"shapes    : {os.path.basename(latest('02-shacl-safeguards', 'backlog_shacl'))} ({len(set(sg.subjects(RDF.type, SH.NodeShape)))} node shapes)")
    print(f"audit     : {len(promo)} promotion(s) in {os.path.basename(latest('01-ontologies', 'backlog_abox'))}")
    print(f"unaudited : {len(unaudited)} shape(s) with no promotion -- kept at base severity")
    if dropped:
        print(f"DROPPED   : {len(dropped)} promotion(s) name a shape that is not in the shapes file: " + ", ".join(x.rsplit('#', 1)[-1] for x in dropped))
    if bad:
        print(f"MALFORMED : {len(bad)} promotion(s) lack a shape, a severity or a rationale, or repeat a shape: " + ", ".join(x.rsplit('#', 1)[-1] for x in bad))
    rc = 2 if (dropped or bad) else 0
    if "--write" in argv:
        path = argv[argv.index("--write") + 1]
        g.serialize(path, format="turtle"); print(f"written   : {path} ({len(g)} statements) -- derived, throwaway, not shipped")
    if "--against" in argv:
        other = Graph()
        for i, a_ in enumerate(argv):
            if a_ == "--against":
                other.parse(argv[i + 1], format="turtle")
        a, b = sig(g), sig(other)
        print(f"against   : derived {len(a)} statements, existing overlay {len(b)}; only derived {len(a - b)}, only existing {len(b - a)}")
        for x in sorted(a - b)[:4]:
            print("  D", x[:200])
        for x in sorted(b - a)[:4]:
            print("  E", x[:200])
        if a != b:
            rc = 2
    print("VERDICT   : " + ("DERIVABLE -- every promotion names a shape and the overlay is derived from the shapes and the audit, nothing else" if rc == 0
                          else "FAILED -- see above"))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
