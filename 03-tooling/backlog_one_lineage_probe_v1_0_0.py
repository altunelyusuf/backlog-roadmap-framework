#!/usr/bin/env python3
"""backlog_one_lineage_probe v1.0.0 -- re-runnable proof of the one-lineage default (T-Box v1.151.0, shapes v1.183.0, G159).

  The Owner's rule of 2026-10-26: one lineage is active at a time; parallel lineages only when each is maintained by its own individual,
  project, program or portfolio (or when connected, G104); one urgency suspension at a time. Exit 0 when every expectation holds.
"""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    for pat in ("03-tooling/backlog_validate_v*.py", "03-tooling/backlog_execution_ready_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl", "01-ontologies/backlog_abox_v*.ttl"):
        print(latest(pat))
    print(os.path.abspath(__file__)); sys.exit(0)
val = latest("03-tooling/backlog_validate_v*.py"); gate = latest("03-tooling/backlog_execution_ready_v*.py")
bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
HEAD = ("@prefix backlog: <http://example.org/backlog#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/one-probe#> .\n"
        "x:Reg backlog:adoptsRuleSet backlog:RS_ConcurrentLineages .\n")
def lin(n, m=None, st="LS_InProgress"):
    return f"x:{n} a backlog:Lineage ; backlog:hasLineageStatus backlog:{st} " + (f"; backlog:maintainedBy x:{m} " if m else "") + ".\n"
def mt(n, kind): return f"x:{n} a backlog:LineageMaintainer ; backlog:maintainerKind backlog:{kind} .\n"
def urg(n, l, w=None):
    w = w or 'W' + n
    return (f'x:{n} a backlog:UrgentInterruption ; backlog:interruptsLineage x:{l} ; backlog:decidedBy backlog:Owner ; backlog:urgencyDeclaredAt "2026-10-26T10:00:00Z"^^xsd:dateTime ; '
                       f'backlog:urgencyReason "down" ; backlog:urgencyTimeBoxUntil "2099-01-01T00:00:00Z"^^xsd:dateTime ; backlog:urgentItem x:{w} .\nx:{w} a backlog:Defect ; backlog:hasState backlog:InProgress .\n')
SCEN = [
 ("two active lineages, no maintainers, unconnected", lin("A") + lin("B"), 1, "nothing connects them"),
 ("two active lineages with the same maintainer", mt("P1", "Mk_Project") + lin("A", "P1") + lin("B", "P1"), 1, "nothing connects them"),
 ("two active lineages with different maintainers (control)", mt("P1", "Mk_Project") + mt("P2", "Mk_Program") + lin("A", "P1") + lin("B", "P2"), 0, "nothing connects them"),
 ("only one of two names a maintainer", mt("P1", "Mk_Individual") + lin("A", "P1") + lin("B"), 1, "nothing connects them"),
 ("a queued lineage beside a running one (control)", lin("A") + lin("B", st="LS_Opened"), 0, "nothing connects them"),
 ("a lineage that declines its profile and adopts no rule", "x:C a backlog:Lineage ; backlog:profileDeclinedReason \"scratch\" .\n", 1, "declines an opening profile"),
 ("a lineage that declines its profile but adopts the rule (control)", "x:C a backlog:Lineage ; backlog:profileDeclinedReason \"scratch\" ; backlog:adoptsRuleSet backlog:RS_ConcurrentLineages .\n", 0, "declines an opening profile"),
 ("two open interruptions on unmaintained lineages", lin("A") + lin("B") + urg("U1", "A") + urg("U2", "B"), 1, "another urgent interruption is open"),
 ("two open interruptions on lineages with different maintainers (control)", mt("P1", "Mk_Project") + mt("P2", "Mk_Portfolio") + lin("A", "P1") + lin("B", "P2") + urg("U1", "A") + urg("U2", "B"), 0, "another urgent interruption is open"),
]
with tempfile.TemporaryDirectory() as d:
    for name, body, want, key in SCEN:
        f = os.path.join(d, "s.ttl"); head = HEAD.replace("x:Reg backlog:adoptsRuleSet backlog:RS_ConcurrentLineages .\n", "") if "declines" in key and "but adopts" not in name else HEAD
        open(f, "w").write(head + body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=900).stdout
        got = sum(1 for ln in out.splitlines() if "[Violation]" in ln and key in ln)
        expect(f"{name}: expected {want}, got {got}", got == want if want else got == 0)
    # the start gate
    for name, body, ok in (("start gate refuses a lineage running beside an unconnected one", lin("A") + lin("B"), False),
                           ("start gate lets differently maintained lineages run", mt("P1", "Mk_Project") + mt("P2", "Mk_Program") + lin("A", "P1") + lin("B", "P2"), True)):
        f = os.path.join(d, "g.ttl"); open(f, "w").write(HEAD + body)
        out = subprocess.run([sys.executable, gate, f, "--lineage", "B"], capture_output=True, text=True).stdout
        fail = "FAIL  no other lineage is active" in out
        expect(name, (not fail) if ok else fail)
print("validator :", os.path.basename(val)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
