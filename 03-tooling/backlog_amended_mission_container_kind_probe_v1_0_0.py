#!/usr/bin/env python3
"""backlog_amended_mission_container_kind_probe v1.0.0 (box 60, G246): MissionClauseCitationShape reads the statement of a mission amendment as well as the mission's own, and rule R5 (ContainerDependencyRule) derives a container dependency only between two containers of one kind (two packages or two iterations), never to or from the whole backlog. Usage: probe [--shapes PATH].
Runs the shape and the rule themselves, copied from the newest shapes file, with pyshacl for the shape (advanced, no inference, over the newest T-box) and the rule's own CONSTRUCT query run per container for the rule; each case plants a register and says whether the shape fires or the dependency is derived.
Cases (citation): a quote of the mission's own statement, of an amended statement, of text only in the mission before widening (which the amendment keeps) conform; a quote found in neither fires; no mission with the quote fires.
Cases (R5): package to package and iteration to iteration derive; iteration to package, package to iteration, a backlog to a container and a container to the backlog derive nothing; a Done dependency derives nothing; the advisory fires for an undeclared pair of one kind and is silent once declared."""
import os, re, sys, glob
from rdflib import Graph, Namespace, BNode, URIRef
from rdflib.namespace import RDF
import pyshacl
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.join(HERE, "..")
SH = Namespace("http://www.w3.org/ns/shacl#"); BL = Namespace("http://example.org/backlog#"); EX = Namespace("http://example.org/probe#")
def newest(folder, stem):
    fs = glob.glob(os.path.join(PKG, folder, stem + "_v*.ttl"))
    return sorted(fs, key=lambda f: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", f)[0]])[-1]
SHAPES_FILE = sys.argv[sys.argv.index("--shapes") + 1] if "--shapes" in sys.argv else newest("02-shacl-safeguards", "backlog_shacl")
SHAPES = Graph(); SHAPES.parse(SHAPES_FILE, format="turtle")
TBOX = newest("01-ontologies", "backlog_tbox")
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(TBOX); print(newest("02-shacl-safeguards", "backlog_shacl")); sys.exit(0)
def reduced(name):
    red = Graph(); seen = set()
    def walk(n):
        if n in seen: return
        seen.add(n)
        for p, o in SHAPES.predicate_objects(n):
            red.add((n, p, o))
            if isinstance(o, BNode) or p in (SH.prefixes, SH.declare): walk(o)
    walk(BL[name]); return red
CIT = reduced("MissionClauseCitationShape"); UND = reduced("UndeclaredContainerDependencyAdvisoryShape")
RULE = next(str(o) for o in SHAPES.objects(None, SH.construct) if "derivedContainerDependency" in str(o))
PRE = "@prefix backlog: <http://example.org/backlog#> . @prefix ex: <http://example.org/probe#> .\n"
TB = Graph(); TB.parse(TBOX, format="turtle")
def data(ttl):
    dg = Graph(); dg += TB; dg.parse(data=PRE + ttl, format="turtle"); return dg
def fired(dg, red, focus):
    _, rg, _ = pyshacl.validate(dg, shacl_graph=red, advanced=True, inference="none")
    return any(str(rg.value(r, SH.focusNode)).endswith("#" + focus) for r in rg.subjects(RDF.type, SH.ValidationResult))
def derive(dg):
    out = set()
    for c in set(dg.subjects(RDF.type, None)):
        if (c, RDF.type, BL.WorkItemContainer) in dg or any(t in (BL.Package, BL.Iteration, BL.Backlog) for t in dg.objects(c, RDF.type)):
            for s, p, o in dg.query("PREFIX backlog: <http://example.org/backlog#> " + RULE.replace("$this", "<%s>" % c)):
                out.add((str(s).split("#")[-1], str(o).split("#")[-1]))
    return out
FAILS = []; N = [0]
def expect(what, ok):
    N[0] += 1
    if not ok: FAILS.append(what); print("FAIL ", what)
M = 'ex:M a backlog:Mission ; backlog:hasMissionStatement "alpha beta gamma" .\n'
A = 'ex:A a backlog:MissionAmendment ; backlog:amendsMission ex:M ; backlog:amendedMissionStatement "alpha beta gamma delta epsilon" .\n'
def dl(q): return 'ex:D a backlog:ScopeDeliverable ; backlog:derivesFromMissionClause "%s" .\n' % q
expect("a quote of the mission's own statement conforms", not fired(data(M + dl("beta gamma")), CIT, "D"))
expect("a quote of the amended statement conforms", not fired(data(M + A + dl("delta epsilon")), CIT, "D"))
expect("a quote of the earlier wording the amendment keeps conforms", not fired(data(M + A + dl("alpha beta")), CIT, "D"))
expect("a quote found in neither statement fires", fired(data(M + A + dl("zeta")), CIT, "D"))
expect("a quote of amended text with no amendment fires", fired(data(M + dl("delta epsilon")), CIT, "D"))
expect("a quote with no mission at all fires", fired(data(dl("alpha")), CIT, "D"))
def pair(kind1, kind2, done=False, extra=""):
    st = "backlog:Done" if done else "backlog:InProgress"
    return ("ex:C1 a backlog:%s . ex:C2 a backlog:%s .\n" % (kind1, kind2)
            + "ex:m a backlog:Story ; backlog:memberOfContainer ex:C1 ; backlog:dependsOn ex:d ; backlog:hasState backlog:InProgress .\n"
            + "ex:d a backlog:Story ; backlog:memberOfContainer ex:C2 ; backlog:hasState %s .\n" % st + extra)
expect("package to package derives", ("C1", "C2") in derive(data(pair("Package", "Package"))))
expect("iteration to iteration derives", ("C1", "C2") in derive(data(pair("Iteration", "Iteration"))))
expect("iteration to package derives nothing", not derive(data(pair("Iteration", "Package"))))
expect("package to iteration derives nothing", not derive(data(pair("Package", "Iteration"))))
expect("a backlog depending on a package derives nothing", not derive(data(pair("Backlog", "Package"))))
expect("a package depending on the backlog derives nothing", not derive(data(pair("Package", "Backlog"))))
expect("two backlogs derive nothing", not derive(data(pair("Backlog", "Backlog"))))
expect("a Done dependency derives nothing", not derive(data(pair("Package", "Package", done=True))))
und = pair("Package", "Package") + "ex:C1 backlog:derivedContainerDependency ex:C2 .\n"
expect("the advisory fires for an undeclared dependency of one kind", fired(data(und), UND, "C1"))
expect("the advisory is silent once the dependency is declared", not fired(data(und + "ex:C1 backlog:containerDependsOn ex:C2 .\n"), UND, "C1"))
print("VERDICT: %s -- %d expectations %s" % ("PASS" if not FAILS else "FAIL", N[0], "hold" if not FAILS else "(%d failed)" % len(FAILS)))
sys.exit(1 if FAILS else 0)
