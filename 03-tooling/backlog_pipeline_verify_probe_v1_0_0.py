#!/usr/bin/env python3
"""Probe for backlog_pipeline_verify v1.9.0 (digest table v4).

Cases: (1) under v4 an ExecutionTask added after the Backlog stage closed leaves the Backlog digest unchanged;
(2) under v3 the same task moves it; (3) under v4 a Story added to the closed stage still moves it;
(4) under v4 a pre-lineage item admitted by the lineage's Backlog output is part of the digest and its removal moves it;
(5) a pre-lineage item NOT admitted by this lineage's output does not enter the digest;
(6) the v4 table holds no ExecutionTask and every other v3 type."""
import glob, importlib.util, os, sys
from rdflib import Graph, RDF, URIRef
if sys.argv[1:] == ["--deps"]:
    _h = os.path.dirname(os.path.abspath(__file__)); _p = os.path.dirname(_h)
    _sv = lambda q: [int(x) for x in __import__("re").findall(r"_v(\d+)_(\d+)_(\d+)\.", q)[0]]
    for pat in ("03-tooling/backlog_pipeline_verify_v*.py", "01-ontologies/backlog_tbox_v*.ttl", "01-ontologies/backlog_abox_v*.ttl"):
        print(sorted(glob.glob(os.path.join(_p, pat)), key=_sv)[-1])
    print(os.path.abspath(__file__)); sys.exit(0)
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
B = "http://example.org/backlog#"; X = "http://example.org/x#"
spec = importlib.util.spec_from_file_location("pv", os.path.join(HERE, "backlog_pipeline_verify_v1_9_0.py"))
pv = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
tb = sorted(glob.glob(os.path.join(PKG, "01-ontologies", "backlog_tbox_v*.ttl")))[-1]
def u(n, ns=B): return URIRef(ns + n)
def reg():
    g = Graph(); L = u("L", X); g.add((L, RDF.type, u("Lineage")))
    for n, t in (("Story1", "Story"), ("Epic1", "Epic")):
        g.add((u(n, X), RDF.type, u(t))); g.add((u(n, X), u("belongsToLineage"), L))
    return g, L
fails = 0
def check(name, ok):
    global fails
    print(("PASS " if ok else "FAIL ") + name); fails += 0 if ok else 1
t3 = pv._load_stage_types(tb, table="v3"); t4 = pv._load_stage_types(tb, table="v4")
g, L = reg()
pv.STAGE_TYPES = t4; d4 = pv.state_digest(g, "Stage_Backlog", L, admitted=True)
pv.STAGE_TYPES = t3; d3 = pv.state_digest(g, "Stage_Backlog", L)
T = u("Task1", X); g.add((T, RDF.type, u("ExecutionTask"))); g.add((T, u("belongsToLineage"), L))
pv.STAGE_TYPES = t4; check("1 v4: a task added after the close leaves the Backlog digest", pv.state_digest(g, "Stage_Backlog", L, admitted=True) == d4)
pv.STAGE_TYPES = t3; check("2 v3: the same task moves it", pv.state_digest(g, "Stage_Backlog", L) != d3)
S = u("Story2", X); g.add((S, RDF.type, u("Story"))); g.add((S, u("belongsToLineage"), L))
pv.STAGE_TYPES = t4; check("3 v4: a story added to the closed stage moves it", pv.state_digest(g, "Stage_Backlog", L, admitted=True) != d4)
g, L = reg(); O = u("Out", X); g.add((O, RDF.type, u("StageOutput"))); g.add((O, u("belongsToLineage"), L))
P = u("Pre", X); g.add((P, RDF.type, u("Story"))); g.add((P, u("belongsToLineage"), u("Other", X))); g.add((P, u("admittedByOutput"), O))
pv.STAGE_TYPES = t4; da = pv.state_digest(g, "Stage_Backlog", L, admitted=True)
g.remove((P, u("admittedByOutput"), O)); g.add((P, u("admittedByOutput"), u("ElsewhereOut", X)))
check("4 v4: an item the lineage's output admitted is in the digest", da != pv.state_digest(g, "Stage_Backlog", L, admitted=True))
check("5 v4: an item admitted by another lineage's output is not", pv.state_digest(g, "Stage_Backlog", L, admitted=True) == pv.state_digest(reg()[0], "Stage_Backlog", L, admitted=True))
b3, b4 = set(t3["Stage_Backlog"]), set(t4["Stage_Backlog"])
check("6 the v4 table is v3 without ExecutionTask", b4 == b3 - {"ExecutionTask"})
print("VERDICT: %s" % ("PASS" if not fails else "FAIL")); sys.exit(1 if fails else 0)
