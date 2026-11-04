#!/usr/bin/env python3
"""backlog_impediment v2.0.0 (--box is required: a break of the raise command) -- raise, advise on and clear an obstacle (Lineage 29, G191; G199).

  backlog_impediment.py REGISTER.ttl raise  --lineage L --prefix P --box BOX [--blocks ITEM] --kind KIND --statement TEXT --owner ROLE [--now ISO]
  backlog_impediment.py REGISTER.ttl advise (--kind KIND | --impediment ID)
  backlog_impediment.py REGISTER.ttl clear  ID --method METHOD [--now ISO]
  backlog_impediment.py REGISTER.ttl list

raise  appends an Impediment (the box whose work it blocks, which must be a box of the lineage that had begun when it was raised (the release of a closed box can still be blocked), and optionally the item in it; its kind, its statement, its owner, the time it was raised) and prints the ways known to clear its kind.
advise prints the ways that clear a kind, with the steps and what shows the obstacle gone; they are advice, never an order, and none waives, skips or defers a rule.
clear  appends the time it was resolved and the way used; it refuses an unknown or already cleared impediment, a way the kind does not list, and a time before it was raised.
list   prints every impediment with its state and its age in hours.
The register is only appended to; nothing already in it is changed. A kind or a way is named by its local name (RuleRefusal, or Mth_StateTheLimit without the prefix Imp_/Mth_ also works)."""
import datetime, fcntl, os, re, sys
from rdflib import Graph, URIRef, RDF, RDFS, Literal
from rdflib.namespace import SKOS
B = "http://example.org/backlog#"; FW = "http://example.org/backlog-framework-register#"
U = lambda n: URIRef(B + n)
local = lambda x: str(x).rsplit("#", 1)[-1]
iso = lambda t: t.strftime("%Y-%m-%dT%H:%M:%SZ")
def die(m): print("REFUSED: " + m); raise SystemExit(1)
def when(a):
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    try: t = datetime.datetime.fromisoformat(a.replace("Z", "+00:00")) if a else now
    except ValueError: die("a time looks like 2026-11-02T10:00:00Z, got %r" % a)
    if t.tzinfo is None: die("a time needs a zone (2026-11-02T10:00:00Z), got %r" % a)
    t = t.astimezone(datetime.timezone.utc)
    if t.year < 2000: die("%s is before the year 2000; a time looks like 2026-11-02T10:00:00Z" % iso(t))
    if t > now + datetime.timedelta(minutes=1): die("%s is in the future; an obstacle is raised or cleared at or before now" % iso(t))
    return t
def find(g, cls, name, what):
    cands = [s for s in g.subjects(RDF.type, U(cls)) if local(s) in (name, ("Imp_" if cls == "ImpedimentKind" else "Mth_") + name)]
    if len(cands) != 1: die("%s %r is not one of: %s" % (what, name, ", ".join(sorted(local(s) for s in g.subjects(RDF.type, U(cls))))))
    return cands[0]
def ways(g, kind):
    out = []
    for m in sorted(g.objects(kind, U("clearableBy")), key=str):
        out.append((local(m), str(g.value(m, RDFS.label)), str(g.value(m, SKOS.definition)) + ((" Limit: " + str(g.value(m, SKOS.scopeNote))) if g.value(m, SKOS.scopeNote) is not None else "")))
    return out
def show(g, kind):
    print("  kind: %s" % g.value(kind, RDFS.label))
    for n, l, d in ways(g, kind): print("   - %s [%s]\n       %s" % (l, n, d))
def write(reg, text, claim=None, once=None):
    """Append text, then parse the whole register again; if it no longer parses, put the file back as it was and refuse."""
    try: add = text.encode("utf-8")
    except UnicodeEncodeError: die("the text is not valid UTF-8; the register is unchanged")
    with open(reg, "rb+", buffering=0) as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        old = f.read()
        if claim and claim.encode("utf-8") in old:
            og = Graph().parse(data=old, format="turtle")
            if (URIRef(claim.strip("<>")), RDF.type, U("Impediment")) in og: die("%s is already in the register: another raise took the number; run it again" % claim)
        if once:
            og = Graph().parse(data=old, format="turtle")
            if (URIRef(once), U("resolvedAt"), None) in og: die("%s is already resolved (by a clear that ran just before this one); nothing was written" % once)
        f.seek(0, 2)
        try:
            view = memoryview(add)
            while len(view):
                n = f.write(view)
                if not n: raise OSError("no progress")
                view = view[n:]
        except BaseException as e:
            f.truncate(len(old)); die("the write failed (%s); the register is as it was" % str(e)[:80])
        try:
            import io
            Graph().parse(data=old + add, format="turtle")
        except Exception as e:
            f.truncate(len(old))
            die("what was to be written does not parse (%s); the register is unchanged" % str(e)[:120])
        os.fsync(f.fileno())
def parse_args(a, names):
    o = {}; i = 0
    while i < len(a):
        if a[i] in names and i + 1 < len(a): o[a[i]] = a[i + 1]; i += 2
        else: die("unexpected argument %r" % a[i])
    return o
def next_id(g, prefix):  # taken from the register as read; write() refuses a number another raise took meanwhile
    n = [int(m.group(1)) for s in g.subjects(RDF.type, U("Impediment")) for m in [re.fullmatch(r"Imp_%s_(\d+)" % re.escape(prefix), local(s))] if m]
    return "Imp_%s_%d" % (prefix, max(n, default=0) + 1)
def main(a):
    if len(a) < 2 or a[1] not in ("raise", "advise", "clear", "list"): print(__doc__); return 2
    reg, cmd = a[0], a[1]; g = Graph(); g.parse(reg, format="turtle")
    if cmd == "list":
        now = when(None)
        for s in sorted(g.subjects(RDF.type, U("Impediment")), key=str):
            r = g.value(s, U("raisedAt")); res = g.value(s, U("resolvedAt")); k = g.value(s, U("hasImpedimentKind")); m = g.value(s, U("clearedBy"))
            age = (now - r.toPython().astimezone(datetime.timezone.utc)).total_seconds() / 3600.0 if r is not None and not res else None
            print("%-28s %s; %s; %s" % (local(s), "cleared by " + local(m) if (m is not None and res is not None) else (("raised after now (check the clock)" if age < 0 else "open %.1f h" % age) if age is not None else ("resolved" if res else "no raise time recorded")), local(k) if k is not None else "no kind", local(g.value(s, U("impedes"))) if g.value(s, U("impedes")) is not None else "-"))
        return 0
    if cmd == "advise":
        o = parse_args(a[2:], ("--kind", "--impediment"))
        if "--impediment" in o:
            im = [s for s in g.subjects(RDF.type, U("Impediment")) if local(s) == o["--impediment"]]
            if len(im) != 1: die("no impediment %r" % o["--impediment"])
            k = g.value(im[0], U("hasImpedimentKind"))
            if k is None: die("%s has no kind; give it one first" % o["--impediment"])
        elif "--kind" in o: k = find(g, "ImpedimentKind", o["--kind"], "kind")
        else: die("advise needs --kind or --impediment")
        show(g, k); return 0
    if cmd == "raise":
        o = parse_args(a[2:], ("--lineage", "--prefix", "--box", "--blocks", "--kind", "--statement", "--owner", "--now"))
        for r in ("--lineage", "--prefix", "--box", "--kind", "--statement", "--owner"):
            if r not in o: die("raise needs %s" % r)
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", o["--prefix"]): die("the prefix is letters and digits (IK), got %r" % o["--prefix"])
        if not o["--statement"].strip(): die("the statement says what is blocked, by what, and what would clear it; it is empty")
        lin = [s for s in g.subjects(RDF.type, U("Lineage")) if local(s) == o["--lineage"]]
        if len(lin) != 1: die("no lineage %r" % o["--lineage"])
        NOT_WORK = {"Role", "ImpedimentKind", "ClearingMethod", "Impediment", "Lineage", "RuleSet", "GovernanceRuling"}
        box = [s for s in g.subjects(RDF.type, U("Iteration")) if local(s) in (o["--box"], "It_%s_%s" % (o["--prefix"], o["--box"]))]
        if len(box) != 1: die("%r is not a box (iteration) of the register: name the box whose work the obstacle blocks, for example %s" % (o["--box"], ", ".join(sorted(local(s) for s in g.subjects(RDF.type, U("Iteration")) if (s, U("belongsToLineage"), lin[0]) in g)[-2:]) or "a box of the lineage"))
        box = box[0]
        if (box, U("belongsToLineage"), lin[0]) not in g: die("%s is not a box of lineage %s: an obstacle blocks the work of a box of its own lineage" % (local(box), o["--lineage"]))
        item = [] if "--blocks" not in o else [s for s in set(g.subjects(None, None)) if local(s) == o["--blocks"] and isinstance(s, URIRef) and (s, RDF.type, None) in g and not any(local(t) in NOT_WORK for t in g.objects(s, RDF.type))]
        if "--blocks" in o and len(item) < 1: die("nothing named %r in the register for the impediment to block (not a role, kind, way, impediment, lineage, rule set or ruling)" % o["--blocks"])
        if len(item) > 1: die("%r names more than one thing in the register: %s" % (o["--blocks"], ", ".join(str(x) for x in item)))
        kind = find(g, "ImpedimentKind", o["--kind"], "kind")
        own = [s for s in set(g.subjects(None, None)) if local(s) == o["--owner"] and isinstance(s, URIRef) and any(local(t) in ("Role",) or (t, RDFS.subClassOf, U("Role")) in g for t in g.objects(s, RDF.type))]
        if not own: die("%r is not a role in the register: an impediment is owned by a role" % o["--owner"])
        t = when(o.get("--now"))
        starts = list(g.objects(box, U("iterationStart")))
        if len(starts) != 1 or not isinstance(starts[0], Literal) or str(starts[0].datatype) != "http://www.w3.org/2001/XMLSchema#dateTime":
            die("%s must have exactly one start recorded as a date-time with a zone, so it can be said to have begun when the obstacle was met" % local(box))
        try: b0 = starts[0].toPython().astimezone(datetime.timezone.utc) if starts[0].toPython().tzinfo else None
        except Exception: b0 = None
        if b0 is None: die("the start of %s has no time zone or is not a time; it needs one such as 2026-11-02T09:00:00Z" % local(box))
        if t < b0: die("%s was raised (%s) before the box began (%s): an obstacle is met in a box that has begun" % (o["--prefix"], iso(t), starts[0]))
        iid = next_id(g, o["--prefix"]); st = o["--statement"].replace("\\", "\\\\").replace('"', '\\"').replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")
        itemq = "<%s>, <%s>" % (box, item[0]) if item else "<%s>" % box; item = item[0] if item else box
        txt = '\n# Impediment raised %s\n<%s%s> a <%sImpediment> ; <%sbelongsToLineage> <%s> ;\n    <%simpedes> %s ; <%shasImpedimentKind> <%s> ;\n    <%shasImpedimentOwner> <%s> ;\n    <%shasImpedimentStatement> "%s" ;\n    <%sraisedAt> "%s"^^<http://www.w3.org/2001/XMLSchema#dateTime> .\n' % (iso(t), FW, iid, B, B, lin[0], B, itemq, B, kind, B, own[0], B, st, B, iso(t))
        write(reg, txt, "<%s%s>" % (FW, iid))
        print("raised %s at %s: blocks %s, %s, owner %s" % (iid, iso(t), local(item), local(kind), local(own[0]))); show(g, kind); return 0
    if cmd == "clear":
        if len(a) < 3: print(__doc__); return 2
        o = parse_args(a[3:], ("--method", "--now"))
        if "--method" not in o: die("clear needs --method: say which way cleared it")
        im = [s for s in g.subjects(RDF.type, U("Impediment")) if local(s) == a[2]]
        if len(im) != 1: die("no impediment %r" % a[2])
        im = im[0]
        if g.value(im, U("resolvedAt")) is not None: die("%s is already resolved" % a[2])
        k = g.value(im, U("hasImpedimentKind"))
        if k is None: die("%s has no kind, so no way is known to clear it; give it a kind first" % a[2])
        m = find(g, "ClearingMethod", o["--method"], "way")
        if (k, U("clearableBy"), m) not in g: die("%s does not list %s; its kind lists: %s. Add the way to the kind through change management first." % (local(k), local(m), ", ".join(n for n, _, _ in ways(g, k))))
        t = when(o.get("--now")); r = g.value(im, U("raisedAt"))
        if r is None: die("%s has no raise time recorded, so no clearing time can be checked against it" % a[2])
        if t < r.toPython().astimezone(datetime.timezone.utc): die("it cannot be resolved (%s) before it was raised (%s)" % (iso(t), r))
        write(reg, '\n# Impediment resolved %s\n<%s> <%sresolvedAt> "%s"^^<http://www.w3.org/2001/XMLSchema#dateTime> ; <%sclearedBy> <%s> .\n' % (iso(t), im, B, iso(t), B, m), once=str(im))
        print("cleared %s at %s by %s" % (a[2], iso(t), g.value(m, RDFS.label))); return 0
if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
