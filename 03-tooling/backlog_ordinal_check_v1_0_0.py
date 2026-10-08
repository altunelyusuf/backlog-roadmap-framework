#!/usr/bin/env python3
"""backlog_ordinal_check v1.0.0 -- every lineage holds its own place in the sequence, across the live register AND the archive.

The ordinal says where a lineage falls in the sequence of runs. Two lineages on one number make that order ambiguous. Until this tool nothing compared ordinals
between the live register and the archive, so a new lineage could take a number an archived one already held (ordinals 17 and 18 were each given twice).

Rule: an ordinal is carried by one lineage, counted over the live data file and the archive data file together. The only excuse is an owner-declared record
in the live data file (a "declared shared ordinal": the ordinal and EXACTLY the lineages that share it). A declaration never covers a third lineage, and a
declaration that names a lineage which does not carry that ordinal is itself a fault.

Commands (all print plainly; exit 0 conformant, 2 a collision or a bad declaration, 3 the check could not discriminate):
  check   (default)  judge the real data; first prove, on throwaway copies, that a planted collision is flagged, a declared pair is excused, and a third lineage
                     on a declared number is flagged -- if any of those fails the tool refuses to certify (exit 3).
  next               print the next free ordinal (highest carried anywhere + 1). Use it BEFORE opening a lineage.
Options: --live FILE  --archive FILE  (default: newest data files in the package)

WHAT TO DO IF A COLLISION IS REPORTED (the same text is printed with every failure):
  1 Never change an archived lineage's ordinal. Archived records are settled history.
  2 If the colliding lineage is YOUR OWN and not yet archived: give it the number printed by `next`, then run the check again. That is a correction to your own record.
  3 If both lineages are archived, or the other one belongs to someone else: do not renumber. Hand the two lineage labels and the number to the framework owner as a
    handover; the owner decides whether to declare the pair (a recorded exception) or to renumber, and a declaration is added to the live data file as a new version.
  4 Never loosen this check or delete a declaration to make a run pass.
"""
import glob, os, re, sys, tempfile
from rdflib import Graph, Namespace, URIRef, Literal, RDF
from rdflib.namespace import XSD

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = Namespace("http://example.org/backlog#")
P = Namespace("http://example.org/ordinalprobe#")

GUIDE = """WHAT TO DO:
  1 Never change an archived lineage's ordinal.
  2 Your own lineage, not yet archived: give it the number from `backlog_ordinal_check next`, then run the check again.
  3 Both archived, or the other lineage is not yours: do not renumber. Hand the two lineage labels and the number to the framework owner (handover); the owner declares the pair or renumbers.
  4 Never loosen the check or delete a declaration to pass."""


def newest(pattern):
    hits = glob.glob(pattern)
    if not hits:
        raise SystemExit("not found: %s" % pattern)
    def key(p):
        m = re.search(r"_v(\d+)_(\d+)_(\d+)\.", p)
        return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)
    return sorted(hits, key=key)[-1]


def load(*paths):
    g = Graph()
    for p in paths:
        g.parse(p, format="turtle")
    return g


def judge(g):
    """Return (problems, carried) for one combined graph. problems: list of text lines; carried: {lineage: ordinal}."""
    carried = {}
    by_ord = {}
    problems = []
    for lin in set(g.subjects(RDF.type, B.Lineage)):
        vals = [int(o) for o in g.objects(lin, B.lineageOrdinal)]
        if len(vals) != 1:
            problems.append("lineage %s holds %d ordinals (needs exactly one)" % (label(g, lin), len(vals)))
            continue
        carried[lin] = vals[0]
        by_ord.setdefault(vals[0], set()).add(lin)
    declared = {}
    for d in g.subjects(RDF.type, B.OrdinalSharingDeclaration):
        o = list(g.objects(d, B.declaredOrdinal))
        who = set(g.objects(d, B.sharedByLineage))
        if len(o) != 1 or len(who) < 2:
            problems.append("declaration %s must state one ordinal and at least two lineages" % d)
            continue
        n = int(o[0])
        declared.setdefault(n, []).append(who)
        for lin in who:
            if carried.get(lin) != n:
                problems.append("declaration for ordinal %d names %s, which does not carry that ordinal" % (n, label(g, lin)))
    for n, lins in sorted(by_ord.items()):
        if len(lins) < 2:
            continue
        if any(who == lins for who in declared.get(n, [])):
            continue
        names = ", ".join(sorted(label(g, l) for l in lins))
        problems.append("ordinal %d is carried by %d lineages: %s" % (n, len(lins), names))
    return problems, carried


def label(g, node):
    for o in g.objects(node, URIRef("http://www.w3.org/2000/01/rdf-schema#label")):
        return str(o)
    return str(node).split("#")[-1]


def add_lineage(g, name, n):
    g.add((P[name], RDF.type, B.Lineage))
    g.add((P[name], B.lineageOrdinal, Literal(n, datatype=XSD.integer)))


def declare(g, name, n, *names):
    d = P[name]
    g.add((d, RDF.type, B.OrdinalSharingDeclaration))
    g.add((d, B.declaredOrdinal, Literal(n, datatype=XSD.integer)))
    for x in names:
        g.add((d, B.sharedByLineage, P[x]))


def self_proof():
    """Three throwaway cases, each judged by the real judge. Returns list of failures."""
    bad = []
    g = Graph(); add_lineage(g, "A", 1); add_lineage(g, "B", 2)
    if judge(g)[0]:
        bad.append("a clean pair was flagged")
    g = Graph(); add_lineage(g, "A", 1); add_lineage(g, "B", 1)
    if not judge(g)[0]:
        bad.append("a planted collision was NOT flagged")
    g = Graph(); add_lineage(g, "A", 1); add_lineage(g, "B", 1); declare(g, "D", 1, "A", "B")
    if judge(g)[0]:
        bad.append("a declared pair was not excused")
    g = Graph(); add_lineage(g, "A", 1); add_lineage(g, "B", 1); add_lineage(g, "C", 1); declare(g, "D", 1, "A", "B")
    if not judge(g)[0]:
        bad.append("a third lineage on a declared number was NOT flagged")
    g = Graph(); add_lineage(g, "A", 1); add_lineage(g, "B", 2); declare(g, "D", 1, "A", "B")
    if not judge(g)[0]:
        bad.append("a declaration naming a lineage that carries another number was NOT flagged")
    return bad


def main(argv):
    live = arch = None
    cmd = "check"
    args = list(argv)
    while args:
        a = args.pop(0)
        if a == "--live":
            live = args.pop(0)
        elif a == "--archive":
            arch = args.pop(0)
        elif a in ("check", "next"):
            cmd = a
        else:
            print("unknown argument: %s" % a); return 2
    live = live or newest(os.path.join(PKG, "01-ontologies", "backlog_abox_v*.ttl"))
    arch = arch or newest(os.path.join(PKG, "01-ontologies", "archive", "backlog_framework_archive_abox_v*.ttl"))
    g = load(live, arch)
    problems, carried = judge(g)
    if cmd == "next":
        print(max(carried.values()) + 1 if carried else 1)
        return 0 if not problems else 2
    bad = self_proof()
    for b in bad:
        print("SELF-PROOF FAILED: %s" % b)
    if bad:
        print("VERDICT: the check could not discriminate; not certifying")
        return 3
    print("SELF-PROOF: collision flagged, declared pair excused, third lineage flagged, wrong declaration flagged")
    print("lineages counted: %d (live + archive); next free ordinal: %d" % (len(carried), max(carried.values()) + 1))
    for p in problems:
        print("COLLISION: %s" % p)
    if problems:
        print(GUIDE)
        print("VERDICT: FAIL (%d)" % len(problems))
        return 2
    print("VERDICT: conformant")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
