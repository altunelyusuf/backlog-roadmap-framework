#!/usr/bin/env python3
"""backlog_date_plan v1.0.0 -- predicts the measure dates of a lineage from its scope, its work and the velocity observed in earlier boxes (G186).

Usage:  backlog_date_plan.py REGISTER.ttl predict --lineage L_NAME [--prefix PD] [--now 2026-11-02T09:00:00Z] [--buffer 1.5] [--note TEXT] [--emit FORECASTS.ttl]

For each objective of the lineage that has a checkpoint it prints: the points of work still to do on the stories that move it (metricMovableBy; Done, Cancelled, Rejected, Deferred and Withdrawn stories are not counted), the velocity (points DELIVERED, that is of stories Done, per elapsed hour, the
median over the pairs of consecutive boxes of the register, a box's elapsed time being the gap to the opening of the next), the expected completion (now + points / velocity, times the
buffer), and the earliest checkpoint date (the next midnight UTC after it, a proposal; the shape's floor is the expected completion itself). The assumptions are printed with it: this is the prediction to discuss before the dates are final.
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

def samples(g, limit=10):
    its = []
    for it in g.subjects(RDF.type, U("Iteration")):
        s = dt(g.value(it, U("iterationStart")))
        if s: its.append((s, it))
    its.sort()
    out = []
    for (s, it), (s2, _) in zip(its, its[1:]):
        pts = sum(float(g.value(st, U("hasEffort")) or 0) for st in (g.value(ev, U("plansItem")) for ev in g.subjects(U("plannedInto"), it)) if st is not None and g.value(st, U("hasState")) == U("Done"))
        hrs = (s2 - s).total_seconds() / 3600.0
        if pts > 0 and hrs > 0: out.append(pts / hrs)
    return out[-limit:]

def predict(g, lineage, now, buffer):
    lin = [l for l in g.subjects(RDF.type, U("Lineage")) if local(l) == lineage]
    if not lin: raise SystemExit("ERROR: no Lineage named %s" % lineage)
    v = samples(g)
    if not v: raise SystemExit("ERROR: no pair of consecutive boxes with effort in the register: there is no observed velocity to predict from")
    vel = statistics.median(v)
    rows = []
    for obj in sorted(g.subjects(U("belongsToLineage"), lin[0]), key=str):
        if (obj, RDF.type, U("Objective")) not in g: continue
        cps = sorted(g.objects(obj, U("hasCheckpoint")), key=str)
        if not cps: continue
        pts = 0.0
        for st in g.objects(obj, U("metricMovableBy")):
            if local(g.value(st, U("hasState"))) not in ("Done", "Cancelled", "Canceled", "Rejected", "Deferred", "Withdrawn"): pts += float(g.value(st, U("hasEffort")) or 0)
        done = now + datetime.timedelta(hours=(pts / vel) * buffer)
        date = (done.astimezone(datetime.timezone.utc) + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        for cp in cps: rows.append((obj, cp, pts, done, date))
    return vel, len(v), rows

def main(a):
    if len(a) < 4 or a[1] != "predict": print(__doc__); return 2
    lineage = prefix = emit = note = None; now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0); buf = 1.5; i = 2
    while i < len(a):
        if a[i] == "--lineage": lineage = a[i + 1]
        elif a[i] == "--prefix": prefix = a[i + 1]
        elif a[i] == "--now": now = datetime.datetime.fromisoformat(a[i + 1].replace("Z", "+00:00"))
        elif a[i] == "--buffer": buf = float(a[i + 1])
        elif a[i] == "--emit": emit = a[i + 1]
        elif a[i] == "--note": note = a[i + 1]
        else: print(__doc__); return 2
        i += 2
    g = Graph(); g.parse(a[0], format="turtle")
    vel, n, rows = predict(g, lineage, now, buf)
    print("== Date plan of %s, made %s ==" % (lineage, now.strftime("%Y-%m-%dT%H:%M:%SZ")))
    print("assumptions: the agents keep the pace observed in %d pair(s) of consecutive boxes (%.2f delivered points per elapsed hour, median); the remaining points are those of the stories that move the objective and are not Done; the buffer is x%g; a box's elapsed time includes its release." % (n, vel, buf))
    late = 0; ttl = ["@prefix backlog: <%s> ." % B, "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> ."]
    fw = re.search(r"@prefix fw: <([^>]+)>", open(a[0], encoding="utf-8").read()); ttl.append("@prefix fw: <%s> ." % fw.group(1))
    for obj, cp, pts, done, date in rows:
        stated = dt(g.value(cp, U("checkpointDate")))
        flag = "" if stated is None or stated >= done else "  STATED DATE IS EARLIER THAN FORECAST"
        late += bool(flag)
        print("  %-26s %5.1f points  expected %s  earliest checkpoint %s  stated %s%s" % (local(obj).replace("Obj_", ""), pts, done.strftime("%Y-%m-%d %H:%MZ"), date.strftime("%Y-%m-%d"), stated.strftime("%Y-%m-%d") if stated else "none", flag))
        if emit:
            k = "Fc_%s_%s" % (prefix, local(cp).split("_", 2)[-1])
            ttl.append("fw:%s a backlog:Forecast ; backlog:forecastFor fw:Register ; backlog:forecastMadeAt \"%s\"^^xsd:dateTime ; backlog:forecastCompletion \"%s\"^^xsd:dateTime ;\n    backlog:forecastAssumption \"The agents keep the pace observed in %d pair(s) of consecutive boxes: %.2f points per elapsed hour (median); %.1f points remain on the stories that move the objective; buffer x%g.%s\" ;\n    backlog:forecastObservedVelocity \"%.2f\"^^xsd:decimal ; backlog:forecastIterationsObserved %d ." % (k, now.strftime("%Y-%m-%dT%H:%M:%SZ"), done.strftime("%Y-%m-%dT%H:%M:%SZ"), n, vel, pts, buf, (" " + note) if note else "", vel, n))
            ttl.append("fw:%s backlog:datePredictedBy fw:%s ." % (local(cp), k))
    if emit: open(emit, "w", encoding="utf-8").write("\n".join(ttl) + "\n"); print("forecasts written to %s" % emit)
    return 1 if late else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
