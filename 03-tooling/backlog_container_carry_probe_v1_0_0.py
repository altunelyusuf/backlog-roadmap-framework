#!/usr/bin/env python3
"""backlog_container_carry_probe v1.0.0 (box 56, G242): ContainerStateRule (R1a-R1c) does not count a member that a sprint review closing that container flags for carry-over. Usage: probe [--shapes PATH].
Runs the rule itself, copied from the newest shapes file, with pyshacl advanced (rules, no inference) over the newest T-box and a small register per case, and reads the derivedState of the container. Cases: closed box with a Done member and a carried Proposed member derives Done; with a carried InProgress member derives Done; member not flagged still counts (InProgress);
no closing review: derived as before; a review that closes another box flags nothing here; all members carried derives nothing; a carried member of a box with only Proposed unflagged members derives Proposed."""
import os, re, sys, glob
from rdflib import Graph, Namespace, BNode
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
walk(BL["ContainerStateRule"])
PRE = ("@prefix backlog: <http://example.org/backlog#> . @prefix ex: <http://example.org/probe#> .\n"
       "ex:C a backlog:Iteration . ex:O a backlog:Iteration .\n")
def mem(n, st): return "ex:%s a backlog:Story ; backlog:memberOfContainer ex:C ; backlog:hasState backlog:%s .\n" % (n, st)
def rev(closes, flags): return "ex:R a backlog:SprintReviewCeremony ; backlog:closesIteration ex:%s %s .\n" % (closes, "".join("; backlog:flagsForCarryOver ex:%s " % f for f in flags))
def derived(ttl):
    from rdflib import URIRef
    dg = Graph(); dg.parse(TBOX, format="turtle"); dg.parse(data=PRE + ttl, format="turtle")
    pyshacl.validate(dg, shacl_graph=RED, advanced=True, inference="none", inplace=True)
    return sorted(str(o).split("#")[1] for o in dg.objects(URIRef("http://example.org/probe#C"), BL.derivedState))
FAILS = []; N = [0]
def expect(what, got, want):
    N[0] += 1
    if got != want: FAILS.append(what); print("FAIL ", what, "got", got, "want", want)
expect("closed box: Done member + carried Proposed member derives Done", derived(mem("A", "Done") + mem("B", "Proposed") + rev("C", ["B"])), ["Done"])
expect("closed box: Done member + carried InProgress member derives Done", derived(mem("A", "Done") + mem("B", "InProgress") + rev("C", ["B"])), ["Done"])
expect("a member the review does not flag still counts: InProgress", derived(mem("A", "Done") + mem("B", "Proposed") + mem("D", "Proposed") + rev("C", ["B"])), ["InProgress"])
expect("no closing review: Done + Proposed derives InProgress as before", derived(mem("A", "Done") + mem("B", "Proposed")), ["InProgress"])
expect("a review that closes another box carries nothing here", derived(mem("A", "Done") + mem("B", "Proposed") + rev("O", ["B"])), ["InProgress"])
expect("every member carried: nothing derived", derived(mem("B", "Proposed") + rev("C", ["B"])), [])
expect("unflagged Proposed members only, one other carried: Proposed", derived(mem("B", "Proposed") + mem("D", "Proposed") + mem("E", "Proposed") + rev("C", ["B"])), ["Proposed"])
expect("no review, all Done: Done as before", derived(mem("A", "Done") + mem("B", "Done")), ["Done"])
print("VERDICT: %s -- %d expectations %s" % ("PASS" if not FAILS else "FAIL", N[0], "hold" if not FAILS else "(%d failed)" % len(FAILS)))
sys.exit(1 if FAILS else 0)
