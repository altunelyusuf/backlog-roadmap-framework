#!/usr/bin/env python3
"""backlog_validate_reference_probe v1.0.0 -- the data file as reference for other data keeps its controlled individuals and none of the register's records (Lineage 22).

When a fixture is validated, the package's data file is loaded as reference: the controlled individuals stay, the register's own statements go. The roadmap-report runs that the plan step
records live in another namespace than the register's, so v1.17.0 kept them while dropping the register they report on, and the first one made the positive fixture violate. Cases: a
controlled individual stays; a statement of the register's namespace goes; a report run goes; the run is the one that distinguishes v1.17.0 from v1.18.0."""
import glob, importlib.util, os, re, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
val = sorted(glob.glob(os.path.join(HERE, "backlog_validate_v*.py")), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(val); sys.exit(0)
spec = importlib.util.spec_from_file_location("bv", val); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from rdflib import Graph
bad = []
def expect(n, ok):
    print(("PASS  " if ok else "FAIL  ") + n)
    if not ok: bad.append(n)
with tempfile.TemporaryDirectory() as d:
    ab = os.path.join(d, "backlog_abox_v9_9_9.ttl")
    open(ab, "w").write("""@prefix backlog: <http://example.org/backlog#> .
@prefix fw: <http://example.org/backlog-framework-register#> .
@prefix report: <http://example.org/report#> .
backlog:Controlled a backlog:Concern .
fw:Register a backlog:Backlog .
report:Run_1 a backlog:RoadmapReport ; backlog:reportOf fw:Register .
""")
    m.ABOX = ab; m._REF.clear()
    ref = m.reference_abox([os.path.join(d, "fixture.ttl")])
    g = Graph().parse(ref, format="turtle")
    subs = {str(s) for s in g.subjects()}
    expect("a controlled individual stays in the reference", "http://example.org/backlog#Controlled" in subs)
    expect("a statement of the register's namespace is dropped", "http://example.org/backlog-framework-register#Register" not in subs)
    expect("a roadmap-report run is dropped with the register it reports on", "http://example.org/report#Run_1" not in subs)
    m._RUNS = "http://nowhere.example/"; m._REF.clear()
    old = {str(s_) for s_ in Graph().parse(m.reference_abox([os.path.join(d, "fixture.ttl")]), format="turtle").subjects()}
    expect("read the v1.17.0 way (runs not dropped) the run stays and the register goes, so the case discriminates", "http://example.org/report#Run_1" in old and "http://example.org/backlog-framework-register#Register" not in old)
print("VERDICT   :", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
