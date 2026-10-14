#!/usr/bin/env python3
"""backlog_scope_order_probe v1.0.0 -- re-runnable proof that no shape judges the ORDER of two stages from the text of two commit names (G114).

A scope output closed at commit 1111111 and a backlog output closed at 2222222, in the correct order (Scope first) and belonging to no common lineage, with two scope
statements that require a deliverable. Until v1.392.0 ScopeContentLateShape fired on both: it compared the two names with !=, which is true whenever they differ, and
tied neither output to the statement's lineage. A hash cannot be ordered without the git history, which only backlog_lineage_order_check reads.
  expected: no message that says the scope stage records a later commit than the backlog stage, with names that differ (1111111 / 2222222) and with names that coincide (aaaaaaa / aaaaaaa).
Exit 0 when no such message appears, 1 otherwise.
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
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/scope-order-probe#> .\n"
def graph(cs, cb):
    return (HEAD + "x:S1 a backlog:ScopeStatement ; backlog:requiresDeliverable x:D1 .\nx:S2 a backlog:ScopeStatement ; backlog:requiresDeliverable x:D1 .\nx:D1 a backlog:ScopeDeliverable .\n"
            f'x:O1 a backlog:StageOutput ; backlog:outputOfStage backlog:Stage_Scope ; backlog:closedAtCommit "{cs}" .\n'
            f'x:O2 a backlog:StageOutput ; backlog:outputOfStage backlog:Stage_Backlog ; backlog:closedAtCommit "{cb}" .\n')
bad = []
with tempfile.TemporaryDirectory() as d:
    for name, (cs, cb) in {"names differ, correct order": ("1111111", "2222222"), "names coincide": ("aaaaaaa", "aaaaaaa")}.items():
        f = os.path.join(d, "s.ttl"); open(f, "w").write(graph(cs, cb))
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=600).stdout
        got = sum(1 for ln in out.splitlines() if "scope stage records a later commit" in ln)
        print(f"{name:34} expected 0 got {got}")
        if got: bad.append(f"{name}: {got} message(s)")
print("validator :", os.path.basename(val)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
