#!/usr/bin/env python3
"""backlog_g173_probe v1.0.0 -- re-runnable proof that a rule judges only the lineage that adopted it (G173).

  Static sweep: every test of the shapes file that asks "has a rule set been adopted" is tied to the element judged, to a non-lineage register, or to the
  lineage that owns the element; none asks whether SOME lineage adopted it. Then planted registers: each case plants an adopter beside a lineage that did
  not adopt (or an archived one) and expects the non-adopter to be judged as before and the adopter as stated. Exit 0 when every expectation holds."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
TB, AB, SH, VAL = (latest("01-ontologies/backlog_tbox_v*.ttl"), latest("01-ontologies/backlog_abox_v*.ttl"), latest("02-shacl-safeguards/backlog_shacl_v*.ttl"), latest("03-tooling/backlog_validate_v*.py"))
if sys.argv[1:] == ["--deps"]:
    print("\n".join([TB, AB, SH, VAL, os.path.abspath(__file__)])); sys.exit(0)
bad = []
def expect(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (" (%s)" % detail if detail else ""))
    if not ok: bad.append(name)

# ---- static sweep -------------------------------------------------------------------------------------------------------------------------------
txt = open(SH).read()
blocks = re.findall(r'sh:select """(.*?)"""', txt, re.S)
loose = []
for b in blocks:
    lns = b.splitlines()
    for i, ln in enumerate(lns):
        nxt = ln + " " + (lns[i + 1] if i + 1 < len(lns) else "")
        for m in re.finditer(r'(\?\w+) backlog:adoptsRuleSet (backlog:RS_\w+)', ln):
            var, rs = m.group(1), m.group(2)
            if var in ("?dl", "?ol", "?nl", "?al"):
                continue   # the deferral's own clauses: the lineage whose status or owner is asked
            if "$this" in ln.split(m.group(0))[0][-40:]:
                continue
            ok = ("FILTER NOT EXISTS { %s a backlog:Lineage }" % var) in nxt or ("%s a backlog:Lineage" % var) in nxt
            if not ok and var in ("?l", "?reg"):
                # a variable bound to the lineage of the element judged: the block must bind it from $this or an item of $this's box
                ok = re.search(r'\$this backlog:\w+ %s\b' % re.escape(var), b) is not None or re.search(r'belongsToLineage %s\b' % re.escape(var), b) is not None or re.search(r'\{ \$this backlog:belongsToLineage %s' % re.escape(var), b) is not None
            if not ok: loose.append((var, rs))
expect("no test of the shapes asks whether some lineage adopted a rule set without tying it to the element judged", not loose, str(loose[:5]))
expect("the shapes file names the rule set of the deferral in every one of its eight deferrals and ten constraints", txt.count("backlog:RS_ObligationsFollowStatus") == 34, str(txt.count("backlog:RS_ObligationsFollowStatus")))

# ---- planted registers --------------------------------------------------------------------------------------------------------------------------
H = "@prefix backlog: <http://example.org/backlog#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/g173#> .\n"
def run(text):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(H + text)
        out = subprocess.run([sys.executable, VAL, f], capture_output=True, text=True, timeout=900).stdout
    return [ln for ln in out.splitlines() if "[Violation]" in ln]
hits = lambda vs, m: [v for v in vs if m in v]
RS = "RS_ObligationsFollowStatus"
def lin(name, adopt, status, extra=""):
    return 'x:%s a backlog:Lineage ; backlog:hasLineageStatus backlog:%s %s %s .\n' % (name, status, ("; backlog:adoptsRuleSet backlog:" + RS) if adopt else "", extra)
MEMBERS = "at least one member item"
# 1. a container owned by an archived standard lineage, beside an adopter at Opened
C = 'x:C a backlog:WorkItemContainer ; backlog:hasIdentifier "C" ; backlog:belongsToLineage x:Old .\n'
v = run(lin("Adopter", True, "LS_Opened") + lin("Old", False, "LS_Closed", "; backlog:lineageArchived true") + C)
expect("a container owned by an archived standard lineage is still asked for a member beside an adopter at Opened", bool(hits(v, MEMBERS)))
v = run(lin("Adopter", True, "LS_Opened") + 'x:C a backlog:WorkItemContainer ; backlog:hasIdentifier "C" ; backlog:belongsToLineage x:Adopter .\n')
expect("the adopter's own container is not asked at Opened (the deferral still works)", not hits(v, MEMBERS))
# 2. an adopter that states two statuses defers nothing it should not
v = run(lin("Adopter", True, "LS_Opened", "; backlog:hasLineageStatus backlog:LS_Backlogged") + 'x:C a backlog:WorkItemContainer ; backlog:hasIdentifier "C" ; backlog:belongsToLineage x:Adopter .\n')
expect("an adopter that states Opened and Backlogged is asked as at Backlogged", bool(hits(v, MEMBERS)))
# 3. the lineage-status rule judges the lineage that adopted it
v = run(lin("A", True, "LS_Opened").replace("; backlog:hasLineageStatus backlog:LS_Opened", "") + lin("B", False, "LS_Opened").replace("; backlog:hasLineageStatus backlog:LS_Opened", ""))
expect("two lineages without a status, neither adopting the lineage-status rule, draw no demand for one", not hits(v, "has no hasLineageStatus"))
v = run('x:A a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_LineageStatus .\nx:B a backlog:Lineage ; backlog:hasLineageStatus backlog:LS_Opened .\n')
expect("a lineage that adopts the lineage-status rule is asked for its status and its neighbour that did not adopt is not", len(hits(v, "has no hasLineageStatus")) == 1)
# 4. the label convention judges the lineage that adopted it
M = 'x:M1 a backlog:Mission ; backlog:belongsToLineage x:A .\nx:M2 a backlog:Mission ; backlog:belongsToLineage x:B .\n'
v = run('x:A a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_LabelConvention .\nx:B a backlog:Lineage .\n' + M)
expect("an unlabelled mission is refused in the lineage that adopted the label convention and not in its neighbour", len(hits(v, "no rdfs:label and no hasTitle")) == 1)
# 5. ceremony records of a lineage that did not adopt the rule sets are not judged
NA = 'x:L a backlog:Lineage .\nx:It a backlog:Iteration ; backlog:belongsToLineage x:L ; backlog:iterationStart "2026-10-28T10:00:00Z"^^xsd:dateTime .\n'
AD = lambda rs: 'x:L a backlog:Lineage ; backlog:adoptsRuleSet backlog:%s .\nx:It a backlog:Iteration ; backlog:belongsToLineage x:L ; backlog:iterationStart "2026-10-28T10:00:00Z"^^xsd:dateTime .\n' % rs
RV = "RS_ReviewNeedsControlRun"
PLAN = 'x:U a backlog:DeploymentUnit ; backlog:deploysFrom x:It .\nx:P a backlog:DeploymentPlan ; backlog:hasWorkKind backlog:WorkKind_Planning ; backlog:deploymentPlanForBox x:It ; backlog:plansDeploymentUnit x:U ; backlog:deploymentPlannedAt "2026-10-28T11:00:00Z"^^xsd:dateTime .\n'
expect("a plan made after the start is refused for an adopter and not for a lineage that did not adopt", bool(hits(run(AD(RV) + PLAN), "after its box started")) and not hits(run(NA + PLAN), "after its box started"))
RUN = 'x:A a backlog:ControlActivity ; backlog:hasWorkKind backlog:WorkKind_Control ; backlog:plannedInBox x:It .\nx:R a backlog:ControlRun ; backlog:runOfActivity x:A ; backlog:ranAt "2026-10-28T09:00:00Z"^^xsd:dateTime ; backlog:hasRunResult "ok" .\n'
expect("a run before the start is refused for an adopter and not for a lineage that did not adopt", bool(hits(run(AD(RV) + RUN), "before the box it controls started")) and not hits(run(NA + RUN), "before the box it controls started"))
DEMO = 'x:S a backlog:Story ; backlog:belongsToLineage x:L ; backlog:hasAcceptanceCriterion x:C1 ; backlog:hasState backlog:InProgress .\nx:C1 a backlog:AcceptanceCriterion .\nx:D a backlog:DemoRun ; backlog:hasWorkKind backlog:WorkKind_Control ; backlog:demonstratesItem x:S ; backlog:demonstratedAgainst x:C1 ; backlog:demoAt "2026-10-28T12:00:00Z"^^xsd:dateTime ; backlog:hasDemoShown "s" ; backlog:hasDemoResult "r" .\n'
expect("a demo of an unfinished item is refused for an adopter and not for a lineage that did not adopt", bool(hits(run(AD(RV) + DEMO), "not finished")) and not hits(run(NA + DEMO), "not finished"))
CHK = 'x:S a backlog:Story ; backlog:belongsToLineage x:L ; backlog:hasState backlog:InProgress ; backlog:startedAt "2026-10-28T12:00:00Z"^^xsd:dateTime .\nx:C a backlog:ReadinessCheck ; backlog:checksReadinessOf x:S ; backlog:readinessCheckedAt "2026-10-28T11:00:00Z"^^xsd:dateTime ; backlog:hasReadinessCriterion x:K .\nx:K a backlog:ReadinessCriterion ; backlog:criterionMet false .\n'
expect("an unmet latest check of a started item is refused for an adopter and not for a lineage that did not adopt", bool(hits(run(AD("RS_ReadinessChecked") + CHK), "criterion that is not met")) and not hits(run(NA + CHK), "criterion that is not met"))
KT = 'x:E a backlog:RefinementEvent ; backlog:refines x:S ; backlog:hasWorkKind backlog:WorkKind_Preparation , backlog:WorkKind_Planning .\nx:S a backlog:Story ; backlog:belongsToLineage x:L .\n'
expect("a record naming two kinds of work is refused for an adopter and not for a lineage that did not adopt", bool(hits(run(AD("RS_CeremonyKinds") + KT), "two kinds of work")) and not hits(run(NA + KT), "two kinds of work"))
# 6. the readiness rule reaches a started item in any state, the admitted route, and respects a stated absence of a start
RDY = 'x:S a backlog:Story ; backlog:belongsToLineage x:L ; backlog:hasState backlog:%s %s .\n'
expect("a started item that was then Suspended is asked for a readiness check", bool(hits(run(AD("RS_ReadinessChecked") + RDY % ("Suspended", '; backlog:startedAt "2026-10-28T12:00:00Z"^^xsd:dateTime')), "no readiness check of it")))
expect("an item that was never started and is Suspended is not asked", not hits(run(AD("RS_ReadinessChecked") + RDY % ("Suspended", "")), "no readiness check of it"))
ADM = 'x:L a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_ReadinessChecked .\nx:O a backlog:StageOutput ; backlog:belongsToLineage x:L ; backlog:outputOfStage backlog:Stage_Backlog .\nx:S a backlog:Story ; backlog:preLineageItem true ; backlog:admittedByOutput x:O ; backlog:hasState backlog:InProgress ; backlog:startedAt "2026-10-28T12:00:00Z"^^xsd:dateTime .\n'
expect("an item reached only through the output that admitted it is asked for a readiness check", bool(hits(run(ADM), "no readiness check of it")))
expect("an item in progress that states why it has no start time is not refused for the missing start", not hits(run(AD("RS_ReadinessChecked") + RDY % ("InProgress", '; backlog:flowPointAbsenceReason "not witnessed"')), "records no start time"))
# 7. a check names one item and one time
CHK2 = 'x:S2 a backlog:Story ; backlog:belongsToLineage x:L ; backlog:hasState backlog:Ready .\n'
expect("a readiness check of two items is refused", bool(hits(run(AD("RS_ReadinessChecked") + CHK + CHK2 + 'x:C backlog:checksReadinessOf x:S2 .\n'), "name the item it is about")))
expect("a readiness check with two times is refused", bool(hits(run(AD("RS_ReadinessChecked") + CHK + 'x:C backlog:readinessCheckedAt "2026-10-28T11:30:00Z"^^xsd:dateTime .\n'), "once, as a dateTime")))
# 8. a time that is not a dateTime does not slip past the box start
expect("a run time written as a plain string is refused", bool(hits(run(AD(RV) + RUN.replace('"2026-10-28T09:00:00Z"^^xsd:dateTime', '"2026-10-28T09:00:00Z"')), "once, as a dateTime")))
expect("a box of an adopter that records no start as a dateTime is refused when a plan is made for it", bool(hits(run(AD(RV).replace('backlog:iterationStart "2026-10-28T10:00:00Z"^^xsd:dateTime', 'backlog:iterationStart "2026-10-28"^^xsd:date') + PLAN), "records no start as a dateTime")))
# 9. a checkpoint count is not negative
CKP = lambda n: AD(RV) + 'x:K a backlog:DailyCheckpoint ; backlog:hasWorkKind backlog:WorkKind_Monitoring ; backlog:checkpointOfBox x:It ; backlog:checkpointAt "2026-10-28T10:30:00Z"^^xsd:dateTime ; backlog:openItemCount %d ; backlog:inProgressItemCount 1 ; backlog:doneItemCount 1 .\n' % n
expect("a checkpoint with a negative count is refused and the same checkpoint with a count of five is not", bool(hits(run(CKP(-5)), "how many items are open")) and not hits(run(CKP(5)), "how many items are open"))
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
