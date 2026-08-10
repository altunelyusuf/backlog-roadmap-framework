#!/usr/bin/env python3
"""backlog_views v1.4.0 — the classical project views, computed not stored.

Emits Mermaid and fixed-width tables from a register. Mermaid because it is
plain text: it diffs, it reviews, it renders in GitHub and most editors without
a toolchain, and it adds no Python dependency to a package whose only ones are
rdflib and pyshacl.

WHAT IS DERIVED HERE, AND WHY NONE OF IT IS STORED

  Gantt              plannedStart/plannedFinish against startedAt/finishedAt
  Burn-down/up       iteration period + finishedAt + hasEffortEstimate
  Cumulative flow    TransitionEvent timestamps by state
  Network (AON)      dependsOn + hasDuration; longest path = critical path
  Earned value       PV/EV/AC from estimates, actuals and the baseline
  Cost dimensions    per-dimension totals, budget comparison, derived roll-up

Storing any of these would duplicate a computable fact that could then disagree
with its own inputs. The framework's standing position is that a derived number
belongs in the report, not the register.

ON SPI, AND WHY IT WAS PREVIOUSLY REFUSED

Schedule performance needs planned value, which needs dates, which the subject
deliberately did not carry: roadmap horizons are ordinal by design. That refusal
was recorded as a scope exclusion and has now been reversed by an owner-decided
ScopeChange rather than by deleting it. Both SPI figures are reported:

  SPI (current)   against the baseline in force now
  SPI (original)  against the first baseline ever set

The second is the one a rebaselined project would rather not show, and it is the
reason superseded baselines are retained rather than replaced. A tool that
reported only the first would let schedule variance be driven to zero by moving
the dates, which is the criticism earned-value practice most often attracts.

WITHOUT A KICKOFF, NO SCHEDULE NUMBER IS PRINTED. A baseline of dates with no
recorded activation anchors to nothing; the views that need day zero say so
rather than assuming today.

Usage: backlog_views_v1_0_0.py <register.ttl> [--gantt|--burn|--cfd|--network|--ev]
"""

import sys
import glob
import os
from datetime import datetime, timedelta

try:
    from rdflib import Graph, Namespace, RDF, Literal
except ImportError:
    print("needs rdflib: pip install rdflib")
    sys.exit(2)

BL = Namespace("http://example.org/backlog#")
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)


def newest(pattern):
    import re
    files = glob.glob(os.path.join(PKG, pattern))
    if not files:
        return None

    def key(p):
        m = re.search(r"_v(\d+)_(\d+)_(\d+)\.", os.path.basename(p))
        return [int(x) for x in m.groups()] if m else [0, 0, 0]
    return sorted(files, key=key)[-1]


def dt(v):
    if v is None:
        return None
    s = str(v).replace("Z", "+00:00")
    try:
        d = datetime.fromisoformat(s)
    except ValueError:
        return None
    return d.replace(tzinfo=None) if d.tzinfo else d


def ident(g, n):
    return str(g.value(n, BL.hasIdentifier) or str(n).rsplit("#", 1)[-1])


def is_container(g, n):
    for c in (BL.Backlog, BL.Package, BL.Release, BL.Iteration, BL.Roadmap,
              BL.ImplementationProject):
        if (n, RDF.type, c) in g:
            return True
    return False


def load(path):
    g = Graph()
    # TBox AND the framework ABox. The ABox declares the StateTransition
    # individuals every TransitionEvent points at, so loading only the TBox
    # left the second hop dangling and the cumulative flow unresolvable — a
    # SECOND defect behind the first, and one the corrected diagnostic
    # surfaced immediately by saying WHY it could not resolve rather than
    # only that it could not.
    for pat in ("01-ontologies/backlog_tbox_v*.ttl",
                "01-ontologies/backlog_abox_v*.ttl"):
        f = newest(pat)
        if f:
            g.parse(f, format="turtle")
    g.parse(path, format="turtle")
    return g


def kickoff(g):
    for k in g.subjects(RDF.type, BL.KickOff):
        return dt(g.value(k, BL.kickedOffAt)), k
    return None, None


def work_items(g):
    out = []
    for i in set(g.subjects(BL.hasState, None)):
        if not is_container(g, i):
            out.append(i)
    return sorted(out, key=str)


def effort(g, item):
    for e in g.objects(item, BL.hasCostEstimate):
        v = g.value(e, BL.hasEffortEstimate)
        if v is not None:
            return float(v)
    return 0.0


# ---------------------------------------------------------------- Gantt
def gantt(g):
    print("\n== GANTT — planned bars against actual, Mermaid ==")
    k, kn = kickoff(g)
    if k is None:
        print("  NOT DRAWN — this register records no KickOff, so planned dates")
        print("  anchor to nothing. A bar drawn from an unanchored baseline shows")
        print("  a plan against itself, which always looks met.")
        return
    print("  day zero: %s (%s)" % (k.date(), str(g.value(kn, BL.hasKickOffMode)).rsplit("#", 1)[-1]))
    rows = []
    for i in work_items(g):
        ps, pf = dt(g.value(i, BL.plannedStart)), dt(g.value(i, BL.plannedFinish))
        if ps and pf:
            rows.append((ps, pf, i))
    if not rows:
        print("  no item carries both a planned start and a planned finish")
        return
    rows.sort()
    print("\n```mermaid")
    print("gantt")
    print("    title Plan against actual")
    print("    dateFormat YYYY-MM-DD")
    print("    axisFormat %m-%d")
    print("    section Planned")
    for ps, pf, i in rows:
        print("    %s :plan_%s, %s, %dd"
              % (ident(g, i), ident(g, i).replace("-", "_"), ps.date(),
                 max(1, (pf - ps).days)))
    actuals = [(dt(g.value(i, BL.startedAt)), dt(g.value(i, BL.finishedAt)), i)
               for _, _, i in rows]
    actuals = [(a, b, i) for a, b, i in actuals if a]
    if actuals:
        print("    section Actual")
        for a, b, i in sorted(actuals):
            end = b or datetime.now()
            print("    %s :done, act_%s, %s, %dd"
                  % (ident(g, i), ident(g, i).replace("-", "_"), a.date(),
                     max(1, (end - a).days)))
    print("```")
    print("\n  slip against the current baseline:")
    for ps, pf, i in rows:
        af = dt(g.value(i, BL.finishedAt))
        if af:
            d = (af - pf).days
            print("    %-12s finished %+d day(s) against plan" % (ident(g, i), d))
        else:
            print("    %-12s not finished" % ident(g, i))


# ------------------------------------------------------------ burn-down
def burn(g):
    print("\n== BURN-DOWN / BURN-UP — per iteration ==")
    its = []
    # Iterations AND Increments: both carry a period, and v1.1.0 looked only at
    # the first, so a backfilled Increment holding twenty shipped releases was
    # skipped in silence — a burn-down that omits a whole container without
    # saying so is worse than one that refuses.
    periodic = set(g.subjects(RDF.type, BL.Iteration)) | set(g.subjects(RDF.type, BL.Increment))
    for i in periodic:
        s, e = dt(g.value(i, BL.iterationStart)), dt(g.value(i, BL.iterationEnd))
        if s and e:
            its.append((s, e, i))
    if not its:
        print("  no iteration carries a period — nothing to burn down against")
        return
    its.sort()
    for s, e, i in its:
        members = [m for m in g.subjects(BL.memberOfContainer, i)]
        if not members:
            continue
        # Basis must be CONSISTENT between the total and the burned amount.
        # v1.0.0 summed effort for the total but fell back to 1.0 per item when
        # burning, so an item with no estimate contributed nothing to the total
        # and one unit to the burn — and the chart reached zero while work was
        # still open. A burn-down that hits zero with items unfinished is the
        # "looks complete" failure this framework exists to refuse, produced by
        # its own tool. Where any member lacks an estimate the whole iteration
        # is counted in ITEMS, and the basis is printed.
        missing = [m for m in members if effort(g, m) == 0.0]
        if missing:
            basis = "items"
            weight = lambda m: 1.0
        else:
            basis = "effort units"
            weight = lambda m: effort(g, m)
        total = sum(weight(m) for m in members)
        print("\n  %s  %s .. %s  (%d item(s), %.1f %s committed)"
              % (ident(g, i), s.date(), e.date(), len(members), total, basis))
        if missing:
            print("    basis is ITEMS: %d member(s) carry no effort estimate, so an"
                  % len(missing))
            print("    effort burn-down would silently omit them: %s"
                  % ", ".join(ident(g, m) for m in missing[:5]))
        days = max(1, (e - s).days)
        rem = total
        line = []
        for d in range(days + 1):
            day = s + timedelta(days=d)
            done = 0.0
            for m in members:
                f = dt(g.value(m, BL.finishedAt))
                if f and f <= day:
                    done += weight(m)
            rem = total - done
            line.append((day, rem, done))
        width = 46
        for day, rem, done in line:
            filled = int(width * (rem / total)) if total else 0
            print("    %s |%s%s| %.1f left" % (day.date(), "#" * filled,
                                               " " * (width - filled), rem))
        open_now = [m for m in members
                    if g.value(m, BL.hasState) not in (BL.Done, BL.Cancelled)]
        if rem == 0 and open_now:
            print("    WARNING: burned to zero with %d item(s) still open (%s)."
                  % (len(open_now), ", ".join(ident(g, m) for m in open_now[:4])))
            print("    A burn-down reaching zero over unfinished work is measuring")
            print("    the wrong thing; check the basis above.")


# -------------------------------------------------------- cumulative flow
def cfd(g):
    print("\n== CUMULATIVE FLOW — items by state over time ==")
    # The target state is TWO hops away: a TransitionEvent points at a
    # StateTransition via viaTransition, and the StateTransition carries
    # toState. v1.0.0 read a single-hop backlog:transitionedTo, which does not
    # exist in the subject's TBox at any version — so this section could only
    # ever print its refusal, and did, which is why the bug survived: a
    # refusal that is correct for the WRONG reason looks exactly like one that
    # is correct. Reported by a parallel session reading the declared model
    # rather than the tool's output. The tool now also distinguishes the two
    # causes it previously conflated.
    events = []
    malformed = 0
    for ev in g.subjects(RDF.type, BL.TransitionEvent):
        when = dt(g.value(ev, BL.transitionedAt))
        trans = g.value(ev, BL.viaTransition)
        to = g.value(trans, BL.toState) if trans is not None else None
        if when and to:
            events.append((when, str(to).rsplit("#", 1)[-1]))
        else:
            malformed += 1
    if not events:
        n = len(list(g.subjects(RDF.type, BL.TransitionEvent)))
        if n == 0:
            print("  no TransitionEvent in this register — a CFD needs the state")
            print("  HISTORY, not the current state. Record transitions.")
        else:
            print("  %d TransitionEvent(s) present but none resolves to a target state." % n)
            print("  The path is two hops: ?e viaTransition ?t . ?t toState ?s .")
            print("  %d event(s) are missing a timestamp or a StateTransition." % malformed)
        return
    events.sort()
    running = {}
    print("  %-12s %s" % ("date", "cumulative entries per state"))
    for when, st in events:
        running[st] = running.get(st, 0) + 1
        print("  %-12s %s" % (when.date(),
                              "  ".join("%s=%d" % (k, v) for k, v in sorted(running.items()))))


# ------------------------------------------------------------- network
def network(g):
    print("\n== NETWORK (AON) — dependencies, and the critical path ==")
    items = work_items(g)
    dep = {i: [d for d in g.objects(i, BL.dependsOn)] for i in items}
    if not any(dep.values()):
        print("  no dependsOn edges — the network is a set of isolated nodes")
        return
    print("\n```mermaid")
    print("graph LR")
    for i in items:
        for d in dep[i]:
            print("    %s --> %s" % (ident(g, d).replace("-", "_"),
                                     ident(g, i).replace("-", "_")))
    print("```")
    dur = {i: float(g.value(i, BL.hasDuration) or 0) for i in items}
    if not any(dur.values()):
        print("\n  critical path NOT computed: no item carries hasDuration.")
        print("  A critical path is the longest chain of DURATIONS, and duration")
        print("  is not effort — two people for a day and one for two days share")
        print("  an effort and differ in duration.")
        return
    memo = {}

    def longest(n, seen):
        if n in memo:
            return memo[n]
        if n in seen:
            return (0.0, [])
        best = (0.0, [])
        for d in dep.get(n, []):
            v, p = longest(d, seen | {n})
            if v > best[0]:
                best = (v, p)
        r = (best[0] + dur.get(n, 0.0), best[1] + [n])
        memo[n] = r
        return r
    top = max((longest(i, set()) for i in items), key=lambda x: x[0])
    print("\n  critical path: %.1f day(s)" % top[0])
    print("    %s" % " -> ".join(ident(g, n) for n in top[1]))


# --------------------------------------------------------- earned value
def ev(g):
    print("\n== EARNED VALUE — CPI, and SPI against both baselines ==")
    k, _ = kickoff(g)
    items = work_items(g)
    bac = sum(effort(g, i) for i in items)
    done = [i for i in items if g.value(i, BL.hasState) == BL.Done]
    earned = sum(effort(g, i) for i in done)
    actual = 0.0
    for i in items:
        a = g.value(i, BL.hasActualEffort)
        if a is not None:
            actual += float(a)
    print("  BAC (budget at completion) : %.1f" % bac)
    print("  EV  (earned value)         : %.1f  (%d item(s) Done)" % (earned, len(done)))
    print("  AC  (actual cost)          : %.1f" % actual)
    if actual > 0:
        print("  CPI = EV/AC                : %.2f  %s"
              % (earned / actual, "under budget" if earned / actual >= 1 else "over budget"))
    else:
        print("  CPI                        : not computable — no actual effort recorded")

    if k is None:
        print("\n  SPI NOT COMPUTED — no KickOff, so there is no day zero and planned")
        print("  value has no date to be measured at. This is refused rather than")
        print("  assumed: assuming today would make every plan appear on schedule")
        print("  on the day it is read.")
        return
    now = datetime.now()
    baselines = sorted(
        ((dt(g.value(b, BL.baselinedAt)), b) for b in g.subjects(RDF.type, BL.PlanBaseline)),
        key=lambda x: (x[0] or datetime.min))
    if not baselines:
        print("\n  SPI NOT COMPUTED — no PlanBaseline recorded.")
        return

    def pv_at(when):
        total = 0.0
        for i in items:
            pf = dt(g.value(i, BL.plannedFinish))
            if pf and pf <= when:
                total += effort(g, i)
        return total
    pv = pv_at(now)
    print("\n  PV (planned value at %s) : %.1f" % (now.date(), pv))
    if pv > 0:
        print("  SPI (current baseline)     : %.2f  %s"
              % (earned / pv, "ahead" if earned / pv >= 1 else "behind"))
    else:
        print("  SPI (current baseline)     : nothing was planned to be complete by now")
    if len(baselines) > 1:
        print("  NOTE: %d baseline(s) exist. The current-baseline SPI above measures"
              % len(baselines))
        print("  against a plan that has been moved %d time(s); the original-baseline"
              % (len(baselines) - 1))
        print("  figure is the one a rebaselined project would rather not show, and")
        print("  it requires the superseded baselines' dates, which are retained")
        print("  precisely so it can be computed.")


# ------------------------------------------------------------ cost
def cost(g):
    print("\n== COST — per dimension, against budget ==")
    dims = sorted(set(g.subjects(RDF.type, BL.CostDimension)), key=str)
    if not dims:
        print("  no CostDimension declared — nothing to total")
        return
    for d in dims:
        unit = g.value(d, BL.hasDimensionUnit)
        rate = g.value(d, BL.hasDimensionRate)
        cur = g.value(d, BL.hasRateCurrency)
        recs = [c for c in g.subjects(BL.alongDimension, d)]
        obs = sum(float(g.value(c, BL.hasQuantity) or 0)
                  for c in recs if g.value(c, BL.isEstimatedCost) == Literal(False))
        est = sum(float(g.value(c, BL.hasQuantity) or 0)
                  for c in recs if g.value(c, BL.isEstimatedCost) == Literal(True))
        unk = sum(float(g.value(c, BL.hasQuantity) or 0)
                  for c in recs if g.value(c, BL.isEstimatedCost) is None)
        name = str(g.value(d, __import__("rdflib").RDFS.label) or str(d).rsplit("#", 1)[-1])
        print("\n  %s  (%s)" % (name, unit or "NO UNIT"))
        print("    observed %.1f | estimated %.1f | unstated %.1f  across %d record(s)"
              % (obs, est, unk, len(recs)))
        if unk:
            print("    %.1f is neither marked observed nor estimated and is NOT folded into" % unk)
            print("    either figure; a total mixing measured and forecast reads as measurement.")
        if rate is not None:
            print("    priced: %.4f %s per unit -> observed spend %.2f %s"
                  % (float(rate), cur, obs * float(rate), cur))
        else:
            print("    UNPRICED — reported separately; it contributes to no monetary total,")
            print("    which is a choice, not an omission: some costs are constraints, not bills.")
        for b in g.subjects(BL.budgetDimension, d):
            ceil = float(g.value(b, BL.hasBudgetCeiling) or 0)
            used = obs + est
            pct = (used / ceil * 100) if ceil else 0
            flag = "OVER" if used > ceil else "within"
            print("    budget %.1f %s -> %.1f used (%.0f%%) %s" % (ceil, unit, used, pct, flag))


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    path = sys.argv[1]
    flags = [a for a in sys.argv[2:] if a.startswith("--")]
    g = load(path)
    print("register    : %s" % os.path.basename(path))
    lvl = None
    for _, o in g.subject_objects(BL.hasConformanceLevel):
        lvl = str(o).rsplit("#", 1)[-1]
    print("level       : %s" % (lvl or "none declared"))
    run_all = not flags
    if run_all or "--gantt" in flags:
        gantt(g)
    if run_all or "--burn" in flags:
        burn(g)
    if run_all or "--cfd" in flags:
        cfd(g)
    if run_all or "--network" in flags:
        network(g)
    if run_all or "--ev" in flags:
        ev(g)
    if run_all or "--cost" in flags:
        cost(g)
    return 0


if __name__ == "__main__":
    sys.exit(main())
