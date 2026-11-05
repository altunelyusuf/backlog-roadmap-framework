#!/usr/bin/env python3
"""Probe for backlog_pipeline_verify v1.15.0 (digest tables v4 and v5; G208 introduced elements).

Cases: (1) under v4 an ExecutionTask added after the Backlog stage closed leaves the Backlog digest unchanged;
(2) under v3 the same task moves it; (3) under v4 a Story added to the closed stage still moves it;
(4) under v4 a pre-lineage item admitted by the lineage's Backlog output is part of the digest and its removal moves it;
(5) a pre-lineage item NOT admitted by this lineage's output does not enter the digest;
(6) the v4 table holds no ExecutionTask and every other v3 type;
(7) under v5 a Specification, TestScenario, ModelArtifact or AcceptanceCriterion added after the close leaves the Backlog digest unchanged;
(8) under v4 the same Specification moves it;
(9) the v5 table is v4 without those four types and an added Story still moves it;
(10) under v5 an Enabler admitted by a ScopeChange leaves the Backlog digest unchanged; (11) an Enabler no ScopeChange admits moves it; (12) under v4 the admitted Enabler still moves it.
Cases 15 to 24 (G208): under v5 a goal, objective or deliverable an accepted scope change names leaves its closed stage digest unchanged (15, 19); one named by a change whose request is not accepted (16), or by no change (17), still moves it; under v4 a named goal still moves it (18); the Backlog digest follows too (22); a change of another lineage (23) or a named element of another kind (24) hides nothing; two mutants of the rule are caught (20, 21)."""
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
spec = importlib.util.spec_from_file_location("pv", os.path.join(HERE, "backlog_pipeline_verify_v1_15_0.py"))
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
t5 = pv._load_stage_types(tb, table="v5")
g, L = reg(); pv.STAGE_TYPES = t5; d5 = pv.state_digest(g, "Stage_Backlog", L, admitted=True)
pv.STAGE_TYPES = t4; d4b = pv.state_digest(g, "Stage_Backlog", L, admitted=True)
for i, c in enumerate(("Specification", "TestScenario", "ModelArtifact", "AcceptanceCriterion")):
    n = u("Obl%d" % i, X); g.add((n, RDF.type, u(c))); g.add((n, u("belongsToLineage"), L))
pv.STAGE_TYPES = t5; check("7 v5: obligation artifacts added after the close leave the Backlog digest", pv.state_digest(g, "Stage_Backlog", L, admitted=True) == d5)
pv.STAGE_TYPES = t4; check("8 v4: the same artifacts move it", pv.state_digest(g, "Stage_Backlog", L, admitted=True) != d4b)
S5 = u("Story5", X); g.add((S5, RDF.type, u("Story"))); g.add((S5, u("belongsToLineage"), L))
pv.STAGE_TYPES = t5; check("9 v5: the table is v4 without the four types, and an added story moves it", set(t5["Stage_Backlog"]) == set(t4["Stage_Backlog"]) - {"Specification", "TestScenario", "ModelArtifact", "AcceptanceCriterion"} and pv.state_digest(g, "Stage_Backlog", L, admitted=True) != d5)
g, L = reg(); pv.STAGE_TYPES = t5; d5 = pv.state_digest(g, "Stage_Backlog", L, admitted=True, change_managed=True)
E1 = u("Enab1", X); g.add((E1, RDF.type, u("Enabler"))); g.add((E1, u("belongsToLineage"), L))
SCg = u("SC1", X); g.add((SCg, RDF.type, u("ScopeChange"))); g.add((SCg, u("admitsItem"), E1))
check("10 v5: an enabler admitted by a scope change leaves the Backlog digest", pv.state_digest(g, "Stage_Backlog", L, admitted=True, change_managed=True) == d5)
E2 = u("Enab2", X); g.add((E2, RDF.type, u("Enabler"))); g.add((E2, u("belongsToLineage"), L))
check("11 v5: an enabler no scope change admits moves it", pv.state_digest(g, "Stage_Backlog", L, admitted=True, change_managed=True) != d5)
g, L = reg(); pv.STAGE_TYPES = t4; d4c = pv.state_digest(g, "Stage_Backlog", L, admitted=True)
E1 = u("Enab1", X); g.add((E1, RDF.type, u("Enabler"))); g.add((E1, u("belongsToLineage"), L)); g.add((u("SC1", X), u("admitsItem"), E1))
check("12 v4: the admitted enabler still moves it", pv.state_digest(g, "Stage_Backlog", L, admitted=True) != d4c)
g, L = reg(); pv.STAGE_TYPES = t5; d5u = pv.state_digest(g, "Stage_Backlog", L, admitted=True, change_managed=True)
E3 = u("Enab3", X); g.add((E3, RDF.type, u("Enabler"))); g.add((E3, u("belongsToLineage"), L)); g.add((u("Urg1", X), u("urgentItem"), E3))
check("13 v5: an item an urgent interruption names leaves the Backlog digest", pv.state_digest(g, "Stage_Backlog", L, admitted=True, change_managed=True) == d5u)
g, L = reg(); pv.STAGE_TYPES = t4; d4u = pv.state_digest(g, "Stage_Backlog", L, admitted=True)
E3 = u("Enab3", X); g.add((E3, RDF.type, u("Enabler"))); g.add((E3, u("belongsToLineage"), L)); g.add((u("Urg1", X), u("urgentItem"), E3))
check("14 v4: the urgent item still moves it", pv.state_digest(g, "Stage_Backlog", L, admitted=True) != d4u)

# ---- G208: elements an accepted scope change names (cases 15 to 21) ----
def named_reg(kind, stage, accepted=True, named=True, cr_state=None):
    g, L = reg(); pv.STAGE_TYPES = t5
    base = pv.state_digest(g, stage, L, admitted=True, change_managed=True)
    E = u("New1", X); g.add((E, RDF.type, u(kind))); g.add((E, u("belongsToLineage"), L))
    if named:
        SC = u("SCn", X); CR = u("CRn", X)
        g.add((SC, RDF.type, u("ScopeChange"))); g.add((SC, u("belongsToLineage"), L)); g.add((SC, u("introducesElement"), E)); g.add((SC, u("fulfillsRequest"), CR))
        if accepted: g.add((CR, u("hasDisposition"), u("Disp_Accepted")))
        else: g.add((CR, u("hasDisposition"), u("Disp_Pending")))
    return g, L, base
def stable(g, L, base, stage, cm=True, tbl=None):
    pv.STAGE_TYPES = tbl or t5
    return pv.state_digest(g, stage, L, admitted=True, change_managed=cm) == base
g, L, b = named_reg("Goal", "Stage_Goal"); check("15 v5: a goal an accepted scope change names leaves the Goal digest unchanged", stable(g, L, b, "Stage_Goal"))
g, L, b = named_reg("Goal", "Stage_Goal", accepted=False); check("16 v5: a goal named by a change whose request is not accepted moves it", not stable(g, L, b, "Stage_Goal"))
g, L, b = named_reg("Goal", "Stage_Goal", named=False); check("17 v5: a goal no change names moves it", not stable(g, L, b, "Stage_Goal"))
g, L, b = named_reg("Goal", "Stage_Goal"); pv.STAGE_TYPES = t4; d4g = pv.state_digest(reg()[0], "Stage_Goal", L, admitted=True)
check("18 v4: the named goal still moves it", pv.state_digest(g, "Stage_Goal", L, admitted=True) != d4g)
g, L, b = named_reg("Objective", "Stage_Objective"); ok_o = stable(g, L, b, "Stage_Objective")
g, L, b = named_reg("ScopeDeliverable", "Stage_Scope"); ok_d = stable(g, L, b, "Stage_Scope")
check("19 v5: a named objective and a named scope deliverable leave their stage digests unchanged", ok_o and ok_d)
orig = pv._named_by_accepted_change
pv._named_by_accepted_change = lambda g, s, l=None: any(True for _ in g.subjects(u("introducesElement"), s))
g, L, b = named_reg("Goal", "Stage_Goal", accepted=False); caught1 = stable(g, L, b, "Stage_Goal")
pv._named_by_accepted_change = lambda g, s, l=None: True
g, L, b = named_reg("Goal", "Stage_Goal", named=False); caught2 = stable(g, L, b, "Stage_Goal")
pv._named_by_accepted_change = orig
check("20 mutant: acceptance ignored -- case 16 would fail (the mutant leaves the digest unchanged)", caught1)
check("21 mutant: naming ignored -- case 17 would fail (the mutant leaves the digest unchanged)", caught2)
g, L, b = named_reg("Goal", "Stage_Backlog"); check("22 v5: a goal an accepted change names also leaves the cumulative Backlog digest unchanged", stable(g, L, b, "Stage_Backlog"))
g, L, b = named_reg("Goal", "Stage_Goal"); g.remove((u("SCn", X), u("belongsToLineage"), L)); g.add((u("SCn", X), u("belongsToLineage"), u("OtherL", X)))
check("23 v5: a change of another lineage hides nothing", not stable(g, L, b, "Stage_Goal"))
g, L, b = named_reg("Mission", "Stage_Mission"); g.add((u("New1", X), u("belongsToLineage"), L)); pv.STAGE_TYPES = t5
check("24 v5: a named element that is not a goal, objective or deliverable (a Mission) is not hidden", pv._named_by_accepted_change(g, u("New1", X), L) is False)
print("VERDICT: %s" % ("PASS" if not fails else "FAIL")); sys.exit(1 if fails else 0)
