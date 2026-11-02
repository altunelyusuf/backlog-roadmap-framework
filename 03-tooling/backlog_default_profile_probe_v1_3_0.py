#!/usr/bin/env python3
"""backlog_default_profile_probe v1.1.0 -- a profile can be marked the default and the opening tool uses it (Lineage 24, D3).

Three registers are planted: one profile marked, none marked, two marked. The opening tool run with no profile writes the block of the marked profile, and refuses (exit 2, naming the problem) with none and with two; the
validator refuses two marks and accepts one. Exit 0 when every expectation holds."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
OPEN, VAL = latest("03-tooling/backlog_open_lineage_v*.py"), latest("03-tooling/backlog_validate_v*.py")
if sys.argv[1:] == ["--deps"]:
    print("\n".join([OPEN, VAL, latest("02-shacl-safeguards/backlog_shacl_v*.ttl"), latest("01-ontologies/backlog_tbox_v*.ttl"), latest("01-ontologies/backlog_abox_v*.ttl"), os.path.abspath(__file__)])); sys.exit(0)
bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/dp#> .\nbacklog:RS_One a backlog:RuleSet .\n"
def reg(a, b):
    mark = lambda f: " ; backlog:isDefaultProfile true" if f else ""
    return HEAD + "x:A a backlog:OpeningProfile%s ; backlog:profileIncludes backlog:RS_One .\nx:B a backlog:OpeningProfile%s ; backlog:profileIncludes backlog:RS_One .\n" % (mark(a), mark(b))
def opened(ttl):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "r.ttl"); open(f, "w").write(ttl)
        r = subprocess.run([sys.executable, OPEN, "--abox", f, "--lineage", "L", "--prefix", "x"], capture_output=True, text=True)
    return r.returncode, r.stdout
def two_marks(ttl):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(ttl)
        out = subprocess.run([sys.executable, VAL, f], capture_output=True, text=True, timeout=900).stdout
    return any("[Violation]" in ln and "DEFAULT_TWO" in ln for ln in out.splitlines())
rc, out = opened(reg(False, True))
expect("with one profile marked, the tool opens the lineage with that profile", rc == 0 and "openedWithProfile backlog:B" in out)
rc, out = opened(reg(False, False))
expect("with none marked, the tool refuses and says none is", rc == 2 and "none is" in out)
rc, out = opened(reg(True, True))
expect("with two marked, the tool refuses and says two are", rc == 2 and "2 are" in out)
expect("the validator refuses two planted marks", two_marks(reg(True, True)))
# v1.1.0: the validator also reads the profiles of the live register, so the live default counts as a mark beside any mark planted
expect("the validator refuses a planted mark beside the live default (two marks)", two_marks(reg(False, True)))
expect("the validator accepts the live default alone (a planted register with no mark)", not two_marks(reg(False, False)))
# v1.1.0 (Lineage 25): the live register. Exactly one profile is marked and it is AAL; the opening tool run with no profile opens with it; the other profiles keep their rule sets.
from rdflib import Graph, Namespace, Literal
B = Namespace("http://example.org/backlog#")
AB = latest("01-ontologies/backlog_abox_v*.ttl"); g = Graph().parse(AB)
marked = [str(x).rsplit("#", 1)[-1] for x in g.subjects(B.isDefaultProfile, Literal(True))]
expect("on the live register exactly one profile is marked as the default, the agentic adaptive profile", marked == ["Profile_AgenticAdaptive"])
inc = lambda p: len(set(g.objects(B[p], B.profileIncludes)))
expect("the standard, agentic and non-agentic adaptive profiles keep nine, ten and sixteen rule sets, and AAL twenty", (inc("Profile_Standard"), inc("Profile_Agentic"), inc("Profile_Adaptive"), inc("Profile_AgenticAdaptive")) == (9, 10, 16, 20))
r = subprocess.run([sys.executable, OPEN, "--abox", AB, "--lineage", "L", "--prefix", "x"], capture_output=True, text=True)
expect("the opening tool run with no profile opens a lineage with the default, adopting the agent-accountability rule set", r.returncode == 0 and "openedWithProfile backlog:Profile_AgenticAdaptive" in r.stdout and "RS_AgentAccountability" in r.stdout)
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
