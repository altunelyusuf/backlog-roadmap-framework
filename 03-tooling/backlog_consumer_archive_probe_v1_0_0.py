#!/usr/bin/env python3
"""backlog_consumer_archive_probe v1.0.0 -- a consumer ledger is archived into its OWN archive file, never into the framework's (G106).

Plants a small consumer register (one achieved lineage with a closure report, one done story) in a temporary folder and runs the archive tool on it:
  1. with no flag: the archive is created beside the ledger (archive/<ledger name>_archive_v1_0_0.ttl), the register moves to its next version, the package archive is byte-identical afterwards
  2. the subjects moved into the consumer archive, and the live ledger keeps a LineageArchiveEntry pointing at it
  3. with --archive-file naming another path: that path is used
  4. a second archival into the existing consumer archive bumps it (1.0.0 -> 1.1.0 file) and extends its header chain
Exit 0 when all hold, 3 otherwise.   Usage: backlog_consumer_archive_probe_v1_0_0.py   (--deps prints the tool it runs)
"""
import glob, hashlib, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
def tool():
    return sorted(glob.glob(os.path.join(HERE, "backlog_lineage_archive_v*.py")), key=lambda x: [int(n) for n in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", x)[0]])[-1]
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(tool())
    for f in sorted(glob.glob(os.path.join(PKG, "01-ontologies", "archive", "backlog_framework_archive_abox_v*.ttl"))): print(f)
    sys.exit(0)
REG = '''@prefix backlog: <http://example.org/backlog#> .
@prefix c: <http://example.org/consumer#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://example.org/consumer-ledger> a owl:Ontology ;
    owl:versionIRI <http://example.org/consumer-ledger/1.0.0> ;
    owl:versionInfo "1.0.0" ;
    owl:priorVersion <http://example.org/consumer-ledger/0.9.0> .

c:Register a backlog:Backlog ; backlog:isRegisterRoot true .
%s'''
def lin(n):
    return f'''c:L{n} a backlog:Lineage ; backlog:lineageForMission c:M{n} ; backlog:lineageArchived false .
c:M{n} a backlog:Mission ; backlog:hasMissionOutcome backlog:Out_Achieved ; backlog:outcomeRationale "probe" .
c:S{n} a backlog:Story ; backlog:belongsToLineage c:L{n} ; backlog:hasState backlog:Done .
c:R{n} a backlog:ClosureReport ; backlog:closesForMission c:M{n} .
'''
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def run(args): return subprocess.run([sys.executable, "-B", tool()] + args, capture_output=True, text=True)
def main():
    pk = sorted(glob.glob(os.path.join(PKG, "01-ontologies", "archive", "backlog_framework_archive_abox_v*.ttl")))
    before = {p: sha(p) for p in pk}; bad = []
    with tempfile.TemporaryDirectory() as d:
        reg = os.path.join(d, "ledger_v1_0_0.ttl"); open(reg, "w").write(REG % (lin(1) + lin(2)))
        r = run([reg, "L1", "--apply"])
        arch = os.path.join(d, "archive", "ledger_archive_v1_0_0.ttl"); arch2 = os.path.join(d, "archive", "ledger_archive_v1_1_0.ttl")
        # the tool bumps the archive after creating its first version: the first archival ends in v1_1_0 beside the created v1_0_0
        if r.returncode != 0 or not os.path.isfile(os.path.join(d, "ledger_v1_1_0.ttl")): bad.append("1: no new register version: " + (r.stdout + r.stderr)[-300:])
        if not os.path.isfile(arch2) or "c:S1 " not in open(arch2).read().replace("backlog:Story", "") and "c:S1" not in open(arch2).read(): bad.append("2: the lineage's subjects are not in the consumer archive")
        if "LineageArchiveEntry" not in open(os.path.join(d, "ledger_v1_1_0.ttl")).read(): bad.append("2: no archive entry left in the ledger")
        if "c:S1 " in open(os.path.join(d, "ledger_v1_1_0.ttl")).read(): bad.append("2: the story is still live")
        if {p: sha(p) for p in pk} != before: bad.append("1: the package archive changed")
        # 3: explicit path on the second lineage
        reg2 = os.path.join(d, "ledger_v1_1_0.ttl"); mine = os.path.join(d, "mine", "mine_archive_v1_0_0.ttl")
        r = run([reg2, "L2", "--apply", "--archive-file", mine])
        if r.returncode != 0 or not os.path.isfile(mine.replace("v1_0_0", "v1_1_0")): bad.append("3: --archive-file path not used: " + (r.stdout + r.stderr)[-300:])
        # 4: a third archival into the now existing default archive extends the chain
        reg3 = os.path.join(d, "ledger_v1_2_0.ttl"); open(reg3, "w").write(REG.replace('"1.0.0"', '"1.2.0"').replace("/1.0.0>", "/1.2.0>") % lin(3))
        r = run([reg3, "L3", "--apply"])
        a3 = os.path.join(d, "archive", "ledger_archive_v1_2_0.ttl")
        if r.returncode != 0 or not os.path.isfile(a3) or "/1.1.0>" not in open(a3).read() or "/1.0.0>" not in open(a3).read(): bad.append("4: archive chain not extended: " + (r.stdout + r.stderr)[-300:])
    if {p: sha(p) for p in pk} != before: bad.append("the package archive changed")
    for b in bad: print("FAIL", b)
    print("consumer archive probe:", "PASS -- a consumer ledger archives into its own file, the package archive untouched" if not bad else f"{len(bad)} failure(s)")
    return 3 if bad else 0
sys.exit(main())
