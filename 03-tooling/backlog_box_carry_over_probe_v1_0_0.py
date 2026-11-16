#!/usr/bin/env python3
"""Probe of the carry-over clause of the box tool's close (box 54): a story planned into the box and not finished by the close is named on the closing review as carried forward; a Done story, a story of another box and a story this close finishes are not.
Usage: probe [--tool PATH]."""
import glob, re, subprocess, sys, tempfile, os
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", p)[0]]
STEP = sorted(glob.glob(PKG + "/03-tooling/backlog_box_step_v*.py"), key=sv)[-1]
if "--tool" in sys.argv:
    STEP = sys.argv[sys.argv.index("--tool") + 1]
REG = """@prefix backlog: <http://example.org/backlog#> . @prefix fw: <http://example.org/backlog-framework-register#> .
fw:L_T a backlog:Lineage .
fw:It_T_1 a backlog:Iteration . fw:It_T_2 a backlog:Iteration .
fw:S_open a backlog:Story ; backlog:hasState backlog:InProgress ; backlog:memberOfContainer fw:Register , fw:It_T_1 .
fw:S_planned a backlog:Story ; backlog:hasState backlog:Proposed ; backlog:memberOfContainer fw:Register , fw:Pkg_T , fw:It_T_1 .
fw:S_late a backlog:Story ; backlog:hasState backlog:Proposed .
fw:S_late backlog:memberOfContainer fw:It_T_1 .
fw:S_done a backlog:Story ; backlog:hasState backlog:Done ; backlog:memberOfContainer fw:It_T_1 .
fw:S_other a backlog:Story ; backlog:hasState backlog:Proposed ; backlog:memberOfContainer fw:It_T_2 .
fw:S_prog a backlog:Story ; backlog:hasState backlog:InProgress ; backlog:memberOfContainer fw:It_T_1 .
fw:S_names a backlog:Story ; backlog:hasState backlog:Proposed ; backlog:memberOfContainer fw:It_T_2 ; backlog:targetsIteration fw:It_T_1 .
fw:S_near a backlog:Story ; backlog:hasState backlog:Proposed ; backlog:memberOfContainer fw:It_T_11 .
"""
def clause(reg_text, it, finished):
    with tempfile.TemporaryDirectory() as d:
        rp = d + "/r.ttl"; open(rp, "w").write(reg_text)
        code = ("import importlib.util;sp=importlib.util.spec_from_file_location('st',%r);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);"
                "reg=m.Reg(%r,'L_T','T');print('CLAUSE', repr(m.carry_over_clause(reg,%r,%r)))") % (STEP, rp, it, set(finished))
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=PKG + "/03-tooling")
        return r.stdout + r.stderr
fails = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: fails.append(name)
o = clause(REG, "It_T_1", ["S_open"])
expect("a planned story the close does not finish is flagged, with the one that has its box in a separate statement", "fw:S_planned" in o and "fw:S_late" in o)
expect("a story this close finishes is not flagged", "fw:S_open" not in o)
expect("a Done member is not flagged", "fw:S_done" not in o)
expect("a story of another box is not flagged, nor one of a box whose name begins with this one's", "fw:S_other" not in o and "fw:S_near" not in o)
o2 = clause(REG, "It_T_1", ["S_open", "S_planned", "S_late", "S_prog"])
expect("when every member is finished or Done, no clause is written", "CLAUSE ''" in o2)
expect("an unfinished story that is InProgress, not only Proposed, is flagged", "fw:S_prog" in o)
expect("a story that only names the box in another property, not as its container, is not flagged", "fw:S_names" not in o)
expect("the clause is the property of the shape that asks for it", "backlog:flagsForCarryOver" in o)
print("VERDICT: %s -- %d expectations %s" % ("PASS" if not fails else "FAIL", 8, "hold" if not fails else "(%d failed)" % len(fails)))
sys.exit(1 if fails else 0)
