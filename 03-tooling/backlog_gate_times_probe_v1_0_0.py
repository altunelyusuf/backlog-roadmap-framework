#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe reads no record of the framework register; it builds its own temporary package and log)
"""backlog_gate_times_probe v1.0.0 -- proves that the seconds of every gate section and every probe are kept in the package (Lineage 31, story Know).

  1  the gate prints a "probe time:" line for a probe that ran and for one it skipped          -> both forms in the gate text
  2  the release tool writes GATE_TIMES/gate_times_vVERSION.tsv from a log and its timing sidecar -> file exists
  3  every section of the sidecar is a row of kind section, with its seconds                   -> all present
  4  every probe time line of the log is a row of kind probe; a skipped probe is marked        -> all present, mark kept
  5  a log without probe lines and without a sidecar still writes the file (header only)        -> file exists, no rows
Exit 0 when every expectation holds, 1 otherwise."""
import glob, importlib.util, os, re, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
tool = latest("03-tooling/backlog_release_tool_v*.py"); gate = latest("03-tooling/backlog_gate_v*.sh")
if sys.argv[1:] == ["--deps"]:
    print(tool); print(gate); print(os.path.abspath(__file__)); sys.exit(0)
bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
spec = importlib.util.spec_from_file_location("rt", tool); rt = importlib.util.module_from_spec(spec); spec.loader.exec_module(rt)
g = open(gate, encoding="utf-8").read()
expect("1 the gate prints probe time lines for a run and for a skipped probe",
       'echo "  probe time: $PROBE $(cat' in g and 'echo "  probe time: $PROBE 0.0 skipped"' in g)
with tempfile.TemporaryDirectory() as d:
    log = os.path.join(d, "gate_9.9.9.log")
    open(log, "w").write("== Alpha ==\n  ok\n  probe time: backlog_a_probe 12.5\n  probe time: backlog_b_probe 0.0 skipped\n  probe time: backlog_c_probe 3.0\n== Beta ==\n")
    open(log + ".timing.tsv", "w").write("20.0\tAlpha\n5.5\tBeta\n")
    out, n = rt.write_gate_times(d, "9.9.9", log)
    expect("2 the file is written under GATE_TIMES", os.path.exists(out) and out.endswith(os.path.join("GATE_TIMES", "gate_times_v9_9_9.tsv")))
    rows = [l.split("\t") for l in open(out).read().splitlines() if not l.startswith("#")]
    expect("3 every section is a row with its seconds", ["section", "Alpha", "20.0", ""] in rows and ["section", "Beta", "5.5", ""] in rows)
    expect("4 every probe is a row; the skipped one is marked", ["probe", "backlog_a_probe", "12.5", ""] in rows and ["probe", "backlog_b_probe", "0.0", "skipped"] in rows and ["probe", "backlog_c_probe", "3.0", ""] in rows and n == 5)
    log2 = os.path.join(d, "gate_9.9.8.log"); open(log2, "w").write("== Alpha ==\n")
    out2, n2 = rt.write_gate_times(d, "9.9.8", log2)
    expect("5 a log without probe lines or sidecar writes a header-only file", os.path.exists(out2) and n2 == 0)
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
