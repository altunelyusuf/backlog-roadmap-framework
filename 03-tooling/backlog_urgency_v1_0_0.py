#!/usr/bin/env python3
"""backlog_urgency v1.0.0 -- the urgent-interruption ceremony as one recorded step each (G158).

  declare   The Owner stops a running lineage for an emergency. One step: the UrgentInterruption record; every started item of the lineage
            moved to Suspended with a rationale and a recorded move; the held items named; the urgent items named. Stamped from the clock.
  resolve   The emergency is over: refused unless every urgent item is Done or Cancelled.
  resume    The lineage goes back to work: refused unless the emergency is resolved and an impact assessment exists (or is given with
            --impact); every held item moves back to In Progress with a recorded move.
  status    Open interruptions, their time box and held items. Exit 2 when one is past its time box.

The tool appends text to the register and changes the state of the items it holds; nothing else. The register is then validated as usual.
Usage: backlog_urgency.py declare REGISTER --lineage IRI --reason TEXT --until ISO --urgent IRI [--urgent IRI ...] [--executor IRI]
       backlog_urgency.py resolve REGISTER --interruption IRI
       backlog_urgency.py resume  REGISTER --interruption IRI [--impact TEXT] [--executor IRI]
       backlog_urgency.py status  REGISTER
"""
import argparse, datetime, re, sys
import rdflib
from rdflib import URIRef, Literal, Namespace, RDF
from rdflib.namespace import XSD
B = Namespace("http://example.org/backlog#")
# the ranks of the lineage statuses (backlog_abox LS_*), used when the register does not carry the framework's own individuals
RANKS = {"LS_Opened": 1, "LS_Scoped": 2, "LS_Goaled": 3, "LS_Objectived": 4, "LS_Backlogged": 5, "LS_InProgress": 6, "LS_Revived": 6,
         "LS_Achieved": 7, "LS_Abandoned": 7, "LS_Archived": 8}
def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def load(path):
    g = rdflib.Graph(); g.parse(path, format="turtle"); return g
def lit(t): return f'"{t}"^^<http://www.w3.org/2001/XMLSchema#dateTime>'
def esc(t): return t.replace("\\", "\\\\").replace('"', '\\"')
def lineage_items(g, lin):
    s = set(g.subjects(B.belongsToLineage, lin))
    for o in g.subjects(B.belongsToLineage, lin):
        s |= set(g.subjects(B.admittedByOutput, o))
    return {i for i in s if (i, B.hasState, None) in g}
def state(g, i):
    return next(g.objects(i, B.hasState), None)
def block_state(path, iri, old, new):
    s = open(path).read(); g = load(path)
    # find the subject statement in the text by either its prefixed name or its full IRI
    names = {f"<{iri}>"} | {f"{p}:{str(iri)[len(str(n)):]}" for p, n in g.namespaces() if str(iri).startswith(str(n)) and str(n)}
    for nm in names:
        m = re.search(r'^%s a [^\n]*\n(?:(?!^\S)[^\n]*\n)*' % re.escape(nm), s, re.M)
        if m:
            blk = m.group(0)
            nb, k = re.subn(r'backlog:hasState backlog:%s' % old, 'backlog:hasState backlog:%s' % new, blk, count=1)
            if k != 1: sys.exit(f"cannot change state of {iri}: its record has no 'hasState {old}' in the text")
            open(path, "w").write(s[:m.start()] + nb + s[m.end():]); return
    sys.exit(f"cannot find the statement of {iri} in {path}")
def add_rationale(path, iri, text):
    s = open(path).read(); g = load(path)
    names = {f"<{iri}>"} | {f"{p}:{str(iri)[len(str(n)):]}" for p, n in g.namespaces() if str(iri).startswith(str(n)) and str(n)}
    for nm in names:
        m = re.search(r'^%s a [^\n]*\n(?:(?!^\S)[^\n]*\n)*' % re.escape(nm), s, re.M)
        if m:
            blk = m.group(0).rstrip("\n"); assert blk.endswith("."), iri
            nb = blk[:-1].rstrip() + f' ;\n    backlog:hasRationale "{esc(text)}" .\n'
            open(path, "w").write(s[:m.start()] + nb + s[m.end():]); return
    sys.exit(f"cannot find the statement of {iri}")
def append(path, text):
    with open(path, "a") as f: f.write("\n" + text.strip("\n") + "\n")
def move(n, item, via, at, note, executor):
    ex = f" ; backlog:transitionedByExecutor <{executor}>" if executor else ""
    return (f'<{n}> a backlog:TransitionEvent ; backlog:transitionedItem <{item}> ; backlog:viaTransition backlog:{via} ; '
            f'backlog:transitionedAt {lit(at)} ; backlog:transitionedBy backlog:Owner{ex} ; backlog:hasTransitionNote "{esc(note)}" .')
def prefixes(path):
    return "" if any(l.startswith("@prefix backlog:") for l in open(path)) else "@prefix backlog: <http://example.org/backlog#> .\n"
def open_ones(g):
    return [u for u in g.subjects(RDF.type, B.UrgentInterruption) if (u, B.urgencyResumedAt, None) not in g]
def declare(a):
    g = load(a.register); lin = URIRef(a.lineage)
    if (lin, RDF.type, B.Lineage) not in g: sys.exit("not a lineage in this register: " + a.lineage)
    for u in open_ones(g):
        if (u, B.interruptsLineage, lin) in g: sys.exit("this lineage already has an open interruption: " + str(u) + " (add the urgent work to it)")
    st = next(g.objects(lin, B.hasLineageStatus), None)
    rk = next(g.objects(st, B.statusRank), None) if st else None
    if st is not None and rk is None: rk = RANKS.get(str(st).rsplit("#", 1)[-1])
    if rk is None or not 2 <= int(rk) <= 6: sys.exit("the lineage is not running (status rank must be 2 to 6); nothing to pause")
    urgent = {URIRef(u) for u in a.urgent}
    for u in urgent:
        if (u, B.hasState, None) not in g: sys.exit("the urgent item is not in the register (record it first): " + str(u))
    until = a.until if a.until.endswith("Z") else a.until + "Z"
    t = now()
    if until <= t: sys.exit("the time box must end after now (" + t + ")")
    held = sorted(i for i in lineage_items(g, lin) if state(g, i) == B.InProgress and i not in urgent)
    ns = str(lin).rsplit("#", 1)[0] + "#" if "#" in str(lin) else str(lin).rsplit("/", 1)[0] + "/"
    n = sum(1 for _ in g.subjects(RDF.type, B.UrgentInterruption)) + 1
    uid = f"{ns}Urgent_{n}"
    out = [prefixes(a.register) + f'<{uid}> a backlog:UrgentInterruption ; rdfs:label "Urgent interruption {n}"@en ; backlog:interruptsLineage <{lin}> ; backlog:decidedBy backlog:Owner ;\n'
           f'    backlog:urgencyDeclaredAt {lit(t)} ; backlog:urgencyReason "{esc(a.reason)}" ; backlog:urgencyTimeBoxUntil {lit(until)}']
    for u in sorted(urgent): out[0] += f' ;\n    backlog:urgentItem <{u}>'
    for h in held: out[0] += f' ;\n    backlog:holdsItem <{h}>'
    out[0] += " ."
    for k, h in enumerate(held):
        out.append(move(f"{uid}_Hold_{k+1}", h, "T_Suspend", t, "paused by the urgent interruption: " + a.reason, a.executor))
    append(a.register, "\n".join(out))
    for h in held:
        block_state(a.register, h, "InProgress", "Suspended"); add_rationale(a.register, h, "paused by the urgent interruption " + uid + ": " + a.reason)
    print(f"declared {uid}: {len(held)} item(s) held (Suspended), {len(urgent)} urgent item(s), time box until {until}")
def resolve(a):
    g = load(a.register); u = URIRef(a.interruption)
    if (u, RDF.type, B.UrgentInterruption) not in g: sys.exit("no such interruption")
    bad = [str(i) for i in g.objects(u, B.urgentItem) if state(g, i) not in (B.Done, B.Cancelled)]
    if bad: sys.exit("not resolved: urgent item(s) still open: " + ", ".join(bad))
    t = now(); append(a.register, prefixes(a.register) + f'<{u}> backlog:urgencyResolvedAt {lit(t)} .')
    print("resolved at", t)
def resume(a):
    g = load(a.register); u = URIRef(a.interruption)
    if (u, RDF.type, B.UrgentInterruption) not in g: sys.exit("no such interruption")
    if (u, B.urgencyResolvedAt, None) not in g: sys.exit("resolve the emergency first")
    t = now(); lin = next(g.objects(u, B.interruptsLineage))
    assessed = (None, B.assessesInterruption, u) in g
    if not assessed and not a.impact: sys.exit("no impact assessment: give --impact TEXT (what slipped, what was re-prioritised, what the pause cost)")
    out = []
    if not assessed:
        out.append(prefixes(a.register) + f'<{u}_Impact> a backlog:ImpactAssessment ; backlog:assessesInterruption <{u}> ; backlog:identifiesAffectedLineage <{lin}> ; backlog:hasImpactStatement "{esc(a.impact)}" .')
    held = sorted(i for i in g.objects(u, B.holdsItem) if state(g, i) == B.Suspended)
    for k, h in enumerate(held): out.append(move(f"{u}_Back_{k+1}", h, "T_Resume", t, "resumed after the urgent interruption", a.executor))
    out.append(f'<{u}> backlog:urgencyResumedAt {lit(t)} .')
    append(a.register, "\n".join(out))
    for h in held: block_state(a.register, h, "Suspended", "InProgress")
    print(f"resumed at {t}: {len(held)} item(s) moved back to In Progress")
def status(a):
    g = load(a.register); late = False; ops = open_ones(g)
    for u in ops:
        box = str(next(g.objects(u, B.urgencyTimeBoxUntil), "")); over = box and box < now()
        late |= bool(over)
        print(f"{u}  lineage {next(g.objects(u, B.interruptsLineage), '?')}  held {len(list(g.objects(u, B.holdsItem)))}  urgent {len(list(g.objects(u, B.urgentItem)))}  until {box}{'  PAST TIME BOX' if over else ''}")
    if not ops: print("no open urgent interruption")
    sys.exit(2 if late else 0)
def main():
    p = argparse.ArgumentParser(); sp = p.add_subparsers(dest="cmd", required=True)
    for c in ("declare", "resolve", "resume", "status"):
        q = sp.add_parser(c); q.add_argument("register")
        if c == "declare":
            q.add_argument("--lineage", required=True); q.add_argument("--reason", required=True); q.add_argument("--until", required=True)
            q.add_argument("--urgent", action="append", required=True)
        if c in ("resolve", "resume"): q.add_argument("--interruption", required=True)
        if c == "resume": q.add_argument("--impact")
        if c in ("declare", "resume"): q.add_argument("--executor")
    a = p.parse_args(); {"declare": declare, "resolve": resolve, "resume": resume, "status": status}[a.cmd](a)
if __name__ == "__main__": main()
