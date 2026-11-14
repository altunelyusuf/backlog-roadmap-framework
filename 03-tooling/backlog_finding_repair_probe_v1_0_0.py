#!/usr/bin/env python3
"""backlog_finding_repair_probe v1.0.0 -- Lineage 29, box 48 (G235; 2SISA handover of 2026-11-10, review findings without repair items).

Runs FindingNeedsRepairShape itself, copied from the newest shapes file, with pyshacl exactly as the validator runs it (advanced, no inference) over the newest T-box and a small
register planted with each case. Nothing is re-derived here: a case either makes the shape fire or it does not. Cases: a finding raised by the review of a finished item that has no
repair item, no remedy carried out and no record fires; each of the three ways out conforms (a defect item; a remedy in a Done iteration with evidence; a finding record with a
disposition other than Nonconformity, a preventive mechanism and a review date); a record missing the mechanism, the review date or the disposition, a Nonconformity record, a
remedy in an open iteration, a remedy with no evidence and a repair that is not a defect each still fire; a finding that does not say a review raised it is not touched.
"""
import os, re, sys, glob
from rdflib import Graph, Namespace, BNode, URIRef
from rdflib.namespace import RDF
import pyshacl

HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.join(HERE, "..")
SH = Namespace("http://www.w3.org/ns/shacl#"); BL = Namespace("http://example.org/backlog#")


def newest(folder, stem):
    fs = glob.glob(os.path.join(PKG, folder, stem + "_v*.ttl"))
    return sorted(fs, key=lambda f: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", f)[0]])[-1]


SHAPES = Graph(); SHAPES.parse(newest("02-shacl-safeguards", "backlog_shacl"), format="turtle")
TBOX = newest("01-ontologies", "backlog_tbox")
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(TBOX); print(newest("02-shacl-safeguards", "backlog_shacl")); sys.exit(0)
RED = Graph()
seen = set()


def walk(n):
    if n in seen:
        return
    seen.add(n)
    for p, o in SHAPES.predicate_objects(n):
        RED.add((n, p, o))
        if isinstance(o, BNode) or p in (SH.prefixes, SH.declare):
            walk(o)


walk(BL["FindingNeedsRepairShape"])
PRE = ("@prefix backlog: <http://example.org/backlog#> . @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> . "
       "@prefix ex: <http://example.org/probe#> .\n")
ITEM = "ex:I a backlog:Story ; backlog:hasState backlog:Done .\n"
FIND = 'ex:F a backlog:%s ; backlog:hasRootCause "c" ; backlog:hasFindingScope backlog:Scope_LineageLocal %s .\n'
IT = "ex:It a backlog:Iteration ; backlog:hasState backlog:%s .\n"
DEF = "ex:D a backlog:%s .\n"
REC = "; backlog:hasFindingDisposition backlog:%s ; backlog:preventiveMechanism \"a mechanism\" ; backlog:dispositionReviewDue \"2027-01-01T00:00:00Z\"^^xsd:dateTime"
RAISED = "; backlog:raisedByReviewOf ex:I"


def fires(ttl):
    dg = Graph(); dg.parse(TBOX, format="turtle"); dg.parse(data=PRE + ttl, format="turtle")
    _, rg, _ = pyshacl.validate(dg, shacl_graph=RED, advanced=True, inference="none")
    return any(str(rg.value(r, SH.focusNode)).endswith("#F") for r in rg.subjects(RDF.type, SH.ValidationResult))


FAILS = []
N = [0]


def expect(what, ok):
    N[0] += 1
    if not ok:
        FAILS.append(what); print("FAIL ", what)


expect("a finding raised by the review of a finished item, with no repair, no remedy and no record, is refused", fires(ITEM + FIND % ("RetrospectiveFinding", RAISED)))
expect("a defect item that repairs it lets it conform", not fires(ITEM + DEF % "Defect" + FIND % ("RetrospectiveFinding", RAISED + "; backlog:repairedByItem ex:D")))
expect("a repair that is not a defect item does not", fires(ITEM + DEF % "Story" + FIND % ("RetrospectiveFinding", RAISED + "; backlog:repairedByItem ex:D")))
expect("a repair named but not described at all does not", fires(ITEM + FIND % ("RetrospectiveFinding", RAISED + "; backlog:repairedByItem ex:Nowhere")))
expect("a remedy carried out in a Done iteration and shown by evidence lets it conform", not fires(ITEM + IT % "Done" + FIND % ("RetrospectiveFinding", RAISED + "; backlog:remedyCarriedOutIn ex:It ; backlog:remedyShownBy ex:E")))
expect("a remedy in an iteration still open does not", fires(ITEM + IT % "InProgress" + FIND % ("RetrospectiveFinding", RAISED + "; backlog:remedyCarriedOutIn ex:It ; backlog:remedyShownBy ex:E")))
expect("a remedy with no evidence does not", fires(ITEM + IT % "Done" + FIND % ("RetrospectiveFinding", RAISED + "; backlog:remedyCarriedOutIn ex:It")))
for disp in ("Disp_KnownError", "Disp_RiskAccepted", "Disp_Observation"):
    expect("a finding record with %s, a preventive mechanism and a review date lets it conform" % disp, not fires(ITEM + FIND % ("FindingRecord", RAISED + REC % disp)))
expect("a finding record with the disposition Nonconformity does not", fires(ITEM + FIND % ("FindingRecord", RAISED + REC % "Disp_Nonconformity")))
expect("a finding record with no preventive mechanism does not", fires(ITEM + FIND % ("FindingRecord", RAISED + REC.replace('; backlog:preventiveMechanism "a mechanism"', "") % "Disp_KnownError")))
expect("a finding record with no review date does not", fires(ITEM + FIND % ("FindingRecord", RAISED + REC.replace('; backlog:dispositionReviewDue "2027-01-01T00:00:00Z"^^xsd:dateTime', "") % "Disp_KnownError")))
expect("a finding record with no disposition does not", fires(ITEM + FIND % ("FindingRecord", RAISED + '; backlog:preventiveMechanism "a mechanism" ; backlog:dispositionReviewDue "2027-01-01T00:00:00Z"^^xsd:dateTime')))
expect("a finding that does not say a review raised it is not touched", not fires(ITEM + FIND % ("RetrospectiveFinding", "")))
expect("a plain finding record with its mechanism and date, raised by no review, is not touched", not fires(ITEM + FIND % ("FindingRecord", REC % "Disp_KnownError")))
CLOSED = "ex:L a backlog:Lineage ; backlog:hasLineageStatus backlog:LS_Achieved .\n"
expect("a lineage that is closed holds a finding with no repair, no remedy and no record: the finding is refused, so the lineage cannot close on it", fires(CLOSED + ITEM + FIND % ("RetrospectiveFinding", RAISED + "; backlog:belongsToLineage ex:L")))
expect("the same lineage with the finding's repair item named: the finding conforms", not fires(CLOSED + ITEM + DEF % "Defect" + FIND % ("RetrospectiveFinding", RAISED + "; backlog:belongsToLineage ex:L ; backlog:repairedByItem ex:D")))
print("VERDICT: %s -- %d expectations %s" % ("PASS" if not FAILS else "FAIL", N[0], "hold" if not FAILS else "(%d failed)" % len(FAILS)))
sys.exit(1 if FAILS else 0)
