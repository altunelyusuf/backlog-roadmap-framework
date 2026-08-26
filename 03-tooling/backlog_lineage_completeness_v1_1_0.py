#!/usr/bin/env python3
"""backlog_lineage_completeness v1.1.0 — what your register does NOT contain.

Every other check in this package asks whether what is present is correct.
This one asks what is missing, because that is the question SHACL structurally
cannot answer for itself.

THE DEFECT THIS EXISTS FOR

sh:targetClass cannot see absence. A shape guarding ScopeStatement has no
target in a register containing zero ScopeStatements, so the constraints
written to govern a layer are exactly the constraints that go silent when the
layer is omitted entirely. Measured on this suite at the time of writing: one
shape guards Mission, one guards ScopeStatement, two guard Objective, two guard
Goal — all unreachable by omission.

The consequence, observed rather than theorised: this framework's own
development register declared L2 conformance, reported zero violations, and
contained no scope, no exclusions, no Definition of Done, no decomposition and
no work below epic level. It was called a lineage. It was four epics and a
sentence each. The owner reported the same pattern in parallel sessions using
the same approach.

LineageCompletenessShape now refuses the worst of it at L2 and above. This tool
covers what a constraint should not: it reports at ANY level, it reports layers
that are thin rather than absent, and it names what would be gained by filling
each gap — so a register can be improved before it is failed.

Exit 0 always unless --strict is given: this is a report, not a gate. The gate
is the shape.

A level mark here means LineageCompletenessShape actually rejects that omission
at that level — nothing else. v1.0.0 marked six layers L2/L3 that the shape does
not reach, which asserted a consequence the suite would not deliver; a report
that overstates its own enforcement is the same defect as prose overstating a
measurement. Corrected at v1.0.2 to the three the shape enforces, with the
conditional case (PlanningEvent, required only where execution tasks exist)
stated in the consequence text rather than encoded as an unconditional mark.

Usage:
  backlog_lineage_completeness_v1_0_0.py REGISTER.ttl [--strict]
"""

import sys
import os
import glob
from rdflib import Graph, Namespace, RDF, URIRef

BL = Namespace("http://example.org/backlog#")
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (label, class, why it matters when missing, the tier where its absence bites)
def _load_layers(tbox_path, reg_path):
    """Read the lineage layers from the ontology.

    EXPORTED at v1.111.0 and READ here. The python literal this replaces
    decided what counts as a layer, in what order, and what its absence costs
    — three judgements a script held and no query could reach.

    Fails LOUDLY when the ontology carries no layers. A fallback to a literal
    would leave this script working and the migration unfinished, and nothing
    would report it: a fallback is a python decision wearing an ontology's
    clothes, which is the thing this release exists to remove.
    """
    from rdflib import Graph, Namespace, RDF
    B = Namespace("http://example.org/backlog#")
    g = Graph()
    g.parse(tbox_path, format="turtle")
    g.parse(reg_path, format="turtle")
    rows = []
    for layer in g.subjects(RDF.type, B.LineageLayer):
        cls = g.value(layer, B.layerClass)
        ordn = g.value(layer, B.layerOrdinal)
        cost = g.value(layer, B.layerAbsenceCost)
        label = g.value(layer, B.layerLabel)
        tier = g.value(layer, B.layerTier)
        if cls is None or ordn is None:
            continue
        rows.append((int(ordn), str(label or cls).split("#")[-1],
                     str(cls).split("#")[-1], str(cost or ""), str(tier or "L2")))
    if not rows:
        raise SystemExit(
            "FATAL: the ontology declares no LineageLayer. The layer table was "
            "exported at v1.111.0 and this script reads it rather than holding "
            "one. Refusing to fall back to a literal: a silent fallback would "
            "leave the migration unfinished and nothing would say so."
        )
    rows.sort()
    return [(label, cls, cost, tier) for _, label, cls, cost, tier in rows]

def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    strict = "--strict" in sys.argv
    reg = [a for a in sys.argv[1:] if not a.startswith("--")][0]

    g = Graph()
    for f in sorted(glob.glob(os.path.join(PKG, "01-ontologies", "backlog_tbox_v*.ttl")))[-1:]:
        g.parse(f, format="turtle")
    g.parse(reg, format="turtle")

    lvl = None
    for _, o in g.subject_objects(BL.hasConformanceLevel):
        lvl = str(o).rsplit("#", 1)[-1]

    print("register    : %s" % os.path.basename(reg))
    print("level       : %s" % (lvl or "none declared"))
    print()

    present, absent = [], []
    _tbox = sorted(glob.glob(os.path.join(PKG, "01-ontologies", "backlog_tbox_v*.ttl")))[-1]
    LAYERS = _load_layers(_tbox, reg)
    for label, cls, why, tier in LAYERS:
        n = len(set(g.subjects(RDF.type, URIRef(str(BL) + cls))))
        if cls == "Evidence":
            n = sum(len(set(g.subjects(RDF.type, URIRef(str(BL) + c))))
                    for c in ("TestEvidence", "ReleaseEvidence", "ArtifactEvidence", "ReviewEvidence"))
        (present if n else absent).append((label, n, why, tier))

    print("PRESENT (%d layer(s))" % len(present))
    for label, n, _, _ in present:
        print("   %-24s %d" % (label, n))

    print("\nABSENT (%d layer(s)) — what each omission costs you" % len(absent))
    for label, _, why, tier in absent:
        mark = "  <-- fails at %s" % tier if tier != "-" else ""
        print("   %-24s %s%s" % (label, why, mark))
    if not absent:
        print("   none")

    depth = len(set(g.subject_objects(BL.decomposesInto)))
    print("\ndecomposition: %d parent-child edge(s)" % depth)
    if depth == 0 and any(l == "Epic/Feature" for l, _, _, _ in present):
        print("   Epics that decompose into nothing are estimates with no plan behind them.")

    blocking = [l for l, _, _, t in absent if t != "-"]
    print("\nVERDICT     : %s" % ("complete for the declared level"
                                  if not blocking else
                                  "%d layer(s) absent that a higher level requires: %s"
                                  % (len(blocking), ", ".join(blocking))))
    return 1 if (strict and blocking) else 0


if __name__ == "__main__":
    sys.exit(main())
