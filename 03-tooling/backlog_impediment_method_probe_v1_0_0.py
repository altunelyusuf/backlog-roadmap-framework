#!/usr/bin/env python3
"""Probe of the ways to clear an obstacle (G190): the real validator on a scratch register in which each impediment or kind lacks or breaks exactly one thing,
and the real register read: every kind lists at least one way, every way is labelled, defined and used by a kind, and none is worded as a way round a rule."""
import glob, re, subprocess, sys, tempfile, os
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", p)[0]]
VAL = sorted(glob.glob(PKG + "/03-tooling/backlog_validate_v*.py"), key=sv)[-1]
REGF = sorted(glob.glob(PKG + "/01-ontologies/backlog_abox_v*.ttl"), key=sv)[-1]
TBOX = sorted(glob.glob(PKG + "/01-ontologies/backlog_tbox_v*.ttl"), key=sv)[-1]
fails = 0
def expect(label, ok):
    global fails
    print(("PASS  " if ok else "FAIL  ") + label); fails += (not ok)
PRE = """@prefix backlog: <http://example.org/backlog#> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> . @prefix ex: <http://example.org/icprobe#> .
ex:LinOn a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_ImpedimentsKnown ; backlog:humanApprovalLevel 3 .
ex:LinOff a backlog:Lineage ; backlog:humanApprovalLevel 3 .
ex:Work a backlog:Story .
ex:KindBare a backlog:ImpedimentKind .
"""
def imp(name, lin="LinOn", resolved=True, methods=("backlog:Mth_ReproduceAndRepairTool",)):
    s = f"ex:I_{name} a backlog:Impediment ; backlog:belongsToLineage ex:{lin} ; backlog:impedes ex:Work ; backlog:hasImpedimentStatement \"Blocked.\" ; backlog:raisedAt \"2026-11-02T11:00:00Z\"^^xsd:dateTime ; backlog:hasImpedimentOwner backlog:Builder ; backlog:hasImpedimentKind backlog:Imp_ToolFault"
    if resolved: s += " ; backlog:resolvedAt \"2026-11-02T12:00:00Z\"^^xsd:dateTime"
    for m in methods: s += f" ; backlog:clearedBy {m}"
    return s + " .\n"
CASES = [("Ok", {}, set()), ("NoMethod", {"methods": ()}, {"IC_NOMETHOD"}), ("WrongMethod", {"methods": ("backlog:Mth_BoundedRetry",)}, {"IC_WRONGMETHOD"}),
         ("TwoMethods", {"methods": ("backlog:Mth_ReproduceAndRepairTool", "backlog:Mth_StateTheLimit")}, {"IC_BADMETHOD", "IC_WRONGMETHOD"}),
         ("NotAMethod", {"methods": ("backlog:Builder",)}, {"IC_BADMETHOD", "IC_WRONGMETHOD"}),
         ("StillOpen", {"resolved": False, "methods": ()}, set()), ("MethodNoResolvedTime", {"resolved": False}, {"IC_NOTCLEARED"}), ("NotBound", {"lin": "LinOff", "methods": ()}, set())]
data = PRE + "".join(imp(n, **k) for n, k, _ in CASES)
with tempfile.NamedTemporaryFile("w", suffix=".ttl", delete=False) as f:
    f.write(data); tmp = f.name
out = subprocess.run([sys.executable, VAL, tmp], capture_output=True, text=True).stdout
os.unlink(tmp)
got = {}
for m in re.finditer(r"\[Violation\]\s+(\S+)\s+(IC_[A-Z]+):", out):
    got.setdefault(m.group(1), set()).add(m.group(2))
for n, k, want in CASES:
    expect(f"{n}: " + (f"refused as {','.join(sorted(want))}" if want else "raises no IC_ message"), got.get("I_" + n, set()) == want)
expect("a kind that lists no way is refused as IC_KINDNOMETHOD", got.get("KindBare", set()) == {"IC_KINDNOMETHOD"})
from rdflib import Graph, RDF, Namespace
B = Namespace("http://example.org/backlog#"); RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#"); SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
g = Graph(); g.parse(REGF, format="turtle"); g.parse(TBOX, format="turtle")
kinds = list(g.subjects(RDF.type, B.ImpedimentKind)); methods = list(g.subjects(RDF.type, B.ClearingMethod))
expect("each of the %d kinds lists at least one way" % len(kinds), len(kinds) == 7 and all(list(g.objects(k, B.clearableBy)) for k in kinds))
expect("each of the %d ways is labelled, defined, marked framework-original and listed by at least one kind" % len(methods), len(methods) == 14 and all(g.value(m, RDFS.label) and g.value(m, SKOS.definition) and g.value(m, B.isFrameworkOriginal) is not None and (None, B.clearableBy, m) in g for m in methods))
bad = [str(m).split("#")[-1] for m in methods if re.search(r"\b(skip|waive|bypass|defer|ignore|override)\w*", str(g.value(m, SKOS.definition)), re.I) and not re.search(r"\b(never|not|no)\b", str(g.value(m, SKOS.definition)), re.I)]
expect("no way is worded as a way round a rule (a definition that names skipping, waiving, bypassing or deferring also says never or not)" + (": " + ",".join(bad) if bad else ""), not bad)
expect("no way describes itself as not clearing the obstacle", not any(re.search(r"does not clear|not clear the", str(g.value(m, SKOS.definition))) for m in methods))
expect("every definition says when the obstacle is gone ('Gone when')", all("Gone when" in str(g.value(m, SKOS.definition)) for m in methods))
r190 = [s for s in g.subjects(B.hasRulingIdentifier, None) if str(g.value(s, B.hasRulingIdentifier)) == "G190"]
expect("the ruling names both shapes", len(r190) == 1 and {str(o).split("#")[-1] for o in g.objects(r190[0], B.enforcedByShape)} == {"ClearedImpedimentNamesMethodShape", "KindHasMethodShape"})
print("VERDICT   :", "PASS" if not fails else "FAIL"); sys.exit(1 if fails else 0)
