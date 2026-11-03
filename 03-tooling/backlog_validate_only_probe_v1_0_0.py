#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe reads no record of the framework register; the validator keeps only the controlled individuals)
"""backlog_validate_only_probe v1.0.0 -- proves the restricted validation of backlog_validate v1.19.0 changes no verdict (Lineage 31, story Probes).

BACKLOG_VALIDATE_ONLY_MESSAGE=TEXT judges only the top-level shapes carrying TEXT. Each case is a tiny register judged twice, whole and restricted.
  1  a planted fault: the violation lines carrying the text are the same whole and restricted        (fires)
  2  a clean case: no line carries the text whole, none restricted                                    (silent)
  3  two texts joined by the separator judge both shapes, and each line equals the whole run's       (several shapes)
  4  a text carried by no shape is REFUSED (exit 2), never read as silence                            (no vacuous pass)
  5  a restricted run says RESTRICTED and never CONFORMANT, so a partial run is not taken for a verdict
  7  one text of several that no shape carries is refused too
  8  the gate unsets the variable at its start and lists this probe once
  6  with one memo directory a restricted and a whole run of the same data never replay each other
Exit 0 when every expectation holds, 1 otherwise."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    for pat in ("03-tooling/backlog_validate_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl", "01-ontologies/backlog_abox_v*.ttl"):
        print(latest(pat))
    print(os.path.abspath(__file__)); sys.exit(0)
val = latest("03-tooling/backlog_validate_v*.py")
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/validate-only-probe#> .\n"
REG = "x:Reg a backlog:Backlog ; backlog:isRegisterRoot true ; backlog:adoptsRuleSet backlog:RS_FlowPointsRecorded .\nx:P a backlog:Executor_IndividualHuman .\n"
W = lambda state, extra: f'x:W a backlog:Task ; backlog:hasState backlog:{state} ; backlog:responsible x:P ; {extra} .\n'
A, B = '"2026-10-14T09:00:00Z"^^xsd:dateTime', '"2026-10-14T11:00:00Z"^^xsd:dateTime'
M1 = "G115: this work item carries a startedAt or finishedAt that its state cannot have"
M2 = "G115: this work item's startedAt equals its finishedAt"
FAULT = REG + W("Proposed", f"backlog:startedAt {A}") + 'x:V a backlog:Task ; backlog:hasState backlog:Done ; backlog:responsible x:P ; backlog:startedAt ' + B + ' ; backlog:finishedAt ' + B + ' .\n'
CLEAN = REG + W("Done", f"backlog:startedAt {A} ; backlog:finishedAt {B}")
bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
def run(body, only=None):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(HEAD + body)
        env = dict(os.environ); env.pop("BACKLOG_VALIDATE_ONLY_MESSAGE", None)
        if only is not None: env["BACKLOG_VALIDATE_ONLY_MESSAGE"] = only
        r = subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=900, env=env)
    return r.returncode, r.stdout
lines = lambda out, keys: sorted(re.sub(r"\s+", " ", l) for l in out.splitlines() if "[Violation]" in l and any(k in l for k in keys))
rc_w, whole = run(FAULT); rc_r, restr = run(FAULT, M1)
expect("1 planted fault: the lines carrying the text are equal whole and restricted, and not empty", lines(whole, [M1]) == lines(restr, [M1]) and len(lines(whole, [M1])) == 1)
rc_w2, whole2 = run(CLEAN); rc_r2, restr2 = run(CLEAN, M1)
expect("2 clean case: silent whole and restricted", not lines(whole2, [M1]) and not lines(restr2, [M1]))
rc_s, several = run(FAULT, M1 + "\x1e" + M2)
expect("3 two texts: both shapes judged, lines equal the whole run's", lines(several, [M1, M2]) == lines(whole, [M1, M2]) and len(lines(whole, [M1, M2])) == 2)
rc_n, none = run(FAULT, "no shape carries this text 7f3a")
expect("4 a text no shape carries is refused, exit 2, no verdict of silence", rc_n == 2 and "CONFORMANT" not in none.replace("NON-CONFORMANT", ""))
expect("5 a restricted run says RESTRICTED, never CONFORMANT", "VERDICT     : RESTRICTED" in restr and "VERDICT     : CONFORMANT" not in restr2 and "VERDICT     : RESTRICTED" in restr2)
# 6 with one memo directory, a restricted run and a whole run of the same data never replay each other (the whole-run memo is keyed by the restriction)
with tempfile.TemporaryDirectory() as md:
    def run_memo(body, only):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "s.ttl"); open(f, "w").write(HEAD + body)
            env = dict(os.environ, BACKLOG_VALIDATE_MEMO_DIR=md); env.pop("BACKLOG_VALIDATE_ONLY_MESSAGE", None)
            if only is not None: env["BACKLOG_VALIDATE_ONLY_MESSAGE"] = only
            return subprocess.run([sys.executable, val, f], capture_output=True, text=True, timeout=900, env=env).stdout
    a1 = run_memo(CLEAN, M1); a2 = run_memo(CLEAN, None); a3 = run_memo(CLEAN, M1)
    expect("6 one memo directory: restricted, whole, restricted again each give their own verdict", "RESTRICTED" in a1 and "RESTRICTED" not in a2 and "RESTRICTED" in a3)
rc_u, uns = run(FAULT, M1 + "\x1e" + "no shape carries this text 7f3a")
expect("7 one text of several that no shape carries is refused too, exit 2", rc_u == 2 and "VERDICT" not in uns)
gate = latest("03-tooling/backlog_gate_v*.sh"); gt = open(gate, encoding="utf-8").read()
expect("8 the gate unsets the variable at its start and lists this probe once", re.search(r"^unset BACKLOG_VALIDATE_ONLY_MESSAGE$", gt, re.M) is not None and gt.count("backlog_validate_only_probe") >= 1 and len(re.findall(r"\bbacklog_validate_only_probe\b", re.search(r"^PROBE_LIST=.*$", gt, re.M).group(0))) == 1)
print("validator :", os.path.basename(val)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
