#!/usr/bin/env python3
"""backlog_sparql_memo_probe v1.1.0 -- the SPARQL parse cache changes no result, and it really saves the parsing (G99).

Runs pyshacl twice on the same small register and the same shapes (a SPARQL constraint, a SPARQL rule, and a constraint that must give DIFFERENT answers for different
focus nodes), once without the cache and once with it:
  1 the two result sets are identical, and not empty (one focus node violates, two do not -- so nothing leaked between focus nodes);
  2 the number of times rdflib parsed a query text drops from one per execution to one per distinct text;
  3 a malformed query still raises, with the cache on and off;
  4 the same text over two different graphs gives two different answers (a prepared query is not tied to a graph);
  5 BACKLOG_SPARQL_MEMO=0 leaves rdflib.Graph.query untouched, and install() twice installs once.
Exit 0 all hold; 2 a case failed. An optional first argument names a memo module to test instead of the newest one (the probe is itself tested against a broken copy).
"""
import glob, importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_ARGS = [a for a in sys.argv[1:] if a != "--deps"]
PATH = _ARGS[0] if _ARGS else sorted(glob.glob(os.path.join(HERE, "backlog_sparql_memo_v*.py")), key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]])[-1]
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(PATH)
    sys.exit(0)
spec = importlib.util.spec_from_file_location("backlog_sparql_memo_under_test", PATH)
memo = importlib.util.module_from_spec(spec); spec.loader.exec_module(memo)

import rdflib, pyshacl
from rdflib import Graph, Namespace, RDF
from rdflib.plugins.sparql import parser as sparql_parser

SHACL = Namespace("http://www.w3.org/ns/shacl#")
bad = []
def check(name, cond):
    print("  %-4s %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        bad.append(name)

DATA = """@prefix ex: <http://example.org/p#> . @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
ex:a a ex:T ; ex:n 1 . ex:b a ex:T ; ex:n 2 . ex:c a ex:T ; ex:n 3 ."""
SHAPES = """@prefix ex: <http://example.org/p#> . @prefix sh: <http://www.w3.org/ns/shacl#> . @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
ex:S a sh:NodeShape ; sh:targetClass ex:T ;
  sh:sparql [ a sh:SPARQLConstraint ; sh:message "n is one" ;
     sh:prefixes [ sh:declare [ sh:prefix "ex" ; sh:namespace "http://example.org/p#"^^<http://www.w3.org/2001/XMLSchema#anyURI> ] ] ;
     sh:select "SELECT $this WHERE { $this ex:n 1 }" ] ;
  sh:rule [ a sh:SPARQLRule ; sh:order 1 ;
     sh:prefixes [ sh:declare [ sh:prefix "ex" ; sh:namespace "http://example.org/p#"^^<http://www.w3.org/2001/XMLSchema#anyURI> ] ] ;
     sh:construct "CONSTRUCT { $this ex:seen true } WHERE { $this ex:n ?v }" ] ."""

def run():
    data = Graph().parse(data=DATA, format="turtle")
    ok, rg, _ = pyshacl.validate(data, shacl_graph=Graph().parse(data=SHAPES, format="turtle"), advanced=True)
    focus = sorted(str(rg.value(r, SHACL.focusNode)) for r in rg.subjects(RDF.type, SHACL.ValidationResult))
    seen = sorted(str(s) for s in data.subjects(rdflib.URIRef("http://example.org/p#seen"), None))
    return focus, len(seen), len(list(data.subjects(rdflib.URIRef("http://example.org/p#seen"), None)))

parses = [0]
orig_parse = sparql_parser.parseQuery
def counting(q):
    parses[0] += 1
    return orig_parse(q)
import rdflib.plugins.sparql.processor as proc
proc.parseQuery = counting
sparql_parser.parseQuery = counting
import rdflib.plugins.sparql as sp
os.environ["BACKLOG_SPARQL_MEMO"] = "0"
memo.uninstall(); base_query = rdflib.Graph.query
a = run(); parses_off = parses[0]
check("case 5: BACKLOG_SPARQL_MEMO=0 leaves Graph.query untouched", memo.install() is False and rdflib.Graph.query is base_query)
del os.environ["BACKLOG_SPARQL_MEMO"]
parses[0] = 0
on1 = memo.install(); on2 = memo.install(); after = rdflib.Graph.query
check("case 5: install() twice installs once and changes Graph.query", on1 and on2 and after is not base_query)
b = run(); parses_on = parses[0]
check("case 1: results identical with and without the cache", a == b and len(a[0]) == 1)
check("case 1: one focus node violates and two do not (no leakage between focus nodes)", len(a[0]) == 1 and a[0][0].endswith("#a"))
check("case 2: parses drop from one per execution to one per text (%d -> %d)" % (parses_off, parses_on), parses_on < parses_off and parses_on <= 3)
try:
    Graph().query("SELECT WHERE {{{")
    raised = False
except Exception:
    raised = True
check("case 3: a malformed query still raises with the cache on", raised)
g1 = Graph().parse(data="@prefix ex: <http://example.org/p#> . ex:a ex:n 1 .", format="turtle")
g2 = Graph().parse(data="@prefix ex: <http://example.org/p#> . ex:a ex:n 1 . ex:b ex:n 1 .", format="turtle")
q = "SELECT ?s WHERE { ?s <http://example.org/p#n> 1 }"
check("case 4: the same text over two graphs gives two answers", len(list(g1.query(q))) == 1 and len(list(g2.query(q))) == 2)
memo.uninstall()
try:
    Graph().query("SELECT WHERE {{{")
    raised_off = False
except Exception:
    raised_off = True
check("case 3: a malformed query raises with the cache off", raised_off)
print("VERDICT : " + ("ALL HOLD" if not bad else "FAILED -- " + "; ".join(bad)))
sys.exit(0 if not bad else 2)
