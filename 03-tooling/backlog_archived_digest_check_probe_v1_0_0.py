#!/usr/bin/env python3
"""backlog_archived_digest_check_probe v1.0.0 -- the ratchet holds in both directions, run as a program (G99).

On the pipeline fixture as a one-lineage archive, and a copy of it with one recorded digest tampered:
  1 reproducing chain, empty baseline         -> exit 0
  2 tampered chain, empty baseline            -> exit 2, NEW FAILURE printed
  3 tampered chain, lineage in the baseline   -> exit 0 (a known failure may not grow, it may stay)
  4 reproducing chain, lineage in the baseline-> exit 0 and a NOTE to remove it (the ratchet only tightens)
Runs without the result cache (BACKLOG_VALIDATE_MEMO_DIR unset) so each case is measured. Exit 0 all hold; 2 a case failed.
"""
import glob, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = sorted(glob.glob(os.path.join(HERE, "backlog_archived_digest_check_v*.py")), key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]])[-1]
env = {k: v for k, v in os.environ.items() if k != "BACKLOG_VALIDATE_MEMO_DIR"}


def run(*args):
    r = subprocess.run([sys.executable, "-B", TOOL] + list(args), capture_output=True, text=True, env=env)
    return r.returncode, r.stdout


FIX = sorted(glob.glob(os.path.join(HERE, "fixtures", "fixture_pipeline_v*.ttl")), key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]])[-1]
bad = []
with tempfile.TemporaryDirectory() as d:
    txt = open(FIX).read()
    m = re.search(r'backlog:hasStateDigest "([0-9a-f]{64})"', txt)
    good = os.path.join(d, "good.ttl"); open(good, "w").write(txt)
    tam = os.path.join(d, "tampered.ttl"); open(tam, "w").write(txt.replace(m.group(1), "0" * 64, 1))
    lin = re.search(r"^(?:ex:)?(\w+)\s+a\s+backlog:Lineage", txt, re.M).group(1)
    empty = os.path.join(d, "empty.txt"); open(empty, "w").write("# nothing\n")
    named = os.path.join(d, "named.txt"); open(named, "w").write(lin + "\n")
    c, o = run("--archive", good, "--baseline", empty)
    if c != 0: bad.append("1 a reproducing chain with an empty baseline was refused")
    c, o = run("--archive", tam, "--baseline", empty)
    if c != 2 or "NEW FAILURE" not in o: bad.append("2 a tampered chain not in the baseline was not refused")
    c, o = run("--archive", tam, "--baseline", named)
    if c != 0: bad.append("3 a tampered chain that is in the baseline was refused")
    c, o = run("--archive", good, "--baseline", named)
    if c != 0 or "remove it from the baseline" not in o: bad.append("4 a baseline entry that now reproduces was not reported")
for b in bad: print("FAILED: " + b)
print("VERDICT: %s" % ("all 4 cases hold" if not bad else "%d case(s) failed" % len(bad)))
sys.exit(0 if not bad else 2)
