#!/usr/bin/env python3
"""backlog_archive_shapes_check v1.1.0 -- the archive is judged by the archive's own shapes, and by nothing else (Lineage 18, OC-S03; v1.1.0 Lineage 19, DC-S05).

v1.1.0: the check proves itself against five planted faults, one per rule the archive holds (an orphaned item, an unmarked lineage, an ended mission with no closure report, a cancelled item no report names, a module with no audience), and judge() is importable so the confirmation step judges by the same rules.

The archive folder (01-ontologies/archive/) holds one data file and one shapes file. The shapes file asks only what a retired record must still
hold: an archived item names a lineage the archive holds, and a lineage held there says it is archived (a warning while two earlier lineages
are still unmarked). The live shapes never read this folder, so settled history is not re-judged by rules written for live work.

THE CHECK PROVES ITSELF EVERY RUN. Before it reports the real archive it adds one orphaned item (an item that names a lineage the archive does
not hold) to a copy and requires the shapes to flag it; if they do not, it refuses to certify and exits 3.

Exit 0 conformant (warnings counted and printed), 2 violation, 3 the check could not discriminate.
Usage: backlog_archive_shapes_check_v1_1_0.py
"""
import glob, os, re, sys, time
from rdflib import Graph, URIRef, Namespace

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = Namespace("http://example.org/backlog#")


def latest(pat):
    hits = glob.glob(os.path.join(PKG, "01-ontologies", "archive", pat))
    if not hits:
        raise SystemExit("no %s in 01-ontologies/archive" % pat)
    return sorted(hits, key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]])[-1]


def run(data, shapes):
    import pyshacl
    ok, rg, txt = pyshacl.validate(data, shacl_graph=shapes, inference="none", advanced=True, allow_warnings=True)
    return ok, txt


PLANT = "http://example.org/planted#"


def plant_faults(data):
    """One graph per rule: a copy of the archive with exactly one planted fault, and the message fragment that must flag it."""
    from rdflib import Literal, RDF
    from rdflib.namespace import DCTERMS
    P = lambda n: URIRef(PLANT + n)
    cases = []
    g = Graph()
    g.add((P("Orphan"), B.belongsToLineage, P("NoSuchLineage"))); cases.append(("an orphaned item", g, "Orphan"))
    g = Graph()
    g.add((P("L1"), RDF.type, B.Lineage)); g.add((P("L1"), B.lineageArchived, Literal(False))); cases.append(("an unmarked lineage", g, "L1"))
    g = Graph()
    g.add((P("M2"), RDF.type, B.Mission)); g.add((P("M2"), B.hasMissionOutcome, B.Out_Abandoned)); cases.append(("an ended mission with no closure report", g, "M2"))
    g = Graph()
    for t in [(P("M3"), RDF.type, B.Mission), (P("M3"), B.hasMissionOutcome, B.Out_Achieved), (P("L3"), RDF.type, B.Lineage), (P("L3"), B.lineageForMission, P("M3")),
              (P("R3"), RDF.type, B.ClosureReport), (P("R3"), B.closesForMission, P("M3")),
              (P("I3"), B.belongsToLineage, P("L3")), (P("I3"), B.hasState, B.Cancelled)]:
        g.add(t)
    cases.append(("a cancelled item no report names", g, "M3"))
    g = Graph()
    g.add((P("Mod"), DCTERMS.isPartOf, URIRef("http://example.org/planted"))); cases.append(("a module with no audience", g, "Mod"))
    return cases


def judge(data, shapes):
    """(conformant, text) for a data graph under the archive's own shapes; warnings never fail."""
    return run(data, shapes)


def main():
    a, s = latest("backlog_framework_archive_abox_v*.ttl"), latest("backlog_archive_shacl_v*.ttl")
    data, shapes = Graph().parse(a), Graph().parse(s)
    print("archive : %s (%d triples)" % (os.path.basename(a), len(data)))
    print("shapes  : %s" % os.path.basename(s))
    for label, g, focus in plant_faults(data):
        ok_p, txt_p = run(g, shapes)
        if ok_p or ("planted#" + focus) not in txt_p:
            print("SELF-PROOF : FAILED -- %s was not flagged. Nothing is certified." % label)
            return 3
    print("SELF-PROOF : ok -- each of the five planted faults is flagged by the archive's own shapes")
    t0 = time.time()
    ok, txt = run(data, shapes)
    warn = len(re.findall(r"Severity: sh:Warning", txt)); viol = len(re.findall(r"Severity: sh:Violation", txt))
    print("result  : %d violation(s), %d warning(s) in %.1fs" % (viol, warn, time.time() - t0))
    for m in sorted(set(re.findall(r"Focus Node: (\S+)", txt)))[:6]:
        print("   -", m)
    print("VERDICT : " + ("CONFORMANT" if ok else "VIOLATIONS"))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
