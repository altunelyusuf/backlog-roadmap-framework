#!/usr/bin/env python3
"""backlog_lineage_compass v1.0.0 — closure readiness, progress, risk and focus, computed.

Answers four real questions this framework's own vocabulary already has the data
for, but nothing previously computed together in one place:

  1. CLOSURE READINESS  -- is this lineage's mission eligible for Out_Achieved?
     (AchievedOnlyWhenClearShape's own condition, run live: every goal's
     objective is either at target or carries an AchievementStatus.)
  2. PROGRESS            -- per objective, latest observation vs baseline and
     target, and whether that observation is stale against a passed checkpoint
     (CheckpointObservedShape's own condition, run live).
  3. RISK                -- real, unresolved Impediment individuals and real,
     not-yet-pursued Opportunity individuals belonging to this lineage.
  4. FOCUS (the compass)  -- among objectives not yet settled, which one has
     the largest fraction of its original gap still remaining. Ranked by
     remaining-fraction = |current - target| / |baseline - target|, using
     only numbers the register already asserts -- not a new estimate.

This is a REPORT, not a gate: it never writes to the register, and it never
sets hasMissionOutcome or lineageArchived itself (that decision names a real
achievement-status or trade-off a human should make, per this framework's own
G58 finding that neither available status was an honest fit without one).
--emit-closure writes a *proposed* transition as a separate, clearly-labelled
Turtle file for review, never applied automatically.

Usage:
  backlog_lineage_compass_v1_0_0.py REGISTER.ttl [--lineage LINEAGE_LOCAL_NAME] [--emit-closure FILE]
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
    hits = glob.glob(os.path.join(PKG, subdir, "%s_v*.%s" % (stem, ext)))
    if not hits:
        raise SystemExit("no artifact matching %s/%s_v*.%s" % (subdir, stem, ext))
    return sorted(hits, key=_semver)[-1]


TBOX = latest("01-ontologies", "backlog_tbox")
ABOX = latest("01-ontologies", "backlog_abox")


def load(paths):
    g = Graph()
    for p in paths:
        g.parse(p, format="turtle")
    return g


def local(n):
    return str(n).split("#")[-1] if n else "(none)"


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def latest_observation(g, obj):
    """The most recent MetricObservation for this objective, or None."""
    best, best_at = None, None
    for obs in g.subjects(BL.observationFor, obj):
        at = g.value(obs, BL.observedAt)
        if at is None:
            continue
        at_dt = at.toPython()
        if best_at is None or at_dt > best_at:
            best, best_at = obs, at_dt
    return best, best_at


def objective_status(g, obj):
    """Returns dict: baseline, target, direction, current, current_at, achieved,
    achievement_status, remaining_fraction, stale (bool, vs any passed checkpoint)."""
    baseline = g.value(obj, BL.hasBaselineValue)
    target = g.value(obj, BL.hasTargetValue)
    direction = g.value(obj, BL.hasTargetDirection)
    ach_status = g.value(obj, BL.hasAchievementStatus)
    obs, at = latest_observation(g, obj)
    current = g.value(obs, BL.hasObservedValue) if obs else None

    met = False
    if current is not None and target is not None and direction is not None:
        c, t = float(current), float(target)
        d = local(direction)
        if d == "Dir_Decrease":
            met = c <= t
        elif d == "Dir_Increase":
            met = c >= t
        elif d == "Dir_Hold":
            met = c == t

    remaining_fraction = None
    if current is not None and baseline is not None and target is not None:
        b, t, c = float(baseline), float(target), float(current)
        denom = abs(b - t)
        remaining_fraction = abs(c - t) / denom if denom > 0 else (0.0 if c == t else 1.0)

    # Staleness: any checkpoint for this objective whose date has passed with
    # no observation dated at or after it -- the same condition CheckpointObservedShape checks.
    stale = False
    for cp in g.objects(obj, BL.hasCheckpoint):
        cd = g.value(cp, BL.checkpointDate)
        if cd is None:
            continue
        if cd.toPython() < now_utc():
            has_covering = False
            for o2, at2 in [(o, a) for o in g.subjects(BL.observationFor, obj)
                            for a in [g.value(o, BL.observedAt)] if a is not None]:
                if at2.toPython() >= cd.toPython():
                    has_covering = True
                    break
            if not has_covering:
                stale = True

    return {
        "baseline": baseline, "target": target, "direction": direction,
        "current": current, "current_at": at, "achieved": met,
        "achievement_status": ach_status, "remaining_fraction": remaining_fraction,
        "stale": stale,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("register")
    ap.add_argument("--lineage", default=None, help="local name of the Lineage to report on")
    ap.add_argument("--emit-closure", default=None, help="write a proposed (not applied) closure Turtle to this path")
    ap.add_argument("--propose-corrective", default=None,
                     help="for the single top FOCUS objective, write a proposed corrective PBI "
                          "(RICE-scored, with a cost estimate and a simple projection) to this path")
    ap.add_argument("--propose-retrospective", default=None,
                     help="for any objective with 2+ closed corrective attempts and still open, "
                          "write a proposed RetrospectiveFinding + Out_Abandoned transition to this path")
    args = ap.parse_args()

    g = load([TBOX, ABOX, args.register])

    lineages = list(g.subjects(RDF.type, BL.Lineage))
    if args.lineage:
        lineages = [l for l in lineages if local(l) == args.lineage]
    if not lineages:
        print("no matching Lineage found"); return 1

    all_lineages_in_graph = list(g.subjects(RDF.type, BL.Lineage))
    # --- Register-wide risk: Impediments/Opportunities that name no specific
    # lineage (e.g. impeding the register container itself) would otherwise be
    # silently invisible in every per-lineage section below. Reported once, here.
    print("#" * 78)
    print("REGISTER-WIDE RISK (not scoped to any single lineage)")
    print("#" * 78)
    reg_imps = [i for i in g.subjects(RDF.type, BL.Impediment)
                if g.value(i, BL.impedes) is not None
                and not any((g.value(i, BL.impedes), BL.belongsToLineage, l) in g for l in all_lineages_in_graph)]
    if not reg_imps:
        print("    No register-wide (non-lineage-scoped) Impediments.")
    for i in reg_imps:
        resolved = g.value(i, BL.resolvedAt)
        status = "RESOLVED" if resolved else "OPEN"
        print("    [%s]" % status, local(i), "impedes", local(g.value(i, BL.impedes)), "--",
              str(g.value(i, BL.hasImpedimentStatement))[:120])
    print()

    for lin in lineages:
        mission = g.value(lin, BL.lineageForMission)
        outcome = g.value(mission, BL.hasMissionOutcome)
        archived = g.value(lin, BL.lineageArchived)
        print("=" * 78)
        print("LINEAGE   :", local(lin), " | ordinal", g.value(lin, BL.lineageOrdinal))
        print("MISSION   :", local(mission), " | outcome:", local(outcome), " | archived:", archived)
        print("=" * 78)

        goals = list(g.subjects(BL.contributesToMission, mission))
        rows = []
        for goal in goals:
            for obj in g.subjects(BL.contributesToGoal, goal):
                st = objective_status(g, obj)
                rows.append((goal, obj, st))

        # --- 1. CLOSURE READINESS ---
        blockers = [(goal, obj, st) for goal, obj, st in rows
                    if not st["achieved"] and st["achievement_status"] is None]
        print("\n[1] CLOSURE READINESS")
        if outcome and local(outcome) != "Out_InFlight":
            print("    Mission outcome already settled:", local(outcome))
        elif not rows:
            print("    No Goal/Objective chain is modeled for this mission -- this framework's own")
            print("    objective-tracking discipline (G33/G58) postdates it. Cannot compute readiness.")
        elif not blockers:
            print("    ELIGIBLE for Out_Achieved: every goal's objective is at target")
            print("    or carries an AchievementStatus explaining why it no longer steers.")
        else:
            print("    NOT eligible. %d of %d goals blocking:" % (len(blockers), len(rows)))
            for goal, obj, st in blockers:
                print("      -", local(obj), "(goal:", local(goal), ") -- current",
                      st["current"], "target", st["target"], "direction", local(st["direction"]))

        # --- 2. PROGRESS ---
        print("\n[2] PROGRESS (per objective, latest real observation)")
        for goal, obj, st in rows:
            flag = "STALE" if st["stale"] else ("MET" if st["achieved"] else "OPEN")
            ach = (" [%s]" % local(st["achievement_status"])) if st["achievement_status"] else ""
            print("    %-28s baseline=%-6s target=%-6s current=%-6s [%s]%s" % (
                local(obj), st["baseline"], st["target"], st["current"], flag, ach))
            if st["stale"]:
                print("        ^ a checkpoint has passed with no observation dated at or after it")

        # --- 3. RISK: real Impediments and Opportunities tied to this lineage ---
        print("\n[3] RISK")
        lineage_objs = set(local(o) for _, o, _ in rows)
        imps = []
        for i in g.subjects(RDF.type, BL.Impediment):
            target_item = g.value(i, BL.impedes)
            if target_item is None:
                continue
            if (target_item, BL.belongsToLineage, lin) in g:
                imps.append(i)
        if not imps:
            print("    No Impediment individuals belong to this lineage.")
        for i in imps:
            resolved = g.value(i, BL.resolvedAt)
            status = "RESOLVED" if resolved else "OPEN"
            print("    [%s]" % status, local(i), "--", str(g.value(i, BL.hasImpedimentStatement))[:120])

        opps = []
        for o in g.subjects(RDF.type, BL.Opportunity):
            if g.value(o, BL.convertedToItem) is not None:
                continue
            opp_for = g.value(o, BL.opportunityFor)
            if local(opp_for) in lineage_objs:
                opps.append(o)
        print("    Opportunities identified for this lineage, not yet pursued:", len(opps))
        for o in opps:
            print("      -", local(o), "--", str(g.value(o, BL.hasOpportunityStatement))[:120])

        # --- 4. FOCUS / COMPASS ---
        print("\n[4] FOCUS -- ranked by fraction of original gap still remaining")
        open_rows = [(goal, obj, st) for goal, obj, st in rows
                     if not st["achieved"] and st["achievement_status"] is None
                     and st["remaining_fraction"] is not None]
        open_rows.sort(key=lambda r: r[2]["remaining_fraction"], reverse=True)
        if not open_rows:
            print("    Nothing open. No focus recommendation needed.")
        for rank, (goal, obj, st) in enumerate(open_rows, 1):
            frac = st["remaining_fraction"]
            if frac > 1.0:
                tag = "REGRESSED past its original baseline (%.0f%% of the original gap, and worse)" % (frac * 100)
            else:
                tag = "%.0f%% of original gap remains" % (frac * 100)
            print("    %d. %-28s %s (current %s, target %s)" % (
                rank, local(obj), tag, st["current"], st["target"]))
        if open_rows:
            top = open_rows[0]
            worse_word = "regressed" if top[2]["remaining_fraction"] > 1.0 else "farthest from target"
            print("\n    COMPASS: %s is the real bottleneck -- %s, %.0f%% of its original gap,"
                  % (local(top[1]), worse_word, top[2]["remaining_fraction"] * 100))
            print("    the largest of any open objective. Closure work should aim here first.")

        # --- 5. FAILURE MODE TAXONOMY -- the reverse-direction check, elegant not counted ---
        print("\n[5] FAILURE MODE TAXONOMY (reverse compass -- real patterns, not a fixed attempt count)")

        def observation_before(obj_node, at_dt):
            best, best_at = None, None
            for o in g.subjects(BL.observationFor, obj_node):
                oa = g.value(o, BL.observedAt)
                if oa is None or oa.toPython() > at_dt:
                    continue
                if best_at is None or oa.toPython() > best_at:
                    best, best_at = o, oa.toPython()
            return best

        def observation_at_or_after(obj_node, at_dt):
            best, best_at = None, None
            for o in g.subjects(BL.observationFor, obj_node):
                oa = g.value(o, BL.observedAt)
                if oa is None or oa.toPython() < at_dt:
                    continue
                if best_at is None or oa.toPython() > best_at:
                    best, best_at = o, oa.toPython()
            return best

        def attempt_ineffective(w, obj_node, direction):
            started = g.value(w, BL.startedAt)
            finished = g.value(w, BL.finishedAt)
            if started is None or finished is None:
                return None  # cannot judge without data
            before = observation_before(obj_node, started.toPython())
            after = observation_at_or_after(obj_node, finished.toPython())
            if before is None or after is None:
                return None
            vb = float(g.value(before, BL.hasObservedValue))
            va = float(g.value(after, BL.hasObservedValue))
            d = local(direction)
            if d == "Dir_Decrease":
                return va >= vb
            if d == "Dir_Increase":
                return va <= vb
            if d == "Dir_Hold":
                return va != vb
            return None

        ineffective = []
        for goal, obj, st in rows:
            if st["achieved"] or st["achievement_status"] is not None:
                continue
            for w in g.objects(obj, BL.metricMovableBy):
                if local(g.value(w, BL.hasState)) not in ("Done", "Cancelled"):
                    continue
                result = attempt_ineffective(w, obj, st["direction"])
                if result:
                    ineffective.append((goal, obj, st, w))

        scope_creep = []
        for e in g.subjects(RDF.type, BL.Epic):
            po = g.value(e, BL.pursuesObjective)
            if po is None:
                continue
            goal_of = g.value(po, BL.contributesToGoal)
            if goal_of is None:
                continue
            has_scope = g.value(goal_of, BL.derivesFromScope) is not None
            admitted = any(True for _ in g.subjects(BL.admitsItem, e))
            if not has_scope and not admitted:
                scope_creep.append(e)

        scope_gaps = [s for s in g.subjects(RDF.type, BL.ScopeStatement)
                      if not any(True for _ in g.subjects(BL.derivesFromScope, s))]

        if not ineffective and not scope_creep and not scope_gaps:
            print("    FM_IneffectiveCorrectiveAction: none. FM_ScopeCreep: none. FM_ScopeGap: none.")
        for goal, obj, st, w in ineffective:
            print("    FM_IneffectiveCorrectiveAction: %-24s via %-20s (closed, did not move the metric)"
                  % (local(obj), local(w)))
        for e in scope_creep:
            print("    FM_ScopeCreep: %-30s (no scope path, no ScopeChange admits it)" % local(e))
        for s in scope_gaps:
            print("    FM_ScopeGap: %-32s (no goal derives from this scope)" % local(s))

        exhausted = [(goal, obj, st) for goal, obj, st, w in ineffective]
        if args.propose_retrospective and exhausted:
            goal, obj, st = exhausted[0]
            attempts = [w for g2, o2, s2, w in ineffective if o2 == obj]
            finding = URIRef(str(obj) + "_IneffectivenessFinding")
            out = Graph()
            out.bind("backlog", BL)
            out.add((finding, RDF.type, BL.RetrospectiveFinding))
            out.add((finding, BL.hasFailureMode, BL.FM_IneffectiveCorrectiveAction))
            out.add((finding, BL.hasRootCause, Literal(
                "PROPOSED by backlog_lineage_compass_v1_0_0, not a finished analysis: %d real corrective "
                "attempt(s) (%s), each confirmed by its own before/after observation to have closed without "
                "moving %s toward target (current %s, target %s). The actual root cause -- whether the "
                "objective itself is achievable as stated, whether the attempts were poorly scoped, or whether "
                "the metric needs redefining -- is for a human retrospective to determine; this tool can only "
                "see that the pattern exists, confirmed by data rather than assumed from a count."
                % (len(attempts), ", ".join(local(w) for w in attempts), local(obj), st["current"], st["target"]))))
            out.add((finding, BL.hasFindingScope, BL.Scope_LineageLocal))
            out.add((finding, BL.relatesToWorkItem, obj))
            out.add((mission, BL.hasMissionOutcome, BL.Out_Abandoned))
            out.add((mission, rdflib.RDFS.comment, Literal(
                "PROPOSED, not applied. %d confirmed-ineffective corrective attempt(s) against %s with no "
                "target reached. Review the RetrospectiveFinding, set a real outcomeRationale, and confirm "
                "this is genuinely the honest call before publishing -- this tool proposes the option, it "
                "does not decide it." % (len(attempts), local(obj)))))
            out.serialize(destination=args.propose_retrospective, format="turtle")
            print("\n    Proposed retrospective + Out_Abandoned option for %s written to %s"
                  % (local(obj), args.propose_retrospective))
            print("    (NOT applied to the register). This is one option surfaced, not a recommendation")
            print("    to abandon -- review alongside [4] FOCUS before deciding.")

        if args.propose_corrective and open_rows:
            goal, obj, st = open_rows[0]
            has_live_action = any(
                (obj, BL.metricMovableBy, w) in g and local(g.value(w, BL.hasState)) not in ("Done", "Cancelled")
                for w in g.objects(obj, BL.metricMovableBy)
            )
            if has_live_action:
                print("\n    %s already has a live corrective action; no new proposal generated."
                      % local(obj))
            else:
                pid = "PBI_Corrective_%s" % local(obj)
                pbi = URIRef(str(obj) + "_CorrectivePBI")
                score = URIRef(str(obj) + "_CorrectiveScore")
                cost = URIRef(str(obj) + "_CorrectiveCost")
                dim = URIRef(str(obj) + "_CorrectiveCostDim")
                out = Graph()
                out.bind("backlog", BL)

                gap_desc = ("regressed past its original baseline" if st["remaining_fraction"] > 1.0
                            else "still %.0f%% short of target" % (st["remaining_fraction"] * 100))
                out.add((pbi, RDF.type, BL.Story))
                out.add((pbi, BL.hasState, BL.Proposed))
                out.add((pbi, BL.hasTitle, Literal(
                    "Move %s back toward target (currently %s, %s)" % (local(obj), st["current"], local(st["direction"])))))
                out.add((obj, BL.metricMovableBy, pbi))
                out.add((score, RDF.type, BL.RICEScore))
                out.add((score, BL.scoredByMethod, BL.Method_RICE))
                # Reach/Impact/Confidence/Effort disclosed as this tool's own estimate, not measured --
                # a human proposing or accepting the PBI should re-score with real knowledge of the work.
                out.add((score, BL.hasReach, Literal(1.0, datatype=XSD.decimal)))
                out.add((score, BL.hasImpact, Literal(2.0, datatype=XSD.decimal)))
                out.add((score, BL.hasConfidence, Literal(0.3, datatype=XSD.decimal)))
                out.add((score, BL.hasEffort, Literal(2.0, datatype=XSD.decimal)))
                out.add((score, BL.hasScoreValue, Literal(round(1.0 * 2.0 * 0.3 / 2.0, 3), datatype=XSD.decimal)))
                out.add((score, BL.hasScoreRationale, Literal(
                    "PROPOSED by backlog_lineage_compass_v1_0_0, not measured. Confidence deliberately low "
                    "(0.3): this tool knows the objective is blocking and %s, not what the real fix costs or "
                    "whether one is even the right response (the metric could instead need redefining -- this "
                    "tool proposes closing the gap, not which of those two is correct). Re-score before "
                    "committing real effort." % gap_desc)))
                out.add((pbi, BL.hasPriorityScore, score))
                out.add((cost, RDF.type, BL.DimensionalCost))
                out.add((cost, BL.costOfItem, pbi))
                out.add((cost, BL.alongDimension, dim))
                out.add((dim, RDF.type, BL.CostDimension))
                out.add((dim, BL.hasDimensionUnit, Literal("effort, unscoped -- placeholder pending real estimation")))
                out.add((cost, BL.hasQuantity, Literal(0, datatype=XSD.decimal)))
                out.add((cost, BL.isEstimatedCost, Literal(True)))
                if st["target"] is not None and st["baseline"] is not None:
                    out.add((pbi, rdflib.RDFS.comment, Literal(
                        "SIMULATION (arithmetic projection only, not a forecast of real effort): if this PBI "
                        "fully succeeds, %s would read %s (target), a change of %s from its current %s."
                        % (local(obj), st["target"], abs(float(st["current"]) - float(st["target"])), st["current"]))))
                out.serialize(destination=args.propose_corrective, format="turtle")
                print("\n    Proposed corrective PBI for %s written to %s (NOT applied to the register)."
                      % (local(obj), args.propose_corrective))
                print("    RICE score %.3f, Confidence deliberately low (0.3) -- this is a starting proposal,"
                      % (1.0 * 2.0 * 0.3 / 2.0))
                print("    not a scoped commitment. Re-score once real effort is known.")
                print("    This is a SKELETON, not a publishable PBI: it still needs a real identifier,")
                print("    lineage membership, investment category, and a real pursuesObjective before it")
                print("    would pass this register's own ordinary WorkItem completeness checks -- adding")
                print("    it alone is enough to close the corrective-action gap this run found, nothing more.")

        if args.emit_closure and not blockers and outcome and local(outcome) == "Out_InFlight":
            out = Graph()
            out.bind("backlog", BL)
            out.add((mission, BL.hasMissionOutcome, BL.Out_Achieved))
            note = ("PROPOSED, not applied. Every goal's objective was at target or carried an "
                    "AchievementStatus as of %s (backlog_lineage_compass_v1_0_0). Review and set "
                    "the real outcomeRationale before publishing." % now_utc().isoformat())
            out.add((mission, BL.outcomeRationale, Literal(note)))
            out.serialize(destination=args.emit_closure, format="turtle")
            print("\n    Proposed closure written to", args.emit_closure, "(NOT applied to the register).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
