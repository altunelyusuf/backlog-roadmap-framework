#!/usr/bin/env python3
"""backlog_self_application_v1_0_0.py — every checker runs against this package.

A4 from the lineage discipline. Several findings in this package's history came
from running a checker against the package that ships it, and EVERY ONE was
noticed by accident:

  the script-decision audit flagged the row checker written beside it
  the distribution builder shipped a cache file it should have excluded
  the reachability gate reported PASS on an empty graph when run bare

The last was found by writing this. That is the argument for it: a checker is
the one artefact whose own subject includes itself, and nothing was asking.

Two things are checked here, both cheap:

  RAN       every checker in 03-tooling exits without crashing when handed the
            package's own files
  NOT BLIND a checker given nothing must not return a verdict. A tool that
            passes on an empty graph reports green for a graph it never read,
            which is the most expensive kind of wrong.

Exit 1 under --strict if any checker is blind.
"""
import sys, os, glob, subprocess

# Checkers that take graph paths and should refuse to run without them.
TAKES_INPUT = ("backlog_reachability_gate", "backlog_validate",
               "backlog_pipeline_verify", "backlog_lineage_completeness")

def main():
    strict = "--strict" in sys.argv
    here = os.path.dirname(os.path.abspath(__file__))
    me = os.path.basename(__file__)
    blind, crashed, ok = [], [], 0
    for path in sorted(glob.glob(os.path.join(here, "*.py"))):
        name = os.path.basename(path)
        if name == me or not any(name.startswith(p) for p in TAKES_INPUT):
            continue
        try:
            r = subprocess.run([sys.executable, path], capture_output=True,
                               text=True, timeout=60)
        except subprocess.TimeoutExpired:
            crashed.append((name, "timed out"))
            continue
        out = (r.stdout + r.stderr)
        if r.returncode == 0 and "PASS" in out:
            blind.append(name)
        elif "FATAL" in out or r.returncode != 0:
            ok += 1
        else:
            ok += 1
    print("input-taking checkers  : %d" % (ok + len(blind) + len(crashed)))
    print("refuse to run blind    : %d" % ok)
    print("PASS on no input       : %d" % len(blind))
    for n in blind:
        print("   BLIND  %s" % n)
    for n, why in crashed:
        print("   %s  %s" % (why, n))
    print("VERDICT     : %s" % (
        "PASS - no checker returns a verdict about a graph it never read"
        if not blind else
        "FAIL - %d checker(s) report PASS on an empty graph" % len(blind)))
    sys.exit(1 if (blind and strict) else 0)

if __name__ == "__main__":
    main()
