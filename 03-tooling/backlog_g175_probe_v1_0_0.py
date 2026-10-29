#!/usr/bin/env python3
"""backlog_g175_probe v1.0.0 -- re-runnable proof for G175: what the fifth post-mortem found, closed and pinned.

  1. A deferral of an epic needs every owner of the epic to have adopted the rule; a register-level obligation follows the register whoever created it.
  2. The pipeline verifier names the lineage it verified: differing digest tables are refused, an unknown lineage is an error.
  3. The status at which each of the eight deferrals begins is pinned (one rank below: not asked; at it: asked), the every-owner condition is pinned, and copies
     of the shapes with the thresholds moved or the condition removed are noticed.
  4. Gate coverage of the lineage-status, agent-accountability, cancellation and repair-reprioritising rule sets (see section 4 below).
Exit 0 when every expectation holds."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
TB, AB, SH, VAL, PV = (latest("01-ontologies/backlog_tbox_v*.ttl"), latest("01-ontologies/backlog_abox_v*.ttl"), latest("02-shacl-safeguards/backlog_shacl_v*.ttl"),
                       latest("03-tooling/backlog_validate_v*.py"), latest("03-tooling/backlog_pipeline_verify_v*.py"))
# To show the probe failing on earlier files, name them: G175_SHAPES (a shapes file) and G175_VERIFY (a pipeline verifier). Nothing else changes.
SH, PV = os.environ.get("G175_SHAPES") or SH, os.environ.get("G175_VERIFY") or PV
if sys.argv[1:] == ["--deps"]:
    print("\n".join([TB, AB, SH, VAL, PV, os.path.abspath(__file__)])); sys.exit(0)
bad = []
def expect(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (" (%s)" % detail if detail else ""))
    if not ok: bad.append(name)
txt = open(SH).read()
H = "@prefix backlog: <http://example.org/backlog#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/x#> .\n"
def run(text, shapes=None):
    env = dict(os.environ)
    if shapes or os.environ.get("G175_SHAPES"): env["BACKLOG_VALIDATE_SHAPES"] = shapes or os.environ["G175_SHAPES"]
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(H + text)
        out = subprocess.run([sys.executable, VAL, f], capture_output=True, text=True, timeout=1200, env=env).stdout
    return [ln for ln in out.splitlines() if "[Violation]" in ln]
def mutated(fn):
    with tempfile.NamedTemporaryFile("w", suffix=".ttl", delete=False) as tf:
        tf.write(fn(txt)); return tf.name
RS = "RS_ObligationsFollowStatus"
LINRS = ["RS_CancellationAssessed", "RS_ChangeSupportsMission", "RS_ConcurrentLineages", "RS_DecompositionStateAgrees", "RS_FlowPointsRecorded",
         "RS_ImpedimentNamesWhatItBlocks", "RS_PlanBeforeStart", "RS_RepairReprioritises", "RS_StatusHistoryRecorded"]
def register(lins, reg_extra="", drop=()):
    """lins: list of (name, status, adopt). One register, one mission per lineage."""
    o = 'x:Reg a backlog:Backlog ; rdfs:label "Probe register"@en ; backlog:isRegisterRoot true ; backlog:hasIdentifier "G175-REG" ; backlog:hasTitle "Probe register"@en %s .\n' % reg_extra
    for i, lin in enumerate(lins):
        n, st, adopt = lin[:3]
        rs = [r for r in LINRS if r not in drop] + (["RS_ObligationsFollowStatus", "RS_ChainBothWays"] + list(lin[3] if len(lin) > 3 else []) if adopt else [])
        o += ('x:M_%s a backlog:Mission ; rdfs:label "Help small shops see what sells %s"@en ; backlog:hasMissionStatement "Help small shop owners see what sells, roughly." ; backlog:missionFor x:Reg ; backlog:hasMissionOrigin backlog:Origin_Stated ; backlog:missionSource "Probe." ; backlog:hasMissionOutcome backlog:Out_InFlight ; backlog:decidedBy backlog:Owner .\n'
              'x:%s a backlog:Lineage ; rdfs:label "Probe lineage %s"@en ; backlog:lineageForMission x:M_%s ; backlog:lineageOrdinal %d ; backlog:lineageArchived false ; backlog:hasLineageStatus backlog:%s ; backlog:openedUnderRevision backlog:%s ; backlog:adoptionRecordedAtOpen true ; backlog:adoptsRuleSet %s .\n'
              % (n, n, n, n, n, i + 1, st, "Pr_4" if adopt else "Pr_3", " , ".join("backlog:" + r for r in rs)))
    return o
msgs = lambda vs: sorted({v.split("]", 1)[1].split(None, 1)[1].strip() for v in vs if "]" in v and len(v.split("]", 1)[1].split(None, 1)) > 1})
named = lambda vs, n, key: any(v.split("]")[1].split()[0] == n and key in v for v in vs if "]" in v)

# ---- 1. owners ---------------------------------------------------------------------------------------------------------------------------------
lines = txt.splitlines()
epic_sites = [l for l in lines if "a coarse epic is owed its decomposition once it is Ready" in l]
conj = lambda var: ("FILTER NOT EXISTS { %s backlog:belongsToLineage ?ol . FILTER NOT EXISTS { ?ol a backlog:Lineage ; backlog:adoptsRuleSet backlog:%s . FILTER NOT EXISTS { ?ol backlog:lineageArchived true } } }" % (var, RS))
expect("both coarse-epic deferrals name the condition that every owner adopted the rule", len(epic_sites) == 2 and all(conj("$this") in l or conj("?e") in l for l in epic_sites))
EP = lambda n, owners, state="Proposed": 'x:%s a backlog:Epic ; backlog:hasIdentifier "%s" ; backlog:hasTitle "Epic %s" ; backlog:hasState backlog:%s ; backlog:hasPriorityScore 3.0 ; %s .\n' % (n, n, n, state, " ; ".join("backlog:belongsToLineage x:" + o for o in owners))
EPIC = "decomposes into nothing"
v = run(register([("A", "LS_Opened", True), ("N", "LS_Opened", False)]) + EP("E1", ["A", "N"]) + EP("E2", ["N"]) + EP("E3", ["A"]))
expect("an epic owned by an adopter alone is not asked for children while it is Proposed", not named(v, "E3", EPIC))
expect("an epic owned by a lineage that did not adopt is asked", named(v, "E2", EPIC))
expect("an epic owned by an adopter and by a lineage that did not adopt is asked as well", named(v, "E1", EPIC))
# a register that carries one creating lineage is judged as a register with no owner
base = [("A", "LS_Opened", True), ("N", "LS_Opened", False)]
v_own = run(register(base, "; backlog:belongsToLineage x:A"))
v_none = run(register(base))
expect("a register carrying one creating lineage is asked what a register with no owner is asked", msgs(v_own) == msgs(v_none) and len(msgs(v_none)) >= 6, "%d against %d messages" % (len(msgs(v_own)), len(msgs(v_none))))

# ---- 2. the verifier names the lineage -----------------------------------------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as d:
    f = os.path.join(d, "t.ttl")
    open(f, "w").write("@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/x#> .\nbacklog:RS_DigestTable_v5 a backlog:RuleSet .\nx:A a backlog:Lineage .\nx:B a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_DigestTable_v5 .\n")
    pv = lambda *a: subprocess.run([sys.executable, PV, f] + list(a), capture_output=True, text=True, timeout=300)
    r0, ra, rb, rt = pv(), pv("--lineage", "A"), pv("--lineage", "B"), pv("--lineage", "Typo")
    f2 = os.path.join(d, "u.ttl")
    open(f2, "w").write(open(f).read().replace("x:A a backlog:Lineage .", "x:A a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_DigestTable_v5 ."))
    r2 = subprocess.run([sys.executable, PV, f2], capture_output=True, text=True, timeout=300)
expect("with no lineage named, lineages that adopt different digest tables are refused and told to name one", r0.returncode == 1 and "name the one to verify with --lineage" in r0.stdout, r0.stdout[:100].strip())
expect("a named lineage is verified against its own table", "digest table: v1" in ra.stdout and "digest table: v5" in rb.stdout)
expect("a lineage name no lineage has is an error and not a fall-back to the first table", rt.returncode == 1 and "no real Lineage named Typo" in rt.stdout and "digest table" not in rt.stdout)
expect("with no lineage named, lineages that adopt the same table are verified against it", "digest table: v5" in r2.stdout)

# ---- 3. thresholds and the every-owner condition ------------------------------------------------------------------------------------------------
from rdflib import Graph, URIRef
B = "http://example.org/backlog#"
ga = Graph().parse(AB, format="turtle")
rank = {s: int(ga.value(URIRef(B + s), URIRef(B + "statusRank"))) for s in ("LS_Opened", "LS_Scoped", "LS_Goaled", "LS_Objectived", "LS_Backlogged")}
SITES = [("no goal advances this mission", 3), ("a container must have at least one member item", 5), ("carries no commitment to a goal", 5), ("declares no Blueprint", 2),
         ("declares no Objective", 4), ("declares no ScopeStatement", 2), ("names no Definition of Done", 5), ("life-cycle stage with neither backlog coverage", 5)]
ENT = 'x:E a backlog:DomainEntity ; rdfs:label "Thing"@en ; backlog:belongsToLineage x:L .\n'
def matrix(shapes=None):
    out = {}
    for st in rank:
        vs = run(register([("L", st, True)]) + ENT, shapes)
        out[st] = {k: any(k in v for v in vs) for k, _ in SITES}
    return out
exp = {st: {k: rank[st] >= n for k, n in SITES} for st in rank}
M = matrix()
wrong = [(st, k) for st in rank for k, _ in SITES if M[st][k] != exp[st][k]]
expect("each of the eight deferrals is asked at its status and not one rank below it", not wrong, str(wrong[:4]))
def shift(t):
    def f(m):
        return re.sub(r"(\?(?:d|n|o)[kr]) (<|>=) (\d)\)", lambda x: "%s %s %d)" % (x.group(1), x.group(2), int(x.group(3)) + 1), m)
    return f(t)
mp = mutated(shift)
try:
    Mm = matrix(mp)
finally:
    os.unlink(mp)
noticed = {k for k, _ in SITES if any(Mm[st][k] != exp[st][k] for st in rank)}
expect("with the threshold of every one of the eight deferrals moved by one, the matrix refuses each of them, so a moved threshold is noticed", noticed == {k for k, _ in SITES}, "not noticed: %s" % sorted({k for k, _ in SITES} - noticed))
CONT = lambda owners: 'x:C a backlog:WorkItemContainer ; backlog:hasIdentifier "C" ; %s .\n' % " ; ".join("backlog:belongsToLineage x:" + o for o in owners)
two = register([("A", "LS_Opened", True), ("N", "LS_Opened", False)]) + CONT(["A", "N"])
one = register([("A", "LS_Opened", True), ("N", "LS_Opened", False)]) + CONT(["A"])
MEMBER = "at least one member item"
expect("a container owned by a deferred adopter and a lineage that did not adopt is asked, and owned by the adopter alone is not", named(run(two), "C", MEMBER) and not named(run(one), "C", MEMBER))
def drop_conj(t):
    return re.sub(r" FILTER NOT EXISTS \{ \$this \(backlog:belongsToLineage\|\^backlog:lineageForMission\) \?nl \. \?nl a backlog:Lineage \. FILTER NOT EXISTS \{[^{}]*(?:\{[^{}]*\}[^{}]*)*\} \}", "", t)
mp = mutated(drop_conj)
try:
    flipped = not named(run(two, mp), "C", MEMBER)
finally:
    os.unlink(mp)
expect("with the every-owner condition removed from the deferrals, the two-owner container is no longer asked, so removing the condition is noticed", flipped)


# ---- 4. gate coverage of the four rule sets that G174 left out ---------------------------------------------------------------------------------
GATED = ["RS_LineageStatus", "RS_AgentAccountability", "RS_CancellationAssessed", "RS_RepairReprioritises"]
cons = []
for part in txt.split("a sh:SPARQLConstraint")[1:]:
    m1 = re.search(r'sh:message "(.*?)" ;', part, re.S); m2 = re.search(r'sh:select """(.*?)"""', part, re.S)
    if m1 and m2:
        for rs in GATED:
            if "backlog:" + rs in m2.group(1): cons.append((rs, m1.group(1)[:60]))
expect("the four rule sets gate nineteen constraints (5 + 7 + 5 + 2); a new gated constraint needs a case here", len(cons) == 19, str(len(cons)))
def gate_removed(t):
    """Every form the gate takes, replaced by a condition that is always true of the node the gate binds: a lineage (the `;` form) or the register root (a free variable), and any type for $this."""
    alt = "|".join(GATED)
    t = re.sub(r"(?<=; )backlog:adoptsRuleSet backlog:(?:%s)\b" % alt, "a backlog:Lineage", t)
    n = [0]
    def r(m):
        n[0] += 1; return "$this a ?_gt%d" % n[0]
    t = re.sub(r"\$this backlog:adoptsRuleSet backlog:(?:%s)\b" % alt, r, t)
    return re.sub(r"(\?\w+) backlog:adoptsRuleSet backlog:(?:%s)\b" % alt, r"\1 a backlog:Backlog", t)
mpg = mutated(gate_removed)
def drawn(vs): return {k for _, k in cons if any(k in v for v in vs)}
# 4a. a small register with one violating record for the five constraints the negative fixture has no case for
Q = "x:%s a backlog:ExecutorInstance , backlog:Executor_AgentTeam ; rdfs:label \"A team run\"@en .\n"
SUP = (Q % "TeamRun" +
       'x:W a backlog:Story ; backlog:hasIdentifier "W" ; backlog:hasTitle "W" ; backlog:hasState backlog:Ready ; backlog:responsible x:TeamRun ; backlog:belongsToLineage x:AL .\n'
       'x:Rp a backlog:Defect ; backlog:hasIdentifier "Rp" ; backlog:hasTitle "Repair" ; backlog:hasState backlog:InProgress ; backlog:belongsToLineage x:RL ; backlog:reprioritises x:Tgt ; backlog:hasPriorityScore x:Sc1 .\n'
       'x:Sc1 a backlog:WSJFScore ; backlog:scoredAt "2026-03-02T10:00:00Z"^^xsd:dateTime .\n'
       'x:Tgt a backlog:Story ; backlog:hasIdentifier "Tgt" ; backlog:hasTitle "Target" ; backlog:hasState backlog:Ready ; backlog:belongsToLineage x:RL .\n'
       'x:I1 a backlog:Story ; backlog:hasIdentifier "I1" ; backlog:hasTitle "Not assessed" ; backlog:hasState backlog:Done ; backlog:belongsToLineage x:CL .\n'
       'x:I2 a backlog:Story ; backlog:hasIdentifier "I2" ; backlog:hasTitle "Sorted wrongly" ; backlog:hasState backlog:InProgress ; backlog:belongsToLineage x:CL .\n'
       'x:Ob a backlog:Objective ; backlog:hasIdentifier "Ob" ; backlog:hasTitle "Unassessed objective" ; backlog:belongsToLineage x:CL .\n'
       'x:Asmt a backlog:AsIsAssessment ; backlog:assessesLineage x:CL ; backlog:accomplishedItem x:I2 .\n'
       'x:Rep a backlog:ClosureReport ; backlog:closesForMission x:M_CL .\n')
def sup(adopt, shapes=None):
    return run(register([("AL", "LS_InProgress", adopt, ["RS_AgentAccountability"]), ("RL", "LS_InProgress", adopt, ["RS_RepairReprioritises"]),
                         ("CL", "LS_Abandoned", adopt, ["RS_CancellationAssessed"])], drop=() if adopt else tuple(GATED)) + SUP, shapes)
SUPPFX = ("G118: an agent team or federation run is named", "G147: this open repair names an open item", "G162: this Abandoned lineage has a work item", "G162: this Abandoned lineage's as-is assessment sorts",
          "G162: this Abandoned lineage has an objective", "G162: the closure report")
SUPKEYS = {k for _, k in cons if k.startswith(SUPPFX)}
a_sup = drawn(sup(True)); n_sup = drawn(sup(False)); r_sup = drawn(sup(False, mpg))
expect("an adopter draws each of the five constraints the negative fixture has no case for", SUPKEYS <= a_sup, "missing: %s" % sorted(SUPKEYS - a_sup))
expect("a lineage that did not adopt draws none of them", not (n_sup & SUPKEYS), sorted(n_sup & SUPKEYS))
expect("with the gate removed from the shapes the same non-adopting register draws all five, so a removed gate is noticed", SUPKEYS <= r_sup, "missing: %s" % sorted(SUPKEYS - r_sup))
# 4b. the negative fixture holds a violating case for the other fourteen. Only the shapes that carry the nineteen constraints are asked, so the run is a few seconds and not the
#     full validation of the fixture (which the release gate runs).
from rdflib import Graph as G2, BNode
SHN = "http://www.w3.org/ns/shacl#"
gs = G2().parse(SH, format="turtle")
sub = G2()
for pre, ns in gs.namespaces(): sub.bind(pre, ns)
def copy_closure(node):
    for p_, o_ in gs.predicate_objects(node):
        sub.add((node, p_, o_))
        if isinstance(o_, BNode): copy_closure(o_)
for shp in set(gs.subjects(URIRef(SHN + "sparql"), None)):
    if isinstance(shp, URIRef) and any("backlog:" + rs in str(sel) for c in gs.objects(shp, URIRef(SHN + "sparql")) for sel in gs.objects(c, URIRef(SHN + "select")) for rs in GATED):
        copy_closure(shp)
FIX = latest("03-tooling/fixtures/fixture_negative_v*.ttl")
gfull = G2().parse(FIX, format="turtle")
def run_on(graph, sh, d, name):
    f = os.path.join(d, name); graph.serialize(f, format="turtle")
    return [ln for ln in subprocess.run([sys.executable, VAL, f], capture_output=True, text=True, timeout=1800, env=dict(os.environ, BACKLOG_VALIDATE_SHAPES=sh)).stdout.splitlines() if "[Violation]" in ln]
FIXKEYS = {k for _, k in cons} - SUPKEYS
with tempfile.TemporaryDirectory() as d:
    subf = os.path.join(d, "sub.ttl"); sub.serialize(subf, format="turtle")
    subm = os.path.join(d, "subm.ttl"); open(subm, "w").write(gate_removed(open(subf).read()))
    # the whole fixture, once, to find the nodes that carry the cases of the fourteen
    vs_full = [ln for ln in subprocess.run([sys.executable, VAL, FIX], capture_output=True, text=True, timeout=1800, env=dict(os.environ, BACKLOG_VALIDATE_SHAPES=subf)).stdout.splitlines() if "[Violation]" in ln]
    expect("the negative fixture draws each of the other fourteen constraints", FIXKEYS <= drawn(vs_full), "missing: %s" % sorted(FIXKEYS - drawn(vs_full)))
    foci = {ln.split()[1] for ln in vs_full if any(k in ln for k in FIXKEYS)}
    names = lambda n: str(n).rsplit("#", 1)[-1].rsplit("/", 1)[-1]
    start = {n for n in set(gfull.subjects()) if isinstance(n, URIRef) and names(n) in foci}
    indeg = {}
    for _, _, o_ in gfull:
        if isinstance(o_, (URIRef, BNode)): indeg[o_] = indeg.get(o_, 0) + 1
    keep, frontier = set(start), set(start)
    for _ in range(3):
        nxt = set()
        for n in frontier:
            for _, o_ in gfull.predicate_objects(n):
                if isinstance(o_, (URIRef, BNode)) and o_ not in keep and indeg.get(o_, 0) <= 60: nxt.add(o_)
        keep |= nxt; frontier = nxt
    for n in list(start):
        for s_, _ in gfull.subject_predicates(n):
            if indeg.get(s_, 0) <= 60 or isinstance(s_, URIRef): keep.add(s_)
    for rs_ in GATED:
        keep |= set(gfull.subjects(URIRef(B + "adoptsRuleSet"), URIRef(B + rs_)))
    red = G2()
    for pre, ns in gfull.namespaces(): red.bind(pre, ns)
    for t_ in gfull:
        if t_[0] in keep: red.add(t_)
    nored = G2()
    for t_ in red:
        if not (t_[1] == URIRef(B + "adoptsRuleSet") and str(t_[2]).rsplit("#", 1)[-1] in GATED): nored.add(t_)
    a_fix, n_fix, r_fix = drawn(run_on(red, subf, d, "ad.ttl")), drawn(run_on(nored, subf, d, "na.ttl")), drawn(run_on(nored, subm, d, "nam.ttl"))
expect("the part of the fixture that carries those cases (%d nodes) draws the fourteen" % len(keep), FIXKEYS <= a_fix, "missing: %s" % sorted(FIXKEYS - a_fix))
expect("the same part with the four rule sets taken out of every adoption draws none of the nineteen", not (n_fix & {k for _, k in cons}), sorted(n_fix))
expect("with the gate removed from the shapes that part draws the fourteen again, so a removed gate is noticed", FIXKEYS <= r_fix, "missing: %s" % sorted(FIXKEYS - r_fix))
os.unlink(mpg)

print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
