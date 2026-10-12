#!/usr/bin/env python3
"""backlog_lineage_concurrency_probe v1.0.0 -- re-runnable proof of UnconnectedActiveLineagesShape (shapes v1.158.0, G104).

Each scenario is a tiny register written to a scratch folder and judged by the CURRENT validator (highest version on disk);
the probe reads only this shape's own message ("nothing connects them"). Both halves (L-95):
  fires   two unconnected active lineages in a register that adopted RS_ConcurrentLineages
  silent  the same pair in a register that did not adopt it (G89, G91)
  silent  a cross-lineage dependsOn; a divide-and-conquer part and its parent; one active and one queued (LS_Opened);
          one active and one finished (LS_Achieved); a chain of connections (A-B, B-C) judged for A and C
Exit 0 when every expectation holds, 1 otherwise. The fixture_negative case LIN_UNCONNECTED_B is the shape's declared proof.
"""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
if sys.argv[1:] == ["--deps"]:
    # what this probe reads: itself, the validator, the shapes and the T-Box it judges with
    pkg = os.path.dirname(HERE)
    for pat in ("03-tooling/backlog_validate_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl"):
        c = sorted(glob.glob(os.path.join(pkg, pat)), key=lambda q: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", q)[0]])
        print(c[-1])
    print(os.path.abspath(__file__)); sys.exit(0)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
val = sorted(glob.glob(os.path.join(HERE, "backlog_validate_v*.py")), key=sv)[-1]
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/concurrency-probe#> .\n"
ADOPT = "x:Reg a backlog:Backlog ; backlog:isRegisterRoot true ; backlog:adoptsRuleSet backlog:RS_ConcurrentLineages .\n"
L = lambda n, st: f"x:{n} a backlog:Lineage ; backlog:hasLineageStatus backlog:{st} .\n"
I = lambda n, lin, dep="": f"x:{n} a backlog:Task ; backlog:belongsToLineage x:{lin}" + (f" ; backlog:dependsOn x:{dep}" if dep else "") + " .\n"
SCEN = {
  "unconnected pair, adopted": (ADOPT + L("P1", "LS_InProgress") + L("P2", "LS_Scoped"), 1),
  "unconnected pair, NOT adopted": (L("N1", "LS_InProgress") + L("N2", "LS_Scoped"), 0),
  "cross-lineage dependsOn": (ADOPT + L("Q1", "LS_InProgress") + L("Q2", "LS_Backlogged") + I("QI1", "Q1") + I("QI2", "Q2", "QI1"), 0),
  "part and parent": (ADOPT + L("R1", "LS_InProgress") + L("R2", "LS_InProgress") + "x:R2 backlog:parentLineage x:R1 .\n", 0),
  "active and queued": (ADOPT + L("S1", "LS_InProgress") + L("S2", "LS_Opened"), 0),
  "active and achieved": (ADOPT + L("T1", "LS_InProgress") + L("T2", "LS_Achieved") + L("T3", "LS_Archived"), 0),
  "chain A-B, B-C": (ADOPT + L("U1", "LS_InProgress") + L("U2", "LS_InProgress") + L("U3", "LS_Revived")
                     + I("UI1", "U1") + I("UI2", "U2", "UI1") + I("UI3", "U2") + I("UI4", "U3", "UI3"), 0),
}
bad = []
with tempfile.TemporaryDirectory() as d:
    for name, (body, want) in SCEN.items():
        f = os.path.join(d, "s.ttl"); open(f, "w").write(HEAD + body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=600).stdout
        got = sum(1 for ln in out.splitlines() if "[Violation]" in ln and "nothing connects them" in ln)
        print(f"{name:26} expected {want} got {got}")
        if got != want: bad.append(f"{name}: expected {want}, got {got}")
print("validator :", os.path.basename(val)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
