#!/usr/bin/env python3
"""backlog_boxes_judged_probe v1.0.0 -- every closed box of Lineage 22 was recorded in order by the step tool and the register is clean (Lineage 22, box 3, D4).

  judge(graph, n) lists what is wrong with box n as the step tool records a box: it is Done with a start, an end and an observed duration; a planning ceremony and a planning event
  for each story precede the start; a checkpoint lies between the start and the end; a review closes the box and its stories after the last checkpoint; a retrospective follows the review
  and produces findings with a root cause and a remedy; every story of the box is Done with evidence; a deployment unit is Done. The probe judges each closed box of the shipped register
  (no fault), then plants a fault in a copy (a checkpoint removed, the review removed, a finding without a remedy, a story not Done, a planning event after the start) and requires the
  judgement to name it, and requires the validator to find no violation in the register. Exit 0 when every expectation holds."""
import glob, os, re, subprocess, sys, copy
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
AB, VAL = latest("01-ontologies/backlog_abox_v*.ttl"), latest("03-tooling/backlog_validate_v*.py")
if sys.argv[1:] == ["--deps"]:
    print("\n".join([AB, VAL, latest("02-shacl-safeguards/backlog_shacl_v*.ttl"), latest("01-ontologies/backlog_tbox_v*.ttl"), os.path.abspath(__file__)])); sys.exit(0)
from rdflib import Graph, Namespace, URIRef, RDF
B = Namespace("http://example.org/backlog#"); FW = Namespace(re.search(r"@prefix fw: <([^>]+)>", open(AB, encoding="utf-8").read()).group(1))
bad = []
def expect(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (" (%s)" % detail if detail else ""))
    if not ok: bad.append(name)
def t(g, s, p):
    v = g.value(s, p); return v.toPython() if v is not None else None
def judge(g, n, P="AP2"):
    """What is wrong with box n of the lineage whose prefix is P; empty when the box is recorded as the step tool records it."""
    out = []
    it = FW["It_%s_%d" % (P, n)]
    if (it, RDF.type, B.Iteration) not in g: return ["no such box"]
    s, e = t(g, it, B.iterationStart), t(g, it, B.iterationEnd)
    if g.value(it, B.hasState) != B.Done: out.append("the box is not Done")
    if s is None or e is None or e <= s: out.append("the box has no start before its end")
    if g.value(it, B.hasObservedDuration) is None: out.append("the box has no observed duration")
    pl = FW["Ceremony_%s_Planning%d" % (P, n)]
    ph = t(g, pl, B.heldAt)
    if ph is None: out.append("no planning ceremony was held for the box")
    events = list(g.objects(pl, B.includesPlanningEvent))
    if not events: out.append("the planning ceremony has no planning event")
    for ev in events:
        at = t(g, ev, B.plannedAt)
        if at is None or (e is not None and at > e): out.append("a planning event lies outside the box")
        if s is not None and at is not None and at < s: out.append("a planning event precedes the start of the box")
    cks = [c for c in g.subjects(B.checkpointOfBox, it)]
    cts = [t(g, c, B.checkpointAt) for c in cks]
    if not cks: out.append("no checkpoint was recorded in the box")
    elif any(c is None or (s and c < s) or (e and c > e) for c in cts): out.append("a checkpoint lies outside the box")
    rv = FW["Review_%s_%d" % (P, n)]
    if (rv, RDF.type, B.SprintReviewCeremony) not in g or g.value(rv, B.closesIteration) != it: out.append("no review closes the box")
    else:
        rt = t(g, rv, B.heldAt)
        if cks and rt is not None and any(c is not None and c > rt for c in cts): out.append("a checkpoint follows the review")
        stories = list(g.objects(rv, B.closesStory))
        if not stories: out.append("the review closes no story")
        for st in stories:
            if g.value(st, B.hasState) != B.Done: out.append("a story the review closes is not Done")
            if g.value(st, B.hasEvidence) is None: out.append("a story the review closes has no evidence")
    retros = list(g.subjects(B.followsReview, rv))
    if not retros: out.append("no retrospective follows the review")
    for r in retros:
        fs = list(g.objects(r, B.producesFinding))
        if not fs: out.append("the retrospective produces no finding")
        for f in fs:
            if g.value(f, B.hasRootCause) is None or g.value(f, B.hasRemedy) is None: out.append("a finding has no root cause or no remedy")
    rel = FW["Rel_%s_%d" % (P, n)]
    if (rel, RDF.type, B.DeploymentUnit) not in g or g.value(rel, B.hasState) != B.Done: out.append("no deployment unit is Done for the box")
    return out
g = Graph(); g.parse(AB, format="turtle")
closed = [n for n in range(1, 20) if (FW["It_AP2_%d" % n], RDF.type, B.Iteration) in g and g.value(FW["It_AP2_%d" % n], B.hasState) == B.Done]
expect("the lineage has closed boxes and they are numbered one to n", bool(closed) and closed == list(range(1, len(closed) + 1)), "boxes %s" % closed)
for n in closed:
    expect("box %d is recorded as the step tool records a box, with no fault" % n, judge(g, n) == [], "; ".join(judge(g, n))[:200])
n = closed[0]
def without(pred):
    h = Graph()
    for tr in g:
        if not pred(tr): h.add(tr)
    return h
ck = list(g.subjects(B.checkpointOfBox, FW["It_AP2_%d" % n]))[0]
expect("a box whose checkpoints are removed is named", "no checkpoint was recorded in the box" in judge(without(lambda x: x[0] == ck), n) or len(list(g.subjects(B.checkpointOfBox, FW["It_AP2_%d" % n]))) > 1)
allck = set(g.subjects(B.checkpointOfBox, FW["It_AP2_%d" % n]))
expect("a box with no checkpoint is named", "no checkpoint was recorded in the box" in judge(without(lambda x: x[0] in allck), n))
rv = FW["Review_AP2_%d" % n]
expect("a box whose review is removed is named", "no review closes the box" in judge(without(lambda x: x[0] == rv), n))
retro = list(g.subjects(B.followsReview, rv))[0]; fnd = list(g.objects(retro, B.producesFinding))[0]
expect("a finding without a remedy is named", "a finding has no root cause or no remedy" in judge(without(lambda x: x[0] == fnd and x[1] == B.hasRemedy), n))
st = list(g.objects(rv, B.closesStory))[0]
h = without(lambda x: x[0] == st and x[1] == B.hasState); h.add((st, B.hasState, B.Ready))
expect("a story the review closes that is not Done is named", "a story the review closes is not Done" in judge(h, n))
ev = list(g.objects(FW["Ceremony_AP2_Planning%d" % n], B.includesPlanningEvent))[0]
h = without(lambda x: x[0] == ev and x[1] == B.plannedAt)
from rdflib import Literal, XSD
h.add((ev, B.plannedAt, Literal("2020-01-01T00:00:00Z", datatype=XSD.dateTime)))
expect("a planning event that precedes the start of the box is named", "a planning event precedes the start of the box" in judge(h, n))
r = subprocess.run([sys.executable, VAL, AB], capture_output=True, text=True, timeout=900)
expect("the validator finds no violation in the register under the rule sets it adopted", r.returncode == 0 and "0 violations at sh:Violation" in r.stdout)
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
