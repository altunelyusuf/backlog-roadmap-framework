#!/usr/bin/env python3
"""backlog_g163_probe v1.1.0 -- re-runnable proof that the opening profile is versioned (G163).

  A profile that grows must not judge a lineage opened earlier (G89); a lineage is held to every rule set up to the revision it opened under.
  Each case runs through the real validator against the real profiles. Exit 0 when every expectation holds.
"""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    for pat in ("03-tooling/backlog_validate_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl", "01-ontologies/backlog_abox_v*.ttl", "03-tooling/backlog_open_lineage_v*.py", "03-tooling/backlog_roadmap_report_v*.py"):
        print(latest(pat))
    print(os.path.abspath(__file__)); sys.exit(0)
val = latest("03-tooling/backlog_validate_v*.py"); tool = latest("03-tooling/backlog_open_lineage_v*.py"); bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
H = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/g163#> .\n"
R1 = "RS_StatusHistoryRecorded RS_FlowPointsRecorded RS_RepairReprioritises RS_ImpedimentNamesWhatItBlocks RS_DecompositionStateAgrees".split()
R2 = ["RS_ConcurrentLineages"]; R3 = "RS_PlanBeforeStart RS_CancellationAssessed RS_ChangeSupportsMission".split()
def lin(rev, adopt):
    t = "x:L a backlog:Lineage ; backlog:openedWithProfile backlog:Profile_Standard ; "
    if rev: t += f"backlog:openedUnderRevision backlog:Pr_{rev} ; "
    return t + "backlog:adoptsRuleSet " + " , ".join("backlog:" + r for r in adopt) + " .\n"
K = "does not adopt a rule set the profile included"
SC = [("opened before the profile grew (no revision recorded), adopts the first revision's sets", lin(None, R1), 0),
      ("opened under revision 1, adopts its sets", lin(1, R1), 0),
      ("opened under revision 1, misses one of its sets", lin(1, R1[1:]), 1),
      ("opened under revision 2, adopts revisions 1 and 2", lin(2, R1 + R2), 0),
      ("opened under revision 2, misses the one-lineage rule", lin(2, R1), 1),
      ("opened under revision 3, adopts all", lin(3, R1 + R2 + R3), 0),
      ("opened under revision 3, misses a revision 3 set", lin(3, R1 + R2 + R3[1:]), 1)]
with tempfile.TemporaryDirectory() as d:
    for name, body, n in SC:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(H + body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=900).stdout
        got = sum(1 for ln in out.splitlines() if "[Violation]" in ln and K in ln)
        expect(f"{name}: expected {n}, got {got}", got == n)
    f = os.path.join(d, "r.ttl"); open(f, "w").write(H + "x:P a backlog:ProfileRevision .\n")
    out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=900).stdout
    expect("a revision with no number is refused", any("[Violation]" in ln and "must carry its number" in ln for ln in out.splitlines()))
rep = latest("03-tooling/backlog_roadmap_report_v*.py")
with tempfile.TemporaryDirectory() as d:
    reg = os.path.join(d, "r.ttl"); out = os.path.join(d, "o.ttl")
    open(reg, "w").write(H + "x:Reg a backlog:Register .\nx:MyBacklog a backlog:Backlog .\n")
    subprocess.run([sys.executable, rep, reg, "--emit", out], capture_output=True, text=True, timeout=900)
    ok = os.path.exists(out) and "reportOf x:MyBacklog" in open(out).read().replace("<http://example.org/g163#MyBacklog>", "x:MyBacklog") or (os.path.exists(out) and "g163#MyBacklog" in open(out).read())
    expect("the emitted report names the Backlog of the register it was run on, not the framework's own", ok)
o = subprocess.run([sys.executable, tool, "--profile", "Profile_Agentic", "--lineage", "L", "--prefix", "x"], capture_output=True, text=True).stdout
from rdflib import Graph, Namespace, RDF
B = Namespace("http://example.org/backlog#")
g = Graph(); g.parse(latest("01-ontologies/backlog_abox_v*.ttl"), format="turtle")
latest_rev = max(int(g.value(r, B.revisionNumber)) for r in g.subjects(RDF.type, B.ProfileRevision))
expect("the opening block names the latest revision (read from the data file, not pinned)", ("openedUnderRevision backlog:Pr_%d" % latest_rev) in o)
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
