#!/usr/bin/env python3
"""backlog_grantor_probe v1.0.0 -- every recorded grant of a reviewer's access, given by an agent, names the person that agent acted for (Lineage 29, story Grantor).
The Owner ruled on 2026-11-04 (option 2): an agent may be recorded as the giver of access when it acts for a named person, and the record names both.
Judged on the newest real register: each agsys:AccessGrant whose giver is an executor run (an agent) has that run prov:actedOnBehalfOf the owner and for nobody else; a grant given by the owner himself needs nothing more; a grant with no giver, or a giver that is not a run, is refused.
What it does not show: that the agent really acted for that person (the record states it, nothing verifies it, and a builder agent can so grant access to its own reviewer, as the Owner was told), or that the Agentic-Systems package's own shape agrees (it still refuses an agent as giver; that package will say when its files follow the ruling).
Mutants (copies in memory): the person removed, the person replaced by an agent, a new grant by a run with no person; controls: a grant given by a person, and a person named on a run that gave no grant.
Exit 0 when every expectation holds."""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
REG = sorted(glob.glob(os.path.join(PKG, "01-ontologies/backlog_abox_v*.ttl")), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(REG); print(sorted(glob.glob(os.path.join(PKG, "01-ontologies/archive/backlog_framework_archive_abox_v*.ttl")), key=sv)[-1]); print(os.path.abspath(__file__)); sys.exit(0)
from rdflib import Graph, URIRef, RDF
B = "http://example.org/backlog#"; AG = "http://example.org/agentic-systems#"; PV = "http://www.w3.org/ns/prov#"; FW = "http://example.org/backlog-framework-register#"
ARCH = sorted(glob.glob(os.path.join(PKG, "01-ontologies/archive/backlog_framework_archive_abox_v*.ttl")), key=sv)[-1]
g = Graph(); g.parse(REG, format="turtle"); g.parse(ARCH, format="turtle")
GRANT, BY, ACTS = URIRef(AG + "AccessGrant"), URIRef(AG + "grantedBy"), URIRef(PV + "actedOnBehalfOf")
RUN, HUMAN = URIRef(B + "ExecutorInstance"), URIRef(B + "Executor_IndividualHuman")
bad = []
def expect(n, ok):
    print(("PASS  " if ok else "FAIL  ") + n)
    if not ok: bad.append(n)
OWNER = URIRef(B + "Owner"); HOLDS = URIRef(B + "holdsRole")
def owner(g, x): return (x, RDF.type, HUMAN) in g and (x, HOLDS, OWNER) in g
def unnamed(g):
    """grants with no giver, or a giver that is neither the owner nor an agent that acts only for the owner"""
    out = []
    for gr in g.subjects(RDF.type, GRANT):
        givers = list(g.objects(gr, BY))
        if not givers: out.append(gr); continue
        for r in givers:
            if owner(g, r): continue
            acts = list(g.objects(r, ACTS))
            if not acts or not all(owner(g, p) for p in acts): out.append(gr)
    return out
grants = list(g.subjects(RDF.type, GRANT)); byrun = [gr for gr in grants if any((r, RDF.type, RUN) in g for r in g.objects(gr, BY))]
expect("the register holds grants given by agents (%d of %d)" % (len(byrun), len(grants)), len(byrun) >= 20)
expect("every one names the person its agent acted for (without: %d)" % len(unnamed(g)), not unnamed(g))
run = next(iter(g.objects(byrun[0], BY))); gr0 = byrun[0]
def mut(f):
    m = Graph(); m += g; f(m); return bool(unnamed(m))
expect("every grant has a giver", all(list(g.objects(x, BY)) for x in grants))
expect("mutant: the person removed is seen", mut(lambda m: m.remove((run, ACTS, None))))
expect("mutant: the person replaced by an agent is seen", mut(lambda m: (m.remove((run, ACTS, None)), m.add((run, ACTS, next(iter(g.objects(byrun[1], BY))))))))
def newgrant(m):
    r2, g2 = URIRef(FW + "Run_Planted"), URIRef(FW + "Grant_Planted")
    m.add((r2, RDF.type, RUN)); m.add((g2, RDF.type, GRANT)); m.add((g2, BY, r2))
expect("mutant: a new grant by a run with no person is seen", mut(newgrant))
def otherhuman(m):
    p2 = URIRef(FW + "Person_Other"); m.add((p2, RDF.type, HUMAN)); m.set((run, ACTS, p2))
expect("mutant: another human than the owner is seen", mut(otherhuman))
expect("mutant: a run that acts for the owner and also for an agent is seen", mut(lambda m: m.add((run, ACTS, next(iter(g.objects(byrun[1], BY)))))))
expect("mutant: a grant with no giver is seen", mut(lambda m: m.remove((gr0, BY, None))))
def untyped(m):
    r2, g2 = URIRef(FW + "Agent_Planted"), URIRef(FW + "Grant_PlantedU"); m.add((g2, RDF.type, GRANT)); m.add((g2, BY, r2))
expect("mutant: a giver that is an agent of no known kind is seen", mut(untyped))
def bypers(m):
    p2, g2 = URIRef(FW + "Person_Planted"), URIRef(FW + "Grant_PlantedP")
    m.add((p2, RDF.type, HUMAN)); m.add((p2, HOLDS, OWNER)); m.add((g2, RDF.type, GRANT)); m.add((g2, BY, p2))
expect("control: a grant given by the owner himself needs no more", not mut(bypers))
expect("control: a person named on a run that gave no grant changes nothing", not mut(lambda m: m.add((URIRef(FW + "Run_Idle"), RDF.type, RUN))))
print("VERDICT   :", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
