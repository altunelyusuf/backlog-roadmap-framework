#!/usr/bin/env python3
"""backlog_score_history_probe v1.0.0 -- Lineage 29, box 46 (G234; IPage handover of 2026-11-10, the stale-score rule).

Runs the stale-score constraint (L3 of ScoreAccountabilityShape) itself, copied from the newest shapes file, with pyshacl exactly as the validator runs it (advanced, no inference),
over the newest T-box and a small register planted with each case. Nothing is re-derived here: a case either makes the constraint fire for a score or it does not.
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
RED = Graph(); seen = set()


def walk(n):
    if n in seen:
        return
    seen.add(n)
    for p, o in SHAPES.predicate_objects(n):
        RED.add((n, p, o))
        if isinstance(o, BNode) or (isinstance(o, URIRef) and (o, RDF.type, None) in SHAPES and p in (SH.sparql, SH.prefixes, SH.declare)):
            walk(o)


walk(BL["ScoreAccountabilityShape"])
PRE = ("@prefix backlog: <http://example.org/backlog#> . @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> . @prefix ex: <http://example.org/probe#> . "
       "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n")
DONE = 'ex:D a backlog:Story ; backlog:hasState backlog:Done ; backlog:finishedAt "2026-09-02T12:00:00Z"^^xsd:dateTime .\n'
OLD, NEW = "2026-09-01T10:00:00Z", "2026-09-03T10:00:00Z"


def score(name, at, extra=""):
    return 'ex:%s a backlog:RICEScore ; backlog:scoredAt "%s"^^xsd:dateTime %s .\n' % (name, at, extra)


def item(name, cls, state, sc, extra=""):
    return "ex:%s a backlog:%s ; backlog:hasState backlog:%s ; backlog:hasPriorityScore ex:%s %s .\n" % (name, cls, state, sc, extra)


def stale(ttl):
    dg = Graph(); dg.parse(TBOX, format="turtle"); dg.parse(data=PRE + DONE + ttl, format="turtle")
    _, rg, _ = pyshacl.validate(dg, shacl_graph=RED, advanced=True, inference="none")
    return {str(rg.value(r, SH.focusNode)).split("#")[-1] for r in rg.subjects(RDF.type, SH.ValidationResult) if "predates the most recent completion" in str(rg.value(r, SH.resultMessage))}


FAILS = []; N = [0]


def expect(what, ok):
    N[0] += 1
    if not ok:
        FAILS.append(what); print("FAIL ", what)


expect("a live score of an open item older than a completion fires", stale(item("S", "Story", "Proposed", "A") + score("A", OLD)) == {"A"})
expect("a live score newer than every completion does not fire", stale(item("S", "Story", "Proposed", "A") + score("A", NEW)) == set())
r = stale(item("E", "Epic", "Proposed", "B , ex:A", "; backlog:decomposesInto ex:S") + score("A", OLD) + score("B", NEW, "; backlog:replacesScore ex:A") + item("S", "Story", "Proposed", "C") + score("C", NEW))
expect("an estimate that a later score replaces is history and does not fire, nor does the newer score", r == set())
r = stale(item("S", "Story", "Proposed", "B , ex:A") + score("A", OLD) + score("B", NEW, "; backlog:replacesScore ex:A"))
expect("the replaced score of a story does not fire either", r == set())
r = stale(item("S", "Story", "Proposed", "B , ex:A") + score("A", OLD) + score("B", OLD, "; backlog:replacesScore ex:A"))
expect("a score that replaces another is itself judged, when it is older than a completion", r == {"B"})
r = stale(item("S", "Story", "Proposed", "A , ex:Y") + score("A", OLD) + score("X", NEW, "; backlog:replacesScore ex:Y") + score("Y", OLD))
expect("a replaced score is left out while the live score beside it on the item is still judged", r == {"A"})
EPIC = item("E", "Epic", "Proposed", "A", "; backlog:decomposesInto ex:S1 , ex:S2") + score("A", OLD)
expect("an epic whose stories are all Done or Cancelled is left out", stale(EPIC + item("S1", "Story", "Done", "A1") + score("A1", NEW) + item("S2", "Story", "Cancelled", "A2") + score("A2", NEW)) == set())
expect("an epic with one open story is still judged", stale(EPIC + item("S1", "Story", "Done", "A1") + score("A1", NEW) + item("S2", "Story", "Proposed", "A2") + score("A2", NEW)) == {"A"})
expect("an epic with no story at all is still judged", stale(item("E", "Epic", "Proposed", "A") + score("A", OLD)) == {"A"})
r = stale(item("E", "Epic", "Proposed", "A", "; backlog:decomposesInto ex:F") + score("A", OLD) + "ex:F a backlog:Feature ; backlog:hasState backlog:Proposed ; backlog:decomposesInto ex:S1 .\n" + item("S1", "Story", "Done", "A1") + score("A1", NEW))
expect("an epic reaching its stories through a feature is read through the whole chain", r == set())
r = stale(item("E", "Epic", "Proposed", "A", "; backlog:decomposesInto ex:F") + score("A", OLD) + "ex:F a backlog:Feature ; backlog:hasState backlog:Proposed ; backlog:decomposesInto ex:S1 , ex:S2 .\n" + item("S1", "Story", "Done", "A1") + score("A1", NEW) + item("S2", "Story", "Proposed", "A2") + score("A2", NEW))
expect("an epic with an open story two levels down is still judged", r == {"A"})
r = stale(item("S", "Story", "Proposed", "A", "; backlog:decomposesInto ex:S1") + score("A", OLD) + item("S1", "Story", "Done", "A1") + score("A1", NEW))
expect("the exclusion belongs to epics: a story is judged whatever it decomposes into", r == {"A"})
r = stale(EPIC + item("S1", "Story", "Done", "A1") + score("A1", NEW) + item("S2", "Story", "Done", "A2") + score("A2", OLD))
expect("a finished epic is left out while an open story's own old score would be judged", r == set())
r = stale(item("S", "Story", "Proposed", "A") + score("A", "2026-09-01T10:00:00") )
expect("the reading of a time without a zone as UTC still holds", r == {"A"})
r = stale(item("S", "Story", "Done", "A") + score("A", OLD))
expect("an item that is Done is not judged, as before", r == set())
print("%d expectations, %d failed" % (N[0], len(FAILS)))
sys.exit(1 if FAILS else 0)
