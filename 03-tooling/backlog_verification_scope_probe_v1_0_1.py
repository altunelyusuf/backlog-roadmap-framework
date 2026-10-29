#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe reads no record of the framework register; the validator keeps only the controlled individuals)
"""backlog_verification_scope_probe v1.0.0 -- re-runnable proof of the scope and risk of the item-level rule sets (shapes v1.162.0, G112).

Each scenario is a tiny graph judged by the CURRENT validator; the probe reads only the named shape's own message.
  Scope of an adoption (RS_IndependentVerification, the same reading serves the other item-level rule sets)
    fires   register adopts; lineage adopts and the item belongs to it; lineage adopts and the item was admitted by an output of an item of it;
            register adopts at a moment and the item finished after it; the same and the item has no finishedAt
    silent  lineage adopts and the item belongs to another lineage; the item finished before the register's adoption moment
  Risk (verificationThreshold 3)
    fires   level 3 without verifier; level 5 without verifier; Done without a level (UnclassifiedDoneShape)
    silent  level 2 without verifier; level 3 with a verifier; a Done item with no level when no threshold is stated (it needs a verifier, not a level)
  Flow points (RS_FlowPointsRecorded)
    fires   Done without a start; Done without a finish; a start written as midnight without a stated precision
    silent  both points as instants; absence with a stated reason; midnight with precision Date; lineage adoption and an item of another lineage
  Other item-level rule sets in a lineage scope
    silent  RS_HumanOversight adopted by a lineage, an agent overseer on an item of another lineage
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
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/verification-scope-probe#> .\n"
IV, FP, HO = "RS_IndependentVerification", "RS_FlowPointsRecorded", "RS_HumanOversight"
def reg(rs, at=None, thr=None):
    return f"x:Reg a backlog:Backlog ; backlog:isRegisterRoot true ; backlog:adoptsRuleSet backlog:{rs}" + (f' ; backlog:ruleSetAdoptedAt "{at}"^^xsd:dateTime' if at else "") + (f" ; backlog:verificationThreshold {thr}" if thr else "") + " .\n"
def lin(n, rs, thr=None):
    return f"x:{n} a backlog:Lineage ; backlog:adoptsRuleSet backlog:{rs}" + (f" ; backlog:verificationThreshold {thr}" if thr else "") + " .\n"
H = "x:P a backlog:Executor_IndividualHuman .\n"
def item(n="W", state="Done", lineage=None, level=None, ver=None, start=None, fin=None, why=None, prec=None, extra=""):
    t = f"x:{n} a backlog:Task ; backlog:hasState backlog:{state} ; backlog:responsible x:P"
    if lineage: t += f" ; backlog:belongsToLineage x:{lineage}"
    if level is not None: t += f" ; backlog:integrityLevel {level}"
    if ver: t += f" ; backlog:verifiedBy x:{ver}"
    if start: t += f' ; backlog:startedAt "{start}"^^xsd:dateTime'
    if fin: t += f' ; backlog:finishedAt "{fin}"^^xsd:dateTime'
    if why: t += f' ; backlog:flowPointAbsenceReason "{why}"'
    if prec: t += f" ; backlog:flowPointPrecision backlog:{prec}"
    return t + extra + " .\n"
Q = "x:Q a backlog:Executor_IndividualHuman .\n"
MISS = "names no verifiedBy"; UNC = "carries no integrityLevel"; FM = "lacks startedAt or finishedAt"; FD = "is exactly midnight"; OVR = "G111: the Executor named as overseer"
I1, I2, I3 = "2026-10-01T09:30:00Z", "2026-10-02T09:30:00Z", "2026-09-01T09:30:00Z"
SCEN = {
  "register adopts":                          (H + reg(IV) + item(), MISS, 1),
  "lineage adopts, item belongs":             (H + lin("L1", IV) + item(lineage="L1"), MISS, 1),
  "lineage adopts, item of another lineage":  (H + lin("L1", IV) + lin("L2", "RS_LineageStatus") + item(lineage="L2"), MISS, 0),
  "lineage adopts, item in no lineage":       (H + lin("L1", IV) + item(), MISS, 0),
  "lineage adopts, item admitted by output":  (H + lin("L1", IV) + item("A", "Open", "L1") + item("W", extra=" ; backlog:admittedByOutput x:A"), MISS, 1),
  "adopted at a moment, finished after":      (H + reg(IV, "2026-10-01T00:00:00Z") + item(fin=I2), MISS, 1),
  "adopted at a moment, finished before":     (H + reg(IV, "2026-10-01T00:00:00Z") + item(fin=I3), MISS, 0),
  "adopted at a moment, no finish":           (H + reg(IV, "2026-10-01T00:00:00Z") + item(), MISS, 1),
  "threshold 3, level 3, no verifier":        (H + reg(IV, thr=3) + item(level=3), MISS, 1),
  "threshold 3, level 5, no verifier":        (H + reg(IV, thr=3) + item(level=5), MISS, 1),
  "threshold 3, level 2, no verifier":        (H + reg(IV, thr=3) + item(level=2), MISS, 0),
  "threshold 3, level 3, with verifier":      (H + Q + reg(IV, thr=3) + item(level=3, ver="Q"), MISS, 0),
  "threshold 3, Done without a level":        (H + reg(IV, thr=3) + item(), UNC, 1),
  "threshold 3, level stated":                (H + reg(IV, thr=3) + item(level=1), UNC, 0),
  "no threshold, no level":                   (H + reg(IV) + item(), UNC, 0),
  "flow: no start":                           (H + reg(FP) + item(fin=I2), FM, 1),
  "flow: no finish":                          (H + reg(FP) + item(start=I1), FM, 1),
  "flow: both instants":                      (H + reg(FP) + item(start=I1, fin=I2), FM, 0),
  "flow: absence with a reason":              (H + reg(FP) + item(why="started before the register existed"), FM, 0),
  "flow: lineage adopts, other lineage":      (H + lin("L1", FP) + lin("L2", "RS_LineageStatus") + item(lineage="L2"), FM, 0),
  "flow: midnight, no precision":             (H + reg(FP) + item(start="2026-10-01T00:00:00Z", fin=I2), FD, 1),
  "flow: midnight, precision Date":           (H + reg(FP) + item(start="2026-10-01T00:00:00Z", fin=I2, prec="Precision_Date"), FD, 0),
  "flow: not midnight":                       (H + reg(FP) + item(start=I1, fin=I2), FD, 0),
  "oversight: lineage adopts, other lineage": (H + "x:AG a backlog:Executor_SingleAgent .\n" + lin("L1", HO) + lin("L2", "RS_LineageStatus") + item(state="InProgress", lineage="L2", extra=" ; backlog:overseenBy x:AG"), OVR, 0),
  "oversight: lineage adopts, item belongs":  (H + "x:AG a backlog:Executor_SingleAgent .\n" + lin("L1", HO) + item(state="InProgress", lineage="L1", extra=" ; backlog:overseenBy x:AG"), OVR, 1),
}
bad = []
with tempfile.TemporaryDirectory() as d:
    for name, (body, key, want) in SCEN.items():
        f = os.path.join(d, "s.ttl"); open(f, "w").write(HEAD + body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=600).stdout
        got = sum(1 for ln in out.splitlines() if "[Violation]" in ln and key in ln)
        print(f"{name:44} expected {want} got {got}")
        if got != want: bad.append(f"{name}: expected {want}, got {got}")
print("validator :", os.path.basename(val)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
