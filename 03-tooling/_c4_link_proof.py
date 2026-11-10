#!/usr/bin/env python3
"""Proof for C4 of the IPage box-tool-for-an-adopting-register handover, against backlog_box_step_v2_0_0.py:
a planning event is found again at close by its link from the planning ceremony (includesPlanningEvent), not by
scanning for whatever Plan_ records happen to survive -- so deleting one outright (not just renaming it) is refused,
and "no records found" is never silently read as "nothing to close"."""
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


def fixture():
    work = tempfile.mkdtemp()
    pk = os.path.join(work, "pkg")
    os.makedirs(os.path.join(pk, "01-ontologies"))
    os.makedirs(os.path.join(pk, "03-tooling"))
    shutil.copy(TOOL, os.path.join(pk, "03-tooling", os.path.basename(TOOL)))
    reg = os.path.join(pk, "01-ontologies", "ipage_abox_v0_1_0.ttl")
    ttl = """@prefix pcl: <http://example.org/ipage-register#> .
@prefix backlog: <http://example.org/backlog#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
<http://example.org/ipage> owl:versionInfo "0.1.0" .
pcl:D1 a backlog:Lineage ; backlog:hasLineageStatus backlog:LS_InProgress .
pcl:KO a backlog:KickOff ; backlog:kicksOffLineage pcl:D1 .
pcl:Story4_D1 a backlog:Story ; backlog:hasIdentifier "4" ; backlog:hasState backlog:Proposed ; backlog:hasEffort 3.0 ;
    backlog:belongsToLineage pcl:D1 ; backlog:producedByStage pcl:Out_B .
pcl:AC_D1_Story4_D1 a backlog:AcceptanceCriterion ; backlog:hasGherkinText "Given a, When b, Then c." .
"""
    open(reg, "w").write(ttl)
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


# ---- planted fault: delete the planning event outright ----
work, pk, reg = fixture()
run(pk, reg, "open", "1", "t", "g", "Story4_D1", "--capacity", "3")
time.sleep(1.1)
run(pk, reg, "act", "1", "Story4_D1", "worked")
txt = open(reg).read()
m = re.search(r"pcl:Plan_D1_1_Story4_D1 a backlog:PlanningEvent[^\n]*\n(?:[^\n]*\n)*?[^\n]*\.\n", txt)
expect("the planning event to delete is found in the fixture (sanity check on the test itself)", m is not None)
open(reg, "w").write(txt[:m.start()] + txt[m.end():])
art = os.path.join(pk, "03-tooling", "artifact.txt")
open(art, "w").write("evidence\n")
spec = {"stories": {"Story4_D1": {"artifact": "03-tooling/artifact.txt", "method": "m", "tool": "t", "harness": "h", "demo": "d", "result": "r"}},
        "run_result": "ok", "release_title": "rel", "findings": [], "observations": []}
sp = os.path.join(work, "spec.json")
json.dump(spec, open(sp, "w"))
rc, out = run(pk, reg, "close", "1", sp)
expect("close is refused when a planning event linked from the ceremony was deleted outright (C4), not silently treated as an empty box", rc != 0 and "gone" in out)
shutil.rmtree(work, ignore_errors=True)

# ---- positive control: the same box, nothing deleted, still closes ----
work2, pk2, reg2 = fixture()
run(pk2, reg2, "open", "1", "t", "g", "Story4_D1", "--capacity", "3")
time.sleep(1.1)
run(pk2, reg2, "act", "1", "Story4_D1", "worked")
art2 = os.path.join(pk2, "03-tooling", "artifact.txt")
open(art2, "w").write("evidence\n")
sp2 = os.path.join(work2, "spec.json")
json.dump(spec, open(sp2, "w"))
rc2, out2 = run(pk2, reg2, "close", "1", sp2)
expect("the same box closes normally when nothing was deleted (positive control)", rc2 == 0 and "closed" in out2)
shutil.rmtree(work2, ignore_errors=True)

print("VERDICT: %s" % ("PASS -- %d expectations hold" % COUNT[0] if not bad else "FAIL -- " + "; ".join(bad)))
if bad:
    print(out[-800:])
sys.exit(1 if bad else 0)
