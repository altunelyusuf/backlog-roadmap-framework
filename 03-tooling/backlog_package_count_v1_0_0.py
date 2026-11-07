#!/usr/bin/env python3
"""backlog_package_count v1.0.0 (Lineage 32, G219) -- how many packages a lineage needs, measured from its chain.

For each deliverable of the scope: the stories that satisfy it (backlog), the objectives those stories pursue (objectives), the goals those
objectives contribute to (goals), leaving out the mission-facing goal that every deliverable serves. Deliverables that serve the same set of
other goals travel together; the number of such groups is the number of packages (at least one: the simplest lineage has exactly one).
A deliverable no story satisfies is a group of its own. With --check, the packages the register declares (deliversDeliverable) must make
exactly the same groups; the tool then exits 1 and says which deliverables sit wrongly.

usage: backlog_package_count_v1_0_0.py REGISTER.ttl --lineage IRI [--check]
"""
import sys, argparse
from rdflib import Graph, URIRef, Namespace, RDF
B = Namespace("http://example.org/backlog#")

def measure(g, lin):
    dels = sorted(set(g.subjects(RDF.type, B.ScopeDeliverable)) & set(g.subjects(B.belongsToLineage, lin)), key=str)
    groups = {}
    for d in dels:
        goals = set()
        for st in g.subjects(B.satisfiesDeliverable, d):
            for ob in g.objects(st, B.pursuesObjective):
                for go in g.objects(ob, B.contributesToGoal):
                    if (go, B.hasGoalFacing, B.Facing_Mission) not in g:
                        goals.add(go)
        key = frozenset(goals) if goals else frozenset([("none", str(d))])
        groups.setdefault(key, []).append(d)
    return dels, list(groups.values())

def declared(g, lin):
    pk = {}
    for p in g.subjects(RDF.type, B.Package):
        if (p, B.belongsToLineage, lin) in g:
            pk[p] = sorted(g.objects(p, B.deliversDeliverable), key=str)
    return pk

def main(argv):
    ap = argparse.ArgumentParser(); ap.add_argument("register"); ap.add_argument("--lineage", required=True); ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    g = Graph(); g.parse(a.register)
    lin = URIRef(a.lineage if "://" in a.lineage else "http://example.org/backlog-framework-register#" + a.lineage.split(":")[-1])
    dels, groups = measure(g, lin)
    n = max(1, len(groups))
    print("lineage %s: %d deliverables -> %d package(s) needed" % (lin.split("#")[-1], len(dels), n))
    for i, grp in enumerate(groups, 1):
        print("  package %d: %s" % (i, ", ".join(d.split("#")[-1] for d in grp)))
    if not a.check: return 0
    pk = declared(g, lin)
    want = sorted(sorted(map(str, grp)) for grp in groups)
    have = sorted(sorted(map(str, ds)) for ds in pk.values())
    if want == have or (not dels and len(pk) >= 1):
        print("CHECK PASS: the %d declared package(s) make the measured groups" % len(pk)); return 0
    print("CHECK FAIL: %d package(s) declared, %d measured; declared groups differ from the measured ones" % (len(pk), n))
    for p, ds in pk.items(): print("  declared %s: %s" % (p.split("#")[-1], ", ".join(d.split("#")[-1] for d in ds)))
    return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
