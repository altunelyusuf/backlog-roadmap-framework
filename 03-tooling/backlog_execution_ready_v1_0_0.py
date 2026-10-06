#!/usr/bin/env python3
"""backlog_execution_ready v1.0.0 -- may work start on this lineage, and on this item?  (the positive question)

WHY THIS EXISTS. Every gate this package ships is negative: it looks for what went wrong among the items that exist.
A lineage whose work is executed outside the register has no items, so every negative gate passes over the empty set.
the adopting project's Lineage_2 (Objective stage closed 2026-09-28, Backlog stage never built) shipped nine releases from a work
ledger while the order check read ORDERED and the pipeline verifier PASS (handover, 2026-10-06). A green verdict over an
empty set is not evidence. This tool asks the question the other way round: it passes only when the facts that must
EXIST before work starts do exist, and it prints what it examined. Call it before assigning any worker to a lineage.

LINEAGE (always):
  - the lineage exists and is not archived                                  (examined: 1)
  - it is not frozen by an unanswered bypass or thrash
  - every stage output Mission..Backlog exists and none is retracted        (examined: the outputs)
  - it holds at least one work item                                         (examined: the item count, printed)
ITEM (--item NAME), the same facts the after-the-fact shapes demand once work has happened, asked before it does:
  - the item belongs to this lineage, or a rebuilt active Backlog output admits it as pre-lineage
  - its state is Ready or InProgress (Ready is what grooming earns)
  - it carries an acceptance criterion (an ExecutionTask inherits it from the item it was planned from)
  - a Story, Epic or Initiative states its applicable design concerns, or that none applies
  - a Story has been taken in by a PlanningEvent

Usage: backlog_execution_ready_v1_0_0.py REGISTER.ttl [MORE.ttl ...] --lineage NAME [--item NAME]
Exit 0 READY, 2 NOT READY (every failed fact is printed), 1 error. Reads only; asserts nothing; never edits.
It does not replace the validator or the order check: it is the precondition they cannot be.
"""
import sys
from rdflib import Graph, Namespace, RDF, URIRef, Literal

B = Namespace("http://example.org/backlog#")
STAGES = ["Stage_Mission", "Stage_Scope", "Stage_Goal", "Stage_Objective", "Stage_Backlog"]
ITEM_TYPES = ["Story", "Epic", "ExecutionTask", "Initiative", "Spike", "Task", "Defect", "Feature", "Enabler"]


def find(g, name):
    hits = {s for s in set(g.subjects()) if isinstance(s, URIRef) and str(s).replace("/", "#").rsplit("#", 1)[-1] == name}
    return sorted(hits)[0] if hits else None


def active(g, o):
    v = g.value(o, B.outputRetracted)
    return not (v is not None and bool(v.toPython()))


def main(argv):
    opts = {}
    files = []
    it = iter(range(len(argv)))
    i = 0
    while i < len(argv):
        if argv[i] in ("--lineage", "--item"):
            opts[argv[i]] = argv[i + 1]; i += 2
        else:
            files.append(argv[i]); i += 1
    if not files or "--lineage" not in opts:
        print(__doc__); return 1
    g = Graph()
    for f in files:
        g.parse(f, format="turtle")
    bad = []

    def check(ok, msg):
        print(("  ok    " if ok else "  FAIL  ") + msg)
        if not ok:
            bad.append(msg)

    L = find(g, opts["--lineage"])
    print(f"register    : {', '.join(f.rsplit('/', 1)[-1] for f in files)}")
    print(f"lineage     : {opts['--lineage']}")
    if L is None or (L, RDF.type, B.Lineage) not in g:
        check(False, "the lineage exists in the register (examined: 0 lineages)"); print("VERDICT     : NOT READY"); return 2
    arch = g.value(L, B.lineageArchived)
    check(not (arch is not None and bool(arch.toPython())), "the lineage is not archived")
    fr = g.value(L, B.lineageFrozen)
    check(not (fr is not None and bool(fr.toPython())), "the lineage is not frozen by an unanswered finding")
    outs = {st: [o for o in g.subjects(B.belongsToLineage, L) if (o, B.outputOfStage, B[st]) in g and active(g, o)] for st in STAGES}
    for st in STAGES:
        check(bool(outs[st]), f"{st} has an active output (examined: {len(outs[st])})")
    items = [s for t in ITEM_TYPES for s in g.subjects(RDF.type, B[t]) if (s, B.belongsToLineage, L) in g]
    admitted = {s for s in g.subjects(B.admittedByOutput, None) if any(o in outs["Stage_Backlog"] for o in g.objects(s, B.admittedByOutput))}
    n_items = len(set(items) | admitted)
    check(n_items > 0, f"the lineage holds at least one work item (examined: {n_items})")
    if "--item" in opts:
        name = opts["--item"]
        X = find(g, name)
        print(f"item        : {name}")
        if X is None:
            check(False, "the item exists in the register")
        else:
            types = {str(t).rsplit("#", 1)[-1] for t in g.objects(X, RDF.type)}
            check(bool(types & set(ITEM_TYPES)), f"it is a work item (types: {', '.join(sorted(types)) or 'none'})")
            check((X, B.belongsToLineage, L) in g or X in admitted, "it belongs to this lineage or is admitted into it")
            st = g.value(X, B.hasState)
            check(st in (B.Ready, B.InProgress), f"its state is Ready or InProgress (is: {str(st).rsplit('#', 1)[-1] if st else 'none'})")
            if "ExecutionTask" not in types:
                check(g.value(X, B.hasAcceptanceCriterion) is not None, "it carries an acceptance criterion")
            if types & {"Story", "Epic", "Initiative"}:
                check(g.value(X, B.hasApplicableConcern) is not None or g.value(X, B.hasNoApplicableConcern) is not None,
                      "it states its applicable design concerns, or that none applies")
            if "Story" in types:
                check(any((e, RDF.type, B.PlanningEvent) in g for e in g.subjects(B.plansItem, X)), "a PlanningEvent has taken it in")
    print("VERDICT     : " + ("READY" if not bad else f"NOT READY -- {len(bad)} fact(s) missing; work may not start"))
    return 0 if not bad else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
