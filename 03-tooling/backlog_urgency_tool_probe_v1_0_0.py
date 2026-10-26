#!/usr/bin/env python3
"""backlog_urgency_tool_probe v1.0.0 -- re-runnable proof of the urgent-interruption recorder (backlog_urgency v1.0.0, G158).

  Runs the whole ceremony on a scratch register: declare (started items held and Suspended, urgent item named), the refusals (a second
  open interruption, resolving with open urgent work, resuming before the end or without an assessment), resolve, resume (held items
  back In Progress), and the real validator after each step reports no G158 violation. Exit 0 when every expectation holds.
"""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    for pat in ("03-tooling/backlog_validate_v*.py", "03-tooling/backlog_urgency_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl", "01-ontologies/backlog_abox_v*.ttl"):
        print(latest(pat))
    print(os.path.abspath(__file__)); sys.exit(0)
val = latest("03-tooling/backlog_validate_v*.py"); tool = latest("03-tooling/backlog_urgency_v*.py")
bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
REG = """@prefix backlog: <http://example.org/backlog#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix x: <http://example.org/urg-tool#> .
x:L a backlog:Lineage ; backlog:hasLineageStatus backlog:LS_InProgress .
x:A a backlog:Story ; backlog:hasState backlog:InProgress ; backlog:belongsToLineage x:L .
x:B a backlog:Story ; backlog:hasState backlog:InProgress ; backlog:belongsToLineage x:L .
x:C a backlog:Story ; backlog:hasState backlog:Ready ; backlog:belongsToLineage x:L .
x:UW a backlog:Defect ; backlog:hasState backlog:InProgress ; backlog:belongsToLineage x:L .
"""
N = "http://example.org/urg-tool#"
def run(*args):
    r = subprocess.run([sys.executable, tool, *args], capture_output=True, text=True); return r.returncode, r.stdout + r.stderr
def g158(reg):
    out = subprocess.run([sys.executable, val, reg], capture_output=True, text=True, timeout=900).stdout
    return [l for l in out.splitlines() if "[Violation]" in l and "G158" in l]
with tempfile.TemporaryDirectory() as d:
    reg = os.path.join(d, "r.ttl"); open(reg, "w").write(REG)
    c, o = run("declare", reg, "--lineage", N + "L", "--reason", "service down", "--until", "2099-01-01T00:00:00Z", "--urgent", N + "UW")
    expect("declare succeeds and holds the two started items, not the Ready one", c == 0 and "2 item(s) held" in o)
    t = open(reg).read()
    expect("the held items read Suspended and the Ready one is untouched", t.count("backlog:hasState backlog:Suspended") == 2 and "x:C a backlog:Story ; backlog:hasState backlog:Ready" in t)
    expect("the register has no G158 violation while the pause is open", g158(reg) == [])
    c, o = run("declare", reg, "--lineage", N + "L", "--reason", "again", "--until", "2099-01-01T00:00:00Z", "--urgent", N + "UW")
    expect("a second open interruption on the lineage is refused", c != 0)
    u = N + "Urgent_1"
    c, o = run("resolve", reg, "--interruption", u)
    expect("resolve is refused while the urgent item is open", c != 0)
    c, o = run("resume", reg, "--interruption", u, "--impact", "x")
    expect("resume is refused before the emergency is resolved", c != 0)
    s = open(reg).read(); open(reg, "w").write(s.replace("x:UW a backlog:Defect ; backlog:hasState backlog:InProgress", "x:UW a backlog:Defect ; backlog:hasState backlog:Done"))
    c, o = run("resolve", reg, "--interruption", u)
    expect("resolve succeeds once the urgent item is Done", c == 0)
    c, o = run("resume", reg, "--interruption", u)
    expect("resume is refused without an impact assessment", c != 0)
    c, o = run("resume", reg, "--interruption", u, "--impact", "Two stories slipped one day; the ranking is unchanged.")
    expect("resume succeeds with an assessment and moves the held items back", c == 0 and "2 item(s) moved back" in o)
    t = open(reg).read()
    expect("the held items read In Progress again", t.count("backlog:hasState backlog:Suspended") == 0 and t.count("backlog:hasState backlog:InProgress") == 2)
    v = g158(reg)
    expect("the register has no G158 violation after the resume" + ("" if not v else ": " + v[0][:200]), v == [])
    c, o = run("status", reg)
    expect("status reports no open interruption", c == 0 and "no open" in o)
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
