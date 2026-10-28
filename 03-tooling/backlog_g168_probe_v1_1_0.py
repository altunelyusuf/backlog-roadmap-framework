#!/usr/bin/env python3
"""backlog_g168_probe v1.1.0 -- re-runnable proof of the readiness check (G168).

  Checks the shipped files (the rule set in the adaptive profile only, the revision, the ruling), then plants small registers and expects the validator to
  refuse a Ready item with no check, a Ready item with an unmet criterion and a bare check, and to accept a Ready item whose criteria are all met.
  Exit 0 when every expectation holds."""
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
expect("the standard and agentic profiles are as they were (nine and ten) and do not include the rule set", len(inc(B.Profile_Standard)) == 9 and len(inc(B.Profile_Agentic)) == 10 and B.RS_ReadinessChecked not in inc(B.Profile_Standard) | inc(B.Profile_Agentic))
expect("the adaptive profile includes the rule set, introduced in profile revision 6", B.RS_ReadinessChecked in inc(B.Profile_Adaptive) and g.value(B.RS_ReadinessChecked, B.introducedInRevision) == B.Pr_6 and int(g.value(B.Pr_6, B.revisionNumber)) == 6)
rul = [r for r in g.subjects(B.hasRulingIdentifier, None) if str(g.value(r, B.hasRulingIdentifier)) == "G168"]
expect("ruling G168 exists, decides revision 6 and the rule set, and names two shapes", len(rul) == 1 and set(g.objects(rul[0], B.rulingDecides)) == {B.Pr_6, B.RS_ReadinessChecked} and len(set(g.objects(rul[0], B.enforcedByShape))) == 2)
H = "@prefix backlog: <http://example.org/backlog#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/g168#> .\n"
def run(text):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(H + text)
        out = subprocess.run([sys.executable, VAL, f], capture_output=True, text=True, timeout=900).stdout
    return [ln for ln in out.splitlines() if "[Violation]" in ln]
NONE, UNMET, BARE = "no readiness check of it exists", "has a criterion that is not met", "must state at least one criterion"
hits = lambda vs, m: [v for v in vs if m in v]
def reg(adopt, state="Ready", extra=""):
    return ('x:L a backlog:Lineage %s .\nx:S a backlog:Story ; backlog:belongsToLineage x:L ; backlog:hasState backlog:%s .\n' % ("; backlog:adoptsRuleSet backlog:RS_ReadinessChecked" if adopt else "", state)) + extra
CHK = 'x:C a backlog:ReadinessCheck ; backlog:checksReadinessOf x:S ; backlog:readinessCheckedAt "2026-10-28T00:00:00Z"^^xsd:dateTime ; backlog:hasReadinessCriterion x:K .\nx:K a backlog:ReadinessCriterion ; backlog:criterionMet %s .\n'
expect("a Ready item of an adopter with no check is refused", bool(hits(run(reg(True)), NONE)))
expect("a Ready item of a lineage that did not adopt the rule set is not judged", not hits(run(reg(False)), NONE))
expect("a Ready item with a check whose criteria are all met is accepted", not hits(run(reg(True, extra=CHK % "true")), NONE) and not hits(run(reg(True, extra=CHK % "true")), UNMET))
expect("a Ready item whose check has an unmet criterion is refused", bool(hits(run(reg(True, extra=CHK % "false")), UNMET)))
expect("an item not yet Ready may hold a check with an unmet criterion", not hits(run(reg(True, "Proposed", CHK % "false")), UNMET))
expect("a Ready item whose criterion has no answer is refused", bool(hits(run(reg(True, extra=CHK.replace(" ; backlog:criterionMet %s", "").replace("x:K a backlog:ReadinessCriterion .", "x:K a backlog:ReadinessCriterion .") % ())), UNMET)))
expect("a bare readiness check is refused: it names no item, no time and no criterion", all(hits(run("x:R a backlog:ReadinessCheck .\n"), m) for m in ("name the item", "record when", BARE)))

# post-mortem corrections (G171)
CHK2 = 'x:C2 a backlog:ReadinessCheck ; backlog:checksReadinessOf x:S ; backlog:readinessCheckedAt "2026-10-28T01:00:00Z"^^xsd:dateTime ; backlog:hasReadinessCriterion x:K2 .\nx:K2 a backlog:ReadinessCriterion ; backlog:criterionMet true .\n'
expect("an earlier unmet check that a later all-met check supersedes does not block a Ready item", not hits(run(reg(True, extra=CHK % "false" + CHK2)), UNMET))
expect("a later unmet check still blocks a Ready item whose earlier check was all met", bool(hits(run(reg(True, extra=CHK % "true" + CHK2.replace("criterionMet true", "criterionMet false"))), UNMET)))
expect("an item that is in progress with no check is refused: Ready cannot be skipped", bool(hits(run(reg(True, "InProgress")), NONE.replace("exists", "exists")) ) or bool(hits(run(reg(True, "InProgress")), "no readiness check of it")))
expect("a Done item with no check is refused", bool(hits(run(reg(True, "Done")), "no readiness check of it")))
LATE = 'x:S backlog:startedAt "2026-10-28T00:30:00Z"^^xsd:dateTime .\n'
LATE_MSG = "made at or before its start"
expect("a started item whose only check was made after its start is refused", bool(hits(run(reg(True, "InProgress", CHK % "true" + LATE.replace("00:30", "00:00").replace("2026-10-28T00:00:00Z", "2026-10-27T23:00:00Z"))), LATE_MSG)))
expect("a started item whose check was made before its start is accepted", not hits(run(reg(True, "InProgress", CHK % "true" + LATE)), LATE_MSG) and not hits(run(reg(True, "InProgress", CHK % "true" + LATE)), "no readiness check of it"))
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
