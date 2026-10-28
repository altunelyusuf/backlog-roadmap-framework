#!/usr/bin/env python3
"""backlog_lineage_steps v1.1.0 -- the plan step, the cancelling exit and the adaptation route as one recorded step each (G162).

  plan    REGISTER --lineage IRI --container IRI [--by Owner|Builder]
          Computes the roadmap report (backlog_roadmap_report --emit) and records the kick-off of the lineage that activates it, stamped from
          the clock, so the plan that is activated is the one that was computed. Work of a lineage that adopted RS_PlanBeforeStart starts after it.
  assess  REGISTER --lineage IRI --fit-gap TEXT --impact TEXT
          Takes the as-is state: sorts every work item as accomplished / failed / in progress / due by its state and every objective as fitted
          (every item serving it is Done) or gapped, and records the as-is assessment.
  close   REGISTER --lineage IRI --mark cancelled|failed --rationale TEXT
          Refuses unless an as-is assessment of the lineage sorts everything; then records the closure report (marked, citing the assessment),
          the mission outcome Abandoned with its rationale and the lineage status Abandoned.
  adapt   REGISTER --lineage IRI --scope IRI --objective IRI --rationale TEXT --owner-decision TEXT --admit IRI [--admit IRI ...]
          The one adaptation route: a change request that supports the named objective, an impact assessment computed from the register (items,
          points, objectives touched), and the scope change admitting the items, decided by the Owner as the text states. The tool refuses an
          objective that is not the lineage's, and an empty Owner decision: the decision is the Owner's, and the text says where it is.
The tool appends text to the register and changes only the statuses it names; the register is then validated as usual.
"""
import argparse, datetime, glob, os, re, subprocess, sys, tempfile
import rdflib
from rdflib import URIRef, Namespace, RDF
B = Namespace("http://example.org/backlog#")
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def dtl(t): return f'"{t}"^^<http://www.w3.org/2001/XMLSchema#dateTime>'
def esc(t): return t.replace("\\", "\\\\").replace('"', '\\"')
def load(p):
    g = rdflib.Graph(); g.parse(p, format="turtle"); return g
def ns_of(iri): s = str(iri); return s.rsplit("#", 1)[0] + "#" if "#" in s else s.rsplit("/", 1)[0] + "/"
def append(p, t):
    with open(p, "a") as f: f.write("\n" + t.strip("\n") + "\n")
def pfx(p): return "" if any(l.startswith("@prefix backlog:") for l in open(p)) else "@prefix backlog: <http://example.org/backlog#> .\n"
def block(path, iri):
    s = open(path).read(); g = load(path)
    names = {f"<{iri}>"} | {f"{p}:{str(iri)[len(str(n)):]}" for p, n in g.namespaces() if str(iri).startswith(str(n)) and str(n)}
    for nm in names:
        m = re.search(r'^%s a [^\n]*\n(?:(?!^\S)[^\n]*\n)*' % re.escape(nm), s, re.M)
        if m: return s, m
    sys.exit(f"cannot find the statement of {iri} in {path}")
def set_pred(path, iri, pred, value):
    s, m = block(path, iri); blk = m.group(0)
    nb, k = re.subn(r'backlog:%s [^;.\n]+' % pred, f'backlog:{pred} {value}', blk, count=1)
    if k == 0:
        nb = blk.rstrip("\n"); assert nb.endswith("."), iri
        nb = nb[:-1].rstrip() + f' ;\n    backlog:{pred} {value} .\n'
    open(path, "w").write(s[:m.start()] + nb + s[m.end():])
def items_of(g, lin):
    s = set(g.subjects(B.belongsToLineage, lin))
    for o in list(s): s |= set(g.subjects(B.admittedByOutput, o))
    return sorted(i for i in s if (i, B.hasState, None) in g)
def objectives_of(g, lin): return sorted(o for o in g.subjects(RDF.type, B.Objective) if (o, B.belongsToLineage, lin) in g)
def sname(g, x): return str(x).rsplit("#", 1)[-1]

def plan(a):
    g = load(a.register); lin = URIRef(a.lineage)
    if (lin, RDF.type, B.Lineage) not in g: sys.exit("not a lineage in this register")
    rr = sorted(glob.glob(os.path.join(HERE, "backlog_roadmap_report_v*.py")), key=sv)[-1]
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "r.ttl")
        r = subprocess.run([sys.executable, rr, a.register, "--emit", out], capture_output=True, text=True)
        if not os.path.exists(out): sys.exit("the roadmap report could not be computed:\n" + (r.stdout + r.stderr)[-800:])
        rg = load(out)
    rep = next(rg.subjects(RDF.type, B.RoadmapReport), None)
    if rep is None: sys.exit("the roadmap report emitted no report individual")
    ts = str(next(rg.objects(rep, B.hasRunTimestamp)))
    if not ts.endswith("Z"):   # the report stamps local time without a zone; the register's instants are UTC
        ts = datetime.datetime.fromisoformat(ts).astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    t = now()
    if ts > t: sys.exit("the report was run after now; clock disagreement")
    n = sum(1 for _ in g.subjects(RDF.type, B.KickOff)) + 1
    kid = f"{ns_of(lin)}KickOff_{n}"
    txt = pfx(a.register) + f'<{rep}> a backlog:RoadmapReport ; backlog:hasRunTimestamp {dtl(ts)} ; backlog:reportOf <{next(rg.objects(rep, B.reportOf))}> ;\n    ' + " ;\n    ".join(f"backlog:hasSection <{s}>" for s in rg.objects(rep, B.hasSection)) + " .\n"
    if (rep, RDF.type, B.RoadmapReport) in g: txt = ""
    txt += (f'<{kid}> a backlog:KickOff ; backlog:kicksOffLineage <{lin}> ; backlog:kickOffFor <{a.container}> ; backlog:kickedOffAt {dtl(t)} ; '
            f'backlog:hasKickOffMode backlog:KickOff_Declared ; backlog:decidedBy backlog:{a.by} ; backlog:activatesReport <{rep}> .')
    append(a.register, txt); print(f"kick-off {kid} recorded at {t}, activating report {rep} (run {ts})")

def sort_all(g, lin):
    acc, fail, prog, due, other = [], [], [], [], []
    for i in items_of(g, lin):
        st = g.value(i, B.hasState)
        (acc if st == B.Done else fail if st == B.Cancelled else prog if st in (B.InProgress, B.Suspended) else due if st in (B.Proposed, B.Refined, B.Ready) else other).append(i)
    fit, gap = [], []
    for o in objectives_of(g, lin):
        serving = [i for i in items_of(g, lin) if o in set(g.objects(i, B.pursuesObjective))]
        (fit if serving and all(g.value(i, B.hasState) == B.Done for i in serving) else gap).append(o)
    return acc, fail, prog, due, other, fit, gap
def assess(a):
    g = load(a.register); lin = URIRef(a.lineage)
    acc, fail, prog, due, other, fit, gap = sort_all(g, lin)
    if other: sys.exit("items in a state the assessment cannot sort: " + ", ".join(sname(g, i) for i in other))
    n = sum(1 for _ in g.subjects(RDF.type, B.AsIsAssessment)) + 1
    aid = f"{ns_of(lin)}AsIs_{n}"; t = now()
    parts = [f"backlog:assessesLineage <{lin}>", f"backlog:assessedAt {dtl(t)}", f'backlog:hasFitGapStatement "{esc(a.fit_gap)}"', f'backlog:hasImpactStatement "{esc(a.impact)}"']
    for pr, xs in (("accomplishedItem", acc), ("failedItem", fail), ("inProgressItem", prog), ("dueItem", due), ("fitsObjective", fit), ("gapsObjective", gap)):
        parts += [f"backlog:{pr} <{x}>" for x in xs]
    append(a.register, pfx(a.register) + f"<{aid}> a backlog:AsIsAssessment ; " + " ;\n    ".join(parts) + " .")
    print(f"as-is assessment {aid}: accomplished {len(acc)}, failed {len(fail)}, in progress {len(prog)}, due {len(due)}; objectives fitted {len(fit)}, gapped {len(gap)}")
def close(a):
    g = load(a.register); lin = URIRef(a.lineage)
    mis = g.value(lin, B.lineageForMission)
    if mis is None: sys.exit("the lineage names no mission (lineageForMission)")
    ass = [x for x in g.subjects(B.assessesLineage, lin)]
    if not ass: sys.exit("no as-is assessment of the lineage: run assess first")
    ass = sorted(ass)[-1]
    sorted_ = set()
    for pr in ("accomplishedItem", "failedItem", "inProgressItem", "dueItem"): sorted_ |= set(g.objects(ass, B[pr]))
    miss = [i for i in items_of(g, lin) if i not in sorted_]
    if miss: sys.exit("the assessment does not sort: " + ", ".join(sname(g, i) for i in miss) + " (assess again)")
    t = now(); n = sum(1 for _ in g.subjects(RDF.type, B.ClosureReport)) + 1
    append(a.register, pfx(a.register) + f'<{ns_of(lin)}Closure_{n}> a backlog:ClosureReport ; backlog:closesForMission <{mis}> ; backlog:reportGeneratedAt {dtl(t)} ;\n'
           f'    backlog:hasClosureMark backlog:Cm_{"Cancelled" if a.mark == "cancelled" else "Failed"} ; backlog:citesAssessment <{ass}> ; backlog:hasClosureSummary "{esc(a.rationale)}" .')
    set_pred(a.register, mis, "hasMissionOutcome", "backlog:Out_Abandoned"); set_pred(a.register, mis, "outcomeRationale", f'"{esc(a.rationale)}"')
    set_pred(a.register, lin, "hasLineageStatus", "backlog:LS_Abandoned")
    print(f"lineage {sname(g, lin)} closed as {a.mark} at {t}, citing {sname(g, ass)}")
def adapt(a):
    g = load(a.register); lin = URIRef(a.lineage); obj = URIRef(a.objective); sc = URIRef(a.scope)
    if (obj, B.belongsToLineage, lin) not in g: sys.exit("the objective is not an objective of this lineage: a request that serves none of them is another mission and waits")
    if not a.owner_decision.strip(): sys.exit("the decision is the Owner's: --owner-decision must say where it is recorded")
    adm = [URIRef(x) for x in a.admit]
    for x in adm:
        if (x, B.hasState, None) not in g: sys.exit("the item is not in the register (record it first): " + str(x))
    pts = 0.0
    for x in adm:
        for pr in (B.hasEffortEstimate, B.hasEffort):
            v = g.value(x, pr)
            if v is not None:
                try: pts += float(v)
                except ValueError: pass
                break
    t = now(); ns = ns_of(lin); n = sum(1 for _ in g.subjects(RDF.type, B.ChangeRequest)) + 1
    cr, ia, scn = f"{ns}CR_{n}", f"{ns}IA_{n}", f"{ns}SC_{n}"
    stmt = (f"{len(adm)} item(s) added to {sname(g, lin)}, {pts:g} point(s) of recorded effort; serves objective {sname(g, obj)}; "
            f"computed from the register at {t}.")
    append(a.register, pfx(a.register) +
           f'<{cr}> a backlog:ChangeRequest ; backlog:requestsChangeTo <{sc}> ; backlog:hasChangeDirection backlog:Direction_Grow ; backlog:hasChangeRequestRationale "{esc(a.rationale)}" ;\n'
           f'    backlog:hasDisposition backlog:Disp_Accepted ; backlog:supportsObjective <{obj}> ; backlog:belongsToLineage <{lin}> .\n'
           f'<{ia}> a backlog:ImpactAssessment ; backlog:analyzesRequest <{cr}> ; backlog:hasImpactStatement "{esc(stmt)}" .\n'
           f'<{scn}> a backlog:ScopeChange ; backlog:fulfillsRequest <{cr}> ; backlog:changesScope <{sc}> ; backlog:decidedBy backlog:Owner ; backlog:belongsToLineage <{lin}> ;\n'
           f'    backlog:hasScopeChangeRationale "{esc(a.rationale)} Owner decision: {esc(a.owner_decision)}" ;\n    ' + " ;\n    ".join(f"backlog:admitsItem <{x}>" for x in adm) + " .")
    print(f"adaptation recorded: {cr}, {ia}, {scn}; {stmt}")
def main():
    p = argparse.ArgumentParser(); sp = p.add_subparsers(dest="cmd", required=True)
    q = sp.add_parser("plan"); q.add_argument("register"); q.add_argument("--lineage", required=True); q.add_argument("--container", required=True); q.add_argument("--by", default="Owner", choices=["Owner", "Builder"])
    q = sp.add_parser("assess"); q.add_argument("register"); q.add_argument("--lineage", required=True); q.add_argument("--fit-gap", required=True); q.add_argument("--impact", required=True)
    q = sp.add_parser("close"); q.add_argument("register"); q.add_argument("--lineage", required=True); q.add_argument("--mark", required=True, choices=["cancelled", "failed"]); q.add_argument("--rationale", required=True)
    q = sp.add_parser("adapt"); q.add_argument("register"); q.add_argument("--lineage", required=True); q.add_argument("--scope", required=True); q.add_argument("--objective", required=True)
    q.add_argument("--rationale", required=True); q.add_argument("--owner-decision", required=True); q.add_argument("--admit", action="append", required=True)
    a = p.parse_args(); {"plan": plan, "assess": assess, "close": close, "adapt": adapt}[a.cmd](a)
if __name__ == "__main__": main()
