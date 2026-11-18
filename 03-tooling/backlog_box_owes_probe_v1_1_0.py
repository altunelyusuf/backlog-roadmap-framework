#!/usr/bin/env python3
"""backlog_box_owes_probe v1.0.0 (Lineage 29, package 17, box 50; course-management handover of 2026-11-14, G236, gap 3).

A tiny package inside a throwaway git repository whose lineage adopts an obligation set: a design task owes a class diagram and a sequence diagram at design level, a build task owes the general evidence class, a specification and an advisory deployment model. Cases: the opening prints what each typed task will owe, says which the tool writes and which are supplied in the register, leaves out an advisory obligation, and prints nothing when no set is adopted; the close with a list of model kinds records one model for each and the close with one kind still records one; the evidence of the build task is typed with the general evidence class when owed and only test evidence when not; an unknown kind in the list is refused. Exit 0 when every expectation holds."""
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

HDR2 = HDR.replace("fw:L_AdaptiveProof a backlog:Lineage ; backlog:hasLineageStatus backlog:LS_InProgress .", "fw:L_AdaptiveProof a backlog:Lineage ; backlog:hasLineageStatus backlog:LS_InProgress %s.")
STORY = """fw:ST_AP_A a backlog:Story ; backlog:hasIdentifier "A" ; backlog:hasState backlog:Proposed ; backlog:hasEffort 3.0 ;
    backlog:belongsToLineage fw:L_AdaptiveProof ; backlog:producedByStage fw:Out_B .
fw:AC_AP_A a backlog:AcceptanceCriterion ; backlog:hasGherkinText "Given a, When b, Then c." .
fw:ST_AP_A backlog:hasAcceptanceCriterion fw:AC_AP_A .
"""
def OB(i, tt, cls, kind=None, level=None, depth=None, sev="Required"):
    return "fw:%s a backlog:StageObligation ; backlog:obligationOfTaskType backlog:%s ; backlog:owesClass backlog:%s ;%s%s%s backlog:obligationSeverity backlog:Oblig_%s ; backlog:inObligationSet fw:OS_T .\n" % (i, tt, cls, " backlog:owesKind backlog:%s ;" % kind if kind else "", " backlog:owesLevel backlog:%s ;" % level if level else "", " backlog:owesDepth backlog:%s ;" % depth if depth else "", sev)
ADOPT = "; backlog:adoptsObligationSet fw:OS_T ; backlog:adoptionRecordedAtOpen true "
MODELS = OB("O1", "Task_DesignDefinition", "ModelArtifact", "Kind_ClassDiagram", "Level_Design") + OB("O2", "Task_DesignDefinition", "ModelArtifact", "Kind_SequenceDiagram", "Level_Design")
EVID = OB("O3", "Task_Implementation", "Evidence")
EXTRA = OB("O4", "Task_Implementation", "Specification", depth="Depth_FullyDeveloped") + OB("O5", "Task_DesignDefinition", "ModelArtifact", "Kind_DeploymentDiagram", "Level_Design", sev="Advisory")
ART = "03-tooling/artifact.txt"
def scenario(reg_text, spec_tasks, close=True, label=""):
    work = tempfile.mkdtemp(); pk = os.path.join(work, "pkg"); os.makedirs(os.path.join(pk, "01-ontologies")); os.makedirs(os.path.join(pk, "03-tooling"))
    shutil.copy(os.path.join(HERE, TOOL), os.path.join(pk, "03-tooling", TOOL))
    REG = os.path.join(pk, "01-ontologies", "backlog_abox_v1_1_0.ttl"); open(REG, "w").write(reg_text)
    git = lambda *a: subprocess.run(["git", "-C", pk] + list(a), capture_output=True, text=True)
    subprocess.run(["git", "-C", work, "init", "-q"]); open(os.path.join(pk, "03-tooling", "other.py"), "w").write("x = 1\n")
    git("add", "-A"); git("-c", "user.email=p@p", "-c", "user.name=p", "commit", "-qm", "p"); git("update-ref", "refs/remotes/origin/main", "HEAD")
    def run(*a):
        r = subprocess.run([sys.executable, os.path.join(pk, "03-tooling", TOOL), REG] + list(a), capture_output=True, text=True); return r.returncode, r.stdout + r.stderr
    spec = {"stories": {"A": {"artifact": ART, "method": "m", "tool": "t", "harness": "h", "demo": "d", "result": "r", "tasks": spec_tasks}}, "run_result": "ok", "release_title": "rel",
            "findings": [{"key": "F", "root_cause": "rc", "remedy": "rm"}], "observations": [{"obj": "A", "value": 1, "method": "m"}]}
    sp = os.path.join(work, "spec.json"); json.dump(spec, open(sp, "w"))
    rc, out = run("open", "1", "t", "g", "A:design+build", "--capacity", "3")
    if rc != 0: print(out); raise SystemExit("open failed")
    open(os.path.join(pk, ART), "w").write("evidence\n"); time.sleep(1.1); run("act", "1", "A", "worked")
    return REG, run, sp, out
T2 = {"design": {"artifact": ART, "tool": "t", "method": "m", "model_kinds": ["Kind_ClassDiagram", {"kind": "Kind_SequenceDiagram", "level": "Level_Design"}], "model_level": "Level_Design"}}
# 1 the opening says what is owed
REG, run, sp, out = scenario(HDR2 % ADOPT + STORY + MODELS + EVID + EXTRA, T2)
expect("the opening prints the class diagram the design task will owe", "the design task of story A owes ModelArtifact Kind_ClassDiagram Level_Design" in out)
expect("the opening prints the sequence diagram the design task will owe", "the design task of story A owes ModelArtifact Kind_SequenceDiagram Level_Design" in out)
expect("the opening says the close writes the models and the evidence", out.count("written by the close") >= 3)
expect("the opening says a class this tool does not write is to be supplied in the register", "the build task of story A owes Specification Depth_FullyDeveloped (not written by this tool: supply it in the register)" in out)
expect("an advisory obligation is not printed as owed", "Kind_DeploymentDiagram" not in out)
REG, run, sp, out = scenario(HDR2 % ADOPT + STORY + OB("O6", "Task_Implementation", "ModelArtifact", "Kind_ClassDiagram", "Level_Design"), {})
expect("a model owed by a build task is not claimed as written, since the close writes models only for design and architecture tasks", "the build task of story A owes ModelArtifact Kind_ClassDiagram Level_Design (not written by this tool: supply it in the register)" in out)
REG, run, sp, out = scenario(HDR2 % "" + STORY, {})
expect("a lineage that adopts no set is told nothing is owed", "owed at the close" not in out)
# 2 the close with a list of kinds
REG, run, sp, out = scenario(HDR2 % ADOPT + STORY + MODELS + EVID, T2)
rc, out = run("close", "1", sp); t = open(REG).read()
expect("a design task with two model kinds closes when the obligations ask for both", rc == 0 and "closed" in out)
expect("one model is recorded for each kind in the list", len(re.findall(r"a backlog:ModelArtifact ; backlog:hasModelKind backlog:Kind_(?:Class|Sequence)Diagram ; backlog:hasModelLevel backlog:Level_Design", t)) == 2)
expect("each model is produced by the design task", t.count("backlog:producesModelArtifact fw:Model_AP_A_Design") == 2)
expect("the build task's evidence is typed with the general evidence class that the obligation names", re.search(r"fw:Ev_AP_A a backlog:TestEvidence, backlog:Evidence ;", t) is not None)
# 3 one kind still gives one model, and no obligation gives test evidence only
T1 = {"design": {"artifact": ART, "tool": "t", "method": "m", "model_kind": "Kind_ClassDiagram", "model_level": "Level_Design"}}
REG, run, sp, out = scenario(HDR2 % "" + STORY, T1)
rc, out = run("close", "1", sp); t = open(REG).read()
expect("a single model_kind still records one model", rc == 0 and t.count("a backlog:ModelArtifact ;") == 1)
expect("with no obligation the evidence is test evidence only", "fw:Ev_AP_A a backlog:TestEvidence ;" in t and "backlog:Evidence" not in t.split("fw:Ev_AP_A a backlog:TestEvidence")[-1].split(" ;")[0])
# 4 an unknown kind in the list is refused and nothing is written
TX = {"design": {"artifact": ART, "tool": "t", "method": "m", "model_kinds": ["Kind_ClassDiagram", "Kind_Nonsense"], "model_level": "Level_Design"}}
REG, run, sp, out = scenario(HDR2 % "" + STORY, TX); before = open(REG).read()
rc, out = run("close", "1", sp)
expect("an unknown kind in the list is refused and the register is unchanged", rc != 0 and "Kind_Nonsense" in out and open(REG).read() == before)
print("VERDICT: %s -- %d expectations %s" % ("PASS" if not bad else "FAIL", COUNT[0], "hold" if not bad else "(%d failed)" % len(bad))); sys.exit(1 if bad else 0)
