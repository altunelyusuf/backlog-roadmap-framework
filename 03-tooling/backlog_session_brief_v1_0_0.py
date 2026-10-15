#!/usr/bin/env python3
"""backlog_session_brief v1.0.0 -- what a session needs in front of it before it chooses work (ruling G122).

A session that starts from a start-gate message alone knows whether it MAY work, not what it SHOULD work on. This brief adds the
four facts the register already holds and nothing else:
  FOCUS        the objective with the largest share of its original gap still open (the compass's own ranking), and how many
               goals still block closing the mission
  IN PROGRESS  the lineage's items that are In Progress
  DUE          checkpoints that fall due within DAYS days, or have passed with no reading since (read them on time, not in a batch)
  TO CLOSE     for each open iteration, the facts a close will need that it does not yet carry (a measured duration with its
               source, a deployment unit that deploys from it), stated before the close is attempted
It reads the register; it never writes, and needs nothing beside it but rdflib.

Usage:  backlog_session_brief_v1_0_0.py REGISTER.ttl LINEAGE_LOCAL_NAME [--days 7] [--vendored DIR --package DIR]
  --vendored DIR --package DIR   list every backlog_* tool in DIR that has a newer version in the package at --package
                                 (a vendored copy that nobody told the session was out of date)
"""
import argparse, datetime, glob, importlib.util, os, re, sys
from rdflib import Graph, Namespace, RDF

B = Namespace("http://example.org/backlog#")
HERE = os.path.dirname(os.path.abspath(__file__))


def local(x): return str(x).split("#")[-1]
def semver(p):
    m = re.findall(r"_v(\d+)_(\d+)_(\d+)\.", os.path.basename(p))
    return tuple(int(x) for x in m[0]) if m else (0, 0, 0)


def objective_status(g, obj):
    """The same reading the compass makes of an objective (latest observation against baseline and target), kept here so the
    brief works in a repository that vendors only the guard's tools; the compass is not needed beside it."""
    base, tgt, d = g.value(obj, B.hasBaselineValue), g.value(obj, B.hasTargetValue), g.value(obj, B.hasTargetDirection)
    best, best_at = None, None
    for o in g.subjects(B.observationFor, obj):
        at = g.value(o, B.observedAt)
        if at is not None and (best_at is None or at.toPython() > best_at): best, best_at = o, at.toPython()
    cur = g.value(best, B.hasObservedValue) if best is not None else None
    met, rem = False, None
    if cur is not None and tgt is not None and d is not None:
        c, t = float(cur), float(tgt)
        met = (c <= t) if local(d) == "Dir_Decrease" else (c >= t) if local(d) == "Dir_Increase" else (c == t)
    if cur is not None and base is not None and tgt is not None:
        den = abs(float(base) - float(tgt)); rem = abs(float(cur) - float(tgt)) / den if den > 0 else (0.0 if float(cur) == float(tgt) else 1.0)
    return {"achieved": met, "achievement_status": g.value(obj, B.hasAchievementStatus), "remaining_fraction": rem}


def lineage_of(g, name):
    return next((l for l in g.subjects(RDF.type, B.Lineage) if local(l) == name), None)


def brief(g, name, days=7, now=None, out=print):
    now = now or datetime.datetime.now(datetime.timezone.utc)
    L = lineage_of(g, name)
    if L is None:
        out(f"BRIEF  lineage {name} is not in the register"); return 1
    M = g.value(L, B.lineageForMission)
    rows = []
    if M is not None:
        for goal in g.subjects(B.contributesToMission, M):
            for obj in g.subjects(B.contributesToGoal, goal):
                rows.append((obj, objective_status(g, obj)))
    # FOCUS
    if not rows:
        out("FOCUS        no objective is modelled for this mission, so there is nothing to steer by")
    else:
        open_ = [(o, s) for o, s in rows if not s["achieved"] and s["achievement_status"] is None]
        ranked = sorted([(o, s) for o, s in open_ if s["remaining_fraction"] is not None], key=lambda r: -r[1]["remaining_fraction"])
        if not open_:
            out("FOCUS        every objective is at target or explained; the mission may be ready to close")
        elif ranked:
            o, s = ranked[0]
            out(f"FOCUS        {local(o)} ({round(100 * s['remaining_fraction'])}% of its gap still open); {len(open_)} of {len(rows)} objectives still block the mission")
        else:
            out(f"FOCUS        {len(open_)} objective(s) block the mission and none has a reading yet: take the first reading")
    # IN PROGRESS
    prog = sorted(local(i) for i in g.subjects(B.belongsToLineage, L) if (i, B.hasState, B.InProgress) in g and (i, RDF.type, B.Iteration) not in g)
    out("IN PROGRESS  " + (", ".join(prog[:8]) + (f" (+{len(prog) - 8} more)" if len(prog) > 8 else "") if prog else "nothing"))
    # DUE
    due = []
    for obj, _ in rows:
        reads = [g.value(o, B.observedAt) for o in g.subjects(B.observationFor, obj)]
        reads = [r.toPython() for r in reads if r is not None]
        for cp in g.objects(obj, B.hasCheckpoint):
            cd = g.value(cp, B.checkpointDate)
            if cd is None: continue
            d = cd.toPython()
            if d.tzinfo is None: d = d.replace(tzinfo=datetime.timezone.utc)
            covered = any((r if r.tzinfo else r.replace(tzinfo=datetime.timezone.utc)) >= d for r in reads)
            if not covered and d <= now + datetime.timedelta(days=days):
                due.append((d, local(obj), "overdue" if d < now else "due"))
    due.sort()
    out("DUE          " + ("; ".join(f"{o} {w} {d.date()}" for d, o, w in due[:8]) + (f" (+{len(due) - 8} more)" if len(due) > 8 else "") if due else f"no checkpoint falls due within {days} days"))
    # TO CLOSE
    lines = []
    for it in sorted(g.subjects(RDF.type, B.Iteration), key=local):
        if (it, B.belongsToLineage, L) not in g or (it, B.hasState, B.Done) in g or (it, B.hasState, B.Cancelled) in g: continue
        need = []
        if g.value(it, B.hasObservedDuration) is None: need.append("a measured duration")
        elif g.value(it, B.hasDurationSource) is None: need.append("the source of its duration")
        if not any(True for _ in g.subjects(B.deploysFrom, it)): need.append("a deployment unit that deploys from it")
        if need: lines.append(f"{local(it)} still needs " + " and ".join(need))
    out("TO CLOSE      " + ("; ".join(lines) if lines else "no open iteration is missing a fact its close will need"))
    return 0


def vendored(vend, pkg, out=print):
    pk = {}
    for p in glob.glob(os.path.join(pkg, "03-tooling", "*.py")) + glob.glob(os.path.join(pkg, "03-tooling", "*.sh")):
        n = re.sub(r"_v\d+_\d+_\d+\.", "_v.", os.path.basename(p))
        if semver(p) > pk.get(n, ((0, 0, 0), ""))[0]: pk[n] = (semver(p), os.path.basename(p))
    behind = []
    for p in glob.glob(os.path.join(vend, "*")):
        b = os.path.basename(p); n = re.sub(r"_v\d+_\d+_\d+\.", "_v.", b)
        if n in pk and pk[n][0] > semver(p): behind.append(f"{b} -> {pk[n][1]}")
    out("VENDORED     " + ("out of date: " + "; ".join(sorted(behind)) if behind else "every vendored tool is the newest the package ships"))
    return 1 if behind else 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("register", nargs="?"); ap.add_argument("lineage", nargs="?")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--vendored"); ap.add_argument("--package")
    a = ap.parse_args(argv)
    rc = 0
    if a.vendored and a.package: rc = vendored(a.vendored, a.package)
    if a.register and a.lineage:
        g = Graph()
        for t in sorted(glob.glob(os.path.join(os.path.dirname(HERE), "01-ontologies", "backlog_tbox_v*.ttl")), key=semver)[-1:]: g.parse(t)
        for t in sorted(glob.glob(os.path.join(os.path.dirname(HERE), "01-ontologies", "backlog_abox_v*.ttl")), key=semver)[-1:]: g.parse(t)
        g.parse(a.register)
        rc = max(rc, brief(g, a.lineage, a.days))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
