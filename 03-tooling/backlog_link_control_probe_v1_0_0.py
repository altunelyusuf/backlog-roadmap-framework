#!/usr/bin/env python3
"""backlog_link_control_probe v1.0.0 -- the link control decides every candidate, in all three families (G135).

What it shows, on the shipped files and on small planted file sets:
  1 the shipped files: every missing-link candidate (any trust, any family) is a link or a coded rejection, and no ledger row is stale (skipped where the OE tool is not beside the package),
  2 planted: an undecided candidate fails, in each of the three families (a syntactic text naming a thing, a semantic property used with no domain, a temporal 'supersedes' text),
  3 planted: the same candidate rejected with a coded reason passes, and a stale row (the link was made) fails,
  4 a ledger row with no reason, or a reason with no coded category, is refused,
  5 the two links the owner asked for are made (T-Box v1.137.0): every MethodologyRule is linked to a Methodology and every ReleaseGate to a release (orh:ReleaseEvent), in the class and in the data.
Exit 0 when every expectation holds, 1 otherwise."""
import glob, importlib.util, os, re, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
TB, AB = latest("01-ontologies/backlog_tbox_v*.ttl"), latest("01-ontologies/backlog_abox_v*.ttl")
if sys.argv[1:] == ["--deps"]:
    print("\n".join([TB, AB, latest("03-tooling/backlog_link_control_v*.py"), latest("03-tooling/link_decisions_v*.tsv"), os.path.abspath(__file__)])); sys.exit(0)
spec = importlib.util.spec_from_file_location("lc", latest("03-tooling/backlog_link_control_v*.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
from rdflib import Graph, Namespace, RDF, RDFS, OWL
B = Namespace("http://example.org/backlog#"); ORH = Namespace("http://example.org/oepack-release-history#")
bad = []
def expect(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (" (%s)" % detail if detail else ""))
    if not ok: bad.append(name)

root = os.path.dirname(PKG); oe = lc.find_oe(root)
if oe:
    und, stale, total, rej = lc.control(root, os.path.basename(PKG), None if not glob.glob(os.path.join(HERE, "link_decisions_v*.tsv")) else latest("03-tooling/link_decisions_v*.tsv"), oe)
    expect("1 the shipped files: every candidate is a link or a coded rejection, none stale", not und and not stale, "%d candidate(s), %d rejected; undecided %s; stale %s" % (total, rej, und[:2], stale[:2]))
else:
    print("SKIP  1 the OE link discovery is not beside this package (a public copy)")

HEAD = "@prefix ex: <http://example.org/p#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix skos: <http://www.w3.org/2004/02/skos/core#> .\n"
BASE = HEAD + '''<http://example.org/p> a owl:Ontology .
ex:ReviewBoard a owl:Class ; rdfs:label "Alpha" ; skos:definition "A review board. It is reviewed through ReleasePanel." .
ex:ReleasePanel a owl:Class ; rdfs:label "Beta" ; skos:definition "A beta." .
'''
SEM = '''ex:ReportItem a owl:Class ; rdfs:label "Gamma" ; skos:definition "A gamma." .
ex:relates a owl:ObjectProperty ; rdfs:label "relates" ; skos:definition "Relates a gamma." .
ex:g1 a ex:ReportItem . ex:g2 a ex:ReportItem , ex:ReportItem . ex:g1 ex:relates ex:g2 .
'''
TEM = '''ex:LegacyRecord a owl:Class ; rdfs:label "Old" ; skos:definition "Old." .
ex:CurrentRecord a owl:Class ; rdfs:label "New" ; skos:definition "New. It supersedes LegacyRecord." .
'''
def plant(body, ledger=None):
    td = tempfile.mkdtemp(); pk = os.path.join(td, "pk"); os.makedirs(os.path.join(pk, "01-ontologies"))
    open(os.path.join(pk, "01-ontologies", "pk_tbox_v1_0_0.ttl"), "w").write(HEAD + body.replace(HEAD, ""))
    lp = None
    if ledger is not None:
        lp = os.path.join(td, "ledger.tsv"); open(lp, "w").write("set\tfamily\tfrom\tto\treason\n" + ledger)
    return td, lp
def fam(und, name): return any(u.startswith(name) for u in und) and all(u.startswith(name) for u in und)
if oe:
    for label, body, family in (("syntactic", BASE, "syntactic"), ("semantic", SEM, "semantic"), ("temporal", TEM, "temporal")):
        td, _ = plant(body)
        try:
            und, stale, total, rej = lc.control(td, "pk", None, oe)
            expect("2 planted %s candidate is undecided and fails" % label, fam(und, family), "%d candidate(s): %s" % (total, [u[:50] for u in und][:3]))
        except lc.Refused as e:
            expect("2 planted %s candidate is undecided and fails" % label, False, str(e)[:80])
    td, _ = plant(BASE)
    und, _, _, _ = lc.control(td, "pk", None, oe)
    row = None
    cands = lc.candidates(td, "pk", oe)
    k = sorted(cands)[0]
    led = "%s\t%s\t%s\t%s\t[wrong-sense] the word means something else here\n" % k
    td2, lp = plant(BASE, led)
    und2, stale2, _, rej2 = lc.control(td2, "pk", lp, oe)
    expect("3a the same candidate rejected with a coded reason passes", not und2 and not stale2 and rej2 == 1)
    td3, lp3 = plant(BASE.replace("through ReleasePanel", "through a panel"), led)
    und3, stale3, _, _ = lc.control(td3, "pk", lp3, oe)
    expect("3b a row whose candidate is gone (text removed or link made) is stale and fails", len(stale3) == 1)
    for label, text in (("no reason", "%s\t%s\t%s\t%s\t \n" % k), ("no coded category", "%s\t%s\t%s\t%s\tbecause I say so\n" % k)):
        td4, lp4 = plant(BASE, text)
        try:
            lc.control(td4, "pk", lp4, oe); ok = False
        except lc.Refused:
            ok = True
        expect("4 a ledger row with %s is refused" % label, ok)
else:
    print("SKIP  2-4 planted checks need the OE link discovery")

t = Graph(); t.parse(TB, format="turtle"); a = Graph(); a.parse(AB, format="turtle")
def restricted(cls, prop, filler):
    for r in t.objects(cls, RDFS.subClassOf):
        if (r, OWL.onProperty, prop) in t and (r, OWL.someValuesFrom, filler) in t: return True
    return False
expect("5a MethodologyRule is linked to Methodology in the class (a restriction on ruleOfMethodology)", restricted(B.MethodologyRule, B.ruleOfMethodology, B.Methodology))
rules = list(a.subjects(RDF.type, B.MethodologyRule))
expect("5b every MethodologyRule individual names its methodology, and it is a Methodology", rules and all(any((m, RDF.type, B.Methodology) in a for m in a.objects(r, B.ruleOfMethodology)) for r in rules), "%d rule(s)" % len(rules))
expect("5c ReleaseGate is linked to a release in the class (guardsRelease some orh:ReleaseEvent)", restricted(B.ReleaseGate, B.guardsRelease, ORH.ReleaseEvent))
expect("5d guardsRelease is declared from ReleaseGate to orh:ReleaseEvent", (B.guardsRelease, RDFS.domain, B.ReleaseGate) in t and (B.guardsRelease, RDFS.range, ORH.ReleaseEvent) in t)
print("VERDICT: %s" % ("PASS -- every expectation holds" if not bad else "FAIL -- " + "; ".join(bad)))
sys.exit(1 if bad else 0)
