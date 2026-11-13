#!/usr/bin/env python3
"""backlog_criterion_remedy_probe v1.0.0 -- Lineage 29, box 45 (G233; 2SISA delivery handover, gaps 3 and 4).

Runs the three shapes of the box (BoundedCriterionShape, CriterionBoundShape, RemedyCarriedOutShape) themselves, copied from the newest shapes file, with pyshacl exactly as the
validator runs it (advanced, no inference) over the newest T-box and a small register planted with each case. Nothing is re-derived here: a case either makes the shape fire or it does not.
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
NAMES = ("BoundedCriterionShape", "CriterionBoundShape", "RemedyCarriedOutShape", "ScoreAccountabilityShape")
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


for n in NAMES:
    walk(BL[n])
PRE = "@prefix backlog: <http://example.org/backlog#> . @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> . @prefix ex: <http://example.org/probe#> .\n"
OPEN = 'ex:C a backlog:DoDCriterion ; rdfs:label "%s"@en ; backlog:hasCheckQuery "run the tests" ; backlog:hasExpectedResult "all pass" ; backlog:hasCriterionStatus backlog:Holds %s .\n'
BOUND = "ex:B a backlog:CriterionBound %s .\n"
FULL = " ; backlog:keepsCase ex:K ; backlog:provesEveryPartBy ex:E ; backlog:laterFindingsGoTo ex:It"
FIND = 'ex:F a backlog:RetrospectiveFinding ; backlog:hasRootCause "c" ; backlog:hasFindingScope backlog:Scope_LineageLocal %s .\n'
IT = "ex:It a backlog:Iteration ; backlog:hasState backlog:%s .\n"


def fires(ttl):
    dg = Graph(); dg.parse(TBOX, format="turtle"); dg.parse(data=PRE + ttl, format="turtle")
    _, rg, _ = pyshacl.validate(dg, shacl_graph=RED, advanced=True, inference="none")
    out = set()
    for r in rg.subjects(RDF.type, SH.ValidationResult):
        out.add((str(rg.value(r, SH.focusNode)).split("#")[-1], str(rg.value(r, SH.sourceShape)).split("#")[-1] if isinstance(rg.value(r, SH.sourceShape), URIRef) else "-", str(rg.value(r, SH.resultMessage))))
    return out


FAILS = []
N = [0]


def expect(what, ok):
    N[0] += 1
    if not ok:
        FAILS.append(what); print("FAIL ", what)


def has(res, focus, text):
    return any(f == focus and text in m for f, _, m in res)


EVERY = "Every case a reviewer could raise is kept in the committed tests"
r = fires(OPEN % (EVERY, ""))
expect("a criterion worded as every case a reviewer could raise, with no bound, is refused", has(r, "C", "states no bound"))
for w in ("holds for each case a reviewer could raise", "no reviewer can find a spelling that slips through", "every reviewer-raised case passes", "whatever spelling a reviewer may raise is handled", "all the spellings a reviewer could raise", "every possible wording, however a reviewer writes it", "Any spelling a reviewer may raise is handled", "All forms the reviewer could raise are covered", "Each reviewer finds another case, so every variant raised is kept"):
    expect("the open wording is caught in other forms: " + w, has(fires(OPEN % (w, "")), "C", "states no bound"))
expect("a criterion that names its own cases is not an open-ended one", not has(fires(OPEN % ("The five cases kept in the committed tests pass", "")), "C", "states no bound"))
expect("a criterion with a bound that keeps cases, shows every part held and names the iteration for later ones is accepted",
       not has(fires(OPEN % (EVERY, "; backlog:hasCriterionBound ex:B") + BOUND % FULL + IT % "Proposed"), "C", "states no bound"))
for part, text in (("keepsCase", "keeps no case"), ("provesEveryPartBy", "names no evidence that every part"), ("laterFindingsGoTo", "names no iteration for the cases found later")):
    cut = FULL.replace(" ; backlog:%s ex:%s" % (part, {"keepsCase": "K", "provesEveryPartBy": "E", "laterFindingsGoTo": "It"}[part]), "")
    res = fires(OPEN % (EVERY, "; backlog:hasCriterionBound ex:B") + BOUND % cut + IT % "Proposed")
    expect("a bound without %s is refused, and the criterion with it is still refused" % part, has(res, "B", text) and has(res, "C", "states no bound"))
r = fires(FIND % "; backlog:remedyCarriedOutIn ex:It ; backlog:remedyShownBy ex:E" + IT % "InProgress")
expect("a remedy said to be carried out in a box still in progress is refused", has(r, "F", "not Done"))
r = fires(FIND % "; backlog:remedyCarriedOutIn ex:It" + IT % "Done")
expect("a remedy said to be carried out with no evidence is refused", has(r, "F", "names no evidence"))
r = fires(FIND % "; backlog:remedyCarriedOutIn ex:It ; backlog:remedyShownBy ex:E" + IT % "Done")
expect("a remedy carried out in a closed box and shown by evidence is accepted, with no defect item", not any(f == "F" for f, _, _ in r))
r = fires(FIND % "" + IT % "Done")
expect("a finding that says nothing of a remedy carried out is not touched by the shape", not any(f == "F" for f, _, _ in r))
r = fires(FIND % "; backlog:remedyCarriedOutIn ex:It , ex:It2 ; backlog:remedyShownBy ex:E" + IT % "Done" + "ex:It2 a backlog:Iteration ; backlog:hasState backlog:Done .\n")
expect("a finding naming two iterations for one remedy is refused", has(r, "F", "one iteration"))

SC = "ex:I a backlog:Story ; backlog:hasState backlog:Proposed ; backlog:hasPriorityScore ex:Sc .\nex:Sc a backlog:RICEScore ; backlog:scoredAt \"%s\"^^xsd:dateTime .\nex:D a backlog:Story ; backlog:finishedAt \"%s\"^^xsd:dateTime .\n"
PREX = PRE + "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
def stale(sa, f):
    dg = Graph(); dg.parse(TBOX, format="turtle"); dg.parse(data=PREX + SC % (sa, f), format="turtle")
    _, rg, _ = pyshacl.validate(dg, shacl_graph=RED, advanced=True, inference="none")
    return any("predates the most recent completion" in str(rg.value(r, SH.resultMessage)) for r in rg.subjects(RDF.type, SH.ValidationResult))
expect("a score made with no time zone and a completion with one: the completion after the score fires the stale-score rule", stale("2026-09-01T10:00:00", "2026-09-01T12:00:00Z"))
expect("a score made with no time zone and a later-in-the-day completion before it does not fire, and nothing stops", not stale("2026-09-01T10:00:00", "2026-09-01T08:00:00Z"))
expect("a score with a zone and a completion without one compare the same way", stale("2026-09-01T10:00:00Z", "2026-09-01T12:00:00") and not stale("2026-09-01T10:00:00Z", "2026-09-01T08:00:00"))
expect("two times in the same form still compare as before", stale("2026-09-01T10:00:00Z", "2026-09-01T12:00:00Z") and not stale("2026-09-01T12:00:00Z", "2026-09-01T10:00:00Z"))
print("VERDICT: %s -- %d expectations %s" % ("PASS" if not FAILS else "FAIL", N[0], "hold" if not FAILS else "(%d failed)" % len(FAILS)))
sys.exit(1 if FAILS else 0)
