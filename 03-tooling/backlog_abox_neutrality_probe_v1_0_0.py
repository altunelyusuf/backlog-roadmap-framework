#!/usr/bin/env python3
"""backlog_abox_neutrality_probe v1.0.0 -- the shipped data file binds nobody who did not adopt (G116).

A consumer measured (2026-10-14) that validating its lineage together with this package's data file gave 131 results of the history rules and 129 of the flow-point
rules on items that were never this package's register's: the file held a register-level adoption of both rule sets, and a register-level adoption is read from any
register in the graph (G112). Two proofs:
  1 (structure) no rule set that an item-level shape (a shape targeting WorkItem) consults is adopted, in the shipped data file, by anything that is not a Lineage;
  2 (behaviour) a consumer graph with items that break every recording and verification rule, loaded together with the WHOLE shipped data file, gets no result of those
    rules; the same items under a consumer register that does adopt them get results (so the first count is not zero for want of a reading).
Exit 0 when both hold, 1 otherwise.
"""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
ABOX, SHAPES = latest("01-ontologies/backlog_abox_v*.ttl"), latest("02-shacl-safeguards/backlog_shacl_v*.ttl")
if sys.argv[1:] == ["--deps"]:
    for pat in ("03-tooling/backlog_validate_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl", "01-ontologies/backlog_abox_v*.ttl"):
        print(latest(pat))
    print(os.path.abspath(__file__)); sys.exit(0)
val = sorted(glob.glob(os.path.join(HERE, "backlog_validate_v*.py")), key=sv)[-1]
from rdflib import Graph, Namespace, RDF, URIRef
B = Namespace("http://example.org/backlog#"); SH = Namespace("http://www.w3.org/ns/shacl#")
bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
sg, ag = Graph().parse(SHAPES, format="turtle"), Graph().parse(ABOX, format="turtle")
item_level = set()
for shp in sg.subjects(SH.targetClass, B.WorkItem):
    for c in sg.objects(shp, SH.sparql):
        for q in sg.objects(c, SH.select):
            item_level |= set(re.findall(r"adoptsRuleSet\s+backlog:(RS_\w+)", str(q)))
leaks = sorted((str(s).split("#")[-1], str(o).split("#")[-1]) for s, o in ag.subject_objects(B.adoptsRuleSet)
               if str(o).split("#")[-1] in item_level and (s, RDF.type, B.Lineage) not in ag)
expect(f"no non-lineage adopts an item-level rule set in the shipped data file ({len(item_level)} such rule sets){'' if not leaks else ': ' + str(leaks)}", not leaks)
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/neutrality-probe#> .\n"
dt = lambda v: f'"{v}"^^xsd:dateTime'
BODY = f"""x:P a backlog:Executor_IndividualHuman .
x:W1 a backlog:Task ; backlog:hasState backlog:Done ; backlog:responsible x:P ; backlog:verifiedBy x:P .
x:W2 a backlog:Task ; backlog:hasState backlog:Proposed ; backlog:responsible x:P ; backlog:startedAt {dt("2026-10-14T09:00:00Z")} .
x:W3 a backlog:Task ; backlog:hasState backlog:Done ; backlog:responsible x:P ; backlog:startedAt {dt("2026-10-14T00:00:00Z")} ; backlog:finishedAt {dt("2026-10-14T00:00:00Z")} , {dt("2026-10-15T10:00:00Z")} .
x:W4 a backlog:Task ; backlog:hasState backlog:InProgress ; backlog:responsible x:P ; backlog:startedAt {dt("2026-10-14T09:00:00Z")} .
x:E1 a backlog:TransitionEvent ; backlog:transitionedItem x:W4 ; backlog:viaTransition backlog:T_Start ; backlog:transitionedAt {dt("2026-10-14T09:00:00Z")} .
"""
REGALL = "x:Reg a backlog:Backlog ; backlog:isRegisterRoot true ; backlog:adoptsRuleSet backlog:RS_StatusHistoryRecorded , backlog:RS_FlowPointsRecorded , backlog:RS_IndependentVerification .\n"
RULES = re.compile(r"\] W\d\s+(G112|G113|G115):")
def count(*files):
    out = subprocess.run([sys.executable, val, *files], capture_output=True, text=True, timeout=900).stdout
    return sum(1 for ln in out.splitlines() if "[Violation]" in ln and RULES.search(ln))
with tempfile.TemporaryDirectory() as d:
    c1 = os.path.join(d, "consumer.ttl"); open(c1, "w").write(HEAD + BODY)
    c2 = os.path.join(d, "adopting.ttl"); open(c2, "w").write(HEAD + REGALL + BODY)
    n_whole = count(c1, ABOX); n_adopt = count(c2)
    expect(f"a consumer graph loaded with the whole shipped data file gets no recording or verification result (got {n_whole})", n_whole == 0)
    expect(f"the same items under a consumer register that adopts get results (got {n_adopt}), so zero above is not for want of a reading", n_adopt > 0)
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
