#!/usr/bin/env python3
"""backlog_shape_syntax_probe v1.0.0 -- the SPARQL in the shapes reads in more than one query engine (another registrant note, G124).

SPARQL allows a space between a function name and its bracket; a fast-path engine used by a consumer (pyoxigraph 0.5.11) refuses
`COALESCE ( ?a , ?b )`. Every select in the newest shapes file is written `NAME(` so one text reads in both. The probe fails on any
built-in function called with a space before its bracket, and proves it can fail by planting one. Exit 0 when it holds."""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
F = sorted(glob.glob(os.path.join(HERE, "..", "02-shacl-safeguards", "backlog_shacl_v*.ttl")), key=sv)[-1]
NAMES = ("COALESCE|BOUND|IF|STR|LANG|DATATYPE|REGEX|CONCAT|SUBSTR|STRLEN|UCASE|LCASE|CONTAINS|STRSTARTS|STRENDS|ABS|ROUND|CEIL|FLOOR|"
         "COUNT|SUM|MIN|MAX|AVG|SAMPLE|GROUP_CONCAT|ISIRI|ISURI|ISBLANK|ISLITERAL|ISNUMERIC|SAMETERM|URI|IRI|STRDT|STRLANG|YEAR|MONTH|DAY|NOW|REPLACE|ENCODE_FOR_URI")
PAT = re.compile(r"(?<![A-Za-z_:\"])(%s)[ \t]+\(" % NAMES)
def spaced(text):
    return [(i + 1, l.strip()[:80]) for i, l in enumerate(text.split("\n"))
            if not l.lstrip().startswith(("rdfs:", "sh:message", "#")) and "rdfs:label" not in l and PAT.search(l)]
bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
hits = spaced(open(F, encoding="utf-8").read())
expect("no built-in function in the newest shapes is called with a space before its bracket", not hits)
for h in hits[:5]: print("   ", os.path.basename(F), h)
expect("the probe can fail: a planted `COALESCE ( ?a , ?b )` is found", bool(spaced("BIND ( COALESCE ( ?a , ?b ) AS ?c )")))
expect("the closed form is accepted", not spaced("BIND ( COALESCE(?a, ?b) AS ?c )"))
try:
    import pyoxigraph
    pyoxigraph.Store().query("SELECT * WHERE { BIND ( COALESCE(?a, ?b) AS ?c ) }")
    expect("the fast-path engine reads the closed form", True)
except ImportError:
    print("NOTE  pyoxigraph is not installed here; the engine check was not made")
print("VERDICT   :", "PASS" if not bad else "FAIL")
sys.exit(1 if bad else 0)
