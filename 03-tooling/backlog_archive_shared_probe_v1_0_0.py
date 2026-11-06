#!/usr/bin/env python3
"""backlog_archive_shared_probe v1.0.0 -- setting down a lineage leaves live what a live lineage uses (Lineage 29, governance story).

The four agent roles (builder, verifier, overseer, approver) are declared once and used by the runs of every lineage. v2.10.0 of the archive tool counted the run of a live
lineage as a candidate for the archive, so the roles went with the archived runs and 63 checks of live lineages failed on a copy of the register. Cases, on a small register:
the archivable lineage's own story and runs are set down; a role used only by archived runs goes with them; a role used by a live run stays; an entity and a gap that only the
archived lineage covers go with it (the closed cluster); an event that points at an archived story goes with it; a cluster one of whose members points at a live story stays live.
Seven mutants of the tool are made in a temporary folder and each must fail at least one case: the pruning removed (the v2.10.0 reading), the pruning dropping every
candidate, the pruning blind to outgoing references, the cluster move removed, the forward closure removed, the reverse closure removed, the live-lineage test removed."""
import glob, importlib.util, os, re, sys, tempfile
from rdflib import Graph
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
tool = sorted(glob.glob(os.path.join(HERE, "backlog_lineage_archive_v*.py")), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(tool); sys.exit(0)
bad = []
def expect(n, ok):
    print(("PASS  " if ok else "FAIL  ") + n)
    if not ok: bad.append(n)
TTL = """@prefix backlog: <http://example.org/backlog#> . @prefix fw: <http://example.org/r#> .
fw:Root a backlog:Backlog ; backlog:isRegisterRoot true .
fw:La a backlog:Lineage ; backlog:lineageForMission fw:Ma . fw:Ma a backlog:Mission ; backlog:hasMissionOutcome backlog:Out_Achieved .
fw:Lb a backlog:Lineage ; backlog:lineageForMission fw:Mb . fw:Mb a backlog:Mission ; backlog:hasMissionOutcome backlog:Out_InFlight .
fw:Sa a backlog:Story ; backlog:belongsToLineage fw:La ; backlog:responsible fw:Run_a , fw:Run_c ; backlog:coversEntity fw:Ent , fw:Ent3 .
fw:Sb a backlog:Story ; backlog:belongsToLineage fw:Lb ; backlog:responsible fw:Run_b ; backlog:dependsOn fw:Sa ; backlog:noted fw:Evt2 .
fw:Run_a a backlog:ExecutorInstance ; backlog:instanceOf fw:Exec_Shared . fw:Run_b a backlog:ExecutorInstance ; backlog:instanceOf fw:Exec_Shared .
fw:Exec_Shared a backlog:Executor_SingleAgent .
fw:Run_c a backlog:ExecutorInstance ; backlog:instanceOf fw:Exec_Only . fw:Exec_Only a backlog:Executor_SingleAgent .
fw:Ent a backlog:Thing . fw:Gap a backlog:Thing ; backlog:namesEntity fw:Ent . fw:Ent backlog:namedByGap fw:Gap .
fw:Ent3 a backlog:Thing ; backlog:namedByGap fw:Gap3 . fw:Gap3 a backlog:Thing ; backlog:namesEntity fw:Ent3 ; backlog:alsoAbout fw:Sb .
fw:Evt a backlog:Event ; backlog:about fw:Sa . fw:Evt2 a backlog:Event ; backlog:about fw:Sa .
"""
NAMES = ["Sa", "Run_a", "Run_c", "Exec_Only", "Ent", "Gap", "Evt", "Evt2", "Sb", "Run_b", "Exec_Shared", "Ent3", "Gap3"]
def run(modpath):
    spec = importlib.util.spec_from_file_location("lar", modpath); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    g = Graph().parse(data=TTL, format="turtle")
    ns = lambda n: m.URIRef("http://example.org/r#" + n)
    part, keep = m.partition(g, [ns("La")])
    return {n: ns(n) in part for n in NAMES}
GO = ["Sa", "Run_a", "Run_c", "Exec_Only", "Ent", "Gap", "Evt", "Evt2"]; STAY = ["Sb", "Run_b", "Exec_Shared", "Ent3", "Gap3"]
def right(r): return all(r[n] for n in GO) and not any(r[n] for n in STAY)
r = run(tool)
expect("the archived lineage's story and its runs are set down", r["Sa"] and r["Run_a"] and r["Run_c"])
expect("a role used only by archived runs is set down with them", r["Exec_Only"])
expect("a role used by a live run stays live", not r["Exec_Shared"])
expect("the live lineage's story and run stay", not r["Sb"] and not r["Run_b"])
expect("an entity and a gap that only the archived lineage covers go with it", r["Ent"] and r["Gap"])
expect("an event that points at an archived story goes with it, also when a live story points at the event (the reference closure)", r["Evt"] and r["Evt2"])
expect("a live story that depends on an archived one stays live", not r["Sb"])
expect("a cluster of which one member points at a live story stays live as a whole", not r["Ent3"] and not r["Gap3"])
src = open(tool).read()
MUT = [
 ("the pruning removed (the v2.10.0 reading)", "cand.discard(s); changed = True\n    changed = True", "pass\n    changed = True"),
 ("the pruning drops every candidate", "if not (all(x in part or x in cand for x in inc) and all(o in part or o in cand for o in out)):\n                cand.discard(s)", "if True:\n                cand.discard(s)"),
 ("the pruning blind to outgoing references", "if not (all(x in part or x in cand for x in inc) and all(o in part or o in cand for o in out)):\n                cand.discard(s)", "if not (all(x in part or x in cand for x in inc)):\n                cand.discard(s)"),
 ("the cluster move removed", "part.add(s); cand.discard(s); changed = True", "cand.discard(s); changed = True"),
 ("the forward closure removed", "if any(o in part for o in g.objects(s, None) if isinstance(o, URIRef)):", "if False:"),
 ("the reverse closure removed", "if incoming and all(x in part for x in incoming):", "if False:"),
 ("the live-lineage test removed", "or s in live_subj or s in keep_live: continue\n            if s in keep_live: continue\n            if any(o in part", "or s in keep_live: continue\n            if s in keep_live: continue\n            if any(o in part"),
]
tmp = tempfile.mkdtemp(prefix="archshared_")
for k, (name, old, new) in enumerate(MUT):
    ok_text = src.count(old) >= 1
    expect("mutant text is present in the tool (%s)" % name, ok_text)
    if not ok_text: continue
    f = os.path.join(tmp, "mut%d.py" % k); open(f, "w").write(src.replace(old, new, 1))
    try: caught = not right(run(f))
    except Exception: caught = True
    expect("mutant caught: %s" % name, caught)
import shutil; shutil.rmtree(tmp, ignore_errors=True)
print("VERDICT   :", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
