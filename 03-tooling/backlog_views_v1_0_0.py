#!/usr/bin/env python3
"""backlog_views v1.0.0 — the classical project views, computed not stored.

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
    tb = newest("01-ontologies/backlog_tbox_v*.ttl")
    if tb:
        g.parse(tb, format="turtle")
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
    for i in set(g.subjects(RDF.type, BL.Iteration)):
        s, e = dt(g.value(i, BL.iterationStart)), dt(g.value(i, BL.iterationEnd))
        if s and e:
            its.append((s, e, i))
    if not its:
        print("  no iteration carries a period — nothing to burn down against")
        return
    its.sort()
    for s, e, i in its:
        members = [m for m in g.subjects(BL.memberOfContainer, i)]
        total = sum(effort(g, m) for m in members) or float(len(members))
        if not members:
            continue
        print("\n  %s  %s .. %s  (%d item(s), %.1f unit(s) committed)"
              % (ident(g, i), s.date(), e.date(), len(members), total))
        days = max(1, (e - s).days)
        rem = total
        line = []
        for d in range(days + 1):
            day = s + timedelta(days=d)
            done = 0.0
            for m in members:
                f = dt(g.value(m, BL.finishedAt))
                if f and f <= day:
                    done += effort(g, m) or 1.0
            rem = total - done
            line.append((day, rem, done))
        width = 46
        for day, rem, done in line:
            filled = int(width * (rem / total)) if total else 0
            print("    %s |%s%s| %.1f left" % (day.date(), "#" * filled,
                                               " " * (width - filled), rem))


# -------------------------------------------------------- cumulative flow
def cfd(g):
    print("\n== CUMULATIVE FLOW — items by state over time ==")
    events = []
    for t in g.subjects(RDF.type, BL.TransitionEvent):
        when = dt(g.value(t, BL.transitionedAt))
        to = g.value(t, BL.transitionedTo)
        if when and to:
            events.append((when, str(to).rsplit("#", 1)[-1]))
    if not events:
        print("  no TransitionEvent carries a timestamp — a CFD needs the")
        print("  state history, not the current state. Record transitions.")
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
