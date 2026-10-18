#!/usr/bin/env python3
"""backlog_order_revision_probe v1.0.0 -- a stage revision from the Backlog stage reads as ordered in the order check (G130).

A planted lineage on a witness map (no git): old Backlog output O1 at commit c3, items admitted by it at c4, then a StageRevision retracts O1, the rebuilt output O2 appears at c6.
  1 items first seen after O1, admitted by O2, revision recorded: ORDERED
  2 a new item added after the retraction and before O2, admitted by O2: ORDERED
  3 an item first seen BEFORE O1 (never in the chain): still BYPASS
  4 O1 flagged retracted but no StageRevision names it: BYPASS (the record is verified, not trusted)
  5 an item after O1 that O2 does not admit: BYPASS
Exit 0 when every expectation holds, 1 otherwise."""
import glob, json, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(latest("03-tooling/backlog_lineage_order_check_v*.py")); print(os.path.abspath(__file__)); sys.exit(0)
CHK = latest("03-tooling/backlog_lineage_order_check_v*.py")
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix ex: <http://example.org/orp#> .\n"
OUT = lambda n, st, c, cons, extra="": 'ex:%s a backlog:StageOutput ; backlog:outputOfStage backlog:Stage_%s ; backlog:belongsToLineage ex:L ; backlog:closedAtCommit "%s" ; backlog:hasStateDigest "d%s" %s%s .\n' % (n, st, c, n, ("; backlog:consumesOutput ex:%s " % cons) if cons else "", extra)
def register(items, record=True, retract=True):
    t = HEAD + "ex:L a backlog:Lineage ; backlog:lineageArchived false .\nex:M a backlog:Mission ; backlog:belongsToLineage ex:L .\n"
    t += OUT("OM", "Mission", "c1", "") + OUT("OS", "Scope", "c1b", "OM") + OUT("OG", "Goal", "c2", "OS") + OUT("OO", "Objective", "c2b", "OG")
    t += OUT("O1", "Backlog", "c3", "OO", "; backlog:outputRetracted true" if retract else "") + OUT("O2", "Backlog", "c6", "OO")
    if record:
        t += "ex:Rev a backlog:StageRevision ; backlog:revisesLineage ex:L ; backlog:revisesFromStage backlog:Stage_Backlog ; backlog:retractsOutput ex:O1 ; backlog:revisionReason \"Two pieces of work.\" ; backlog:revisedAtCommit \"c5\" .\n"
    for n, adm in items:
        t += 'ex:%s a backlog:Story ; backlog:hasIdentifier "%s" ; backlog:hasState backlog:Done ; backlog:belongsToLineage ex:L ; backlog:admittedByOutput ex:%s .\n' % (n, n, adm)
    return t
W = {"L": ["c0", 100], "M": ["c1", 110], "OM": ["c1", 110], "OS": ["c1b", 115], "OG": ["c2", 120], "OO": ["c2b", 125], "O1": ["c3", 130], "O2": ["c6", 160],
     "Rev": ["c5", 150], "Old": ["c4", 140], "New": ["c5b", 155], "Pre": ["c0", 100], "Odd": ["c4", 140]}
bad = []
def verdict(name, text, want):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "r.ttl"); open(f, "w").write(text); w = os.path.join(d, "w.json"); json.dump(W, open(w, "w"))
        out = subprocess.run([sys.executable, CHK, f, "--witness", w], capture_output=True, text=True).stdout
    got = "BYPASS" if "BYPASS" in out else ("ORDERED" if "ORDERED" in out else "OTHER")
    ok = got == want
    print(("PASS  " if ok else "FAIL  ") + "%s (%s)" % (name, got))
    if not ok: bad.append(name)
verdict("1 items admitted by the rebuilt output, revision recorded", register([("Old", "O2")]), "ORDERED")
verdict("2 a new item added after the retraction, admitted by the rebuilt output", register([("Old", "O2"), ("New", "O2")]), "ORDERED")
verdict("3 an item first seen before the first Backlog output is still a bypass", register([("Pre", "O2")]), "BYPASS")
verdict("4 flagged retracted with no StageRevision naming it: still a bypass", register([("Old", "O2")], record=False), "BYPASS")
verdict("5 an item the rebuilt output does not admit: still a bypass", register([("Odd", "O1")]), "BYPASS")
print("VERDICT: %s" % ("PASS -- 5 expectations hold" if not bad else "FAIL -- " + "; ".join(bad)))
sys.exit(1 if bad else 0)
