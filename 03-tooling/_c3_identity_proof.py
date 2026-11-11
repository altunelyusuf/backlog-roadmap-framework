#!/usr/bin/env python3
"""Proof for C3 of the IPage box-tool-for-an-adopting-register handover, against backlog_box_step_v2_0_0.py:
a story named however the adopting register likes (not the framework's ST_<prefix>_<key> pattern) is found, opened,
worked, and closed by its own identity, and every event the tool writes along the way points at the real subject."""
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


work = tempfile.mkdtemp()
pk = os.path.join(work, "pkg")
os.makedirs(os.path.join(pk, "01-ontologies"))
os.makedirs(os.path.join(pk, "03-tooling"))
shutil.copy(TOOL, os.path.join(pk, "03-tooling", os.path.basename(TOOL)))
reg = os.path.join(pk, "01-ontologies", "ipage_abox_v0_1_0.ttl")
# Story4_D1 -- a name that does NOT match ST_<prefix>_<key> at all, exactly as the handover's own example names it.
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


def run(*a):
    r = subprocess.run([sys.executable, os.path.join(pk, "03-tooling", os.path.basename(TOOL)), reg, "--lineage", "pcl:D1", "--prefix", "D1"] + list(a),
                        capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


# open using the story's OWN name directly, not a short key the tool would turn into ST_D1_<key>
rc, out = run("open", "1", "t", "g", "Story4_D1", "--capacity", "3")
expect("open succeeds, finding the story by its own name (Story4_D1), not a ST_<prefix>_<key> pattern (C3)", rc == 0 and "now InProgress" in out)
after = open(reg).read()
expect("the story itself is addressed as pcl:Story4_D1, unretouched", "pcl:Story4_D1 a backlog:Story" in after and re.search(r"pcl:Story4_D1 a backlog:Story .*?backlog:hasState backlog:InProgress", after, re.S) is not None)
expect("the planning/refinement events the tool wrote point AT the real subject (plansItem/refines/transitionedItem pcl:Story4_D1), not a phantom ST_D1_Story4_D1", "pcl:ST_D1_Story4_D1" not in after and after.count("pcl:Story4_D1") >= 4)

time.sleep(1.1)
rc, out = run("act", "1", "Story4_D1", "worked on it")
expect("a checkpoint records against the real story name", rc == 0 and "checkpoint 1" in out)

art = os.path.join(pk, "03-tooling", "artifact.txt")
open(art, "w").write("evidence\n")
spec = {"stories": {"Story4_D1": {"artifact": "03-tooling/artifact.txt", "method": "m", "tool": "t", "harness": "h", "demo": "d", "result": "r"}},
        "run_result": "ok", "release_title": "rel", "findings": [{"key": "F1", "root_cause": "rc", "remedy": "rm", "story": "Story4_D1"}], "observations": []}
sp = os.path.join(work, "spec.json")
json.dump(spec, open(sp, "w"))
rc, out = run("close", "1", sp)
expect("close succeeds, resolving Story4_D1 throughout (not a phantom ST_D1_Story4_D1)", rc == 0 and "closed" in out)
final = open(reg).read()
expect("the story ends Done, still addressed as pcl:Story4_D1", re.search(r"pcl:Story4_D1 a backlog:Story .*?backlog:hasState backlog:Done", final, re.S) is not None)
expect("no phantom ST_D1_Story4_D1 Story subject was ever minted or referenced as a target (ST_D1_Story4_D1 appears only inside the tool's own event-id names, never after plansItem/refines/transitionedItem/closesStory/deploysItem/relatesToWorkItem)",
       "a backlog:Story" not in final.split("ST_D1_Story4_D1", 1)[-1].split("\n", 1)[0] if "ST_D1_Story4_D1" in final else True
       and not re.search(r"(?:plansItem|refines|transitionedItem|closesStory|deploysItem|relatesToWorkItem|harnessFor|demonstratesItem)\s+(?:fw|pcl):ST_D1_Story4_D1\b", final))
expect("the finding relates to the real story", re.search(r"relatesToWorkItem pcl:Story4_D1", final) is not None)
expect("the review/release close out against the real story", re.search(r"closesStory pcl:Story4_D1", final) is not None and re.search(r"deploysItem pcl:Story4_D1", final) is not None)

shutil.rmtree(work, ignore_errors=True)
print("VERDICT: %s" % ("PASS -- %d expectations hold" % COUNT[0] if not bad else "FAIL -- " + "; ".join(bad)))
if bad:
    print(out[-1200:])
sys.exit(1 if bad else 0)
