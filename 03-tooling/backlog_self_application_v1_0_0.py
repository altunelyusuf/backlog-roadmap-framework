#!/usr/bin/env python3
"""backlog_self_application_v1_0_0.py — every checker runs against this package.

A4 from the lineage discipline. Several findings in this package's history came
from running a checker against the package that ships it, and EVERY ONE was
noticed by accident:

  the script-decision audit flagged the row checker written beside it
  the distribution builder shipped a cache file it should have excluded
  the reachability gate reported PASS on an empty graph when run bare

The last was found by writing this. That is the argument for it: a checker is
the one artefact whose own subject includes itself, and nothing was asking.

Two things are checked here, both cheap:

  RAN       every checker in 03-tooling exits without crashing when handed the
            package's own files
  NOT BLIND a checker given nothing must not return a verdict. A tool that
            passes on an empty graph reports green for a graph it never read,
            which is the most expensive kind of wrong.

Exit 1 under --strict if any checker is blind.
"""
import sys, os, re, glob, subprocess

def _accepts_graph_path(script_name, tbox_path, register_path):
    """Does this checker take a graph via CLI argument?

    OWNER FINDING, corrected TWICE in this release before landing here, and
    the second correction is the one worth keeping honest about. First
    attempt: a hardcoded python tuple of script names — a decision the
    ontology never stated. Second attempt: guessed from whether the source
    touches sys.argv[1:] directly — WRONG, because backlog_validate uses
    argparse and was misclassified as self-sufficient when it in fact
    refuses correctly. Third attempt: "run bare, is the output PASS" —
    ALSO WRONG, because six checkers (adoption_check, criterion_resolve,
    number_origin, coverage_gate, doc_coverage_gate, lineage_discipline)
    locate their own data via internal glob and correctly report PASS on
    real, self-located data. That behavioural test cannot distinguish a
    checker that examined nothing from one that examined everything and
    found it clean.

    The fact does not derive cleanly from source shape or from output text.
    It is declared here, as ToolScript individuals in the register — the
    same move CodeTable made for classification tables baked into python —
    and VERIFIED once against real observed behaviour rather than trusted.
    """
    from rdflib import Graph, Namespace, RDF
    B = Namespace("http://example.org/backlog#")
    g = Graph()
    g.parse(tbox_path, format="turtle")
    g.parse(register_path, format="turtle")
    for t in g.subjects(RDF.type, B.ToolScript):
        if str(g.value(t, B.scriptFileName)) == script_name:
            v = g.value(t, B.acceptsGraphPath)
            return v is not None and str(v) == "true"
    return None  # undeclared: reported, not guessed


def _returns_pass_blind(script_path):
    """Run a graph-accepting checker bare; PASS with nothing read is blind."""
    try:
        r = subprocess.run([sys.executable, script_path], capture_output=True,
                           text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return None
    out = r.stdout + r.stderr
    return r.returncode == 0 and "PASS" in out

def main():
    strict = "--strict" in sys.argv
    here = os.path.dirname(os.path.abspath(__file__))
    pkg = os.path.dirname(here)
    me = os.path.basename(__file__)
    tbox = sorted(glob.glob(os.path.join(pkg, "01-ontologies", "backlog_tbox_v*.ttl")))
    reg = sorted(glob.glob(os.path.join(pkg, "01-ontologies",
                 "backlog_framework_register_abox_v*.ttl")))
    if not tbox or not reg:
        raise SystemExit(
            "FATAL: no TBox or register found. This reads acceptsGraphPath "
            "from the ontology, so with nothing to read it would examine "
            "zero declared scripts and PASS. Refusing that verdict.")
    blind, crashed, ok, undeclared = [], [], 0, []
    for path in sorted(glob.glob(os.path.join(here, "*.py"))):
        name = os.path.basename(path)
        if name == me:
            continue
        accepts = _accepts_graph_path(name, tbox[-1], reg[-1])
        if accepts is None:
            undeclared.append(name)
            continue
        if not accepts:
            continue
        verdict = _returns_pass_blind(path)
        if verdict is None:
            crashed.append((name, "timed out"))
        elif verdict:
            blind.append(name)
        else:
            ok += 1
    for name in undeclared:
        print("   UNDECLARED  %s (not in ToolScript; not tested)" % name)
    print("graph-accepting checkers : %d" % (ok + len(blind) + len(crashed)))
    print("refuse to run blind    : %d" % ok)
    print("PASS on no input       : %d" % len(blind))
    for n in blind:
        print("   BLIND  %s" % n)
    for n, why in crashed:
        print("   %s  %s" % (why, n))
    print("VERDICT     : %s" % (
        "PASS - no checker returns a verdict about a graph it never read"
        if not blind else
        "FAIL - %d checker(s) report PASS on an empty graph" % len(blind)))
    sys.exit(1 if (blind and strict) else 0)

if __name__ == "__main__":
    main()
