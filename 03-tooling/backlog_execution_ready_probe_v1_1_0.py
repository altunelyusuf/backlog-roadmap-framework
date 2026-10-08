#!/usr/bin/env python3
"""backlog_execution_ready_probe v1.1.0 -- proof that the start gate discriminates (L-95), both halves.

Runs backlog_execution_ready on fixtures/fixture_execution_ready_negative and asserts the exit code and the missing fact
for every case: the groomed item and its lineage are READY (exit 0); every other case is NOT READY (exit 2) and names
exactly the fact it lacks. A gate that never fails certifies nothing; a gate that never passes blocks everything.
Exit 0 when every expectation holds, 1 otherwise. Cite the fixture by stem (L-123).
"""
import glob, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
tool = sorted(glob.glob(os.path.join(HERE, "backlog_execution_ready_v*.py")), key=sv)[-1]
fx = sorted(glob.glob(os.path.join(HERE, "fixtures", "fixture_execution_ready_negative_v*.ttl")), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(tool); print(fx)
    sys.exit(0)


CASES = [  # (args, exit, text that must appear in the output)
    (["--lineage", "Lin_Ready"], 0, "VERDICT     : READY"),
    (["--lineage", "Lin_Ready", "--item", "S_Groomed"], 0, "VERDICT     : READY"),
    (["--lineage", "Lin_Ready", "--item", "S_NoCriterion"], 2, "FAIL  it carries an acceptance criterion"),
    (["--lineage", "Lin_Ready", "--item", "S_NoConcern"], 2, "FAIL  it states its applicable design concerns"),
    (["--lineage", "Lin_Ready", "--item", "S_Unplanned"], 2, "FAIL  a PlanningEvent has taken it in"),
    (["--lineage", "Lin_Ready", "--item", "S_Proposed"], 2, "FAIL  its state is Ready or InProgress"),
    (["--lineage", "Lin_Ready", "--item", "S_Missing"], 2, "FAIL  the item exists in the register"),
    (["--lineage", "Lin_Waiting"], 2, "FAIL  Stage_Backlog has an active output (examined: 0)"),
    (["--lineage", "Lin_Waiting"], 2, "FAIL  the lineage holds at least one work item (examined: 0)"),
    (["--lineage", "Lin_Retracted"], 2, "FAIL  Stage_Backlog has an active output (examined: 0)"),
    (["--lineage", "Lin_Frozen"], 2, "FAIL  the lineage is not frozen"),
    (["--lineage", "Lin_Nowhere"], 2, "FAIL  the lineage exists"),
]
bad = []
for args, want, text in CASES:
    r = subprocess.run([sys.executable, tool, fx] + args, capture_output=True, text=True, timeout=120)
    ok = r.returncode == want and text in r.stdout
    print(("PASS  " if ok else "FAIL  ") + " ".join(args) + f"  -> exit {r.returncode}")
    if not ok: bad.append(" ".join(args))
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
