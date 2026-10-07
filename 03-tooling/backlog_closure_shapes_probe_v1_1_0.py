#!/usr/bin/env python3
"""backlog_closure_shapes_probe v1.1.0 (v1.1.0, DC-S04: the module-audience rule is probed too) -- each rule of Lineage 19 is shown firing on a planted fault and silent on its corrected twin.

A rule that has never been seen to fail proves nothing (L-95). This builds small graphs in memory and runs the package's own shapes file over them:
  1. an abandoned mission with no closure report                       -> MissionClosureRequiresReportShape fires; with a report, silent
  2. an ended mission whose report omits a cancelled item of its lineage -> ClosureReportNamesCancelledShape fires; naming the item, silent
  3. a module record with no audience                                    -> ModuleAudienceDeclaredShape fires; with an audience, silent
Exit 0 when every rule fires on its fault and is silent on its twin; 3 otherwise.
Usage: backlog_closure_shapes_probe_v1_1_0.py
"""
import glob, os, re, sys
from rdflib import Graph, Namespace, URIRef, Literal, RDF
from rdflib.namespace import XSD, DCTERMS

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = Namespace("http://example.org/backlog#")
P = Namespace("http://example.org/probe#")
SH = Namespace("http://www.w3.org/ns/shacl#")


def latest(sub, pat):
    hits = glob.glob(os.path.join(PKG, sub, pat))
    return sorted(hits, key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]])[-1]


def fired(shapes, data, marker, focus):
    """True when a result on `focus` carries `marker` in its message (a property shape's source is a blank node, so the message identifies the rule)."""
    import pyshacl
    _, rg, _ = pyshacl.validate(data, shacl_graph=shapes, inference="none", advanced=True, allow_warnings=True)
    for r in rg.subjects(RDF.type, SH.ValidationResult):
        if rg.value(r, SH.focusNode) == focus and marker in str(rg.value(r, SH.resultMessage)):
            return True
    return False


def base(outcome):
    g = Graph()
    m = P.Mission
    g.add((m, RDF.type, B.Mission)); g.add((m, B.hasMissionOutcome, outcome))
    g.add((m, B.outcomeRationale, Literal("probe")))
    return g


def add_report(g, named=()):
    r = P.Report
    g.add((r, RDF.type, B.ClosureReport)); g.add((r, B.closesForMission, P.Mission))
    for i in named:
        g.add((r, B.reportsCancelledItem, i))


def add_lineage_with_cancelled(g):
    g.add((P.Lineage, RDF.type, B.Lineage)); g.add((P.Lineage, B.lineageForMission, P.Mission))
    g.add((P.Item, RDF.type, B.Story)); g.add((P.Item, B.belongsToLineage, P.Lineage)); g.add((P.Item, B.hasState, B.Cancelled))


def main():
    shapes = Graph().parse(latest("02-shacl-safeguards", "backlog_shacl_v*.ttl"))
    results = []
    # 1 abandoned without a report
    g = base(B.Out_Abandoned)
    results.append(("abandoned mission, no report: rule fires", fired(shapes, g, "marked Achieved or Abandoned and no real ClosureReport", P.Mission), True))
    add_report(g)
    results.append(("abandoned mission with a report: rule silent", fired(shapes, g, "marked Achieved or Abandoned and no real ClosureReport", P.Mission), False))
    # 2 report omits a cancelled item
    g = base(B.Out_Achieved); add_lineage_with_cancelled(g); add_report(g)
    results.append(("report omits a cancelled item: rule fires", fired(shapes, g, "does not name an item its lineage cancelled", P.Mission), True))
    g = base(B.Out_Achieved); add_lineage_with_cancelled(g); add_report(g, [P.Item])
    results.append(("report names the cancelled item: rule silent", fired(shapes, g, "does not name an item its lineage cancelled", P.Mission), False))
    # 3 module record without an audience
    g = Graph(); g.add((P.Module, DCTERMS.isPartOf, URIRef("http://example.org/probe")))
    results.append(("module record, no audience: rule fires", fired(shapes, g, "declares no audience", P.Module), True))
    g.add((P.Module, B.moduleAudience, B.Aud_Private))
    results.append(("module record with an audience: rule silent", fired(shapes, g, "declares no audience", P.Module), False))
    bad = 0
    for label, got, want in results:
        ok = got == want
        bad += not ok
        print("  %-52s %s" % (label, "ok" if ok else "FAILED (fired=%s)" % got))
    print("VERDICT : " + ("PASS -- every rule fires on its fault and is silent on its twin" if not bad else "FAIL -- %d probe(s) did not discriminate" % bad))
    return 0 if not bad else 3


if __name__ == "__main__":
    sys.exit(main())
