#!/usr/bin/env python3
"""backlog_urgent_seed_probe v1.0.0 -- the seed item of an urgent interruption reads as ordered in the order check (Owner ruling G218).

A planted lineage on a witness map (no git): chain Mission c1 .. Backlog c3, and one item the lineage's chain did not exist for when it was recorded.
  1 the item is named by an interruption of ANOTHER lineage and first appears with it (same instant), before the chain: ORDERED
  2 the item first appears BEFORE that interruption: BYPASS
  3 the item is named by no interruption: BYPASS
  4 the interruption interrupts the item's OWN lineage: BYPASS (an interruption does not excuse work inside the lineage it pauses)
  and two mutants of the checker, each caught: the own-lineage test is dropped (case 4 fails), the instant test is dropped (case 2 fails)
Exit 0 when every expectation holds, 1 otherwise."""
import glob, json, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(latest("03-tooling/backlog_lineage_order_check_v*.py")); print(os.path.abspath(__file__)); sys.exit(0)
CHK = latest("03-tooling/backlog_lineage_order_check_v*.py")
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix ex: <http://example.org/usp#> .\n"
OUT = lambda n, st, c, cons: 'ex:%s a backlog:StageOutput ; backlog:outputOfStage backlog:Stage_%s ; backlog:belongsToLineage ex:L ; backlog:closedAtCommit "%s" ; backlog:hasStateDigest "d%s" .\n' % (n, st, c, n)
def register(named=True, own=False):
    t = HEAD + "ex:L a backlog:Lineage ; backlog:lineageArchived false .\nex:Other a backlog:Lineage ; backlog:lineageArchived false .\nex:M a backlog:Mission ; backlog:belongsToLineage ex:L .\n"
    t += OUT("OM", "Mission", "c1", "") + OUT("OS", "Scope", "c1b", "") + OUT("OG", "Goal", "c2", "") + OUT("OO", "Objective", "c2b", "") + OUT("OB", "Backlog", "c3", "")
    t += 'ex:Seed a backlog:Story ; backlog:hasIdentifier "Seed" ; backlog:hasState backlog:Backlog ; backlog:belongsToLineage ex:L .\n'
    if named:
        t += 'ex:U a backlog:UrgentInterruption ; backlog:interruptsLineage ex:%s ; backlog:urgentItem ex:Seed .\n' % ("L" if own else "Other")
    return t
W = {"L": ["c0", 90], "Other": ["c0", 90], "M": ["c1", 110], "OM": ["c1", 110], "OS": ["c1b", 115], "OG": ["c2", 120], "OO": ["c2b", 125], "OB": ["c3", 130], "U": ["c05", 95], "Seed": ["c05", 95]}
bad = []
def run(chk, text, w=W):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "r.ttl"); open(f, "w").write(text); wf = os.path.join(d, "w.json"); json.dump(w, open(wf, "w"))
        out = subprocess.run([sys.executable, chk, f, "--witness", wf], capture_output=True, text=True).stdout
    return "BYPASS" if "BYPASS" in out else ("ORDERED" if "ORDERED" in out else "OTHER")
W_EARLY = dict(W, Seed=["c04", 92])
CASES = {1: (register(), W, "ORDERED"), 2: (register(), W_EARLY, "BYPASS"), 3: (register(named=False), W, "BYPASS"), 4: (register(own=True), W, "BYPASS")}
NAMES = {1: "the seed of an interruption of another lineage, recorded with it, reads ordered", 2: "a seed that first appeared before the interruption is a bypass",
         3: "an item no interruption names is a bypass", 4: "an interruption of the item's own lineage excuses nothing"}
for k, (t, w, want) in CASES.items():
    got = run(CHK, t, w); ok = got == want; print(("PASS  " if ok else "FAIL  ") + "%d %s (%s)" % (k, NAMES[k], got))
    if not ok: bad.append(k)
SRC = open(CHK).read()
MUT = {"A: the own-lineage test is dropped": ("if (u, B.interruptsLineage, L) not in g]", "]", [4]),
       "B: the instant test is dropped": ("if any(x and item_first[ln][1] >= x[1] for x in uf):", "if any(x for x in uf):", [2])}
for name, (old, new, cases) in MUT.items():
    assert SRC.count(old) == 1, name
    with tempfile.TemporaryDirectory() as d:
        m = os.path.join(d, "mut.py"); open(m, "w").write(SRC.replace(old, new))
        caught = [c for c in cases if run(m, CASES[c][0], CASES[c][1]) != CASES[c][2]]
    ok = caught == cases; print(("PASS  " if ok else "FAIL  ") + "mutant %s caught by cases %s" % (name, caught))
    if not ok: bad.append(name)
print("VERDICT: " + ("PASS" if not bad else "FAIL")); sys.exit(1 if bad else 0)
