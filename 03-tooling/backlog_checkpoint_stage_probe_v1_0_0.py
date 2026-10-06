#!/usr/bin/env python3
"""backlog_checkpoint_stage_probe v1.0.0 -- re-runnable proof of the checkpoint-condition ruling (v1.117.0/v1.145.0).

Runs the CURRENT validator (highest version on disk, rules merged, as production runs it) on
fixtures/fixture_checkpoint_anchor_negative and asserts, by checkpoint name, both halves:
  fires   CP_TextOnlyBacklogged, CP_NoTimingObjectived
  silent  CP_TextOnlyObjectived, CP_TextAndItemBacklogged, CP_DatedBacklogged, CP_TextOnlyGoaled
A probe that only shows the rule firing proves half the rule (L-95); the silent controls are the other half.
Exit 0 when every expectation holds, 1 otherwise. Cite the fixture by stem (L-123).
"""
import glob, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
val = sorted(glob.glob(os.path.join(HERE, "backlog_validate_v*.py")), key=sv)[-1]
fx = sorted(glob.glob(os.path.join(HERE, "fixtures", "fixture_checkpoint_anchor_negative_v*.ttl")), key=sv)[-1]
out = subprocess.run([sys.executable, val, fx], capture_output=True, text=True, timeout=600).stdout
fired = {m.group(1) for m in re.finditer(r"\[Violation\]\s+(CP_\w+)", out)}
FIRES = {"CP_TextOnlyBacklogged", "CP_NoTimingObjectived"}
SILENT = {"CP_TextOnlyObjectived", "CP_TextAndItemBacklogged", "CP_DatedBacklogged", "CP_TextOnlyGoaled"}
bad = [f"expected to FIRE, did not: {c}" for c in sorted(FIRES - fired)] + \
      [f"expected SILENT, fired: {c}" for c in sorted(SILENT & fired)] + \
      [f"unexpected checkpoint fired: {c}" for c in sorted(fired - FIRES - SILENT)]
print("validator :", os.path.basename(val)); print("fixture   :", os.path.basename(fx))
print("fired     :", ", ".join(sorted(fired)) or "(none)")
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
