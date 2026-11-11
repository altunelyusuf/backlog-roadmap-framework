#!/usr/bin/env python3
"""Proof for C5 of the IPage box-tool-for-an-adopting-register handover, against backlog_box_step_v2_0_0.py:
a box planned in advance (Proposed, with its base plan and member stories) opens in place the same way whether
the register is handed to the tool as authored or after rdflib has reserialised it -- exactly one Iteration
record results, and the base plan is unchanged, not duplicated."""
import os, re, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "backlog_box_step_v2_0_0.py")
bad, COUNT = [], [0]


def expect(name, ok):
    COUNT[0] += 1
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok:
        bad.append(name)


def git(pk, *a):
    return subprocess.run(["git", "-C", pk] + list(a), capture_output=True, text=True)


TTL = """@prefix pcl: <http://example.org/ipage-register#> .
@prefix backlog: <http://example.org/backlog#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
<http://example.org/ipage> owl:versionInfo "0.1.0" .
pcl:D1 a backlog:Lineage ; backlog:hasLineageStatus backlog:LS_InProgress .
pcl:KO a backlog:KickOff ; backlog:kicksOffLineage pcl:D1 .
pcl:Story4_D1 a backlog:Story ; backlog:hasIdentifier "4" ; backlog:hasState backlog:Proposed ; backlog:hasEffort 3.0 ;
    backlog:memberOfContainer pcl:It_D1_1 ; backlog:belongsToLineage pcl:D1 ; backlog:producedByStage pcl:Out_B .
pcl:AC_D1_Story4_D1 a backlog:AcceptanceCriterion ; backlog:hasGherkinText "Given a, When b, Then c." .
pcl:It_D1_1 a backlog:Iteration ; backlog:hasIdentifier "D1-BOX-1" ; backlog:hasTitle "planned" ; backlog:hasSprintGoal "g" ;
    backlog:hasState backlog:Proposed ; backlog:hasCapacity 3.0 ; backlog:belongsToLineage pcl:D1 .
pcl:PB_D1_1 a backlog:PlanBaseline ; backlog:baselineFor pcl:It_D1_1 ; backlog:isCurrentBaseline true ;
    backlog:hasBaselineStart "2026-01-01T00:00:00Z"^^xsd:dateTime ; backlog:hasBaselineEnd "2026-01-01T04:00:00Z"^^xsd:dateTime .
"""


def one_pass(reserialize):
    work = tempfile.mkdtemp()
    pk = os.path.join(work, "pkg")
    os.makedirs(os.path.join(pk, "01-ontologies"))
    os.makedirs(os.path.join(pk, "03-tooling"))
    shutil.copy(TOOL, os.path.join(pk, "03-tooling", os.path.basename(TOOL)))
    reg = os.path.join(pk, "01-ontologies", "ipage_abox_v0_1_0.ttl")
    open(reg, "w").write(TTL)
    if reserialize:
        import rdflib
        g = rdflib.Graph().parse(reg, format="turtle")
        g.serialize(destination=reg, format="turtle")
    git(pk, "init", "-q")
    open(os.path.join(pk, "03-tooling", "other.py"), "w").write("x = 1\n")
    git(pk, "add", "-A")
    git(pk, "-c", "user.email=p@p", "-c", "user.name=p", "commit", "-qm", "p")
    git(pk, "update-ref", "refs/remotes/origin/main", "HEAD")

    def run(*a):
        r = subprocess.run([sys.executable, os.path.join(pk, "03-tooling", os.path.basename(TOOL)), reg, "--lineage", "pcl:D1", "--prefix", "D1"] + list(a),
                            capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    rc, out = run("open", "1", "t", "g", "Story4_D1", "--capacity", "3")
    final = open(reg).read()
    ok = (rc == 0 and "planned in advance" in out
          and final.count("pcl:It_D1_1 a backlog:Iteration") == 1
          and final.count("pcl:PB_D1_1 a backlog:PlanBaseline") == 1
          and re.search(r"pcl:It_D1_1 a backlog:Iteration .*?backlog:hasState backlog:InProgress ; backlog:iterationStart \"", final, re.S) is not None)
    shutil.rmtree(work, ignore_errors=True)
    return ok, out


ok1, out1 = one_pass(False)
expect("a planned box in the adopting namespace opens in place as authored (one Iteration, base plan unchanged)", ok1)
ok2, out2 = one_pass(True)
expect("the same result holds after the fixture is reserialised by rdflib first (C5/C1)", ok2)

print("VERDICT: %s" % ("PASS -- %d expectations hold" % COUNT[0] if not bad else "FAIL -- " + "; ".join(bad)))
if bad:
    print(out1[-800:]); print(out2[-800:])
sys.exit(1 if bad else 0)
