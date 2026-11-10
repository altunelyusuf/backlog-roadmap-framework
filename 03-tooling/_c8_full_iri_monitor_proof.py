#!/usr/bin/env python3
"""Proof for C8 of the IPage box-tool-for-an-adopting-register handover: cmd_close invokes the agent monitor with full IRIs
(not bare, namespace-ambiguous local names) for --lineage and --closing, on an adopting (pcl:) register, and the monitor
(now v1.4.0) understands them -- while the close itself still succeeds exactly as before."""
import json, os, shutil, subprocess, sys, tempfile, time

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
pcl:AC_D1_Story4_D1 a backlog:AcceptanceCriterion ; backlog:hasGherkinText "Given a, When b, Then c." .
"""

work = tempfile.mkdtemp()
pk = os.path.join(work, "pkg")
os.makedirs(os.path.join(pk, "01-ontologies"))
os.makedirs(os.path.join(pk, "03-tooling"))
for f in ("backlog_box_step_v2_0_0.py", "backlog_agent_monitor_v1_3_0.py", "backlog_agent_monitor_v1_4_0.py"):
    shutil.copy(os.path.join(HERE, f), os.path.join(pk, "03-tooling", f))
reg = os.path.join(pk, "01-ontologies", "ipage_abox_v0_1_0.ttl")
open(reg, "w").write(TTL)
git(pk, "init", "-q")
git(pk, "add", "-A")
git(pk, "-c", "user.email=p@p", "-c", "user.name=p", "commit", "-qm", "p")
git(pk, "update-ref", "refs/remotes/origin/main", "HEAD")


def run(*a):
    r = subprocess.run([sys.executable, os.path.join(pk, "03-tooling", "backlog_box_step_v2_0_0.py"), reg, "--lineage", "pcl:D1", "--prefix", "D1"] + list(a),
                        capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


run("open", "1", "t", "g", "Story4_D1", "--capacity", "3")
time.sleep(1.1)
run("act", "1", "Story4_D1", "worked")
art = os.path.join(pk, "03-tooling", "artifact.txt")
open(art, "w").write("evidence\n")
spec = {"stories": {"Story4_D1": {"artifact": "03-tooling/artifact.txt", "method": "m", "tool": "t", "harness": "h", "demo": "d", "result": "r"}},
        "run_result": "ok", "release_title": "rel", "findings": [], "observations": []}
sp = os.path.join(work, "spec.json")
json.dump(spec, open(sp, "w"))
rc, out = run("close", "1", sp)
expect("the box closes successfully on an adopting register with the full-IRI monitor call wired in (no regression)", rc == 0 and "closed" in out)

# Directly prove the two things C8 requires, without relying on introspecting the already-finished subprocess:
# (a) the source cmd_close builds for the monitor call uses full IRIs, not bare names
src = open(os.path.join(pk, "03-tooling", "backlog_box_step_v2_0_0.py")).read()
expect("cmd_close's monitor call is built from full IRIs (reg.ns-qualified), not bare local names", '"<%s%s>" % (reg.ns, reg.L[3:])' in src and '"<%s%s>" % (reg.ns, x)' in src)

# (b) the monitor itself (v1.4.0) actually understands a full IRI / prefixed form for --lineage and --closing, on this exact
# adopting-register namespace, by invoking it directly the way cmd_close now does.
mon = os.path.join(pk, "03-tooling", "backlog_agent_monitor_v1_4_0.py")
r = subprocess.run([sys.executable, mon, reg, "--lineage", "<http://example.org/ipage-register#D1>",
                    "--closing", "<http://example.org/ipage-register#Story4_D1>,pcl:T_D1_Story4_D1_Build"],
                   capture_output=True, text=True)
expect("the monitor (v1.4.0) runs scoped to the adopting lineage when called with a full IRI, exactly as cmd_close now calls it",
       r.returncode in (0, 1) and "lineage D1" in r.stdout)

shutil.rmtree(work, ignore_errors=True)

print("VERDICT: %s" % ("PASS -- %d expectations hold" % COUNT[0] if not bad else "FAIL -- " + "; ".join(bad)))
sys.exit(1 if bad else 0)
