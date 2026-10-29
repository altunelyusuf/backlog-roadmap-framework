#!/usr/bin/env python3
"""backlog_g174_probe v1.3.0 -- re-runnable proof for G174: a deferral judges the lineage that owns the element, the verifier chooses its digest table from the
lineage's own rule sets, and every gate of the ceremony shapes is seen by a probe that fails when the gate is removed.

  1. Static: all eight deferral clauses carry the owner branch and none keeps the old register-wide form.
  2. Planted registers for the deferral: an adopter below the status that creates the element beside a live adopter past it, a live non-adopter and an
     archived adopter -- the adopter's own element is not asked, the others are.
  3. The digest table of the pipeline verifier follows the lineage verified, not a word found in the file.
  4. Gate coverage: fifteen constraints of the ceremony shapes are each gated by the rule set a lineage must adopt. One register of non-adopter records
     (one violating record per constraint) must draw none of the fifteen messages; the same records in an adopter lineage must draw all fifteen; and a
     copy of the shapes with the gate of every one of the fifteen removed must draw all fifteen for the non-adopter -- so removing any gate is noticed.
  5. Records: the observations of the contained rules equal the inclusions of the standard and agentic profiles (nineteen, ten of them distinct), each finding of the
     lineage is produced by exactly one retrospective, and no deployment unit is dated before the review that closed its box. (An earlier text of this line promised
     more than the code checks; corrected by G175.)
Exit 0 when every expectation holds."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
TB, AB, SH, VAL, PV = (latest("01-ontologies/backlog_tbox_v*.ttl"), latest("01-ontologies/backlog_abox_v*.ttl"), latest("02-shacl-safeguards/backlog_shacl_v*.ttl"),
                       latest("03-tooling/backlog_validate_v*.py"), latest("03-tooling/backlog_pipeline_verify_v*.py"))
if sys.argv[1:] == ["--deps"]:
    print("\n".join([TB, AB, SH, VAL, PV, os.path.abspath(__file__)])); sys.exit(0)
bad = []
def expect(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (" (%s)" % detail if detail else ""))
    if not ok: bad.append(name)

# ---- 1. static ------------------------------------------------------------------------------------------------------------------------------------
txt = open(SH).read()
lines = txt.splitlines()
sites = [i for i, ln in enumerate(lines) if "G166: an adopter of RS_ObligationsFollowStatus owes this" in ln]
OWN = "$this (backlog:belongsToLineage|^backlog:lineageForMission) ?dl"
carry = [i for i in sites if OWN in lines[i + 1]]
expect("all eight deferral clauses carry the owner branch", len(sites) == 8 and len(carry) == 8, "%d clauses, %d with the owner branch" % (len(sites), len(carry)))
expect("no deferral keeps the old register-wide form", "FILTER NOT EXISTS { ?dl a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_ObligationsFollowStatus" not in txt)
expect("the register-wide branch applies only where the element has no owner or is itself a register", all("FILTER ( NOT EXISTS { $this (backlog:belongsToLineage|^backlog:lineageForMission) ?xl . ?xl a backlog:Lineage } || EXISTS { $this a backlog:Backlog } || EXISTS { $this backlog:isRegisterRoot true } )" in lines[i + 1] for i in sites))

# ---- helpers -----------------------------------------------------------------------------------------------------------------------------------------
H = "@prefix backlog: <http://example.org/backlog#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/x#> .\n"
def run(text, shapes=None):
    env = dict(os.environ)
    if shapes: env["BACKLOG_VALIDATE_SHAPES"] = shapes
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(H + text)
        out = subprocess.run([sys.executable, VAL, f], capture_output=True, text=True, timeout=1200, env=env).stdout
    return [ln for ln in out.splitlines() if "[Violation]" in ln]
RS = "RS_ObligationsFollowStatus"
def lin(name, adopt, status, extra=""):
    return 'x:%s a backlog:Lineage ; backlog:hasLineageStatus backlog:%s %s %s .\n' % (name, status, ("; backlog:adoptsRuleSet backlog:" + RS) if adopt else "", extra)
def cont(name, owner): return 'x:%s a backlog:WorkItemContainer ; backlog:hasIdentifier "%s" ; backlog:belongsToLineage x:%s .\n' % (name, name, owner)
MEMBERS = "at least one member item"
flagged = lambda vs, n: any(v.split("]")[1].split()[0] == n and MEMBERS in v for v in vs if "]" in v)

# ---- 2. the deferral judges the owner ------------------------------------------------------------------------------------------------------------
reg = (lin("A", True, "LS_Opened") + cont("CA", "A")
       + lin("B", True, "LS_Backlogged") + cont("CB", "B")
       + lin("N", False, "LS_Opened") + cont("CN", "N")
       + lin("L", True, "LS_Backlogged", "; backlog:lineageArchived true") + cont("CL", "L"))
v = run(reg)
expect("an adopter below the status that creates a container is not asked for a member while other lineages are live", not flagged(v, "CA"))
expect("a live adopter past that status is asked", flagged(v, "CB"))
expect("a live lineage that did not adopt the rule set is asked", flagged(v, "CN"))
expect("an archived adopter past that status is asked", flagged(v, "CL"))

# ---- 3. the digest table follows the lineage verified ---------------------------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as d:
    f = os.path.join(d, "t.ttl")
    open(f, "w").write("@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/x#> .\nbacklog:RS_DigestTable_v5 a backlog:RuleSet .\nx:A a backlog:Lineage .\nx:B a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_DigestTable_v5 .\n")
    tab = lambda l: [ln for ln in subprocess.run([sys.executable, PV, f, "--lineage", l], capture_output=True, text=True, timeout=300).stdout.splitlines() if ln.startswith("digest table")]
    ta, tb = tab("A"), tab("B")
expect("a lineage that did not adopt the v5 table is verified against v1 although the file defines the v5 rule set", bool(ta) and ta[0].startswith("digest table: v1"), str(ta)[:80])
expect("the lineage that adopted it is verified against v5", bool(tb) and tb[0].startswith("digest table: v5"), str(tb)[:80])

# ---- 4. gate coverage -----------------------------------------------------------------------------------------------------------------------------
KEYS = {  # id: (message key, kind)
    1: "names no kind of work", 2: "names two kinds of work", 3: "no readiness check of it exists", 4: "records no start time",
    5: "made at or before its start", 6: "criterion that is not met", 7: "before the box it controls started",
    8: "records no start as a dateTime, so whether the run came", 9: "shows an item that is not finished", 10: "before the item it shows was started",
    11: "was made after its box started", 12: "so whether the plan came before the start", 13: "has no recorded run", 14: "records no time it was held",
    15: "held before the planned control",
}
NODE = {1: "Rf1", 2: "Rf2", 3: "S3", 4: "S4", 5: "S5", 6: "Ck6", 7: "Run7", 8: "Run8", 9: "Demo9", 10: "Demo10", 11: "Plan11", 12: "Plan12", 13: "Rev13", 14: "Rev14", 15: "Rev15"}
def recs(s, adopt):
    L = "x:L_" + s
    t = lambda h: '"2026-10-28T%s:00Z"^^xsd:dateTime' % h
    a = ""
    if adopt: a = "; backlog:adoptsRuleSet backlog:RS_CeremonyKinds , backlog:RS_ReadinessChecked , backlog:RS_ReviewNeedsControlRun"
    o = "%s a backlog:Lineage %s .\n" % (L, a)
    def box(n, start=True):
        return "x:%s_%s a backlog:Iteration ; backlog:belongsToLineage %s %s .\n" % (n, s, L, ('; backlog:iterationStart %s' % t("10:00")) if start else "")
    def item(n, state, extra=""):
        return "x:%s_%s a backlog:Story ; backlog:belongsToLineage %s ; backlog:hasState backlog:%s %s .\n" % (n, s, L, state, extra)
    n = lambda k: "x:%s_%s" % (k, s)
    o += item("S1", "Open")
    o += "%s a backlog:RefinementEvent ; backlog:refines %s .\n" % (n("Rf1"), n("S1"))
    o += "%s a backlog:RefinementEvent ; backlog:refines %s ; backlog:hasWorkKind backlog:WorkKind_Preparation , backlog:WorkKind_Planning .\n" % (n("Rf2"), n("S1"))
    o += item("S3", "Ready")
    o += item("S4", "InProgress")
    o += item("S5", "InProgress", "; backlog:startedAt %s" % t("12:00"))
    o += "%s a backlog:ReadinessCheck ; backlog:checksReadinessOf %s ; backlog:readinessCheckedAt %s ; backlog:hasReadinessCriterion %s .\n%s a backlog:ReadinessCriterion ; backlog:criterionMet true .\n" % (n("Ck5"), n("S5"), t("13:00"), n("K5"), n("K5"))
    o += item("S6", "Ready")
    o += "%s a backlog:ReadinessCheck ; backlog:checksReadinessOf %s ; backlog:readinessCheckedAt %s ; backlog:hasReadinessCriterion %s .\n%s a backlog:ReadinessCriterion ; backlog:criterionMet false .\n" % (n("Ck6"), n("S6"), t("11:00"), n("K6"), n("K6"))
    o += box("It7") + "%s a backlog:ControlActivity ; backlog:hasWorkKind backlog:WorkKind_Control ; backlog:plannedInBox %s .\n" % (n("Act7"), n("It7"))
    o += "%s a backlog:ControlRun ; backlog:runOfActivity %s ; backlog:ranAt %s ; backlog:hasRunResult \"r\" .\n" % (n("Run7"), n("Act7"), t("09:00"))
    o += box("It8", False) + "%s a backlog:ControlActivity ; backlog:hasWorkKind backlog:WorkKind_Control ; backlog:plannedInBox %s .\n" % (n("Act8"), n("It8"))
    o += "%s a backlog:ControlRun ; backlog:runOfActivity %s ; backlog:ranAt %s ; backlog:hasRunResult \"r\" .\n" % (n("Run8"), n("Act8"), t("09:00"))
    o += item("S9", "InProgress", "; backlog:hasAcceptanceCriterion %s" % n("C9")) + "%s a backlog:AcceptanceCriterion .\n" % n("C9")
    o += "%s a backlog:DemoRun ; backlog:hasWorkKind backlog:WorkKind_Control ; backlog:demonstratesItem %s ; backlog:demonstratedAgainst %s ; backlog:demoAt %s .\n" % (n("Demo9"), n("S9"), n("C9"), t("11:00"))
    o += item("S10", "Done", "; backlog:startedAt %s ; backlog:hasAcceptanceCriterion %s" % (t("12:00"), n("C10"))) + "%s a backlog:AcceptanceCriterion .\n" % n("C10")
    o += "%s a backlog:DemoRun ; backlog:hasWorkKind backlog:WorkKind_Control ; backlog:demonstratesItem %s ; backlog:demonstratedAgainst %s ; backlog:demoAt %s .\n" % (n("Demo10"), n("S10"), n("C10"), t("11:00"))
    o += box("It11") + "%s a backlog:DeploymentUnit ; backlog:deploysFrom %s .\n" % (n("U11"), n("It11"))
    o += "%s a backlog:DeploymentPlan ; backlog:hasWorkKind backlog:WorkKind_Planning ; backlog:deploymentPlanForBox %s ; backlog:plansDeploymentUnit %s ; backlog:deploymentPlannedAt %s .\n" % (n("Plan11"), n("It11"), n("U11"), t("11:00"))
    o += box("It12", False) + "%s a backlog:DeploymentUnit ; backlog:deploysFrom %s .\n" % (n("U12"), n("It12"))
    o += "%s a backlog:DeploymentPlan ; backlog:hasWorkKind backlog:WorkKind_Planning ; backlog:deploymentPlanForBox %s ; backlog:plansDeploymentUnit %s ; backlog:deploymentPlannedAt %s .\n" % (n("Plan12"), n("It12"), n("U12"), t("09:00"))
    for k, held in ((13, None), (14, None), (15, "10:30")):
        o += box("It%d" % k) + "%s a backlog:ControlActivity ; backlog:hasWorkKind backlog:WorkKind_Control ; backlog:plannedInBox %s .\n" % (n("Act%d" % k), n("It%d" % k))
        o += "%s a backlog:SprintReviewCeremony ; backlog:hasWorkKind backlog:WorkKind_Closure ; backlog:ceremonyFor %s %s .\n" % (n("Rev%d" % k), n("It%d" % k), ("; backlog:heldAt %s" % t(held)) if held else "")
    o += "%s a backlog:ControlRun ; backlog:runOfActivity %s ; backlog:ranAt %s ; backlog:hasRunResult \"r\" .\n" % (n("Run15"), n("Act15"), t("11:00"))
    o += "%s a backlog:ControlRun ; backlog:runOfActivity %s ; backlog:ranAt %s ; backlog:hasRunResult \"r\" .\n" % (n("Run14"), n("Act14"), t("11:00"))
    return o
def has(vs, k, s):
    return any((NODE[k] + "_" + s) in v.split("]")[1].split()[0] and KEYS[k] in v for v in vs if "]" in v)
def ids(vs, s): return [k for k in KEYS if has(vs, k, s)]
NA, AD = recs("na", False), recs("ad", True)
v_ship_na = run(NA)
expect("a lineage that did not adopt the ceremony rule sets draws none of the fifteen gated messages", not ids(v_ship_na, "na"), str(ids(v_ship_na, "na")))
v_ship_ad = run(AD)
expect("the same records in a lineage that adopted them draw all fifteen", sorted(ids(v_ship_ad, "ad")) == list(KEYS), "missing: %s" % [k for k in KEYS if k not in ids(v_ship_ad, "ad")])
# a copy of the shapes with the gate of each of the fifteen constraints removed
MARK = {1: "names no kind of work", 2: "names two kinds of work", 3: "no readiness check of it exists", 4: "records no start time", 5: "made at or before its start",
        6: "has a criterion that is not met", 7: "took place before the box it controls started", 8: "records no start as a dateTime, so whether the run came",
        9: "shows an item that is not finished", 10: "took place before the item it shows was started", 11: "was made after its box started",
        12: "so whether the plan came before the start", 13: "has no recorded run", 14: "records no time it was held", 15: "was held before the planned control"}
GATE = re.compile(r"\?l backlog:adoptsRuleSet backlog:RS_\w+ \.[ \t]*")
parts = re.split(r"(?=\n    sh:sparql \[ a sh:SPARQLConstraint)", txt)
mut, removed = [], set()
for p in parts:
    hit = [k for k, m in MARK.items() if "sh:message \"" in p and m in p.split("sh:prefixes")[0]]
    if hit and GATE.search(p):
        p = GATE.sub("", p, count=1); removed.add(hit[0])
    mut.append(p)
expect("the gate of each of the fifteen constraints was found and removed in the copy", removed == set(KEYS), "not found: %s" % sorted(set(KEYS) - removed))
with tempfile.NamedTemporaryFile("w", suffix=".ttl", delete=False) as tf:
    tf.write("".join(mut)); mp = tf.name
try:
    v_mut = run(NA, shapes=mp)
finally:
    os.unlink(mp)
seen = ids(v_mut, "na")
expect("with the gate of every one of the fifteen removed, the non-adopter's records draw all fifteen, so removing any one gate is noticed", sorted(seen) == list(KEYS), "missing: %s" % [k for k in KEYS if k not in seen])

# ---- 5. the records say what the data shows -----------------------------------------------------------------------------------------------------
from rdflib import Graph, URIRef, RDF, Literal
B = "http://example.org/backlog#"; FW = "http://example.org/backlog-framework-register#"
g = Graph().parse(AB, format="turtle")
_arc = sorted(glob.glob(os.path.join(PKG, "01-ontologies/archive/backlog_framework_archive_abox_v*.ttl")), key=sv)
if _arc: g.parse(_arc[-1], format="turtle")  # v1.3.0: Lineage 20 is archived, its observations live in the archive
inc = lambda p: {str(o) for o in g.objects(URIRef(B + p), URIRef(B + "profileIncludes"))}
inclusions = len(inc("Profile_Standard")) + len(inc("Profile_Agentic")); distinct = len(inc("Profile_Standard") | inc("Profile_Agentic"))
vals = {str(s).rsplit("#", 1)[1]: float(g.value(s, URIRef(B + "hasObservedValue"))) for s in g.subjects(URIRef(B + "observesMetric"), URIRef(FW + "Metric_AC_Contained"))}
expect("every observation of the contained rules equals the inclusions of the standard and agentic profiles, and the metric says a rule set in both is counted twice", bool(vals) and all(v == inclusions for v in vals.values()) and inclusions > distinct and "counted once for each profile" in str(g.value(URIRef(FW + "Metric_AC_Contained"), URIRef("http://www.w3.org/2004/02/skos/core#definition"))), "%s against %d inclusions, %d distinct" % (vals, inclusions, distinct))
prod = {}
for r in [x for x in g.subjects(RDF.type, URIRef(B + "SprintRetrospective")) if str(x).startswith(FW + "Retro_AC_")]:
    for f in g.objects(r, URIRef(B + "producesFinding")): prod.setdefault(str(f).rsplit("#", 1)[1], []).append(str(r).rsplit("#", 1)[1])
dup = {f: rs for f, rs in prod.items() if len(rs) > 1}
expect("no finding is produced by two retrospectives of the lineage", not dup, str(dup)[:300])
found = {str(f).rsplit("#", 1)[1] for f in g.subjects(RDF.type, URIRef(B + "RetrospectiveFinding")) if str(f).startswith(FW + "Find_AC_")}
orph = sorted(found - set(prod))
expect("every finding of the lineage is produced by a retrospective", not orph, str(orph))
bad_dep = []
for u in g.subjects(RDF.type, URIRef(B + "DeploymentUnit")):
    d = g.value(u, URIRef(B + "hasDeploymentDate")); box = g.value(u, URIRef(B + "deploysFrom"))
    for rv in g.subjects(URIRef(B + "closesIteration"), box):
        h = g.value(rv, URIRef(B + "heldAt"))
        if d is not None and h is not None and d.toPython() < h.toPython(): bad_dep.append(str(u).rsplit("#", 1)[1])
expect("no deployment unit is dated before the review that closed its box", not bad_dep, str(bad_dep))

print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
