#!/usr/bin/env python3
"""backlog_adoption_check_v1_0_0.py — capabilities shipped and never adopted.

A1 from the lineage discipline. G20 recurs because a class and the constraint
that requires it are separate objects with no relation between them:

  Package        unused for 91 releases
  TaskType       14 values, 44 of 51 tasks chose one
  TestCase       shipped, 46 of 55 stories never used it
  CodeTable      hasTableKind existed, nothing required it

Every one was a capability delivered and not adopted, and the gap was invisible
because nothing joined the thing built to the thing that would make anyone use
it.

Three states per class, reported separately because they mean different things:

  OBLIGED    a shape mentions it, or it declares obligedBy
  OPTIONAL   no obligation and adoptionRationale says why
  ORPHAN     no obligation and no reason given — optional by omission, which
             is what left Package unused while every check passed

Reports rather than fails: 18 orphans today, and a gate failing on 18 gets
suppressed. Exit 1 under --strict.
"""
import sys, os, glob

def main():
    strict = "--strict" in sys.argv
    here = os.path.dirname(os.path.abspath(__file__))
    pkg = os.path.dirname(here)
    tbox = sorted(glob.glob(os.path.join(
        pkg, "01-ontologies", "backlog_tbox_v*.ttl")))
    shacl = sorted(glob.glob(os.path.join(
        pkg, "02-shacl-safeguards", "backlog_shacl_v*.ttl")))
    if not tbox or not shacl:
        raise SystemExit(
            "FATAL: no TBox or shapes found. This reports on the terms it "
            "reads, so with nothing to read it would report zero orphans and "
            "PASS. Refusing to return a verdict about files it never opened.")
    from rdflib import Graph, Namespace, RDF, OWL
    B = Namespace("http://example.org/backlog#")
    g = Graph()
    g.parse(tbox[-1], format="turtle")
    shapes_text = open(shacl[-1], encoding="utf-8").read()

    obliged = optional = []
    obliged, optional, orphan = [], [], []
    for c in g.subjects(RDF.type, OWL.Class):
        if not str(c).startswith(str(B)):
            continue
        name = str(c).split("#")[-1]
        if list(g.objects(c, OWL.oneOf)):
            continue                      # enumerations are used by their members
        if ("backlog:" + name) in shapes_text or g.value(c, B.obligedBy):
            obliged.append(name)
        elif g.value(c, B.adoptionRationale):
            optional.append(name)
        else:
            orphan.append(name)

    print("classes examined     : %d" % (len(obliged) + len(optional) + len(orphan)))
    print("obliged by a shape   : %d" % len(obliged))
    print("optional, with reason: %d" % len(optional))
    print("ORPHAN               : %d" % len(orphan))
    for n in sorted(orphan):
        print("   %s" % n)
    print("VERDICT     : %s" % (
        "PASS - every class is obliged or optional for a stated reason"
        if not orphan else
        "REPORTED - %d class(es) optional by omission; a capability nothing "
        "requires is one that gets skipped" % len(orphan)))
    sys.exit(1 if (orphan and strict) else 0)

if __name__ == "__main__":
    main()
