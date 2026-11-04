#!/usr/bin/env python3
"""backlog_finding_kind_probe v1.0.0 -- Lineage 29, box 6 (G199): every finding recorded before Lineage 29 closed names the kind of obstacle that is its root cause,
the three whose recorded kind was wrong are read again through readAsKind (the recorded kind stays: a committed record is never edited), and the count that is
left is shown to move when a kind or a reading is taken away (mutants). It reads the newest register; nothing is written to it.

  python3 -I backlog_finding_kind_probe_v1_0_0.py          exit 0 when every case holds"""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", p)[0]]
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); sys.exit(0)
REGF = sorted(glob.glob(PKG + "/01-ontologies/backlog_abox_v*.ttl"), key=sv)[-1]
from rdflib import Graph, RDF, URIRef
B = "http://example.org/backlog#"; FW = "http://example.org/backlog-framework-register#"
U = lambda n: URIRef(B + n); local = lambda x: str(x).rsplit("#", 1)[-1]
KINDS = {"Imp_RuleRefusal", "Imp_EvidenceGap", "Imp_ToolFault", "Imp_WrongOrder", "Imp_AccessLimit", "Imp_DecisionWaiting", "Imp_ServiceFailure"}
AFTER = ("Find_IK_", "Find_CS_", "Find_GS_")                      # findings of Lineage 29 itself and of the two lineages after its closure
READ = {"Find_AA_StageScriptKeptOldStatus": ("Imp_RuleRefusal", "Imp_ToolFault"), "Find_AP2_UndeclaredPredicate": ("Imp_RuleRefusal", "Imp_ToolFault"),
        "Find_AA_EntityStagesAgain": ("Imp_RuleRefusal", "Imp_ToolFault")}   # recorded, read as
fails = 0
def expect(label, ok):
    global fails
    print(("PASS  " if ok else "FAIL  ") + label); fails += (not ok)
def counted(g):
    """-> (findings of the earlier set, those with no kind, those whose kind is not one of the seven, the three that are not read as they should be)"""
    fs = [f for f in g.subjects(RDF.type, U("RetrospectiveFinding")) if not local(f).startswith(AFTER)]
    def kind(f):
        r = g.value(f, U("readAsKind")); return r if r is not None else g.value(f, U("hasImpedimentKind"))
    none = [local(f) for f in fs if kind(f) is None]
    odd = [local(f) for f in fs if kind(f) is not None and local(kind(f)) not in KINDS]
    wrong = []
    for k, (was, now) in READ.items():
        f = URIRef(FW + k)
        if not (g.value(f, U("hasImpedimentKind")) is not None and local(g.value(f, U("hasImpedimentKind"))) == was and g.value(f, U("readAsKind")) is not None and local(g.value(f, U("readAsKind"))) == now): wrong.append(k)
    return fs, none, odd, wrong
g = Graph(); g.parse(REGF, format="turtle")
fs, none, odd, wrong = counted(g)
expect("%d earlier findings are read" % len(fs), len(fs) == 105)
expect("every earlier finding carries a kind, recorded or read (%d without)" % len(none), not none)
expect("every kind is one of the seven" + (": " + ",".join(odd) if odd else ""), not odd)
expect("the three whose recorded kind was wrong keep it and are read as the right one" + (": " + ",".join(wrong) if wrong else ""), not wrong)
expect("no finding carries two recorded kinds or two readings", all(len(list(g.objects(f, U("hasImpedimentKind")))) <= 1 and len(list(g.objects(f, U("readAsKind")))) <= 1 for f in fs))
# mutants: the count moves when the work is undone
m = Graph(); m += g; f0 = sorted(f for f in fs if g.value(f, U("hasImpedimentKind")) is not None and local(f) not in READ)[0]
m.remove((f0, U("hasImpedimentKind"), None)); expect("mutant: a kind taken from a finding is counted", len(counted(m)[1]) == 1)
m = Graph(); m += g; m.remove((URIRef(FW + "Find_AA_EntityStagesAgain"), U("readAsKind"), None)); expect("mutant: a reading taken away is counted", counted(m)[3] == ["Find_AA_EntityStagesAgain"])
m = Graph(); m += g; m.set((URIRef(FW + "Find_AA_EntityStagesAgain"), U("hasImpedimentKind"), U("Imp_ToolFault"))); expect("mutant: a recorded kind edited in place is counted", counted(m)[3] == ["Find_AA_EntityStagesAgain"])
m = Graph(); m += g; m.set((f0, U("hasImpedimentKind"), U("Imp_Mood"))); expect("mutant: a kind that is not one of the seven is counted", counted(m)[2] == [local(f0)])
print("VERDICT   :", "PASS" if not fails else "FAIL"); sys.exit(1 if fails else 0)
