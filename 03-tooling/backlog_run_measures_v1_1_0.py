#!/usr/bin/env python3
"""backlog_run_measures v1.1.0 -- runs the stored measurement query of an objective on a register and records the observation (box 57, G243; IPage handover of 2026-11-16, point 4, criteria C8 and C9).

An objective says how its value is derived with `backlog:hasMeasurementQuery`. This tool executes that query, a SPARQL SELECT, on the register as it stands, prints the one number it returns, and with --record writes a
backlog:MetricObservation that cites the query and the version and sha256 digest of the register it ran on, so anyone can re-derive the number. It refuses, and prints no value, when an objective has no query, when the
query is not a SPARQL SELECT (for example a shell command), when the query does not return exactly one numeric value, or when the objective has no success metric to observe. The tool executes the query and adds no judgement; the measurement
is the query's own. Facts held in files rather than in the register are first recorded as completion evidence (path and content hash, verified by backlog_evidence_bridge) and then counted by a query over those records.

Usage: backlog_run_measures_v1_1_0.py REGISTER.ttl [--archive FILE ...] (--objective NAME | --all) [--record OUT.ttl] [--at ISO_TIME]
  NAME is the local name of the objective (Obj_X) or its label text. --all runs every objective that carries a query and lists the ones that do not. --record appends the observations to OUT.ttl.
Exit codes: 0 every requested value was produced; 2 a refusal."""
import hashlib, logging, math, os, re, sys, datetime
from decimal import Decimal
from rdflib import Graph, Namespace, RDF, RDFS, Literal, URIRef
from rdflib.namespace import XSD
from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.parser import parseQuery

logging.getLogger("rdflib").setLevel(logging.CRITICAL)

B = Namespace("http://example.org/backlog#")


def refuse(msg):
    sys.stdout.flush()
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def loc(x):
    return str(x).rsplit("#", 1)[-1] if "#" in str(x) else str(x).rstrip("/").rsplit("/", 1)[-1]


def version_of(path):
    m = re.findall(r"_v(\d+)_(\d+)_(\d+)", os.path.basename(path))
    return ".".join(m[-1]) if m else "unversioned"


def digest(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def bname(path):
    return os.path.basename(path).encode("utf-8", "backslashreplace").decode("utf-8")


def esc(t):
    t = t.replace("\\", "\\\\").replace('"', '\\"')
    return "".join(c if (c >= " " and c != "\x7f") else "\\u%04X" % ord(c) for c in t)


def one_number(g, query):
    ns = dict(list(g.namespaces()) + [("backlog", B)])
    try:
        pq = prepareQuery(query, initNs=ns)
    except Exception as e:
        raise ValueError("the stored query is not a SPARQL query this tool can run (%s)" % str(e).splitlines()[0][:120])
    tree = repr(parseQuery(query))
    if "ServiceGraphPattern" in tree:
        raise ValueError("the stored query calls out to another service, which this tool does not do")
    if "datasetClause" in tree:
        raise ValueError("the stored query names its own dataset (FROM), which this tool does not read; it runs on the register and archives given")
    for fn in ("RAND", "NOW", "UUID", "STRUUID", "BNODE"):
        if "Builtin_" + fn in tree:
            raise ValueError("the stored query calls %s(), so its value cannot be re-derived from the register" % fn)
    try:
        res = g.query(pq)
    except Exception as e:
        raise ValueError("the stored query is not a SPARQL query this tool can run (%s)" % str(e).splitlines()[0][:120])
    if res.type != "SELECT":
        raise ValueError("the stored query is not a SELECT query")
    try:
        rows = list(res)
    except Exception as e:
        raise ValueError("the stored query failed while it ran (%s)" % str(e).splitlines()[0][:120])
    if len(rows) != 1 or len(res.vars) != 1:
        raise ValueError("the query returns %d row(s) and %d column(s), not exactly one value" % (len(rows), len(res.vars)))
    v = rows[0][0]
    if not isinstance(v, Literal) or v.datatype not in (XSD.integer, XSD.decimal, XSD.double, XSD.float, XSD.int, XSD.long, XSD.nonNegativeInteger):
        raise ValueError("the query does not return a number")
    try:
        d = Decimal(str(v.toPython()))
    except Exception:
        raise ValueError("the query does not return a finite number")
    if not d.is_finite():
        raise ValueError("the query does not return a finite number")
    return d


def plain(d):
    t = format(d, "f")
    if "." in t:
        t = t.rstrip("0")
        if t.endswith("."):
            t += "0"
    else:
        t += ".0"
    return t


def shown(d):
    t = plain(d)
    return t[:-2] if t.endswith(".0") else t


def objectives(g):
    return sorted(g.subjects(RDF.type, B.Objective), key=str)


def find(g, name):
    hits = [o for o in objectives(g) if loc(o) == name or name in [str(l) for l in g.objects(o, RDFS.label)]]
    if len(hits) != 1:
        refuse("%s objective named '%s'" % ("no" if not hits else "more than one", name))
    return hits[0]


def main(argv):
    a = list(argv); arch = []; rec = None; at = None; name = None; allo = False; pos = []
    while a:
        x = a.pop(0)
        if x in ("--archive", "--record", "--at", "--objective"):
            if not a or a[0] == "":
                refuse("%s needs a value" % x)
            v = a.pop(0)
            if x == "--archive": arch.append(v)
            elif x == "--record":
                if rec is not None: refuse("--record is given twice")
                rec = v
            elif x == "--at":
                if at is not None: refuse("--at is given twice")
                at = v
            else:
                if name is not None: refuse("--objective is given twice")
                name = v
        elif x == "--all": allo = True
        else: pos.append(x)
    if len(pos) != 1 or (not name and not allo) or (name and allo):
        sys.stderr.write("REFUSED: give exactly one register and exactly one of --objective NAME or --all\n" + __doc__.split("Usage:")[1].split("Exit codes")[0] + "\n"); sys.exit(2)
    if at is not None:
        try:
            if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", at):
                raise ValueError(at)
            tm = datetime.datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
            if tm > datetime.datetime.now(datetime.timezone.utc):
                raise ValueError(at)
        except ValueError:
            refuse("--at must be a real UTC time that is not in the future, such as 2026-11-17T12:00:00Z")
    if rec is not None and not os.path.isdir(os.path.dirname(os.path.abspath(rec))):
        refuse("the folder of %s does not exist" % rec)
    reg = pos[0]
    if rec is not None and os.path.isdir(rec):
        refuse("%s is a folder, not a file" % rec)
    if rec is not None and os.path.exists(rec) and not os.path.isfile(rec):
        refuse("%s is not a regular file" % rec)
    if rec is not None and os.path.exists(rec) and any(os.path.exists(f) and os.path.samefile(f, rec) for f in [reg] + arch):
        refuse("%s is the register or an archive being read; observations are never appended to the file they cite" % rec)
    g = Graph(); dig = {}
    for f in [reg] + arch:
        if not os.path.isfile(f):
            refuse("cannot read %s: it is not a file that exists here" % bname(f))
        try:
            raw = open(f, "rb").read()
        except OSError as e:
            refuse("cannot read %s (%s)" % (bname(f), e.strerror))
        dig[f] = hashlib.sha256(raw).hexdigest()
        try:
            g.parse(data=raw.decode("utf-8-sig"), format="turtle")
        except Exception as e:
            refuse("cannot read %s as Turtle (%s)" % (bname(f), str(e).splitlines()[0][:100] if str(e) else type(e).__name__))
    chosen = [find(g, name)] if name else objectives(g)
    for o in chosen:
        if not isinstance(o, URIRef):
            refuse("an objective without an identifier of its own cannot be recorded against")
    when = at or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tag = re.sub(r"\D", "", when)
    src = "register %s (version %s, sha256 %s)" % (bname(reg), version_of(reg), dig[reg])
    if arch:
        src += " and archive " + " and ".join("%s (version %s, sha256 %s)" % (bname(f), version_of(f), dig[f]) for f in arch)
    out, notrun = [], []
    for o in chosen:
        qs = list(g.objects(o, B.hasMeasurementQuery))
        if len(qs) > 1:
            refuse("%s carries %d measurement queries; which one gives the value is not decided, so none is run" % (loc(o), len(qs)))
        q = qs[0] if qs else None
        if q is None:
            if name:
                refuse("%s carries no measurement query, so no value is printed" % loc(o))
            notrun.append(loc(o)); continue
        try:
            val = one_number(g, str(q))
        except ValueError as e:
            refuse("%s: %s" % (loc(o), e))
        metrics = list(g.objects(o, B.hasSuccessMetric))
        if len(metrics) > 1:
            refuse("%s has %d success metrics; the observation cannot be recorded against one of them by guess" % (loc(o), len(metrics)))
        metric = metrics[0] if metrics else None
        if metric is not None and not isinstance(metric, URIRef):
            refuse("%s has a success metric that is not an identified metric" % loc(o))
        if metric is None:
            refuse("%s has no success metric, so there is nothing to record the observation against" % loc(o))
        ns = str(o).rsplit("#", 1)[0] + "#" if "#" in str(o) else str(o).rsplit("/", 1)[0] + "/"
        oid = "Obs_" + loc(o) + "_Q" + tag + "_" + (hashlib.sha256("".join(dig[x] for x in [reg] + arch).encode()).hexdigest() if arch else dig[reg])[:8]
        method = "Ran the stored measurement query of the objective on the %s at %s; the query: %s" % (src, when, " ".join(str(q).split()))
        out.append((ns, oid, o, metric, val, when, method))
    if rec is not None and out and os.path.exists(rec):
        hv = Graph()
        try:
            if os.path.getsize(rec):
                hv.parse(rec, format="turtle")
        except OSError as e:
            refuse("cannot read %s (%s)" % (rec, e.strerror))
        except Exception as e:
            refuse("%s exists but is not Turtle (%s); nothing is added to it" % (rec, str(e).splitlines()[0][:100] if str(e) else type(e).__name__))
        for ns, oid, *_ in out:
            if any(True for _x in hv.triples((URIRef(ns + oid), None, None))):
                refuse("%s already holds the observation %s (same objective, time and register)" % (rec, oid))
    if rec is not None and out:
        pre = "@prefix backlog: <http://example.org/backlog#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
        fresh = not os.path.exists(rec) or os.path.getsize(rec) == 0
        text = pre if fresh else "\n" + pre
        e = esc
        for ns, oid, o, metric, val, when, method in out:
            text += ('<%s%s> a backlog:MetricObservation ; rdfs:label "Query run: %s"@en ;\n    backlog:observesMetric <%s> ; backlog:observationFor <%s> ;\n    backlog:hasObservedValue %s ; backlog:observedAt "%s"^^xsd:dateTime ;\n    backlog:hasObservationMethod "%s" .\n'
                     % (ns, oid, e(loc(o)), metric, o, plain(val), when, e(method)))
        try:
            with open(rec, "a") as fh:
                fh.write(text)
        except OSError as ex:
            refuse("cannot write %s (%s)" % (rec, ex.strerror))
    for ns, oid, o, metric, val, when, method in out:
        print("%s = %s   [query run on the %s]" % (loc(o), shown(val), src))
    if notrun:
        print("not run (no stored query): %d objective(s): %s" % (len(notrun), ", ".join(notrun)))
    if rec is not None and out:
        print("recorded %d observation(s) in %s" % (len(out), rec))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
