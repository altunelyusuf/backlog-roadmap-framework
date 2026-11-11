#!/usr/bin/env python3
"""backlog_date_plan v1.2.0 -- predicts the measure dates of a lineage from its scope, its work and the velocity observed in earlier boxes (G186).

v1.2.0 (book-ontology handover, box-step-tool-reads-only-the-framework-own-register-namespace, 2026-11-10): effort was read only from
hasEffort, which a register built on the validator's own cost-estimate vocabulary (hasEffortEstimate on a backlog:CostEstimate, reached by
hasCostEstimate) does not carry; it is now read through that fallback too (effort_of), wherever this tool reads a story's or an objective's
remaining points. The forecast's own forecastFor also assumed the register's root individual was named "Register"; it is now found by its
own marker, backlog:isRegisterRoot true (register_root), not assumed.

Usage:  backlog_date_plan.py REGISTER.ttl predict --lineage L_NAME [--prefix PD] [--now 2026-11-02T09:00:00Z] [--buffer 1.5] [--note TEXT] [--effort OBJECTIVE=POINTS ...] [--emit FORECASTS.ttl]

For each objective of the lineage that has a checkpoint it prints: the points of work still to do on the stories that move it (metricMovableBy; Done, Cancelled, Rejected, Deferred and Withdrawn stories are not counted), the velocity (points DELIVERED, that is of stories Done, per elapsed hour, the
median over the pairs of consecutive boxes of the register, a box's elapsed time being the gap to the opening of the next), the expected completion (now + points / velocity, times the
buffer), and the earliest checkpoint date (the next midnight UTC after it, a proposal; the shape's floor is the expected completion itself). The assumptions are printed with it: this is the prediction to discuss before the dates are final.
--effort gives the planned points of an objective whose stories do not exist yet (the Objective stage of a lineage is written before its Backlog); it is used only for an objective that has no mover.
With --emit it writes one Forecast per objective and the link from the checkpoint to it; it exits 1 when a stated checkpoint date is earlier than the forecast expects.
The work is done by agents: the prediction is from effort and observed pace, not from a calendar of working days."""
import sys, re, datetime, statistics
from rdflib import Graph, URIRef, RDF, Literal
B = "http://example.org/backlog#"
def U(x): return URIRef(B + x)
def local(x): return str(x).rsplit("#", 1)[-1]
def dt(v):
    d = v.toPython() if v is not None else None
    return d if isinstance(d, datetime.datetime) else None

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

def predict(g, lineage, now, buffer, effort=None):
    lin = [l for l in g.subjects(RDF.type, U("Lineage")) if local(l) == lineage]
    if not lin: raise SystemExit("ERROR: no Lineage named %s" % lineage)
    v = samples(g)
    if not v: raise SystemExit("ERROR: no pair of consecutive boxes with effort in the register: there is no observed velocity to predict from")
    vel = statistics.median(v)
    rows = []; used = set()
    for obj in sorted(g.subjects(U("belongsToLineage"), lin[0]), key=str):
        if (obj, RDF.type, U("Objective")) not in g: continue
        cps = sorted(g.objects(obj, U("hasCheckpoint")), key=str)
        if not cps: continue
        pts = 0.0
        for st in g.objects(obj, U("metricMovableBy")):
            if local(g.value(st, U("hasState"))) not in ("Done", "Cancelled", "Canceled", "Rejected", "Deferred", "Withdrawn"): pts += effort_of(g, st)
        if effort and local(obj).split("_", 1)[-1] in effort and not list(g.objects(obj, U("metricMovableBy"))): pts = effort[local(obj).split("_", 1)[-1]]; used.add(local(obj).split("_", 1)[-1])
        done, date = expect(pts, vel, now, buffer)
        for cp in cps: rows.append((obj, cp, pts, done, date))
    bad = sorted(set(effort or {}) - used)
    if bad: raise SystemExit("ERROR: --effort names %s, which is not an objective of %s with a checkpoint and no mover (effort is only for an objective whose stories do not exist yet)" % (", ".join(bad), lineage))
    return vel, len(v), rows

def add_effort(effort, arg):
    k, _, v = arg.partition("=")
    try: effort[k] = float(v)
    except ValueError: raise SystemExit("ERROR: --effort needs OBJECTIVE=POINTS, got %r" % arg)
    if not effort[k] > 0: raise SystemExit("ERROR: --effort points must be above zero, got %r" % arg)

def main(a):
    if len(a) < 4 or a[1] != "predict": print(__doc__); return 2
    lineage = prefix = emit = note = None; effort = {}; now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0); buf = 1.5; i = 2
    while i < len(a):
        if a[i] == "--lineage": lineage = a[i + 1]
        elif a[i] == "--prefix": prefix = a[i + 1]
        elif a[i] == "--now": now = datetime.datetime.fromisoformat(a[i + 1].replace("Z", "+00:00"))
        elif a[i] == "--buffer": buf = float(a[i + 1])
        elif a[i] == "--emit": emit = a[i + 1]
        elif a[i] == "--note": note = a[i + 1]
        elif a[i] == "--effort": add_effort(effort, a[i + 1])
        else: print(__doc__); return 2
        i += 2
    g = Graph(); g.parse(a[0], format="turtle")
    vel, n, rows = predict(g, lineage, now, buf, effort)
    print("== Date plan of %s, made %s ==" % (lineage, now.strftime("%Y-%m-%dT%H:%M:%SZ")))
    print("assumptions: the agents keep the pace observed in %d pair(s) of consecutive boxes (%.2f delivered points per elapsed hour, median); the remaining points are those of the stories that move the objective and are not Done; the buffer is x%g; a box's elapsed time includes its release." % (n, vel, buf))
    late = 0; ttl = ["@prefix backlog: <%s> ." % B, "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> ."]
    fw = re.search(r"@prefix fw: <([^>]+)>", open(a[0], encoding="utf-8").read()); ttl.append("@prefix fw: <%s> ." % fw.group(1))
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
