#!/usr/bin/env python3
"""backlog_flow_point_git_trace_probe v1.0.0 -- proof that the git comparison discriminates (G115). Builds a throw-away git repository with a register
committed at known author dates, and asserts what backlog_flow_point_git_trace reports for it.

  FUTURE   finished (naive 2026-12-01T18:00:00, read as UTC) after the commit that first recorded it Done (2026-10-14T10:00Z)   -> future_finish, exit 2
  TWO      two different finishedAt                                                                                            -> two_values, exit 2
  EQUAL    start = finish                                                                                                      -> finish_not_after_start (a signal; exit 2 only with --strict)
  SHORT    a span of one minute                                                                                                -> under_2_min (a signal; exit 2 only with --strict)
  MIDNIGHT start at exactly 00:00:00                                                                                           -> midnight (a signal)
  SAME     one instant written in two zones                                                                                    -> NOT two_values
  CLEAN    started and finished before the commit that recorded it Done, a path Proposed -> InProgress -> Done                 -> in no class; exit 0 on a register that holds only this
Exit 0 when every expectation holds, 1 otherwise.
"""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
tool = sorted(glob.glob(os.path.join(HERE, "backlog_flow_point_git_trace_v*.py")), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(tool); sys.exit(0)
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/trace-probe#> .\n"
dtl = lambda v: f'"{v}"^^xsd:dateTime'
def item(n, state, starts=(), fins=()):
    t = f"x:{n} a backlog:Task ; backlog:hasState backlog:{state}"
    for s in starts: t += f" ; backlog:startedAt {dtl(s)}"
    for f in fins: t += f" ; backlog:finishedAt {dtl(f)}"
    return t + " .\n"
C1, C2 = "2026-10-13T09:00:00+00:00", "2026-10-14T10:00:00+00:00"
def commit(repo, msg, when):
    env = dict(os.environ, GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when, GIT_AUTHOR_NAME="p", GIT_AUTHOR_EMAIL="p@x", GIT_COMMITTER_NAME="p", GIT_COMMITTER_EMAIL="p@x")
    subprocess.run(["git", "-C", repo, "add", "-A"], check=True, env=env)
    subprocess.run(["git", "-C", repo, "commit", "-q", "-m", msg], check=True, env=env)
def build(d, first, second):
    subprocess.run(["git", "init", "-q", d], check=True)
    open(os.path.join(d, "reg.ttl"), "w").write(HEAD + first); commit(d, "one", C1)
    open(os.path.join(d, "reg.ttl"), "w").write(HEAD + second); commit(d, "two", C2)
def run(d, *extra):
    r = subprocess.run([sys.executable, tool, d, "reg.ttl", *extra], capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout
def count(out, cls):
    m = re.search(rf"^{cls}: (\d+)", out, re.M); return int(m.group(1)) if m else -1
bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
S0 = item("FUTURE", "InProgress", ["2026-10-13T09:30:00Z"]) + item("TWO", "InProgress", ["2026-10-13T09:30:00Z"]) + item("EQUAL", "InProgress", ["2026-10-13T09:30:00Z"]) \
     + item("SHORT", "InProgress", ["2026-10-13T09:30:00Z"]) + item("MIDNIGHT", "InProgress", ["2026-10-13T00:00:00Z"]) + item("SAME", "InProgress", ["2026-10-13T09:30:00Z"]) + item("CLEAN", "Proposed")
S1 = item("FUTURE", "Done", ["2026-10-13T09:30:00Z"], ["2026-12-01T18:00:00"]) + item("TWO", "Done", ["2026-10-13T09:30:00Z"], ["2026-10-13T11:00:00Z", "2026-10-13T12:00:00Z"]) \
     + item("EQUAL", "Done", ["2026-10-13T09:30:00Z"], ["2026-10-13T09:30:00Z"]) + item("SHORT", "Done", ["2026-10-13T09:30:00Z"], ["2026-10-13T09:31:00Z"]) \
     + item("MIDNIGHT", "Done", ["2026-10-13T00:00:00Z"], ["2026-10-13T08:00:00Z"]) + item("SAME", "Done", ["2026-10-13T09:30:00Z"], ["2026-10-13T11:00:00Z", "2026-10-13T14:00:00+03:00"]) \
     + item("CLEAN", "Done", ["2026-10-13T09:30:00Z"], ["2026-10-13T11:00:00Z"])
with tempfile.TemporaryDirectory() as d:
    build(d, S0, S1)
    rc, out = run(d)
    sets = {k: re.search(rf"^{k}: \d+ (\[.*\])", out, re.M).group(1) if re.search(rf"^{k}: \d+ (\[.*\])", out, re.M) else "" for k in ("future_finish", "two_values", "finish_not_after_start", "under_2_min", "midnight")}
    expect("FUTURE is reported as future_finish", "'FUTURE'" in sets["future_finish"] and count(out, "future_finish") == 1)
    expect("TWO is reported as two_values, SAME is not", "'TWO'" in sets["two_values"] and "'SAME'" not in sets["two_values"] and count(out, "two_values") == 1)
    expect("EQUAL is reported as finish_not_after_start", "'EQUAL'" in sets["finish_not_after_start"])
    expect("SHORT is reported as under_2_min", "'SHORT'" in sets["under_2_min"])
    expect("MIDNIGHT is reported as midnight", "'MIDNIGHT'" in sets["midnight"])
    expect("CLEAN is in no class", all("'CLEAN'" not in v for v in sets.values()))
    expect("exit 2 on a future finish and two values", rc == 2)
    expect("the state paths seen in the commits are listed", "state paths seen in commits" in out)
with tempfile.TemporaryDirectory() as d:
    build(d, item("CLEAN", "Proposed") + item("SIGNALS", "InProgress", ["2026-10-13T09:30:00Z"]),
             item("CLEAN", "Done", ["2026-10-13T09:30:00Z"], ["2026-10-13T11:00:00Z"]) + item("SIGNALS", "Done", ["2026-10-13T09:30:00Z"], ["2026-10-13T09:30:00Z"]))
    rc, out = run(d); expect("exit 0 when only signals are present (default mode)", rc == 0)
    rc, out = run(d, "--strict"); expect("exit 2 with --strict when a finish is not after its start", rc == 2)
with tempfile.TemporaryDirectory() as d:
    build(d, item("CLEAN", "Proposed"), item("CLEAN", "Done", ["2026-10-13T09:30:00Z"], ["2026-10-13T11:00:00Z"]))
    rc, out = run(d, "--strict"); expect("exit 0, strict, on a clean register", rc == 0)
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
