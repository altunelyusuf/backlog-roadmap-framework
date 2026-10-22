#!/usr/bin/env python3
"""backlog_kind_category_probe v1.2.0 -- the kinds of classes and categories of links recorded in the T-Box fit the OE kind rules (G139).

What it shows:
  1 the ledger and the T-Box agree: every kb:hasClassKind / kb:hasRelationshipCategory triple has a ledger row with evidence, and every row is in the T-Box,
  2 every recorded class and property exists in the T-Box, and every kind and category exists in the OE governance A-Box (skipped where the OE tool is not beside the package),
  3 the OE kind-rule check finds no violation in the recorded kinds and categories (skipped likewise),
  5 the held list equals the classes still without a kind, and no object property is without a category (a new term cannot hide),
  4 planted: a category that the kinds do not fit (supersedesRule recorded as Normative, whose ends must be Agents) is found as a violation.
Exit 0 when every expectation holds, 1 otherwise."""
import glob, os, re, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
TB, LED, HELD = latest("01-ontologies/backlog_tbox_v*.ttl"), latest("03-tooling/kind_category_recording_v*.tsv"), latest("03-tooling/kind_category_held_v*.tsv")
if sys.argv[1:] == ["--deps"]:
    print("\n".join([TB, LED, HELD, os.path.abspath(__file__)])); sys.exit(0)
from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef
B = Namespace("http://example.org/backlog#"); KB = Namespace("http://example.org/knowledge-base#")
bad = []
def expect(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (" (%s)" % detail if detail else ""))
    if not ok: bad.append(name)
g = Graph(); g.parse(TB)
rows = [l.rstrip("\n").split("\t") for l in open(LED, encoding="utf-8")][1:]
led = {(r[0], r[2], r[3]) for r in rows if r}
tb = {("class", str(s), str(o).split("#")[1]) for s, o in g.subject_objects(KB.hasClassKind)} | {("property", str(s), str(o).split("#")[1]) for s, o in g.subject_objects(KB.hasRelationshipCategory)}
expect("1 the ledger and the T-Box agree", led == tb, "%d row(s); only in ledger %s; only in T-Box %s" % (len(led), sorted(led - tb)[:2], sorted(tb - led)[:2]))
expect("1 every ledger row has evidence", all(len(r) >= 5 and r[4].strip() for r in rows if r))
exist = all(((B[u.split("#")[1]], RDF.type, OWL.Class) in g) if k == "class" else ((B[u.split("#")[1]], RDF.type, OWL.ObjectProperty) in g) for k, u, _ in led)
expect("2 every recorded class and property is declared in the T-Box", exist)
SK = Namespace("http://www.w3.org/2004/02/skos/core#")
named = lambda x: isinstance(x, URIRef) and ((x, SK.definition, None) in g or (x, RDFS.label, None) in g)
def cat(p, seen=()):
    return (p, KB.hasRelationshipCategory, None) in g or any(cat(q, seen + (p,)) for q in g.objects(p, RDFS.subPropertyOf) if q not in seen)
nokind = {str(c) for c in g.subjects(RDF.type, OWL.Class) if named(c) and (c, KB.hasClassKind, None) not in g}
nocat = [str(p) for p in g.subjects(RDF.type, OWL.ObjectProperty) if named(p) and not cat(p)]
held = {l.split("\t")[1] for l in open(HELD, encoding="utf-8").read().splitlines()[1:] if l}
expect("5 the held list equals the classes without a kind", held == nokind, "%d held; only held %s; only untyped %s" % (len(held), sorted(held - nokind)[:2], sorted(nokind - held)[:2]))
expect("5 every object property has a category", not nocat, "%d without: %s" % (len(nocat), nocat[:2]))
root = os.path.dirname(PKG); tools = sorted([x for x in glob.glob(os.path.join(root, "repo-tooling", "oe_kind_rule_check_v*.py")) if "_test_" not in x], key=sv); tool = tools[-1] if tools else ""; gov = sorted(glob.glob(os.path.join(root, "oe-method", "09-governance", "oegov_abox_v*.ttl")), key=sv)
if not (tool and gov):
    print("SKIP  2-4 the OE kind-rule check is not beside this package (a public copy)")
else:
    og = Graph(); og.parse(gov[-1])
    expect("2 every kind and category is in the OE governance A-Box", all((KB[x], None, None) in og for _, _, x in led))
    def run(ttl_text):
        td = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(td, "oe-method")); os.symlink(os.path.dirname(gov[-1]), os.path.join(td, "oe-method", "09-governance"))
            d = os.path.join(td, "pk", "01-ontologies"); os.makedirs(d); open(os.path.join(d, "pk_tbox.ttl"), "w", encoding="utf-8").write(ttl_text)
            r = subprocess.run([sys.executable, "-B", tool, td], capture_output=True, text=True, timeout=300); return r.stdout + r.stderr
        finally: shutil.rmtree(td, ignore_errors=True)
    src = open(TB, encoding="utf-8").read()
    o = run(src); m = re.search(r"(\d+) violation\(s\) of (\d+) end\(s\) measured", o)
    expect("3 the OE kind-rule check finds no violation in the recorded kinds and categories", bool(m) and m.group(1) == "0" and int(m.group(2)) > 0, m.group(0) if m else o[:120])
    p = run(src.replace("backlog:supersedesRule kb:hasRelationshipCategory kb:RelationshipCategory_Versioning", "backlog:supersedesRule kb:hasRelationshipCategory kb:RelationshipCategory_Normative")); m = re.search(r"(\d+) violation\(s\)", p)
    expect("4 planted: a category the kinds do not fit is a violation", bool(m) and int(m.group(1)) >= 1, m.group(0) if m else p[:120])
print("OK" if not bad else "FAILED: %s" % bad); sys.exit(1 if bad else 0)
