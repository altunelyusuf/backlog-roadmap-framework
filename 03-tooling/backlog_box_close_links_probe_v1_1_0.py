#!/usr/bin/env python3
"""backlog_box_close_links_probe v1.0.0 (Lineage 29, package 17, box 49; course-management handover of 2026-11-14, G236, gaps 1 and 2 and this lineage's own finding).

A tiny package inside a throwaway git repository, as the box tool probe v1.9.0 builds one, whose story holds its criterion, objective and metric under names this tool does not mint, linked by
hasAcceptanceCriterion, pursuesObjective and hasSuccessMetric. The box is opened, a checkpoint recorded and the close run as it is run for real. Cases: a close whose spec names no finding is refused and
the register is unchanged; with a finding the close succeeds; the evidence attests, and the demo is shown against, the story's own criterion; the closing observation is about the objective and metric the story
pursues, not about names the tool would mint; the story is given an execution modality, the spec's own when it names one, and one it already holds is kept; a story with no links is still closed under the
names the tool mints. Exit 0 when every expectation holds."""
import os, re, shutil, subprocess, sys, tempfile, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = sorted((f for f in os.listdir(HERE) if re.match(r"backlog_box_step_v\d+_\d+_\d+\.py$", f)), key=lambda f: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", f)[0]])[-1]
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(os.path.join(HERE, TOOL)); sys.exit(0)
bad, COUNT = [], [0]
def expect(name, ok):
    COUNT[0] += 1
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
HDR = """@prefix fw: <http://example.org/backlog-framework-register#> .
@prefix backlog: <http://example.org/backlog#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
<http://example.org/backlog> owl:versionInfo "1.1.0" .
fw:L_AdaptiveProof a backlog:Lineage ; backlog:hasLineageStatus backlog:LS_InProgress .
fw:KO a backlog:KickOff ; backlog:kicksOffLineage fw:L_AdaptiveProof .
"""
LINKED = HDR + """fw:ST_AP_A a backlog:Story ; backlog:hasIdentifier "A" ; backlog:hasState backlog:Proposed ; backlog:hasEffort 3.0 ;
    backlog:belongsToLineage fw:L_AdaptiveProof ; backlog:producedByStage fw:Out_B ;
    backlog:hasAcceptanceCriterion fw:Crit_Alpha , fw:Crit_Beta ; backlog:pursuesObjective fw:Goal_Obj_Z %s.
fw:Crit_Alpha a backlog:AcceptanceCriterion ; backlog:hasGherkinText "Given a, When b, Then c." .
fw:Crit_Beta a backlog:AcceptanceCriterion ; backlog:hasGherkinText "Given d, When e, Then f." .
fw:Goal_Obj_Z a backlog:Objective ; backlog:hasSuccessMetric fw:Gauge_Z .
fw:Gauge_Z a backlog:Metric .
"""
PLAIN = HDR + """fw:ST_AP_A a backlog:Story ; backlog:hasIdentifier "A" ; backlog:hasState backlog:Proposed ; backlog:hasEffort 3.0 ;
    backlog:belongsToLineage fw:L_AdaptiveProof ; backlog:producedByStage fw:Out_B .
fw:AC_AP_A a backlog:AcceptanceCriterion ; backlog:hasGherkinText "Given a, When b, Then c." .
fw:ST_AP_A backlog:hasAcceptanceCriterion fw:AC_AP_A .
"""
ART = "03-tooling/artifact.txt"
def scenario(reg_text, extra_spec=None, findings=True, label=""):
    work = tempfile.mkdtemp(); pk = os.path.join(work, "pkg"); os.makedirs(os.path.join(pk, "01-ontologies")); os.makedirs(os.path.join(pk, "03-tooling"))
    shutil.copy(os.path.join(HERE, TOOL), os.path.join(pk, "03-tooling", TOOL))
    REG = os.path.join(pk, "01-ontologies", "backlog_abox_v1_1_0.ttl"); open(REG, "w").write(reg_text)
    git = lambda *a: subprocess.run(["git", "-C", pk] + list(a), capture_output=True, text=True)
    subprocess.run(["git", "-C", work, "init", "-q"]); open(os.path.join(pk, "03-tooling", "other.py"), "w").write("x = 1\n")
    git("add", "-A"); git("-c", "user.email=p@p", "-c", "user.name=p", "commit", "-qm", "p"); git("update-ref", "refs/remotes/origin/main", "HEAD")
    def run(*a):
        r = subprocess.run([sys.executable, os.path.join(pk, "03-tooling", TOOL), REG] + list(a), capture_output=True, text=True); return r.returncode, r.stdout + r.stderr
    spec = {"stories": {"A": {"artifact": ART, "method": "m", "tool": "t", "harness": "h", "demo": "d", "result": "r"}}, "run_result": "ok", "release_title": "rel",
            "findings": [{"key": "F", "root_cause": "rc", "remedy": "rm"}] if findings else [], "observations": [{"obj": "A", "value": 1, "method": "m"}]}
    if extra_spec: spec.update(extra_spec)
    sp = os.path.join(work, "spec.json"); json.dump(spec, open(sp, "w"))
    rc, out = run("open", "1", "t", "g", "A", "--capacity", "3")
    if rc != 0: print(out); raise SystemExit("open failed")
    open(os.path.join(pk, ART), "w").write("evidence\n"); time.sleep(1.1); run("act", "1", "A", "worked")
    return REG, run, sp
# 1 a close that names no finding is refused and writes nothing
REG, run, sp = scenario(LINKED % "", findings=False)
before = open(REG).read(); rc, out = run("close", "1", sp)
expect("a close whose spec names no finding is refused, naming what to give", rc != 0 and "names no finding" in out)
expect("the refused close wrote nothing", open(REG).read() == before)
# 2 with a finding, names the story's own records
REG, run, sp = scenario(LINKED % "")
rc, out = run("close", "1", sp); t = open(REG).read()
expect("a story whose records are named otherwise closes", rc == 0 and "closed" in out)
expect("the evidence attests the story's own criteria, not a name the tool would mint", "attestsCriterion fw:Crit_Alpha , fw:Crit_Beta" in t and "fw:AC_AP_A" not in t)
expect("the demo is shown against the story's own criterion", "demonstratedAgainst fw:Crit_Alpha" in t)
expect("each criterion is told its artifact", "fw:Crit_Alpha backlog:satisfiedByArtifact" in t and "fw:Crit_Beta backlog:satisfiedByArtifact" in t)
expect("the closing observation is about the objective and metric the story pursues", "observesMetric fw:Gauge_Z ; backlog:observationFor fw:Goal_Obj_Z" in t and "Obj_AP_A" not in t and "Metric_AP_A" not in t)
expect("the closed story is given an execution modality", "backlog:hasExecutionModality backlog:Mode_Automated" in t.split("fw:ST_AP_A backlog:finishedAt")[-1].split(" .")[0])
# 3 the spec's own modality; one the story already holds is kept
REG, run, sp = scenario(LINKED % "", {"modality": "Mode_Assisted"}); rc, out = run("close", "1", sp)
expect("the spec's own modality is written", rc == 0 and "backlog:hasExecutionModality backlog:Mode_Assisted" in open(REG).read().split("fw:ST_AP_A backlog:finishedAt")[-1].split(" .")[0])
REG, run, sp = scenario(LINKED % "; backlog:hasExecutionModality backlog:Mode_Manual "); rc, out = run("close", "1", sp)
expect("a modality the story already holds is kept: the closing statement adds none", rc == 0 and "Mode_Manual" in open(REG).read() and "hasExecutionModality" not in open(REG).read().split("fw:ST_AP_A backlog:finishedAt")[-1].split(" .")[0])
# 4 no links: the names the tool mints
REG, run, sp = scenario(PLAIN); rc, out = run("close", "1", sp); t = open(REG).read()
expect("a story with no such links still closes under the names this tool mints", rc == 0 and "attestsCriterion fw:AC_AP_A" in t and "observationFor fw:Obj_AP_A" in t)
print("VERDICT: %s -- %d expectations %s" % ("PASS" if not bad else "FAIL", COUNT[0], "hold" if not bad else "(%d failed)" % len(bad))); sys.exit(1 if bad else 0)
