#!/usr/bin/env python3
"""backlog_urgency_probe v1.1.0 -- re-runnable proof of the urgent interruption (T-Box v1.150.0, shapes v1.182.0, G158).

  The Owner's rule of 2026-10-26: a lineage under an emergency is paused, not worked around. Each of the twelve constraints of
  UrgentInterruptionShape fires on its planted case and is silent on a control, and two lineages joined by an interruption count as
  connected under RS_ConcurrentLineages. Exit 0 when every expectation holds, 1 otherwise.
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
KEYS = {"INC": "is incomplete", "ORD": "out of order", "RUN": "not running", "GO": "still In Progress", "HELD": "is not Suspended",
        "BACK": "still Suspended", "UND": "neither Done nor Cancelled", "ASS": "no impact assessment", "BOX": "after its time box",
        "TWO": "another urgent interruption is open", "SCOPE": "also admitted", "FOREIGN": "does not belong", "L1": "nothing connects them"}
HEAD = ("@prefix backlog: <http://example.org/backlog#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/urg-probe#> .\n"
        "x:Owner1 a backlog:Owner .\n")
def lineage(n, status="LS_InProgress", extra=""):
    return f"x:{n} a backlog:Lineage ; backlog:hasLineageStatus backlog:{status} {extra}.\n"
def item(n, lin, state="InProgress"):
    return f"x:{n} a backlog:Story ; backlog:hasState backlog:{state} ; backlog:belongsToLineage x:{lin} .\n"
def urg(n="U", lin="L", extra="", box="2099-01-01T00:00:00Z", decl="2026-10-26T10:00:00Z", items=("UW",), hold=()):
    t = (f"x:{n} a backlog:UrgentInterruption ; backlog:interruptsLineage x:{lin} ; backlog:decidedBy backlog:Owner ; "
         f'backlog:urgencyDeclaredAt "{decl}"^^xsd:dateTime ; backlog:urgencyReason "service down" ; backlog:urgencyTimeBoxUntil "{box}"^^xsd:dateTime ')
    for i in items: t += f"; backlog:urgentItem x:{i} "
    for i in hold: t += f"; backlog:holdsItem x:{i} "
    return t + extra + ".\n"
BASE = lineage("L") + item("UW", "L", "InProgress")
SCEN = [
 ("incomplete interruption", "x:U a backlog:UrgentInterruption .\n", {"INC": 1}),
 ("complete open interruption (control)", BASE + urg(), {"INC": 0, "ORD": 0, "RUN": 0, "GO": 0, "HELD": 0, "TWO": 0, "BOX": 0}),
 ("time box before declaration", BASE + urg(box="2026-10-26T09:00:00Z"), {"ORD": 1}),
 ("resumed with no end", BASE + urg(extra='; backlog:urgencyResumedAt "2026-10-27T00:00:00Z"^^xsd:dateTime '), {"ORD": 1}),
 ("interrupts a queued lineage", lineage("L", "LS_Opened") + item("UW", "L") + urg(), {"RUN": 1}),
 ("interrupts a finished lineage", lineage("L", "LS_Achieved") + item("UW", "L") + urg(), {"RUN": 1}),
 ("a started item goes on during the pause", BASE + item("S1", "L") + urg(), {"GO": 1}),
 ("the started item is held and Suspended (control)", BASE + item("S1", "L", "Suspended") + urg(hold=("S1",)), {"GO": 0, "HELD": 0}),
 ("a held item moved on during the pause", BASE + item("S1", "L", "Done") + urg(hold=("S1",)), {"HELD": 1}),
 ("resumed, a held item still Suspended", BASE + item("S1", "L", "Suspended") + urg(hold=("S1",), extra='; backlog:urgencyResolvedAt "2026-10-26T12:00:00Z"^^xsd:dateTime ; backlog:urgencyResumedAt "2026-10-26T13:00:00Z"^^xsd:dateTime '), {"BACK": 1}),
 ("ended with the urgent item still open", BASE + urg(extra='; backlog:urgencyResolvedAt "2026-10-26T12:00:00Z"^^xsd:dateTime '), {"UND": 1}),
 ("ended with the urgent item Done (control)", lineage("L") + item("UW", "L", "Done") + urg(extra='; backlog:urgencyResolvedAt "2026-10-26T12:00:00Z"^^xsd:dateTime '), {"UND": 0}),
 ("resumed with no impact assessment", lineage("L") + item("UW", "L", "Done") + urg(extra='; backlog:urgencyResolvedAt "2026-10-26T12:00:00Z"^^xsd:dateTime ; backlog:urgencyResumedAt "2026-10-26T13:00:00Z"^^xsd:dateTime '), {"ASS": 1}),
 ("resumed with the assessment (control)", lineage("L") + item("UW", "L", "Done") + "x:A a backlog:ImpactAssessment ; backlog:assessesInterruption x:U .\n" + urg(extra='; backlog:urgencyResolvedAt "2026-10-26T12:00:00Z"^^xsd:dateTime ; backlog:urgencyResumedAt "2026-10-26T13:00:00Z"^^xsd:dateTime '), {"ASS": 0, "ORD": 0, "BACK": 0}),
 ("open past its time box", BASE + urg(decl="2026-10-25T10:00:00Z", box="2026-10-25T12:00:00Z"), {"BOX": 1}),
 ("two open interruptions on one lineage", BASE + urg() + urg("V"), {"TWO": 1}),
 ("an urgent item also admitted as scope", BASE + "x:SC a backlog:ScopeChange ; backlog:admitsItem x:UW .\n" + urg(), {"SCOPE": 1}),
 ("a held item of another lineage", BASE + lineage("M") + item("S1", "M", "Suspended") + urg(hold=("S1",)), {"FOREIGN": 1}),
 ("two lineages joined only by an interruption count as connected", "x:Reg backlog:adoptsRuleSet backlog:RS_ConcurrentLineages .\n" + lineage("L") + lineage("M") + item("UW", "M") + urg(), {"L1": 0}),
 ("two unconnected active lineages are still refused", "x:Reg backlog:adoptsRuleSet backlog:RS_ConcurrentLineages .\n" + lineage("L") + lineage("M"), {"L1": 1}),
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
