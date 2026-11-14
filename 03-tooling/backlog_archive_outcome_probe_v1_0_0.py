#!/usr/bin/env python3
"""backlog_archive_outcome_probe v1.0.0 -- the lineage archive tool states the outcome the mission has and reads the header however its version line ends (G235, box 47; IPage handover of 2026-11-10).

Cases: (1) an achieved lineage's trigger says achieved and Out_Achieved; (2) an abandoned lineage's trigger says abandoned and Out_Abandoned, names its closure report and the
cancelled items that report names, and says nothing of achieved; (3) a header whose versionInfo ends with a semicolon, with a full stop, or has other spacing moves, version
line, IRI and prior chain; (4) a first archive header whose version IRI closes the statement still parses as one statement after the move; (5) a header that does not read the
version is refused with the form the tool expects named. Exit 0 when every expectation holds."""
import glob, importlib.util, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
tool = sorted(glob.glob(os.path.join(HERE, "backlog_lineage_archive_v*.py")), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(tool); sys.exit(0)
spec = importlib.util.spec_from_file_location("lar", tool); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from rdflib import Graph
bad = []
def expect(n, ok):
    print(("PASS  " if ok else "FAIL  ") + n)
    if not ok: bad.append(n)
TTL = """@prefix backlog: <http://example.org/backlog#> . @prefix fw: <http://example.org/r#> .
fw:LA a backlog:Lineage ; backlog:lineageForMission fw:MA . fw:MA backlog:hasMissionOutcome backlog:Out_Achieved .
fw:RA backlog:closesForMission fw:MA .
fw:LB a backlog:Lineage ; backlog:lineageForMission fw:MB . fw:MB backlog:hasMissionOutcome backlog:Out_Abandoned .
fw:RB backlog:closesForMission fw:MB ; backlog:reportsCancelledItem fw:I1 , fw:I2 .
"""
g = Graph().parse(data=TTL, format="turtle")
a = m.trigger_text(g, m.URIRef("http://example.org/r#LA")) if hasattr(m, "URIRef") else None
from rdflib import URIRef
a = m.trigger_text(g, URIRef("http://example.org/r#LA")); b = m.trigger_text(g, URIRef("http://example.org/r#LB"))
expect("1 an achieved lineage's trigger says achieved, Out_Achieved and names its report", "Out_Achieved" in a and "found achieved" in a.lower() and "RA" in a and "abandon" not in a.lower())
expect("2 an abandoned lineage's trigger says abandoned and Out_Abandoned", "Out_Abandoned" in b and "abandoned" in b.lower())
expect("2 it says nothing of achieved", "achieved" not in b.lower())
expect("2 it names its closure report and the 2 cancelled items it names", "RB" in b and "2 cancelled item" in b)
H = ('<http://e.org/a> a owl:Ontology ;\n    owl:versionIRI <http://e.org/a/1.2.0> ;\n    owl:versionInfo "1.2.0"%s\n    owl:priorVersion <http://e.org/a/1.1.0>%s\n')
t, why = m.move_header(H % (" ;", " ."), "1.2.0", "1.3.0")
expect("3 a version line ending with a semicolon moves", why is None and 'owl:versionInfo "1.3.0" ;' in t and "a/1.3.0>" in t and "a/1.2.0> , <http://e.org/a/1.1.0>" in t)
t, why = m.move_header('<http://e.org/a> a owl:Ontology ;\n    owl:priorVersion <http://e.org/a/1.1.0> ;\n    owl:versionIRI <http://e.org/a/1.2.0> ;\n    owl:versionInfo "1.2.0" .\n', "1.2.0", "1.3.0")
expect("3 a version line ending the header with a full stop moves, the full stop kept", why is None and t.rstrip().endswith('owl:versionInfo "1.3.0" .') and "a/1.2.0> , <http://e.org/a/1.1.0>" in t)
t, why = m.move_header(H.replace('owl:versionInfo "1.2.0"%s', 'owl:versionInfo   "1.2.0"   %s') % (";", " ."), "1.2.0", "1.3.0")
expect("3 other spacing moves", why is None and '"1.3.0"' in t and "1.2.0\"" not in t)
g2 = '@prefix owl: <http://www.w3.org/2002/07/owl#> .\n'
t, why = m.move_header('<http://e.org/a> a owl:Ontology ;\n    owl:versionInfo "1.0.0" ;\n    owl:versionIRI <http://e.org/a/1.0.0> .\n', "1.0.0", "1.1.0", first_chain_ok=True)
ok4 = why is None
if ok4:
    try:
        gg = Graph().parse(data=g2 + t, format="turtle"); ok4 = len(gg) == 4
    except Exception as e:
        ok4 = False
expect("4 a first header whose version IRI closes the statement is still one valid statement after the move", ok4)
t, why = m.move_header(H % (" ;", " ."), "9.9.9", "10.0.0")
expect("5 a header that does not read the version is refused, naming the form expected", t is None and "form expected" in why and "owl:versionInfo" in why and ";" in why and "." in why)
print("VERDICT   :", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
