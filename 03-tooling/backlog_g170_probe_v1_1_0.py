#!/usr/bin/env python3
"""backlog_g170_probe v1.1.0 -- re-runnable proof of the deployment plan and of the review refused while a planned control has no run (G170).

  Checks the shipped files (the rule set in the adaptive profile only, the revision, the ruling), then plants small registers and expects the validator to refuse
  a plan with no box, unit or time, a plan made after its box started and a plan whose unit ships from another box, and to refuse a review of a box whose planned
  control has no run until the run is recorded. Exit 0 when every expectation holds."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
TB, AB, SH, VAL = (latest("01-ontologies/backlog_tbox_v*.ttl"), latest("01-ontologies/backlog_abox_v*.ttl"), latest("02-shacl-safeguards/backlog_shacl_v*.ttl"), latest("03-tooling/backlog_validate_v*.py"))
if sys.argv[1:] == ["--deps"]:
    print("\n".join([TB, AB, SH, VAL, os.path.abspath(__file__)])); sys.exit(0)
from rdflib import Graph, Namespace
B = Namespace("http://example.org/backlog#")
bad = []
def expect(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (" (%s)" % detail if detail else ""))
    if not ok: bad.append(name)
g = Graph(); g.parse(AB, format="turtle")
inc = lambda p: set(g.objects(p, B.profileIncludes))
expect("the standard and agentic profiles are as they were (nine and ten) and do not include the rule set", len(inc(B.Profile_Standard)) == 9 and len(inc(B.Profile_Agentic)) == 10 and B.RS_ReviewNeedsControlRun not in inc(B.Profile_Standard) | inc(B.Profile_Agentic))
expect("the adaptive profile includes the rule set, introduced in profile revision 7", B.RS_ReviewNeedsControlRun in inc(B.Profile_Adaptive) and g.value(B.RS_ReviewNeedsControlRun, B.introducedInRevision) == B.Pr_7 and int(g.value(B.Pr_7, B.revisionNumber)) == 7)
rul = [r for r in g.subjects(B.hasRulingIdentifier, None) if str(g.value(r, B.hasRulingIdentifier)) == "G170"]
expect("ruling G170 exists, decides revision 7 and the rule set, and names two shapes", len(rul) == 1 and set(g.objects(rul[0], B.rulingDecides)) == {B.Pr_7, B.RS_ReviewNeedsControlRun} and len(set(g.objects(rul[0], B.enforcedByShape))) == 2)
H = "@prefix backlog: <http://example.org/backlog#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/g170#> .\n"
def run(text):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(H + text)
        out = subprocess.run([sys.executable, VAL, f], capture_output=True, text=True, timeout=900).stdout
    return [ln for ln in out.splitlines() if "[Violation]" in ln]
hits = lambda vs, m: [v for v in vs if m in v]
d = lambda t: '"2026-10-28T%s:00Z"^^xsd:dateTime' % t
BOX = 'x:It a backlog:Iteration ; backlog:iterationStart %s .\nx:Other a backlog:Iteration .\nx:U a backlog:DeploymentUnit ; backlog:deploysFrom x:It .\n' % d("10:00")
PL = 'x:P a backlog:DeploymentPlan ; backlog:hasWorkKind backlog:WorkKind_Planning ; backlog:deploymentPlanForBox x:It ; backlog:plansDeploymentUnit x:U ; backlog:deploymentPlannedAt %s .\n'
v = run('x:P a backlog:DeploymentPlan .\n'); expect("a bare deployment plan is refused: no box, no unit, no time, no kind", all(hits(v, m) for m in ("name the box", "name the deployment unit", "when it was made", "serves planning")))
v = run(BOX + PL % d("09:00")); expect("a plan made before the box started and naming the unit is accepted", not [x for x in v if "G170" in x])
expect("a plan made after the box started is refused", bool(hits(run(BOX + PL % d("11:00")), "after its box started")))
expect("a plan whose unit ships from another box is refused", bool(hits(run(BOX + (PL % d("09:00")).replace("deploymentPlanForBox x:It", "deploymentPlanForBox x:Other")), "ships from another box")))
LIN = 'x:L a backlog:Lineage %s .\nx:B a backlog:Iteration ; backlog:belongsToLineage x:L .\nx:A a backlog:ControlActivity ; backlog:hasWorkKind backlog:WorkKind_Control ; backlog:plannedInBox x:B .\nx:V a backlog:SprintReviewCeremony ; backlog:ceremonyFor x:B .\n'
ADOPT = "; backlog:adoptsRuleSet backlog:RS_ReviewNeedsControlRun"
expect("a review of a box whose planned control has no run is refused", bool(hits(run(LIN % ADOPT), "has no recorded run")))
RUN = 'x:R a backlog:ControlRun ; backlog:runOfActivity x:A ; backlog:ranAt %s ; backlog:hasRunResult "Passed." .\n' % d("10:30")
expect("the same review is accepted once the run is recorded", not hits(run(LIN % ADOPT + RUN), "has no recorded run"))
expect("a review of a lineage that did not adopt the rule set is not judged", not hits(run(LIN % ""), "has no recorded run"))
expect("a review of a box with no planned control is not refused", not hits(run('x:L a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_ReviewNeedsControlRun .\nx:B a backlog:Iteration ; backlog:belongsToLineage x:L .\nx:V a backlog:SprintReviewCeremony ; backlog:ceremonyFor x:B .\n'), "has no recorded run"))

# post-mortem correction (G171): the review waits for the run
LINH = LIN.replace("backlog:ceremonyFor x:B .", "backlog:ceremonyFor x:B ; backlog:heldAt %s .") 
expect("a review held before the run is refused: a run recorded after the review does not count", bool(hits(run(LINH % (ADOPT, d("10:10")) + RUN), "held before the planned control")))
expect("a review held after the run is accepted", not hits(run(LINH % (ADOPT, d("10:40")) + RUN), "held before the planned control") and not hits(run(LINH % (ADOPT, d("10:40")) + RUN), "has no recorded run"))
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
