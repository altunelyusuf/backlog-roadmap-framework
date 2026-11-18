#!/usr/bin/env python3
"""backlog_run_measures_probe v1.1.0 (box 57, G243): the runner of stored measurement queries prints the number its query returns, records an observation that cites the query and the register version and digest, and refuses -- printing no value -- an objective with no query, a query that is not a SPARQL SELECT, a query that does not return exactly one number, and an objective with no success metric.
Usage: probe [--tool PATH]  (--tool runs the probe on another copy of the tool, for the planted-fault check)."""
import glob, os, re, subprocess, sys, tempfile
from rdflib import Graph, Namespace, RDF
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", p)[0]]
TOOL = sorted(glob.glob(PKG + "/03-tooling/backlog_run_measures_v*.py"), key=sv)[-1]
if "--tool" in sys.argv:
    TOOL = sys.argv[sys.argv.index("--tool") + 1]
B = Namespace("http://example.org/backlog#")
HEAD = ("@prefix backlog: <http://example.org/backlog#> . @prefix fw: <http://example.org/probe#> . @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> . @prefix core: <http://example.org/core#> .\n"
        "fw:M a core:Metric .\nfw:S1 a backlog:Story .\nfw:S2 a backlog:Story .\nfw:S3 a backlog:Story .\n")
def obj(n, q=None, metric=True, label=None):
    t = "fw:%s a backlog:Objective" % n + (' ; rdfs:label "%s"' % label if label else "") + (" ; backlog:hasSuccessMetric fw:M" if metric else "")
    if q is not None:
        t += ' ; backlog:hasMeasurementQuery """%s"""' % q.replace("\\", "\\\\").replace('"', '\\"')
    return t + " .\n"
COUNT = "SELECT (COUNT(?s) AS ?n) WHERE { ?s a backlog:Story }"
def run(reg, args, extra=None, name="r_v1_2_3.ttl"):
    with tempfile.TemporaryDirectory() as d:
        rp = os.path.join(d, name); open(rp, "w").write(reg)
        if extra:
            open(os.path.join(d, "arc_v1_0_0.ttl"), "w").write(extra)
        a = [x.replace("@R", rp).replace("@A", os.path.join(d, "arc_v1_0_0.ttl")).replace("@O", os.path.join(d, "out.ttl")) for x in args]
        p = subprocess.run([sys.executable, TOOL, rp] + a, capture_output=True, text=True)
        out = os.path.join(d, "out.ttl")
        return p.returncode, p.stdout, p.stderr, (open(out).read() if os.path.exists(out) else None), open(rp, "rb").read()
FAILS = []; N = [0]
def expect(what, ok):
    N[0] += 1
    if not ok: FAILS.append(what); print("FAIL ", what)
rc, o, e, rec, raw = run(HEAD + obj("Obj_C", COUNT), ["--objective", "Obj_C", "--record", "@O"])
expect("a count query prints its value", rc == 0 and "Obj_C = 3" in o)
import hashlib
from rdflib import RDFS
g = Graph(); g.parse(data="@prefix x: <http://x/> .\n" + (rec or ""), format="turtle") if rec else None
ob = list(g.subjects(RDF.type, B.MetricObservation)) if rec else []
expect("--record writes one MetricObservation for the objective and its metric with the value", len(ob) == 1 and str(g.value(ob[0], B.observationFor)).endswith("Obj_C") and str(g.value(ob[0], B.observesMetric)).endswith("#M") and float(g.value(ob[0], B.hasObservedValue)) == 3.0)
m = str(g.value(ob[0], B.hasObservationMethod)) if ob else ""
expect("the observation cites the query, the register version and its digest", "COUNT(?s)" in m and "version 1.2.3" in m and hashlib.sha256(raw).hexdigest() in m)
rc, o, e, rec, _ = run(HEAD + obj("Obj_N"), ["--objective", "Obj_N", "--record", "@O"])
expect("an objective with no query is refused and prints no value", rc == 2 and "Obj_N =" not in o and "no measurement query" in e and rec is None)
rc, o, e, rec, _ = run(HEAD + obj("Obj_X", "python3 05-lineage/measure_governance_v1_1_0.py --metric Branches"), ["--objective", "Obj_X", "--record", "@O"])
expect("a stored shell command is refused as not a SPARQL query and prints no value", rc == 2 and "Obj_X =" not in o and "SPARQL" in e and rec is None)
rc, o, e, rec, _ = run(HEAD + obj("Obj_R", "SELECT ?s WHERE { ?s a backlog:Story }"), ["--objective", "Obj_R"])
expect("a query returning three rows is refused", rc == 2 and "Obj_R =" not in o and "row" in e)
rc, o, e, rec, _ = run(HEAD + obj("Obj_I", "SELECT ?s WHERE { ?s a backlog:Story } LIMIT 1"), ["--objective", "Obj_I"])
expect("a query returning an IRI, not a number, is refused", rc == 2 and "Obj_I =" not in o and "number" in e)
rc, o, e, rec, _ = run(HEAD + obj("Obj_W", "SELECT ?s ?t WHERE { ?s a backlog:Story . BIND(1 AS ?t) } LIMIT 1"), ["--objective", "Obj_W"])
expect("a query returning two columns is refused", rc == 2 and "Obj_W =" not in o)
rc, o, e, rec, _ = run(HEAD + obj("Obj_M", COUNT, metric=False), ["--objective", "Obj_M", "--record", "@O"])
expect("an objective with no success metric is refused", rc == 2 and "Obj_M =" not in o and "success metric" in e and rec is None)
rc, o, e, rec, _ = run(HEAD + obj("Obj_Z", "SELECT (COUNT(?s) AS ?n) WHERE { ?s a backlog:Nothing }"), ["--objective", "Obj_Z", "--record", "@O"])
expect("a query whose number is zero prints and records zero", rc == 0 and "Obj_Z = 0" in o and rec is not None and "hasObservedValue 0.0" in rec)
rc, o, e, rec, _ = run(HEAD + obj("Obj_P", "SELECT (COUNT(?s) AS ?n) WHERE { ?s a backlog:Story . FILTER (?s = fw:S1) }"), ["--objective", "Obj_P"])
expect("the prefixes of the register itself are available to the query", rc == 0 and "Obj_P = 1" in o)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", COUNT), ["--objective", "Obj_C"], extra="@prefix backlog: <http://example.org/backlog#> . @prefix fw: <http://example.org/probe#> . fw:S9 a backlog:Story .\n")
rc2, o2, e2, _, _ = run(HEAD + obj("Obj_C", COUNT), ["--objective", "Obj_C", "--archive", "@A"], extra="@prefix backlog: <http://example.org/backlog#> . @prefix fw: <http://example.org/probe#> . fw:S9 a backlog:Story .\n")
expect("with --archive the query reads the archive too", "Obj_C = 3" in o and rc2 == 0 and "Obj_C = 4" in o2)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", COUNT, label="Stories counted") + obj("Obj_N"), ["--all", "--record", "@O"])
expect("--all runs the objectives that have a query and lists the ones without", rc == 0 and "Obj_C = 3" in o and "not run (no stored query): 1" in o and rec is not None and rec.count("a backlog:MetricObservation") == 1)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", COUNT, label="Stories counted"), ["--objective", "Stories counted"])
expect("an objective is found by its label", rc == 0 and "Obj_C = 3" in o)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", COUNT), ["--objective", "Obj_Nope"])
expect("an unknown objective is refused", rc == 2 and "no objective" in e)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", COUNT) + obj("Obj_X", "python3 x.py"), ["--all"])
expect("--all refuses when one stored query is not SPARQL, rather than skipping it", rc == 2 and "Obj_X" in e)
# -- second round (first review of box 57): values, archive citation, evaluation errors, recording edges
from rdflib import XSD
def obsgraph(rec):
    gg = Graph()
    try:
        gg.parse(data=rec or "", format="turtle")
    except Exception:
        pass
    return gg
rc, o, e, rec, _ = run(HEAD + obj("Obj_T", "SELECT (0.00001 AS ?n) WHERE {}"), ["--objective", "Obj_T", "--record", "@O"])
gg = obsgraph(rec) if rec else None
val = next(gg.objects(None, B.hasObservedValue)) if gg else None
expect("a tiny value is recorded as xsd:decimal, exactly", rc == 0 and val is not None and val.datatype == XSD.decimal and str(val) == "0.00001")
rc, o, e, rec, _ = run(HEAD + obj("Obj_H", "SELECT (2.5 AS ?n) WHERE {}"), ["--objective", "Obj_H", "--record", "@O"])
gg = obsgraph(rec) if rec else None
val = next(gg.objects(None, B.hasObservedValue)) if gg else None
expect("a value with a fraction is recorded whole, as decimal", rc == 0 and val is not None and val.datatype == XSD.decimal and str(val) == "2.5" and "Obj_H = 2.5" in o)
at = next(gg.objects(None, B.observedAt)) if gg else None
expect("observedAt is an xsd:dateTime", at is not None and at.datatype == XSD.dateTime)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", COUNT), ["--objective", "Obj_C", "--archive", "@A", "--record", "@O"], extra="@prefix backlog: <http://example.org/backlog#> . @prefix fw: <http://example.org/probe#> . fw:S9 a backlog:Story .\n")
m2 = str(next(obsgraph(rec).objects(None, B.hasObservationMethod))) if rec else ""
expect("with --archive the observation cites the archive file, its version and digest", "arc_v1_0_0.ttl" in m2 and "archive" in m2 and m2.count("sha256") == 2)
for what, q, word in [("a regular expression that fails while it runs", 'SELECT (COUNT(?s) AS ?n) WHERE { ?s a backlog:Story . FILTER(REGEX(STR(?s), "(")) }', "ran"),
                      ("a query that calls out to another service", 'SELECT (COUNT(?s) AS ?n) WHERE { SERVICE <http://127.0.0.1:1/sparql> { ?s a backlog:Story } }', "service"),
                      ("an infinite result", 'SELECT ("INF"^^<http://www.w3.org/2001/XMLSchema#double> AS ?n) WHERE {}', "finite"),
                      ("a result that is not a number (a plain string)", 'SELECT ("abc" AS ?n) WHERE {}', "number"),
                      ("an ASK query", 'ASK { ?s a backlog:Story }', "SELECT"),
                      ("an INSERT query", 'INSERT DATA { <http://x/a> <http://x/b> 1 }', "SPARQL")]:
    rc, o, e, rec, _ = run(HEAD + obj("Obj_E", q), ["--objective", "Obj_E", "--record", "@O"])
    expect("%s is refused with a reason, not a crash, and writes nothing" % what, rc == 2 and "Traceback" not in e and "REFUSED" in e and "Obj_E =" not in o and rec is None)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", COUNT) + obj("Obj_X", "python3 x.py"), ["--all", "--record", "@O"])
expect("--all prints no value when one stored query is refused", rc == 2 and "Obj_C =" not in o and rec is None)
rc, o, e, rec, _ = run(HEAD + obj("Obj_N"), ["--all", "--record", "@O"])
expect("--record with nothing run writes no file", rc == 0 and rec is None and "not run (no stored query): 1" in o)
with tempfile.TemporaryDirectory() as d:
    rp = os.path.join(d, "r_v1_0_0.ttl"); open(rp, "w").write(HEAD + obj("Obj_C", COUNT))
    op = os.path.join(d, "out.ttl")
    r1 = subprocess.run([sys.executable, TOOL, rp, "--objective", "Obj_C", "--record", op, "--at", "2026-11-17T10:00:00Z"], capture_output=True, text=True)
    r2 = subprocess.run([sys.executable, TOOL, rp, "--objective", "Obj_C", "--record", op, "--at", "2026-11-17T11:00:00Z"], capture_output=True, text=True)
    r3 = subprocess.run([sys.executable, TOOL, rp, "--objective", "Obj_C", "--record", op, "--at", "2026-11-17T11:00:00Z"], capture_output=True, text=True)
    gg = Graph()
    try:
        gg.parse(op, format="turtle")
    except Exception:
        pass
    expect("a second recording into the same file keeps the first and parses", r1.returncode == 0 and r2.returncode == 0 and len(list(gg.subjects(RDF.type, B.MetricObservation))) == 2)
    expect("the same observation twice (same objective, time, register) is refused, not written with two values", r3.returncode == 2 and "already holds" in r3.stderr and len(list(gg.subjects(RDF.type, B.MetricObservation))) == 2)
    op2 = os.path.join(d, "empty.ttl"); open(op2, "w").close()
    r4 = subprocess.run([sys.executable, TOOL, rp, "--objective", "Obj_C", "--record", op2], capture_output=True, text=True)
    g4 = Graph()
    try:
        g4.parse(op2, format="turtle"); okp = len(list(g4.subjects(RDF.type, B.MetricObservation))) == 1
    except Exception:
        okp = False
    expect("recording into an existing empty file writes a file that parses", r4.returncode == 0 and okp)
    r5 = subprocess.run([sys.executable, TOOL, rp, "--objective", "Obj_C", "--at", 'yesterday"x'], capture_output=True, text=True)
    expect("a time that is not a UTC time is refused", r5.returncode == 2 and "UTC" in r5.stderr)
    r6 = subprocess.run([sys.executable, TOOL, rp, "--objective", "Obj_C", "--record", os.path.join(d, "nope", "o.ttl")], capture_output=True, text=True)
    expect("a record path in a missing folder is refused before any value is printed", r6.returncode == 2 and "Obj_C =" not in r6.stdout and "Traceback" not in r6.stderr)
rc, o, e, rec, _ = run(HEAD + obj("Obj_E", 'SELECT ("12" AS ?n) WHERE {}'), ["--objective", "Obj_E", "--record", "@O"])
expect("a number written as a string is not a number and is refused", rc == 2 and "Obj_E =" not in o and "number" in e and rec is None)
import http.server, threading
hits = []
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self): hits.append(1); self.send_response(200); self.end_headers()
    do_POST = do_GET
    def log_message(self, *a): pass
srv = http.server.HTTPServer(("127.0.0.1", 0), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
rc, o, e, rec, _ = run(HEAD + obj("Obj_E", "SELECT (COUNT(?s) AS ?n) WHERE { SERVICE <http://127.0.0.1:%d/q> { ?s a backlog:Story } }" % srv.server_port), ["--objective", "Obj_E"])
srv.shutdown()
expect("a stored query never opens a network connection (a local server saw no request)", rc == 2 and not hits)
# -- third round (second review of box 57): inputs, exact output, files that are not the tool's own
import re as _re
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", COUNT), ["--objective", "Obj_C", "--record", "@O"])
expect("the printed line gives exactly the value (3, not 30 or 3.0)", rc == 0 and _re.search(r"(?m)^Obj_C = 3   \[query run on the register r_v1_2_3\.ttl \(version 1\.2\.3, sha256 [0-9a-f]{64}\)\]$", o) is not None)
expect("the tool says how many observations it recorded", "recorded 1 observation(s) in" in o)
rc, o, e, rec, raw = run(HEAD + obj("Obj_C", COUNT), ["--objective", "Obj_C", "--record", "@O"])
expect("the observation identifier carries the first eight hex digits of the register digest", rec is not None and ("_" + hashlib.sha256(raw).hexdigest()[:8] + ">") in rec)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", COUNT), ["--objective", "Obj_C"], name="reg.ttl")
expect("a register path with no version in its name is read and said to be unversioned", rc == 0 and "version unversioned" in o)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", 'SELECT (COUNT(?s) AS ?n) WHERE { ?s a backlog:Story . FILTER(STR(?s) != "a\\\\b\\"c") }'), ["--objective", "Obj_C", "--record", "@O"])
mm = ""
try:
    mm = str(next(obsgraph(rec).objects(None, B.hasObservationMethod)))
except Exception:
    pass
expect("a quote and a backslash in the stored query are escaped in the record, which parses and cites the query whole", rc == 0 and 'FILTER(STR(?s) != "a\\\\b\\"c")' in mm)
rc, o, e, rec, _ = run(HEAD + obj("Obj_E", "SELECT (1 AS ?a) (2 AS ?b) WHERE {}"), ["--objective", "Obj_E"])
expect("a result with two columns is refused even when the first is a number", rc == 2 and "column" in e and "Obj_E =" not in o)
rc, o, e, rec, _ = run(HEAD + obj("Obj_E", "SELECT ?n WHERE { ?s a backlog:Nothing . BIND(1 AS ?n) }"), ["--objective", "Obj_E"])
expect("a result with no row is refused", rc == 2 and "row" in e and "Obj_E =" not in o)
rc, o, e, rec, _ = run(HEAD + obj("Obj_E", "SELECT (-2 AS ?n) WHERE {}"), ["--objective", "Obj_E", "--record", "@O"])
gg = obsgraph(rec) if rec else None
val = next(gg.objects(None, B.hasObservedValue)) if gg else None
expect("a negative value is printed and recorded as it is", rc == 0 and "Obj_E = -2 " in o and val is not None and str(val) == "-2.0")
NOPFX = ("@prefix fw: <http://example.org/probe#> .\nfw:S1 a <http://example.org/backlog#Story> . fw:M a <http://example.org/core#Metric> .\n"
         'fw:Obj_Q a <http://example.org/backlog#Objective> ; <http://example.org/backlog#hasSuccessMetric> fw:M ; <http://example.org/backlog#hasMeasurementQuery> "SELECT (COUNT(?s) AS ?n) WHERE { ?s a backlog:Story }" .\n')
rc, o, e, rec, _ = run(NOPFX, ["--objective", "Obj_Q"])
expect("a register that declares no backlog prefix still answers a query written with it", rc == 0 and "Obj_Q = 1" in o)
rc, o, e, rec, _ = run(HEAD + obj("Obj_L", COUNT) + "fw:Obj_L backlog:hasMeasurementQuery 'SELECT (COUNT(?s) AS ?n) WHERE { ?s a backlog:Story } LIMIT 2' .\n", ["--objective", "Obj_L"])
expect("an objective with two stored queries is refused, not run by guess", rc == 2 and "2 measurement queries" in e and "Obj_L =" not in o)
rc, o, e, rec, _ = run(HEAD + obj("Obj_L", COUNT) + "fw:Obj_L backlog:hasSuccessMetric fw:M2 .\n", ["--objective", "Obj_L", "--record", "@O"])
expect("an objective with two success metrics is refused, not recorded by guess", rc == 2 and "2 success metrics" in e and rec is None)
with tempfile.TemporaryDirectory() as d:
    rp = os.path.join(d, "r_v1_0_0.ttl"); open(rp, "w").write(HEAD + obj("Obj_C", COUNT))
    op = os.path.join(d, "other.ttl"); open(op, "w").write("@prefix ex: <http://ex/> .\nex:a ex:b ex:c .\n")
    r = subprocess.run([sys.executable, TOOL, rp, "--objective", "Obj_C", "--record", op], capture_output=True, text=True)
    g5 = Graph()
    try:
        g5.parse(op, format="turtle"); okp = len(list(g5.subjects(RDF.type, B.MetricObservation))) == 1
    except Exception:
        okp = False
    expect("recording into a file that holds other Turtle keeps it and writes a file that parses", r.returncode == 0 and okp)
    def clean(args, what, word=None):
        r = subprocess.run([sys.executable, TOOL] + args, capture_output=True, text=True)
        expect("%s is refused cleanly (exit 2, a reason, no traceback, no value printed)" % what, r.returncode == 2 and "REFUSED" in r.stderr and "Traceback" not in r.stderr and "Obj_C =" not in r.stdout and (word is None or word in r.stderr))
    clean([rp, "--objective", "Obj_C", "--record", d], "a record path that is a folder", "folder")
    clean([rp, "--objective", "Obj_C", "--record", "/proc/none.ttl"], "a record path that cannot be written", "cannot write")
    clean([os.path.join(d, "missing.ttl"), "--objective", "Obj_C"], "a missing register", "cannot read")
    bad = os.path.join(d, "bad_v1_0_0.ttl"); open(bad, "w").write("this is not turtle {")
    clean([bad, "--objective", "Obj_C"], "a register that is not Turtle", "cannot read")
    clean([rp, "--objective", "Obj_C", "--archive", bad], "an archive that is not Turtle", "cannot read")
    clean([rp, "--objective"], "an option with no value", "needs a value")
# -- fourth round (third review of box 57): a record file that is not Turtle; a duplicate held in prefixed form
with tempfile.TemporaryDirectory() as d:
    rp = os.path.join(d, "r_v1_0_0.ttl"); open(rp, "w").write(HEAD + obj("Obj_C", COUNT))
    bp = os.path.join(d, "broken.ttl"); open(bp, "w").write("ex:a ex:b ex:c .\n")
    r = subprocess.run([sys.executable, TOOL, rp, "--objective", "Obj_C", "--record", bp], capture_output=True, text=True)
    expect("recording into a file that is not Turtle is refused and leaves it as it was", r.returncode == 2 and "not Turtle" in r.stderr and "Obj_C =" not in r.stdout and open(bp).read() == "ex:a ex:b ex:c .\n")
    op = os.path.join(d, "obs.ttl")
    r1 = subprocess.run([sys.executable, TOOL, rp, "--objective", "Obj_C", "--at", "2026-01-01T00:00:00Z", "--record", op], capture_output=True, text=True)
    txt = open(op).read()
    pm = _re.search(r"<(http[^>]*#)(Obs_[^>]*)>", txt)
    txt2 = txt.replace(pm.group(0), "fw2:" + pm.group(2)).replace("@prefix backlog:", "@prefix fw2: <" + pm.group(1) + "> .\n@prefix backlog:", 1)
    open(op, "w").write(txt2)
    r2 = subprocess.run([sys.executable, TOOL, rp, "--objective", "Obj_C", "--at", "2026-01-01T00:00:00Z", "--record", op], capture_output=True, text=True)
    expect("a duplicate observation held in prefixed form is found and refused", r1.returncode == 0 and r2.returncode == 2 and "already holds" in r2.stderr and open(op).read() == txt2)
# -- fifth round (fourth review of box 57)
hits2 = []
class H2(http.server.BaseHTTPRequestHandler):
    def do_GET(self): hits2.append(1); self.send_response(200); self.end_headers()
    do_POST = do_GET
    def log_message(self, *a): pass
srv2 = http.server.HTTPServer(("127.0.0.1", 0), H2); threading.Thread(target=srv2.serve_forever, daemon=True).start()
q = "SELECT (COUNT(?s) AS ?n) WHERE { \\u0053ERVICE <http://127.0.0.1:%d/q> { ?s a backlog:Story } }" % srv2.server_port
rc, o, e, rec, _ = run(HEAD + obj("Obj_E", q), ["--objective", "Obj_E"])
srv2.shutdown()
expect("a service call hidden by a unicode escape is refused and opens no connection", rc == 2 and not hits2 and "Obj_E =" not in o)
rc, o, e, rec, _ = run(HEAD + obj("Obj_E", 'SELECT ("abc"^^<http://www.w3.org/2001/XMLSchema#integer> AS ?n) WHERE {}'), ["--objective", "Obj_E"])
expect("an ill-typed number is refused with a reason and no traceback", rc == 2 and "REFUSED" in e and "Traceback" not in e and "Obj_E =" not in o)
for bad in ("2026-13-45T99:99:99Z", "2026-02-30T10:00:00Z"):
    rc, o, e, rec, _ = run(HEAD + obj("Obj_C", COUNT), ["--objective", "Obj_C", "--at", bad, "--record", "@O"])
    expect("an impossible time %s is refused and nothing is recorded" % bad, rc == 2 and "REFUSED" in e and rec is None and "Obj_C =" not in o)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", COUNT), ["--objective", "Obj_C", "--at", "2026-11-17T12:00:00Z", "--record", "@O"])
expect("a good time is kept as given with its Z", rc == 0 and rec is not None and '"2026-11-17T12:00:00Z"^^xsd:dateTime' in rec)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", COUNT), ["--objective", "Obj_C", "--record", "@O"])
expect("the default time is written in UTC with its Z", rec is not None and _re.search(r'backlog:observedAt "\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ"\^\^xsd:dateTime', rec) is not None)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", COUNT) + obj("Obj_D", COUNT), ["--all", "--record", "@O"])
ids = _re.findall(r"<[^>]*#(Obs_[^>]*)>", rec or "")
expect("every observation of --all carries its objective in its identifier and the identifiers differ", len(ids) == 2 and len(set(ids)) == 2 and any(x.startswith("Obs_Obj_C_") for x in ids) and any(x.startswith("Obs_Obj_D_") for x in ids) and "recorded 2 observation(s)" in o)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", COUNT, label="Same") + obj("Obj_D", COUNT, label="Same"), ["--objective", "Same"])
expect("a label that names two objectives is refused, not resolved by taking the first", rc == 2 and "more than one" in e and "Same =" not in o)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", COUNT), ["--objective", "Obj_C", "--all"])
expect("--objective together with --all is refused with a reason", rc == 2 and "REFUSED" in e and "Obj_C =" not in o)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", COUNT), [])
expect("no option at all is refused with a reason line", rc == 2 and "REFUSED" in e)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", "SELECT (COUNT(?s) AS ?n) WHERE {   ?s   a   backlog:Story\n }"), ["--objective", "Obj_C", "--record", "@O"])
expect("the stored query is cited with its whitespace normalised to single spaces", rec is not None and "WHERE { ?s a backlog:Story }" in rec)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", COUNT), ["--objective", "Obj_C"], name="x_v1_0_0_v2_0_1.ttl")
expect("the version is the last one in the file name", rc == 0 and "version 2.0.1" in o and "version 1.0.0" not in o)
with tempfile.TemporaryDirectory() as d:
    rp = os.path.join(d, "r_v1_0_0.ttl"); open(rp, "w").write(HEAD + obj("Obj_C", COUNT))
    ap = os.path.join(d, "arch_v7_0_0.ttl"); open(ap, "w").write("@prefix fw: <http://example.org/probe#> .\nfw:Z a fw:Z .\n")
    r = subprocess.run([sys.executable, TOOL, rp, "--archive", ap, "--objective", "Obj_C"], capture_output=True, text=True)
    dg = hashlib.sha256(open(ap, "rb").read()).hexdigest(); dr = hashlib.sha256(open(rp, "rb").read()).hexdigest()
    expect("the archive is cited with its own digest and version, the register with its own", ("arch_v7_0_0.ttl (version 7.0.0, sha256 " + dg + ")") in r.stdout and ("r_v1_0_0.ttl (version 1.0.0, sha256 " + dr + ")") in r.stdout)
    before = open(rp).read()
    for tgt, nm in ((rp, "the register"), (ap, "an archive")):
        b0 = open(tgt).read()
        r = subprocess.run([sys.executable, TOOL, rp, "--archive", ap, "--objective", "Obj_C", "--record", tgt], capture_output=True, text=True)
        expect("recording into %s it cites is refused and leaves it as it was" % nm, r.returncode == 2 and "REFUSED" in r.stderr and open(tgt).read() == b0 and "Obj_C =" not in r.stdout)
    r = subprocess.run([sys.executable, TOOL, rp, "--objective", "Obj_C", "--record", "/dev/full"], capture_output=True, text=True)
    expect("a write that fails at the end is refused, never reported as recorded", r.returncode == 2 and "recorded" not in r.stdout and "Traceback" not in r.stderr and "Obj_C =" not in r.stdout)
    r = subprocess.run([sys.executable, TOOL, "nonexistent_register.ttl", "--objective", "Obj_C"], capture_output=True, text=True, cwd=d)
    expect("a missing relative register is named as given in the reason", r.returncode == 2 and "nonexistent_register.ttl" in r.stderr and os.path.dirname(d) not in r.stderr.replace(d, "") and "Errno" not in r.stderr)
rc, o, e, rec, _ = run(HEAD.replace("fw:M a core:Metric .", "") + "fw:Obj_Z a backlog:Objective ; backlog:hasSuccessMetric 5 ; backlog:hasMeasurementQuery \"" + COUNT + "\" .\n", ["--objective", "Obj_Z", "--record", "@O"])
expect("a success metric that is a literal is refused, not turned into an invalid identifier", rc == 2 and "REFUSED" in e and rec is None)
rc, o, e, rec, _ = run(HEAD + "[ a backlog:Objective ; backlog:hasSuccessMetric fw:M ; backlog:hasMeasurementQuery \"" + COUNT + "\" ] .\n", ["--all", "--record", "@O"])
expect("an objective that is a blank node is refused, not recorded against an invalid identifier", rc == 2 and "REFUSED" in e and rec is None)
# -- sixth round (fifth review of box 57)
def sub(args, cwd=None, files=None):
    with tempfile.TemporaryDirectory() as d:
        paths = {}
        for k, v in (files or {}).items():
            paths[k] = os.path.join(d, k); open(paths[k], "wb").write(v if isinstance(v, bytes) else v.encode())
        a = [paths.get(x, x) for x in args]
        r = subprocess.run([sys.executable, TOOL] + a, capture_output=True, text=True, cwd=d)
        return r, d
REG = HEAD + obj("Obj_C", COUNT)
r, d = sub(["reg_v1_0_0.ttl", "--objective", "Obj_C", "--record", ""], files={"reg_v1_0_0.ttl": REG})
expect("--record with an empty value is refused", r.returncode == 2 and "needs a value" in r.stderr and "Obj_C =" not in r.stdout)
r, d = sub(["reg_v1_0_0.ttl", "--objective", "Obj_C", "--at", "\uff12\uff10\uff12\uff16-01-01T00:00:00Z", "--record", "o.ttl"], files={"reg_v1_0_0.ttl": REG})
expect("--at with non-ASCII digits is refused and nothing is recorded", r.returncode == 2 and not os.path.exists(os.path.join(d, "o.ttl")))
r, d = sub(["reg_v1_0_0.ttl", "--objective", "Obj_C", "--at", "2099-01-01T00:00:00Z"], files={"reg_v1_0_0.ttl": REG})
expect("--at in the future is refused", r.returncode == 2 and "future" in r.stderr)
r, d = sub(["reg_v1_0_0.ttl", "--objective", "Obj_C", "--objective", "Obj_D"], files={"reg_v1_0_0.ttl": REG})
expect("an option given twice is refused, the last does not win silently", r.returncode == 2 and "twice" in r.stderr)
for nm in ("nl\nreg_v1_0_0.ttl", "cr\rreg_v1_0_0.ttl", "tab\treg_v1_0_0.ttl"):
    with tempfile.TemporaryDirectory() as d:
        rp = os.path.join(d, nm); open(rp, "w").write(REG)
        op = os.path.join(d, "o.ttl"); open(op, "w").write("@prefix ex: <http://ex/> .\nex:a ex:b ex:c .\n")
        r = subprocess.run([sys.executable, TOOL, rp, "--objective", "Obj_C", "--record", op], capture_output=True, text=True)
        gg = obsgraph(open(op).read())
        expect("a register file name with a control character (%r) leaves a record that parses" % nm, r.returncode == 0 and len(list(gg.subjects(RDF.type, B.MetricObservation))) == 1)
with tempfile.TemporaryDirectory() as d:
    rp = os.path.join(d.encode(), b"lat1\xffx_v1_0_0.ttl"); open(rp, "w").write(REG)
    r = subprocess.run([sys.executable, TOOL.encode(), rp, b"--objective", b"Obj_C", b"--record", os.path.join(d.encode(), b"o.ttl")], capture_output=True)
    expect("a register file name that is not UTF-8 is handled without a traceback and the record parses", r.returncode == 0 and b"Traceback" not in r.stderr and len(list(obsgraph(open(os.path.join(d, "o.ttl")).read()).subjects(RDF.type, B.MetricObservation))) == 1)
rc, o, e, rec, _ = run(HEAD + obj("Obj_A", COUNT) + obj("A", COUNT), ["--all", "--record", "@O", "--at", "2026-01-01T00:00:00Z"])
ids = _re.findall(r"<[^>]*#(Obs_[^>]*)>", rec or "")
expect("objectives whose names differ only by Obj_ get different observations", len(ids) == 2 and len(set(ids)) == 2)
with tempfile.TemporaryDirectory() as d:
    rp = os.path.join(d, "reg_v1_0_0.ttl"); open(rp, "w").write(REG)
    ap = os.path.join(d, "arc_v2_0_0.ttl"); open(ap, "w").write("@prefix backlog: <http://example.org/backlog#> . @prefix fw: <http://example.org/probe#> . fw:X1 a backlog:Story .\n")
    op = os.path.join(d, "a.ttl")
    r1 = subprocess.run([sys.executable, TOOL, rp, "--objective", "Obj_C", "--record", op, "--at", "2026-01-01T00:00:00Z"], capture_output=True, text=True)
    r2 = subprocess.run([sys.executable, TOOL, rp, "--archive", ap, "--objective", "Obj_C", "--record", op, "--at", "2026-01-01T00:00:00Z"], capture_output=True, text=True)
    gg = obsgraph(open(op).read())
    expect("the same run with an archive is a different measurement: both are recorded, with different identifiers", r1.returncode == 0 and r2.returncode == 0 and len(set(gg.subjects(RDF.type, B.MetricObservation))) == 2)
for dup in (["--record", "x.ttl", "--record", "y.ttl"], ["--at", "2026-01-01T00:00:00Z", "--at", "2026-01-02T00:00:00Z"]):
    r, d = sub(["reg_v1_0_0.ttl", "--objective", "Obj_C"] + dup, files={"reg_v1_0_0.ttl": REG})
    expect("%s given twice is refused" % dup[0], r.returncode == 2 and "twice" in r.stderr)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", COUNT) + obj("Obj_N", None), ["--all"])
expect("--all names the objectives that carry no query", rc == 0 and "Obj_N" in o and "not run (no stored query): 1" in o)
for what, qq in (("a string", 'SELECT (COUNT(?s) AS ?n) WHERE { ?s a backlog:Story FILTER(STR(?s) != "SERVICE") }'), ("a comment", "SELECT (COUNT(?s) AS ?n) WHERE { ?s a backlog:Story } # SERVICE")):
    rc, o, e, rec, _ = run(HEAD + obj("Obj_C", qq), ["--objective", "Obj_C"])
    expect("the word SERVICE in %s does not make a local query a refused one" % what, rc == 0 and "Obj_C = 3" in o)
for what, qq in (("EXISTS", 'SELECT (COUNT(?s) AS ?n) WHERE { ?s a backlog:Story FILTER EXISTS { SERVICE <http://127.0.0.1:1/q> { ?s ?p ?o } } }'), ("OPTIONAL", 'SELECT (COUNT(?s) AS ?n) WHERE { ?s a backlog:Story OPTIONAL { SERVICE SILENT <http://127.0.0.1:1/q> { ?s ?p ?o } } }'), ("a subquery", 'SELECT (COUNT(?s) AS ?n) WHERE { { SELECT ?s WHERE { SERVICE <http://127.0.0.1:1/q> { ?s ?p ?o } } } }')):
    rc, o, e, rec, _ = run(HEAD + obj("Obj_C", qq), ["--objective", "Obj_C"])
    expect("a service call inside %s is refused" % what, rc == 2 and "service" in e and "Obj_C =" not in o)
for fn in ("RAND()", "NOW()", "STRUUID()", "BNODE()"):
    rc, o, e, rec, _ = run(HEAD + obj("Obj_C", "SELECT (COUNT(?s) + STRLEN(STR(%s)) * 0 AS ?n) WHERE { ?s a backlog:Story }" % fn), ["--objective", "Obj_C"])
    expect("a query calling %s is refused: its value cannot be re-derived" % fn, rc == 2 and "re-derived" in e and "Obj_C =" not in o)
rc, o, e, rec, _ = run(HEAD + obj("Obj_C", "SELECT (COUNT(?s) AS ?n) FROM <http://127.0.0.1:1/x> WHERE { ?s a backlog:Story }"), ["--objective", "Obj_C"])
expect("a query naming its own dataset (FROM) is refused", rc == 2 and "FROM" in e and "Obj_C =" not in o)
rc, o, e, rec, _ = run(HEAD + 'fw:Obj_C a backlog:Objective ; rdfs:label "Alpha"@en , "Birinci"@tr ; backlog:hasSuccessMetric fw:M ; backlog:hasMeasurementQuery "' + COUNT + '" .\n', ["--objective", "Birinci"])
expect("an objective with two labels is found by either", rc == 0 and "Obj_C = 3" in o)
r, d = sub(["reg_v1_0_0.ttl", "--objective", "Obj_C", "--record", "/dev/null"], files={"reg_v1_0_0.ttl": REG})
expect("recording into a file that is not a regular file is refused", r.returncode == 2 and "regular" in r.stderr)
with tempfile.TemporaryDirectory() as d:
    a1 = os.path.join(d, "a1_v1_0_0.ttl"); open(a1, "w").write("@prefix backlog: <http://example.org/backlog#> . @prefix fw: <http://example.org/probe#> . fw:X1 a backlog:Story .\n")
    a2 = os.path.join(d, "a2_v2_0_0.ttl"); open(a2, "w").write("@prefix backlog: <http://example.org/backlog#> . @prefix fw: <http://example.org/probe#> . fw:X2 a backlog:Story . fw:X3 a backlog:Story .\n")
    rp = os.path.join(d, "reg_v3_0_0.ttl"); open(rp, "w").write(REG); op = os.path.join(d, "o.ttl")
    r = subprocess.run([sys.executable, TOOL, rp, "--archive", a1, "--archive", a2, "--objective", "Obj_C", "--record", op, "--at", "2026-01-01T00:00:00Z"], capture_output=True, text=True)
    gg = obsgraph(open(op).read()) if os.path.exists(op) else Graph()
    mm = str(next(gg.objects(None, B.hasObservationMethod), ""))
    expect("two archives are both read (3 + 1 + 2 = 6 stories) and both cited", r.returncode == 0 and "Obj_C = 6" in r.stdout and "a1_v1_0_0.ttl (version 1.0.0" in mm and "a2_v2_0_0.ttl (version 2.0.0" in mm)
    expect("the method states the time of the run", " at 2026-01-01T00:00:00Z;" in mm)
    lb = str(next(gg.objects(None, RDFS.label), ""))
    expect("the observation label names the objective", lb == "Query run: Obj_C")
os.makedirs("/tmp/probe_v9_9_9_dir", exist_ok=True)
with tempfile.TemporaryDirectory(prefix="x_v9_9_9_") as d:
    rp = os.path.join(d, "reg.ttl"); open(rp, "w").write(REG)
    r = subprocess.run([sys.executable, TOOL, rp, "--objective", "Obj_C"], capture_output=True, text=True)
    expect("a version-like folder name does not give the register a version", "version unversioned" in r.stdout)
rc, o, e, rec, _ = run(HEAD + "".join("fw:S%d a backlog:Story .\n" % i for i in range(10, 17)) + obj("Obj_C", COUNT), ["--objective", "Obj_C"])
expect("a value of ten or more is printed whole", rc == 0 and "Obj_C = 10 " in o)
print("VERDICT: %s -- %d expectations %s" % ("PASS" if not FAILS else "FAIL", N[0], "hold" if not FAILS else "(%d failed)" % len(FAILS)))
sys.exit(1 if FAILS else 0)
