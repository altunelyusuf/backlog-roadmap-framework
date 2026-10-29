#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe reads no record of the framework register; the validator keeps only the controlled individuals)
"""backlog_agent_accountability_probe v1.0.0 -- re-runnable proof of RS_AgentAccountability (T-Box v1.133.0, shapes v1.168.0, G118).

  Each shape of the rule set fires on its planted case and is silent on its control; the item-level shapes bind only an adopter (a lineage), and an item outside it is not judged.
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
val = sorted(glob.glob(os.path.join(HERE, "backlog_validate_v*.py")), key=sv)[-1]
bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)

T = "2026-10-15T08:00:00Z"
HEAD = ("@prefix backlog: <http://example.org/backlog#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/acc-probe#> .\n"
        "x:L a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_AgentAccountability ; backlog:humanApprovalLevel 3 .\n"
        "x:H a backlog:Executor_IndividualHuman .\n"
        "x:DefA a backlog:Executor_SingleAgent .\nx:DefB a backlog:Executor_SingleAgent .\nx:DefC a backlog:Executor_SingleAgent .\nx:DefD a backlog:Executor_SingleAgent .\n"
        "x:DefT a backlog:Executor_AgentTeam ; backlog:hasController x:H ; backlog:hasExecutorMember x:DefA .\n")
def run(n, d, kind="backlog:Executor_SingleAgent", extra=""):
    return f'x:{n} a backlog:ExecutorInstance , {kind} ; backlog:instanceOf x:{d} ; backlog:instantiatedFromVersion "1.0.0" ; backlog:instantiatedAt "{T}"^^xsd:dateTime {extra}.\n'
RUNS = run("RA","DefA") + run("RB","DefB") + run("RC","DefC") + run("RD","DefD") + run("RA2","DefA")
def item(state="Done", resp="RA", ov="RB", ver="RC", app="RD", lvl=2, lin=True, extra=""):
    parts = [f"x:W a backlog:Task ; backlog:hasState backlog:{state}"]
    if lin: parts.append("backlog:belongsToLineage x:L")
    for k, v in (("responsible", resp), ("overseenBy", ov), ("verifiedBy", ver), ("approvedBy", app)):
        if v: parts.append(f"backlog:{k} x:{v}")
    if lvl is not None: parts.append(f"backlog:integrityLevel {lvl}")
    return " ; ".join(parts) + extra + " .\n"
KEYS = {
 "DEF": "as a standing definition, not as a run", "ANON": "names no transitionedByExecutor", "MDEF": "named as a standing definition and not as a run",
 "SAME": "are the same party, one contains the other", "UNACC": "lacks overseenBy, verifiedBy or approvedBy", "HUMAN": "no person or human team approved it",
 "ASM": "no TeamAssembly records that it was built", "DELEG": "was not spawned by the executor responsible", "KIND": "is not of the kind of its definition",
 "CLOCK": "retired before it was instantiated", "UNSEAT": "is not a run, or holds no seat", "SEATIND": "held by a run of the same definition",
 "NOWORK": "has no seat that does the work", "INSTBARE": "names the definition it is a run of"}
def asm(seats, team="RT", members=True):
    t = run("RT", "DefT", "backlog:Executor_AgentTeam", "; backlog:hasExecutorMember x:RA ")
    a = f"x:AS a backlog:TeamAssembly ; backlog:assemblesTeam x:{team} ; backlog:assembledFor x:W ; backlog:assembledAt \"{T}\"^^xsd:dateTime ; backlog:assembledBy x:H ; backlog:hasSeat " + " , ".join(f"x:S{i}" for i in range(len(seats))) + " .\n"
    for i, (fn, h) in enumerate(seats):
        a += f"x:S{i} a backlog:Seat ; backlog:seatFunction backlog:{fn}" + (f" ; backlog:heldBy x:{h}" if h else "") + " .\n"
    return t + a
OK = RUNS + item()
SCEN = [
 ("clean: four different definitions, level below the human level", OK, {}),
 ("a definition named as responsible", RUNS + item(resp="DefA"), {"DEF": 1}),
 ("a person responsible (control)", RUNS + item(resp="H"), {"DEF": 0}),
 ("an item outside the adopting lineage is not judged", RUNS + item(resp="DefA", lin=False), {"DEF": 0}),
 ("two runs of one definition do and verify", RUNS + item(ver="RA2"), {"SAME": 1}),
 ("the same run does and verifies", RUNS + item(ver="RA"), {"SAME": 1}),
 ("Done without approval", RUNS + item(app=None), {"UNACC": 1}),
 ("not Done without approval (control)", RUNS + item(state="InProgress", app=None), {"UNACC": 0}),
 ("level 4 approved by an agent run", RUNS + item(lvl=4), {"HUMAN": 1}),
 ("level 4 approved by a person", RUNS + item(lvl=4, app="H"), {"HUMAN": 0}),
 ("Done with no integrity level", RUNS + item(lvl=None), {"HUMAN": 1}),
 ("an agent team run named with no assembly", RUNS + run("RT","DefT","backlog:Executor_AgentTeam") + item(resp="RT"), {"ASM": 1}),
 ("an agent team run named with its assembly", RUNS + asm([("Seat_Does","RA"),("Seat_Verifies","RC")]) + item(resp="RT"), {"ASM": 0, "UNSEAT": 0, "NOWORK": 0, "SEATIND": 0}),
 ("a move with no maker", RUNS + item(extra=""), {"ANON": 0}),
 ("a recorded move with no maker", RUNS + item() + "x:E a backlog:TransitionEvent ; backlog:transitionedItem x:W .\n", {"ANON": 1}),
 ("a recorded move by a person", RUNS + item() + "x:E a backlog:TransitionEvent ; backlog:transitionedItem x:W ; backlog:transitionedByExecutor x:H .\n", {"ANON": 0, "MDEF": 0}),
 ("a recorded move by a definition", RUNS + item() + "x:E a backlog:TransitionEvent ; backlog:transitionedItem x:W ; backlog:transitionedByExecutor x:DefA .\n", {"MDEF": 1}),
 ("a recorded move by a run", RUNS + item() + "x:E a backlog:TransitionEvent ; backlog:transitionedItem x:W ; backlog:transitionedByExecutor x:RA .\n", {"ANON": 0, "MDEF": 0}),
 ("a lineage delegated and spawned by the responsible run", RUNS + item() + "x:W backlog:delegatedLineage x:L2 .\nx:L2 a backlog:Lineage ; backlog:spawnedBy x:RA .\n", {"DELEG": 0}),
 ("a lineage delegated and spawned by another run", RUNS + item() + "x:W backlog:delegatedLineage x:L2 .\nx:L2 a backlog:Lineage ; backlog:spawnedBy x:RB .\n", {"DELEG": 1}),
 ("a single-agent definition run as a team", RUNS + run("RX","DefA","backlog:Executor_AgentTeam"), {"KIND": 1}),
 ("a run of a run", RUNS + run("RY","RA"), {"KIND": 1}),
 ("a run retired before it began", RUNS + run("RZ","DefB",extra='; backlog:retiredAt "2026-10-14T08:00:00Z"^^xsd:dateTime '), {"CLOCK": 1}),
 ("a bare run", RUNS + "x:RB2 a backlog:ExecutorInstance , backlog:Executor_SingleAgent .\n", {"INSTBARE": 1}),
 ("an agent member without a seat", RUNS + asm([("Seat_Does","RB")]), {"UNSEAT": 1}),
 ("a verifying seat held by a run of the doing definition", RUNS + asm([("Seat_Does","RA"),("Seat_Verifies","RA2")]), {"SEATIND": 1}),
 ("an assembly with no seat that does the work", RUNS + asm([("Seat_Verifies","RC"),("Seat_Does",None)]) .replace("x:S1 a backlog:Seat ; backlog:seatFunction backlog:Seat_Does","x:S1 a backlog:Seat ; backlog:seatFunction backlog:Seat_Reviews"), {"NOWORK": 1}),
]
with tempfile.TemporaryDirectory() as d:
    for name, body, want in SCEN:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(HEAD + body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=900).stdout
        for k, n in want.items():
            got = sum(1 for ln in out.splitlines() if "[Violation]" in ln and KEYS[k] in ln)
            expect(f"{name} [{k}]: expected {n}, got {got}", got == n)
print("validator :", os.path.basename(val)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
