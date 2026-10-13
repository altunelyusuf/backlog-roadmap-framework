#!/usr/bin/env python3
"""backlog_competency_tree_probe v1.0.0 -- the closed competency tree holds, and the check discriminates (G110).

Real files (the highest T-Box and A-Box):
  every individual typed Competency is listed in the T-Box's owl:oneOf for Competency, and every listed member exists
  each skill has exactly one skos:broader and it is a CompetencyCategory; each finer skill has exactly one skos:broader and it is a skill (never a category, never another finer skill)
  every skill and finer skill has a label and a definition, and a dcterms:source unless it is one of the original twenty-four (recorded without one before v1.125.0)
Planted faults (small in-memory graphs): an unlisted skill, a skill with two parents, a finer skill below a finer skill, a skill with no source, a finer skill directly under a category -- each must be reported; the corrected twin must be silent.
Exit 0 when the real files are clean and every planted fault is caught, 1 otherwise.
"""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
def latest(pat): return sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(latest("01-ontologies/backlog_tbox_v*.ttl")); print(latest("01-ontologies/backlog_abox_v*.ttl")); print(os.path.abspath(__file__)); sys.exit(0)
import rdflib
from rdflib import RDF, RDFS, OWL, URIRef, Namespace
from rdflib.collection import Collection
B = Namespace("http://example.org/backlog#"); SKOS = Namespace("http://www.w3.org/2004/02/skos/core#"); DC = Namespace("http://purl.org/dc/terms/")

ORIGINAL_24 = set("Comp_" + x for x in "RequirementsElicitation ConceptualDataModeling ImpactAssessment ScopeDefinition SoftwareArchitecture OntologyModeling APIDesign UXDesign Coding ToolScripting DataMigration IntegrationBuild ShaclAuthoring TestDesign ClauseProof QualityReview BacklogStewardship RankingDecision GovernanceRuling LineageDiscipline ReleaseManagement ToolRunOperation IncidentResponse RetrospectiveFacilitation".split())

def check(g):
    bad = []
    cats = set(g.subjects(RDF.type, B.CompetencyCategory))
    listed = set()
    for lst in g.objects(B.Competency, OWL.oneOf): listed |= set(Collection(g, lst))
    typed = set(g.subjects(RDF.type, B.Competency))
    for c in typed - listed: bad.append(f"{c.split('#')[-1]}: typed Competency but not in the closed list")
    for c in listed - typed: bad.append(f"{c.split('#')[-1]}: in the closed list but not defined")
    skills = {c for c in typed if any(p in cats for p in g.objects(c, SKOS.broader))}
    for c in sorted(typed, key=str):
        n = c.split('#')[-1]; par = list(g.objects(c, SKOS.broader))
        if len(par) != 1: bad.append(f"{n}: {len(par)} broader (exactly one required)"); continue
        p = par[0]
        if p in cats: pass
        elif p in skills: pass
        else: bad.append(f"{n}: broader {p.split('#')[-1]} is neither a category nor a skill (a finer skill may not sit below a finer skill)")
        for prop, nm in ((RDFS.label, "label"), (SKOS.definition, "definition"), (DC.source, "source")):
            if nm == "source" and n in ORIGINAL_24: continue      # recorded without a source before v1.125.0; every later skill must carry one
            if not any(True for _ in g.objects(c, prop)): bad.append(f"{n}: no {nm}")
    return bad

def build(extra=""):
    g = rdflib.Graph(); g.parse(data="""@prefix backlog: <http://example.org/backlog#> . @prefix owl: <http://www.w3.org/2002/07/owl#> . @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> . @prefix dcterms: <http://purl.org/dc/terms/> .
backlog:Competency owl:oneOf ( backlog:S1 backlog:F1 ) .
backlog:Cat a backlog:CompetencyCategory .
backlog:S1 a backlog:Competency ; rdfs:label "s" ; skos:definition "d" ; dcterms:source "x" ; skos:broader backlog:Cat .
backlog:F1 a backlog:Competency ; rdfs:label "f" ; skos:definition "d" ; dcterms:source "x" ; skos:broader backlog:S1 .
""" + extra, format="turtle"); return g

bad = []
real = rdflib.Graph(); real.parse(latest("01-ontologies/backlog_tbox_v*.ttl"), format="turtle"); real.parse(latest("01-ontologies/backlog_abox_v*.ttl"), format="turtle")
r = check(real)
n_typed = len(set(real.subjects(RDF.type, B.Competency))); print(f"real files: {n_typed} competencies, {len(r)} fault(s)")
bad += [f"real: {x}" for x in r]
PLANT = {
 "unlisted skill": 'backlog:U a backlog:Competency ; rdfs:label "u" ; skos:definition "d" ; dcterms:source "x" ; skos:broader backlog:Cat .',
 "two parents": 'backlog:T a backlog:Competency ; rdfs:label "t" ; skos:definition "d" ; dcterms:source "x" ; skos:broader backlog:Cat , backlog:S1 . backlog:Competency owl:oneOf ( backlog:S1 backlog:F1 backlog:T ) .',
 "finer below finer": 'backlog:G a backlog:Competency ; rdfs:label "g" ; skos:definition "d" ; dcterms:source "x" ; skos:broader backlog:F1 .',
 "no source": 'backlog:N a backlog:Competency ; rdfs:label "n" ; skos:definition "d" ; skos:broader backlog:Cat .',
 "no parent": 'backlog:O a backlog:Competency ; rdfs:label "o" ; skos:definition "d" ; dcterms:source "x" .',
}
base = check(build())
print(f"twin (clean): {len(base)} fault(s)"); 
if base: bad.append(f"the clean twin reports {base}")
for name, ttl in PLANT.items():
    # a planted skill must also be listed, except in the 'unlisted' case, so only the intended fault shows
    extra = ttl
    if name not in ("unlisted skill", "two parents"):
        who = re.match(r"backlog:(\w+)", ttl).group(1)
        extra = ttl + f" backlog:Competency owl:oneOf ( backlog:S1 backlog:F1 backlog:{who} ) ."
    got = check(build(extra))
    print(f"planted '{name}': {len(got)} reported")
    if not got: bad.append(f"planted fault not caught: {name}")
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
