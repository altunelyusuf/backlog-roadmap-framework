#!/usr/bin/env python3
"""backlog_agent_monitor v1.0.0 -- the report that lets people stay on the loop without being assigned to tasks (G118).

Read-only. It reads a register and computes, at the instant it is run (or --now), what a person has to look at:

  1. Runs        every ExecutorInstance: its definition and version, when it was created, whether it is retired, how many status moves it made.
  2. Moves       recorded status moves with no maker, or made by a definition instead of a run.
  3. Stalled     items In Progress whose latest recorded move (or, with none, start) is older than --stall-hours (default 24).
  4. Accountability  Done items without an overseer, a verifier or an approver; Done items at or above a humanApprovalLevel with no person approving.
  5. Teams       agent team or federation runs named for an item with no recorded assembly.

Sections 3 to 5 are the ESCALATION list: the only things a person is asked to act on. Exit 0 when it is empty, 1 otherwise. A register that does not
use ExecutorInstance simply reports nothing under 1, 2 and 5 -- the report states what it found, not what it was told to look for.

Usage: backlog_agent_monitor_v1_0_0.py REGISTER.ttl [--now 2026-10-15T09:00:00Z] [--stall-hours 24] [--lineage NAME]
"""
import datetime, sys
from rdflib import Graph, URIRef, RDF
from rdflib.namespace import XSD

B = "http://example.org/backlog#"
PRE = "PREFIX backlog: <%s>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" % B
AGENT = "backlog:Executor_SingleAgent, backlog:Executor_AgentTeam, backlog:Executor_AgentFederation"
FUN = "backlog:responsible, backlog:verifiedBy, backlog:overseenBy, backlog:approvedBy, backlog:reviewedBy, backlog:supportedBy"

def local(x): return str(x).rsplit("#", 1)[-1].rsplit("/", 1)[-1]
def label(g, x):
    l = g.value(x, URIRef("http://www.w3.org/2000/01/rdf-schema#label"))
    return str(l) if l else local(x)
def when(v):
    if v is None: return None
    d = v.toPython()
    if isinstance(d, datetime.datetime):
        return d if d.tzinfo else d.replace(tzinfo=datetime.timezone.utc)
    return None

def main(argv):
    now = datetime.datetime.now(datetime.timezone.utc); stall = 24.0; lineage = None; files = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--now": now = datetime.datetime.fromisoformat(argv[i + 1].replace("Z", "+00:00")); i += 2
        elif a == "--stall-hours": stall = float(argv[i + 1]); i += 2
        elif a == "--lineage": lineage = argv[i + 1]; i += 2
        else: files.append(a); i += 1
    if not files:
        print(__doc__); return 2
    g = Graph()
    for f in files: g.parse(f, format="turtle")
    in_scope = None
    if lineage:
        L = [s for s in g.subjects(RDF.type, URIRef(B + "Lineage")) if local(s) == lineage]
        if not L: print("ERROR: no Lineage named %s" % lineage); return 2
        in_scope = {s for s in g.subjects(URIRef(B + "belongsToLineage"), L[0])}
    def ok(s): return in_scope is None or s in in_scope
    esc = []
    print("== Agent monitor: computed %s%s ==" % (now.strftime("%Y-%m-%d %H:%M:%SZ"), "" if not lineage else ", lineage " + lineage))

    print("\n-- 1. Runs --")
    runs = sorted(g.subjects(RDF.type, URIRef(B + "ExecutorInstance")), key=str)
    for r in runs:
        d = g.value(r, URIRef(B + "instanceOf")); ver = g.value(r, URIRef(B + "instantiatedFromVersion")); at = when(g.value(r, URIRef(B + "instantiatedAt")))
        ret = when(g.value(r, URIRef(B + "retiredAt")))
        moves = sum(1 for _ in g.subjects(URIRef(B + "transitionedByExecutor"), r))
        print("  %-30s of %-24s v%-8s created %s  %s  moves %d" % (label(g, r), label(g, d) if d else "(no definition)", ver or "?", at.strftime("%Y-%m-%d %H:%M") if at else "?", "retired" if ret else "active", moves))
    if not runs: print("  none recorded")

    print("\n-- 2. Moves --")
    anon = defn = 0
    for e in g.subjects(RDF.type, URIRef(B + "TransitionEvent")):
        it = g.value(e, URIRef(B + "transitionedItem"))
        if it is None or not ok(it): continue
        who = g.value(e, URIRef(B + "transitionedByExecutor"))
        if who is None: anon += 1
        elif (who, RDF.type, URIRef(B + "ExecutorInstance")) not in g and g.query(PRE + "ASK { ?w a/rdfs:subClassOf* ?k . FILTER (?k IN (%s)) }" % AGENT, initBindings={"w": who}).askAnswer:
            defn += 1
    print("  with no recorded maker: %d    made by a definition, not a run: %d" % (anon, defn))
    if anon: esc.append("%d recorded status move(s) name nobody who made them" % anon)
    if defn: esc.append("%d recorded status move(s) were made by a standing definition and not by a run" % defn)

    print("\n-- 3. Stalled (In Progress, nothing recorded for %g h) --" % stall)
    n = 0
    for it in sorted(g.subjects(URIRef(B + "hasState"), URIRef(B + "InProgress")), key=str):
        if not ok(it): continue
        last = None
        for e in g.subjects(URIRef(B + "transitionedItem"), it):
            t = when(g.value(e, URIRef(B + "transitionedAt")))
            if t and (last is None or t > last): last = t
        if last is None: last = when(g.value(it, URIRef(B + "startedAt")))
        if last is None:
            print("  %-34s no move or start recorded" % label(g, it)); esc.append("%s is In Progress with no move or start recorded" % label(g, it)); n += 1
        else:
            h = (now - last).total_seconds() / 3600.0
            if h > stall:
                print("  %-34s last record %.1f h ago" % (label(g, it), h)); esc.append("%s has been In Progress for %.1f h with nothing recorded" % (label(g, it), h)); n += 1
    if not n: print("  none")

    print("\n-- 4. Accountability of Done work --")
    n = 0
    for it in sorted(g.subjects(URIRef(B + "hasState"), URIRef(B + "Done")), key=str):
        if not ok(it): continue
        lacks = [p for p, w in (("overseenBy", "an overseer"), ("verifiedBy", "a verifier"), ("approvedBy", "an approver")) if g.value(it, URIRef(B + p)) is None]
        # only items that take part in the agent model are asked: they name an executor run, or their adopter adopted the rule set
        engaged = any((x, RDF.type, URIRef(B + "ExecutorInstance")) in g for p in ("responsible", "overseenBy", "verifiedBy", "approvedBy") for x in g.objects(it, URIRef(B + p))) \
            or any(True for reg in g.subjects(URIRef(B + "adoptsRuleSet"), URIRef(B + "RS_AgentAccountability")) if (it, URIRef(B + "belongsToLineage"), reg) in g or (reg, RDF.type, URIRef(B + "Backlog")) in g)
        if lacks and engaged:
            print("  %-34s lacks %s" % (label(g, it), ", ".join(lacks))); esc.append("%s is Done and lacks %s" % (label(g, it), ", ".join(lacks))); n += 1
        lvl = g.value(it, URIRef(B + "integrityLevel"))
        for reg in g.subjects(URIRef(B + "adoptsRuleSet"), URIRef(B + "RS_AgentAccountability")):
            if not ((it, URIRef(B + "belongsToLineage"), reg) in g or (reg, RDF.type, URIRef(B + "Backlog")) in g): continue
            t = g.value(reg, URIRef(B + "humanApprovalLevel"))
            if t is None or (lvl is not None and lvl.toPython() < t.toPython()): continue
            person = g.query(PRE + "ASK { ?it backlog:approvedBy ?h . ?h a/rdfs:subClassOf* ?k . FILTER (?k IN (backlog:Executor_IndividualHuman, backlog:Executor_HumanTeam)) }", initBindings={"it": it}).askAnswer
            if not person:
                print("  %-34s needs a person to approve (level %s, human level %s)" % (label(g, it), lvl if lvl is not None else "unclassified", t)); esc.append("%s needs a person to approve it" % label(g, it)); n += 1
    if not n: print("  none")

    print("\n-- 5. Teams --")
    n = 0
    for x in runs:
        if not g.query(PRE + "ASK { ?x a ?k . FILTER (?k IN (backlog:Executor_AgentTeam, backlog:Executor_AgentFederation)) }", initBindings={"x": x}).askAnswer: continue
        named = any(True for p in FUN.replace("backlog:", "").split(", ") for it in g.subjects(URIRef(B + p), x) if ok(it))
        if named and g.value(None, URIRef(B + "assemblesTeam"), x) is None:
            print("  %-34s named for work, no recorded assembly" % label(g, x)); esc.append("%s is named for work and has no recorded assembly" % label(g, x)); n += 1
    if not n: print("  none")

    print("\n== Escalation: %d thing(s) for a person ==" % len(esc))
    for e in esc: print("  - " + e)
    return 1 if esc else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
