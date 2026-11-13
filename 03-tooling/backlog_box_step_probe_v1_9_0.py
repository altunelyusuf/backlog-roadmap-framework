#!/usr/bin/env python3
"""backlog_box_step_probe v1.9.0 (Lineage 29, package 14; 2SISA delivery handover, G233): a story opened with `KEY:design+build+verification` holds three tasks of those three types, each with its own readiness check, transitions and, at the close, its own evidence, and a task or a task's evidence that is missing is refused; a bare KEY still records the one build task; a refused step prints every violation it found, grouped by the check that raised it, not the first few, and puts the register back. v1.8.0 (IPage handover box-tool-for-an-adopting-register, C5): a planned box is opened in place whatever ORDER its own predicates
are written in, because a graph serializer is free to reorder them (it alphabetises them) and the tool must still open the box, not refuse it. v1.7.0
treated box 5's layout (hasCapacity before hasState, named "odd") as one the tool "cannot open in place" and refused; that was this exact reordering,
so v1.7.0's assertion is superseded here, not silently dropped: box 5 now opens correctly, and a genuinely unrecoverable layout (box 6, no hasCapacity
at all) takes over proving that a truly unreadable box is still refused rather than guessed at.
v1.7.0 (Lineage 29, box 41: a time-box planned in advance is opened in place, once, with its base plan kept, and only with member stories; a time-box already open is still refused) -- v1.6.0 -- the step tool accepts a box recorded in order and refuses each fault made by hand (Lineage 21, D3), and reads the obligations of a status from the register (Lineage 22, D3).

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
fw:KO a backlog:KickOff ; backlog:kicksOffLineage fw:L_AdaptiveProof .
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
expect("with no validator beside the tool, open says the register was not validated", "NOT CHECKED" in out)
expect("an open box holds no deployment unit yet (a unit may not carry unfinished work) and its plan names the one that will ship (Lineage 23)", "fw:Rel_AP_1 a backlog:DeploymentUnit" not in open(REG).read() and "plansDeploymentUnit fw:Rel_AP_1" in open(REG).read())
rc2, out2 = run(*OPEN)
expect("a box already opened is not opened again", rc2 != 0 and "already has records" in out2)
txt = open(REG).read()
expect("the story moved to InProgress with one state and one start", txt.count("backlog:hasState backlog:InProgress") >= 2 and "T_Start" in txt)
open(os.path.join(pk, ART), "w").write("evidence\n")
rc, out = run("close", "1", SP)
expect("close is refused when no checkpoint was recorded in the box", rc != 0 and "composed in one pass" in out)
rc, out = run("act", "1", "A", "kept by Ruling_Something and G162")
expect("an underscored identifier of any kind is refused too (Lineage 23, review)", run("act", "1", "A", "see DPlan_X_1")[0] != 0 and run("act", "1", "A", "see LS_InProgress")[0] != 0 and run("act", "1", "A", "see fw:Thing")[0] != 0)
expect("a note that names a modelled thing by identifier is refused (Lineage 23)", rc != 0 and "by identifier" in out)
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
# v1.1.0: a validator beside the tool (a stub that reports a planted violation, and a status that owes one)
open(os.path.join(pk, "03-tooling", "backlog_validate_v1_0_0.py"), "w").write("import sys\nt = open(sys.argv[1]).read()\nv = []\nif 'VIOLATE' in t: v.append('  [Violation] FocusV   it holds a planted violation')\nif 'hasLineageStatus backlog:LS_Achieved' in t: v.append('  [Violation] L_AdaptiveProof   claims achieved without a closure report')\nprint(chr(10).join(v)); print('VERDICT : ' + ('NON-CONFORMANT' if v else 'CONFORMANT')); sys.exit(1 if v else 0)\n")
rc, out = run("owes", "LS_Achieved")
expect("owes lists what a status would violate that the register does not violate now", rc == 0 and "claims achieved without a closure report" in out)
rc, out = run("owes", "LS_InProgress")
expect("owes names nothing for a status that adds no violation", rc == 0 and "owes nothing" in out)
before = open(REG).read()
bad_spec = json.loads(open(SP).read()); bad_spec["findings"] = [{"key": "F", "root_cause": "VIOLATE", "remedy": "rm"}]
json.dump(bad_spec, open(os.path.join(work, "spec_bad.json"), "w"))
rc, out = run("close", "1", os.path.join(work, "spec_bad.json"))
expect("close that would introduce a violation is refused, names it, and puts the register back as it was", rc != 0 and "FocusV" in out and open(REG).read() == before)
rc, out = run("close", "1", SP)
final = open(REG).read()
expect("the same box closes once the faults are removed", rc == 0 and "closed" in out)
expect("the story is Done with one state, the box Done, the deployment unit recorded",
       len(re.findall(r"fw:ST_AP_A a backlog:Story .*?backlog:hasState backlog:(\w+)", final, re.S)) == 1
       and re.search(r"fw:ST_AP_A a backlog:Story .*?backlog:hasState backlog:Done", final, re.S) is not None
       and re.search(r"fw:It_AP_1 a backlog:Iteration .*?backlog:hasState backlog:Done", final, re.S) is not None and "fw:Rel_AP_1 a backlog:DeploymentUnit" in final and final.count("fw:Rel_AP_1 a backlog:DeploymentUnit") == 1
       and re.search(r"fw:Rel_AP_1 a backlog:DeploymentUnit .*?backlog:hasState backlog:Done ; backlog:hasDeploymentDate .*?backlog:deploysItem fw:ST_AP_A", final, re.S) is not None and "plansDeploymentUnit fw:Rel_AP_1" in final)
import importlib.util
sp = importlib.util.spec_from_file_location("bs", os.path.join(HERE, TOOL)); bs = importlib.util.module_from_spec(sp); sp.loader.exec_module(bs)
expect("a violation naming lineages that differ only in a digit of their names is a different violation", bs.new_violations({("P", "L1: lineage (http://x#L_Lin4) has no goal")}, {("P", "L1: lineage (http://x#L_Lin3) has no goal")}) == [("P", "L1: lineage (http://x#L_Lin4) has no goal")])
expect("a violation whose message differs from before only in a number is not reported as new, and a different one is", bs.new_violations({("F", "C1: 6 items")}, {("F", "C1: 5 items")}) == [] and bs.new_violations({("F", "C1: 6 items"), ("F", "C2: other")}, {("F", "C1: 5 items")}) == [("F", "C2: other")])
a, b = bs.tick(), bs.tick()
expect("two records written back to back are at least one second apart", b > a)
a, b = "fw:L_Mine", "fw:L_Other"
KO = lambda lin: "fw:K a backlog:KickOff ; backlog:kicksOffLineage %s .\n" % lin
expect("a kick-off of another lineage does not count as the lineage's own (Lineage 25)", not bs.has_own_kickoff(KO(b), a))
expect("a kick-off of the lineage itself counts, in either spelling (Lineage 25)", bs.has_own_kickoff(KO(a), a) and bs.has_own_kickoff("fw:K a backlog:KickOff ; backlog:kicksOffLineage <http://example.org/backlog-framework-register#L_Mine> .\n", a))
expect("a lineage whose name is the start of another's is not mistaken for it (Lineage 25)", not bs.has_own_kickoff(KO("fw:L_MineToo"), a))

# v1.7.0: a time-box planned in advance (state Proposed, with its stories and its base plan) is opened in place
publish()   # box 1 is finished and published: the files it left are the baseline of box 2
_r = open(REG).read()
_r += """
fw:ST_AP_B a backlog:Story ; backlog:hasIdentifier "B" ; backlog:hasState backlog:Proposed ; backlog:hasEffort 2.0 ;
    backlog:memberOfContainer fw:Register ; backlog:belongsToLineage fw:L_AdaptiveProof ; backlog:producedByStage fw:Out_B .
fw:ST_AP_B backlog:memberOfContainer fw:It_AP_2 .
fw:ST_AP_C a backlog:Story ; backlog:hasIdentifier "C" ; backlog:hasState backlog:Proposed ; backlog:hasEffort 1.0 ;
    backlog:belongsToLineage fw:L_AdaptiveProof ; backlog:producedByStage fw:Out_B .
fw:AC_AP_B a backlog:AcceptanceCriterion ; backlog:hasGherkinText "Given a, When b, Then c." .
fw:It_AP_2 a backlog:Iteration ; backlog:hasIdentifier "AP-BOX-2" ; backlog:hasTitle "planned" ; backlog:hasSprintGoal "g" ; backlog:hasState backlog:Proposed ; backlog:hasCapacity 3.0 ; backlog:belongsToLineage fw:L_AdaptiveProof .
fw:PB_AP_2 a backlog:PlanBaseline ; backlog:baselineFor fw:It_AP_2 ; backlog:isCurrentBaseline true ; backlog:hasBaselineStart "2026-01-01T00:00:00Z"^^xsd:dateTime ; backlog:hasBaselineEnd "2026-01-01T04:00:00Z"^^xsd:dateTime .
"""
open(REG, "w").write(_r)
rc, out = run("open", "2", "t", "g", "C", "--capacity", "3")
expect("a planned box is not opened with a story that is not a member of it", rc != 0 and "not a member of the planned box" in out)
rc, out = run("open", "2", "t", "g", "B", "--capacity", "3")
expect("a planned box is opened when the membership of its story is a line appended after the story, as in the register", rc == 0)
fin2 = open(REG).read()
expect("a planned box is opened in place: it moves to In progress with its start", rc == 0 and "planned in advance" in out and re.search(r"fw:It_AP_2 a backlog:Iteration ;.*?backlog:hasState backlog:InProgress ; backlog:iterationStart \"", fin2, re.S) is not None)
expect("no second record of the planned box and no second base plan is written", fin2.count("fw:It_AP_2 a backlog:Iteration") == 1 and fin2.count("fw:PB_AP_2 a backlog:PlanBaseline") == 1 and "backlog:hasState backlog:Proposed ; backlog:hasCapacity 3.0 ; backlog:belongsToLineage fw:L_AdaptiveProof" not in fin2.split("fw:PB_AP_2")[0].split("fw:It_AP_2 a")[1].split("\n")[0])
expect("its story is planned into it and now InProgress", "backlog:plannedInto fw:It_AP_2" in fin2 and re.search(r"fw:ST_AP_B a backlog:Story .*?backlog:hasState backlog:InProgress", fin2, re.S) is not None)
rc, out = run("open", "2", "t", "g", "B", "--capacity", "3")
expect("a box already open is still refused after a planned one was opened", rc != 0 and "already has records" in out)
open(REG, "a").write("""
fw:It_AP_3 a backlog:Iteration ; backlog:hasIdentifier "AP-BOX-3" ; backlog:hasTitle "started" ; backlog:hasState backlog:Proposed ; backlog:iterationStart "2026-01-01T00:00:00Z"^^xsd:dateTime ; backlog:hasCapacity 3.0 ; backlog:belongsToLineage fw:L_AdaptiveProof .
fw:It_AP_4 a backlog:Iteration ; backlog:hasIdentifier "AP-BOX-4" ; backlog:hasTitle "other" ; backlog:hasState backlog:Proposed ; backlog:hasCapacity 3.0 ; backlog:belongsToLineage fw:L_Other .
fw:It_AP_5 a backlog:Iteration ; backlog:hasIdentifier "AP-BOX-5" ; backlog:hasTitle "odd" ; backlog:hasCapacity 3.0 ; backlog:hasState backlog:Proposed ; backlog:belongsToLineage fw:L_AdaptiveProof .
fw:ST_AP_D a backlog:Story ; backlog:hasIdentifier "D" ; backlog:hasState backlog:Proposed ; backlog:hasEffort 1.0 ;
    backlog:belongsToLineage fw:L_AdaptiveProof ; backlog:producedByStage fw:Out_B .
fw:ST_AP_D backlog:memberOfContainer fw:It_AP_5 .
fw:It_AP_6 a backlog:Iteration ; backlog:hasIdentifier "AP-BOX-6" ; backlog:hasTitle "unreadable" ; backlog:hasState backlog:Proposed ; backlog:belongsToLineage fw:L_AdaptiveProof .
""")
rc, out = run("open", "3", "t", "g", "C", "--capacity", "3")
expect("a planned box that already has a start is refused", rc != 0 and "already has records" in out)
rc, out = run("open", "4", "t", "g", "C", "--capacity", "3")
expect("a box planned in another lineage is refused", rc != 0 and "another lineage" in out)
rc, out = run("open", "5", "t", "g", "D", "--capacity", "3")
expect("a planned box opens in place however its own predicates are ordered -- capacity written before state, as a graph serializer would (C5) -- no longer refused as 'odd'", rc == 0 and "planned in advance" in out)
rc, out = run("open", "6", "t", "g", "C", "--capacity", "3")
expect("a planned box with no capacity recorded at all is still refused, not guessed at", rc != 0 and "cannot open in place" in out)

# v1.9.0: typed tasks and all violations
publish()
_r = open(REG).read() + """
fw:ST_AP_E a backlog:Story ; backlog:hasIdentifier "E" ; backlog:hasState backlog:Proposed ; backlog:hasEffort 2.0 ;
    backlog:memberOfContainer fw:Register ; backlog:belongsToLineage fw:L_AdaptiveProof ; backlog:producedByStage fw:Out_B .
fw:ST_AP_E backlog:memberOfContainer fw:It_AP_7 .
fw:AC_AP_E a backlog:AcceptanceCriterion ; backlog:hasGherkinText "Given a, When b, Then c." .
fw:It_AP_7 a backlog:Iteration ; backlog:hasIdentifier "AP-BOX-7" ; backlog:hasTitle "typed" ; backlog:hasSprintGoal "g" ; backlog:hasState backlog:Proposed ; backlog:hasCapacity 3.0 ; backlog:belongsToLineage fw:L_AdaptiveProof .
fw:PB_AP_7 a backlog:PlanBaseline ; backlog:baselineFor fw:It_AP_7 ; backlog:isCurrentBaseline true ; backlog:hasBaselineStart "2026-01-02T00:00:00Z"^^xsd:dateTime ; backlog:hasBaselineEnd "2026-01-02T04:00:00Z"^^xsd:dateTime .
"""
open(REG, "w").write(_r)
open(os.path.join(pk, "03-tooling", "backlog_validate_v1_0_0.py"), "w").write('import sys, os, tempfile\nHERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.join(HERE, "..")\nimport rdflib\nfrom rdflib import Graph\nB = rdflib.Namespace("http://example.org/backlog#"); SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")\nTBOX = (__import__("glob").glob(os.path.join(PKG, "01-ontologies", "backlog_tbox_v*.ttl")) or [os.path.join(PKG, "01-ontologies", "backlog_tbox_none.ttl")])[0]; SHAPES = (__import__("glob").glob(os.path.join(PKG, "02-shacl-safeguards", "backlog_shacl_v*.ttl")) or [os.path.join(PKG, "02-shacl-safeguards", "backlog_shacl_none.ttl")])[0]\ndef load(paths):\n    g = Graph()\n    for q in paths: g.parse(q, format="turtle")\n    return g\ndef reference_abox(files): return files[0]\ndef _latest_overlay():\n    g = Graph(); g.parse(SHAPES, format="turtle")\n    for n in ("GroomingToExecutionShape", "DesignTaskProducesShape", "UndeclaredContainerDependencyAdvisoryShape"):\n        g.set((B[n], SH.severity, SH.Violation))\n    fd, q = tempfile.mkstemp(suffix=".promoted.ttl"); os.close(fd); g.serialize(q, format="turtle"); return q\ndef lineage_rule_set_adopters(files):\n    g = load(files); return {x for x in g.subjects(B.adoptsRuleSet, B.RS_SeverityAudit_20260909) if (x, rdflib.RDF.type, B.Lineage) in g}\ndef promoted_overlay(files):\n    g = load(files)\n    for x in g.subjects(B.adoptsRuleSet, B.RS_SeverityAudit_20260909):\n        if (x, rdflib.RDF.type, B.Lineage) not in g: return _latest_overlay()\n    return None\ndef _lineage_scope(g, lins):\n    n = set(lins)\n    for l in lins: n.update(g.subjects(B.belongsToLineage, l))\n    return n\nif __name__ == "__main__":\n    t = open(sys.argv[1]).read()\n    v = []\n    if \'MANYV\' in t:\n        for i in range(7): v.append(\'  [Violation] F%d   C%d: planted violation %d\' % (i, i % 2, i))\n    if \'LONGV\' in t:\n        v.append(\'  [Violation] FocL   X9: \' + \'x\' * 150 + \' tail one\'); v.append(\'  [Violation] FocL   X9: \' + \'x\' * 150 + \' tail two\')\n    print(chr(10).join(v)); print(\'VERDICT : \' + (\'NON-CONFORMANT\' if v else \'CONFORMANT\')); sys.exit(1 if v else 0)\n')
publish()
rc, out = run("open", "7", "t", "g", "E:design+nonsense", "--capacity", "3")
import importlib.util as _iu
_tsp = _iu.spec_from_file_location("tool_mod0", os.path.join(HERE, TOOL)); _tm = _iu.module_from_spec(_tsp); _tsp.loader.exec_module(_tm)
expect("an effort written as a typed number is read, a bare decimal too, and anything else is refused with a message", _tm.num_of('"5"^^xsd:decimal', "x") == 5.0 and _tm.num_of("5.0", "x") == 5.0 and _tm.num_of('"2.5"^^xsd:float', "x") == 2.5)
try:
    _tm.num_of("five", "hasEffort of story X"); _nr = False
except SystemExit as _e:
    _nr = "REFUSED" in str(_e)
expect("an effort that is no number is refused with a message, not a traceback", _nr)
expect("a task kind that is not one of design, build, verification is refused", rc != 0 and "not a task kind" in out)
os.makedirs(os.path.join(pk, "02-shacl-safeguards"), exist_ok=True)
import glob as _g
def _newest(folder, stem):
    return sorted(_g.glob(os.path.join(HERE, "..", folder, stem + "_v*.ttl")), key=lambda f: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", f)[0]])[-1]
for _f, _st in (("02-shacl-safeguards", "backlog_shacl"), ("01-ontologies", "backlog_tbox")):
    shutil.copy(_newest(_f, _st), os.path.join(pk, _f, os.path.basename(_newest(_f, _st))))
publish()
open(REG, "a").write("\n" + "".join("backlog:%s a owl:NamedIndividual , backlog:ModelKind .\n" % k for k in ("Kind_ClassDiagram", "Kind_ComponentDiagram", "Kind_SequenceDiagram", "Kind_UseCaseDiagram")) + "".join("backlog:%s a owl:NamedIndividual , backlog:ModelLevel .\n" % k for k in ("Level_Design", "Level_Analysis")) + "backlog:Concern_Architecture a owl:NamedIndividual ; backlog:coversTaskType backlog:Task_ArchitectureDefinition .\n")   # the controlled individuals the framework's own A-box declares, which the shapes' class checks read
_pre7 = open(REG).read()
_CO = "\nfw:L_AdaptiveProof backlog:adoptsObligationSet fw:OS_T .\nfw:ObK a backlog:StageObligation ; backlog:obligationOfConcern backlog:Concern_Architecture ; backlog:owesClass backlog:ModelArtifact ; backlog:owesKind backlog:Kind_ComponentDiagram ; backlog:owesLevel backlog:Level_Design ;%s backlog:obligationSeverity backlog:Oblig_Required ; backlog:inObligationSet fw:OS_T .\n"
open(REG, "w").write(_pre7 + _CO % "")
rc, out = run("open", "7", "t", "g", "E:architecture+build", "--capacity", "3")
expect("a story with an architecture task is not opened where a Required architecture-concern obligation owes a model the lineage lacks, and the reason is named", rc != 0 and "ConcernObligationShape" in out)
open(REG, "w").write(_pre7 + _CO % " backlog:owesDepth backlog:Depth_Brief ;" + "fw:MA_C a backlog:ModelArtifact ; backlog:hasModelKind backlog:Kind_ComponentDiagram ; backlog:hasModelLevel backlog:Level_Design ; backlog:belongsToLineage fw:L_AdaptiveProof .\n")
rc, out = run("open", "7", "t", "g", "E:architecture+build", "--capacity", "3")
expect("the concern obligation is met by the lineage's own model of its kind and level whatever its depth", rc == 0 and "now InProgress" in out)
open(REG, "w").write(_pre7)
rc, out = run("open", "7", "t", "g", "E:architecture+design+build+verification", "--capacity", "3")
t7 = open(REG).read()
expect("a story opened with three task kinds is opened", rc == 0 and "now InProgress" in out)
expect("the story holds a design, a build and a verification task of the three types", all(re.search(r"fw:T_AP_E_%s a backlog:ExecutionTask .*?backlog:hasTaskType backlog:%s " % (n, ty), t7, re.S) for n, ty in (("Architecture", "Task_ArchitectureDefinition"), ("Design", "Task_DesignDefinition"), ("Build", "Task_Implementation"), ("Verification", "Task_Verification"))))
open(REG, "w").write(_pre7)
rc, out = run("open", "7", "t", "g", "E:analysis+requirements+architecture+design+build+integration+verification+validation+correction", "--capacity", "3")
_t9 = open(REG).read()
expect("a story opened with all nine task kinds holds a task of each type, as the rulings let one story carry every kind of its work", rc == 0 and all(re.search(r"fw:T_AP_E_%s a backlog:ExecutionTask .*?backlog:hasTaskType backlog:%s " % (n, ty), _t9, re.S) for n, ty in (("Analysis", "Task_SystemAnalysis"), ("Requirements", "Task_RequirementsDefinition"), ("Architecture", "Task_ArchitectureDefinition"), ("Design", "Task_DesignDefinition"), ("Build", "Task_Implementation"), ("Integration", "Task_Integration"), ("Verification", "Task_Verification"), ("Validation", "Task_Validation"), ("Correction", "Task_MaintenanceTask"))))
open(REG, "w").write(_pre7)
rc, out = run("open", "7", "t", "g", "E:architecture+design+build+verification", "--capacity", "3")
t7 = open(REG).read()
_sa = re.search(r"fw:ST_AP_E backlog:decomposesInto [^\n]*backlog:startedAt (\"[^\"]+\"\^\^xsd:dateTime)", t7); _ev = re.search(r"fw:Ev7_ST_AP_E_T_Start a [^\n]*backlog:transitionedAt (\"[^\"]+\"\^\^xsd:dateTime)", t7)
expect("the story's start and its first move into In progress are the same instant, as the validator's rule G113 requires", _sa is not None and _ev is not None and _sa.group(1) == _ev.group(1))
expect("each task has its own readiness check, its own transitions and the story decomposes into all three", all(("fw:Chk_AP_7_T_E%s a backlog:ReadinessCheck" % sfx) in t7 for sfx in ("_Architecture", "_Design", "", "_Verification")) and all(("fw:Ev7_T_AP_E_%s_T_Start a" % n) in t7 for n in ("Architecture", "Design", "Build", "Verification")) and "backlog:decomposesInto fw:T_AP_E_Architecture , fw:T_AP_E_Design , fw:T_AP_E_Build , fw:T_AP_E_Verification" in t7 and "backlog:producesTask fw:T_AP_E_Architecture , fw:T_AP_E_Design , fw:T_AP_E_Build , fw:T_AP_E_Verification" in t7)
open(os.path.join(pk, "03-tooling", "typed_build.txt"), "w").write("b\n")
open(os.path.join(pk, "03-tooling", "typed_design.txt"), "w").write("d\n")
open(os.path.join(pk, "03-tooling", "typed_arch.txt"), "w").write("a\n")
open(os.path.join(pk, "03-tooling", "typed_verify.txt"), "w").write("v\n")
time.sleep(1.1)
rc, out = run("act", "7", "E", "worked")
spec7 = {"stories": {"E": {"artifact": "03-tooling/typed_build.txt", "method": "m", "tool": "t", "harness": "h", "demo": "d", "result": "r",
                          "tasks": {"architecture": {"artifact": "03-tooling/typed_arch.txt", "tool": "t", "method": "m", "model_kind": "Kind_ClassDiagram", "model_level": "Level_Design"}, "design": {"artifact": "03-tooling/typed_design.txt", "tool": "t", "method": "m"}}}}, "run_result": "ok", "release_title": "rel7", "findings": [], "observations": []}
json.dump(spec7, open(os.path.join(work, "spec7.json"), "w"))
_cur9 = open(REG).read()
open(REG, "w").write(_t9)
rc, out = run("close", "7", os.path.join(work, "spec7.json"))
expect("a story opened with nine task kinds is not refused at its close as a plan changed by hand, and the close does not stop in a traceback (box 45 found the tool knew four kinds there)", "taken out of the plan" not in out and "Traceback" not in out and rc != 0)
open(REG, "w").write(_cur9)
rc, out = run("close", "7", os.path.join(work, "spec7.json"))
expect("close is refused when a task of the story has no evidence given", rc != 0 and "verification task of story E" in out)
spec7["stories"]["E"]["tasks"]["verification"] = {"artifact": "03-tooling/typed_verify.txt", "tool": "t", "method": "m"}
json.dump(spec7, open(os.path.join(work, "spec7.json"), "w"))
cur7 = open(REG).read()
open(REG, "w").write(cur7.replace("fw:T_AP_E_Verification a backlog:ExecutionTask", "fw:T_AP_E_Gone a backlog:ExecutionTask", 1))
rc, out = run("close", "7", os.path.join(work, "spec7.json"))
expect("close is refused when a task written at the opening was renamed by hand", rc != 0 and "changed by hand" in out)
open(REG, "w").write(cur7)
cur7a = open(REG).read()
spec7n = json.loads(json.dumps(spec7)); spec7n["stories"]["E"]["tasks"]["architecture"].pop("model_kind"); spec7n["stories"]["E"]["tasks"]["architecture"].pop("model_level"); json.dump(spec7n, open(os.path.join(work, "spec7n.json"), "w"))
open(REG, "w").write(cur7a + "\nfw:L_AdaptiveProof backlog:adoptsRuleSet backlog:RS_SeverityAudit_20260909 .\n")
rc, out = run("close", "7", os.path.join(work, "spec7n.json"))
expect("a lineage that adopted the severity audit has a close refused when a design or architecture task gives no model, the promoted shape named", rc != 0 and "DesignTaskProducesShape" in out)
def OB(i, subj, cls, kind=None, level=None, depth=None, sev="Required", st="OS_T"):
    return "fw:%s a backlog:StageObligation ; %s ; backlog:owesClass backlog:%s ;%s%s%s backlog:obligationSeverity backlog:Oblig_%s ; backlog:inObligationSet fw:%s .\n" % (i, subj, cls, " backlog:owesKind backlog:%s ;" % kind if kind else "", " backlog:owesLevel backlog:%s ;" % level if level else "", " backlog:owesDepth backlog:%s ;" % depth if depth else "", sev, st)
ADOPT = "\nfw:L_AdaptiveProof backlog:adoptsObligationSet fw:OS_T .\n"
DES, ARC, VER, BLD = "backlog:obligationOfTaskType backlog:Task_DesignDefinition", "backlog:obligationOfTaskType backlog:Task_ArchitectureDefinition", "backlog:obligationOfTaskType backlog:Task_Verification", "backlog:obligationOfTaskType backlog:Task_Implementation"
def closes(extra, sf="spec7.json"):
    open(REG, "w").write(cur7a + extra)
    rc_, out_ = run("close", "7", os.path.join(work, sf))
    open(REG, "w").write(cur7a)
    return rc_, out_
SHAPEMSG = "the shapes that read what this step writes find"
spec7d = json.loads(json.dumps(spec7)); spec7d["stories"]["E"]["tasks"]["architecture"].pop("model_kind"); spec7d["stories"]["E"]["tasks"]["architecture"].pop("model_level"); spec7d["stories"]["E"]["tasks"]["design"]["model_kind"] = "Kind_ClassDiagram"; spec7d["stories"]["E"]["tasks"]["design"]["model_level"] = "Level_Design"; json.dump(spec7d, open(os.path.join(work, "spec7d.json"), "w"))
spec7d = json.loads(json.dumps(spec7)); spec7d["stories"]["E"]["tasks"]["architecture"].pop("model_kind"); spec7d["stories"]["E"]["tasks"]["architecture"].pop("model_level"); spec7d["stories"]["E"]["tasks"]["design"]["model_kind"] = "Kind_ClassDiagram"; spec7d["stories"]["E"]["tasks"]["design"]["model_level"] = "Level_Design"; json.dump(spec7d, open(os.path.join(work, "spec7d.json"), "w"))
rc, out = closes(ADOPT + OB("Ob1", ARC, "ModelArtifact", "Kind_UseCaseDiagram", "Level_Analysis"))
expect("an adopted obligation of kind and level that the close does not give is refused by the obligation shapes themselves", rc != 0 and SHAPEMSG in out and "TaskTypeObligationLevelShape" in out)
rc, out = closes(ADOPT + OB("Ob1", DES, "ModelArtifact", "Kind_ClassDiagram", "Level_Design") + OB("Ob2", DES, "ModelArtifact", "Kind_SequenceDiagram", "Level_Design"), "spec7d.json")
expect("two Required obligations of one task type: giving one kind leaves the design task refused", rc != 0 and "TaskTypeObligationShape" in out)
rc, out = closes(ADOPT + OB("Ob1", DES, "ModelArtifact", "Kind_ClassDiagram", "Level_Design") + OB("Ob2", DES, "ModelArtifact", "Kind_SequenceDiagram", "Level_Design") + "fw:MA_Prior a backlog:ModelArtifact ; backlog:hasModelKind backlog:Kind_SequenceDiagram ; backlog:hasModelLevel backlog:Level_Design ; backlog:belongsToLineage fw:L_AdaptiveProof .\n", "spec7d.json")
expect("the lineage's own earlier model covers the other obligation, so the close is not refused by the obligation shapes", SHAPEMSG not in out)
rc, out = closes(ADOPT + OB("Ob1", DES, "ModelArtifact", "Kind_ClassDiagram", "Level_Design") + OB("Ob2", DES, "ModelArtifact", "Kind_SequenceDiagram", "Level_Design") + "fw:MA_Prior a backlog:ModelArtifact ; backlog:hasModelKind backlog:Kind_SequenceDiagram ; backlog:hasModelLevel backlog:Level_Design ; backlog:belongsToLineage fw:L_Other .\n", "spec7d.json")
expect("an earlier model of ANOTHER lineage does not cover the obligation", rc != 0 and "TaskTypeObligationShape" in out)
rc, out = closes(ADOPT + OB("Ob1", DES, "ModelArtifact", "Kind_ClassDiagram", "Level_Design", sev="Advisory"), "spec7.json")
expect("an Advisory obligation is not demanded", SHAPEMSG not in out)
rc, out = closes(ADOPT + "fw:L_AdaptiveProof backlog:adoptsObligationSet fw:OS_U .\n" + OB("Ob1", DES, "ModelArtifact", "Kind_ClassDiagram", "Level_Design", st="OS_U") + OB("Ob2", DES, "ModelArtifact", "Kind_SequenceDiagram", "Level_Design", st="OS_U"), "spec7d.json")
expect("every adopted set is read, not the first", rc != 0 and "TaskTypeObligationShape" in out)
rc, out = closes(ADOPT + OB("Ob1", BLD, "Evidence"))
expect("an owed Evidence is not covered by the TestEvidence the tool writes (the shapes match the class exactly)", rc != 0 and "TaskTypeObligationShape" in out)
rc, out = closes(ADOPT + OB("Ob1", DES, "ModelArtifact", "Kind_ClassDiagram", "Level_Design", "Depth_Brief"), "spec7d.json")
expect("an owed depth on a model the tool writes without one is refused", rc != 0 and "TaskTypeObligationLevelShape" in out)
rc, out = closes(ADOPT + OB("Ob1", VER, "TestEvidence", level="Level_Design"))
expect("an owed level on the TestEvidence the tool writes without one is refused", rc != 0 and "TaskTypeObligationLevelShape" in out)
spec7m = json.loads(json.dumps(spec7)); spec7m["stories"]["E"]["tasks"]["architecture"].pop("model_level"); json.dump(spec7m, open(os.path.join(work, "spec7m.json"), "w"))
rc, out = closes(ADOPT + OB("Ob1", ARC, "ModelArtifact", "Kind_ClassDiagram", "Level_Design"), "spec7m.json")
expect("a model written without its level where the adopted set names levels is refused as ModelLevelStatedShape reads it", rc != 0 and "ModelLevelStatedShape" in out)
rc, out = closes(ADOPT + OB("Ob1", ARC, "ModelArtifact", "Kind_ClassDiagram", "Level_Design") + OB("Ob2", ARC, "ModelArtifact", "Kind_ComponentDiagram", "Level_Design", sev="Advisory"))
expect("the architecture model the close gives meets the obligation of the architecture task type", SHAPEMSG not in out)

import importlib.util
_sp = importlib.util.spec_from_file_location("tool_mod", os.path.join(pk, "03-tooling", TOOL)); tool = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(tool)
def fv(txt): return {(f, m.split(":")[0]) for f, m in (tool.shape_violations(txt) or set())}
_t8 = t7.replace("backlog:hasTaskType backlog:Task_ArchitectureDefinition", "backlog:hasTaskType backlog:Task_Implementation")
_AUD = "\nfw:L_AdaptiveProof backlog:adoptsRuleSet backlog:RS_SeverityAudit_20260909 .\n"
expect("the guard's shape run finds a task without a type (TaskTypeShape)", any(x[1] == "TaskTypeShape" for x in fv(re.sub(r"backlog:hasTaskType backlog:Task_Implementation ;?", "", t7, count=1))))
expect("the guard's shape run finds a story that left Proposed with no concern claim (GroomingShape)", ("ST_AP_E", "GroomingShape") in fv(t7.replace("backlog:hasApplicableConcern backlog:Concern_Architecture", "backlog:foo backlog:bar")) and ("ST_AP_E", "GroomingShape") not in fv(t7))
expect("the guard's shape run finds a model with no kind (ModelArtifactShape)", ("ST_AP_E", "GroomingShape") in fv(t7.replace("backlog:hasApplicableConcern backlog:Concern_Architecture", "backlog:foo backlog:bar")))
expect("the guard's shape run finds an obligation bound to nothing (StageObligationShape)", any(x[1] == "StageObligationShape" for x in fv(t7 + "\nfw:ObX a backlog:StageObligation .\n")))
expect("a shape the severity audit promotes is a Violation only for a lineage that adopted it (GroomingToExecutionShape: a concern with no task it covers)", not any(x[1] == "GroomingToExecutionShape" for x in fv(_t8)) and ("ST_AP_E", "GroomingToExecutionShape") in fv(_t8 + _AUD))
_REGAUD = "\nfw:Reg backlog:adoptsRuleSet backlog:RS_SeverityAudit_20260909 .\n"
expect("a register-level adoption of the severity audit grades the promoted shapes for every record, not only an adopting lineage's", ("ST_AP_E", "GroomingToExecutionShape") in fv(_t8 + _REGAUD) and ("ST_AP_E", "GroomingToExecutionShape") not in fv(_t8))
_DEP = "\nfw:It_AP_9 a backlog:Iteration .\nfw:ST_AP_D a backlog:Story ; backlog:hasState backlog:Proposed ; backlog:memberOfContainer fw:It_AP_9 .\nfw:ST_AP_E backlog:dependsOn fw:ST_AP_D .\n"
expect("a promoted shape that reads what a rule derives fires: a member depending on unfinished work in another container with no container dependency declared", ("It_AP_7", "UndeclaredContainerDependencyAdvisoryShape") in fv(t7 + _DEP + _AUD) and not any(x[1] == "UndeclaredContainerDependencyAdvisoryShape" for x in fv(t7 + _DEP)))
_vsave = tool.validator
tool.validator = lambda: None
expect("with no validator the shape check still runs from the shapes and T-box beside the tool", any(x[1] == "ModelArtifactShape" for x in fv(t7 + "\nfw:MA_X a backlog:ModelArtifact .\n")))
tool.validator = _vsave
spec7l = json.loads(json.dumps(spec7d)); spec7l["stories"]["E"]["tasks"]["design"]["model_level"] = "Level_Foo"; json.dump(spec7l, open(os.path.join(work, "spec7l.json"), "w"))
open(REG, "w").write(cur7a)
rc, out = run("close", "7", os.path.join(work, "spec7l.json"))
expect("a model level the framework does not declare is refused", rc != 0 and "Level_Foo is not a model level the framework declares" in out)
open(REG, "w").write(cur7a)
open(os.path.join(pk, "03-tooling", "typed_build.txt"), "w").write("")
rc, out = run("close", "7", os.path.join(work, "spec7.json"))
expect("close is refused for a story whose own evidence artifact is empty", rc != 0 and "does not exist or is empty" in out)
open(os.path.join(pk, "03-tooling", "typed_build.txt"), "w").write("b\n")
spec7["stories"]["E"]["tasks"]["architecture"]["model_kind"] = "Kind_Nonsense"
json.dump(spec7, open(os.path.join(work, "spec7x.json"), "w"))
rc, out = run("close", "7", os.path.join(work, "spec7x.json"))
expect("a model kind the framework does not declare is refused", rc != 0 and "not a model kind" in out)
open(os.path.join(pk, "03-tooling", "typed_design.txt"), "w").write("")
rc, out = run("close", "7", os.path.join(work, "spec7.json"))
expect("close is refused for a typed task whose evidence artifact is empty", rc != 0 and "does not exist or is empty" in out)
open(os.path.join(pk, "03-tooling", "typed_design.txt"), "w").write("d\n")
cur7b = open(REG).read()
open(REG, "w").write(cur7b.replace("backlog:producesTask fw:T_AP_E_Architecture , fw:T_AP_E_Design , fw:T_AP_E_Build , fw:T_AP_E_Verification", "backlog:producesTask fw:T_AP_E_Architecture , fw:T_AP_E_Design , fw:T_AP_E_Build", 1))
rc, out = run("close", "7", os.path.join(work, "spec7.json"))
expect("close is refused when a task was taken out of the planning event by hand while its own record stays", rc != 0 and "taken out of the plan by hand" in out)
open(REG, "w").write(cur7b)
rc, out = run("close", "7", os.path.join(work, "spec7.json"))
c7 = open(REG).read()
expect("the box closes with the evidence of every task given", rc == 0 and "closed" in out)
expect("all three tasks are Done, each with its own evidence, and the story is Done", all(re.search(r"fw:T_AP_E_%s a backlog:ExecutionTask .*?backlog:hasState backlog:Done .*?backlog:hasEvidence fw:%s " % (n, ev), c7, re.S) for n, ev in (("Design", "Ev_AP_E_Design"), ("Build", "Ev_AP_E"), ("Verification", "Ev_AP_E_Verification"))) and re.search(r"fw:ST_AP_E a backlog:Story .*?backlog:hasState backlog:Done", c7, re.S) is not None and "fw:Ev7_T_AP_E_Design_T_Complete a" in c7 and "fw:Ev7_T_AP_E_Verification_T_Complete a" in c7)
expect("the architecture task that produced a model records it, its kind, its level and what it describes, and the task names it; a design task that gave no kind records no model", "fw:Model_AP_E_Architecture a backlog:ModelArtifact ; backlog:hasModelKind backlog:Kind_ClassDiagram ; backlog:hasModelLevel backlog:Level_Design ; backlog:describesItem fw:ST_AP_E" in c7 and "fw:T_AP_E_Architecture backlog:producesModelArtifact fw:Model_AP_E_Architecture" in c7 and "Model_AP_E_Design" not in c7)
expect("a story carries the architecture concern only when it plans an architecture task", "fw:ST_AP_E backlog:decomposesInto" in c7 and re.search(r"fw:ST_AP_E backlog:decomposesInto [^\n]*hasApplicableConcern backlog:Concern_Architecture", c7) is not None and re.search(r"fw:ST_AP_B backlog:decomposesInto [^\n]*hasApplicableConcern", c7) is None)
expect("the build task's readiness check keeps the label every earlier box wrote", 'rdfs:label "Readiness of the task of story B"@en' in c7)
expect("a bare KEY still records the one build task with the names every earlier box wrote", "fw:T_AP_B_Build a backlog:ExecutionTask" in c7 and "fw:T_AP_B_Design" not in c7 and "fw:Chk_AP_2_T_B a backlog:ReadinessCheck" in c7)
publish()
_r = open(REG).read() + """
fw:ST_AP_F a backlog:Story ; backlog:hasIdentifier "F" ; backlog:hasState backlog:Proposed ; backlog:hasEffort 2.0 ;
    backlog:memberOfContainer fw:Register ; backlog:belongsToLineage fw:L_AdaptiveProof ; backlog:producedByStage fw:Out_B .
fw:ST_AP_F backlog:memberOfContainer fw:It_AP_8 .
fw:AC_AP_F a backlog:AcceptanceCriterion ; backlog:hasGherkinText "Given a, When b, Then c." .
fw:It_AP_8 a backlog:Iteration ; backlog:hasIdentifier "AP-BOX-8" ; backlog:hasTitle "many" ; backlog:hasSprintGoal "g" ; backlog:hasState backlog:Proposed ; backlog:hasCapacity 3.0 ; backlog:belongsToLineage fw:L_AdaptiveProof .
fw:PB_AP_8 a backlog:PlanBaseline ; backlog:baselineFor fw:It_AP_8 ; backlog:isCurrentBaseline true ; backlog:hasBaselineStart "2026-01-03T00:00:00Z"^^xsd:dateTime ; backlog:hasBaselineEnd "2026-01-03T04:00:00Z"^^xsd:dateTime .
"""
open(REG, "w").write(_r)
rc, out = run("open", "8", "t", "g", "F", "--capacity", "3")
open(os.path.join(pk, "03-tooling", "many.txt"), "w").write("m\n")
time.sleep(1.1)
run("act", "8", "F", "worked")
many = {"stories": {"F": {"artifact": "03-tooling/many.txt", "method": "m", "tool": "t", "harness": "h", "demo": "d", "result": "r"}}, "run_result": "ok", "release_title": "rel8", "findings": [{"key": "G", "root_cause": "MANYV", "remedy": "rm"}], "observations": []}
json.dump(many, open(os.path.join(work, "many.json"), "w"))
before8 = open(REG).read()
rc, out = run("close", "8", os.path.join(work, "many.json"))
expect("a refused step names every one of the 7 violations it found, not the first few", rc != 0 and all(("F%d:" % i) in out for i in range(7)) and "7 violation(s)" in out)
expect("the violations are grouped by the check that raised them", "C0  (4)" in out and "C1  (3)" in out)
many["findings"] = [{"key": "G", "root_cause": "LONGV", "remedy": "rm"}]
json.dump(many, open(os.path.join(work, "many2.json"), "w"))
rc, out = run("close", "8", os.path.join(work, "many2.json"))
expect("two violations on one focus that differ only after 110 characters are both kept, in full", rc != 0 and "tail one" in out and "tail two" in out and "2 violation(s)" in out)
expect("a refused step puts the register back as it was", open(REG).read() == before8)
shutil.rmtree(work, ignore_errors=True)
print("VERDICT: %s" % ("PASS -- %d expectations hold" % COUNT[0] if not bad else "FAIL -- " + "; ".join(bad)))
sys.exit(1 if bad else 0)
