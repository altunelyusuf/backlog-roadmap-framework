#!/usr/bin/env python3
"""backlog_reachability_gate_v1_0_0.py — a class the vocabulary cannot point at.

Package sat unused for 91 releases because no property had it as a range. It
could be declared and never referred to, and the cost was a wrong conclusion
drawn in good faith: packages were believed impossible before delivery when the
concept had existed all along.

Two signals, and only the second is a failure:

  no RANGE property        45 classes. Reachable by rdf:type alone, so usable —
                           AdoptionProfile is one. Reported, not failed.
  no RANGE and NO INSTANCE 23 classes. Declared, unreferenceable, unused. This
                           is the Package trap and it fails.

Run against the TBox plus the register: instances live in the register, so a
TBox-only run would condemn every class the register happens to use.

Exit 0 when no class is both unreferenceable and unused.
"""
import sys, glob
from rdflib import Graph, RDF, RDFS, OWL, URIRef
B="http://example.org/backlog#"
g=Graph()
args=[a for a in sys.argv[1:] if not a.startswith("-")]
if not args:
    # Found by self-application, which is the whole point of running a checker
    # against the package that ships it. With no arguments this parsed NOTHING
    # and reported PASS: zero classes, zero unreachable, green.
    #
    # A checker that passes on an empty graph is worse than no checker. The
    # release gate happens to pass paths, so this never fired here — but the
    # script ships, and an adopter running it bare would be told their
    # vocabulary is clean when it was never read.
    raise SystemExit(
        "FATAL: no input given. This checker reports on the classes it is "
        "handed, so with no input it would report zero unreachable classes "
        "and PASS. Refusing to return a verdict about a graph it never read.\n"
        "usage: backlog_reachability_gate_v1_0_0.py TBOX.ttl [REGISTER.ttl ...]")
for f in args: g.parse(f,format='turtle')
bad=[]; norange=[]
for cl in g.subjects(RDF.type,OWL.Class):
    if not str(cl).startswith(B): continue
    if list(g.objects(cl,OWL.oneOf)): continue
    if list(g.subjects(RDFS.subClassOf,cl)): continue
    if list(g.subjects(RDFS.range,cl)): continue
    n=str(cl).split("#")[-1]
    norange.append(n)
    if not list(g.subjects(RDF.type,cl)): bad.append(n)
print("no range property     : %d (reachable by rdf:type; reported only)"%len(norange))
print("...and no instance    : %d"%len(bad))
for n in sorted(bad): print("   %s"%n)
print("VERDICT     : %s"%("PASS - every class is either referenceable or in use"
                          if not bad else
                          "FAIL - a class nothing can reference and nothing uses is the Package trap"))
sys.exit(1 if bad else 0)
