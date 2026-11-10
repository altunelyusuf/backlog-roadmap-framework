#!/usr/bin/env python3
"""backlog_adopting_register_probe v1.0.0 -- re-runnable proof that backlog_box_step generalizes to a register that is
NOT the framework's own (IPage handover box-tool-for-an-adopting-register, v1.1.0, C1-C8). Builds a throwaway package
whose register lives in its own namespace (prefix pcl:, <http://example.org/ipage-register#>) and own story-naming
convention, and drills the same ten acceptance criteria that backlog_box_step_probe and backlog_agent_monitor_probe
drill against the framework's own register, plus the cross-cutting ones specific to adopting:

  C1  graph-native reads survive a different Turtle serializer's layout (rdflib reserialization), not just the as-authored text
  C2  no subject or statement is ever written into the framework's own literal namespace -- only the adopting register's
  C3  a story found and referenced by its own identity (e.g. Story4_D1), never forced into ST_<prefix>_<key>
  C4  a planning event is found again at close by its LINK from the ceremony, not by scanning for whatever Plan_ records survive
  C5  a planned (Proposed) box opens in place the same way whatever order a graph serializer writes its properties in
  C6  every existing refusal (work before open, story not Proposed, no checkpoint, published statement edited, artifact
      older than the box) still fires, parity with the framework's own register
  C7  the validator is found via a declared BRSF_ROOT, not only when it happens to sit beside the tool
  C8  the agent monitor is called with full IRIs, and (now v1.4.0) understands them, not only bare local names

--deps: this probe and both tools it drills are declared, so the release gate's stamp only re-runs it when either changes."""
import glob, json, os, re, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = sorted(glob.glob(os.path.join(HERE, "backlog_box_step_v*.py")), key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", p)[0]])[-1]
MON = sorted(glob.glob(os.path.join(HERE, "backlog_agent_monitor_v*.py")), key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", p)[0]])[-1]

if sys.argv[1:] == ["--deps"]:
    print(TOOL); print(MON); print(os.path.abspath(__file__)); sys.exit(0)

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


def fixture(reserialize=False):
    work = tempfile.mkdtemp()
    pk = os.path.join(work, "pkg")
    os.makedirs(os.path.join(pk, "01-ontologies"))
    os.makedirs(os.path.join(pk, "03-tooling"))
    for f in (TOOL, MON):
        shutil.copy(f, os.path.join(pk, "03-tooling", os.path.basename(f)))
    reg = os.path.join(pk, "01-ontologies", "ipage_abox_v0_1_0.ttl")
    open(reg, "w").write(TTL)
    if reserialize:
        import rdflib as rl
        rl.Graph().parse(reg, format="turtle").serialize(destination=reg, format="turtle")
    # the committed ("published") tree must match the reserialized bytes, exactly as a real reserializing editor would commit
    # them -- reserializing AFTER commit would look, to the tool, like work that began outside the box (a different, real bug)
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


def close_spec(work, extra_findings=None):
    spec = {"stories": {"Story4_D1": {"artifact": "03-tooling/artifact.txt", "method": "m", "tool": "t", "harness": "h", "demo": "d", "result": "r"}},
            "run_result": "ok", "release_title": "rel", "findings": extra_findings or [], "observations": []}
    sp = os.path.join(work, "spec.json")
    json.dump(spec, open(sp, "w"))
    return sp


# ---------------------------------------------------------------- C1 / C2 ----
work, pk, reg = fixture()
rc, out = run(pk, reg, "open", "1", "t", "g", "Story4_D1", "--capacity", "3")
after = open(reg).read()
expect("C1/C2: open succeeds on a register in the adopting namespace (pcl:, not fw:) and no subject lands in the framework's own literal namespace",
       rc == 0 and "now InProgress" in out and "example.org/backlog-framework-register#" not in after and not re.search(r"(?<![A-Za-z0-9_])fw:", after))
time.sleep(1.1)
run(pk, reg, "act", "1", "Story4_D1", "worked")
art = os.path.join(pk, "03-tooling", "artifact.txt")
open(art, "w").write("evidence\n")
rc, out = run(pk, reg, "close", "1", close_spec(work))
final = open(reg).read()
expect("C1/C2: close succeeds; the story ends Done addressed as pcl:Story4_D1, still no fw: namespace anywhere",
       rc == 0 and "closed" in out and re.search(r"pcl:Story4_D1 a backlog:Story .*?backlog:hasState backlog:Done", final, re.S) is not None
       and "example.org/backlog-framework-register#" not in final and not re.search(r"(?<![A-Za-z0-9_])fw:", final))
shutil.rmtree(work, ignore_errors=True)

work, pk, reg = fixture(reserialize=True)
rc, out = run(pk, reg, "open", "1", "t", "g", "Story4_D1", "--capacity", "3")
expect("C1: the same open succeeds after the fixture is reserialised by rdflib first (survives a different Turtle writer's layout)", rc == 0 and "now InProgress" in out)
shutil.rmtree(work, ignore_errors=True)

# ---------------------------------------------------------------- C3 ----
work, pk, reg = fixture()
rc, out = run(pk, reg, "open", "1", "t", "g", "Story4_D1", "--capacity", "3")
after = open(reg).read()
expect("C3: open finds the story by its own name (Story4_D1), not forced into ST_<prefix>_<key>",
       rc == 0 and "pcl:Story4_D1 a backlog:Story" in after and "pcl:ST_D1_Story4_D1" not in after)
time.sleep(1.1)
run(pk, reg, "act", "1", "Story4_D1", "worked")
art = os.path.join(pk, "03-tooling", "artifact.txt")
open(art, "w").write("evidence\n")
rc, out = run(pk, reg, "close", "1", close_spec(work, [{"key": "F1", "root_cause": "rc", "remedy": "rm", "story": "Story4_D1"}]))
final = open(reg).read()
expect("C3: close resolves Story4_D1 throughout -- the finding, the closed review and the deployed release all point at the real subject",
       rc == 0 and "closed" in out
       and re.search(r"relatesToWorkItem pcl:Story4_D1", final) is not None
       and re.search(r"closesStory pcl:Story4_D1", final) is not None
       and re.search(r"deploysItem pcl:Story4_D1", final) is not None)
shutil.rmtree(work, ignore_errors=True)

# ---------------------------------------------------------------- C4 ----
work, pk, reg = fixture()
run(pk, reg, "open", "1", "t", "g", "Story4_D1", "--capacity", "3")
time.sleep(1.1)
run(pk, reg, "act", "1", "Story4_D1", "worked")
txt = open(reg).read()
m = re.search(r"pcl:Plan_D1_1_Story4_D1 a backlog:PlanningEvent[^\n]*\n(?:[^\n]*\n)*?[^\n]*\.\n", txt)
if m:
    open(reg, "w").write(txt[:m.start()] + txt[m.end():])
art = os.path.join(pk, "03-tooling", "artifact.txt")
open(art, "w").write("evidence\n")
rc, out = run(pk, reg, "close", "1", close_spec(work))
expect("C4: close is refused when a planning event linked from the ceremony was deleted outright, not silently read as an empty box",
       m is not None and rc != 0 and "gone" in out)
shutil.rmtree(work, ignore_errors=True)

# positive control for C4, reused below as the C6 clean-close control too
work, pk, reg = fixture()
run(pk, reg, "open", "1", "t", "g", "Story4_D1", "--capacity", "3")
time.sleep(1.1)
run(pk, reg, "act", "1", "Story4_D1", "worked")
art = os.path.join(pk, "03-tooling", "artifact.txt")
open(art, "w").write("evidence\n")
rc, out = run(pk, reg, "close", "1", close_spec(work))
expect("C4 positive control: the same box closes normally when nothing was deleted", rc == 0 and "closed" in out)
shutil.rmtree(work, ignore_errors=True)

# ---------------------------------------------------------------- C5 ----
PLANNED_TTL = TTL + """pcl:It_D1_1 a backlog:Iteration ; backlog:hasIdentifier "D1-BOX-1" ; backlog:hasTitle "planned" ; backlog:hasSprintGoal "g" ;
    backlog:hasState backlog:Proposed ; backlog:hasCapacity 3.0 ; backlog:belongsToLineage pcl:D1 .
pcl:PB_D1_1 a backlog:PlanBaseline ; backlog:baselineFor pcl:It_D1_1 ; backlog:isCurrentBaseline true ;
    backlog:hasBaselineStart "2026-01-01T00:00:00Z"^^xsd:dateTime ; backlog:hasBaselineEnd "2026-01-01T04:00:00Z"^^xsd:dateTime .
"""


def c5_pass(reserialize):
    work = tempfile.mkdtemp()
    pk = os.path.join(work, "pkg")
    os.makedirs(os.path.join(pk, "01-ontologies"))
    os.makedirs(os.path.join(pk, "03-tooling"))
    for f in (TOOL, MON):
        shutil.copy(f, os.path.join(pk, "03-tooling", os.path.basename(f)))
    reg = os.path.join(pk, "01-ontologies", "ipage_abox_v0_1_0.ttl")
    text = PLANNED_TTL.replace('pcl:Story4_D1 a backlog:Story ; backlog:hasIdentifier "4" ; backlog:hasState backlog:Proposed ; backlog:hasEffort 2.0 ;\n    backlog:belongsToLineage pcl:D1 ; backlog:producedByStage pcl:Out_B .',
                               'pcl:Story4_D1 a backlog:Story ; backlog:hasIdentifier "4" ; backlog:hasState backlog:Proposed ; backlog:hasEffort 2.0 ;\n    backlog:memberOfContainer pcl:It_D1_1 ; backlog:belongsToLineage pcl:D1 ; backlog:producedByStage pcl:Out_B .')
    open(reg, "w").write(text)
    if reserialize:
        import rdflib as rl
        rl.Graph().parse(reg, format="turtle").serialize(destination=reg, format="turtle")
    git(pk, "init", "-q")
    open(os.path.join(pk, "03-tooling", "other.py"), "w").write("x = 1\n")
    git(pk, "add", "-A")
    git(pk, "-c", "user.email=p@p", "-c", "user.name=p", "commit", "-qm", "p")
    git(pk, "update-ref", "refs/remotes/origin/main", "HEAD")
    rc, out = run(pk, reg, "open", "1", "t", "g", "Story4_D1", "--capacity", "3")
    final = open(reg).read()
    ok = (rc == 0 and "planned in advance" in out
          and final.count("pcl:It_D1_1 a backlog:Iteration") == 1
          and final.count("pcl:PB_D1_1 a backlog:PlanBaseline") == 1)
    shutil.rmtree(work, ignore_errors=True)
    return ok


expect("C5: a planned (Proposed) box opens in place as authored (one Iteration, base plan unchanged)", c5_pass(False))
expect("C5: the same holds after the fixture is reserialised by rdflib first (property order no longer assumed)", c5_pass(True))

# ---------------------------------------------------------------- C6 (refusal parity) ----
work, pk, reg = fixture()
open(os.path.join(pk, "03-tooling", "other.py"), "w").write("x = 2\n")
rc, out = run(pk, reg, "open", "1", "t", "g", "Story4_D1", "--capacity", "3")
expect("C6: open refused when a governed file already differs from the published tree", rc != 0 and "work began before the box was opened" in out)
shutil.rmtree(work, ignore_errors=True)

work, pk, reg = fixture()
rc, out = run(pk, reg, "open", "1", "t", "g", "Story5_D1", "--capacity", "3")
expect("C6: open refused for a story that is not Proposed", rc != 0 and "not Proposed" in out)
shutil.rmtree(work, ignore_errors=True)

work, pk, reg = fixture()
run(pk, reg, "open", "1", "t", "g", "Story4_D1", "--capacity", "3")
art = os.path.join(pk, "03-tooling", "artifact.txt")
open(art, "w").write("evidence\n")
rc, out = run(pk, reg, "close", "1", close_spec(work))
expect("C6: close refused when no checkpoint was recorded", rc != 0 and "composed in one pass" in out)
shutil.rmtree(work, ignore_errors=True)

work, pk, reg = fixture()
run(pk, reg, "open", "1", "t", "g", "Story4_D1", "--capacity", "3")
time.sleep(1.1)
run(pk, reg, "act", "1", "Story4_D1", "worked")
cur = open(reg).read()
open(reg, "w").write(cur.replace("backlog:hasEffort 2.0 ;", "backlog:hasEffort 9.0 ;", 1))
art = os.path.join(pk, "03-tooling", "artifact.txt")
open(art, "w").write("evidence\n")
rc, out = run(pk, reg, "close", "1", close_spec(work))
expect("C6: close refused when a published statement was edited in place", rc != 0 and "gone or changed" in out)
shutil.rmtree(work, ignore_errors=True)

work, pk, reg = fixture()
run(pk, reg, "open", "1", "t", "g", "Story4_D1", "--capacity", "3")
time.sleep(1.1)
run(pk, reg, "act", "1", "Story4_D1", "worked")
art = os.path.join(pk, "03-tooling", "artifact.txt")
open(art, "w").write("evidence\n")
os.utime(art, (1577836800, 1577836800))
rc, out = run(pk, reg, "close", "1", close_spec(work))
expect("C6: close refused for an artifact older than the box", rc != 0 and "older than the box" in out)
shutil.rmtree(work, ignore_errors=True)

# ---------------------------------------------------------------- C7 ----
work, pk, reg = fixture()
open(os.path.join(pk, "03-tooling", "other.py"), "w").write("x = 1\n")
frw = os.path.join(work, "framework")
os.makedirs(os.path.join(frw, "03-tooling"))
open(os.path.join(frw, "03-tooling", "backlog_validate_v1_0_0.py"), "w").write("import sys\nprint('VERDICT : CONFORMANT')\nsys.exit(0)\n")
env_before = os.environ.pop("BRSF_ROOT", None)
rc, out = run(pk, reg, "owes", "LS_InProgress")
expect("C7: with no validator beside the tool and no BRSF_ROOT, nothing is checked (unchanged default)", "NOT CHECKED" in out)
rc, out = run(pk, reg, "--brsf-root", frw, "owes", "LS_InProgress")
expect("C7: --brsf-root points the tool at a validator in a separately checked-out framework, so it IS checked this time", "NOT CHECKED" not in out and rc == 0)
if env_before is not None:
    os.environ["BRSF_ROOT"] = env_before
shutil.rmtree(work, ignore_errors=True)

# ---------------------------------------------------------------- C8 ----
work, pk, reg = fixture()
run(pk, reg, "open", "1", "t", "g", "Story4_D1", "--capacity", "3")
time.sleep(1.1)
run(pk, reg, "act", "1", "Story4_D1", "worked")
art = os.path.join(pk, "03-tooling", "artifact.txt")
open(art, "w").write("evidence\n")
rc, out = run(pk, reg, "close", "1", close_spec(work))
src = open(TOOL).read()
expect("C8: the box closes successfully with the full-IRI monitor call wired in, and cmd_close builds that call from full IRIs (reg.ns-qualified), not bare local names",
       rc == 0 and "closed" in out and '"<%s%s>" % (reg.ns, reg.L[3:])' in src and '"<%s%s>" % (reg.ns, x)' in src)
r = subprocess.run([sys.executable, MON, reg, "--lineage", "<http://example.org/ipage-register#D1>",
                    "--closing", "<http://example.org/ipage-register#Story4_D1>,pcl:T_D1_Story4_D1_Build"],
                    capture_output=True, text=True)
expect("C8: the agent monitor runs scoped to the adopting lineage when called with a full IRI, exactly as cmd_close calls it",
       r.returncode in (0, 1) and "lineage D1" in r.stdout)
shutil.rmtree(work, ignore_errors=True)

print("VERDICT: %s" % ("PASS -- %d expectations hold" % COUNT[0] if not bad else "FAIL -- " + "; ".join(bad)))
if bad:
    print(out[-800:])
sys.exit(1 if bad else 0)
