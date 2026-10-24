#!/usr/bin/env python3
"""backlog_gate_timing_probe v1.0.0 -- proof that the release tool records seconds per gate section and leaves the gate's log unchanged (G152)."""
import glob, importlib.util, os, re, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
tool = sorted(glob.glob(os.path.join(HERE, "backlog_release_tool_v*.py")), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(tool); sys.exit(0)
spec = importlib.util.spec_from_file_location("rt", tool); rt = importlib.util.module_from_spec(spec); spec.loader.exec_module(rt)
bad = []
def expect(n, ok):
    print(("PASS  " if ok else "FAIL  ") + n)
    if not ok: bad.append(n)
with tempfile.TemporaryDirectory() as d:
    g = os.path.join(d, "fake_gate.sh")
    open(g, "w").write('echo "== Quick =="; echo a; echo "== Slow =="; sleep 2; echo b; echo "== Last =="; echo c\n')
    log = os.path.join(d, "gate.log")
    secs = rt.timed_gate(["bash", g], log, 60, d)
    expect("three sections are timed, the slowest first", [b for a, b in secs][0] == "Slow" and len(secs) == 3 and secs[0][0] >= 1.5)
    expect("the gate's own output is in the log unchanged", open(log).read() == "== Quick ==\na\n== Slow ==\nb\n== Last ==\nc\n")
    expect("a sidecar file holds the timings", os.path.exists(log + ".timing.tsv") and "Slow" in open(log + ".timing.tsv").read())
print("VERDICT   :", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
