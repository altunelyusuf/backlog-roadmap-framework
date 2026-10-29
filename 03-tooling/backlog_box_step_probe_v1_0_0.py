#!/usr/bin/env python3
"""backlog_box_step_probe v1.0.0 -- the step tool accepts a box recorded in order and refuses each fault made by hand (Lineage 21, D3).

A tiny package inside a throwaway git repository (the package sits one folder down, as the real one does). The tool is run as it is run for real; each refusal is planted and the same box then passes once the fault is removed
(a tool that refuses is not thereby correct). Planted: work before the box opened, a story not Proposed, a box opened twice, a close with no checkpoint, a name changed by hand, a published
statement edited away, an artifact older than the box. Positive: open, checkpoint and close leave a Done story with a single state, a Done box and a deployment unit.
"""
import os, re, shutil, subprocess, sys, tempfile, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = sorted((f for f in os.listdir(HERE) if re.match(r"backlog_box_step_v\d+_\d+_\d+\.py$", f)), key=lambda f: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", f)[0]])[-1]
bad, COUNT = [], [0]
def expect(name, ok):
    COUNT[0] += 1
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
work = tempfile.mkdtemp()
pk = os.path.join(work, "pkg"); os.makedirs(os.path.join(pk, "01-ontologies")); os.makedirs(os.path.join(pk, "03-tooling"))
shutil.copy(os.path.join(HERE, TOOL), os.path.join(pk, "03-tooling", TOOL))
REG = os.path.join(pk, "01-ontologies", "backlog_abox_v1_1_0.ttl")
open(REG, "w").write("""@prefix fw: <http://example.org/backlog-framework-register#> .
@prefix backlog: <http://example.org/backlog#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
<http://example.org/backlog> owl:versionInfo "1.1.0" .
fw:L_AdaptiveProof a backlog:Lineage ; backlog:hasLineageStatus backlog:LS_InProgress .
fw:KO a backlog:KickOff .
fw:ST_AP_A a backlog:Story ; backlog:hasIdentifier "A" ; backlog:hasState backlog:Proposed ; backlog:hasEffort 3.0 ;
    backlog:belongsToLineage fw:L_AdaptiveProof ; backlog:producedByStage fw:Out_B .
fw:AC_AP_A a backlog:AcceptanceCriterion ; backlog:hasGherkinText "Given a, When b, Then c." .
fw:ST_AP_P a backlog:Story ; backlog:hasIdentifier "P" ; backlog:hasState backlog:InProgress ; backlog:hasEffort 1.0 ;
    backlog:belongsToLineage fw:L_AdaptiveProof ; backlog:producedByStage fw:Out_B .
""")
ART = "03-tooling/artifact.txt"
def git(*a): return subprocess.run(["git", "-C", pk] + list(a), capture_output=True, text=True)
def publish():
    git("add", "-A"); git("-c", "user.email=p@p", "-c", "user.name=p", "commit", "-qm", "p"); git("update-ref", "refs/remotes/origin/main", "HEAD")
subprocess.run(["git", "-C", work, "init", "-q"]); open(os.path.join(pk, "03-tooling", "other.py"), "w").write("x = 1\n"); publish()
def run(*a):
    r = subprocess.run([sys.executable, os.path.join(pk, "03-tooling", TOOL), REG] + list(a), capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr
OPEN = ["open", "1", "t", "g", "A", "--capacity", "3"]
spec = {"stories": {"A": {"artifact": ART, "method": "m", "tool": "t", "harness": "h", "demo": "d", "result": "r"}}, "run_result": "ok", "release_title": "rel",
        "findings": [{"key": "F", "root_cause": "rc", "remedy": "rm"}], "observations": [{"obj": "X", "value": 1, "method": "m"}]}
json.dump(spec, open(os.path.join(work, "spec.json"), "w"))
SP = os.path.join(work, "spec.json")

open(os.path.join(pk, "03-tooling", "other.py"), "w").write("x = 2\n")
rc, out = run(*OPEN)
expect("open is refused when a governed file already differs from the published tree", rc != 0 and "work began before the box was opened" in out)
open(os.path.join(pk, "03-tooling", "other.py"), "w").write("x = 1\n")
rc, out = run("open", "1", "t", "g", "P", "--capacity", "3")
expect("open is refused for a story that is not Proposed", rc != 0 and "not Proposed" in out)
rc, out = run(*OPEN)
expect("the same box opens once the fault is removed", rc == 0 and "now InProgress" in out)
rc2, out2 = run(*OPEN)
expect("a box already opened is not opened again", rc2 != 0 and "already has records" in out2)
txt = open(REG).read()
expect("the story moved to InProgress with one state and one start", txt.count("backlog:hasState backlog:InProgress") >= 2 and "T_Start" in txt)
open(os.path.join(pk, ART), "w").write("evidence\n")
rc, out = run("close", "1", SP)
expect("close is refused when no checkpoint was recorded in the box", rc != 0 and "composed in one pass" in out)
time.sleep(1.1)
rc, out = run("act", "1", "A", "worked")
expect("a checkpoint is recorded with the clock", rc == 0 and "checkpoint 1" in out)
cur = open(REG).read()
open(REG, "w").write(cur.replace("fw:Plan_AP_1_A ", "fw:Plan_AP_1_Renamed "))
rc, out = run("close", "1", SP)
expect("close is refused when an identifier written at the opening was renamed by hand", rc != 0 and "changed by hand" in out)
open(REG, "w").write(cur)
open(REG, "w").write(cur.replace("backlog:hasEffort 3.0 ;", "backlog:hasEffort 4.0 ;", 1))
rc, out = run("close", "1", SP)
expect("close is refused when a published statement was edited in place", rc != 0 and "gone or changed" in out)
open(REG, "w").write(cur)
os.utime(os.path.join(pk, ART), (1577836800, 1577836800))
rc, out = run("close", "1", SP)
expect("close is refused for an artifact older than the box", rc != 0 and "older than the box" in out)
os.utime(os.path.join(pk, ART), None)
_v = open(REG).read().replace('owl:versionInfo "1.1.0"', 'owl:versionInfo "1.2.0"'); open(REG, "w").write(_v)   # the version header moves with every release and is not an edit
rc, out = run("close", "1", SP)
final = open(REG).read()
expect("the same box closes once the faults are removed", rc == 0 and "closed" in out)
expect("the story is Done with one state, the box Done, the deployment unit recorded",
       len(re.findall(r"fw:ST_AP_A a backlog:Story .*?backlog:hasState backlog:(\w+)", final, re.S)) == 1
       and re.search(r"fw:ST_AP_A a backlog:Story .*?backlog:hasState backlog:Done", final, re.S) is not None
       and re.search(r"fw:It_AP_1 a backlog:Iteration .*?backlog:hasState backlog:Done", final, re.S) is not None and "fw:Rel_AP_1 a backlog:DeploymentUnit" in final)
import importlib.util
sp = importlib.util.spec_from_file_location("bs", os.path.join(HERE, TOOL)); bs = importlib.util.module_from_spec(sp); sp.loader.exec_module(bs)
a, b = bs.tick(), bs.tick()
expect("two records written back to back are at least one second apart", b > a)
shutil.rmtree(work, ignore_errors=True)
print("VERDICT: %s" % ("PASS -- %d expectations hold" % COUNT[0] if not bad else "FAIL -- " + "; ".join(bad)))
sys.exit(1 if bad else 0)
