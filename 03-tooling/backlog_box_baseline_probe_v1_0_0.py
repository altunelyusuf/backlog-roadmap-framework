#!/usr/bin/env python3
"""Probe of the base plan of a box (G187): the real validator on a scratch register of boxes, each with or without a current base plan, in a lineage that plans its dates or not; a finished box
measured against its baseline is not refused for ending when it did, an open box whose window moved still is."""
import glob, re, subprocess, sys, tempfile, os
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", p)[0]]
VAL = sorted(glob.glob(PKG + "/03-tooling/backlog_validate_v*.py"), key=sv)[-1]
X = "^^xsd:dateTime"
D = lambda t: '"2026-11-02T%s:00Z"%s' % (t, X)
def box(name, lin="LinOn", base=True, end=True, current=True, state=None, window=None):
    s = f"ex:I_{name} a backlog:Iteration ; backlog:belongsToLineage ex:{lin} ; backlog:iterationStart {D('11:00')}"
    if window: s += f" ; backlog:iterationEnd {D(window)}"
    if state: s += f" ; backlog:hasState backlog:{state}"
    s += " .\n"
    if base:
        s += f"ex:PB_{name} a backlog:PlanBaseline ; backlog:baselineFor ex:I_{name} ; backlog:baselinedAt {D('11:00')} ; backlog:isCurrentBaseline {'true' if current else 'false'} ; backlog:hasBaselineStart {D('11:00')}"
        if end: s += f" ; backlog:hasBaselineEnd {D('12:00')}"
        s += " .\n"
    return s
CASES = [("Ok", {}, set()), ("NoBase", {"base": False}, {"BP_NOBASEPLAN"}), ("NoEnd", {"end": False}, {"BP_NOBASEPLAN"}), ("OnlySuperseded", {"current": False}, {"BP_NOBASEPLAN"}),
         ("NotBound", {"lin": "LinOff", "base": False}, set()),
         ("FinishedLate", {"state": "Done", "window": "13:30"}, set()),
         ("OpenMovedSilently", {"window": "13:30"}, {"SILENT"})]
PRE = """@prefix backlog: <http://example.org/backlog#> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> . @prefix ex: <http://example.org/bbprobe#> .
ex:LinOn a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_PlannedDates ; backlog:humanApprovalLevel 3 .
ex:LinOff a backlog:Lineage ; backlog:humanApprovalLevel 3 .
"""
data = PRE + "".join(box(n, **k) for n, k, _ in CASES)
with tempfile.NamedTemporaryFile("w", suffix=".ttl", delete=False) as f:
    f.write(data); tmp = f.name
out = subprocess.run([sys.executable, VAL, tmp], capture_output=True, text=True).stdout
os.unlink(tmp)
got = {}
for line in out.splitlines():
    m = re.search(r"\[Violation\]\s+(I_\S+)\s+(.*)", line)
    if not m: continue
    code = "BP_NOBASEPLAN" if "BP_NOBASEPLAN" in m.group(2) else ("SILENT" if "disagrees with its baseline" in m.group(2) else None)
    if code: got.setdefault(m.group(1), set()).add(code)
fails = 0
for n, k, want in CASES:
    ok = got.get("I_" + n, set()) == want
    print(("PASS  " if ok else "FAIL  ") + f"{n}: " + (("refused as " + ",".join(sorted(want))) if want else "raises neither message")); fails += (not ok)
# the step tool on a planted register: boxes 1-3 delivered 2, 3 and 2 points, starting 00:00, 01:00, 03:00, box 4 starts 04:00 with 3.5 points -> paces 2.0, 1.5, 2.0, median 2.0;
# the planned end is 04:00 + 3.5 / 2.0 x 1.5 = 06:37:30
STEP = sorted(glob.glob(PKG + "/03-tooling/backlog_box_step_v*.py"), key=sv)[-1]
REG = """@prefix backlog: <http://example.org/backlog#> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> . @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> . @prefix fw: <http://example.org/backlog-framework-register#> .
fw:L_T a backlog:Lineage .
"""
for i, (h, e, st) in enumerate([(0, 2, "Done"), (1, 3, "Done"), (3, 2, "Done"), (4, 3.5, "InProgress")], 1):
    REG += f"fw:It_T_{i} a backlog:Iteration ; backlog:iterationStart \"2026-11-01T0{h}:00:00Z\"^^xsd:dateTime .\nfw:S{i} a backlog:Story ; backlog:hasEffort {float(e)} ; backlog:hasState backlog:{st} .\nfw:Ev{i} backlog:plannedInto fw:It_T_{i} ; backlog:plansItem fw:S{i} .\n"
def run(reg_text, n=4):
    with tempfile.TemporaryDirectory() as d:
        rp = d + "/r.ttl"; open(rp, "w").write(reg_text)
        code = ("import importlib.util,sys;sp=importlib.util.spec_from_file_location('st',%r);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);"
                "m.cmd_baseline(m.Reg(%r,'L_T','T'),%d)") % (STEP, rp, n)
        env = dict(os.environ)
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=PKG + "/03-tooling")
        return r, open(rp).read()
r, t = run(REG)
ok = "ends 2026-11-01 06:37Z" in r.stdout and "2.00 points per hour" in r.stdout and "hasBaselineEnd \"2026-11-01T06:37:30Z\"" in t and "isCurrentBaseline true" in t and "baselineFor fw:It_T_4" in t
print(("PASS  " if ok else "FAIL  ") + "the tool records the base plan of a box: start of the box, end = start + points / median delivered pace x 1.5"); fails += (not ok)
if not ok: print(r.stdout[-300:], r.stderr[-300:])
r2, _ = run(t)
ok = r2.returncode != 0 and "already has a base plan" in (r2.stdout + r2.stderr)
print(("PASS  " if ok else "FAIL  ") + "a second base plan for the same box is refused (moving it is a Rebaseline)"); fails += (not ok)
r3, _ = run(REG.split("fw:It_T_2")[0].replace("backlog:Done", "backlog:Proposed") + "fw:It_T_4 a backlog:Iteration ; backlog:iterationStart \"2026-11-01T04:00:00Z\"^^xsd:dateTime .\n")
ok = r3.returncode != 0 and "no pair of consecutive boxes" in (r3.stdout + r3.stderr)
print(("PASS  " if ok else "FAIL  ") + "with no pace delivered in earlier boxes no base plan is invented"); fails += (not ok)
print("VERDICT   :", "PASS" if not fails else "FAIL"); sys.exit(1 if fails else 0)
