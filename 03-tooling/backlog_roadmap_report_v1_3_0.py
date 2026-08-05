#!/usr/bin/env python3
"""backlog_roadmap_report v1.3.0 — the roadmap, computed.

A roadmap is this script's output, never a maintained document. The moment a
computed value is copied into prose it starts decaying, and a report that is
recalled rather than re-run is a memory of a decision, not a decision. Every
run is therefore a fresh computation stamped with its own timestamp, and the
recommendations it emits point back at that run.

Sections produced (all eight are mandatory; a missing one fails the SHACL
suite, not just this script):

  1. NEXT under the throughput model
  2. NEXT under the launch-scoped model      <- both printed, always
  3. Full ranked backlog (COMPUTED — see below)
  4. Flagged items (not-yet-scoreable, with reasons)
  5. Silent-gap check                        <- must read zero
  6. Launch readiness by package
  7. Package-level multi-factor ranking      <- excludes non-capabilities
  8. Orphan and package-coverage check
  9. Lifecycle and workflow                  <- states, permitted moves, unexplained states

R3 arbitration: while any launch-gate container is still open, the scoped
answer ranks only items inside the active gate (lowest launch priority) plus
cross-cutting prerequisites — items outside it that something inside depends
on. Once every gate has cleared, the scope collapses to the whole register and
the two answers coincide by construction. The two are never reconciled by
arithmetic; a disagreement is displayed so a human resolves it knowingly.

Usage:
  backlog_roadmap_report_v1_3_0.py REGISTER.ttl [--method IRI] [--emit report.ttl]
"""

import argparse
import datetime
import glob
import os
import re
import sys

import rdflib
from rdflib import Graph, Literal, URIRef, RDF, XSD

BL = rdflib.Namespace("http://example.org/backlog#")
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
def _semver(path):
    m = re.search(r"_v(\d+)_(\d+)_(\d+)\.[a-z]+$", os.path.basename(path))
    return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)


def latest(subdir, stem, ext="ttl"):
    """Resolve a pointer by PATTERN, not by pinned filename: the highest-versioned
    stem_v*.ext in subdir. Version bumps of an ontology then never require editing
    the tooling that reads it — the same version-independent pointer rule the OE
    Operating Discipline applies to its own artifact references."""
    hits = glob.glob(os.path.join(PKG, subdir, "%s_v*.%s" % (stem, ext)))
    if not hits:
        raise SystemExit("no artifact matching %s/%s_v*.%s" % (subdir, stem, ext))
    return sorted(hits, key=_semver)[-1]


TBOX = latest("01-ontologies", "backlog_tbox")
ABOX = latest("01-ontologies", "backlog_abox")

CONTAINER_TYPES = ["WorkItemContainer", "Backlog", "Package", "Increment", "Iteration", "ImplementationProject"]

SECTIONS = ["Section_NextThroughput", "Section_NextLaunchScoped", "Section_RankedBacklog",
            "Section_FlaggedItems", "Section_SilentGapCheck", "Section_LaunchReadiness",
            "Section_PackageRanking", "Section_OrphanCoverageCheck", "Section_LifecycleWorkflow"]


def load(paths):
    g = Graph()
    for p in paths:
        g.parse(p, format="turtle")
    for t in list(g.triples((None, rdflib.OWL.imports, None))):
        g.remove(t)
    return g


def is_container(g, node):
    """A container is anything typed as one of the container classes; checking the
    root class alone misses Package/Backlog/Increment/Iteration instances, which is
    how a container would otherwise be counted as an unscored work item."""
    return any((node, RDF.type, BL[c]) in g for c in CONTAINER_TYPES)


def ident(g, node):
    return str(g.value(node, BL.hasIdentifier) or str(node).rsplit("#", 1)[-1])


def startable(g, item):
    for dep in g.objects(item, BL.dependsOn):
        if g.value(dep, BL.hasState) != BL.Done:
            return False
    return True


def scored(g, item, method):
    for sc in g.objects(item, BL.hasPriorityScore):
        if method is None or g.value(sc, BL.scoredByMethod) == method:
            v = g.value(sc, BL.hasScoreValue)
            if v is not None:
                return float(v)
    return None


def ranked(g, method, candidates=None):
    rows = []
    for item in set(g.subjects(BL.hasState, None)):
        if is_container(g, item):
            continue
        if candidates is not None and item not in candidates:
            continue
        v = scored(g, item, method)
        if v is None:
            continue
        rows.append((v, item, g.value(item, BL.hasState), startable(g, item)))
    rows.sort(key=lambda r: -r[0])
    return rows


def active_gates(g):
    """EVERY launch gate tied at the lowest open priority; empty when all cleared.

    Ties are legitimate and deliberately unconstrained: hasRoadmapRank must be
    unique per roadmap because a rank that does not order is not a rank, but
    launch priority orders gates that must clear before launch, and co-equal
    mandatory preconditions are a real situation. Forcing an owner to invent a
    sequence that does not exist would be the same fabrication the framework
    refuses elsewhere.

    The earlier single-gate form sorted (priority, container) tuples, so a tie fell
    through to comparing container URIs as strings — the alphabetically first gate
    won, silently, and the launch-scoped answer under-covered the real
    launch-blocking set. Reported by an adopting project whose register carries six
    co-equal gates at priority 0.
    """
    open_gates = []
    for c in set(g.subjects(BL.isLaunchGate, Literal(True))):
        members = list(g.subjects(BL.memberOfContainer, c))
        if not members:
            continue
        if all(g.value(m, BL.hasState) in (BL.Done, BL.Cancelled) for m in members):
            continue
        lp = g.value(c, BL.hasLaunchPriority)
        open_gates.append((int(lp) if lp is not None else 10 ** 6, c))
    if not open_gates:
        return []
    lowest = min(p for p, _ in open_gates)
    return [c for p, c in sorted(open_gates, key=lambda x: str(x[1])) if p == lowest]


def scoped_candidates(g, gates):
    """Union of members across every tied gate, plus cross-cutting prerequisites."""
    inside = set()
    for gate in gates:
        inside |= set(g.subjects(BL.memberOfContainer, gate))
    prereq = set()
    for m in inside:
        for d in g.objects(m, BL.dependsOn):
            if d not in inside:
                prereq.add(d)
    return inside | prereq, prereq


def main():
    ap = argparse.ArgumentParser(description="Compute the roadmap from the register.")
    ap.add_argument("register")
    ap.add_argument("--method", default="http://example.org/backlog#Method_WSJF")
    ap.add_argument("--emit", default=None, help="write the RoadmapReport individual to this Turtle file")
    args = ap.parse_args()

    g = load([TBOX, ABOX, args.register])
    method = URIRef(args.method) if args.method else None
    now = datetime.datetime.now().replace(microsecond=0)

    print("roadmap report  : computed %s" % now.isoformat())
    print("register        : %s" % os.path.basename(args.register))
    print("method          : %s" % (args.method or "any"))
    print("tooling         : rdflib %s, backlog_roadmap_report v1.3.0" % rdflib.__version__)

    gates = active_gates(g)
    all_rows = ranked(g, method)
    next_throughput = next((r for r in all_rows if r[2] == BL.Ready and r[3]), None)

    if gates:
        cands, prereq = scoped_candidates(g, gates)
        scoped_rows = ranked(g, method, cands)
        next_scoped = next((r for r in scoped_rows if r[2] == BL.Ready and r[3]), None)
        names = ", ".join(ident(g, x) for x in gates)
        if len(gates) == 1:
            scope_note = ("scoped to open launch gate %s (+%d cross-cutting prerequisite(s))"
                          % (names, len(prereq)))
        else:
            scope_note = ("scoped to %d co-equal open launch gates at the same priority — %s "
                          "(+%d cross-cutting prerequisite(s)); all are unioned, none is chosen"
                          % (len(gates), names, len(prereq)))
    else:
        next_scoped = next_throughput
        scope_note = "no launch gate open — scope collapsed to the whole register (R3)"

    print("\n== 1. NEXT (throughput model) ==")
    print("  %s" % (("%s  score %.2f" % (ident(g, next_throughput[1]), next_throughput[0]))
                    if next_throughput else "nothing startable and scored"))

    print("\n== 2. NEXT (launch-scoped model) ==")
    print("  %s" % scope_note)
    print("  %s" % (("%s  score %.2f" % (ident(g, next_scoped[1]), next_scoped[0]))
                    if next_scoped else "nothing startable and scored inside the active gate"))
    if next_throughput and next_scoped and next_throughput[1] != next_scoped[1]:
        print("  DISAGREEMENT: the two models point at different work. Displayed, not resolved —")
        print("  the launch question is an owner decision and is not computed from the score.")
        # A recorded standing decision is printed BESIDE the disagreement, never
        # instead of it. The fork stays visible; what changes is that the owner no
        # longer re-argues it every run.
        for b in g.subjects(RDF.type, BL.Backlog):
            resolution = g.value(b, BL.hasRankingForkResolution)
            if resolution is None:
                continue
            pick = next_scoped if resolution == BL.LaunchScopedRanking else next_throughput
            print("  RESOLVED PER RECORDED OWNER DECISION (%s): pick up %s"
                  % (str(resolution).rsplit("#", 1)[-1], ident(g, pick[1])))
            why = g.value(b, BL.hasDecisionRationale)
            if why:
                print("    because: %s" % str(why)[:100])

    # A section ordered by score is a COMPUTED view, not an assertion. Every
    # ordering this report prints is derived at run time from hasScoreValue; none
    # of it is backlog:hasRoadmapRank, which is an owner-declared fact. The
    # distinction is labelled because it has already been lost once: a downstream
    # reader took a rank column out of a handover document, assumed it was
    # asserted RDF, and drew a conclusion about a register that did not contain
    # the property at all. A report that does not say which of its numbers are
    # facts invites exactly that.
    print("\n== 3. Full ranked backlog — COMPUTED ordering by score ==")
    print("     Position here is derived from hasScoreValue at run time. It is NOT")
    print("     backlog:hasRoadmapRank; nothing in this section is an assertion in the")
    print("     register. Ties in this ordering are ties in the SCORE, and carry none of")
    print("     the uniqueness obligation a declared roadmap rank does.")
    declared = sorted(set(g.subjects(BL.hasRoadmapRank, None)))
    print("     declared roadmap ranks in this register: %d" % len(declared))
    for v, item, state, ok in all_rows:
        print("  %-10s %-12s score %6.2f  %s" % (ident(g, item), str(state).rsplit("#", 1)[-1],
                                                 v, "startable" if ok else "blocked"))

    print("\n== 4. Flagged items (not yet scoreable) ==")
    flagged = [i for i in g.subjects(BL.notYetScoreable, Literal(True))]
    if not flagged:
        print("  none")
    for i in flagged:
        print("  %-10s %s" % (ident(g, i), g.value(i, BL.hasScoreabilityReason) or "(no reason recorded)"))

    print("\n== 5. Silent-gap check ==")
    silent = []
    for item in set(g.subjects(BL.hasState, None)):
        if is_container(g, item):
            continue
        if g.value(item, BL.hasState) not in (BL.Proposed, BL.Ready):
            continue
        if list(g.objects(item, BL.hasPriorityScore)):
            continue
        if g.value(item, BL.notYetScoreable) == Literal(True):
            continue
        silent.append(item)
    print("  silent gaps: %d %s" % (len(silent), "(must read zero)" if not silent else "-> DEFECT"))
    for i in silent:
        print("    %s" % ident(g, i))

    print("\n== 6. Launch readiness by package ==")
    gate_list = sorted(set(g.subjects(BL.isLaunchGate, Literal(True))),
                       key=lambda c: (int(g.value(c, BL.hasLaunchPriority) or 10 ** 6), str(c)))
    if not gate_list:
        print("  no launch gates declared")
    for c in gate_list:
        members = list(g.subjects(BL.memberOfContainer, c))
        blocking = [m for m in members if g.value(m, BL.hasState) not in (BL.Done, BL.Cancelled)]
        ext = list(g.objects(c, BL.hasExternalBlocker))
        deps = list(g.objects(c, BL.containerDependsOn))
        derived = [d for d in g.objects(c, BL.derivedContainerDependency) if d not in deps]
        print("  %-14s priority %-3s  blocking %d/%d  external dependency risk: %s"
              % (ident(g, c), g.value(c, BL.hasLaunchPriority), len(blocking), len(members),
                 ", ".join(ident(g, b) for b in ext) if ext else "none disclosed"))
        if deps or derived:
            print("                 depends on: %s%s"
                  % (", ".join(ident(g, d) for d in deps) or "none declared",
                     "  (undeclared but derived: %s)" % ", ".join(ident(g, d) for d in derived) if derived else ""))

    print("\n== 7. Package-level ranking (multi-factor, non-capabilities excluded) ==")
    rows = []
    for c in set(g.subjects(RDF.type, None)):
        if not any(g.triples((c, BL.memberOfContainer, None))) and (c, BL.hasPriorityScore, None) in g:
            pass
        if (c, BL.hasPriorityScore, None) not in g:
            continue
        if not list(g.subjects(BL.memberOfContainer, c)):
            continue
        if g.value(c, BL.isBusinessCapability) == Literal(False):
            continue
        v = scored(g, c, None)
        if v is not None:
            rows.append((v, c))
    rows.sort(key=lambda r: -r[0])
    if not rows:
        print("  no container carries a judged score")
    for i, (v, c) in enumerate(rows, start=1):
        declared = g.value(c, BL.hasRoadmapRank)
        note = ""
        if declared is not None and int(declared) != i:
            note = "  DISAGREEMENT: roadmap rank %s, score rank %d — both shown, neither adjusted" % (declared, i)
        print("  %-14s score %6.2f  roadmap rank %-4s%s" % (ident(g, c), v, declared if declared is not None else "—", note))
        deps = list(g.objects(c, BL.containerDependsOn))
        if deps:
            print("                 depends on: %s" % ", ".join(ident(g, d) for d in deps))
    excluded = [c for c in g.subjects(BL.isBusinessCapability, Literal(False))]
    for c in excluded:
        deps = list(g.objects(c, BL.containerDependsOn))
        print("  excluded: %s (tagged not a business capability)%s"
              % (ident(g, c), "  depends on: " + ", ".join(ident(g, d) for d in deps) if deps else ""))

    print("\n== 8. Orphan and package-coverage check ==")
    orphans = [i for i in set(g.subjects(BL.hasState, None))
               if not is_container(g, i)
               and not list(g.objects(i, BL.memberOfContainer))]
    empty = [c for c in set(g.subjects(RDF.type, BL.Package)) | set(g.subjects(RDF.type, BL.Backlog))
             if not list(g.subjects(BL.memberOfContainer, c))]
    print("  orphan items      : %d %s" % (len(orphans), ", ".join(ident(g, i) for i in orphans)))
    print("  empty containers  : %d %s" % (len(empty), ", ".join(ident(g, c) for c in empty)))

    print("\n== 9. Lifecycle and workflow ==")
    states = ["Proposed", "Ready", "InProgress", "Done", "Cancelled"]
    counts = {}
    for s in states:
        counts[s] = sum(1 for i in g.subjects(BL.hasState, BL[s]) if not is_container(g, i))
    print("  item states  : " + ", ".join("%s %d" % (s, counts[s]) for s in states))
    workflows = list(g.subjects(RDF.type, BL.Workflow))
    if not workflows:
        print("  no workflow governs this register — state changes are unconstrained")
    for w in workflows:
        print("  workflow %s permits:" % ident(g, w))
        for t_ in sorted(g.objects(w, BL.hasTransition), key=str):
            frm = g.value(t_, BL.fromState)
            to = g.value(t_, BL.toState)
            print("    %-10s %-12s -> %-12s guard: %s"
                  % (g.value(t_, BL.hasTransitionName) or "",
                     str(frm).rsplit("#", 1)[-1], str(to).rsplit("#", 1)[-1],
                     (str(g.value(t_, BL.hasTransitionGuard) or "none"))[:58]))
    unexplained = []
    for item in set(g.subjects(BL.hasState, None)):
        if is_container(g, item):
            continue
        events = [(g.value(e, BL.transitionedAt), e) for e in g.subjects(BL.transitionedItem, item)]
        if not events:
            continue
        events.sort(key=lambda x: str(x[0]))
        last = events[-1][1]
        dest = g.value(g.value(last, BL.viaTransition), BL.toState)
        if dest is not None and g.value(item, BL.hasState) != dest:
            unexplained.append(item)
    print("  states not explained by recorded history: %d %s"
          % (len(unexplained), ", ".join(ident(g, i) for i in unexplained)))

    if args.emit:
        out = Graph()
        out.bind("backlog", BL)
        report = URIRef("http://example.org/report#Run_%s" % now.strftime("%Y%m%dT%H%M%S"))
        out.add((report, RDF.type, BL.RoadmapReport))
        out.add((report, BL.hasRunTimestamp, Literal(now.isoformat(), datatype=XSD.dateTime)))
        for b in g.subjects(RDF.type, BL.Backlog):
            out.add((report, BL.reportOf, b))
            break
        for s in SECTIONS:
            out.add((report, BL.hasSection, BL[s]))
        if next_throughput:
            out.add((next_throughput[1], BL.derivedInReport, report))
            out.add((next_throughput[1], BL.underRankingModel, BL.ThroughputRanking))
        if next_scoped:
            out.add((next_scoped[1], BL.derivedInReport, report))
            out.add((next_scoped[1], BL.underRankingModel, BL.LaunchScopedRanking))
        out.serialize(args.emit, format="turtle")
        print("\nreport individual emitted: %s" % args.emit)

    return 1 if silent else 0


if __name__ == "__main__":
    sys.exit(main())
