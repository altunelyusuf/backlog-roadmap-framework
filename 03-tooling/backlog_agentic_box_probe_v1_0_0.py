#!/usr/bin/env python3
"""backlog_agentic_box_probe v1.0.0 -- a box recorded by the step tool in an agentic lineage draws no violation of the two agentic rule sets (Lineage 24, D2).

The tool is run as it is run for real in a throwaway package, and the REAL validator then judges the register it wrote (a stub would have hidden the fault of Lineage 23): no violation of agent accountability or independent verification. Planted: a verifier that is the maker, a missing review file, and the verifier link removed after the close (the validator must then name the fault). v1.0.0 - the first version. -- the step tool accepts a box recorded in order and refuses each fault made by hand (Lineage 21, D3), and reads the obligations of a status from the register (Lineage 22, D3).

A tiny package inside a throwaway git repository (the package sits one folder down, as the real one does). The tool is run as it is run for real; each refusal is planted and the same box then passes once the fault is removed
(a tool that refuses is not thereby correct). Planted: work before the box opened, a story not Proposed, a box opened twice, a close with no checkpoint, a name changed by hand, a published
statement edited away, an artifact older than the box. Positive: open, checkpoint and close leave a Done story with a single state, a Done box and a deployment unit.
"""
import os, re, shutil, subprocess, sys, tempfile, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
VAL = sorted((os.path.join(HERE, f) for f in os.listdir(HERE) if re.match(r"backlog_validate_v\d+_\d+_\d+\.py$", f)), key=lambda f: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", f)[0]])[-1]
MON = sorted((f for f in os.listdir(HERE) if re.match(r"backlog_agent_monitor_v\d+_\d+_\d+\.py$", f)), key=lambda f: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", f)[0]])[-1]
if sys.argv[1:] == ["--deps"]:
    print("\n".join([os.path.join(HERE, f) for f in os.listdir(HERE) if re.match(r"backlog_box_step_v\d+", f)] + [VAL, os.path.join(HERE, MON), os.path.abspath(__file__)])); sys.exit(0)
TOOL = sorted((f for f in os.listdir(HERE) if re.match(r"backlog_box_step_v\d+_\d+_\d+\.py$", f)), key=lambda f: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", f)[0]])[-1]
bad, COUNT = [], [0]
def expect(name, ok):
    COUNT[0] += 1
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
work = tempfile.mkdtemp()
pk = os.path.join(work, "pkg"); os.makedirs(os.path.join(pk, "01-ontologies")); os.makedirs(os.path.join(pk, "03-tooling"))
shutil.copy(os.path.join(HERE, TOOL), os.path.join(pk, "03-tooling", TOOL)); shutil.copy(os.path.join(HERE, MON), os.path.join(pk, "03-tooling", MON))
REG = os.path.join(pk, "01-ontologies", "backlog_abox_v1_1_0.ttl")
open(REG, "w").write("""@prefix fw: <http://example.org/backlog-framework-register#> .
@prefix backlog: <http://example.org/backlog#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
<http://example.org/backlog> owl:versionInfo "1.1.0" .
fw:L_AdaptiveProof a backlog:Lineage ; backlog:hasLineageStatus backlog:LS_InProgress .
fw:KO a backlog:KickOff ; backlog:kicksOffLineage fw:L_AdaptiveProof .
fw:L_AdaptiveProof backlog:openedWithProfile backlog:Profile_AgenticAdaptive ;
    backlog:adoptsRuleSet backlog:RS_AgentAccountability , backlog:RS_IndependentVerification ;
    backlog:humanApprovalLevel 3 .
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
def judged(path):
    out = subprocess.run([sys.executable, VAL, path], capture_output=True, text=True, timeout=900).stdout
    return [ln for ln in out.splitlines() if "[Violation]" in ln and ("G118" in ln or "G109" in ln)]
rc, out = run("open", "1", "t", "g", "A", "--capacity", "3")
expect("the box opens in an agentic lineage", rc == 0 and "now InProgress" in out)
txt = open(REG).read()
expect("the builder run is recorded and the story names it as responsible", "fw:Run_AP_1_Builder a backlog:ExecutorInstance" in txt and "backlog:responsible fw:Run_AP_1_Builder" in txt)
expect("every move written at the opening names the run that made it", txt.count("transitionedBy backlog:Builder") == txt.count("transitionedByExecutor fw:Run_AP_1_Builder") > 0)
open(os.path.join(pk, ART), "w").write("evidence\n")
time.sleep(1.1); rc, out = run("act", "1", "A", "worked")
spec = {"stories": {"A": {"artifact": ART, "method": "m", "tool": "t", "harness": "h", "demo": "d", "result": "r"}}, "run_result": "ok", "release_title": "rel",
        "findings": [{"key": "F", "root_cause": "rc", "remedy": "rm"}], "observations": [{"obj": "X", "value": 1, "method": "m"}]}
SP = os.path.join(work, "spec.json")
json.dump(spec, open(SP, "w"))
rc, out = run("close", "1", SP)
expect("close is refused in an agentic lineage when no verifying agent is named", rc != 0 and "verifying agent" in out)
spec["verifier"] = {"agent": "Builder", "review": "03-tooling/review.txt"}; json.dump(spec, open(SP, "w"))
rc, out = run("close", "1", SP)
expect("close is refused when the verifier is the maker", rc != 0 and "verifier is the maker" in out)
spec["verifier"] = {"agent": "an independent reviewer", "review": "03-tooling/review.txt"}; json.dump(spec, open(SP, "w"))
rc, out = run("close", "1", SP)
expect("close is refused when the review file does not exist", rc != 0 and "review file" in out)
open(os.path.join(pk, "03-tooling", "review.txt"), "w").write("The claims hold.\n")
before = open(REG).read()
rc, out = run("close", "1", SP)
final = open(REG).read()
expect("the box closes once a review by another agent is kept", rc == 0 and "closed" in out)
expect("the four roles are recorded as four runs of four definitions", all(("fw:Run_AP_1_%s a backlog:ExecutorInstance" % r) in final for r in ("Builder", "Overseer", "Verifier", "Approver")) and all(("backlog:instanceOf fw:Exec_%s" % r) in final for r in ("Builder", "Overseer", "Verifier", "Approver")))
expect("the Done story names the runs that oversaw, verified and approved it", "backlog:overseenBy fw:Run_AP_1_Overseer ; backlog:verifiedBy fw:Run_AP_1_Verifier ; backlog:approvedBy fw:Run_AP_1_Approver" in final)
expect("every move names the run that made it", final.count("transitionedBy backlog:Builder") == final.count("transitionedByExecutor fw:Run_AP_1_Builder"))
v = judged(REG)
expect("the REAL validator draws no violation of the two agentic rule sets on the register the tool wrote", v == [])
broken = os.path.join(work, "broken.ttl"); open(broken, "w").write(final.replace("backlog:verifiedBy fw:Run_AP_1_Verifier ;", ""))
expect("the same register without the verifier link is refused by the real validator (the probe can fail)", len(judged(broken)) >= 1)
shutil.rmtree(work, ignore_errors=True)
print("VERDICT: %s" % ("PASS -- %d expectations hold" % COUNT[0] if not bad else "FAIL -- " + "; ".join(bad)))
sys.exit(1 if bad else 0)
