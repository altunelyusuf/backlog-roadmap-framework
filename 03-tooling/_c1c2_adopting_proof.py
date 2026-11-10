#!/usr/bin/env python3
"""Proof for C1/C2 of the IPage box-tool-for-an-adopting-register handover, against backlog_box_step_v2_0_0.py:
a small register in a namespace that is NOT the framework's (prefix pcl:, IRI http://example.org/ipage-register#)
is opened, worked, and closed -- and no new subject lands in the framework's own namespace (C2), and the result
is the same whether the fixture is reserialised by rdflib first (C1, for the parts this slice already reads as a graph)."""
import os, re, shutil, subprocess, sys, tempfile, json, time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "backlog_box_step_v2_0_0.py")
bad, COUNT = [], [0]


def expect(name, ok):
    COUNT[0] += 1
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok:
        bad.append(name)


def make_fixture(reserialize=False):
    work = tempfile.mkdtemp()
    pk = os.path.join(work, "pkg")
    os.makedirs(os.path.join(pk, "01-ontologies"))
    os.makedirs(os.path.join(pk, "03-tooling"))
    shutil.copy(TOOL, os.path.join(pk, "03-tooling", os.path.basename(TOOL)))
    reg = os.path.join(pk, "01-ontologies", "ipage_abox_v0_1_0.ttl")
    ttl = """@prefix pcl: <http://example.org/ipage-register#> .
@prefix backlog: <http://example.org/backlog#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
<http://example.org/ipage> owl:versionInfo "0.1.0" .
pcl:D1 a backlog:Lineage ; backlog:hasLineageStatus backlog:LS_InProgress .
pcl:KO a backlog:KickOff ; backlog:kicksOffLineage pcl:D1 .
pcl:ST_D1_A a backlog:Story ; backlog:hasIdentifier "A" ; backlog:hasState backlog:Proposed ; backlog:hasEffort 2.0 ;
    backlog:belongsToLineage pcl:D1 ; backlog:producedByStage pcl:Out_B .
pcl:AC_D1_A a backlog:AcceptanceCriterion ; backlog:hasGherkinText "Given a, When b, Then c." .
"""
    open(reg, "w").write(ttl)
    if reserialize:
        import rdflib
        g = rdflib.Graph().parse(reg, format="turtle")
        g.serialize(destination=reg, format="turtle")
    git(pk, "init", "-q")
    open(os.path.join(pk, "03-tooling", "other.py"), "w").write("x = 1\n")
    git(pk, "add", "-A")
    git(pk, "-c", "user.email=p@p", "-c", "user.name=p", "commit", "-qm", "p")
    git(pk, "update-ref", "refs/remotes/origin/main", "HEAD")
    return work, pk, reg


def git(pk, *a):
    return subprocess.run(["git", "-C", pk] + list(a), capture_output=True, text=True)


def run(pk, reg, *a):
    r = subprocess.run([sys.executable, os.path.join(pk, "03-tooling", os.path.basename(TOOL)), reg, "--lineage", "pcl:D1", "--prefix", "D1"] + list(a),
                        capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def one_pass(reserialize):
    work, pk, reg = make_fixture(reserialize)
    rc, out = run(pk, reg, "open", "1", "t", "g", "A", "--capacity", "3")
    ok_open = rc == 0 and "now InProgress" in out
    text_after_open = open(reg).read()
    ok_ns_open = "example.org/backlog-framework-register#" not in text_after_open and "\nfw:" not in text_after_open and not re.search(r"(?<![A-Za-z0-9_])fw:", text_after_open)
    ok_real_ns = "pcl:ST_D1_A" in text_after_open and "pcl:It_D1_1 a backlog:Iteration" in text_after_open
    time.sleep(1.1)
    rc2, out2 = run(pk, reg, "act", "1", "A", "worked on it")
    ok_act = rc2 == 0 and "checkpoint 1" in out2
    art = os.path.join(pk, "03-tooling", "artifact.txt")
    open(art, "w").write("evidence\n")
    spec = {"stories": {"A": {"artifact": "03-tooling/artifact.txt", "method": "m", "tool": "t", "harness": "h", "demo": "d", "result": "r"}},
            "run_result": "ok", "release_title": "rel", "findings": [], "observations": []}
    sp = os.path.join(work, "spec.json")
    json.dump(spec, open(sp, "w"))
    rc3, out3 = run(pk, reg, "close", "1", sp)
    ok_close = rc3 == 0 and "closed" in out3
    final = open(reg).read()
    ok_ns_close = "example.org/backlog-framework-register#" not in final and not re.search(r"(?<![A-Za-z0-9_])fw:", final)
    ok_done = re.search(r"pcl:ST_D1_A a backlog:Story .*?backlog:hasState backlog:Done", final, re.S) is not None
    shutil.rmtree(work, ignore_errors=True)
    return dict(ok_open=ok_open, ok_ns_open=ok_ns_open, ok_real_ns=ok_real_ns, ok_act=ok_act, ok_close=ok_close, ok_ns_close=ok_ns_close, ok_done=ok_done,
                out_open=out, out_close=out3)


r1 = one_pass(reserialize=False)
expect("open succeeds on a register whose own namespace is not the framework's (pcl:, not fw:)", r1["ok_open"])
expect("after open, no new subject is written into the framework's own literal namespace (C2)", r1["ok_ns_open"])
expect("after open, the new box and the existing story are addressed in the register's own namespace (pcl:)", r1["ok_real_ns"])
expect("act records a checkpoint on the adopting register", r1["ok_act"])
expect("close succeeds on the adopting register", r1["ok_close"])
expect("after close, still no subject in the framework's own literal namespace (C2)", r1["ok_ns_close"])
expect("the story ends Done, addressed as pcl:ST_D1_A (C2: its own namespace, not retargeted)", r1["ok_done"])

r2 = one_pass(reserialize=True)
expect("the same result holds when the fixture is reserialised by rdflib before the run starts (C1, partial: the read side is namespace-correct under reserialisation)", r2["ok_open"] and r2["ok_close"] and r2["ok_done"])

print("VERDICT: %s" % ("PASS -- %d expectations hold" % COUNT[0] if not bad else "FAIL -- " + "; ".join(bad)))
if bad:
    print("---- last open output ----\n" + r1["out_open"][-800:])
    print("---- last close output ----\n" + r1["out_close"][-800:])
sys.exit(1 if bad else 0)
