#!/usr/bin/env python3
"""backlog_date_plan_package_rank_probe v1.0.0 -- box 60, G246 (IPage handover of 2026-11-16, point 3): the date planner's --sequential order reads the roadmap rank of the package a mover belongs to.

Runs the newest backlog_date_plan on small registers planted with each case and reads what it prints. Cases: a story with no rank in a ranked package is ordered by the package's rank (the lower-ranked package's objective is forecast first, cumulative points show it); a story with a rank of its own keeps it over its package's; an epic mover with no rank and no package takes the rank of its stories' packages; a story with neither its own rank nor a ranked package still refuses, naming that the package was read too; a register without --sequential is unchanged. `--tool PATH` runs another copy (the mutation check); `--deps` lists the inputs."""
import os, re, sys, glob, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.join(HERE, "..")
def newest(folder, stem, ext):
    fs = glob.glob(os.path.join(PKG, folder, stem + "_v*." + ext))
    return sorted(fs, key=lambda f: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", f)[0]])[-1]
TOOL = newest("03-tooling", "backlog_date_plan", "py")
if sys.argv[1:2] == ["--deps"]: print(os.path.abspath(__file__)); print(TOOL); sys.exit(0)
if sys.argv[1:2] == ["--tool"]: TOOL = sys.argv[2]
NS = "http://example.org/other#"
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix o: <%s> .\n" % NS
BASE = 'o:Lin a backlog:Lineage .\no:Register a backlog:Register ; backlog:isRegisterRoot true .\n'
def boxes():
    out = ""
    for i in range(3):
        out += 'o:It%d a backlog:Iteration ; backlog:iterationStart "2026-11-0%dT08:00:00Z"^^xsd:dateTime .\n' % (i, i + 1)
        if i < 2: out += 'o:S%d a backlog:Story ; backlog:hasState backlog:Done ; backlog:hasEffort 4.0 .\no:P%d a backlog:PlanningEvent ; backlog:plansItem o:S%d ; backlog:plannedInto o:It%d .\n' % (i, i, i, i)
    return out
def pkg(n, rank=None): return 'o:%s a backlog:Package%s .\n' % (n, " ; backlog:hasRoadmapRank %d" % rank if rank is not None else "")
def story(n, eff=None, rank=None, pk=None, pursues=None, part=None):
    t = 'o:%s a backlog:Story ; backlog:hasState backlog:Proposed ;' % n
    if eff is not None: t += ' backlog:hasEffort %s ;' % eff
    if rank is not None: t += ' backlog:hasRoadmapRank %d ;' % rank
    if pk: t += ' backlog:memberOfContainer o:%s ;' % pk
    if pursues: t += ' backlog:pursuesObjective o:%s ;' % pursues
    if part: t += ' backlog:partOf o:%s ;' % part
    return t.rstrip(" ;") + " .\n"
def obj(name, movers):
    return 'o:Obj_%s a backlog:Objective ; backlog:belongsToLineage o:Lin ; backlog:hasCheckpoint o:CP_%s ; backlog:metricMovableBy %s .\no:CP_%s backlog:checkpointDate "2026-12-31T00:00:00Z"^^xsd:dateTime .\n' % (name, name, ", ".join(movers), name)
def run(ttl, *args):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "r.ttl"); open(f, "w").write(ttl)
        r = subprocess.run([sys.executable, TOOL, f, "predict", "--lineage", "Lin", "--prefix", "PD", "--now", "2026-11-10T00:00:00Z"] + list(args), capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr
def points(out, name):
    m = re.search(r"%s\s+([\d.]+) points" % name, out); return float(m.group(1)) if m else None
FAILS = []; N = [0]
def expect(what, ok):
    N[0] += 1
    if not ok: FAILS.append(what)
    print(("ok   " if ok else "FAIL ") + what)
R = HEAD + BASE + boxes()
# 1: package rank read; Y is in the package ranked first, so X waits for it (cumulative points)
t1 = R + pkg("PkA", 2) + pkg("PkB", 1) + story("A", 5.0, pk="PkA", pursues="Obj_X") + story("B", 3.0, pk="PkB", pursues="Obj_Y") + obj("X", ["o:A"]) + obj("Y", ["o:B"])
c, out = run(t1, "--sequential")
expect("1a stories with no rank in ranked packages are sequenced, not refused", c in (0, 1) and "needs a roadmap rank" not in out and "Traceback" not in out)
expect("1b the objective of the package ranked first is counted alone and the next after it", points(out, "Obj_Y") == 3.0 or points(out, "Y") == 3.0 or (re.search(r"Y\s+3\.0 points", out) is not None))
expect("1c the later package's objective carries the earlier one's points (8.0 cumulative)", re.search(r"X\s+8\.0 points", out) is not None)
# 2: own rank beats the package's
t2 = R + pkg("PkA", 5) + pkg("PkB", 6) + story("A", 5.0, rank=9, pk="PkA", pursues="Obj_X") + story("B", 3.0, rank=1, pk="PkB", pursues="Obj_Y") + obj("X", ["o:A"]) + obj("Y", ["o:B"])
c, out = run(t2, "--sequential")
expect("2 a story's own rank is kept over its package's (Y first, X cumulative 8.0)", re.search(r"Y\s+3\.0 points", out) is not None and re.search(r"X\s+8\.0 points", out) is not None)
# 3: epic mover takes the rank of its stories' packages
t3 = R + pkg("PkA", 2) + pkg("PkB", 1) + story("E") + story("A", 5.0, pk="PkA", part="E", pursues="Obj_X") + story("B", 3.0, pk="PkB", pursues="Obj_Y") + obj("X", ["o:E"]) + obj("Y", ["o:B"])
c, out = run(t3, "--sequential")
expect("3 an epic with no rank takes the rank of its stories' packages", c in (0, 1) and "needs a roadmap rank" not in out and re.search(r"X\s+8\.0 points", out) is not None)
# 4: no rank anywhere still refuses, and the message says the package was read
t4 = R + pkg("PkA") + story("A", 5.0, pk="PkA", pursues="Obj_X") + obj("X", ["o:A"])
c, out = run(t4, "--sequential")
expect("4 neither a rank of its own nor a ranked package refuses and says the package was read", c != 0 and "needs a roadmap rank" in out and "package" in out)
t5 = R + story("A", 5.0, pursues="Obj_X") + obj("X", ["o:A"])
c, out = run(t5, "--sequential")
expect("5 a story in no package and with no rank refuses", c != 0 and "needs a roadmap rank" in out)
# 6: without --sequential nothing changes
c, out = run(t1)
expect("6 without --sequential each objective is forecast alone (X 5.0, Y 3.0)", re.search(r"X\s+5\.0 points", out) is not None and re.search(r"Y\s+3\.0 points", out) is not None)
# 7: a story in two packages takes the lowest rank
t7 = R + pkg("PkA", 1) + pkg("PkC", 3) + pkg("PkB", 2) + story("A", 5.0, pursues="Obj_X") + 'o:A backlog:memberOfContainer o:PkA , o:PkC .\n' + story("B", 3.0, pk="PkB", pursues="Obj_Y") + obj("X", ["o:A"]) + obj("Y", ["o:B"])
c, out = run(t7, "--sequential")
expect("7 a story in two packages takes the lowest rank (X first alone 5.0, Y cumulative 8.0)", re.search(r"X\s+5\.0 points", out) is not None and re.search(r"Y\s+8\.0 points", out) is not None)
# 8: only a package's rank counts, not that of another kind of container
t8 = R + 'o:Sp a backlog:Iteration ; backlog:hasRoadmapRank 1 .\n' + story("A", 5.0, pk="Sp", pursues="Obj_X") + obj("X", ["o:A"])
c, out = run(t8, "--sequential")
expect("8 a rank on a container that is not a package is not read (still refuses)", c != 0 and "needs a roadmap rank" in out)
print("VERDICT: %s -- %d expectations %s" % ("PASS" if not FAILS else "FAIL", N[0], "hold" if not FAILS else "(%d failed)" % len(FAILS)))
sys.exit(1 if FAILS else 0)
