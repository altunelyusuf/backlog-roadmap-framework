#!/usr/bin/env python3
"""backlog_agent_monitor_probe v1.1.0 -- re-runnable proof of backlog_agent_monitor (G118). Plants a register with one of each finding and one clean item and checks the report."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
if sys.argv[1:] == ["--deps"]:
    print(os.path.join(HERE, "backlog_agent_monitor_v1_1_0.py")); print(os.path.abspath(__file__)); sys.exit(0)
tool = os.path.join(HERE, "backlog_agent_monitor_v1_1_0.py")
bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
D = '^^<http://www.w3.org/2001/XMLSchema#dateTime>'
TTL = f"""@prefix backlog: <http://example.org/backlog#> .
@prefix x: <http://example.org/mon-probe#> .
x:L a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_AgentAccountability ; backlog:humanApprovalLevel 3 .
x:H a backlog:Executor_IndividualHuman .
x:DefA a backlog:Executor_SingleAgent . x:DefB a backlog:Executor_SingleAgent .
x:RA a backlog:ExecutorInstance , backlog:Executor_SingleAgent ; backlog:instanceOf x:DefA ; backlog:instantiatedFromVersion "2.1.0" ; backlog:instantiatedAt "2026-10-15T06:00:00Z"{D} .
x:RB a backlog:ExecutorInstance , backlog:Executor_SingleAgent ; backlog:instanceOf x:DefB ; backlog:instantiatedFromVersion "1.0.0" ; backlog:instantiatedAt "2026-10-15T06:00:00Z"{D} ; backlog:retiredAt "2026-10-15T08:00:00Z"{D} .
x:RT a backlog:ExecutorInstance , backlog:Executor_AgentTeam ; backlog:instanceOf x:DefT ; backlog:instantiatedFromVersion "1.0.0" ; backlog:instantiatedAt "2026-10-15T06:00:00Z"{D} .
x:DefT a backlog:Executor_AgentTeam .
x:Stalled a backlog:Task ; backlog:hasState backlog:InProgress ; backlog:belongsToLineage x:L ; backlog:responsible x:RA .
x:E1 a backlog:TransitionEvent ; backlog:transitionedItem x:Stalled ; backlog:transitionedAt "2026-10-13T06:00:00Z"{D} ; backlog:transitionedByExecutor x:RA .
x:Fresh a backlog:Task ; backlog:hasState backlog:InProgress ; backlog:belongsToLineage x:L ; backlog:responsible x:RA .
x:E2 a backlog:TransitionEvent ; backlog:transitionedItem x:Fresh ; backlog:transitionedAt "2026-10-15T08:30:00Z"{D} ; backlog:transitionedByExecutor x:RA .
x:Anon a backlog:Task ; backlog:hasState backlog:InProgress ; backlog:belongsToLineage x:L ; backlog:startedAt "2026-10-15T08:00:00Z"{D} .
x:E3 a backlog:TransitionEvent ; backlog:transitionedItem x:Anon ; backlog:transitionedAt "2026-10-15T08:00:00Z"{D} .
x:E4 a backlog:TransitionEvent ; backlog:transitionedItem x:Anon ; backlog:transitionedAt "2026-10-15T08:10:00Z"{D} ; backlog:transitionedByExecutor x:DefA .
x:DoneBare a backlog:Task ; backlog:hasState backlog:Done ; backlog:belongsToLineage x:L ; backlog:responsible x:RA ; backlog:integrityLevel 1 .
x:DoneHigh a backlog:Task ; backlog:hasState backlog:Done ; backlog:belongsToLineage x:L ; backlog:responsible x:RA ; backlog:overseenBy x:RB ; backlog:verifiedBy x:RB ; backlog:approvedBy x:RB ; backlog:integrityLevel 4 .
x:DoneClean a backlog:Task ; backlog:hasState backlog:Done ; backlog:belongsToLineage x:L ; backlog:responsible x:RA ; backlog:overseenBy x:RB ; backlog:verifiedBy x:RB ; backlog:approvedBy x:H ; backlog:integrityLevel 4 .
x:Audit a backlog:RecurringActivity ; backlog:recurrenceInterval "P7D"^^<http://www.w3.org/2001/XMLSchema#duration> .
x:AuditPass1 a backlog:Task ; backlog:occurrenceOf x:Audit ; backlog:hasState backlog:Done ; backlog:startedAt "2026-10-01T08:00:00Z"{D} .
x:Fresh2 a backlog:RecurringActivity ; backlog:recurrenceInterval "P1M"^^<http://www.w3.org/2001/XMLSchema#duration> .
x:Fresh2Pass a backlog:Task ; backlog:occurrenceOf x:Fresh2 ; backlog:hasState backlog:Done ; backlog:startedAt "2026-10-10T08:00:00Z"{D} .
x:Ended a backlog:RecurringActivity ; backlog:recurrenceInterval "P1D"^^<http://www.w3.org/2001/XMLSchema#duration> ; backlog:recurrenceEndedAt "2026-09-01T00:00:00Z"{D} .
x:Never a backlog:RecurringActivity ; backlog:recurrenceInterval "P7D"^^<http://www.w3.org/2001/XMLSchema#duration> .
x:Teamed a backlog:Task ; backlog:hasState backlog:Ready ; backlog:belongsToLineage x:L ; backlog:responsible x:RT .
"""
with tempfile.TemporaryDirectory() as d:
    f = os.path.join(d, "r.ttl"); open(f, "w").write(TTL)
    r = subprocess.run([sys.executable, "-I", tool, f, "--now", "2026-10-15T09:00:00Z"], capture_output=True, text=True)
    out = r.stdout
    expect("the report ends with an escalation list and exits 1", "== Escalation:" in out and r.returncode == 1)
    expect("runs: version, retired state and move counts are shown", "v2.1.0" in out and "retired" in out and "moves 2" in out)
    expect("moves: one with no maker, one made by a definition", "with no recorded maker: 1    made by a definition, not a run: 1" in out)
    expect("stalled: the item idle for two days is named, the fresh one is not", "Stalled" in out.split("-- 3.")[1].split("-- 4.")[0] and "Fresh" not in out.split("-- 3.")[1].split("-- 4.")[0])
    expect("accountability: Done without overseer, verifier, approver is named", "DoneBare" in out and "lacks overseenBy, verifiedBy, approvedBy" in out)
    expect("accountability: Done at the human level approved by an agent needs a person", "DoneHigh" in out and "needs a person to approve" in out)
    expect("accountability: the item approved by a person is not asked about", "DoneClean" not in out)
    expect("teams: the team run named for work has no assembly", "RT" in out.split("-- 5.")[1] and "no recorded assembly" in out)
    rec = out.split("-- 6.")[1]
    expect("recurring: an activity past its interval and one with no occurrence are named", "Audit" in rec and "Never" in rec and "overdue" in out)
    expect("recurring: an activity inside its interval and an ended one are not named", "Fresh2" not in rec.split("== Escalation")[0] and "Ended" not in rec.split("== Escalation")[0])
    r2 = subprocess.run([sys.executable, "-I", tool, f, "--now", "2026-10-15T09:00:00Z", "--lineage", "NoSuch"], capture_output=True, text=True)
    expect("an unknown lineage is refused", r2.returncode == 2)
print("VERDICT   :", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
