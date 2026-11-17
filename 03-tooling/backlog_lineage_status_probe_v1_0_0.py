#!/usr/bin/env python3
"""backlog_lineage_status_probe v1.0.0 (box 55, G241): LineageStatusSingleShape -- the live pointer LS_Archived of a lineage marked lineageArchived true is the pointer, not a second status. Usage: probe [--shapes PATH].
Runs the shape itself, copied from the newest shapes file, with pyshacl as the validator runs it (advanced, no inference) over the newest T-box and a lineage planted per case; a case either makes the shape fire on the lineage or it does not.
Cases: LS_Archived plus the final outcome on an archived lineage conforms; two other statuses on an archived lineage, three statuses with LS_Archived among them, LS_Archived plus another on a lineage marked not archived or not marked at all, and two statuses on a live lineage fire; one status conforms."""
import os, re, sys, glob
from rdflib import Graph, Namespace, BNode
from rdflib.namespace import RDF
import pyshacl
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.join(HERE, "..")
SH = Namespace("http://www.w3.org/ns/shacl#"); BL = Namespace("http://example.org/backlog#")
def newest(folder, stem):
    fs = glob.glob(os.path.join(PKG, folder, stem + "_v*.ttl"))
    return sorted(fs, key=lambda f: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", f)[0]])[-1]
SHAPES_FILE = sys.argv[sys.argv.index("--shapes") + 1] if "--shapes" in sys.argv else newest("02-shacl-safeguards", "backlog_shacl")
SHAPES = Graph(); SHAPES.parse(SHAPES_FILE, format="turtle")
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
walk(BL["LineageStatusSingleShape"])
PRE = "@prefix backlog: <http://example.org/backlog#> . @prefix ex: <http://example.org/probe#> .\n"
def lin(statuses, arch):
    a = {"true": "; backlog:lineageArchived true", "false": "; backlog:lineageArchived false", None: ""}[arch]
    return "ex:L a backlog:Lineage %s ; backlog:hasLineageStatus %s .\n" % (a, " , ".join("backlog:" + s for s in statuses))
def fires(ttl):
    dg = Graph(); dg.parse(TBOX, format="turtle"); dg.parse(data=PRE + ttl, format="turtle")
    _, rg, _ = pyshacl.validate(dg, shacl_graph=RED, advanced=True, inference="none")
    return any(str(rg.value(r, SH.focusNode)).endswith("#L") for r in rg.subjects(RDF.type, SH.ValidationResult))
FAILS = []; N = [0]
def expect(what, ok):
    N[0] += 1
    if not ok: FAILS.append(what); print("FAIL ", what)
expect("an archived lineage holding LS_Archived and its final outcome conforms", not fires(lin(["LS_Archived", "LS_Achieved"], "true")))
expect("the same with another outcome (LS_Closed) conforms", not fires(lin(["LS_Archived", "LS_Closed"], "true")))
expect("an archived lineage with two statuses that are not LS_Archived fires", fires(lin(["LS_Achieved", "LS_Closed"], "true")))
expect("an archived lineage with LS_Archived and two others fires", fires(lin(["LS_Archived", "LS_Achieved", "LS_Closed"], "true")))
expect("LS_Archived plus another on a lineage marked not archived fires", fires(lin(["LS_Archived", "LS_Achieved"], "false")))
expect("LS_Archived plus another on a lineage with no archive mark fires", fires(lin(["LS_Archived", "LS_Achieved"], None)))
expect("two statuses on a live lineage fire", fires(lin(["LS_InProgress", "LS_Achieved"], "false")))
expect("one status conforms", not fires(lin(["LS_InProgress"], "false")))
expect("an archived lineage holding only LS_Archived conforms", not fires(lin(["LS_Archived"], "true")))
print("VERDICT: %s -- %d expectations %s" % ("PASS" if not FAILS else "FAIL", N[0], "hold" if not FAILS else "(%d failed)" % len(FAILS)))
sys.exit(1 if FAILS else 0)
