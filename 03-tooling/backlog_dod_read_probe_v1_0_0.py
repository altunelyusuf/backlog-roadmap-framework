#!/usr/bin/env python3
"""backlog_dod_read_probe v1.0.0 -- Lineage 29, package 17, box 49 (G236; course-management handover of 2026-11-14, gap 4).

Runs ItemCompletenessLinkageShape itself, copied from the newest shapes file, with pyshacl as the box tool's guard runs it (advanced, NO inference) over the newest T-box and a small register planted with each case.
The Definition of Done is derived by a rule (effective Definition of Done: the item's own link, or one container's); without inference the constraint saw neither, and reported every task the box tool had written
with its own link as governed by none. Cases: an item with its own link, one whose container holds it, and one that carries the derived link all pass; an item with none anywhere is still reported."""
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
RED = Graph(); seen = set()
def walk(n):
    if n in seen: return
    seen.add(n)
    for p, o in SHAPES.predicate_objects(n):
        RED.add((n, p, o))
        if isinstance(o, BNode) or p in (SH.prefixes, SH.declare): walk(o)
walk(BL["ItemCompletenessLinkageShape"])
PRE = "@prefix backlog: <http://example.org/backlog#> . @prefix ex: <http://example.org/probe#> .\n"
TASK = "ex:T a backlog:ExecutionTask ; backlog:hasState backlog:InProgress %s .\n"
MSG = "no Definition of Done governs"
def reported(ttl):
    dg = Graph(); dg.parse(TBOX, format="turtle"); dg.parse(data=PRE + ttl, format="turtle")
    _, rg, _ = pyshacl.validate(dg, shacl_graph=RED, advanced=True, inference="none")
    return any(str(rg.value(r, SH.focusNode)).endswith("#T") and MSG in str(rg.value(r, SH.resultMessage)) for r in rg.subjects(RDF.type, SH.ValidationResult))
FAILS = []; N = [0]
def expect(what, ok):
    N[0] += 1
    if not ok: FAILS.append(what); print("FAIL ", what)
expect("a task that carries the Definition of Done the box tool writes is not reported", not reported(TASK % "; backlog:appliesDefinitionOfDone ex:D" + "ex:D a backlog:DoDCriterion .\n"))
expect("a task whose container holds the Definition of Done is not reported", not reported(TASK % "; backlog:memberOfContainer ex:C" + "ex:C a backlog:Iteration ; backlog:appliesDefinitionOfDone ex:D .\nex:D a backlog:DoDCriterion .\n"))
expect("a task that carries the derived link is not reported either", not reported(TASK % "; backlog:effectiveDefinitionOfDone ex:D" + "ex:D a backlog:DoDCriterion .\n"))
expect("a task with no Definition of Done anywhere is still reported", reported(TASK % ""))
expect("a task whose container holds none is still reported", reported(TASK % "; backlog:memberOfContainer ex:C" + "ex:C a backlog:Iteration .\n"))
expect("a task whose container's container holds one is reported: the derivation reads one container only", reported(TASK % "; backlog:memberOfContainer ex:C" + "ex:C a backlog:Iteration ; backlog:memberOfContainer ex:C2 .\nex:C2 a backlog:Iteration ; backlog:appliesDefinitionOfDone ex:D .\nex:D a backlog:DoDCriterion .\n"))
print("VERDICT: %s -- %d expectations %s" % ("PASS" if not FAILS else "FAIL", N[0], "hold" if not FAILS else "(%d failed)" % len(FAILS))); sys.exit(1 if FAILS else 0)
