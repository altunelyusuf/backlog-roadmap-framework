#!/usr/bin/env python3
"""backlog_date_report v1.2.0 -- the base, updated and finished dates of a lineage's objectives, and the plan of each box against what happened (G188).

Usage:  backlog_date_report.py REGISTER.ttl --lineage L_NAME [--strict] [--now 2026-11-02T12:00:00Z]

For each objective with a checkpoint it prints
  base      the date stated at planning (checkpointDate), with the completion its forecast expected;
  updated   derived, never stored: the latest end among the boxes that hold the stories that move the objective (metricMovableBy) -- the end of a finished box, the planned end of an open one
            (its current base plan); stories that move it and are in no box are counted, and have no date;
  finished  the first reading of the unbroken run, ending at the latest reading, in which the objective stood at its target (a decrease reaches it or less, an increase reaches it or more); a hold is dated by its latest reading when that equals the target; 'open' when the latest reading does not stand at the target;
  and the variances, in hours, of updated and finished against the base.
For each box of the lineage it prints the base plan (start, end), the actual end of a finished box and the variance in hours. The base of an objective with several checkpoints is the earliest. A date later than its base is marked LATE; an open box whose planned end has passed is marked PAST PLAN; a mover in a box with no end and no base plan is counted and undated. All times are UTC.
v1.2.0 (Lineage 29, story DatesReport): a value that is not a date (a text, a wrong datatype) or not a number is named in a closing section "Malformed input" and the report goes on without it, where v1.1.0 stopped with a TypeError (comparing a date with nothing); about 130 malformed variants of the date and number fields were tried in review and none stops it now; with --strict the exit code is 1 also when anything is malformed.
v1.1.0 (G191): after the boxes it names, for each box that is LATE or PAST PLAN, the impediments of the lineage that stood open while the box ran (raised before its actual end or now, resolved after its actual start, or the planned start when no actual one is recorded; only impediments that name the lineage are counted), with their kind and hours open.
With --strict the exit code is 1 when anything is LATE. Nothing is written."""
import sys, datetime
from rdflib import Graph, URIRef, RDF
B = "http://example.org/backlog#"
U = lambda x: URIRef(B + x)
local = lambda x: str(x).rsplit("#", 1)[-1]

MAL = []
def dt(v):
    d = v.toPython() if v is not None else None
    if v is not None and not isinstance(d, (datetime.datetime, datetime.date)) and str(v) not in MAL:
        MAL.append(str(v))
    if isinstance(d, datetime.datetime):
        try:
            return (d if d.tzinfo else d.replace(tzinfo=datetime.timezone.utc)).astimezone(datetime.timezone.utc)
        except (OverflowError, ValueError):        # a date outside the calendar once moved to UTC is not a usable date
            if str(v) not in MAL: MAL.append(str(v))
            return None
    if isinstance(d, datetime.date):  # a date alone is midnight UTC
        return datetime.datetime(d.year, d.month, d.day, tzinfo=datetime.timezone.utc)
    return None

def fmt(d): return d.strftime("%Y-%m-%d %H:%MZ") if d else "-"
def var(a, b): return "%+.1f h" % ((a - b).total_seconds() / 3600.0) if a and b else "-"

def box_of(g, st):
    return [g.value(ev, U("plannedInto")) for ev in g.subjects(U("plansItem"), st) if g.value(ev, U("plannedInto")) is not None]

def baseline(g, it):
    for b in g.subjects(U("baselineFor"), it):
        if str(g.value(b, U("isCurrentBaseline"))).lower() == "true":
            return dt(g.value(b, U("hasBaselineStart"))), dt(g.value(b, U("hasBaselineEnd")))
    return None, None

def box_end(g, it):
    if g.value(it, U("hasState")) == U("Done") and g.value(it, U("iterationEnd")) is not None:
        return dt(g.value(it, U("iterationEnd")))
    return baseline(g, it)[1]

def reached(g, obj):
    tv = g.value(obj, U("hasTargetValue")); dr = local(g.value(obj, U("hasTargetDirection")) or "")
    if tv is None: return None
    try: tv = float(tv)
    except ValueError: MAL.append(str(tv)); return None
    allobs = []
    for ob in g.subjects(U("observationFor"), obj):
        v = g.value(ob, U("hasObservedValue")); t = dt(g.value(ob, U("observedAt")))
        try: fv = float(v) if v is not None else None
        except ValueError: fv = None; MAL.append(str(v))
        if fv is not None and t is not None: allobs.append((t, fv))
    allobs.sort()
    ok = lambda v: (v <= tv) if dr.endswith("Decrease") else ((v >= tv) if dr.endswith("Increase") else (v == tv))
    if not allobs or not ok(allobs[-1][1]): return None  # the latest reading must stand at the target
    if dr.endswith("Hold"): return allobs[-1][0]  # a hold is dated by its latest reading
    i = len(allobs) - 1
    while i > 0 and ok(allobs[i - 1][1]): i -= 1
    return allobs[i][0]  # a decrease or an increase: the first reading of the unbroken run that ends at the latest

def main(a):
    if len(a) < 3 or "--lineage" not in a: print(__doc__); return 2
    g = Graph(); g.parse(a[0], format="turtle")
    lname = a[a.index("--lineage") + 1]
    lin = [l for l in g.subjects(RDF.type, U("Lineage")) if local(l) == lname]
    if not lin: print("ERROR: no Lineage named %s" % lname); return 2
    late = 0
    now = datetime.datetime.fromisoformat(a[a.index("--now") + 1].replace("Z", "+00:00")) if "--now" in a else datetime.datetime.now(datetime.timezone.utc)
    print("== Dates of %s ==" % lname)
    for obj in sorted(g.subjects(U("belongsToLineage"), lin[0]), key=str):
        if (obj, RDF.type, U("Objective")) not in g: continue
        cps = sorted(g.objects(obj, U("hasCheckpoint")), key=str)
        if not cps: continue
        bds = [x for x in (dt(g.value(c, U("checkpointDate"))) for c in cps if g.value(c, U("checkpointDate")) is not None) if x is not None]
        base = min(bds) if bds else None
        fcs = [x for x in (dt(g.value(g.value(c, U("datePredictedBy")), U("forecastCompletion"))) for c in cps if g.value(c, U("datePredictedBy")) is not None) if x is not None]
        ends, unplanned, noend = [], 0, 0
        for st in g.objects(obj, U("metricMovableBy")):
            bs = box_of(g, st)
            if not bs: unplanned += 1; continue
            es = [e for e in (box_end(g, i) for i in bs) if e]
            if not es: noend += 1
            ends += es
        upd = max(ends) if ends else None
        fin = reached(g, obj)
        flag = " LATE" if (upd and base and upd > base) or (fin and base and fin > base) else ""
        late += bool(flag)
        notes = (("  [%d mover(s) in no box]" % unplanned) if unplanned else "") + (("  [%d mover(s) in a box with no end]" % noend) if noend else "")
        print("  %-28s base %s (forecast %s)  updated %s %s  finished %s %s%s%s" % (local(obj), fmt(base), fmt(min(fcs) if fcs else None), fmt(upd), var(upd, base), fmt(fin) if fin else "open", var(fin, base) if fin else "", notes, flag))
    print("== Boxes ==")
    late_boxes = []
    for it in sorted(g.subjects(U("belongsToLineage"), lin[0]), key=str):
        if (it, RDF.type, U("Iteration")) not in g: continue
        s, e = baseline(g, it)
        act = dt(g.value(it, U("iterationEnd"))) if g.value(it, U("hasState")) == U("Done") else None
        flag = " LATE" if (e and act and act > e) else (" PAST PLAN" if (e and not act and e < now) else "")
        late += bool(flag)
        if flag:
            st = dt(g.value(it, U("iterationStart"))) if g.value(it, U("iterationStart")) is not None else s
            late_boxes.append((local(it), st, act or now))
        print("  %-14s plan %s -> %s   actual end %s %s%s%s" % (local(it), fmt(s), fmt(e), fmt(act) if act else "open", var(act, e) if act else "", "" if e else "  [no base plan]", flag))
    print("== Obstacles that stood in a late box ==")
    found = 0
    for name, st, en in late_boxes:
        if st is None: print("  %-14s [the box has no start, so no impediment can be placed in it]" % name); found += 1; continue
        for im in sorted(g.subjects(U("belongsToLineage"), lin[0]), key=str):
            if (im, RDF.type, U("Impediment")) not in g or g.value(im, U("raisedAt")) is None: continue
            r, res = dt(g.value(im, U("raisedAt"))), (dt(g.value(im, U("resolvedAt"))) if g.value(im, U("resolvedAt")) is not None else None)
            if r is None: continue
            if r < en and (res is None or res > st):
                k = g.value(im, U("hasImpedimentKind"))
                print("  %-14s %s: %s, %s" % (name, local(im), local(k) if k is not None else "no kind", ("open %.1f h" % ((now - r).total_seconds() / 3600.0)) if res is None else ("%.1f h, resolved %s" % ((res - r).total_seconds() / 3600.0, fmt(res)))))
                found += 1
    if not found: print("  none" if late_boxes else "  no late box")
    print("== Malformed input ==")
    for m in MAL: print("  not a date or number: %r" % m)
    if not MAL: print("  none")
    print("late: %d" % late)
    return 1 if ((late or MAL) and "--strict" in a) else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
