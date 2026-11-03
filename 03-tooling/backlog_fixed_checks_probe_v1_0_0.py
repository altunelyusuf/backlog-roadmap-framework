#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe reads no record of the framework register; it builds its own temporary repositories)
"""backlog_fixed_checks_probe v1.0.0 -- proves the kept inputs of the flow-point trace (v1.3.0) and the order check (v1.16.0) change no verdict (Lineage 31, story Fixed).

Each case is a temporary git repository; every result is compared with the same tool run with no memo directory, which keeps nothing.
  F1  flow trace, a register renamed at each commit: the run that fills the memo equals the run without one, and keeps the walk
  F2  flow trace, a commit added: the run that appends to the kept walk equals a fresh run
  F3  flow trace, the history rewritten (the kept head is no longer an ancestor): the kept walk is not used; equals a fresh run
  O1  order check, an adoption after the Mission commit (the finding of the revival probe): the run that fills the memo and the run that reads it give the finding as the run without a memo does
  O2  order check, the control: no finding in any of the three runs
Exit 0 when every expectation holds, 1 otherwise."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(HERE, pat)), key=sv)[-1]
flow, order = latest("backlog_flow_point_git_trace_v*.py"), latest("backlog_lineage_order_check_v*.py")
if sys.argv[1:] == ["--deps"]:
    print(flow); print(order); print(os.path.abspath(__file__)); sys.exit(0)
bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
ENV = dict(os.environ, GIT_AUTHOR_NAME="p", GIT_AUTHOR_EMAIL="p@x", GIT_COMMITTER_NAME="p", GIT_COMMITTER_EMAIL="p@x")
def git(d, *a, when=None):
    env = dict(ENV)
    if when: env.update(GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
    return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, check=True, env=env).stdout
PRE = "@prefix backlog: <http://example.org/backlog#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n@prefix x: <http://example.org/fixed-probe#> .\n"
def item(n, state, s=None, f=None):
    t = f"x:{n} a backlog:Task ; backlog:hasState backlog:{state}"
    if s: t += f' ; backlog:startedAt "{s}"^^xsd:dateTime'
    if f: t += f' ; backlog:finishedAt "{f}"^^xsd:dateTime'
    return t + " .\n"
# ---- flow trace
def fl(d, reg, memo):
    env = dict(os.environ); env.pop("BACKLOG_VALIDATE_MEMO_DIR", None)
    if memo: env["BACKLOG_VALIDATE_MEMO_DIR"] = memo
    r = subprocess.run([sys.executable, flow, d, reg, os.path.join(d, reg)], capture_output=True, text=True, timeout=300, env=env)
    return r.returncode, r.stdout
with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as memo:
    git(d, "init", "-q"); os.makedirs(os.path.join(d, "o"))
    def put(ver, body, when, msg, prev=None):
        if prev: git(d, "mv", f"o/reg_v1_0_{prev}.ttl", f"o/reg_v1_0_{ver}.ttl")
        open(os.path.join(d, f"o/reg_v1_0_{ver}.ttl"), "w").write(PRE + body); git(d, "add", "-A"); git(d, "commit", "-q", "-m", msg, when=when)
    put(0, item("A", "InProgress", "2026-10-13T09:00:00Z"), "2026-10-13T10:00:00+00:00", "one")
    put(1, item("A", "Done", "2026-10-13T09:00:00Z", "2026-10-13T09:30:00Z"), "2026-10-14T10:00:00+00:00", "two", prev=0)
    reg = "o/reg_v1_0_1.ttl"
    r_fresh = fl(d, reg, None); r_cold = fl(d, reg, memo)
    expect("F1 flow trace: the run that fills the memo equals the run without one", r_cold == r_fresh and "VERDICT" in r_fresh[1] and any(n.startswith("aux_flowwalk_") for n in os.listdir(memo)))
    put(2, item("A", "Done", "2026-10-13T09:00:00Z", "2026-12-01T09:30:00Z") + item("B", "Proposed"), "2026-10-15T10:00:00+00:00", "three", prev=1)
    reg = "o/reg_v1_0_2.ttl"
    r_fresh = fl(d, reg, None); r_inc = fl(d, reg, memo)
    expect("F2 flow trace: the run that appends a commit to the kept walk equals a fresh run, and still sees the fault", r_inc == r_fresh and "future_finish: 1" in r_fresh[1])
    git(d, "reset", "-q", "--hard", "HEAD~1")
    put(2, item("A", "Done", "2026-10-13T09:00:00Z", "2026-10-13T09:45:00Z") + item("C", "Proposed"), "2026-10-16T10:00:00+00:00", "three again", prev=1)
    r_fresh = fl(d, reg, None); r_rew = fl(d, reg, memo)
    expect("F3 flow trace: after a rewritten history the kept walk is not used and the run equals a fresh run", r_rew == r_fresh and "future_finish: 0" in r_fresh[1])
# ---- order check
B = "http://example.org/backlog#"; NS = "http://example.org/fixed-probe#"
P = f"@prefix backlog: <{B}> .\n@prefix x: <{NS}> .\n"
LIN = ("x:L a backlog:Lineage ; backlog:lineageOrdinal 1 ; backlog:adoptionRecordedAtOpen true ; backlog:adoptsRuleSet backlog:RS_A .\n"
       "x:O_M a backlog:StageOutput ; backlog:outputOfStage backlog:Stage_Mission ; backlog:belongsToLineage x:L ; backlog:closedAtCommit \"c\" ; backlog:hasStateDigest \"d\" .\n")
LATE = "x:L backlog:adoptsRuleSet backlog:RS_B .\n"
def build_ord(d, steps):
    git(d, "init", "-q"); os.makedirs(os.path.join(d, "reg")); f = os.path.join(d, "reg", "register.ttl")
    for body, msg in steps:
        open(f, "w").write(P + body); git(d, "add", "-A"); git(d, "commit", "-q", "-m", msg)
    return f
def ordrun(f, memo):
    env = dict(os.environ); env.pop("BACKLOG_VALIDATE_MEMO_DIR", None)
    if memo: env["BACKLOG_VALIDATE_MEMO_DIR"] = memo
    out = subprocess.run([sys.executable, order, f], capture_output=True, text=True, timeout=300, env=env).stdout
    return sum(1 for ln in out.splitlines() if "claims adoptionRecordedAtOpen but adopts" in ln)
for name, steps, want in (("O1 order check: an adoption after the Mission commit is found without a memo, filling it and reading it back", [(LIN, "mission"), (LIN + LATE, "late adoption")], 1),
                          ("O2 order check: the control is silent in all three runs", [(LIN, "mission"), (LIN + "x:Z a backlog:Task .\n", "more")], 0)):
    with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as memo:
        f = build_ord(d, steps)
        a = ordrun(f, None); b = ordrun(f, memo); kept = [n for n in os.listdir(memo) if n.startswith("aux_order_")]; c = ordrun(f, memo)
        expect(f"{name}: expected {want}, got {a}, {b}, {c}; kept files after the filling run: {len(kept)}", a == b == c == want and (len(kept) > 0 or want == 0))
print("flow trace :", os.path.basename(flow)); print("order check:", os.path.basename(order)); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
