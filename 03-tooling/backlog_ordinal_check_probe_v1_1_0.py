#!/usr/bin/env python3
"""backlog_ordinal_check_probe v1.1.0 -- the ordinal check is proven end to end, as a program, on throwaway live and archive files (G99 ordinal rule).

Seven cases, each run through the real tool with --live and --archive pointing at small files:
  1 distinct ordinals across live and archive            -> exit 0
  2 an archived lineage and a live one on one number      -> exit 2, the hand-over guidance is printed
  3 the same pair, declared                               -> exit 0
  4 a third lineage on a declared number                  -> exit 2
  5 a declaration naming a lineage on another number      -> exit 2
  6 `next` gives highest carried + 1, counting the archive-> that number
  7 two archived lineages on one number (both in the archive) -> exit 2
Exit 0 all hold; 2 a case failed.
"""
import glob, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = sorted(glob.glob(os.path.join(HERE, "backlog_ordinal_check_v*.py")), key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]])[-1]
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/probe#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"


def lin(name, n):
    return "x:%s a backlog:Lineage ; rdfs:label \"%s\" ; backlog:lineageOrdinal %d .\n" % (name, name, n)


def decl(name, n, *who):
    return "x:%s a backlog:OrdinalSharingDeclaration ; backlog:declaredOrdinal %d ; backlog:sharedByLineage %s .\n" % (name, n, " , ".join("x:" + w for w in who))


def run(live, arch, *extra):
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "live.ttl"), os.path.join(d, "arch.ttl")
        open(a, "w").write(HEAD + live); open(b, "w").write(HEAD + arch)
        r = subprocess.run([sys.executable, "-B", TOOL, "--live", a, "--archive", b] + list(extra), capture_output=True, text=True)
        return r.returncode, r.stdout


if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(TOOL)
    sys.exit(0)


bad = []
def need(ok, what):
    if not ok:
        bad.append(what)

c, o = run(lin("L1", 1) + lin("L3", 3), lin("L2", 2)); need(c == 0, "1 distinct ordinals were refused")
c, o = run(lin("L9", 2), lin("L2", 2)); need(c == 2 and "WHAT TO DO" in o and "owner" in o, "2 a live/archive collision was not refused with guidance")
c, o = run(lin("L9", 2) + decl("D", 2, "L9", "L2"), lin("L2", 2)); need(c == 0, "3 a declared pair was refused")
c, o = run(lin("L9", 2) + lin("L8", 2) + decl("D", 2, "L9", "L2"), lin("L2", 2)); need(c == 2, "4 a third lineage on a declared number passed")
c, o = run(lin("L9", 3) + lin("L2b", 2) + decl("D", 2, "L9", "L2b"), lin("L1", 1)); need(c == 2, "5 a wrong declaration passed")
c, o = run(lin("L1", 1), lin("L7", 7)); need(c == 0, "6a clean files refused")
c, o = run(lin("L1", 1), lin("L7", 7), "next"); need(o.strip() == "8", "6 next did not count the archive (got %r)" % o.strip())
c, o = run(lin("L1", 1), lin("L2", 2) + lin("L2b", 2)); need(c == 2, "7 two archived lineages on one number passed")
for b in bad:
    print("FAILED: " + b)
print("VERDICT: %s" % ("all 7 cases hold" if not bad else "%d case(s) failed" % len(bad)))
sys.exit(0 if not bad else 2)
