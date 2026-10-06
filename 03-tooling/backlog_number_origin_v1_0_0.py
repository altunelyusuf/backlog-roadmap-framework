#!/usr/bin/env python3
"""backlog_number_origin_v1_0_0.py — does every number say where it came from?

A3 from the lineage discipline. G24 recurs because nothing marks a figure as
derived or asserted:

  hasCommittedEffort vs hasCapacity   both asserted; an iteration held 15
                                      points declaring 9 and every check passed
  iterationStart / iterationEnd       asserted, compared to nothing; 32 and 28
                                      minutes declared as fourteen days, 667x

Three checks:

  DECLARED    every numeric property states its origin
  QUERIED     every derived property ships the query that recomputes it
  COMPARED    no shape compares two ASSERTED properties to each other — that is
              the G24 shape, and it is the one nothing could see

The third is the point. A derived figure checked against an asserted one is a
real check; two assertions agreeing prove only that someone wrote both.

Exit 1 under --strict.
"""
import sys, os, glob

def main():
    strict = "--strict" in sys.argv
    here = os.path.dirname(os.path.abspath(__file__))
    pkg = os.path.dirname(here)
    tbox = sorted(glob.glob(os.path.join(pkg, "01-ontologies", "backlog_tbox_v*.ttl")))
    shacl = sorted(glob.glob(os.path.join(pkg, "02-shacl-safeguards", "backlog_shacl_v*.ttl")))
    if not tbox or not shacl:
        raise SystemExit(
            "FATAL: no TBox or shapes found. This reports on the properties it "
            "reads, so with nothing to read it would report zero undeclared "
            "numbers and PASS. Refusing to return a verdict about files it "
            "never opened.")

    from rdflib import Graph, Namespace, RDF, RDFS, OWL
    B = Namespace("http://example.org/backlog#")
    XSD = "http://www.w3.org/2001/XMLSchema#"
    g = Graph()
    g.parse(tbox[-1], format="turtle")
    shapes = open(shacl[-1], encoding="utf-8").read()

    numeric, undeclared, unqueried = [], [], []
    asserted = set()
    for p in g.subjects(RDF.type, OWL.DatatypeProperty):
        if not str(p).startswith(str(B)):
            continue
        r = g.value(p, RDFS.range)
        if r is None or str(r) not in (XSD + "decimal", XSD + "integer",
                                       XSD + "float", XSD + "double"):
            continue
        name = str(p).split("#")[-1]
        numeric.append(name)
        origin = g.value(p, B.numberOrigin)
        if origin is None:
            undeclared.append(name)
            continue
        kind = str(origin).split("#")[-1]
        if kind == "Num_Asserted":
            asserted.add(name)
        if kind == "Num_Derived" and g.value(p, B.derivationQuery) is None:
            unqueried.append(name)

    # G24: a shape whose SPARQL mentions two asserted properties is comparing
    # one judgement against another. Reported per clause, not per property.
    both = []
    for block in shapes.split("sh:sparql"):
        hits = sorted({a for a in asserted if ("backlog:" + a) in block})
        if len(hits) >= 2:
            both.append(tuple(hits[:3]))
    both = sorted(set(both))

    print("numeric properties        : %d" % len(numeric))
    print("undeclared origin         : %d" % len(undeclared))
    for n in undeclared:
        print("   %s" % n)
    print("derived without a query   : %d" % len(unqueried))
    for n in unqueried:
        print("   %s" % n)
    print("clauses comparing two asserted properties : %d" % len(both))
    for t in both[:8]:
        print("   %s" % " vs ".join(t))
    bad = undeclared or unqueried
    print("VERDICT     : %s" % (
        "PASS - every number states its origin and every derivation ships"
        if not bad else
        "FAIL - %d number(s) do not say where they came from"
        % (len(undeclared) + len(unqueried))))
    sys.exit(1 if (bad and strict) else 0)

if __name__ == "__main__":
    main()
