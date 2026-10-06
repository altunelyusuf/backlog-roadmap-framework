#!/usr/bin/env python3
"""backlog_admitted_prelineage_probe v1.0.0 -- re-runnable proof of the admitted pre-lineage exemption (shapes v1.147.0).

Runs the CURRENT validator on fixtures/fixture_admitted_prelineage_negative and asserts, per story, both halves (L-95):
  EXEMPT (silent for an item a rebuilt, active Backlog-stage output admits as pre-lineage), and still FIRING for a fresh
  item and for one that is flagged but not admitted:
    GroomingShape, no concern declared      "declares neither an applicable design concern"
    GroomingShape, concern unaddressed      "declares a design concern that no refinement event addressed"
    L4StoryGranularityShape                 "no PlanningEvent ever took it"
  and the verification-fact shapes (evidence, criterion, harness, audit date, finish point) must STILL fire on the admitted
  items: admission exempts records of acts, never the facts a Done claim rests on.
Exit 0 when every expectation holds, 1 otherwise. Cite the fixture by stem (L-123).
"""
import glob, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
val = sorted(glob.glob(os.path.join(HERE, "backlog_validate_v*.py")), key=sv)[-1]
fx = sorted(glob.glob(os.path.join(HERE, "fixtures", "fixture_admitted_prelineage_negative_v*.ttl")), key=sv)[-1]
out = subprocess.run([sys.executable, val, fx], capture_output=True, text=True, timeout=900).stdout
fired = {}
for m in re.finditer(r"\[Violation\]\s+(S_\w+)\s+(.*)", out):
    fired.setdefault(m.group(1), []).append(m.group(2))
ACT = {"neither": "declares neither an applicable design concern",
       "unaddressed": "declares a design concern that no refinement event addressed",
       "planning": "no PlanningEvent ever took it"}
FACT = ["at least one Evidence artifact", "at least one acceptance criterion", "test harness whose completeness",
        "lastAuditedAt", "records no finish point"]
has = lambda n, key: any(key in x for x in fired.get(n, []))
EXP = {  # node: (acts that must be silent, acts that must fire)
    "S_Carried": (["neither", "planning"], []),
    "S_CarriedConcern": (["unaddressed", "planning"], []),
    "S_Fresh": ([], ["neither", "planning"]),
    "S_FlaggedOnly": ([], ["neither", "planning"]),
    "S_FreshConcern": ([], ["unaddressed", "planning"]),
}
bad = []
for n, (silent, fire) in EXP.items():
    for k in silent:
        if has(n, ACT[k]): bad.append(f"{n}: expected SILENT ({k}), fired")
    for k in fire:
        if not has(n, ACT[k]): bad.append(f"{n}: expected to FIRE ({k}), did not")
    for k in FACT:
        if not has(n, k): bad.append(f"{n}: verification fact shape did not fire: {k}")
print("validator :", os.path.basename(val)); print("fixture   :", os.path.basename(fx))
for n in EXP: print(f"  {n:18} {len(fired.get(n, []))} violation(s)")
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
