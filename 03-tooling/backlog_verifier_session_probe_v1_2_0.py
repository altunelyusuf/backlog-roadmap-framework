#!/usr/bin/env python3
"""Probe of RS_VerifierSession (G184): the real validator on one scratch register in which each verifier run lacks exactly one thing.
A control run with the full record must raise none of the VS_ messages; a lineage that does not adopt the rule set is not bound.
Also: AAL includes the rule set (21), the other profiles are as they were (9, 10, 16)."""
import glob, re, subprocess, sys, tempfile, os
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", p)[0]]
VAL = sorted(glob.glob(PKG + "/03-tooling/backlog_validate_v*.py"), key=sv)[-1]
ABOX = sorted(glob.glob(PKG + "/01-ontologies/backlog_abox_v*.ttl"), key=sv)[-1]
PRE = """@prefix backlog: <http://example.org/backlog#> . @prefix agsys: <http://example.org/agentic-systems#> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> . @prefix ex: <http://example.org/vsprobe#> .
ex:LinOn a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_VerifierSession ; backlog:humanApprovalLevel 3 .
ex:LinOff a backlog:Lineage ; backlog:humanApprovalLevel 3 .
ex:Def a backlog:Executor_SingleAgent . ex:DefBare a backlog:Executor_SingleAgent .
ex:Cfg a agsys:AgentConfiguration ; agsys:isConfigurationOf ex:Def ; agsys:recordedAt "2026-11-01T09:00:00Z"^^xsd:dateTime .
ex:Human a backlog:Executor_IndividualHuman . ex:HumanAndAgent a backlog:Executor_IndividualHuman , backlog:Executor_SingleAgent . ex:Builder a backlog:ExecutorInstance , backlog:Executor_SingleAgent .
"""
D64 = "a" * 64
def run(name, omit=None, lin="LinOn", level=2, late=False, bare=False, digest=D64, grantor="Builder", extra="", untyped=False, noinst=False):
    typ = "backlog:Executor_SingleAgent" if untyped else "backlog:ExecutorInstance"
    parts = [f"ex:{name} a {typ} ;" + ("" if noinst else f" backlog:instanceOf ex:{'DefBare' if bare else 'Def'} ; backlog:instantiatedAt \"2026-11-01T10:00:00Z\"^^xsd:dateTime ;")]
    if omit != "start": parts.append(" agsys:startedInWay ex:Req ;")
    if omit != "grant": parts.append(f" agsys:startedUnderGrant ex:G_{name} ;")
    if omit != "plan": parts.append(f" agsys:followsPlan ex:P_{name} ;")
    if omit != "session": parts.append(" agsys:executedBy ex:Sess ;")
    if omit != "unchanged": parts.append(" agsys:placeUnchanged true ;")
    s = " ".join(parts) + " .\n" + extra.replace("NAME", name)
    ga = "2026-11-01T11:00:00Z" if late else "2026-11-01T09:30:00Z"
    s += f"ex:G_{name} a agsys:AccessGrant ; agsys:grantedBy ex:{grantor} ; agsys:grantedPlace \"the working tree\" ; agsys:grantedAt \"{ga}\"^^xsd:dateTime .\n"
    s += f"ex:P_{name} a agsys:VerificationPlan ; agsys:hasPlanDigest \"{digest}\" .\n"
    s += f"ex:I_{name} a backlog:Story ; backlog:belongsToLineage ex:{lin} ; backlog:integrityLevel {level} ; backlog:verifiedBy ex:{name} .\n"
    return s
CASES = [  # name, kwargs, expected VS_ code or None
 ("Ok", {}, None), ("NoStart", {"omit": "start"}, "VS_INCOMPLETE"), ("NoGrant", {"omit": "grant"}, "VS_INCOMPLETE"),
 ("NoPlan", {"omit": "plan"}, "VS_INCOMPLETE"), ("BadDigest", {"digest": "abc"}, "VS_INCOMPLETE"),
 ("NoSession", {"omit": "session"}, "VS_INCOMPLETE"), ("NoUnchanged", {"omit": "unchanged"}, "VS_INCOMPLETE"),
 ("Late", {"late": True}, "VS_ORDER"), ("NoConfig", {"bare": True}, "VS_NO_CONFIG"),
 ("AgentGrantorHigh", {"level": 3}, "VS_GRANTOR"), ("PersonGrantorHigh", {"level": 3, "grantor": "Human"}, None),
 ("NoInstance", {"noinst": True, "late": True}, "VS_INCOMPLETE"), ("UntypedVerifier", {"untyped": True, "omit": "start"}, "VS_INCOMPLETE"),
 ("TwoGrants", {"extra": "ex:NAME agsys:startedUnderGrant ex:G_Other .\nex:G_Other a agsys:AccessGrant .\n"}, "VS_INCOMPLETE"),
 ("TwoPlans", {"extra": "ex:NAME agsys:followsPlan ex:P_Other .\nex:P_Other agsys:hasPlanDigest \"zz\" .\n"}, "VS_INCOMPLETE"),
 ("TwoUnchanged", {"extra": "ex:NAME agsys:placeUnchanged false .\n"}, "VS_INCOMPLETE"),
 ("DualGrantor", {"level": 3, "grantor": "HumanAndAgent"}, "VS_GRANTOR"),
 ("AgentGrantorLow", {"level": 2}, None), ("Unbound", {"omit": "grant", "bare": True, "lin": "LinOff"}, None)]
data = PRE + "".join(run(n, **k) for n, k, _ in CASES)
with tempfile.NamedTemporaryFile("w", suffix=".ttl", delete=False) as f:
    f.write(data); tmp = f.name
out = subprocess.run([sys.executable, VAL, tmp], capture_output=True, text=True).stdout
os.unlink(tmp)
got = {}
for m in re.finditer(r"\[Violation\]\s+(\S+)\s+(VS_[A-Z_]+):", out):
    got.setdefault(m.group(1), set()).add(m.group(2))
fails = 0
def expect(label, ok):
    global fails
    print(("PASS  " if ok else "FAIL  ") + label); fails += (not ok)
for n, k, want in CASES:
    have = got.get(n, set())
    expect(f"{n}: " + (f"refused as {want}" if want else "raises no VS_ message"), have == ({want} if want else set()))
inc = lambda p: len(re.findall(r"backlog:RS_\w+", (re.search(r"backlog:" + p + r" a owl:NamedIndividual[^.]*?\n(?:\s+[^\n]*\n)*?[^\n]*profileIncludes[^\n]*", open(ABOX).read()) or [""])[0]))
txt = open(ABOX).read()
def count(profile):
    return len({m for m in re.findall(r"backlog:" + profile + r" backlog:profileIncludes (backlog:RS_\w+)", txt)} | {x for blk in re.findall(r"^backlog:" + profile + r" a [^\n]*\n(?:    [^\n]*\n)+", txt, re.M) for x in re.findall(r"backlog:(RS_\w+)", blk.split("profileIncludes",1)[1] if "profileIncludes" in blk else "")} )
for p, n in (("Profile_Standard", 9), ("Profile_Agentic", 10), ("Profile_Adaptive", 16), ("Profile_AgenticAdaptive", 21)):
    expect(f"{p} includes {n} rule sets", count(p) == n)
print("VERDICT   :", "PASS" if not fails else "FAIL"); sys.exit(1 if fails else 0)
