#!/usr/bin/env python3
"""backlog_plan_then_execute_probe v1.0.0 -- six checks against finding a defect after the fact (T-Box v1.138.0, shapes v1.176.0, G136).

Each check fires on a planted fault and is silent on its corrected twin:
  1 a closure caveat tracked by no work item and no change request (ClosureCaveatTrackedShape; a violation for the new class),
  2 a criterion that names its tool but not the version, and a criterion whose text cites a gate and names no tool (advisories),
  3 work planned into an iteration after it started with no rebaseline and no carry-over (the sprint goal is fixed at the start),
  4 a story with no parent and no 'stands alone' while the register holds an epic,
  5 an executor brief not derived from a criterion, naming no task or no executor instance; a started task with no brief,
  6 a task whose start is recorded before the start of the executor instance that was briefed.
Also: the new classes and properties are declared with domain and range.
Exit 0 when every expectation holds, 1 otherwise."""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
TB, SH = latest("01-ontologies/backlog_tbox_v*.ttl"), latest("02-shacl-safeguards/backlog_shacl_v*.ttl")
if sys.argv[1:] == ["--deps"]:
    print("\n".join([TB, SH, os.path.abspath(__file__)])); sys.exit(0)
from rdflib import Graph, Namespace, RDF, RDFS, OWL
from pyshacl import validate
B = Namespace("http://example.org/backlog#"); SHNS = Namespace("http://www.w3.org/ns/shacl#")
shapes = Graph(); shapes.parse(SH, format="turtle"); t = Graph(); t.parse(TB, format="turtle")
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix ex: <http://example.org/p#> .\n@prefix prov: <http://www.w3.org/ns/prov#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
bad = []
def expect(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (" (%s)" % detail if detail else ""))
    if not ok: bad.append(name)
def fired(text):
    g = Graph(); g.parse(data=HEAD + text, format="turtle")
    _, rg, _ = validate(g, shacl_graph=shapes, advanced=True, inference="none", abort_on_first=False)
    out = set()
    for r in rg.subjects(RDF.type, SHNS.ValidationResult):
        out.add(str(rg.value(r, SHNS.sourceShape)).split("#")[-1])
        if str(rg.value(r, SHNS.resultMessage) or "").startswith("G136: this closure caveat"): out.add("ClosureCaveatTrackedShape")
    return out & WANT
WANT = {"ClosureCaveatTrackedShape", "CriterionToolVersionShape", "CriterionCitesGateShape", "PlanningAfterIterationStartShape", "StoryEpicOrAloneShape", "BriefDerivedShape", "StartedWithoutBriefShape", "StartBeforeExecutorShape"}
def fault_and_twin(label, shape, fault, twin):
    f, w = fired(fault), fired(twin)
    expect("%s: the fault fires %s, the twin is silent" % (label, shape), shape in f and shape not in w, "fault %s; twin %s" % (sorted(f), sorted(w)))

fault_and_twin("1", "ClosureCaveatTrackedShape", "ex:C a backlog:ClosureCaveat .", "ex:C a backlog:ClosureCaveat ; backlog:caveatTrackedBy ex:W .\nex:W a backlog:Story .")
fault_and_twin("2a", "CriterionToolVersionShape", "ex:A a backlog:AcceptanceCriterion ; backlog:measuredWithTool ex:T .", "ex:A a backlog:AcceptanceCriterion ; backlog:measuredWithTool ex:T ; backlog:measuredWithVersion \"1.13.0\" .")
fault_and_twin("2b", "CriterionCitesGateShape", 'ex:A a backlog:AcceptanceCriterion ; backlog:hasGherkinText "Then the validator passes" .', 'ex:A a backlog:AcceptanceCriterion ; backlog:hasGherkinText "Then the validator passes" ; backlog:measuredWithTool ex:T ; backlog:measuredWithVersion "1.13.0" .')
IT = 'ex:I a backlog:Iteration ; backlog:iterationStart "2026-10-01T00:00:00"^^xsd:dateTime .\n'
fault_and_twin("3", "PlanningAfterIterationStartShape", IT + 'ex:P a backlog:PlanningEvent ; backlog:plannedInto ex:I ; backlog:plannedAt "2026-10-05T00:00:00"^^xsd:dateTime .',
               IT + 'ex:P a backlog:PlanningEvent ; backlog:plannedInto ex:I ; backlog:plannedAt "2026-10-05T00:00:00"^^xsd:dateTime .\nex:R a backlog:Rebaseline ; backlog:rebaselines ex:I ; backlog:rebaselinedAt "2026-10-04T00:00:00"^^xsd:dateTime .')
EP = 'ex:E a backlog:Epic .\n'
fault_and_twin("4", "StoryEpicOrAloneShape", EP + 'ex:S a backlog:Story .', EP + 'ex:S a backlog:Story ; backlog:standsAlone true .')
TASK = 'ex:T a backlog:ExecutionTask ; backlog:startedAt "2026-10-05T10:00:00"^^xsd:dateTime .\nex:CR a backlog:AcceptanceCriterion .\nex:X a backlog:ExecutorInstance ; backlog:instantiatedAt "2026-10-05T09:00:00"^^xsd:dateTime .\n'
GOOD = TASK + 'ex:B a backlog:ExecutorBrief ; backlog:briefFor ex:T ; backlog:briefedExecutorInstance ex:X ; backlog:briefCriterion ex:CR .'
fault_and_twin("5a", "BriefDerivedShape", TASK + 'ex:B a backlog:ExecutorBrief ; backlog:briefFor ex:T .', GOOD)
fault_and_twin("5b", "StartedWithoutBriefShape", TASK, GOOD)
fault_and_twin("6", "StartBeforeExecutorShape", TASK.replace("09:00:00", "11:00:00") + 'ex:B a backlog:ExecutorBrief ; backlog:briefFor ex:T ; backlog:briefedExecutorInstance ex:X ; backlog:briefCriterion ex:CR .', GOOD)
decl = {"ClosureCaveat": "c", "ExecutorBrief": "c", "closureCaveat": "p", "caveatTrackedBy": "p", "briefFor": "p", "briefedExecutorInstance": "p", "briefCriterion": "p", "measuredWithTool": "p", "measuredWithVersion": "p", "standsAlone": "p"}
ok = all(((B[n], RDF.type, OWL.Class) in t) if k == "c" else ((B[n], RDFS.domain, None) in t and (B[n], RDFS.range, None) in t) for n, k in decl.items())
expect("7 the new classes are declared and the new properties carry a domain and a range", ok)
print("VERDICT: %s" % ("PASS -- every expectation holds" if not bad else "FAIL -- " + "; ".join(bad)))
sys.exit(1 if bad else 0)
