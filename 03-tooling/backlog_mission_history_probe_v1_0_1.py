#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe reads no record of the framework register; the validator keeps only the controlled individuals)
"""backlog_mission_history_probe v1.0.0 -- re-runnable proof of the mission-history and closure-anchor rules (shapes v1.170.0, G121).

  A mission is inside a lineage when a lineage pursues it or pursues a mission that replaced it, however long the chain; a mission outside both is refused.
  A replaced mission that still says it is in flight is reported; one that states no outcome, or a closure, is not.
  A closure report without its commit anchor is refused only for an adopter: a register (reports generated before ruleSetAdoptedAt are exempt) or a lineage
  (the reports of its own mission). Nothing is refused for a register that adopted nothing.
Exit 0 when every expectation holds, 1 otherwise.
"""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    for pat in ("03-tooling/backlog_validate_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl", "01-ontologies/backlog_abox_v*.ttl"):
        print(latest(pat))
    print(os.path.abspath(__file__)); sys.exit(0)
val = latest("03-tooling/backlog_validate_v*.py")
bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
DT = "^^<http://www.w3.org/2001/XMLSchema#dateTime>"
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/mh-probe#> .\n"
OUT, FLY, ANC = "pursued by no lineage and is not an earlier statement", "was replaced by another and still says it is in flight", "records no closureCommittedAt"
def M(n, extra=""): return f'x:{n} a backlog:Mission ; backlog:hasMissionStatement "s" ; backlog:decidedBy backlog:Owner {extra}.\n'
def LIN(n, m, extra=""): return f'x:{n} a backlog:Lineage ; backlog:lineageForMission x:{m} ; backlog:lineageOrdinal 1 {extra}.\n'
def CR(n, m, gen, anchor=False): return f'x:{n} a backlog:ClosureReport ; backlog:closesForMission x:{m} ; backlog:reportGeneratedAt "{gen}"{DT} ' + ('; backlog:closureCommittedAt "abc1234" ' if anchor else '') + '.\n'
def hits(out, key, node): return sum(1 for ln in out.splitlines() if key in ln and re.search(r"\b" + node + r"\b", ln))
def run(body):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(HEAD + body)
        return subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=900).stdout

# A: the register adopts both rule sets, closure reports generated before 2026-10-01 are exempt
A = ('x:Reg a backlog:Backlog ; backlog:isRegisterRoot true ; backlog:adoptsRuleSet backlog:RS_MissionHistory , backlog:RS_ClosureCommitAnchor ; backlog:ruleSetAdoptedAt "2026-10-01T00:00:00Z"' + DT + ' .\n'
     + M("Lone") + M("Pursued") + LIN("L_P", "Pursued")
     + M("C1") + M("C2", "; backlog:supersedesMission x:C1 ") + M("C3", "; backlog:supersedesMission x:C2 ") + LIN("L_C", "C3")
     + M("D1") + M("D2", "; backlog:supersedesMission x:D1 ") + M("D3", "; backlog:supersedesMission x:D2 ")
     + M("FlyOld", "; backlog:hasMissionOutcome backlog:Out_InFlight ") + M("FlyNew", "; backlog:supersedesMission x:FlyOld ") + LIN("L_F", "FlyNew")
     + M("AchOld", "; backlog:hasMissionOutcome backlog:Out_Achieved ; backlog:outcomeRationale \"done\" ") + M("AchNew", "; backlog:supersedesMission x:AchOld ") + LIN("L_A", "AchNew")
     + M("NoneOld") + M("NoneNew", "; backlog:supersedesMission x:NoneOld ") + LIN("L_N", "NoneNew")
     + CR("RepOld", "Pursued", "2026-09-01T00:00:00Z") + CR("RepNew", "Pursued", "2026-10-10T00:00:00Z") + CR("RepNewOk", "Pursued", "2026-10-10T00:00:00Z", True))
o = run(A)
expect("a mission no lineage pursues and nothing replaced is refused", hits(o, OUT, "Lone") == 1)
expect("a mission a lineage pursues is inside", hits(o, OUT, "Pursued") == 0)
expect("the earlier statements of a mission a lineage pursues are inside, however long the chain", all(hits(o, OUT, n) == 0 for n in ("C1", "C2", "C3")))
expect("a chain whose last statement no lineage pursues is outside, every link of it", all(hits(o, OUT, n) == 1 for n in ("D1", "D2", "D3")))
blk = re.split(r"\n\s+\d+ x \[", o[o.index(FLY):])[0] if FLY in o else ""
expect("a replaced mission that still says it is in flight is reported", "on: FlyOld" in blk)
expect("a replaced mission that states a closure is not reported", "on: AchOld" not in blk)
expect("a replaced mission that states no outcome is not reported", "on: NoneOld" not in o)
expect("a report generated before the adoption date needs no anchor", hits(o, ANC, "RepOld") == 0)
expect("a report generated after the adoption date and without an anchor is refused", hits(o, ANC, "RepNew") == 1)
expect("a report generated after the adoption date with its anchor is accepted", hits(o, ANC, "RepNewOk") == 0)
# B: nothing adopted -- nothing refused
o = run(M("Lone") + M("FlyOld", "; backlog:hasMissionOutcome backlog:Out_InFlight ") + M("FlyNew", "; backlog:supersedesMission x:FlyOld ") + CR("Rep", "Lone", "2026-10-10T00:00:00Z"))
expect("a register that adopted nothing is refused nothing (G89, G91)", OUT not in o and FLY not in o and ANC not in o)
# C: a lineage adopts the anchor for the reports of its own mission only
C = (M("MineM") + M("OtherM") + LIN("L_Mine", "MineM", "; backlog:adoptsRuleSet backlog:RS_ClosureCommitAnchor ") + LIN("L_Other", "OtherM", "")
     + CR("RepMine", "MineM", "2026-09-01T00:00:00Z") + CR("RepOther", "OtherM", "2026-09-01T00:00:00Z"))
o = run(C)
expect("a lineage that adopts the anchor binds the reports of its own mission", hits(o, ANC, "RepMine") == 1)
expect("and not the reports of a mission another lineage pursues", hits(o, ANC, "RepOther") == 0)
print("validator :", os.path.basename(val)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
