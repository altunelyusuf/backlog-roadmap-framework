#!/usr/bin/env python3
"""backlog_live_obstacle_probe v1.0.0 -- a blocked agent is shown raising an obstacle, taking a way and being unblocked in a box (G199; Lineage 29, story LiveProof).
It reads the newest real register and finds the obstacles of Lineage 29 raised in a box through the tool, with a time after the box began and a way the kind lists, cleared after they were raised;
for the one raised in box 7 (the link-control refusal of the new rule set) it also runs the check that refused, and shows it passes now: the work resumed.
Mutants (copies in memory) show each condition counts: no box, a way the kind does not list, a clearance before the raise, a kind taken away.
Exit 0 when every expectation holds."""
import glob, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
REG = latest("01-ontologies/backlog_abox_v*.ttl"); TBOX = latest("01-ontologies/backlog_tbox_v*.ttl"); LINK = latest("03-tooling/backlog_link_control_probe_v*.py")
if sys.argv[1:] == ["--deps"]:
    for p in (REG, TBOX, LINK): print(p)
    print(os.path.abspath(__file__)); sys.exit(0)
from rdflib import Graph, RDF, URIRef, Literal
B = "http://example.org/backlog#"; FW = "http://example.org/backlog-framework-register#"
U = lambda n: URIRef(B + n); local = lambda x: str(x).rsplit("#", 1)[-1]
g = Graph(); g.parse(REG, format="turtle"); g.parse(TBOX, format="turtle")
bad = []
def expect(n, ok):
    print(("PASS  " if ok else "FAIL  ") + n)
    if not ok: bad.append(n)
def good(g, imp):
    """the conditions of a shown obstacle: a kind, a box of its lineage, raised after the box began, cleared by a way the kind lists, after it was raised"""
    k = g.value(imp, U("hasImpedimentKind")); lin = g.value(imp, U("belongsToLineage")); m = g.value(imp, U("clearedBy"))
    r = g.value(imp, U("raisedAt")); c = g.value(imp, U("resolvedAt"))
    boxes = [b for b in g.objects(imp, U("impedes")) if (b, RDF.type, U("Iteration")) in g and (b, U("belongsToLineage"), lin) in g]
    if None in (k, m, r, c) or not boxes: return False
    if not any(g.value(b, U("iterationStart")) is not None and g.value(b, U("iterationStart")).toPython() <= r.toPython() for b in boxes): return False
    return (k, U("clearableBy"), m) in g and r.toPython() < c.toPython()
imps = [i for i in g.subjects(RDF.type, U("Impediment")) if (i, U("belongsToLineage"), URIRef(FW + "L_ImpedimentsKnown")) in g]
expect("Lineage 29 has recorded obstacles (%d)" % len(imps), len(imps) >= 2)
expect("each is shown raised in a box, cleared by a way its kind lists, after it was raised", all(good(g, i) for i in imps))
live = URIRef(FW + "Imp_IK_2")
expect("the obstacle of box 7 is in the register, in that box, a refusal by a rule, cleared by satisfying the obligation in the same step",
       (live, U("impedes"), URIRef(FW + "It_IK_7")) in g and g.value(live, U("hasImpedimentKind")) == U("Imp_RuleRefusal") and g.value(live, U("clearedBy")) == U("Mth_SatisfyInStep"))
st = str(g.value(live, U("hasImpedimentStatement")) or "")
expect("its statement names the check that is run below (the link-control probe)", "link-control probe" in st)
res = g.value(live, U("resolvedAt"))
later = [c for c in g.subjects(U("checkpointOfBox"), URIRef(FW + "It_IK_7")) if g.value(c, U("checkpointAt")) is not None and res is not None and g.value(c, U("checkpointAt")).toPython() > res.toPython()]
expect("work went on in the box after it was cleared (a later checkpoint of the box)", len(later) >= 1)
r = subprocess.run([sys.executable, "-I", LINK], capture_output=True, text=True, timeout=900)
expect("the check that refused (the link-control probe) passes now: the work resumed", r.returncode == 0 and "PASS -- every expectation holds" in r.stdout)
def mut(f):
    m = Graph(); m += g; f(m); return good(m, live)
expect("mutant: with no box the obstacle is not a shown one", not mut(lambda m: m.remove((live, U("impedes"), URIRef(FW + "It_IK_7")))))
expect("mutant: cleared by a way the kind does not list, it is not", not mut(lambda m: m.set((live, U("clearedBy"), U("Mth_BoundedRetry")))))
expect("mutant: cleared before it was raised, it is not", not mut(lambda m: m.set((live, U("resolvedAt"), m.value(live, U("raisedAt"))))))
expect("mutant: with no kind, it is not", not mut(lambda m: m.remove((live, U("hasImpedimentKind"), None))))
def mut2(f):
    m = Graph(); m += g; f(m)
    st = str(m.value(live, U("hasImpedimentStatement")) or ""); res = m.value(live, U("resolvedAt"))
    lat = [c for c in m.subjects(U("checkpointOfBox"), URIRef(FW + "It_IK_7")) if m.value(c, U("checkpointAt")).toPython() > res.toPython()]
    return "link-control probe" in st and len(lat) >= 1
expect("mutant: a statement about something else is not tied to the check", not mut2(lambda m: m.set((live, U("hasImpedimentStatement"), Literal("Something unrelated happened")))))
expect("mutant: with no later checkpoint nothing shows the work went on", not mut2(lambda m: [m.remove((c, None, None)) for c in list(m.subjects(U("checkpointOfBox"), URIRef(FW + "It_IK_7")))]))
print("VERDICT   :", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
