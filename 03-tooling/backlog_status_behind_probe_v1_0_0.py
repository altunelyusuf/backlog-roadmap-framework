#!/usr/bin/env python3
"""backlog_status_behind_probe v1.0.0 -- a lineage whose status is behind its chain is refused (Lineage 23, D1).

Plants a lineage that adopts the lineage-status rule set, states LS_Scoped, and has an active Goal output: the validator must refuse it. The same lineage stating LS_Goaled, one whose
Goal output is retracted, and one stating LS_InProgress are not refused. Exit 0 when every expectation holds."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
VAL = latest("03-tooling/backlog_validate_v*.py")
if sys.argv[1:] == ["--deps"]:
    print("\n".join([VAL, latest("02-shacl-safeguards/backlog_shacl_v*.ttl"), latest("01-ontologies/backlog_tbox_v*.ttl"), os.path.abspath(__file__)])); sys.exit(0)
bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/sb#> .\nx:M a backlog:Mission .\n"
def lineage(status, retracted=False):
    return HEAD + "x:L a backlog:Lineage ; backlog:lineageOrdinal 1 ; backlog:lineageArchived false ; backlog:lineageForMission x:M ; backlog:adoptsRuleSet backlog:RS_LineageStatus ; backlog:hasLineageStatus backlog:%s .\n" % status \
        + "x:O a backlog:StageOutput ; backlog:outputOfStage backlog:Stage_Goal ; backlog:belongsToLineage x:L ; backlog:closedAtCommit \"c\" ; backlog:hasStateDigest \"d\" %s.\n" % ("; backlog:outputRetracted true " if retracted else "")
def refused(ttl):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(ttl)
        out = subprocess.run([sys.executable, VAL, f], capture_output=True, text=True, timeout=900).stdout
    return any("[Violation]" in ln and "behind its chain" in ln for ln in out.splitlines())
expect("a lineage stating LS_Scoped with an active Goal output is refused", refused(lineage("LS_Scoped")))
expect("the same lineage stating LS_Goaled is not refused", not refused(lineage("LS_Goaled")))
expect("a lineage stating LS_Scoped whose Goal output is retracted is not refused", not refused(lineage("LS_Scoped", True)))
expect("a lineage stating LS_InProgress is not refused", not refused(lineage("LS_InProgress")))
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
