#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe reads no record of the framework register; it builds its own temporary repositories)
"""backlog_revival_opening_probe v1.0.0 -- proves the revival opening of Lineage 29 (order check v1.15.0).

A lineage that claims adoptionRecordedAtOpen may adopt a rule set only in the commit of its Mission output. A revived lineage
(lineageRevivedAt and a reactivation naming it) that rebuilds its chain by a StageRevision opens again at the commit where its
latest stage revision first appears, as a restart's rebuilt Mission commit does (G148 Q3). Each case is a temporary repository.
  1  an adoption in the stage revision's commit, lineage revived                    -> accepted (control)
  2  an adoption one commit after the stage revision, lineage revived               -> refused
  3  an adoption after the Mission commit, lineage NOT revived, with a revision      -> refused (no relief without revival)
  4  an adoption after the Mission commit, lineage revived, NO stage revision       -> refused (no relief without a rebuild)
  5  an adoption in the Mission commit, lineage revived with a revision             -> accepted (the old rule still holds)
Exit 0 when every expectation holds, 1 otherwise."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
chk = latest("03-tooling/backlog_lineage_order_check_v*.py")
if sys.argv[1:] == ["--deps"]:
    print(chk); print(os.path.abspath(__file__)); sys.exit(0)
B = "http://example.org/backlog#"; NS = "http://example.org/revival-probe#"
bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
def git(d, *a): return subprocess.run(["git", "-c", "user.email=p@p", "-c", "user.name=p", *a], cwd=d, capture_output=True, text=True, check=True).stdout
P = f"@prefix backlog: <{B}> .\n@prefix x: <{NS}> .\n"
def lineage(revived, adopt_at_mission):
    return ("x:L a backlog:Lineage ; backlog:lineageOrdinal 1 ; backlog:adoptionRecordedAtOpen true"
            + (" ; backlog:adoptsRuleSet backlog:RS_A" if adopt_at_mission else "")
            + (" ; backlog:lineageRevivedAt \"2026-11-03T00:00:00Z\"^^<http://www.w3.org/2001/XMLSchema#dateTime>" if revived else "") + " .\n"
            "x:O_M a backlog:StageOutput ; backlog:outputOfStage backlog:Stage_Mission ; backlog:belongsToLineage x:L ; backlog:closedAtCommit \"c\" ; backlog:hasStateDigest \"d\" .\n")
REACT = "x:R a backlog:LineageReactivation ; backlog:reactivatesLineage x:L .\n"
REV = "x:V a backlog:StageRevision ; backlog:revisesLineage x:L ; backlog:revisesFromStage backlog:Stage_Objective .\n"
LATE = "x:L backlog:adoptsRuleSet backlog:RS_B .\n"
def run(steps):
    with tempfile.TemporaryDirectory() as d:
        git(d, "init", "-q"); os.makedirs(os.path.join(d, "reg")); f = os.path.join(d, "reg", "register.ttl")
        for body, msg in steps:
            open(f, "w").write(P + body); git(d, "add", "-A"); git(d, "commit", "-q", "-m", msg)
        out = subprocess.run([sys.executable, chk, f], capture_output=True, text=True, timeout=300).stdout
        return sum(1 for ln in out.splitlines() if "claims adoptionRecordedAtOpen but adopts" in ln)
base = lineage(True, True) + REACT
CASES = [
 ("1 an adoption in the stage revision's commit, lineage revived (control)", [(base, "mission+react"), (base + REV + LATE, "revision with adoption")], 0),
 ("2 an adoption one commit after the stage revision", [(base, "mission+react"), (base + REV, "revision"), (base + REV + LATE, "late adoption")], 1),
 ("3 an adoption after the Mission commit, lineage not revived, with a revision", [(lineage(False, True), "mission"), (lineage(False, True) + REV + LATE, "revision with adoption")], 1),
 ("4 an adoption after the Mission commit, lineage revived, no stage revision", [(base, "mission+react"), (base + LATE, "late adoption")], 1),
 ("5 an adoption in the Mission commit, lineage revived with a revision (control)", [(base, "mission+react"), (base + REV, "revision")], 0),
]
for name, steps, want in CASES:
    got = run(steps)
    expect(f"{name}: expected {want}, got {got}", got == want)
print("order check:", os.path.basename(chk)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
