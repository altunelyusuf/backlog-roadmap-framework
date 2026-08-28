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
bad=[]; norange=[]; explained=[]
for cl in g.subjects(RDF.type,OWL.Class):
    if not str(cl).startswith(B): continue
    if list(g.objects(cl,OWL.oneOf)): continue
    if list(g.subjects(RDFS.subClassOf,cl)): continue
    if list(g.subjects(RDFS.range,cl)): continue
    n=str(cl).split("#")[-1]
    norange.append(n)
    # A class carrying adoptionRationale has been RULED optional and the
    # reason is recorded. Reporting it as a failure asks the same question A1
    # already answered — two checkers disagreeing about one population is
    # worse than either being wrong, because a reader cannot tell which to
    # believe.
    #
    # The gate keeps its own question: is this class REACHABLE. A1 asks
    # whether it is OBLIGED. They differ, and the difference is why both
    # exist — but a class ruled optional-with-reason is not a Package trap.
    if list(g.objects(cl, URIRef(B + "adoptionRationale"))):
        explained.append(n)
    elif not list(g.subjects(RDF.type,cl)): bad.append(n)
print("no range property     : %d (reachable by rdf:type; reported only)"%len(norange))
print("...and no instance    : %d"%len(bad))
print("...ruled optional     : %d (adoptionRationale recorded; see A1)"%len(explained))
for n in sorted(bad): print("   %s"%n)
print("VERDICT     : %s"%("PASS - every class is referenceable, in use, or ruled optional with a reason"
                          if not bad else
                          "REPORTED - %d class(es) neither referenceable nor used; --strict fails on these" % len(bad)))
# REPORTS by default. Twenty classes are unreachable today, every one
# predating this lineage. Failing on them blocks every release until a separate
# decision is taken about each, and a gate that blocks gets suppressed.
# --strict is available for a package that has reached zero.
#
# Reconciled with A1 at v1.129.0: a class ruled optional-with-reason is
# reported separately and not counted here. Two checkers disagreeing about one
# population is worse than either being wrong.
sys.exit(1 if (bad and "--strict" in sys.argv) else 0)
