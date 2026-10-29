#!/usr/bin/env python3
"""backlog_open_lineage_probe v1.1.0 -- proof that the opening block carries the profile's rule sets and that the shape holds a lineage to them (G155), and (v1.1.0, G177) that a lineage opened under the adaptive profile can plan after its Backlog stage."""
import glob, hashlib, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
tool = latest("03-tooling/backlog_open_lineage_v*.py"); val = latest("03-tooling/backlog_validate_v*.py")
if sys.argv[1:] == ["--deps"]:
    for x in (tool, val, latest("01-ontologies/backlog_abox_v*.ttl"), latest("02-shacl-safeguards/backlog_shacl_v*.ttl"), latest("03-tooling/backlog_pipeline_verify_v*.py"), latest("01-ontologies/backlog_tbox_v*.ttl")): print(x)
    print(os.path.abspath(__file__)); sys.exit(0)
bad = []
def expect(n, ok):
    print(("PASS  " if ok else "FAIL  ") + n)
    if not ok: bad.append(n)
run = lambda *a: subprocess.run([sys.executable, tool, *a], capture_output=True, text=True)
ag = run("--profile", "Profile_Agentic", "--lineage", "L", "--prefix", "x").stdout
st = run("--profile", "Profile_Standard", "--lineage", "L", "--prefix", "x").stdout
expect("the agentic block adopts the accountability rule set and the recording pair", all(k in ag for k in ("RS_AgentAccountability", "RS_StatusHistoryRecorded", "RS_FlowPointsRecorded")) and "adoptionRecordedAtOpen true" in ag)
expect("the standard block does not adopt the accountability rule set", "RS_AgentAccountability" not in st and "RS_RepairReprioritises" in st)
expect("an unknown profile is refused", run("--profile", "Profile_Nope", "--lineage", "L").returncode == 2)
ls = run("--list").stdout
expect("--list names both profiles", "Profile_Agentic" in ls and "Profile_Standard" in ls)
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/open-probe#> .\nx:L a backlog:Lineage .\n"
PROF = "backlog:Profile_Agentic a backlog:OpeningProfile ; backlog:profileIncludes " + " , ".join("backlog:" + m for m in re.findall(r"backlog:(RS_\w+)", ag)) + " .\n"
def count(body):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(HEAD + PROF + body)
        out = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=900).stdout
    return sum(1 for ln in out.splitlines() if "[Violation]" in ln and "G155:" in ln)
expect("a lineage that wrote the tool's block entire draws no profile finding", count(ag) == 0)
expect("the same block with one rule set left out draws the finding", count(ag.replace("RS_AgentAccountability", "RS_StatusHistoryRecorded", 1)) == 1)
# ---- v1.1.0 (G177): planning after the Backlog stage closed, with and without a digest table ----
pv, tbox = latest("03-tooling/backlog_pipeline_verify_v*.py"), latest("01-ontologies/backlog_tbox_v*.ttl")
ad = run("--profile", "Profile_Adaptive", "--lineage", "L", "--prefix", "x").stdout
expect("the adaptive block adopts a digest table", "RS_DigestTable_v5" in ad)
no_table = re.sub(r"backlog:RS_DigestTable_v5 ,\s*|\s*,\s*backlog:RS_DigestTable_v5", lambda m: "" if m.group(0).endswith(",") or m.group(0).startswith("backlog:RS_DigestTable_v5") else "", ad)
import importlib.util
from rdflib import Graph, URIRef
sp = importlib.util.spec_from_file_location("pv", pv); mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod)
PRE = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/open-probe#> .\nx:L a backlog:Lineage ; backlog:lineageForMission x:M .\nx:M a backlog:Mission .\n"
STORY = "x:S a backlog:Story ; backlog:belongsToLineage x:L .\n"
TASK = "x:T a backlog:ExecutionTask ; backlog:belongsToLineage x:L .\n"
STAGES = ("Mission", "Scope", "Goal", "Objective", "Backlog")
def chain(block, table):
    g = Graph().parse(data=PRE + block + STORY, format="turtle")
    mod.STAGE_TYPES = mod._load_stage_types(tbox, table=table)
    out, prev = "", None
    for st in STAGES:
        d = mod.state_digest(g, "Stage_" + st, URIRef("http://example.org/open-probe#L"), admitted=table in ("v4", "v5"), change_managed=table == "v5")
        out += "x:O%s a backlog:StageOutput ; backlog:outputOfStage backlog:Stage_%s ; backlog:belongsToLineage x:L ; backlog:hasStateDigest \"%s\" %s.\n" % (st, st, d, ("; backlog:consumesOutput x:O%s " % prev) if prev else "")
        prev = st
    return PRE + block + STORY + out
def verifies(text, extra=""):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "c.ttl"); open(f, "w").write(text + extra)
        return subprocess.run([sys.executable, pv, f, tbox, "--lineage", "L"], capture_output=True, text=True, timeout=900).returncode == 0
AD, NT = chain(ad, "v5"), chain(no_table, "v1")
expect("a lineage opened with the adaptive block reproduces its chain", verifies(AD))
expect("it still reproduces after a task is planned into a box", verifies(AD, TASK))
expect("the same lineage opened without a digest table reproduces before a task", verifies(NT))
expect("and stops reproducing once a task is planned (the fault G177 names)", not verifies(NT, TASK))
print("VERDICT   :", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
