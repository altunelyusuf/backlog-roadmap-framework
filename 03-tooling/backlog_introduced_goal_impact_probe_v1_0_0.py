#!/usr/bin/env python3
"""backlog_introduced_goal_impact_probe v1.0.0 -- the two shapes of G208 do what they say (Lineage 29, story: a scope change names what it introduces).

Reads the newest shapes file and the newest negative fixture, keeps only the fixture's G208 cases and checks, with pyshacl:
(1) a scope change that introduces a goal, whose impact analysis is silent on other goals, fires the Named shape (IGI_NAMED_BAD);
(2) one whose analysis names an affected goal and no work item fires the Answered shape (IGI_ANSWER_BAD);
(3) an analysis that names an affected goal and the work that answers it fires neither (IGI_GOOD);
(4) an analysis that says no other goal is affected fires neither (IGI_NONE).
Mutants of the shapes, made on a copy in memory: (M1) the Named shape no longer reads "findsNoOtherGoalAffected" -- caught by case 4; (M2) the Answered shape no longer requires
the missing work item -- caught by case 3; (M3) the Named shape no longer requires the goal to be a goal -- not equivalent: caught by a change that introduces an objective (case 5, which must not fire)."""
import glob, os, re, sys
from rdflib import Graph, Namespace, RDF, URIRef
import pyshacl
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda q: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", q)[0]]
if sys.argv[1:] == ["--deps"]:
    for pat in ("02-shacl-safeguards/backlog_shacl_v*.ttl", "03-tooling/fixtures/fixture_negative_v*.ttl"):
        print(sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1])
    print(os.path.abspath(__file__)); sys.exit(0)
shapes_path = sorted(glob.glob(os.path.join(PKG, "02-shacl-safeguards", "backlog_shacl_v*.ttl")), key=sv)[-1]
fx_path = sorted(glob.glob(os.path.join(PKG, "03-tooling", "fixtures", "fixture_negative_v*.ttl")), key=sv)[-1]
FX = "http://example.org/fixture-negative#"; B = "http://example.org/backlog#"
fx = Graph(); fx.parse(fx_path)
data = Graph()
for s, p, o in fx:
    if str(s).startswith(FX + "IGI_"):
        data.add((s, p, o))
obj_sc = URIRef(FX + "IGI_OBJ"); obj = URIRef(FX + "IGI_O1"); cr5 = URIRef(FX + "IGI_CR5"); ia5 = URIRef(FX + "IGI_IA5")
data.add((obj, RDF.type, URIRef(B + "Objective"))); data.add((cr5, RDF.type, URIRef(B + "ChangeRequest"))); data.add((ia5, RDF.type, URIRef(B + "ImpactAssessment")))
data.add((ia5, URIRef(B + "analyzesRequest"), cr5)); data.add((obj_sc, RDF.type, URIRef(B + "ScopeChange")))
data.add((obj_sc, URIRef(B + "fulfillsRequest"), cr5)); data.add((obj_sc, URIRef(B + "introducesElement"), obj))
text = open(shapes_path, encoding="utf-8").read()
def fired(shapes_text):
    sg = Graph(); sg.parse(data=shapes_text, format="turtle")
    ok, rg, _ = pyshacl.validate(data, shacl_graph=sg, inference="none", advanced=True)
    SH = Namespace("http://www.w3.org/ns/shacl#"); out = {}
    for r in rg.subjects(RDF.type, SH.ValidationResult):
        f = str(rg.value(r, SH.focusNode)).split("#")[-1]; sh = str(rg.value(r, SH.sourceShape)); out.setdefault(f, set()).add(sh.split("#")[-1])
    return out
fails = 0
def check(name, ok):
    global fails
    print(("PASS " if ok else "FAIL ") + name); fails += 0 if ok else 1
N, A = "IntroducedGoalImpactNamedShape", "IntroducedGoalImpactAnsweredShape"
base = fired(text)
# the source shape of a SPARQL constraint is the node shape; filter by its name
fires = lambda d, f, shape: any(shape in s for s in d.get(f, set()))
check("1 a silent analysis fires the Named shape", fires(base, "IGI_NAMED_BAD", N))
check("2 an analysis with an affected goal and no work fires the Answered shape", fires(base, "IGI_ANSWER_BAD", A))
check("3 an analysis with the affected goal and the work that answers it fires neither", not fires(base, "IGI_GOOD", N) and not fires(base, "IGI_GOOD", A))
check("4 an analysis that says no other goal is affected fires neither", not fires(base, "IGI_NONE", N) and not fires(base, "IGI_NONE", A))
check("5 a change that introduces an objective fires neither (the rule is about goals)", not fires(base, "IGI_OBJ", N) and not fires(base, "IGI_OBJ", A))
m1 = text.replace("FILTER NOT EXISTS { ?ia2 backlog:analyzesRequest ?cr ; backlog:findsNoOtherGoalAffected true }", "")
check("6 mutant M1 (the 'no other goal affected' statement ignored) is caught by case 4", fires(fired(m1), "IGI_NONE", N))
m2 = text.replace("FILTER NOT EXISTS { ?ia backlog:callsForItem ?w }", "")
check("7 mutant M2 (the work item no longer required) is caught by case 3", fires(fired(m2), "IGI_GOOD", A))
m3 = text.replace("$this backlog:introducesElement ?g . ?g a backlog:Goal . $this backlog:fulfillsRequest ?cr .\n            FILTER NOT EXISTS { ?ia backlog:analyzesRequest ?cr ; backlog:affectsGoal ?x }", "$this backlog:introducesElement ?g . $this backlog:fulfillsRequest ?cr .\n            FILTER NOT EXISTS { ?ia backlog:analyzesRequest ?cr ; backlog:affectsGoal ?x }")
check("8 mutant M3 (any introduced element counts, not only a goal) is caught by case 5", m3 != text and fires(fired(m3), "IGI_OBJ", N))
print("VERDICT: %s" % ("PASS" if not fails else "FAIL")); sys.exit(1 if fails else 0)
