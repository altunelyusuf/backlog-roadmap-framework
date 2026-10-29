#!/usr/bin/env python3
"""backlog_archived_digest_tables_probe v1.0.0 -- the archived-digest check measures the digest table under which a lineage reproduces (Lineage 22, D1).

The cause of a non-reproducing archived lineage was stated, not measured, and for Lineage 20 it was wrong. The check now measures it with the verifier's own functions. Cases on the
archive file, whose closed lineages do not change: Lineage 20 reproduces under v5 only; a lineage closed under the early tables reproduces under v1 to v3 and not under v4 or v5;
an old lineage reproduces under none; a lineage with no stage output has no table; and the check's verdict is untouched by the measurement (a table the lineage did not adopt never makes it pass)."""
import glob, importlib.util, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
tool = sorted(glob.glob(os.path.join(HERE, "backlog_archived_digest_check_v*.py")), key=sv)[-1]
arch = sorted(glob.glob(os.path.join(PKG, "01-ontologies", "archive", "backlog_framework_archive_abox_v*.ttl")), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(tool); print(arch); sys.exit(0)
spec = importlib.util.spec_from_file_location("adc", tool); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
bad = []
def expect(n, ok):
    print(("PASS  " if ok else "FAIL  ") + n)
    if not ok: bad.append(n)
r = m.tables_reproducing(arch, ["L_AdaptiveCeremonies", "L_OEPackageConsolidation", "L_Plan", "L_Build"])
expect("Lineage 20 reproduces under v5 and under no other table", r["L_AdaptiveCeremonies"] == ["v5"])
expect("a lineage closed under the early tables reproduces under v1, v2 and v3 and not under v4 or v5", r["L_OEPackageConsolidation"] == ["v1", "v2", "v3"])
expect("an old lineage that no table explains reproduces under none", r["L_Plan"] == [])
expect("a lineage with no stage output has no table", r["L_Build"] == [])
out = subprocess.run([sys.executable, "-B", tool], capture_output=True, text=True).stdout
expect("the check prints the measured table for Lineage 20 and keeps its verdict within the baseline", "TABLES: L_AdaptiveCeremonies reproduces under v5 only" in out and "VERDICT: within the baseline" in out)
print("VERDICT   :", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
