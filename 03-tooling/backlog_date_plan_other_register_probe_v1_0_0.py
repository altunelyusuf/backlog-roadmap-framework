#!/usr/bin/env python3
"""backlog_date_plan_other_register_probe v1.0.0 -- Lineage 29, box 52 (G238; the date planner on a register of another package: OE P8 and P9, another registrant point 2, IPage item 4).

Runs the newest backlog_date_plan on small registers planted with each case, in a namespace of their own that declares no `fw:` prefix, and reads what it prints and writes. Cases: a register with no `fw:` prefix is forecast in
its own namespace and linked to its own root; a decomposed mover (an epic with no effort) counts the open effort of its stories once; zero points while an open item that pursues the objective carries no effort is refused, never printed;
a register with no pair of boxes names --pace-from, and with --pace-from it is forecast and says the pace is borrowed; --sequential adds the points of the objectives in roadmap order; a wrong --effort key says which form is expected;
a register with a time without a zone still forecasts; and a register that declares `fw:` prints what it always printed. `--tool PATH` runs another copy (the mutation check); `--deps` lists the inputs.
"""
import os, re, sys, glob, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.join(HERE, "..")
def newest(folder, stem, ext):
    fs = glob.glob(os.path.join(PKG, folder, stem + "_v*." + ext))
    return sorted(fs, key=lambda f: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", f)[0]])[-1]
TOOL = newest("03-tooling", "backlog_date_plan", "py")
if sys.argv[1:2] == ["--deps"]: print(TOOL); sys.exit(0)
if sys.argv[1:2] == ["--tool"]: TOOL = sys.argv[2]
NS = "http://example.org/other#"
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix o: <%s> .\n" % NS
def boxes(n=3, zone=True):
    z = "Z" if zone else ""; out = ""
    for i in range(n):
        out += 'o:It%d a backlog:Iteration ; backlog:iterationStart "2026-11-0%dT08:00:00%s"^^xsd:dateTime .\n' % (i, i + 1, z)
        if i < n - 1:
            out += 'o:S%d a backlog:Story ; backlog:hasState backlog:Done ; backlog:hasEffort 4.0 .\no:P%d a backlog:PlanningEvent ; backlog:plansItem o:S%d ; backlog:plannedInto o:It%d .\n' % (i, i, i, i)
    return out
def obj(name, movers, rank=None, cp=True):
    t = 'o:Obj_%s a backlog:Objective ; backlog:belongsToLineage o:Lin ;' % name
    if cp: t += ' backlog:hasCheckpoint o:CP_%s ;' % name
    t += ' backlog:metricMovableBy %s .\n' % ", ".join(movers)
    if cp: t += 'o:CP_%s backlog:checkpointDate "2026-12-31T00:00:00Z"^^xsd:dateTime .\n' % name
    return t
BASE = 'o:Lin a backlog:Lineage .\no:Register a backlog:Register ; backlog:isRegisterRoot true .\n'
def story(n, eff=None, rank=None, state="Proposed", pursues=None, part=None):
    t = 'o:%s a backlog:Story ; backlog:hasState backlog:%s ;' % (n, state)
    if eff is not None: t += ' backlog:hasEffort %s ;' % eff
    if rank is not None: t += ' backlog:hasRoadmapRank %d ;' % rank
    if pursues: t += ' backlog:pursuesObjective o:%s ;' % pursues
    if part: t += ' backlog:partOf o:%s ;' % part
    return t.rstrip(" ;") + " .\n"
def run(ttl, *args, emit=False):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "r.ttl"); open(f, "w").write(ttl); em = os.path.join(d, "e.ttl")
        a = [sys.executable, TOOL, f, "predict", "--lineage", "Lin", "--prefix", "PD", "--now", "2026-11-10T00:00:00Z"] + list(args) + (["--emit", em] if emit else [])
        r = subprocess.run(a, capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr, (open(em).read() if emit and os.path.exists(em) else "")
FAILS = []; N = [0]
def expect(what, ok):
    N[0] += 1
    if not ok: FAILS.append(what)
    print(("ok   " if ok else "FAIL ") + what)
pace = HEAD + BASE + boxes()
# 1 no fw prefix: forecast in its own namespace, linked to its own root
r1 = HEAD + BASE + boxes() + story("A", 5.0, 1, pursues="Obj_X") + obj("X", ["o:A"])
c, out, em = run(r1, emit=True)
expect("1a a register with no fw: prefix is forecast, not stopped", c in (0, 1) and "Traceback" not in out and "5.0 points" in out)
expect("1b the forecasts are written in the register's own namespace", ("@prefix fw: <%s>" % NS) in em)
expect("1c the forecast is linked to that register's own root", "backlog:forecastFor fw:Register" in em)
# 2 epic mover counts the open effort of its stories once
r2 = HEAD + BASE + boxes() + story("E") + story("C1", 3.0, 1, part="E", pursues="Obj_X") + story("C2", 2.0, 2, part="E", pursues="Obj_X") + story("C3", 9.0, 3, state="Done", part="E") + obj("X", ["o:E"])
c, out, em = run(r2)
expect("2a an epic with no effort counts the open effort of its stories (5.0), not zero and not the finished one", "5.0 points" in out and "0.0 points" not in out)
r2b = HEAD + BASE + boxes() + story("E") + story("C1", 3.0, 1, part="E", pursues="Obj_X") + 'o:E backlog:decomposesInto o:C1 .\n' + obj("X", ["o:E", "o:C1"])
c, out, em = run(r2b)
expect("2b a story reached twice is counted once", "3.0 points" in out and "6.0 points" not in out)
# 3 zero points while an open item pursues the objective is refused
r3 = HEAD + BASE + boxes() + story("Z", None, 1, pursues="Obj_X") + obj("X", ["o:Z"])
c, out, em = run(r3)
expect("3 an open mover with no effort and no stories under it is refused, never counted as zero", c == 1 and "ERROR" in out and "no effort" in out and "Traceback" not in out)
# 4 pace from another register
r4 = HEAD + BASE + story("A", 5.0, 1, pursues="Obj_X") + obj("X", ["o:A"])
c, out, em = run(r4)
expect("4a no pair of boxes names --pace-from", "ERROR" in out and "--pace-from" in out)
with tempfile.TemporaryDirectory() as d:
    pf = os.path.join(d, "pace.ttl"); open(pf, "w").write(pace)
    c, out, em = run(r4, "--pace-from", pf, emit=True)
    expect("4b with --pace-from the register is forecast", "5.0 points" in out and "Traceback" not in out)
    expect("4c the forecast says the pace is borrowed, not observed", "borrowed" in em)
# 5 sequential
r5 = HEAD + BASE + boxes() + story("A", 4.0, 1, pursues="Obj_X") + story("B", 6.0, 2, pursues="Obj_Y") + obj("X", ["o:A"]) + obj("Y", ["o:B"])
c, out, em = run(r5)
expect("5a without --sequential each objective is forecast alone", "6.0 points" in out and "10.0 points" not in out)
c, out, em = run(r5, "--sequential")
expect("5b with --sequential the later objective carries the earlier points (10.0)", "10.0 points" in out)
r5b = HEAD + BASE + boxes() + story("A", 4.0, None, pursues="Obj_X") + story("B", 6.0, 2, pursues="Obj_Y") + obj("X", ["o:A"]) + obj("Y", ["o:B"])
c, out, em = run(r5b, "--sequential")
expect("5c --sequential without a roadmap rank says so", c != 0 and "roadmap rank" in out and "Traceback" not in out)
# 6 effort key message
r6 = HEAD + BASE + boxes() + 'o:Obj_Y_Rules a backlog:Objective ; backlog:belongsToLineage o:Lin ; backlog:hasCheckpoint o:CP_Y .\no:CP_Y backlog:checkpointDate "2026-12-31T00:00:00Z"^^xsd:dateTime .\n'
c, out, em = run(r6, "--effort", "Obj_Y_Rules=3")
expect("6 a wrong --effort key says which form is expected", "ERROR" in out and "after its first underscore" in out)
# 7 a time without a zone
r7 = HEAD + BASE + boxes(zone=False) + story("A", 5.0, 1, pursues="Obj_X") + obj("X", ["o:A"])
c, out, em = run(r7)
expect("7 a time without a zone still forecasts", "5.0 points" in out and "Traceback" not in out)
# 9 an objective with no mover but an open item with no effort that pursues it is refused too
r9 = HEAD + BASE + boxes() + story("Z", None, 1, pursues="Obj_X") + 'o:Obj_X a backlog:Objective ; backlog:belongsToLineage o:Lin ; backlog:hasCheckpoint o:CP_X .\no:CP_X backlog:checkpointDate "2026-12-31T00:00:00Z"^^xsd:dateTime .\n'
c, out, em = run(r9)
expect("9 an objective with no mover and an open item with no effort that pursues it is refused, not printed as 0", c == 1 and "ERROR" in out and "0 points" in out)
# 10 --note does not replace the statement that the pace is borrowed, and the printed assumptions carry it
with tempfile.TemporaryDirectory() as d:
    pf = os.path.join(d, "pace.ttl"); open(pf, "w").write(pace)
    c, out, em = run(r4, "--pace-from", pf, "--note", "discussed with the Owner", emit=True)
    expect("10 --note keeps the statement that the pace is borrowed, in the emitted forecast and in what is printed", "borrowed" in em and "discussed with the Owner" in em and "borrowed" in out)
# 11 sequential is recorded in the forecast and a story shared by two objectives is counted once
r11 = HEAD + BASE + boxes() + story("A", 4.0, 1, pursues="Obj_X") + story("B", 6.0, 2, pursues="Obj_Y") + obj("X", ["o:A"]) + obj("Y", ["o:A", "o:B"])
c, out, em = run(r11, "--sequential", emit=True)
expect("11a with --sequential a story shared by two objectives is counted once (4 then 10, not 14)", "10.0 points" in out and "14.0 points" not in out)
expect("11b the forecast says its points are cumulative in roadmap order", "cumulative" in em)
# 12 the register's root is found by its marker, whatever its name
r12 = HEAD + BASE.replace("o:Register", "o:TheRoot") + boxes() + story("A", 5.0, 1, pursues="Obj_X") + obj("X", ["o:A"])
c, out, em = run(r12, emit=True)
expect("12 the forecast is linked to the register's root found by its marker, not assumed to be named Register", "backlog:forecastFor fw:TheRoot" in em)
# 13 an epic with one story that has no effort is refused, not undercounted
r13 = HEAD + BASE + boxes() + story("E") + story("C1", 3.0, 1, part="E", pursues="Obj_X") + story("C2", None, 2, part="E", pursues="Obj_X") + obj("X", ["o:E"])
c, out, em = run(r13)
expect("13 an epic with one open story that has no effort is refused, never undercounted", c == 1 and "ERROR" in out and "no effort" in out and "Traceback" not in out)
# 8 a register that declares fw: and has direct movers with effort prints what it always printed
FWNS = "http://example.org/own#"
r8 = "@prefix backlog: <http://example.org/backlog#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix fw: <%s> .\n" % FWNS + BASE.replace("o:", "fw:") + boxes().replace("o:", "fw:") + story("A", 3.0, 1, pursues="Obj_X").replace("o:", "fw:") + story("B", 2.0, 2, pursues="Obj_X").replace("o:", "fw:") + story("D", 1.0, 3, state="Done").replace("o:", "fw:") + obj("X", ["o:A", "o:B", "o:D"]).replace("o:", "fw:")
c, out, em = run(r8, emit=True)
expect("8 a register that declares fw: with direct movers prints 5.0 points and writes in the namespace it declares", "5.0 points" in out and ("@prefix fw: <%s>" % FWNS) in em and "fw:Fc_PD_X" in em)
print("VERDICT: %s -- %d expectations%s" % ("PASS" if not FAILS else "FAIL", N[0], " hold" if not FAILS else ": " + "; ".join(FAILS)))
sys.exit(1 if FAILS else 0)
