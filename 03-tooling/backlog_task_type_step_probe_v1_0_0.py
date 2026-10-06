#!/usr/bin/env python3
"""backlog_task_type_step_probe v1.0.0 -- re-runnable proof of the task-type step shapes (v1.118.0/v1.146.0).

Runs the CURRENT validator (highest version on disk) on fixtures/fixture_task_type_step_negative and asserts by
step name both halves (L-95):
  fires   STEP_NoOrdinal, STEP_NoCheck, STEP_DupA, STEP_DupB, STEP_Orphan
  silent  STEP_Good1, STEP_Good2, STEP_OtherType, Run_Step
Exit 0 when every expectation holds, 1 otherwise. Cite the fixture by stem (L-123).
"""
import glob, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
val = sorted(glob.glob(os.path.join(HERE, "backlog_validate_v*.py")), key=sv)[-1]
fx = sorted(glob.glob(os.path.join(HERE, "fixtures", "fixture_task_type_step_negative_v*.ttl")), key=sv)[-1]
out = subprocess.run([sys.executable, val, fx], capture_output=True, text=True, timeout=600).stdout
fired = {m.group(1) for m in re.finditer(r"\[Violation\]\s+((?:STEP|Run)_\w+)", out)}
FIRES = {"STEP_NoOrdinal", "STEP_NoCheck", "STEP_DupA", "STEP_DupB", "STEP_Orphan"}
SILENT = {"STEP_Good1", "STEP_Good2", "STEP_OtherType", "Run_Step"}
bad = [f"expected to FIRE, did not: {c}" for c in sorted(FIRES - fired)] + \
      [f"expected SILENT, fired: {c}" for c in sorted(SILENT & fired)] + \
      [f"unexpected node fired: {c}" for c in sorted(fired - FIRES - SILENT)]
print("validator :", os.path.basename(val)); print("fixture   :", os.path.basename(fx))
print("fired     :", ", ".join(sorted(fired)) or "(none)")
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
