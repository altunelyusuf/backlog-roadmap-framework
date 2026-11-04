#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe reads no record of the framework register; it builds a scratch register)
"""backlog_forecast_discussed_probe v1.0.0 -- a forecast behind a checkpoint is recorded as discussed (G198; Lineage 29, story ForecastRecord).
Scratch register, real validator and real shapes. A lineage that adopts the rule set:
  Ok        forecast with a discussion record (who, when, not before it was made)      -> not refused
  NoRecord  forecast with none                                                         -> refused
  Early     discussion dated before the forecast was made                               -> refused
  NoWho     a time and no one                                                           -> refused
A lineage that did not adopt it, forecast with none (Outside)                          -> not refused (the rule binds only adopters)
Exit 0 when every expectation holds, 1 otherwise."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
VAL = latest("03-tooling/backlog_validate_v*.py")
if sys.argv[1:] == ["--deps"]:
    for pat in ("03-tooling/backlog_validate_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl", "01-ontologies/backlog_abox_v*.ttl"): print(latest(pat))
    print(os.path.abspath(__file__)); sys.exit(0)
X = "^^xsd:dateTime"
PRE = '@prefix backlog: <http://example.org/backlog#> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> . @prefix ex: <http://example.org/fdprobe#> .\nex:LOn a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_ForecastDiscussed ; backlog:humanApprovalLevel 3 .\nex:LOff a backlog:Lineage ; backlog:humanApprovalLevel 3 .\n'
def case(n, lin, extra):
    return ('ex:O_%s a backlog:Objective ; backlog:belongsToLineage ex:%s ; backlog:hasCheckpoint ex:C_%s .\nex:C_%s a backlog:ObjectiveCheckpoint ; backlog:checkpointDate "2026-11-05T00:00:00Z"%s ; backlog:datePredictedBy ex:F_%s .\n'
            'ex:F_%s a backlog:Forecast ; backlog:forecastMadeAt "2026-11-04T06:40:00Z"%s ; backlog:forecastCompletion "2026-11-04T10:00:00Z"%s ; backlog:forecastAssumption "x" ; backlog:forecastObservedVelocity 1.5%s .\n' % (n, lin, n, n, X, n, n, X, X, extra))
CASES = [("Ok", "LOn", ' ; backlog:forecastDiscussedAt "2026-11-04T07:00:00Z"%s ; backlog:forecastDiscussedBy backlog:Owner' % X, False),
         ("NoRecord", "LOn", "", True),
         ("Early", "LOn", ' ; backlog:forecastDiscussedAt "2026-11-04T06:00:00Z"%s ; backlog:forecastDiscussedBy backlog:Owner' % X, True),
         ("NoWho", "LOn", ' ; backlog:forecastDiscussedAt "2026-11-04T07:00:00Z"%s' % X, True),
         ("Outside", "LOff", "", False)]
data = PRE + "".join(case(n, l, e) for n, l, e, _ in CASES)
with tempfile.TemporaryDirectory() as d:
    f = os.path.join(d, "s.ttl"); open(f, "w").write(data)
    env = dict(os.environ, BACKLOG_VALIDATE_ONLY_MESSAGE="FD_UNDISCUSSED"); env.pop("BACKLOG_VALIDATE_MEMO_DIR", None)
    out = subprocess.run([sys.executable, VAL, f], capture_output=True, text=True, timeout=600, env=env).stdout
hit = set(re.findall(r"\[Violation\]\s+C_(\w+)\s+FD_UNDISCUSSED", out))
bad = []
for n, l, e, want in CASES:
    ok = (n in hit) == want
    print(("PASS  " if ok else "FAIL  ") + "%s: %s" % (n, "refused" if want else "not refused"))
    if not ok: bad.append(n)
print("VERDICT   :", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
