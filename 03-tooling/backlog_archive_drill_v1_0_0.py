#!/usr/bin/env python3
"""backlog_archive_drill v1.0.0 -- the archive tool's refusals are shown on planted lineages (Lineage 19, DC-S01).

The archive tool (backlog_lineage_archive) decides whether a lineage may be set down. This drill builds small lineages in memory and requires:
  1. an achieved lineage with a closure report                       -> archivable
  2. an achieved lineage with no closure report                      -> refused, naming the missing report
  3. an abandoned lineage with its reason and NO closure report      -> refused (v2.4.0 accepted it)
  4. an abandoned lineage with its reason and a report               -> archivable
  5. a lineage whose report omits a cancelled item                   -> refused, naming the item; when the report names it -> archivable
Exit 0 when every case behaves, 3 otherwise.
Usage: backlog_archive_drill_v1_0_0.py
"""
import glob, importlib.util, os, re, sys
from rdflib import Graph, Namespace, URIRef, Literal, RDF

HERE = os.path.dirname(os.path.abspath(__file__))
B = Namespace("http://example.org/backlog#")
P = Namespace("http://example.org/drill#")


def tool():
    p = sorted(glob.glob(os.path.join(HERE, "backlog_lineage_archive_v*.py")), key=lambda x: [int(n) for n in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", x)[0]])[-1]
    spec = importlib.util.spec_from_file_location("lar", p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m, os.path.basename(p)


def lineage(outcome, report=True, cancelled=False, names_cancelled=False):
    g = Graph()
    g.add((P.L, RDF.type, B.Lineage)); g.add((P.L, B.lineageForMission, P.M)); g.add((P.L, B.lineageArchived, Literal(False)))
    g.add((P.M, RDF.type, B.Mission)); g.add((P.M, B.hasMissionOutcome, outcome)); g.add((P.M, B.outcomeRationale, Literal("drill")))
    g.add((P.S1, RDF.type, B.Story)); g.add((P.S1, B.belongsToLineage, P.L)); g.add((P.S1, B.hasState, B.Done))
    if report:
        g.add((P.R, RDF.type, B.ClosureReport)); g.add((P.R, B.closesForMission, P.M))
    if cancelled:
        g.add((P.S2, RDF.type, B.Story)); g.add((P.S2, B.belongsToLineage, P.L)); g.add((P.S2, B.hasState, B.Cancelled))
        if names_cancelled:
            g.add((P.R, B.reportsCancelledItem, P.S2))
    return g


def main():
    m, name = tool()
    cases = [
        ("achieved, report: archivable", lineage(B.Out_Achieved), lambda r: r == []),
        ("achieved, no report: refused", lineage(B.Out_Achieved, report=False), lambda r: any("no ClosureReport" in x for x in r)),
        ("abandoned, reason only: refused", lineage(B.Out_Abandoned, report=False), lambda r: any("no ClosureReport" in x for x in r)),
        ("abandoned, reason and report: archivable", lineage(B.Out_Abandoned), lambda r: r == []),
        ("report omits a cancelled item: refused, naming it", lineage(B.Out_Abandoned, cancelled=True), lambda r: any("S2" in x for x in r)),
        ("report names the cancelled item: archivable", lineage(B.Out_Abandoned, cancelled=True, names_cancelled=True), lambda r: r == []),
    ]
    bad = 0
    for label, g, ok in cases:
        r = m.archivable(g, P.L); good = ok(r); bad += not good
        print("  %-52s %s" % (label, "ok" if good else "FAILED: %s" % r))
    print("tool    : %s" % name)
    print("VERDICT : " + ("PASS" if not bad else "FAIL -- %d case(s)" % bad))
    return 0 if not bad else 3


if __name__ == "__main__":
    sys.exit(main())
