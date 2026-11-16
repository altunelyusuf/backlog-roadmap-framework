#!/usr/bin/env python3
"""backlog_done_running_probe v1.0.0 -- Lineage 29, box 51 (G237; risk 2 of the 2SISA handover of 2026-11-10, Done under a Definition of Done with no running criterion).

Runs DoneNeedsRunningCriterionShape itself, copied from the newest shapes file, with pyshacl exactly as the validator runs it (advanced, no inference) over the newest T-box and a small
register planted with each case. Nothing is re-derived here: a case either makes the shape fire or it does not. Cases: a Done item whose Definition of Done has only criteria that report not yet enforceable, or has none, fires; one criterion that holds, or that is violated, lets it conform;
the Definitions read from the item, from a container the item belongs to or as derived on the item counts the same; an item that is not Done is not touched; a Done item with no Definition at all is
left to the other rule; an item under two Definitions fires only when neither runs anything.
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


walk(BL["DoneNeedsRunningCriterionShape"])
PRE = ("@prefix backlog: <http://example.org/backlog#> . @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> . "
       "@prefix ex: <http://example.org/probe#> .\n")
ITEM = "ex:I a backlog:Story ; backlog:hasState backlog:%s %s .\n"
DEF = "ex:D a backlog:DefinitionOfDone %s .\n"
CRIT = 'ex:%s a backlog:DoDCriterion ; backlog:hasCheckQuery "q" ; backlog:hasExpectedResult "r" ; backlog:hasCriterionStatus backlog:%s .\n'
HAS = "; backlog:hasDoDCriterion %s"
APPLIES = "; backlog:appliesDefinitionOfDone ex:D"


def fires(ttl):
    dg = Graph(); dg.parse(TBOX, format="turtle"); dg.parse(data=PRE + ttl, format="turtle")
    _, rg, _ = pyshacl.validate(dg, shacl_graph=RED, advanced=True, inference="none")
    return any(str(rg.value(r, SH.focusNode)).endswith("#I") for r in rg.subjects(RDF.type, SH.ValidationResult))


FAILS = []
N = [0]


def expect(what, ok):
    N[0] += 1
    if not ok:
        FAILS.append(what); print("FAIL ", what)


def done(extra, defs, state="Done"):
    return ITEM % (state, extra) + defs


NYE = CRIT % ("A", "NotYetEnforceable")
expect("a Done item whose only criterion is not yet enforceable is refused", fires(done(APPLIES, DEF % (HAS % "ex:A") + NYE)))
expect("a Done item whose criteria are all not yet enforceable is refused", fires(done(APPLIES, DEF % (HAS % "ex:A , ex:B") + NYE + CRIT % ("B", "NotYetEnforceable"))))
expect("a Done item under a Definition with no criterion is refused", fires(done(APPLIES, DEF % "")))
expect("one criterion that holds lets a Done item conform", not fires(done(APPLIES, DEF % (HAS % "ex:A , ex:B") + NYE + CRIT % ("B", "Holds"))))
expect("a criterion that is violated is a running criterion", not fires(done(APPLIES, DEF % (HAS % "ex:A") + CRIT % ("A", "Violated"))))
expect("an item that is not Done is not touched, whatever its Definition holds", not fires(done(APPLIES, DEF % (HAS % "ex:A") + NYE, "InProgress")))
expect("a Definition named by a container the item belongs to counts: refused when nothing runs", fires(done("; backlog:memberOfContainer ex:C", "ex:C backlog:appliesDefinitionOfDone ex:D .\n" + DEF % (HAS % "ex:A") + NYE)))
expect("a Definition named by a container counts: accepted when a criterion runs", not fires(done("; backlog:memberOfContainer ex:C", "ex:C backlog:appliesDefinitionOfDone ex:D .\n" + DEF % (HAS % "ex:A") + CRIT % ("A", "Holds"))))
expect("the Definition derived on the item counts: refused when nothing runs", fires(done("; backlog:effectiveDefinitionOfDone ex:D", DEF % (HAS % "ex:A") + NYE)))
expect("the Definition derived on the item counts: accepted when a criterion runs", not fires(done("; backlog:effectiveDefinitionOfDone ex:D", DEF % (HAS % "ex:A") + CRIT % ("A", "Holds"))))
expect("a Done item with no Definition at all is left to the rule that asks for one", not fires(done("", "")))
TWO = "ex:C backlog:appliesDefinitionOfDone ex:D2 .\n" + DEF % (HAS % "ex:A") + "ex:D2 a backlog:DefinitionOfDone ; backlog:hasDoDCriterion ex:B .\n" + CRIT % ("B", "NotYetEnforceable")
expect("a Done item under two Definitions is accepted when one of them has a running criterion", not fires(done(APPLIES + "; backlog:memberOfContainer ex:C", TWO + CRIT % ("A", "Holds"))))
expect("a Done item under two Definitions is refused when neither has a running criterion", fires(done(APPLIES + "; backlog:memberOfContainer ex:C", TWO + CRIT % ("A", "NotYetEnforceable"))))
print("VERDICT: %s -- %d expectations %s" % ("PASS" if not FAILS else "FAIL", N[0], "hold" if not FAILS else "(%d failed)" % len(FAILS)))
sys.exit(1 if FAILS else 0)
