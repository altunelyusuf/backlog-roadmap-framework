#!/usr/bin/env python3
"""backlog_archive_mission_history_probe v1.0.0 -- the statements a mission replaced are archived with its lineage (G121).

Plants a ledger: lineage LA pursues MA3, which replaced MA2, which replaced MA1, which replaced MB, the mission lineage LB pursues. MA1 and MA2 each have a
closure report and MA2 a goal. Archives LA and checks that MA1, MA2, their reports and the goal moved with it, that MB (another lineage's) and its lineage stayed,
and that nothing the live ledger keeps points at a moved record except the archive entry. Exit 0 when all hold, 3 otherwise.  (--deps prints the tool it runs)
"""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda x: [int(n) for n in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", x)[0]]
tool = sorted(glob.glob(os.path.join(HERE, "backlog_lineage_archive_v*.py")), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(tool); sys.exit(0)
from rdflib import Graph, Namespace, RDF
X = Namespace("http://example.org/hist#")
REG = '''@prefix backlog: <http://example.org/backlog#> .
@prefix h: <http://example.org/hist#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
<http://example.org/hist-ledger> a owl:Ontology ; owl:versionIRI <http://example.org/hist-ledger/1.0.0> ; owl:versionInfo "1.0.0" ; owl:priorVersion <http://example.org/hist-ledger/0.9.0> .
h:Register a backlog:Backlog ; backlog:isRegisterRoot true .
h:LA a backlog:Lineage ; backlog:lineageForMission h:MA3 ; backlog:lineageArchived false .
h:MA3 a backlog:Mission ; backlog:hasMissionOutcome backlog:Out_Achieved ; backlog:outcomeRationale "done" ; backlog:supersedesMission h:MA2 .
h:MA2 a backlog:Mission ; backlog:supersedesMission h:MA1 .
h:MA1 a backlog:Mission ; backlog:hasMissionOutcome backlog:Out_Achieved ; backlog:outcomeRationale "done" ; backlog:supersedesMission h:MB .
h:SA a backlog:Story ; backlog:belongsToLineage h:LA ; backlog:hasState backlog:Done .
h:RA3 a backlog:ClosureReport ; backlog:closesForMission h:MA3 .
h:RA2 a backlog:ClosureReport ; backlog:closesForMission h:MA2 .
h:RA1 a backlog:ClosureReport ; backlog:closesForMission h:MA1 .
h:GA2 a backlog:Goal ; backlog:contributesToMission h:MA2 .
h:LB a backlog:Lineage ; backlog:lineageForMission h:MB ; backlog:lineageArchived false .
h:MB a backlog:Mission ; backlog:hasMissionOutcome backlog:Out_Achieved ; backlog:outcomeRationale "done" .
h:SB a backlog:Story ; backlog:belongsToLineage h:LB ; backlog:hasState backlog:Done .
h:RB a backlog:ClosureReport ; backlog:closesForMission h:MB .
'''
bad = []
with tempfile.TemporaryDirectory() as d:
    reg = os.path.join(d, "ledger_v1_0_0.ttl"); open(reg, "w").write(REG)
    r = subprocess.run([sys.executable, "-B", tool, reg, "LA", "--apply"], capture_output=True, text=True)
    live = os.path.join(d, "ledger_v1_1_0.ttl")
    if r.returncode != 0 or not os.path.isfile(live): bad.append("the archival did not apply: " + (r.stdout + r.stderr)[-300:])
    else:
        L = Graph().parse(live, format="turtle")
        arch = sorted(glob.glob(os.path.join(d, "archive", "ledger_archive_v*.ttl")), key=sv)[-1]
        A = Graph().parse(arch, format="turtle")
        for n in ("MA1", "MA2", "RA1", "RA2", "GA2"):
            if (X[n], None, None) in L: bad.append(f"{n} is still live")
            if (X[n], None, None) not in A: bad.append(f"{n} is not in the archive")
        for n in ("MB", "LB", "SB", "RB"):
            if (X[n], None, None) not in L: bad.append(f"{n} (another lineage's) left the live ledger")
            if (X[n], None, None) in A: bad.append(f"{n} (another lineage's) was archived")
        gone = {X[n] for n in ("MA1", "MA2", "RA1", "RA2", "GA2")}
        dangling = [(s, p, o) for s, p, o in L if o in gone]
        if dangling: bad.append(f"{len(dangling)} live triple(s) still point at a moved record")
for b in bad: print("FAIL", b)
print("archive mission-history probe:", "PASS -- the replaced statements move with their lineage, another lineage's stay" if not bad else f"{len(bad)} failure(s)")
sys.exit(3 if bad else 0)
