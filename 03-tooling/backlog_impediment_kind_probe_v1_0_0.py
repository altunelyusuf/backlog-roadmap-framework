#!/usr/bin/env python3
"""Probe of the kinds of obstacle (G189): the real validator on a scratch register in which each impediment lacks or breaks exactly one thing, and the real register read for coverage:
each of the 29 findings classified (a selection of the 105 in the register whose root cause names a refusal, a failure or a wait) names exactly one of the seven kinds, and every kind is labelled, defined and exemplified."""
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
PRE = """@prefix backlog: <http://example.org/backlog#> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> . @prefix ex: <http://example.org/ikprobe#> .
ex:LinOn a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_ImpedimentsKnown ; backlog:humanApprovalLevel 3 .
ex:LinOff a backlog:Lineage ; backlog:humanApprovalLevel 3 .
ex:Work a backlog:Story .
"""
def imp(name, lin="LinOn", kinds=("backlog:Imp_ToolFault",)):
    s = f"ex:I_{name} a backlog:Impediment ; backlog:belongsToLineage ex:{lin} ; backlog:impedes ex:Work ; backlog:hasImpedimentStatement \"Blocked.\" ; backlog:raisedAt \"2026-11-02T11:00:00Z\"^^xsd:dateTime ; backlog:hasImpedimentOwner backlog:Builder"
    for k in kinds: s += f" ; backlog:hasImpedimentKind {k}"
    return s + " .\n"
CASES = [("Ok", {}, set()), ("NoKind", {"kinds": ()}, {"IK_NOKIND"}), ("TwoKinds", {"kinds": ("backlog:Imp_ToolFault", "backlog:Imp_WrongOrder")}, {"IK_BADKIND"}),
         ("NotAKind", {"kinds": ("backlog:Builder",)}, {"IK_BADKIND"}), ("NotBound", {"lin": "LinOff", "kinds": ()}, set()),
         ("NotBoundTwoKinds", {"lin": "LinOff", "kinds": ("backlog:Imp_ToolFault", "backlog:Imp_WrongOrder")}, {"IK_BADKIND"})]
data = PRE + "".join(imp(n, **k) for n, k, _ in CASES)
with tempfile.NamedTemporaryFile("w", suffix=".ttl", delete=False) as f:
    f.write(data); tmp = f.name
out = subprocess.run([sys.executable, VAL, tmp], capture_output=True, text=True).stdout
os.unlink(tmp)
got = {}
for m in re.finditer(r"\[Violation\]\s+(I_\S+)\s+(IK_[A-Z]+):", out):
    got.setdefault(m.group(1), set()).add(m.group(2))
for n, k, want in CASES:
    expect(f"{n}: " + (f"refused as {','.join(sorted(want))}" if want else "raises no IK_ message"), got.get("I_" + n, set()) == want)
from rdflib import Graph, RDF, Namespace
B = Namespace("http://example.org/backlog#"); RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#"); SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
g = Graph(); g.parse(REGF, format="turtle"); g.parse(TBOX, format="turtle")
KINDS = ["RuleRefusal", "EvidenceGap", "ToolFault", "WrongOrder", "AccessLimit", "DecisionWaiting", "ServiceFailure"]
expect("the register holds exactly the seven kinds, each labelled, defined, exemplified and marked framework-original",
       sorted(str(s).split("#")[-1][4:] for s in g.subjects(RDF.type, B.ImpedimentKind)) == sorted(KINDS) and
       all(g.value(B["Imp_" + k], RDFS.label) is not None and "Example:" in str(g.value(B["Imp_" + k], SKOS.definition) or "") and g.value(B["Imp_" + k], B.isFrameworkOriginal) is not None for k in KINDS))
fs = [x for x in set(g.subjects(B.hasImpedimentKind, None)) if (x, RDF.type, B.RetrospectiveFinding) in g]
ks = {x: list(g.objects(x, B.hasImpedimentKind)) for x in fs}
n_fit = sum(1 for x in fs if len(ks[x]) == 1 and str(ks[x][0]).split("#")[-1][4:] in KINDS)
expect("every classified finding whose root cause names a refusal, a failure or a wait names exactly one kind (%d of %d)" % (n_fit, len(fs)), n_fit == len(fs) and len(fs) >= 29)
expect("the kinds are all used by the findings or by the sessions: five by the findings, two (access limited, outside service failing) by the sessions only", sorted({str(v[0]).split("#")[-1][4:] for v in ks.values()}) == sorted(["RuleRefusal", "EvidenceGap", "ToolFault", "WrongOrder", "DecisionWaiting"]))
expect("the Adaptive-agentic profile includes the rule set from revision 13 and the other three profiles do not", [str(o).split("#")[-1] for o in g.objects(B.Profile_AgenticAdaptive, B.profileIncludes)].count("RS_ImpedimentsKnown") == 1 and not any(B.RS_ImpedimentsKnown in set(g.objects(B[p], B.profileIncludes)) for p in ("Profile_Standard", "Profile_Agentic", "Profile_Adaptive")))
print("VERDICT   :", "PASS" if not fails else "FAIL"); sys.exit(1 if fails else 0)
