#!/usr/bin/env python3
"""backlog_next_act_probe v1.2.0 (box 61, G247): the next-act check lists a rule's refusals with the rule's repair before the step, the armed check refuses an unarmed clone, and repair rounds are appended and iterated until satisfied. `--tool PATH` runs another copy (the mutation check); `--deps` lists the inputs.
Cases: an Owner ruling with no date is refused with its repair (condition, method, who decides, when to ask the Owner); a conforming register passes; an advisory alone does not refuse; a refusal with no repair record says so (--all); a Done box with an unsatisfied last round is refused and passes once a satisfied round is appended (the loop); a round after a satisfied round is refused and an earlier round is never edited; the armed check refuses a clone with nothing, names each thing missing, accepts a clone with all three layers and the framework's own clone."""
import os, re, sys, glob, subprocess, tempfile, json
os.environ["BACKLOG_ARMED_STRICT"] = "1"   # the cases below plant clones in the temporary directory and must be judged
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.join(HERE, "..")
def newest(folder, stem, ext="py"):
    fs = glob.glob(os.path.join(PKG, folder, stem + "_v*." + ext))
    return sorted(fs, key=lambda f: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", f)[0]])[-1]
TOOL = newest("03-tooling", "backlog_next_act")
if sys.argv[1:2] == ["--deps"]:
    print(os.path.abspath(__file__)); print(TOOL); print(newest("01-ontologies", "backlog_tbox", "ttl")); print(newest("02-shacl-safeguards", "backlog_shacl", "ttl")); sys.exit(0)
if sys.argv[1:2] == ["--tool"]: TOOL = sys.argv[2]
PRE = "@prefix backlog: <http://example.org/backlog#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix fw: <http://example.org/probe#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
REPAIRS = PRE + '''fw:Rp1 a backlog:RuleRepair ; backlog:repairsShape backlog:OwnerRulingDatedShape ; backlog:repairDecidedBy backlog:Builder ; backlog:hasRepairCondition "COND-OWNER" ; backlog:hasRepairMethod "METHOD-OWNER" ; backlog:repairAsksOwnerWhen "ASK-OWNER" .
fw:Rp2 a backlog:RuleRepair ; backlog:repairsShape backlog:RepairRoundsEndShape ; backlog:repairDecidedBy backlog:Builder ; backlog:hasRepairCondition "COND-ROUNDS" ; backlog:hasRepairMethod "METHOD-ROUNDS" ; backlog:repairAsksOwnerWhen "ASK-ROUNDS" .
fw:Rp3 a backlog:RuleRepair ; backlog:repairsShape backlog:MissionClauseCitationShape ; backlog:repairDecidedBy backlog:Builder ; backlog:hasRepairCondition "COND-CITE" ; backlog:hasRepairMethod "METHOD-CITE" ; backlog:repairAsksOwnerWhen "ASK-CITE" .
'''
UNDATED = PRE + 'fw:G9999 a backlog:GovernanceRuling ; backlog:hasRulingIdentifier "G9999" ; backlog:rulingSource "Owner instruction with no date" .\n'
DATED = PRE + 'fw:G9999 a backlog:GovernanceRuling ; backlog:hasRulingIdentifier "G9999" ; backlog:rulingSource "Owner instruction of 2026-11-19 at 12:13" .\n'
BOX = PRE + 'fw:Box a backlog:Iteration ; backlog:hasState backlog:Done .\n'
def run(args, files):
    with tempfile.TemporaryDirectory() as d:
        fs = []
        for name, text in files.items():
            f = os.path.join(d, name); open(f, "w").write(text); fs.append(f)
        a = [sys.executable, TOOL] + [x.replace("{d}", d) for x in args] + fs
        r = subprocess.run(a, capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr
def runcheck(reg_text, extra=()):
    with tempfile.TemporaryDirectory() as d:
        rf, pf = os.path.join(d, "reg.ttl"), os.path.join(d, "rep.ttl"); open(rf, "w").write(reg_text); open(pf, "w").write(REPAIRS)
        r = subprocess.run([sys.executable, TOOL, "check", rf, "--repairs", pf] + list(extra), capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr
FAILS = []; N = [0]
def expect(what, ok):
    N[0] += 1
    if not ok: FAILS.append(what)
    print(("ok   " if ok else "FAIL ") + what)
c, o = runcheck(UNDATED)
expect("1 an undated Owner ruling is refused before the step (exit 2) and the rule is named", c == 2 and "OwnerRulingDatedShape" in o)
expect("2 the refusal prints the repair of its rule (condition, method, who decides, when to ask the Owner)", all(x in o for x in ("COND-OWNER", "METHOD-OWNER", "Builder", "ASK-OWNER")))
c, o = runcheck(DATED)
expect("3 a conforming register passes (exit 0)", c == 0 and "nothing refuses" in o)
c, o = runcheck(DATED + 'fw:D a backlog:ScopeDeliverable ; backlog:derivesFromMissionClause "a quote that is nowhere" .\n')
expect("4 an advisory alone does not refuse (exit 0) and is listed only with --warnings", c == 0 and "nothing refuses" in o)
c, o = runcheck(DATED + 'fw:D a backlog:ScopeDeliverable ; backlog:derivesFromMissionClause "a quote that is nowhere" .\n', ["--warnings"])
expect("4b with --warnings the advisory is listed with its repair", c == 2 and "METHOD-CITE" in o)
c, o = runcheck(DATED + 'fw:RR a backlog:RepairRound ; backlog:hasRoundNumber 1 .\n', ["--all"])
expect("5 a refusal whose rule has no repair record says so", c == 2 and "no repair record" in o)
c, o = runcheck(BOX + 'fw:R1 a backlog:RepairRound ; backlog:roundFor fw:Box ; backlog:hasRoundNumber 1 ; backlog:hasRoundRepairs "x" ; backlog:roundSatisfied false ; backlog:roundAt "2026-11-19T10:00:00Z"^^xsd:dateTime .\n')
expect("6 a Done box whose last round is not satisfied is refused with its repair", c == 2 and "RepairRoundsEndShape" in o and "METHOD-ROUNDS" in o)
c, o = runcheck(BOX + 'fw:R1 a backlog:RepairRound ; backlog:roundFor fw:Box ; backlog:hasRoundNumber 1 ; backlog:hasRoundRepairs "x" ; backlog:roundSatisfied false ; backlog:roundAt "2026-11-19T10:00:00Z"^^xsd:dateTime .\nfw:R2 a backlog:RepairRound ; backlog:roundFor fw:Box ; backlog:hasRoundNumber 2 ; backlog:hasRoundRepairs "y" ; backlog:roundSatisfied true ; backlog:roundAt "2026-11-19T11:00:00Z"^^xsd:dateTime .\n')
expect("7 the same box passes once a later round is satisfied", c == 0)
# round command: append, iterate, refuse after satisfied, never edit
with tempfile.TemporaryDirectory() as d:
    reg = os.path.join(d, "reg.ttl"); open(reg, "w").write(PRE + BOX.split("\n", 4)[-1])
    base = [sys.executable, TOOL, "round", reg, "--for", "Box", "--now", "2026-11-19T10:00:00Z"]
    r1 = subprocess.run(base + ["--repairs", "first repair"], capture_output=True, text=True); t1 = open(reg).read()
    r2 = subprocess.run(base + ["--repairs", "second repair", "--satisfied"], capture_output=True, text=True); t2 = open(reg).read()
    r3 = subprocess.run(base + ["--repairs", "after the end"], capture_output=True, text=True); t3 = open(reg).read()
    expect("8 a first round is appended as number 1, not satisfied", r1.returncode == 0 and "Round_RR_Box_1" in t1 and "roundSatisfied false" in t1)
    expect("9 the next round is appended as number 2 and ends the series, the first untouched", r2.returncode == 0 and "Round_RR_Box_2" in t2 and t2.startswith(t1) and "roundSatisfied true" in t2)
    expect("10 a round after a satisfied round is refused and writes nothing", r3.returncode == 2 and t3 == t2)
    from rdflib import Graph
    g = Graph(); g.parse(reg, format="turtle"); expect("11 the register still parses and holds two rounds", len([1 for _ in g.subjects(None, None)]) > 2 and t2.count("a backlog:RepairRound") == 2)
    reg2 = os.path.join(d, "reg2.ttl"); open(reg2, "w").write(PRE + BOX.split("\n", 4)[-1])
    b2 = [sys.executable, TOOL, "round", reg2, "--for", "Box", "--now", "2026-11-19T10:00:00Z"]
    subprocess.run(b2 + ["--repairs", "Fixed the date. Then rechecked.", "--satisfied"], capture_output=True, text=True); t = open(reg2).read()
    r = subprocess.run(b2 + ["--repairs", "after satisfied"], capture_output=True, text=True)
    expect("21 a round after a satisfied one is refused when the repairs text holds a full stop", r.returncode == 2 and open(reg2).read() == t)
    reg3 = os.path.join(d, "reg3.ttl"); open(reg3, "w").write(PRE + BOX.split("\n", 4)[-1])
    r = subprocess.run([sys.executable, TOOL, "round", reg3, "--for", "Box", "--repairs", "line one\nline two\ttab \"q\" back\\slash", "--now", "2026-11-19T10:00:00Z"], capture_output=True, text=True)
    g = Graph(); g.parse(reg3, format="turtle")
    expect("22 a repairs text with a line break, a tab, a quote and a backslash is written and the register still parses", r.returncode == 0 and any("line one\nline two\ttab" in str(o) for o in g.objects(None, None)))
    r = subprocess.run([sys.executable, TOOL, "round", reg3, "--for", "Bad Name", "--repairs", "x"], capture_output=True, text=True)
    expect("23 a subject name that is not a local name is refused and writes nothing", r.returncode == 1)
# a clean register is not refused on violations that exist only in the repairs file given with --repairs
with tempfile.TemporaryDirectory() as d:
    rf, pf = os.path.join(d, "reg.ttl"), os.path.join(d, "rep.ttl"); open(rf, "w").write(DATED); open(pf, "w").write(REPAIRS + UNDATED.split("\n", 4)[-1])
    r = subprocess.run([sys.executable, TOOL, "check", rf, "--repairs", pf], capture_output=True, text=True)
    expect("24 a clean register is not refused on content that only the --repairs file holds", r.returncode == 0 and "nothing refuses" in r.stdout)
# armed
with tempfile.TemporaryDirectory() as d:
    subprocess.run(["git", "init", "-q", d]); 
    r = subprocess.run([sys.executable, TOOL, "armed", "--root", d], capture_output=True, text=True)
    expect("12 a clone with nothing is refused (exit 2) and each missing layer is named", r.returncode == 2 and all(x in r.stdout for x in (".backlog-guard.json", "git hooks", "session hooks")) and "backlog_guard_install" in r.stdout)
    open(os.path.join(d, ".backlog-guard.json"), "w").write("{}")
    r = subprocess.run([sys.executable, TOOL, "armed", "--root", d], capture_output=True, text=True)
    expect("13 a clone with only the configuration is still refused", r.returncode == 2 and ".backlog-guard.json" not in r.stdout.split("missing")[1])
    os.makedirs(os.path.join(d, ".githooks")); open(os.path.join(d, ".githooks", "commit-msg"), "w").write("#!/bin/sh\n")
    subprocess.run(["git", "-C", d, "config", "core.hooksPath", ".githooks"])
    os.makedirs(os.path.join(d, ".claude")); open(os.path.join(d, ".claude", "settings.json"), "w").write('{"hooks": "backlog_guard_claude_hook"}')
    r = subprocess.run([sys.executable, TOOL, "armed", "--root", d], capture_output=True, text=True)
    expect("14 a clone with the configuration, the git hooks and the session hooks is armed (exit 0)", r.returncode == 0 and "armed" in r.stdout)
with tempfile.TemporaryDirectory() as d:
    subprocess.run(["git", "init", "-q", d]); q = os.path.join(d, "backlog-roadmap-framework"); os.makedirs(os.path.join(q, "03-tooling")); open(os.path.join(q, "VERSION.txt"), "w").write("1\n"); open(os.path.join(q, "03-tooling", "backlog_release_tool_v1_0_0.py"), "w").write("")
    subprocess.run(["git", "-C", d, "remote", "add", "origin", "git@github.com:the maintainer/Ontologies.git"])
    r = subprocess.run([sys.executable, TOOL, "armed", "--root", q], capture_output=True, text=True)
    expect("15 the framework's own clone is accepted, saying its release gate guards it", r.returncode == 0 and "release gate" in r.stdout)

def clone(d, cfg=True, hooks=True, sess=True):
    subprocess.run(["git", "init", "-q", d])
    if cfg: open(os.path.join(d, ".backlog-guard.json"), "w").write("{}")
    if hooks:
        os.makedirs(os.path.join(d, ".githooks")); open(os.path.join(d, ".githooks", "commit-msg"), "w").write("#!/bin/sh\n"); subprocess.run(["git", "-C", d, "config", "core.hooksPath", ".githooks"])
    if sess: os.makedirs(os.path.join(d, ".claude")); open(os.path.join(d, ".claude", "settings.json"), "w").write('{"x": "backlog_guard_claude_hook"}')
def armedrun(d): return subprocess.run([sys.executable, TOOL, "armed", "--root", d], capture_output=True, text=True)
for name, kw, word in (("25 a clone without the guard configuration", dict(cfg=False), ".backlog-guard.json"), ("26 a clone without the git hooks", dict(hooks=False), "git hooks"), ("27 a clone without the session hooks", dict(sess=False), "session hooks")):
    with tempfile.TemporaryDirectory() as d:
        clone(d, **kw); r = armedrun(d)
        expect(name + " is refused, naming only the missing layer", r.returncode == 2 and word in r.stdout.split("missing")[-1] and r.stdout.count("; ") == 0)
with tempfile.TemporaryDirectory() as d:
    clone(d, hooks=False); os.makedirs(os.path.join(d, ".githooks")); subprocess.run(["git", "-C", d, "config", "core.hooksPath", ".githooks"]); r = armedrun(d)
    expect("28 a hooks path set but no commit-msg hook is refused", r.returncode == 2 and "git hooks" in r.stdout)
with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, "packages", "fw"); os.makedirs(os.path.join(p, "03-tooling")); subprocess.run(["git", "init", "-q", d]); open(os.path.join(p, "VERSION.txt"), "w").write("1\n"); open(os.path.join(p, "03-tooling", "backlog_release_tool_v1_0_0.py"), "w").write("")
    r = armedrun(p)
    expect("29 an unarmed clone that vendors the framework package (VERSION.txt and a release tool, any name) is refused", r.returncode == 2 and "NOT ARMED" in r.stdout)
    q = os.path.join(d, "backlog-roadmap-framework"); os.makedirs(os.path.join(q, "03-tooling")); open(os.path.join(q, "VERSION.txt"), "w").write("1\n"); open(os.path.join(q, "03-tooling", "backlog_release_tool_v1_0_0.py"), "w").write("")
    r = armedrun(q)
    expect("30 the right directory name alone, without the framework origin, is refused", r.returncode == 2)
# the tools that open a box or a lineage refuse an unarmed clone
import shutil
def package(d, armed_layers=False, with_next=True):
    subprocess.run(["git", "init", "-q", d]); t = os.path.join(d, "pkg", "03-tooling"); os.makedirs(t)
    if with_next: shutil.copy(TOOL, os.path.join(t, os.path.basename(TOOL)))
    for stem in ("backlog_box_step", "backlog_open_lineage"):
        shutil.copy(newest("03-tooling", stem), os.path.join(t, os.path.basename(newest("03-tooling", stem))))
    os.symlink(os.path.join(PKG, "01-ontologies"), os.path.join(d, "pkg", "01-ontologies"))
    if armed_layers:
        open(os.path.join(d, ".backlog-guard.json"), "w").write("{}"); os.makedirs(os.path.join(d, ".githooks")); open(os.path.join(d, ".githooks", "commit-msg"), "w").write("#!/bin/sh\n")
        subprocess.run(["git", "-C", d, "config", "core.hooksPath", ".githooks"]); os.makedirs(os.path.join(d, ".claude")); open(os.path.join(d, ".claude", "settings.json"), "w").write('{"x": "backlog_guard_claude_hook"}')
    return os.path.join(d, "pkg", "03-tooling")
def box_open(t):
    return subprocess.run([sys.executable, os.path.join(t, os.path.basename(newest("03-tooling", "backlog_box_step"))), os.path.join(t, "..", "reg.ttl"), "open", "1", "t", "g", "K:analysis"], capture_output=True, text=True)
def lin_open(t):
    return subprocess.run([sys.executable, os.path.join(t, os.path.basename(newest("03-tooling", "backlog_open_lineage"))), "--lineage", "L_X", "--prefix", "X"], capture_output=True, text=True)
with tempfile.TemporaryDirectory() as d:
    t = package(d); r = box_open(t)
    expect("16 a box is not opened in an unarmed clone (exit 2, NOT ARMED, how to arm it)", r.returncode == 2 and "NOT ARMED" in r.stdout and "backlog_guard_install" in r.stdout)
    r = lin_open(t)
    expect("17 a lineage is not opened in an unarmed clone and no opening block is printed", r.returncode == 2 and "NOT ARMED" in r.stdout and "openedWithProfile" not in r.stdout)
with tempfile.TemporaryDirectory() as d:
    t = package(d, with_next=False); r = box_open(t); r2 = lin_open(t)
    expect("18 without the next-act tool beside them both refuse, saying where it comes from", r.returncode == 2 and "not beside" in r.stdout and r2.returncode == 2 and "not beside" in r2.stdout)
with tempfile.TemporaryDirectory() as d:
    t = package(d, armed_layers=True); r = box_open(t); r2 = lin_open(t)
    expect("19 in an armed clone the lineage opens as before and the box step goes past the guard", r2.returncode == 0 and "openedWithProfile" in r2.stdout and "NOT ARMED" not in r.stdout and "not beside" not in r.stdout)

with tempfile.TemporaryDirectory() as d:
    env = dict(os.environ); env.pop("BACKLOG_ARMED_STRICT", None)
    r = subprocess.run([sys.executable, TOOL, "armed", "--root", d], capture_output=True, text=True, env=env)
    expect("20 a throwaway package in the temporary directory, outside any git work tree, is a sandbox and is not checked unless the strict switch is set", r.returncode == 0 and "sandbox" in r.stdout)
    r = subprocess.run([sys.executable, TOOL, "armed", "--root", d], capture_output=True, text=True)
    expect("20b with the strict switch the same package is checked", r.returncode == 2)
with tempfile.TemporaryDirectory() as d:
    subprocess.run(["git", "init", "-q", d]); env = dict(os.environ); env.pop("BACKLOG_ARMED_STRICT", None)
    r = subprocess.run([sys.executable, TOOL, "armed", "--root", d], capture_output=True, text=True, env=env)
    expect("20c a real clone (a git work tree) under the temporary directory is checked, not exempted", r.returncode == 2 and "NOT ARMED" in r.stdout)
with tempfile.TemporaryDirectory() as d:
    t = package(d, with_next=False); env = dict(os.environ); env.pop("BACKLOG_ARMED_STRICT", None)
    r = subprocess.run([sys.executable, os.path.join(t, os.path.basename(newest("03-tooling", "backlog_box_step"))), os.path.join(t, "..", "reg.ttl"), "open", "1", "t", "g", "K:analysis"], capture_output=True, text=True, env=env)
    r2 = subprocess.run([sys.executable, os.path.join(t, os.path.basename(newest("03-tooling", "backlog_open_lineage"))), "--lineage", "L_X", "--prefix", "X"], capture_output=True, text=True, env=env)
    expect("32 a real clone (git work tree) under the temporary directory without the next-act tool is refused by the box tool and the lineage tool even with the strict switch unset", r.returncode == 2 and "not beside" in r.stdout and r2.returncode == 2 and "openedWithProfile" not in r2.stdout)
with tempfile.TemporaryDirectory() as d:
    clone(d, sess=False); os.makedirs(os.path.join(d, ".claude")); open(os.path.join(d, ".claude", "settings.json"), "w").write("{}")
    expect("33 a session settings file that does not name the guard hook is not the session layer", armedrun(d).returncode == 2)
with tempfile.TemporaryDirectory() as d:
    reg = os.path.join(d, "reg.ttl"); open(reg, "w").write(PRE + BOX.split("\n", 4)[-1])
    subprocess.run([sys.executable, TOOL, "round", reg, "--for", "Box", "--repairs", "--satisfied", "--now", "2026-11-19T10:00:00Z"], capture_output=True, text=True)
    expect("34 a repairs text that reads --satisfied does not set the satisfied flag", "roundSatisfied false" in open(reg).read())
print("VERDICT: %s -- %d expectations %s" % ("PASS" if not FAILS else "FAIL", N[0], "hold" if not FAILS else "(%d failed)" % len(FAILS)))
sys.exit(1 if FAILS else 0)
