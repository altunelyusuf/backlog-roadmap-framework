#!/usr/bin/env python3
"""v1.5.0 (G159): one active lineage by default. When the lineage or its register adopts RS_ConcurrentLineages (every lineage opened with a profile does), another active lineage must be connected to it or maintained by a different party, else the start is refused.
backlog_execution_ready v1.4.0 -- may work start on this lineage, and on this item?  (the positive question)

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
  - while no item of it has started, it records its work: RS_StatusHistoryRecorded and RS_FlowPointsRecorded are adopted by
    the lineage or by its register, or the lineage states recordingRuleSetsDeclinedReason   (G115; examined: the adopters)
ITEM (--item NAME), the same facts the after-the-fact shapes demand once work has happened, asked before it does:
  - the item belongs to this lineage, or a rebuilt active Backlog output admits it as pre-lineage
  - its state is Ready or InProgress (Ready is what grooming earns)
  - it carries an acceptance criterion (an ExecutionTask inherits it from the item it was planned from)
  - a Story, Epic or Initiative states its applicable design concerns, or that none applies
  - a Story has been taken in by a PlanningEvent

v1.4.0 (G155): a lineage that has not started work declares the opening profile it chose (openedWithProfile) or states profileDeclinedReason. The choice is explicit; the tool backlog_open_lineage writes it.
v1.3.0 (G148): the freeze is lifted for the start gate once the finding named by frozenBy is answered: a bypass by a LineageRestart
that answersBypass it, a thrash by the lineage's frozenRuling. lineageFrozen stays true in the append-only register; the gate reads
the answer, not the flag alone. another registrant's lineage printed "frozen" after the restart that answered its bypass.
v1.2.0 (G115): a lineage that has not started work either adopts the two recording rule sets (itself or through its register) or
states why not. It is the start gate, not the validator, that asks: the rule sets bind only what adopted them (G89), so a lineage
that never adopted them is not wrong afterwards, but it must not BEGIN work without having decided. A lineage with an item already
In Progress, Suspended or Done is not asked (it is not retroactively blocked); it can still adopt at a stated moment (G112).
v1.1.0: the decision is a function, evaluate(graph, lineage, item, emit), so the work guard asks it without re-parsing the
register per item. Output and exit codes are unchanged from v1.0.0.

Usage: backlog_execution_ready_v1_1_0.py REGISTER.ttl [MORE.ttl ...] --lineage NAME [--item NAME]
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


def evaluate(g, lineage, item=None, emit=print):
    """Return the list of missing facts (empty = READY). emit receives each printed line."""
    bad = []

    def check(ok, msg):
        emit(("  ok    " if ok else "  FAIL  ") + msg)
        if not ok:
            bad.append(msg)

    L = find(g, lineage)
    emit(f"lineage     : {lineage}")
    if L is None or (L, RDF.type, B.Lineage) not in g:
        check(False, "the lineage exists in the register (examined: 0 lineages)")
        return bad
    arch = g.value(L, B.lineageArchived)
    check(not (arch is not None and bool(arch.toPython())), "the lineage is not archived")
    fr = g.value(L, B.lineageFrozen)
    flagged = fr is not None and bool(fr.toPython())
    by = g.value(L, B.frozenBy)
    answered = g.value(L, B.frozenRuling) is not None or (
        by is not None and any(True for _ in g.subjects(B.answersBypass, by)))
    check(not (flagged and not answered), "the lineage is not frozen by an unanswered finding")
    one_rule = (L, B.adoptsRuleSet, B.RS_ConcurrentLineages) in g or any(
        (r, B.adoptsRuleSet, B.RS_ConcurrentLineages) in g for r in set(g.subjects(B.adoptsRuleSet, None)) if (r, RDF.type, B.Lineage) not in g)
    if one_rule:
        rank = {"LS_Scoped": 2, "LS_Goaled": 3, "LS_Objectived": 4, "LS_Backlogged": 5, "LS_InProgress": 6, "LS_Revived": 6}
        def running(x):
            return rank.get(str(g.value(x, B.hasLineageStatus)).rsplit("#", 1)[-1], 0) >= 2
        def near(x):
            n = set(g.objects(x, B.parentLineage)) | set(g.subjects(B.parentLineage, x))
            for i in g.subjects(B.belongsToLineage, x):
                for d in list(g.objects(i, B.dependsOn)) + list(g.subjects(B.dependsOn, i)):
                    n |= set(g.objects(d, B.belongsToLineage))
                for u in g.subjects(B.urgentItem, i):
                    n |= set(g.objects(u, B.interruptsLineage))
            for u in g.subjects(B.interruptsLineage, x):
                for i in g.objects(u, B.urgentItem):
                    n |= set(g.objects(i, B.belongsToLineage))
            return n
        def group(x):
            seen, todo = {x}, [x]
            while todo:
                for y in near(todo.pop()):
                    if y not in seen: seen.add(y); todo.append(y)
            return seen
        mine = g.value(L, B.maintainedBy); grp = group(L)
        clash = [o for o in set(g.subjects(RDF.type, B.Lineage)) if o != L and running(o) and o not in grp
                 and not (mine is not None and g.value(o, B.maintainedBy) is not None and g.value(o, B.maintainedBy) != mine)]
        check(not clash or not running(L), "no other lineage is active unless it is connected or maintained by a different party "
              f"(active beside it: {', '.join(sorted(str(o).rsplit('#', 1)[-1] for o in clash)) or 'none'}). One lineage runs and the other waits (G159)")
    outs = {st: [o for o in g.subjects(B.belongsToLineage, L) if (o, B.outputOfStage, B[st]) in g and active(g, o)] for st in STAGES}
    for st in STAGES:
        check(bool(outs[st]), f"{st} has an active output (examined: {len(outs[st])})")
    items = [s for t in ITEM_TYPES for s in g.subjects(RDF.type, B[t]) if (s, B.belongsToLineage, L) in g]
    admitted = {s for s in g.subjects(B.admittedByOutput, None) if any(o in outs["Stage_Backlog"] for o in g.objects(s, B.admittedByOutput))}
    n_items = len(set(items) | admitted)
    check(n_items > 0, f"the lineage holds at least one work item (examined: {n_items})")
    everyone = set(items) | admitted
    started = [s for s in everyone if g.value(s, B.hasState) in (B.InProgress, B.Suspended, B.Done)]
    if started:
        emit(f"  ok    recording rule sets: not asked, work has already started (examined: {len(started)} started item(s); G89 -- no retroactive block)")
    else:
        prof = g.value(L, B.openedWithProfile); pwhy = g.value(L, B.profileDeclinedReason)
        check(prof is not None or pwhy is not None,
              f"the lineage declares an opening profile or states profileDeclinedReason (profile: {str(prof).rsplit('#', 1)[-1] if prof is not None else 'none'}; "
              f"declined: {'yes' if pwhy is not None else 'no'}). Choose how the lineage works when it opens: run backlog_open_lineage, or say why not (G155)")
        why = g.value(L, B.recordingRuleSetsDeclinedReason)
        registers = [r for r in set(g.subjects(B.adoptsRuleSet, None)) if (r, RDF.type, B.Lineage) not in g]
        for rs in (B.RS_StatusHistoryRecorded, B.RS_FlowPointsRecorded):
            by = []
            if (L, B.adoptsRuleSet, rs) in g:
                by.append("the lineage")
            if any((r, B.adoptsRuleSet, rs) in g for r in registers):
                by.append("its register")
            check(bool(by) or why is not None,
                  f"{str(rs).rsplit('#', 1)[-1]} is adopted by the lineage or its register, or the lineage states recordingRuleSetsDeclinedReason "
                  f"(adopted by: {', '.join(by) or 'nobody'}; declined: {'yes' if why is not None else 'no'}). Work that begins unrecorded cannot "
                  f"be dated afterwards: adopt the rule set before the first item starts, or say why not (G115)")
    if item is not None:
        name = item
        X = find(g, name)
        emit(f"item        : {name}")
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
    return bad


def main(argv):
    opts = {}
    files = []
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
    print(f"register    : {', '.join(f.rsplit('/', 1)[-1] for f in files)}")
    bad = evaluate(g, opts["--lineage"], opts.get("--item"))
    print("VERDICT     : " + ("READY" if not bad else f"NOT READY -- {len(bad)} fact(s) missing; work may not start"))
    return 0 if not bad else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
