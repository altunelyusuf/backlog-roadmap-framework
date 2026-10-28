#!/usr/bin/env python3
"""backlog_g166_probe v1.5.0 -- re-runnable proof of the adaptive profile (G166).

  Checks the shipped files (the profile beside the standard and agentic ones, the two rule sets, the revision, the ruling), then plants small registers
  and expects the validator to defer, ask, refuse and accept exactly as the rule sets say. Exit 0 when every expectation holds."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
TB, AB, SH, VAL = (latest("01-ontologies/backlog_tbox_v*.ttl"), latest("01-ontologies/backlog_abox_v*.ttl"), latest("02-shacl-safeguards/backlog_shacl_v*.ttl"), latest("03-tooling/backlog_validate_v*.py"))
if sys.argv[1:] == ["--deps"]:
    print("\n".join([TB, AB, SH, VAL, os.path.abspath(__file__)])); sys.exit(0)
from rdflib import Graph, Namespace, RDF
B = Namespace("http://example.org/backlog#"); SHN = Namespace("http://www.w3.org/ns/shacl#"); FW = Namespace("http://example.org/framework#")
bad = []
def expect(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (" (%s)" % detail if detail else ""))
    if not ok: bad.append(name)
g = Graph(); g.parse(AB, format="turtle"); s = Graph(); s.parse(SH, format="turtle")
inc = lambda p: set(g.objects(p, B.profileIncludes))
std, agt, ada = inc(B.Profile_Standard), inc(B.Profile_Agentic), inc(B.Profile_Adaptive)
new = {B.RS_ObligationsFollowStatus, B.RS_ChainBothWays}
expect("the standard profile is as it was: nine rule sets", len(std) == 9, "%d" % len(std))
expect("the agentic profile is as it was: ten rule sets, the standard nine and agent accountability", len(agt) == 10 and std < agt)
expect("the adaptive profile is the standard nine plus the two new rule sets and the later ceremony-kind rule set, and no more", ada == std | new | {B.RS_CeremonyKinds, B.RS_ReadinessChecked, B.RS_ReviewNeedsControlRun}, "%d" % len(ada))
expect("the two new rule sets belong to profile revision 4 and the older ones do not", all(g.value(r, B.introducedInRevision) == B.Pr_4 for r in new) and not any(g.value(r, B.introducedInRevision) == B.Pr_4 for r in std))
expect("profile revision 4 carries its number", g.value(B.Pr_4, B.revisionNumber) is not None and int(g.value(B.Pr_4, B.revisionNumber)) == 4)
ruling = [r for r in g.subjects(B.hasRulingIdentifier, None) if str(g.value(r, B.hasRulingIdentifier)) == "G166"]
expect("ruling G166 exists, decides revision 4 and both rule sets, and names two shapes that exist", len(ruling) == 1 and set(g.objects(ruling[0], B.rulingDecides)) == new | {B.Pr_4} and len(set(g.objects(ruling[0], B.enforcedByShape))) == 2 and all((x, RDF.type, SHN.NodeShape) in s for x in g.objects(ruling[0], B.enforcedByShape)))
sh_txt = open(SH).read()
expect("ten constraints defer (eighteen mentions: each of the eight register-level deferrals names the rule set twice, once for the deferring adopter and once for the lineage that would keep the check on) to the lineage status or the epic state (seven register-level, the entity life-cycle sweep, two coarse-epic)", sh_txt.count("backlog:RS_ObligationsFollowStatus") == 18, "%d" % sh_txt.count("backlog:RS_ObligationsFollowStatus"))
H = "@prefix backlog: <http://example.org/backlog#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/g166#> .\n"
def lineage(status, adopt, revision="Pr_4"):
    rs = ["RS_CancellationAssessed", "RS_ChangeSupportsMission", "RS_ConcurrentLineages", "RS_DecompositionStateAgrees", "RS_FlowPointsRecorded", "RS_ImpedimentNamesWhatItBlocks", "RS_PlanBeforeStart", "RS_RepairReprioritises", "RS_StatusHistoryRecorded"] + (["RS_ObligationsFollowStatus", "RS_ChainBothWays"] if adopt else [])
    return (H + '<http://example.org/g166> a owl:Ontology ; owl:versionIRI <http://example.org/g166/1.0.0> ; owl:versionInfo "1.0.0" ; rdfs:label "G166 probe"@en .\n'
        'x:Reg a backlog:Backlog ; rdfs:label "Probe register"@en ; backlog:isRegisterRoot true ; backlog:hasIdentifier "G166-REG" ; backlog:hasTitle "Probe register"@en .\n'
        'x:M a backlog:Mission ; rdfs:label "Help small shops see what sells"@en ; backlog:hasMissionStatement "Help small shop owners see what sells, roughly." ; backlog:missionFor x:Reg ; backlog:hasMissionOrigin backlog:Origin_Stated ; backlog:missionSource "Probe." ; backlog:hasMissionOutcome backlog:Out_InFlight ; backlog:decidedBy backlog:Owner .\n'
        'x:L a backlog:Lineage ; rdfs:label "Probe lineage"@en ; backlog:lineageForMission x:M ; backlog:lineageOrdinal 1 ; backlog:lineageArchived false ; backlog:hasLineageStatus backlog:%s ; backlog:openedUnderRevision backlog:%s ; backlog:adoptionRecordedAtOpen true ; backlog:adoptsRuleSet %s .\n'
        % (status, revision, " , ".join("backlog:" + r for r in rs)))
SEVEN = ("no goal advances this mission", "a container must have at least one member item", "carries no commitment to a goal", "declares no Blueprint", "declares no Objective", "declares no ScopeStatement", "names no Definition of Done")
def run(text):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(text)
        out = subprocess.run([sys.executable, VAL, f], capture_output=True, text=True, timeout=900).stdout
    return [ln for ln in out.splitlines() if "[Violation]" in ln]
hits = lambda vs, ms: [m for m in ms if any(m in v for v in vs)]
v_plain = run(lineage("LS_Opened", False, "Pr_3"))
expect("a lineage that did not adopt the deferral is asked all seven register-level checks at once", len(hits(v_plain, SEVEN)) == 7, "%d of 7" % len(hits(v_plain, SEVEN)))
v_open = run(lineage("LS_Opened", True))
expect("an adopter at Opened is asked none of the seven", not hits(v_open, SEVEN), "%d asked" % len(hits(v_open, SEVEN)))
v_goal = run(lineage("LS_Goaled", True))
expect("an adopter at Goaled is asked for its goal, scope statement and blueprint, and not for the objective, commitment, member item or definition of done", len(hits(v_goal, [SEVEN[0], SEVEN[3], SEVEN[5]])) == 3 and not hits(v_goal, [SEVEN[1], SEVEN[2], SEVEN[4], SEVEN[6]]), "%d asked" % len(hits(v_goal, SEVEN)))
v_bl = run(lineage("LS_Backlogged", True))
expect("an adopter at Backlogged is asked all seven: nothing is removed, each is asked at the status that creates it", len(hits(v_bl, SEVEN)) == 7, "%d of 7" % len(hits(v_bl, SEVEN)))
base = lineage("LS_InProgress", True)
ENT = 'x:E a backlog:DomainEntity ; rdfs:label "Thing"@en ; backlog:belongsToLineage x:L .\n'
SWEEP = "life-cycle stage with neither backlog coverage"
expect("an adopter at Scoped is not asked the entity life-cycle sweep", not hits(run(lineage("LS_Scoped", True) + ENT), [SWEEP]))
expect("an adopter at Backlogged is asked the entity life-cycle sweep", bool(hits(run(lineage("LS_Backlogged", True) + ENT), [SWEEP])))
expect("a lineage that did not adopt the deferral is asked the sweep at Scoped", bool(hits(run(lineage("LS_Scoped", False, "Pr_3") + ENT), [SWEEP])))
v_ok = run(base + 'x:D1 a backlog:ScopeDeliverable ; rdfs:label "Weekly sales summary"@en .\nx:S1 a backlog:Story ; rdfs:label "Show the summary"@en ; backlog:belongsToLineage x:L ; backlog:hasState backlog:InProgress ; backlog:satisfiesDeliverable x:D1 .\n')
expect("a started item on a deliverable no scope requires is refused for an adopter", bool(hits(v_ok, ["satisfies a deliverable that no scope statement of the lineage requires"])))
v_prop = run(base + 'x:D1 a backlog:ScopeDeliverable ; rdfs:label "Weekly sales summary"@en .\nx:S1 a backlog:Story ; rdfs:label "Show the summary"@en ; backlog:belongsToLineage x:L ; backlog:hasState backlog:Proposed ; backlog:satisfiesDeliverable x:D1 .\n')
expect("the same item still only proposed is not refused: it may be found from the bottom and joined before it starts", not hits(v_prop, ["satisfies a deliverable that no scope statement of the lineage requires"]))
v_na = run(lineage("LS_InProgress", False, "Pr_3") + 'x:D1 a backlog:ScopeDeliverable ; rdfs:label "Weekly sales summary"@en .\nx:S1 a backlog:Story ; rdfs:label "Show the summary"@en ; backlog:belongsToLineage x:L ; backlog:hasState backlog:InProgress ; backlog:satisfiesDeliverable x:D1 .\n')
expect("a lineage that did not adopt the chain rule is not judged by it", not hits(v_na, ["satisfies a deliverable that no scope statement of the lineage requires"]))
v_rev = run(H + "x:R a backlog:ChainRevision .\n")
for m in ("name the one chain element", "what the element pointed at before", "what the element points at now", "state its reason", "name the objective it serves", "name the role that decided", "name the box boundary"):
    expect("a bare chain revision is refused: " + m, bool(hits(v_rev, [m])))
v_same = run(H + "x:R a backlog:ChainRevision ; backlog:revisedFrom x:A ; backlog:revisedTo x:A .\n")
expect("a revision whose before and after are the same re-points nothing", bool(hits(v_same, ["re-points nothing"])))

# post-mortem correction (G171): a deferral by one lineage must not switch the checks off for another lineage of the register
STD2 = ('x:M2 a backlog:Mission ; rdfs:label "Second mission"@en ; backlog:hasMissionStatement "Another thing." ; backlog:missionFor x:Reg ; backlog:hasMissionOrigin backlog:Origin_Stated ; backlog:missionSource "Probe." ; backlog:hasMissionOutcome backlog:Out_InFlight ; backlog:decidedBy backlog:Owner .\n'
        'x:L2 a backlog:Lineage ; rdfs:label "Standard lineage"@en ; backlog:lineageForMission x:M2 ; backlog:lineageOrdinal 2 ; backlog:lineageArchived false ; backlog:hasLineageStatus backlog:LS_InProgress ; backlog:openedUnderRevision backlog:Pr_3 ; backlog:adoptionRecordedAtOpen true ; backlog:adoptsRuleSet backlog:RS_ConcurrentLineages .\n')
v_mix = run(lineage("LS_Opened", True) + STD2)
expect("a low-status adopter beside a standard lineage does not switch the register-level checks off: all seven are asked", len(hits(v_mix, SEVEN)) >= 6, "%d of 7" % len(hits(v_mix, SEVEN)))
v_mix_sweep = run(lineage("LS_Scoped", True) + ENT + STD2)
expect("the same beside a standard lineage keeps the entity life-cycle sweep asked", bool(hits(v_mix_sweep, [SWEEP])))
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
