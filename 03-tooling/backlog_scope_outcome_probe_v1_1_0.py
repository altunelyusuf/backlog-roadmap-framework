#!/usr/bin/env python3
"""backlog_scope_outcome_probe v1.1.0 -- the scope outcome is derived from the objectives that name the scope they fill, and only from those (shapes v1.174.0, G131, G132).

One small planted register per case: a backlog that holds the scope, one story Done (so the completion rule derives the scope Done), and one or two objectives.
The rules are run (SHACL advanced mode, in place) and the derived scope outcome is read back.
  1 the objective names the scope it fills (fillsScope, scope first) and its target is reached:      Ach_Met
  2 the scope names the objective (scopeRealizesObjective, retired by G132) and its target is reached:  no outcome derived (the retired link is not read)
  3 scope first, deadline passed, observed short of the target:                                         Ach_Missed
  4 scope first, no observation yet (the honest third state):                                          Ach_Pending
  5 scope first, one objective met and one with no observation:                                        Ach_Pending (a met objective does not hide an open one)
  6 scope first, one objective met and one missed:                                                    Ach_Missed
  7 the objective names the scope AND the scope carries the retired link:                             Ach_Met, and only that
  8 no objective at all:                                                                              no outcome derived
  9 the scope is not complete (a story still open) though its objective is met:                        no outcome derived
Run with --shapes FILE to judge another version of the shapes (shapes v1.172.0 fail cases 1, 3, 4, 5 and 6; shapes v1.173.0 fail case 2).
Exit 0 when every expectation holds, 1 otherwise."""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(latest("02-shacl-safeguards/backlog_shacl_v*.ttl")); print(os.path.abspath(__file__)); sys.exit(0)
SHAPES = latest("02-shacl-safeguards/backlog_shacl_v*.ttl")
if "--shapes" in sys.argv:
    SHAPES = sys.argv[sys.argv.index("--shapes") + 1]
from rdflib import Graph, Namespace, URIRef
from pyshacl import validate
B = Namespace("http://example.org/backlog#")
shapes = Graph(); shapes.parse(SHAPES, format="turtle")

HEAD = ("@prefix backlog: <http://example.org/backlog#> .\n@prefix ex: <http://example.org/sop#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
        "ex:BL a backlog:Backlog ; backlog:hasScopeStatement ex:S .\nex:S a backlog:ScopeStatement .\n")
STORY = lambda state: 'ex:W a backlog:Story ; backlog:memberOfContainer ex:BL ; backlog:hasState backlog:%s .\n' % state
def objective(n, kind, observed=None, target=10.0, past=False):
    t = 'ex:%s a backlog:Objective ; backlog:hasTargetValue %s ; backlog:hasTargetDirection backlog:Dir_Increase ' % (n, target)
    if past:
        t += '; backlog:hasObjectiveDeadline "2020-01-01T00:00:00"^^xsd:dateTime '
    if kind in ("fills", "both"):
        t += '; backlog:fillsScope ex:S '
    t += '.\n'
    if kind in ("realizes", "both"):
        t += 'ex:S backlog:scopeRealizesObjective ex:%s .\n' % n
    if observed is not None:
        t += 'ex:Obs_%s a backlog:MetricObservation ; backlog:observationFor ex:%s ; backlog:hasObservedValue %s .\n' % (n, n, observed)
    return t

def outcomes(text):
    g = Graph(); g.parse(data=text, format="turtle")
    validate(g, shacl_graph=shapes, advanced=True, inplace=True, inference="none", abort_on_first=False)
    return sorted(str(o).split("#")[-1] for o in g.objects(URIRef("http://example.org/sop#S"), B.scopeOutcome))

bad = []
def expect(name, got, want):
    ok = got == want
    print(("PASS  " if ok else "FAIL  ") + "%s (%s)" % (name, ",".join(got) or "no outcome"))
    if not ok:
        bad.append(name)

expect("1 scope first, target reached", outcomes(HEAD + STORY("Done") + objective("O", "fills", observed=12.0)), ["Ach_Met"])
expect("2 retired link only: not read", outcomes(HEAD + STORY("Done") + objective("O", "realizes", observed=12.0)), [])
expect("3 scope first, deadline passed, short of target", outcomes(HEAD + STORY("Done") + objective("O", "fills", observed=3.0, past=True)), ["Ach_Missed"])
expect("4 scope first, no observation: too early to tell", outcomes(HEAD + STORY("Done") + objective("O", "fills")), ["Ach_Pending"])
expect("5 scope first, one met and one open: pending", outcomes(HEAD + STORY("Done") + objective("O", "fills", observed=12.0) + objective("P", "fills")), ["Ach_Pending"])
expect("6 scope first, one met and one missed: missed", outcomes(HEAD + STORY("Done") + objective("O", "fills", observed=12.0) + objective("M", "fills", observed=3.0, past=True)), ["Ach_Missed"])
expect("7 retired link beside the ruled one: met, once", outcomes(HEAD + STORY("Done") + objective("O", "both", observed=12.0)), ["Ach_Met"])
expect("8 no objective: nothing derived", outcomes(HEAD + STORY("Done")), [])
expect("9 scope not complete: nothing derived", outcomes(HEAD + STORY("InProgress") + objective("O", "fills", observed=12.0)), [])
print("VERDICT: %s" % ("PASS -- 9 expectations hold" if not bad else "FAIL -- " + "; ".join(bad)))
sys.exit(1 if bad else 0)
