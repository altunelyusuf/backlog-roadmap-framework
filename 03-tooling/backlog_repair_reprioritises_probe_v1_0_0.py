#!/usr/bin/env python3
"""backlog_repair_reprioritises_probe v1.0.0 -- re-runnable proof of RS_RepairReprioritises (T-Box v1.145.0, shapes v1.178.0, G147).

  The owner's rule of 2026-10-23: a repair entering the backlog changes the priority of the items it touches. The rule binds only an
  adopter; an open repair names the open items it re-prioritises or states why none, and each named open item has a score later than a
  score of the repair. Each constraint fires on its planted case and is silent on its control.
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

KEYS = {"NONE": "names no item it re-prioritises", "STALE": "has not been scored since the repair was"}
HEAD = ("@prefix backlog: <http://example.org/backlog#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/rrp-probe#> .\n"
        "x:L a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_RepairReprioritises .\n")
def score(n, at):
    return f'x:{n} a backlog:WSJFScore ; backlog:scoredAt "{at}"^^xsd:dateTime .\n'
def defect(state="InProgress", lin=True, extra="", scored=True):
    p = [f"x:D a backlog:Defect ; backlog:hasState backlog:{state}"]
    if lin: p.append("backlog:belongsToLineage x:L")
    if scored: p.append("backlog:hasPriorityScore x:DS")
    return " ; ".join(p) + " " + extra + ".\n" + (score("DS", "2026-10-23T10:00:00Z") if scored else "")
def story(state="Ready", scores=("2026-10-01T10:00:00Z",)):
    s = f"x:S a backlog:Story ; backlog:hasState backlog:{state} ; backlog:belongsToLineage x:L"
    if scores: s += " ; backlog:hasPriorityScore " + " , ".join(f"x:S{i}" for i in range(len(scores)))
    return s + " .\n" + "".join(score(f"S{i}", t) for i, t in enumerate(scores))
NAMES = "; backlog:reprioritises x:S "
SCEN = [
 ("an open repair names nothing and gives no reason", defect(), {"NONE": 1, "STALE": 0}),
 ("an open repair says why it touches nothing (control)", defect(extra='; backlog:reprioritisesNothingBecause "no open item shares its cause" '), {"NONE": 0, "STALE": 0}),
 ("an open repair names an item re-scored after it (control)", defect(extra=NAMES) + story(scores=("2026-10-01T10:00:00Z", "2026-10-23T11:00:00Z")), {"NONE": 0, "STALE": 0}),
 ("an open repair names an item scored only before it", defect(extra=NAMES) + story(), {"NONE": 0, "STALE": 1}),
 ("an open repair names an item with no score", defect(extra=NAMES) + story(scores=()), {"STALE": 1}),
 ("an open repair names an item that is Done (nothing open to re-rank)", defect(extra=NAMES) + story(state="Done"), {"STALE": 0}),
 ("a Done repair is not asked", defect(state="Done"), {"NONE": 0, "STALE": 0}),
 ("a repair outside the adopting lineage is not judged", defect(lin=False), {"NONE": 0, "STALE": 0}),
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
