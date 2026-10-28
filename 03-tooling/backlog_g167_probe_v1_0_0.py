#!/usr/bin/env python3
"""backlog_g167_probe v1.0.0 -- re-runnable proof of the kind of work of a ceremony record (G167).

  Checks the shipped files (the closed set of eight kinds, the rule set in the adaptive profile only, the revision, the ruling), then plants small
  registers and expects the validator to refuse a ceremony record of an adopter with no kind or two, and to accept each of the eight kinds. Exit 0 when every expectation holds."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
TB, AB, SH, VAL = (latest("01-ontologies/backlog_tbox_v*.ttl"), latest("01-ontologies/backlog_abox_v*.ttl"), latest("02-shacl-safeguards/backlog_shacl_v*.ttl"), latest("03-tooling/backlog_validate_v*.py"))
if sys.argv[1:] == ["--deps"]:
    print("\n".join([TB, AB, SH, VAL, os.path.abspath(__file__)])); sys.exit(0)
from rdflib import Graph, Namespace, RDF
from rdflib.collection import Collection
B = Namespace("http://example.org/backlog#")
bad = []
def expect(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (" (%s)" % detail if detail else ""))
    if not ok: bad.append(name)
g = Graph(); g.parse(AB, format="turtle"); t = Graph(); t.parse(TB, format="turtle")
KINDS = ["Preparation", "Planning", "Execution", "Monitoring", "Control", "Reporting", "Closure", "ChangeManagement"]
members = set(Collection(t, t.value(B.WorkKind, __import__("rdflib").OWL.oneOf)))
expect("the kind of work is a closed set of exactly eight", members == {B["WorkKind_" + k] for k in KINDS}, "%d" % len(members))
expect("each of the eight is declared with a label and a definition", all(g.value(B["WorkKind_" + k], __import__("rdflib").RDFS.label) and g.value(B["WorkKind_" + k], __import__("rdflib").SKOS.definition if hasattr(__import__("rdflib"), "SKOS") else __import__("rdflib").namespace.SKOS.definition) for k in KINDS))
inc = lambda p: set(g.objects(p, B.profileIncludes))
expect("the standard and agentic profiles are as they were (nine and ten) and do not include the rule set", len(inc(B.Profile_Standard)) == 9 and len(inc(B.Profile_Agentic)) == 10 and B.RS_CeremonyKinds not in inc(B.Profile_Standard) | inc(B.Profile_Agentic))
expect("the adaptive profile includes the rule set, introduced in profile revision 5", B.RS_CeremonyKinds in inc(B.Profile_Adaptive) and g.value(B.RS_CeremonyKinds, B.introducedInRevision) == B.Pr_5 and int(g.value(B.Pr_5, B.revisionNumber)) == 5)
rul = [r for r in g.subjects(B.hasRulingIdentifier, None) if str(g.value(r, B.hasRulingIdentifier)) == "G167"]
expect("ruling G167 exists, decides revision 5 and the rule set, and names two shapes", len(rul) == 1 and set(g.objects(rul[0], B.rulingDecides)) == {B.Pr_5, B.RS_CeremonyKinds} and len(set(g.objects(rul[0], B.enforcedByShape))) == 2)
H = "@prefix backlog: <http://example.org/backlog#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/g167#> .\n"
def run(text):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(H + text)
        out = subprocess.run([sys.executable, VAL, f], capture_output=True, text=True, timeout=900).stdout
    return [ln for ln in out.splitlines() if "[Violation]" in ln]
NONE, TWO = "names no kind of work", "names two kinds of work"
hits = lambda vs, m: [v for v in vs if m in v]
def reg(adopt, ceremony):
    return ('x:L a backlog:Lineage %s .\nx:It a backlog:Iteration ; backlog:belongsToLineage x:L .\n' % ("; backlog:adoptsRuleSet backlog:RS_CeremonyKinds" if adopt else "")) + ceremony
PL = "x:C a backlog:SprintPlanningCeremony ; backlog:ceremonyFor x:It %s .\n"
expect("a planning ceremony of an adopter with no kind of work is refused", bool(hits(run(reg(True, PL % "")), NONE)))
expect("a planning ceremony of a lineage that did not adopt the rule set is not judged", not hits(run(reg(False, PL % "")), NONE))
expect("a planning ceremony with two kinds is refused", bool(hits(run(reg(True, PL % "; backlog:hasWorkKind backlog:WorkKind_Planning , backlog:WorkKind_Closure")), TWO)))
for k in KINDS:
    v = run(reg(True, PL % ("; backlog:hasWorkKind backlog:WorkKind_" + k)))
    expect("the kind %s is accepted on a planning ceremony" % k, not hits(v, NONE) and not hits(v, TWO))
expect("a refinement event of an adopter with no kind is refused", bool(hits(run('x:L a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_CeremonyKinds .\nx:S a backlog:Story ; backlog:belongsToLineage x:L .\nx:R a backlog:RefinementEvent ; backlog:refines x:S .\n'), NONE)))
expect("a retrospective that follows a review of an adopter is judged through the review", bool(hits(run(reg(True, 'x:V a backlog:SprintReviewCeremony ; backlog:ceremonyFor x:It .\nx:T a backlog:SprintRetrospective ; backlog:followsReview x:V .\n')), NONE)))
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
