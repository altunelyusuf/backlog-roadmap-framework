#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe reads no record of the framework register; the validator keeps only the controlled individuals)
"""backlog_handover_rules_probe v1.3.0 -- re-runnable proof of the five G148 rulings and the G150 rename case rulings (T-Box v1.146.0, shapes v1.179.0, A-Box v1.56.0).

  A  L4 intent chain and the empty-epic rule do not judge a Cancelled item (an adopting project: a cancelled epic is not work to measure or groom).
  B  RS_DecompositionStateAgrees: a parent whose children are all Done or Cancelled, one at least Done, is not left open.
  C  the order check witnesses each ADOPTION of a lineage that claims adoptionRecordedAtOpen against the active Mission commit.
  D1 backlog_execution_ready lifts the freeze when the finding named by frozenBy is answered (covered by its own probe, fixture
     Lin_FrozenAnswered; this probe only checks that probe is the one the gate runs).
  D2 a goal may derive from the scope of a mission that supersedes the one it contributes to (another registrant restart).
Each rule fires on its planted case and is silent on its control. Exit 0 when every expectation holds, 1 otherwise.
"""
import glob, importlib.util, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    for pat in ("03-tooling/backlog_validate_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl",
                "01-ontologies/backlog_abox_v*.ttl", "03-tooling/backlog_lineage_order_check_v*.py", "03-tooling/backlog_execution_ready_probe_v*.py"):
        print(latest(pat))
    print(os.path.abspath(__file__)); sys.exit(0)
val = latest("03-tooling/backlog_validate_v*.py")
bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)

HEAD = ("@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/g148-probe#> .\n"
        "x:L a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_DecompositionStateAgrees .\n")
KEYS = {"INTENT": "L4: this item advances no recorded objective", "EMPTY": "decomposes into nothing",
        "DSA": "yet the item itself is neither Done nor Cancelled", "CMA": "W:Advisory (G154)", "DEP": "is Done and sits in no DeploymentUnit", "IMP": "impedes no work item or container", "TRI": "whose mission is not the mission the goal contributes to"}
def item(n, cls, state, extra="", lin=True):
    return f"x:{n} a backlog:{cls} ; backlog:hasState backlog:{state}" + (" ; backlog:belongsToLineage x:L" if lin else "") + " " + extra + ".\n"
SCEN = [
 # A
 ("A  a Proposed epic with no objective and no child", HEAD + item("E", "Epic", "Proposed"), {"INTENT": 1, "EMPTY": 1}),
 ("A  a Cancelled epic with no objective and no child (exempt)", HEAD + item("E", "Epic", "Cancelled"), {"INTENT": 0, "EMPTY": 0}),
 # B
 ("B  parent InProgress, its only child Done", HEAD + item("P", "Story", "InProgress", "; backlog:decomposesInto x:K ") + item("K", "Story", "Done"), {"DSA": 1}),
 ("B  parent Ready, children Done and Cancelled", HEAD + item("P", "Story", "Ready", "; backlog:decomposesInto x:K , x:C ") + item("K", "Story", "Done") + item("C", "Story", "Cancelled"), {"DSA": 1}),
 ("B  parent InProgress, one child still open (control)", HEAD + item("P", "Story", "InProgress", "; backlog:decomposesInto x:K , x:O ") + item("K", "Story", "Done") + item("O", "Story", "InProgress"), {"DSA": 0}),
 ("B  parent InProgress, every child Cancelled (control: nothing was done)", HEAD + item("P", "Story", "InProgress", "; backlog:decomposesInto x:C ") + item("C", "Story", "Cancelled"), {"DSA": 0}),
 ("B  parent Done (control)", HEAD + item("P", "Story", "Done", "; backlog:decomposesInto x:K ") + item("K", "Story", "Done"), {"DSA": 0}),
 ("B  no adoption anywhere (control: the rule binds only an adopter)", HEAD.replace("backlog:adoptsRuleSet backlog:RS_DecompositionStateAgrees", "") .replace("x:L a backlog:Lineage ; ", "x:L a backlog:Lineage ") + item("P", "Story", "InProgress", "; backlog:decomposesInto x:K ") + item("K", "Story", "Done"), {"DSA": 0}),
 # G153: a Done epic is delivered through its stories, so the deployment-coverage rule does not ask for a unit
 ("G153 a Done epic whose Done story is deployed, audit adopter", HEAD + "x:L backlog:adoptsRuleSet backlog:RS_SeverityAudit_20260909 .\nx:E a backlog:Epic ; backlog:hasState backlog:Done ; backlog:belongsToLineage x:L ; backlog:decomposesInto x:S .\nx:S a backlog:Story ; backlog:hasState backlog:Done ; backlog:belongsToLineage x:L .\nx:U a backlog:DeploymentUnit ; backlog:deploysItem x:S .\n", {"DEP": 0}),
 ("G153 a Done story in no unit, audit adopter (control)", HEAD + "x:L backlog:adoptsRuleSet backlog:RS_SeverityAudit_20260909 .\nx:S a backlog:Story ; backlog:hasState backlog:Done ; backlog:belongsToLineage x:L .\n", {"DEP": 1}),
 # G154
 ("G154 frozen by a bypass, the owner's ruling, one bypassed item admitted by no ScopeChange", HEAD + "x:L backlog:lineageFrozen true ; backlog:frozenBy x:BP ; backlog:frozenRuling \"No need to restart.\" .\nx:BP a backlog:LineageBypass ; backlog:bypassedLineage x:L ; backlog:bypassedItem x:I .\nx:I a backlog:Story ; backlog:belongsToLineage x:L .\n", {"CMA": 1}),
 ("G154 the same, the item admitted (control)", HEAD + "x:L backlog:lineageFrozen true ; backlog:frozenBy x:BP ; backlog:frozenRuling \"No need to restart.\" .\nx:BP a backlog:LineageBypass ; backlog:bypassedLineage x:L ; backlog:bypassedItem x:I .\nx:I a backlog:Story ; backlog:belongsToLineage x:L .\nx:SC a backlog:ScopeChange ; backlog:admitsItem x:I .\n", {"CMA": 0}),
 # G149
 ("G149 an unresolved impediment that blocks nothing", HEAD + "x:L backlog:adoptsRuleSet backlog:RS_ImpedimentNamesWhatItBlocks .\nx:I a backlog:Impediment ; backlog:belongsToLineage x:L .\n", {"IMP": 1}),
 ("G149 an unresolved impediment that names its work (control)", HEAD + "x:L backlog:adoptsRuleSet backlog:RS_ImpedimentNamesWhatItBlocks .\nx:S a backlog:Story ; backlog:belongsToLineage x:L .\nx:I a backlog:Impediment ; backlog:belongsToLineage x:L ; backlog:impedes x:S .\n", {"IMP": 0}),
 ("G149 a resolved impediment that blocks nothing (control)", HEAD + "x:L backlog:adoptsRuleSet backlog:RS_ImpedimentNamesWhatItBlocks .\nx:I a backlog:Impediment ; backlog:belongsToLineage x:L ; backlog:resolvedAt \"2026-10-24T10:00:00Z\"^^<http://www.w3.org/2001/XMLSchema#dateTime> .\n", {"IMP": 0}),
 ("G149 no adoption (control)", HEAD + "x:I a backlog:Impediment ; backlog:belongsToLineage x:L .\n", {"IMP": 0}),
 # D2
 ("D2 goal contributes to a mission, its scope belongs to an unrelated mission", HEAD + "x:G a backlog:Goal ; backlog:contributesToMission x:M1 ; backlog:derivesFromScope x:S2 .\nx:S2 backlog:scopeForMission x:M2 .\n", {"TRI": 1}),
 ("D2 the scope's mission supersedes the goal's mission (control)", HEAD + "x:G a backlog:Goal ; backlog:contributesToMission x:M1 ; backlog:derivesFromScope x:S2 .\nx:S2 backlog:scopeForMission x:M2 .\nx:M2 backlog:supersedesMission x:M1 .\n", {"TRI": 0}),
 ("D2 two restarts later: M3 supersedes M2 supersedes M1 (control)", HEAD + "x:G a backlog:Goal ; backlog:contributesToMission x:M1 ; backlog:derivesFromScope x:S3 .\nx:S3 backlog:scopeForMission x:M3 .\nx:M3 backlog:supersedesMission x:M2 .\nx:M2 backlog:supersedesMission x:M1 .\n", {"TRI": 0}),
]
with tempfile.TemporaryDirectory() as d:
    for name, body, want in SCEN:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=900).stdout
        for k, n in want.items():
            sev, key = ("[Warning]", KEYS[k][2:]) if KEYS[k].startswith("W:") else ("[Violation]", KEYS[k])
            got = sum(1 for ln in out.splitlines() if sev in ln and key in ln)
            expect(f"{name} [{k}]: expected {n}, got {got}", got == n)

# C: the per-adoption git witness, on a temporary repository
chk = latest("03-tooling/backlog_lineage_order_check_v*.py")
spec = importlib.util.spec_from_file_location("oc", chk); oc = importlib.util.module_from_spec(spec); spec.loader.exec_module(oc)
from rdflib import URIRef
NS = "http://example.org/g148-git#"; B = "http://example.org/backlog#"
def git(d, *a): return subprocess.run(["git", "-c", "user.email=p@p", "-c", "user.name=p", *a], cwd=d, capture_output=True, text=True, check=True).stdout
with tempfile.TemporaryDirectory() as d:
    git(d, "init", "-q"); os.makedirs(os.path.join(d, "reg"))
    f = os.path.join(d, "reg", "register.ttl")
    P = f"@prefix backlog: <{B}> .\n@prefix x: <{NS}> .\n"
    def commit(body, msg):
        open(f, "w").write(P + body); git(d, "add", "-A"); git(d, "commit", "-q", "-m", msg)
        return git(d, "rev-parse", "--short", "HEAD").strip()
    c1 = commit("x:Other a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_A .\nx:L a backlog:Lineage .\n", "other adopts RS_A; L is declared")
    c2 = commit("x:Other a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_A .\nx:L a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_A .\n", "L adopts RS_A later")
    c3 = commit("x:Other a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_A .\nx:L a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_A , backlog:RS_B .\n", "L adopts RS_B later still")
    w = oc.GitWitness(d, "reg"); w.reg_files = ["reg/register.ttl"]
    L = URIRef(NS + "L"); AR = URIRef(B + "adoptsRuleSet")
    a = w.adoption_first(L, AR, URIRef(B + "RS_A")); b = w.adoption_first(L, AR, URIRef(B + "RS_B")); n = w.adoption_first(L, AR, URIRef(B + "RS_Never"))
    expect("C  the lineage's own adoption is found at its commit, not at another lineage's earlier use of the same name", a is not None and a[0] == c2)
    expect("C  a second adoption on the same lineage is found at its own, later commit", b is not None and b[0] == c3 and b[1] > a[1])
    expect("C  a set never adopted is not found", n is None)
    # through the order check itself: Mission output committed with the lineage, a rule set adopted two commits later
    def reg(adopt_later):
        return (f"@prefix backlog: <{B}> .\n@prefix x: <{NS}> .\n"
                "x:L a backlog:Lineage ; backlog:lineageOrdinal 1 ; backlog:adoptionRecordedAtOpen true" + (" ; backlog:adoptsRuleSet backlog:RS_A" if adopt_later == 0 else "") + " .\n"
                "x:O_M a backlog:StageOutput ; backlog:outputOfStage backlog:Stage_Mission ; backlog:belongsToLineage x:L ; backlog:closedAtCommit \"c\" ; backlog:hasStateDigest \"d\" .\n"
                + ("x:L backlog:adoptsRuleSet backlog:RS_A .\n" if adopt_later == 2 else ""))
    for label, mode, want in (("an adoption in the Mission commit (control)", 0, 0), ("an adoption two commits after the Mission output", 2, 1)):
        with tempfile.TemporaryDirectory() as e:
            git(e, "init", "-q"); os.makedirs(os.path.join(e, "reg")); g2 = os.path.join(e, "reg", "register.ttl")
            if mode == 0:
                open(g2, "w").write(reg(0)); git(e, "add", "-A"); git(e, "commit", "-q", "-m", "mission", "--author=p <p@p>") if False else subprocess.run(["git", "-c", "user.email=p@p", "-c", "user.name=p", "commit", "-q", "-m", "mission"], cwd=e, check=True)
            else:
                open(g2, "w").write(reg(1)); git(e, "add", "-A"); git(e, "commit", "-q", "-m", "mission")
                open(g2, "w").write(reg(1) + "x:Z a backlog:Epic .\n"); git(e, "add", "-A"); git(e, "commit", "-q", "-m", "unrelated")
                open(g2, "w").write(reg(2)); git(e, "add", "-A"); git(e, "commit", "-q", "-m", "adopt")
            out = subprocess.run([sys.executable, chk, g2], capture_output=True, text=True, timeout=300).stdout
            got = sum(1 for ln in out.splitlines() if "claims adoptionRecordedAtOpen but adopts" in ln)
            expect(f"C  order check: {label}: expected {want}, got {got}", got == want)
# C2 (G150): a BP-D7 versioned rename after the Mission commit must not make an adoption at open look late, and a late one after it is still caught
for label, late, want in (("adoption at open, then a versioned rename (control)", 0, 0), ("adoption at open, rename, then a late adoption", 1, 1)):
    with tempfile.TemporaryDirectory() as e:
        git(e, "init", "-q"); os.makedirs(os.path.join(e, "reg"))
        a = os.path.join(e, "reg", "register_v1_0_0.ttl"); b = os.path.join(e, "reg", "register_v1_1_0.ttl")
        def rg(adopt_late):
            return (f"@prefix backlog: <{B}> .\n@prefix x: <{NS}> .\n"
                    "x:L a backlog:Lineage ; backlog:lineageOrdinal 1 ; backlog:adoptionRecordedAtOpen true ; backlog:adoptsRuleSet backlog:RS_A .\n"
                    "x:O_M a backlog:StageOutput ; backlog:outputOfStage backlog:Stage_Mission ; backlog:belongsToLineage x:L ; backlog:closedAtCommit \"c\" ; backlog:hasStateDigest \"d\" .\n"
                    + ("x:L backlog:adoptsRuleSet backlog:RS_B .\n" if adopt_late else ""))
        open(a, "w").write(rg(0)); git(e, "add", "-A"); git(e, "commit", "-q", "-m", "mission")
        git(e, "mv", a, b); open(b, "a").write("x:Z a backlog:Epic .\n"); git(e, "add", "-A"); git(e, "commit", "-q", "-m", "evolve")
        if late:
            open(b, "w").write(rg(1) + "x:Z a backlog:Epic .\n"); git(e, "add", "-A"); git(e, "commit", "-q", "-m", "adopt late")
        out = subprocess.run([sys.executable, chk, b], capture_output=True, text=True, timeout=300).stdout
        got = sum(1 for ln in out.splitlines() if "claims adoptionRecordedAtOpen but adopts" in ln)
        expect(f"C2 order check across a versioned rename: {label}: expected {want}, got {got}", got == want)
# G154: the owner's route -- a bypass answered by the owner's frozenRuling and a ScopeChange admitting every bypassed item
STAGES = ["Mission", "Scope", "Goal", "Objective", "Backlog"]
def route_register(upto, ruling, admit):
    t = f"@prefix backlog: <{B}> .\n@prefix x: <{NS}> .\n"
    t += "x:L a backlog:Lineage ; backlog:lineageOrdinal 1 ; backlog:lineageArchived false" + (" ; backlog:lineageFrozen true ; backlog:frozenBy x:BP" if upto > 5 else "") + (" ; backlog:frozenRuling \"No need to restart, you should use change management.\"" if ruling else "") + " .\n"
    for n in range(upto if upto <= 5 else 5):
        st = STAGES[n]; prev = f" ; backlog:consumesOutput x:O_{STAGES[n-1]}" if n else ""
        t += f"x:O_{st} a backlog:StageOutput ; backlog:outputOfStage backlog:Stage_{st} ; backlog:belongsToLineage x:L{prev} ; backlog:closedAtCommit \"c\" ; backlog:hasStateDigest \"d{st}\" .\n"
    return t
with tempfile.TemporaryDirectory() as e:
    git(e, "init", "-q"); os.makedirs(os.path.join(e, "reg")); rf = os.path.join(e, "reg", "register.ttl")
    def put(body, msg): open(rf, "w").write(body); git(e, "add", "-A"); git(e, "commit", "-q", "-m", msg)
    item = "x:I1 a backlog:Story ; backlog:hasState backlog:Done ; backlog:belongsToLineage x:L .\nx:I2 a backlog:Story ; backlog:hasState backlog:Done ; backlog:belongsToLineage x:L .\n"
    put(route_register(0, 0, 0), "lineage"); put(route_register(0, 0, 0) + item, "work first")
    for n in range(1, 6): put(route_register(n, 0, 0) + item, "stage %d" % n)
    finding = "x:BP a backlog:LineageBypass ; backlog:bypassedLineage x:L ; backlog:bypassedItem x:I1 , x:I2 .\n"
    put(route_register(6, 0, 0) + item + finding, "bypass recorded")
    def verdict(body):
        open(rf, "w").write(body)
        out = subprocess.run([sys.executable, chk, rf], capture_output=True, text=True, timeout=300).stdout
        m = re.search(r"^\s+L\s+(\w+)", out, re.M); return m.group(1) if m else out[-300:]
    base = route_register(6, 1, 0) + item + finding
    expect("G154 a bypass with no ruling and no restart reads FOUND", verdict(route_register(6, 0, 0) + item + finding) == "FOUND")
    expect("G154 the ruling alone, nothing admitted, does not answer it", verdict(base) != "ANSWERED_BY_CHANGE")
    expect("G154 the ruling and one of two bypassed items admitted does not answer it", verdict(base + "x:SC a backlog:ScopeChange ; backlog:admitsItem x:I1 .\n") != "ANSWERED_BY_CHANGE")
    expect("G154 the ruling and every bypassed item admitted reads ANSWERED_BY_CHANGE", verdict(base + "x:SC a backlog:ScopeChange ; backlog:admitsItem x:I1 , x:I2 .\n") == "ANSWERED_BY_CHANGE")
# D1: the freeze lift is proved by the start gate's own probe
r = subprocess.run([sys.executable, latest("03-tooling/backlog_execution_ready_probe_v*.py")], capture_output=True, text=True, timeout=600)
expect("D1 the start gate lifts a freeze whose bypass a restart answered, and keeps an unanswered one (its own probe)", r.returncode == 0 and "Lin_FrozenAnswered" in r.stdout)
print("validator :", os.path.basename(val)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
