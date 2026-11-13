#!/usr/bin/env python3
"""Probe of RS_PlannedDates (G186) and backlog_date_plan: the real validator on one scratch register in which each checkpoint lacks exactly one thing, and the prediction tool on a planted register
whose velocity and completion are computed by hand."""
import glob, re, subprocess, sys, tempfile, os, datetime
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", p)[0]]
VAL = sorted(glob.glob(PKG + "/03-tooling/backlog_validate_v*.py"), key=sv)[-1]
TOOL = sorted(glob.glob(PKG + "/03-tooling/backlog_date_plan_v*.py"), key=sv)[-1]
PRE = """@prefix backlog: <http://example.org/backlog#> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> . @prefix ex: <http://example.org/pdprobe#> .
ex:LinOn a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_PlannedDates ; backlog:humanApprovalLevel 3 .
ex:LinOff a backlog:Lineage ; backlog:humanApprovalLevel 3 .
"""
fails = 0
def expect(label, ok):
    global fails
    print(("PASS  " if ok else "FAIL  ") + label); fails += (not ok)
def case(name, lin="LinOn", date="2026-11-04T00:00:00Z", forecast="full", fc="2026-11-03T12:00:00Z", dtype="xsd:dateTime", fid=None, vel="3.3", assume="pace of earlier boxes", made="2026-11-02T09:00:00Z", extra="", ftype="a backlog:Forecast"):
    fid = fid or f"F_{name}"
    s = f"ex:O_{name} a backlog:Objective ; backlog:belongsToLineage ex:{lin} ; backlog:hasCheckpoint ex:C_{name} .\nex:C_{name} a backlog:ObjectiveCheckpoint ; backlog:checkpointDate \"{date}\"^^{dtype}" if date else f"ex:O_{name} a backlog:Objective ; backlog:belongsToLineage ex:{lin} ; backlog:hasCheckpoint ex:C_{name} .\nex:C_{name} a backlog:ObjectiveCheckpoint"
    if forecast != "none": s += f" ; backlog:datePredictedBy ex:{fid}"
    s += " .\n"
    if forecast != "none":
        s += f"ex:{fid} {ftype} ; backlog:forecastFor ex:Reg ; backlog:forecastMadeAt \"{made}\"^^xsd:dateTime ; backlog:forecastCompletion \"{fc}\"^^xsd:dateTime"
        if forecast != "noassumption": s += f" ; backlog:forecastAssumption \"{assume}\""
        if forecast != "novelocity": s += f" ; backlog:forecastObservedVelocity \"{vel}\"^^xsd:decimal"
        s += " .\n"
    return s + extra.replace("NAME", name)
CASES = [("Ok", {}, None), ("NoForecast", {"forecast": "none"}, "PD_UNPLANNED"), ("NoVelocity", {"forecast": "novelocity"}, "PD_UNPLANNED"),
         ("NoAssumption", {"forecast": "noassumption"}, "PD_UNPLANNED"), ("EarlierThanForecast", {"date": "2026-11-03T00:00:00Z"}, "PD_UNPLANNED"),
         ("SameAsForecast", {"date": "2026-11-03T12:00:00Z"}, None),
         ("EmptyAssumption", {"assume": ""}, "PD_UNPLANNED"), ("SpacesAssumption", {"assume": "   "}, "PD_UNPLANNED"), ("NoDate", {"date": ""}, "PD_UNPLANNED"), ("ZeroVelocity", {"vel": "0"}, "PD_UNPLANNED"), ("MadeAfterCompletion", {"made": "2026-11-05T09:00:00Z"}, "PD_UNPLANNED"),
         ("StringDate", {"dtype": "xsd:string"}, "PD_UNPLANNED"), ("SharedForecastA", {"fid": "F_Shared"}, "PD_UNPLANNED"), ("SharedForecastB", {"fid": "F_Shared"}, "PD_UNPLANNED"),
         ("TwoForecasts", {"extra": "ex:C_NAME backlog:datePredictedBy ex:F_Second .\nex:F_Second a backlog:Forecast ; backlog:forecastFor ex:Reg ; backlog:forecastMadeAt \"2026-11-02T09:00:00Z\"^^xsd:dateTime ; backlog:forecastCompletion \"2026-11-03T12:00:00Z\"^^xsd:dateTime ; backlog:forecastAssumption \"x\" ; backlog:forecastObservedVelocity \"2\"^^xsd:decimal .\n"}, "PD_UNPLANNED"), ("Unbound", {"lin": "LinOff", "forecast": "none"}, None)]
data = PRE + "".join(case(n, **k) for n, k, _ in CASES)
with tempfile.NamedTemporaryFile("w", suffix=".ttl", delete=False) as f:
    f.write(data); tmp = f.name
out = subprocess.run([sys.executable, VAL, tmp], capture_output=True, text=True).stdout
os.unlink(tmp)
got = {}
for m in re.finditer(r"\[Violation\]\s+(\S+)\s+(PD_[A-Z_]+):", out):
    got.setdefault(m.group(1), set()).add(m.group(2))
for n, k, want in CASES:
    expect(f"{n}: " + (f"refused as {want}" if want else "raises no PD_ message"), got.get("C_" + n, set()) == ({want} if want else set()))
# the prediction tool on a planted register: three boxes, efforts 2, 3 and 2; starts 00:00, 01:00 and 03:00 on 2026-11-01 -> velocities 2/1 and 3/2 = 2.0, 1.5, median 1.75
REG = """@prefix backlog: <http://example.org/backlog#> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> . @prefix fw: <http://example.org/pdtool#> .
fw:L a backlog:Lineage . fw:Register a backlog:WorkItemContainer .
"""
for i, (h, e) in enumerate([(0, 2), (1, 3), (3, 2)], 1):
    REG += f"fw:It{i} a backlog:Iteration ; backlog:iterationStart \"2026-11-01T0{h}:00:00Z\"^^xsd:dateTime .\nfw:S{i} a backlog:Story ; backlog:hasEffort {float(e)} ; backlog:hasState backlog:Done .\nfw:Ev{i} backlog:plannedInto fw:It{i} ; backlog:plansItem fw:S{i} .\n"
REG += "fw:T1 a backlog:Story ; backlog:hasEffort 3.5 ; backlog:hasState backlog:Proposed .\nfw:O1 a backlog:Objective ; backlog:belongsToLineage fw:L ; backlog:hasCheckpoint fw:C1 ; backlog:metricMovableBy fw:T1 , fw:S1 .\nfw:C1 a backlog:ObjectiveCheckpoint ; backlog:checkpointDate \"2026-11-02T00:00:00Z\"^^xsd:dateTime .\n"
with tempfile.TemporaryDirectory() as d:
    rp = os.path.join(d, "r.ttl"); open(rp, "w").write(REG); em = os.path.join(d, "f.ttl")
    r = subprocess.run([sys.executable, "-I", TOOL, rp, "predict", "--lineage", "L", "--prefix", "T", "--now", "2026-11-02T00:00:00Z", "--buffer", "1.0", "--emit", em], capture_output=True, text=True)
    # 3.5 points still to do (S1 is Done) / 1.75 per hour = 2 hours -> 02:00 on the 2nd, earliest checkpoint the 3rd; the stated 2026-11-02T00:00 is earlier than the forecast
    mixed = REG.replace('"2026-11-01T00:00:00Z"^^xsd:dateTime', '"2026-11-01T00:00:00"^^xsd:dateTime', 1).replace("backlog:hasEffort 2.0", 'backlog:hasEffort "2"^^xsd:decimal', 1)
    rm = os.path.join(d, "m.ttl"); open(rm, "w").write(mixed)
    rx = subprocess.run([sys.executable, "-I", TOOL, rm, "predict", "--lineage", "L", "--prefix", "T", "--now", "2026-11-02T00:00:00Z", "--buffer", "1.0"], capture_output=True, text=True)
    expect("a register that mixes times with and without a zone, and writes an effort as a typed number, is predicted from without a traceback (a time without a zone is read as UTC)", "Traceback" not in rx.stderr and "1.75 delivered points per elapsed hour" in rx.stdout)
    expect("velocity is the median of the pairs of consecutive boxes (1.75 points per elapsed hour)", "1.75 delivered points per elapsed hour" in r.stdout)
    expect("the work still to do is the points of the movers that are not Done (3.5)", "3.5 points" in r.stdout)
    expect("the expected completion is now + points / velocity", "expected 2026-11-02 02:00Z" in r.stdout and "earliest checkpoint 2026-11-03" in r.stdout)
    expect("a stated date earlier than the forecast is named and the tool exits 1", "STATED DATE IS EARLIER THAN FORECAST" in r.stdout and r.returncode == 1)
    expect("the emitted forecast carries the time made, the expected date, the assumption and the velocity", all(x in open(em).read() for x in ("forecastMadeAt", "forecastCompletion", "forecastAssumption", "forecastObservedVelocity", "datePredictedBy")))
    # an objective with no mover is planned from --effort: 3.5 points at 1.75 per hour, buffer 1.0 -> 2 hours
    open(rp, "a").write("fw:O9 a backlog:Objective ; backlog:belongsToLineage fw:L ; backlog:hasCheckpoint fw:C9 .\nfw:C9 a backlog:ObjectiveCheckpoint ; backlog:checkpointDate \"2026-11-09T00:00:00Z\"^^xsd:dateTime .\n")
    r9 = subprocess.run([sys.executable, "-I", TOOL, rp, "predict", "--lineage", "L", "--prefix", "T", "--now", "2026-11-02T00:00:00Z", "--buffer", "1.0", "--effort", "O9=3.5"], capture_output=True, text=True)
    expect("an objective with no mover is planned from the effort given (3.5 points: expected 02:00, earliest checkpoint the 3rd)", any(l.strip().startswith("O9") and "3.5 points" in l and "expected 2026-11-02 02:00Z" in l for l in r9.stdout.splitlines()))
    for label, arg in (("an effort for an objective that does not exist", "O7=2"), ("an effort for an objective that already has movers", "O1=2"), ("an effort with no points", "O9"), ("an effort of zero", "O9=0")):
        rb = subprocess.run([sys.executable, "-I", TOOL, rp, "predict", "--lineage", "L", "--prefix", "T", "--now", "2026-11-02T00:00:00Z", "--effort", arg], capture_output=True, text=True)
        expect(label + " is refused with a message, not a traceback", rb.returncode != 0 and "ERROR" in (rb.stderr + rb.stdout) and "Traceback" not in rb.stderr)
    r2 = subprocess.run([sys.executable, "-I", TOOL, rp, "predict", "--lineage", "Nope"], capture_output=True, text=True)
    expect("an unknown lineage is refused", r2.returncode != 0)
print("VERDICT   :", "PASS" if not fails else "FAIL"); sys.exit(1 if fails else 0)
