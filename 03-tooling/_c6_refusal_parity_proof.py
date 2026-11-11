#!/usr/bin/env python3
"""Proof for C6 of the IPage box-tool-for-an-adopting-register handover, against backlog_box_step_v2_0_0.py:
every existing refusal still fires on an adopting register (prefix pcl:, not fw:), not only on the framework's own."""
import os, re, shutil, subprocess, sys, tempfile, json, time

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
pcl:Story4_D1 a backlog:Story ; backlog:hasIdentifier "4" ; backlog:hasState backlog:Proposed ; backlog:hasEffort 2.0 ;
    backlog:belongsToLineage pcl:D1 ; backlog:producedByStage pcl:Out_B .
pcl:Story5_D1 a backlog:Story ; backlog:hasIdentifier "5" ; backlog:hasState backlog:InProgress ; backlog:hasEffort 1.0 ;
    backlog:belongsToLineage pcl:D1 ; backlog:producedByStage pcl:Out_B .
pcl:AC_D1_Story4_D1 a backlog:AcceptanceCriterion ; backlog:hasGherkinText "Given a, When b, Then c." .
"""


def fresh():
    work = tempfile.mkdtemp()
    pk = os.path.join(work, "pkg")
    os.makedirs(os.path.join(pk, "01-ontologies"))
    os.makedirs(os.path.join(pk, "03-tooling"))
    shutil.copy(TOOL, os.path.join(pk, "03-tooling", os.path.basename(TOOL)))
    reg = os.path.join(pk, "01-ontologies", "ipage_abox_v0_1_0.ttl")
    open(reg, "w").write(TTL)
    git(pk, "init", "-q")
    open(os.path.join(pk, "03-tooling", "other.py"), "w").write("x = 1\n")
    git(pk, "add", "-A")
    git(pk, "-c", "user.email=p@p", "-c", "user.name=p", "commit", "-qm", "p")
    git(pk, "update-ref", "refs/remotes/origin/main", "HEAD")
    return work, pk, reg


def run(pk, reg, *a):
    r = subprocess.run([sys.executable, os.path.join(pk, "03-tooling", os.path.basename(TOOL)), reg, "--lineage", "pcl:D1", "--prefix", "D1"] + list(a),
                        capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


# 1. open refused when a governed file already differs from the published tree
work, pk, reg = fresh()
open(os.path.join(pk, "03-tooling", "other.py"), "w").write("x = 2\n")
rc, out = run(pk, reg, "open", "1", "t", "g", "Story4_D1", "--capacity", "3")
expect("open is refused when a governed file already differs from the published tree (adopting register)", rc != 0 and "work began before the box was opened" in out)
shutil.rmtree(work, ignore_errors=True)

# 2. open refused for a story that is not Proposed
work, pk, reg = fresh()
rc, out = run(pk, reg, "open", "1", "t", "g", "Story5_D1", "--capacity", "3")
expect("open is refused for a story that is not Proposed (adopting register)", rc != 0 and "not Proposed" in out)
shutil.rmtree(work, ignore_errors=True)

# 3. close refused when no checkpoint was recorded
work, pk, reg = fresh()
run(pk, reg, "open", "1", "t", "g", "Story4_D1", "--capacity", "3")
art = os.path.join(pk, "03-tooling", "artifact.txt")
open(art, "w").write("evidence\n")
spec = {"stories": {"Story4_D1": {"artifact": "03-tooling/artifact.txt", "method": "m", "tool": "t", "harness": "h", "demo": "d", "result": "r"}},
        "run_result": "ok", "release_title": "rel", "findings": [], "observations": []}
sp = os.path.join(work, "spec.json")
json.dump(spec, open(sp, "w"))
rc, out = run(pk, reg, "close", "1", sp)
expect("close is refused when no checkpoint was recorded (adopting register)", rc != 0 and "composed in one pass" in out)
shutil.rmtree(work, ignore_errors=True)

# 4. close refused when a published statement is gone or changed
work, pk, reg = fresh()
run(pk, reg, "open", "1", "t", "g", "Story4_D1", "--capacity", "3")
time.sleep(1.1)
run(pk, reg, "act", "1", "Story4_D1", "worked")
cur = open(reg).read()
open(reg, "w").write(cur.replace("backlog:hasEffort 2.0 ;", "backlog:hasEffort 9.0 ;", 1))
art = os.path.join(pk, "03-tooling", "artifact.txt")
open(art, "w").write("evidence\n")
sp = os.path.join(work, "spec.json")
json.dump(spec, open(sp, "w"))
rc, out = run(pk, reg, "close", "1", sp)
expect("close is refused when a published statement was edited in place (adopting register)", rc != 0 and "gone or changed" in out)
shutil.rmtree(work, ignore_errors=True)

# 5. close refused for an artifact older than the box
work, pk, reg = fresh()
run(pk, reg, "open", "1", "t", "g", "Story4_D1", "--capacity", "3")
time.sleep(1.1)
run(pk, reg, "act", "1", "Story4_D1", "worked")
art = os.path.join(pk, "03-tooling", "artifact.txt")
open(art, "w").write("evidence\n")
os.utime(art, (1577836800, 1577836800))
sp = os.path.join(work, "spec.json")
json.dump(spec, open(sp, "w"))
rc, out = run(pk, reg, "close", "1", sp)
expect("close is refused for an artifact older than the box (adopting register)", rc != 0 and "older than the box" in out)
shutil.rmtree(work, ignore_errors=True)

# 6. positive control: the same sequence, nothing planted, closes cleanly
work, pk, reg = fresh()
run(pk, reg, "open", "1", "t", "g", "Story4_D1", "--capacity", "3")
time.sleep(1.1)
run(pk, reg, "act", "1", "Story4_D1", "worked")
art = os.path.join(pk, "03-tooling", "artifact.txt")
open(art, "w").write("evidence\n")
sp = os.path.join(work, "spec.json")
json.dump(spec, open(sp, "w"))
rc, out = run(pk, reg, "close", "1", sp)
expect("the same box closes once nothing is planted (positive control, adopting register)", rc == 0 and "closed" in out)
shutil.rmtree(work, ignore_errors=True)

print("VERDICT: %s" % ("PASS -- %d expectations hold" % COUNT[0] if not bad else "FAIL -- " + "; ".join(bad)))
if bad:
    print(out[-800:])
sys.exit(1 if bad else 0)
