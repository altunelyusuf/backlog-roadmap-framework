#!/usr/bin/env python3
"""backlog_date_plan v1.5.0 -- predicts the measure dates of a lineage from its scope, its work and the velocity observed in earlier boxes (G186).

v1.5.0 (box 60, G246; IPage handover of 2026-11-16, point 3): `--sequential` reads the roadmap rank of a mover from the mover itself; when it has none, from the package it belongs to (memberOfContainer a Package that carries hasRoadmapRank); when it has none either, from the items it is decomposed into (partOf, decomposesInto), the lowest rank found. A mover with a rank of its own keeps it, and a mover with none of these still refuses, saying which mover and that its package was read too. Before: only a rank on the mover was read, so a register that ranks packages on the roadmap (as the framework's own planning does) was refused.

v1.4.0 (OE, another registrant and IPage handovers, 2026-11-16): the tool works on a register of any package. (1) The namespace of the forecasts is the one the register declares as `fw:`, else the namespace of the lineage's own IRI, and the forecast is linked to that register's root; it no longer stops on a register with no `fw:` prefix. (2) A mover that carries no effort but is decomposed (an epic) counts the open effort of its descendants (partOf, decomposesInto), each once. (3) A forecast of zero points while an open story pursues the objective is refused, never printed. (4) `--pace-from REGISTER` borrows the pace of another register, and the forecast says so. (5) `--sequential` adds the points of the objectives in the order of the roadmap rank of their open movers, so that sequential work is not forecast as if every objective started now. (6) `--effort` names the key the tool expects. (7) An open item with no effort and no stories under it makes the forecast refuse, never count as zero; under `--sequential` a story shared by objectives is counted once, and the forecast says its points are cumulative.
v1.3.0 (course-management handover, box-step-tool-stops-on-typed-effort-and-on-mixed-time-zones, 2026-11-12): a time without a zone (`"2026-09-24T14:35:00"^^xsd:dateTime`, valid Turtle) and a time with one cannot be compared in Python, so the sort of the iterations' starts stopped with a TypeError. `dt` now reads a time without a zone as UTC, says so here, and returns an aware time in every case; nothing in the register is rewritten.
v1.2.0 (book-ontology handover, box-step-tool-reads-only-the-framework-own-register-namespace, 2026-11-10): effort was read only from
hasEffort, which a register built on the validator's own cost-estimate vocabulary (hasEffortEstimate on a backlog:CostEstimate, reached by
hasCostEstimate) does not carry; it is now read through that fallback too (effort_of), wherever this tool reads a story's or an objective's
remaining points. The forecast's own forecastFor also assumed the register's root individual was named "Register"; it is now found by its
own marker, backlog:isRegisterRoot true (register_root), not assumed.

Usage:  backlog_date_plan.py REGISTER.ttl predict --lineage L_NAME [--prefix PD] [--now 2026-11-02T09:00:00Z] [--buffer 1.5] [--note TEXT] [--effort KEY=POINTS ...] [--pace-from REGISTER.ttl] [--sequential] [--emit FORECASTS.ttl]   (KEY is the objective name after its first underscore: Obj4_X_Rules takes X_Rules=POINTS)

For each objective of the lineage that has a checkpoint it prints: the points of work still to do on the stories that move it (metricMovableBy; Done, Cancelled, Rejected, Deferred and Withdrawn stories are not counted), the velocity (points DELIVERED, that is of stories Done, per elapsed hour, the
median over the pairs of consecutive boxes of the register, a box's elapsed time being the gap to the opening of the next), the expected completion (now + points / velocity, times the
buffer), and the earliest checkpoint date (the next midnight UTC after it, a proposal; the shape's floor is the expected completion itself). The assumptions are printed with it: this is the prediction to discuss before the dates are final.
--effort gives the planned points of an objective whose stories do not exist yet (the Objective stage of a lineage is written before its Backlog); it is used only for an objective that has no mover.
With --emit it writes one Forecast per objective and the link from the checkpoint to it; it exits 1 when a stated checkpoint date is earlier than the forecast expects.
The work is done by agents: the prediction is from effort and observed pace, not from a calendar of working days."""
import sys, os, re, datetime, statistics
from rdflib import Graph, URIRef, RDF, Literal
B = "http://example.org/backlog#"
def U(x): return URIRef(B + x)
def local(x): return str(x).rsplit("#", 1)[-1]
def dt(v):
    d = v.toPython() if v is not None else None
    if not isinstance(d, datetime.datetime): return None
    return d if d.tzinfo is not None else d.replace(tzinfo=datetime.timezone.utc)   # v1.3.0: no zone means UTC, so times with and without one compare

def effort_of(g, subject):
    """A story's (or other work item's) effort: hasEffort when present, otherwise hasEffortEstimate of the
    backlog:CostEstimate it hasCostEstimate (book-ontology handover, 2026-11-10) -- never zero merely because a
    register built on the validator's own cost-estimate vocabulary carries effort that way instead."""
    v = g.value(subject, U("hasEffort"))
    if v is not None: return float(v)
    ce = g.value(subject, U("hasCostEstimate"))
    if ce is not None:
        v2 = g.value(ce, U("hasEffortEstimate"))
        if v2 is not None: return float(v2)
    return 0.0

def open_effort(g, st, seen=None, unsized=None):
    """Open effort of a mover: its own effort when it has one, else the open effort of the items it is decomposed into (partOf, decomposesInto), each counted once (OE handover P9, 2026-11-05). An open item with no effort and no stories under it is added to `unsized`: it is a hole in the sum, never a zero."""
    seen = set() if seen is None else seen
    if st in seen: return 0.0
    seen.add(st)
    if local(g.value(st, U("hasState"))) in ("Done", "Cancelled", "Canceled", "Rejected", "Deferred", "Withdrawn"): return 0.0
    own = effort_of(g, st)
    if own > 0: return own
    kids = set(g.subjects(U("partOf"), st)) | set(g.objects(st, U("decomposesInto")))
    if not kids:
        if unsized is not None: unsized.append(st)
        return 0.0
    return sum(open_effort(g, k, seen, unsized) for k in sorted(kids, key=str))

def register_root(g):
    """The register's own root individual: found by its own marker, backlog:isRegisterRoot true, not assumed to be
    named "Register" (an adopting register may root itself under another name)."""
    for s in g.subjects(U("isRegisterRoot"), Literal(True)):
        return s
    return U("Register")

def samples(g, limit=10):
    its = []
    for it in g.subjects(RDF.type, U("Iteration")):
        s = dt(g.value(it, U("iterationStart")))
        if s: its.append((s, it))
    its.sort()
    out = []
    for (s, it), (s2, _) in zip(its, its[1:]):
        pts = sum(effort_of(g, st) for st in (g.value(ev, U("plansItem")) for ev in g.subjects(U("plannedInto"), it)) if st is not None and g.value(st, U("hasState")) == U("Done"))
        hrs = (s2 - s).total_seconds() / 3600.0
        if pts > 0 and hrs > 0: out.append(pts / hrs)
    return out[-limit:]

def expect(pts, vel, now, buffer):
    """The expected completion of pts points at vel points per hour, and the earliest checkpoint date (the day after it, at midnight UTC)."""
    done = now + datetime.timedelta(hours=(pts / vel) * buffer)
    date = (done.astimezone(datetime.timezone.utc) + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return done, date

def predict(g, lineage, now, buffer, effort=None, pace_graph=None, sequential=False):
    lin = [l for l in g.subjects(RDF.type, U("Lineage")) if local(l) == lineage]
    if not lin: raise SystemExit("ERROR: no Lineage named %s" % lineage)
    v = samples(pace_graph if pace_graph is not None else g)
    if not v: raise SystemExit("ERROR: no pair of consecutive boxes with effort in the register%s: there is no observed velocity to predict from" % (" given by --pace-from" if pace_graph is not None else " (name another register with --pace-from, or give --effort for an objective with no story yet)"))
    vel = statistics.median(v)
    rows = []; rows0 = []; used = set()
    for obj in sorted(g.subjects(U("belongsToLineage"), lin[0]), key=str):
        if (obj, RDF.type, U("Objective")) not in g: continue
        cps = sorted(g.objects(obj, U("hasCheckpoint")), key=str)
        if not cps: continue
        movers = sorted(g.objects(obj, U("metricMovableBy")), key=str); override = bool(effort and local(obj).split("_", 1)[-1] in effort and not movers)
        pts = 0.0; unsized = []; seen = set()
        for st in movers: pts += open_effort(g, st, seen, unsized)
        openers = [s for s in g.subjects(U("pursuesObjective"), obj) if local(g.value(s, U("hasState"))) not in ("Done", "Cancelled", "Canceled", "Rejected", "Deferred", "Withdrawn")]
        if unsized and not override:
            raise SystemExit("ERROR: %s has %d open item(s) with no effort and no stories under them (%s): the sum of points would leave them out; give them an effort" % (local(obj), len(unsized), ", ".join(local(x) for x in unsized[:3])))
        if pts == 0.0 and openers and not override:
            raise SystemExit("ERROR: %s would be forecast at 0 points, yet %d open item(s) pursue it and carry no effort: give them an effort, or the forecast says the work is finished when it is not" % (local(obj), len(openers)))
        if effort and local(obj).split("_", 1)[-1] in effort and not movers: pts = effort[local(obj).split("_", 1)[-1]]; used.add(local(obj).split("_", 1)[-1])
        rows0.append((obj, cps, pts, movers))
    if sequential:
        def item_rank(m, seen):
            if m in seen: return None
            seen.add(m)
            own = g.value(m, U("hasRoadmapRank"))
            if own is not None: return float(own)
            pk = [float(g.value(c, U("hasRoadmapRank"))) for c in g.objects(m, U("memberOfContainer")) if (c, RDF.type, U("Package")) in g and g.value(c, U("hasRoadmapRank")) is not None]
            if pk: return min(pk)
            kids = set(g.subjects(U("partOf"), m)) | set(g.objects(m, U("decomposesInto")))
            ks = [r for r in (item_rank(k, seen) for k in sorted(kids, key=str)) if r is not None]
            return min(ks) if ks else None
        def rank(o):
            rs = [r for r in (item_rank(m, set()) for m in g.objects(o, U("metricMovableBy"))) if r is not None]
            return min(rs) if rs else float("inf")
        order = sorted(rows0, key=lambda r: (rank(r[0]), str(r[0])))
        if any(rank(r[0]) == float("inf") and r[2] > 0 for r in order): raise SystemExit("ERROR: --sequential needs a roadmap rank (hasRoadmapRank) on a mover of every objective that still has work, or on the package the mover belongs to, or on the items it is decomposed into; none was found for some")
        acc = 0.0; cum = {}; seen = set()
        for r in order:
            acc += sum(open_effort(g, m, seen) for m in r[3]) if r[3] else r[2]; cum[r[0]] = acc
        rows0 = [(o, c, cum[o], m) for (o, c, p, m) in rows0]
    for obj, cps, pts, _m in rows0:
        done, date = expect(pts, vel, now, buffer)
        for cp in cps: rows.append((obj, cp, pts, done, date))
    bad = sorted(set(effort or {}) - used)
    if bad: raise SystemExit("ERROR: --effort names %s, which is not an objective of %s with a checkpoint and no mover (effort is only for an objective whose stories do not exist yet; the key is the objective's name after its first underscore, so Obj4_X_Rules takes X_Rules=POINTS)" % (", ".join(bad), lineage))
    return vel, len(v), rows

def add_effort(effort, arg):
    k, _, v = arg.partition("=")
    try: effort[k] = float(v)
    except ValueError: raise SystemExit("ERROR: --effort needs OBJECTIVE=POINTS, got %r" % arg)
    if not effort[k] > 0: raise SystemExit("ERROR: --effort points must be above zero, got %r" % arg)

def main(a):
    if len(a) < 4 or a[1] != "predict": print(__doc__); return 2
    lineage = prefix = emit = note = pace = None; seq = False; effort = {}; now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0); buf = 1.5; i = 2
    while i < len(a):
        if a[i] == "--lineage": lineage = a[i + 1]
        elif a[i] == "--prefix": prefix = a[i + 1]
        elif a[i] == "--now": now = datetime.datetime.fromisoformat(a[i + 1].replace("Z", "+00:00"))
        elif a[i] == "--buffer": buf = float(a[i + 1])
        elif a[i] == "--emit": emit = a[i + 1]
        elif a[i] == "--note": note = a[i + 1]
        elif a[i] == "--effort": add_effort(effort, a[i + 1])
        elif a[i] == "--pace-from": pace = a[i + 1]
        elif a[i] == "--sequential": seq = True; i -= 1
        else: print(__doc__); return 2
        i += 2
    g = Graph(); g.parse(a[0], format="turtle")
    pg = None
    if pace: pg = Graph(); pg.parse(pace, format="turtle")
    extra = []
    if pace: extra.append("The pace is borrowed from %s, not observed in this register." % os.path.basename(pace))
    if seq: extra.append("The points are cumulative in roadmap order (each objective carries the points of those before it; a story shared by objectives is counted once).")
    if note: extra.append(note)
    note = " ".join(extra) if extra else None
    vel, n, rows = predict(g, lineage, now, buf, effort, pg, seq)
    print("== Date plan of %s, made %s ==" % (lineage, now.strftime("%Y-%m-%dT%H:%M:%SZ")))
    print("assumptions: the agents keep the pace observed in %d pair(s) of consecutive boxes (%.2f delivered points per elapsed hour, median); the remaining points are those of the stories that move the objective and are not Done; the buffer is x%g; a box's elapsed time includes its release." % (n, vel, buf))
    if note: print("note: " + note)
    late = 0; ttl = ["@prefix backlog: <%s> ." % B, "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> ."]
    txt = open(a[0], encoding="utf-8").read(); fw = re.search(r"@prefix fw: <([^>]+)>", txt)
    lin0 = [l for l in g.subjects(RDF.type, U("Lineage")) if local(l) == lineage][0]
    ns = fw.group(1) if fw else (str(lin0).rsplit("#", 1)[0] + "#" if "#" in str(lin0) else str(lin0).rsplit("/", 1)[0] + "/")
    ttl.append("@prefix fw: <%s> ." % ns)
    root = local(register_root(g))
    for obj, cp, pts, done, date in rows:
        stated = dt(g.value(cp, U("checkpointDate")))
        flag = "" if stated is None or stated >= done else "  STATED DATE IS EARLIER THAN FORECAST"
        late += bool(flag)
        print("  %-26s %5.1f points  expected %s  earliest checkpoint %s  stated %s%s" % (local(obj).replace("Obj_", ""), pts, done.strftime("%Y-%m-%d %H:%MZ"), date.strftime("%Y-%m-%d"), stated.strftime("%Y-%m-%d") if stated else "none", flag))
        if emit:
            k = "Fc_%s_%s" % (prefix, local(cp).split("_", 2)[-1])
            ttl.append("fw:%s a backlog:Forecast ; backlog:forecastFor fw:%s ; backlog:forecastMadeAt \"%s\"^^xsd:dateTime ; backlog:forecastCompletion \"%s\"^^xsd:dateTime ;\n    backlog:forecastAssumption \"The agents keep the pace observed in %d pair(s) of consecutive boxes: %.2f points per elapsed hour (median); %.1f points remain on the stories that move the objective; buffer x%g.%s\" ;\n    backlog:forecastObservedVelocity \"%.2f\"^^xsd:decimal ; backlog:forecastIterationsObserved %d ." % (k, root, now.strftime("%Y-%m-%dT%H:%M:%SZ"), done.strftime("%Y-%m-%dT%H:%M:%SZ"), n, vel, pts, buf, (" " + note) if note else "", vel, n))
            ttl.append("fw:%s backlog:datePredictedBy fw:%s ." % (local(cp), k))
    if emit: open(emit, "w", encoding="utf-8").write("\n".join(ttl) + "\n"); print("forecasts written to %s" % emit)
    return 1 if late else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
