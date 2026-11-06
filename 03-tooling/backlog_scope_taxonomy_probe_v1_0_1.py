#!/usr/bin/env python3
"""backlog_scope_taxonomy_probe v1.0.0 -- the scope taxonomy is a tree whose areas and exclusions are answered (G200; Lineage 29, story TaxonomyLink).
Part A, scratch register, real validator and real shapes, judged by name (SI_NOANSWER, PI_BADPARENT):
  a lineage that adopts RS_ScopeItemsAnswered and has reached the Goal stage: an area or an exclusion with no goal is refused, with a goal is not, under a parent of its own kind is not;
  a lineage that is not yet at the Goal stage, or did not adopt the rule set: not refused; a parent of another kind, or itself, is refused wherever it stands.
Part B, a copy of the newest real register in which Lineage 29 adopts the rule set: the register as it is raises no refusal (every area and exclusion of Lineage 29 is answered),
an area planted in its scope with no goal is refused by name, with a goal is not, and the same area in a lineage that did not adopt is not.
Exit 0 when every expectation holds, 1 otherwise."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
VAL, REG = latest("03-tooling/backlog_validate_v*.py"), latest("01-ontologies/backlog_abox_v*.ttl")
if sys.argv[1:] == ["--deps"]:
    for pat in ("03-tooling/backlog_validate_v*.py", "01-ontologies/backlog_abox_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl", "02-shacl-safeguards/backlog_shacl_v*.ttl"): print(latest(pat))
    print(os.path.abspath(__file__)); sys.exit(0)
KEYS = "SI_NOANSWER\x1ePI_BADPARENT"
def judge(data, name):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, name); open(f, "w", encoding="utf-8").write(data)
        env = dict(os.environ, BACKLOG_VALIDATE_ONLY_MESSAGE=KEYS); env.pop("BACKLOG_VALIDATE_MEMO_DIR", None)
        out = subprocess.run([sys.executable, VAL, f], capture_output=True, text=True, timeout=900, env=env).stdout
    return sorted(set((m.group(2), m.group(1)) for m in re.finditer(r"\[Violation\]\s+(\S+)\s+(SI_NOANSWER|PI_BADPARENT)", out)))
bad = []
def expect(n, ok):
    print(("PASS  " if ok else "FAIL  ") + n)
    if not ok: bad.append(n)
# ---- part A
PRE = "@prefix backlog: <http://example.org/backlog#> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> . @prefix ex: <http://example.org/sprobe#> .\n"
def lin(n, adopts=True, status="LS_Goaled"): return "ex:L%s a backlog:Lineage ; %s backlog:hasLineageStatus backlog:%s ; backlog:humanApprovalLevel 3 .\nex:S%s a backlog:ScopeStatement ; backlog:belongsToLineage ex:L%s ; %s .\n" % (n, "backlog:adoptsRuleSet backlog:RS_ScopeItemsAnswered ;" if adopts else "", status, n, n, "%s")
A = "a backlog:ScopeArea ; backlog:hasScopeLayer backlog:Layer_Work"; E = "a backlog:ScopeExclusion ; backlog:hasScopeLayer backlog:Layer_Work"
def scope(n, adopts=True, status="LS_Goaled", areas=(), excl=(), extra=""):
    link = " ; ".join(["backlog:coversArea ex:%s" % a for a in areas] + ["backlog:hasScopeExclusion ex:%s" % e for e in excl])
    return lin(n, adopts, status) % link + extra
cases = [
 ("AreaNoGoal",    scope("1", areas=["Ar1"]) + "ex:Ar1 %s .\n" % A, {"Ar1": "SI_NOANSWER"}),
 ("AreaGoal",      scope("2", areas=["Ar2"]) + "ex:Ar2 %s .\nex:G2 a backlog:Goal ; backlog:hasGoalFacing backlog:Facing_Scope ; backlog:goalCoversArea ex:Ar2 .\n" % A, {}),
 ("ExclNoGuard",   scope("3", excl=["Ex3"]) + "ex:Ex3 %s .\n" % E, {"Ex3": "SI_NOANSWER"}),
 ("ExclGuarded",   scope("4", excl=["Ex4"]) + "ex:Ex4 %s .\nex:G4 a backlog:Goal ; backlog:hasGoalFacing backlog:Facing_Exclusion ; backlog:guardsExclusion ex:Ex4 .\n" % E, {}),
 ("AreaUnderArea", scope("5", areas=["Ar5", "Ar5b"]) + "ex:Ar5 %s .\nex:Ar5b %s ; backlog:hasParentItem ex:Ar5 .\nex:G5 a backlog:Goal ; backlog:hasGoalFacing backlog:Facing_Scope ; backlog:goalCoversArea ex:Ar5 .\n" % (A, A), {}),
 ("NotGoaledYet",  scope("6", status="LS_Scoped", areas=["Ar6"]) + "ex:Ar6 %s .\n" % A, {}),
 ("NotAdopted",    scope("7", adopts=False, areas=["Ar7"]) + "ex:Ar7 %s .\n" % A, {}),
 ("ParentOtherKind", "ex:ArBad %s ; backlog:hasParentItem ex:DelBad .\nex:DelBad a backlog:ScopeDeliverable ; backlog:hasScopeLayer backlog:Layer_Product .\n" % A, {"ArBad": "PI_BADPARENT"}),
 ("ParentSelf",    "ex:ArSelf %s ; backlog:hasParentItem ex:ArSelf .\n" % A, {"ArSelf": "PI_BADPARENT"}),
 ("GoalUnderGoal", "ex:GKid a backlog:Goal ; backlog:hasParentItem ex:GTop .\nex:GTop a backlog:Goal .\n", {}),
]
got = judge(PRE + "".join(c[1] for c in cases), "s.ttl")
for n, _, want in cases:
    names = {k for k in re.findall(r"ex:(\w+) ", _) } if False else None
want_all = {}
for n, _, w in cases: want_all.update(w)
have = {a: b for b, a in got}
for n, _, w in cases:
    subj = list(w) or [x for x in re.findall(r"^ex:((?:Ar|Ex|G)\w+) ", _, re.M)]
    ok = all(have.get(s) == w[s] for s in w) and all(s not in have for s in subj if s not in w)
    expect("A %s: %s" % (n, ("refused as " + ", ".join(w.values())) if w else "not refused"), ok)
# ---- part B
text = open(REG, encoding="utf-8").read()
ADOPT = "\nfw:L_ImpedimentsKnown backlog:adoptsRuleSet backlog:RS_ScopeItemsAnswered .\n"
base = judge(text + ADOPT, os.path.basename(REG))
expect("B the real register with Lineage 29 adopting raises no refusal (%d)" % len(base), base == [])
PLANT = lambda g: "fw:Scope2_ImpedimentsKnown backlog:coversArea fw:Area_Planted .\nfw:Area_Planted a backlog:ScopeArea ; backlog:hasScopeLayer backlog:Layer_Work .\n" + (("fw:Goal_Planted a backlog:Goal ; backlog:hasGoalFacing backlog:Facing_Scope ; backlog:goalCoversArea fw:Area_Planted .\n") if g else "")
r = judge(text + ADOPT + PLANT(False), os.path.basename(REG))
expect("B an area planted in the scope of Lineage 29 with no goal is refused by name", r == [("SI_NOANSWER", "Area_Planted")])
expect("B the same area with a goal is not refused", judge(text + ADOPT + PLANT(True), os.path.basename(REG)) == [])
# the register now holds one live lineage and it adopted the rule set, so a lineage that did not adopt is planted
PLO = "fw:L_PlantedOther a backlog:Lineage .\nfw:Scope_PlantedOther a backlog:ScopeStatement ; backlog:belongsToLineage fw:L_PlantedOther .\n"
other = PLO + "fw:Scope_PlantedOther backlog:coversArea fw:Area_PlantedOut .\nfw:Area_PlantedOut a backlog:ScopeArea ; backlog:hasScopeLayer backlog:Layer_Work .\n"
expect("B the same area in the scope of a planted lineage that did not adopt is not refused", judge(text + ADOPT + other, os.path.basename(REG)) == [])
print("register:", os.path.basename(REG)); print("VERDICT   :", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
