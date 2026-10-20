#!/usr/bin/env python3
"""backlog_links_not_text_probe v1.0.0 -- a connection is a link, never text (T-Box v1.136.0, A-Box v1.52.0, shapes v1.175.0, G134).

What it shows, on the shipped files and on small planted graphs:
  1 the five properties that used to hold text (entryForLineage, entryForMission, entryOutcome, includesRetiredLineage, tableInModule) are object properties with a range,
  2 every value they hold in the shipped data is a link (never a literal), and it resolves to a thing of the range's class (the archived lineage and mission in the archive file),
  3 the seven properties that lacked a domain or a range now declare it (outScopes, assembledFor, hasExpectedPolarity, addressesFinding, promotedSeverity, promotesShape, moduleAudience),
  4 the relationships the definitions stated in words are links in the data (success mirror, horizon expectation, initiative-level counterpart, stage concerned),
  5 text where a link belongs is advised by the shapes (a planted text value draws a warning for each of the five; the same value as a link draws none).
Exit 0 when every expectation holds, 1 otherwise."""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
TB, AB = latest("01-ontologies/backlog_tbox_v*.ttl"), latest("01-ontologies/backlog_abox_v*.ttl")
ARC, SH = latest("01-ontologies/archive/backlog_framework_archive_abox_v*.ttl"), latest("02-shacl-safeguards/backlog_shacl_v*.ttl")
if sys.argv[1:] == ["--deps"]:
    print("\n".join([TB, AB, ARC, SH, os.path.abspath(__file__)])); sys.exit(0)
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL
from rdflib.namespace import XSD
from pyshacl import validate
B = Namespace("http://example.org/backlog#"); SHNS = Namespace("http://www.w3.org/ns/shacl#")
t = Graph(); t.parse(TB, format="turtle"); a = Graph(); a.parse(AB, format="turtle"); arc = Graph(); arc.parse(ARC, format="turtle")
bad = []
def expect(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (" (%s)" % detail if detail else ""))
    if not ok:
        bad.append(name)

FIVE = {"entryForLineage": B.Lineage, "entryForMission": B.Mission, "entryOutcome": B.MissionOutcome, "includesRetiredLineage": B.Lineage, "tableInModule": B.ToolScript}
expect("1 the five are object properties with their range",
       all((B[p], RDF.type, OWL.ObjectProperty) in t and (B[p], RDFS.range, rng) in t for p, rng in FIVE.items()))
vals = {p: list(a.objects(None, B[p])) for p in FIVE}
expect("2a the data holds values for each of the five", all(vals[p] for p in FIVE), ", ".join("%s %d" % (p, len(v)) for p, v in vals.items()))
expect("2b no value of the five is text", not [v for p in FIVE for v in vals[p] if isinstance(v, Literal)])
def typed(x, cls):
    return (x, RDF.type, cls) in a or (x, RDF.type, cls) in arc or (x, RDF.type, cls) in t
expect("2c every value resolves to a thing of the range's class", all(typed(v, FIVE[p]) for p in FIVE for v in vals[p]),
       "unresolved: %s" % sorted({str(v).split("#")[-1] for p in FIVE for v in vals[p] if not typed(v, FIVE[p])})[:5])

U = lambda c: any(True for _ in t.objects(c, OWL.unionOf)) if c is not None else False
def has(prop, kind):
    return t.value(B[prop], kind) is not None
need = {"outScopes": RDFS.range, "assembledFor": RDFS.range, "hasExpectedPolarity": RDFS.domain, "addressesFinding": RDFS.domain,
        "promotedSeverity": RDFS.range, "promotesShape": RDFS.range, "moduleAudience": RDFS.domain}
expect("3 the seven properties declare the domain or range they lacked", all(has(p, k) for p, k in need.items()),
       "missing: %s" % [p for p, k in need.items() if not has(p, k)])

def used(p):
    return len(list(a.subject_objects(B[p])))
links = {"successMirrorOf": 2, "horizonExpectsState": 1, "initiativeLevelCounterpart": 1, "concernsStage": 3}
expect("4 the relationships stated in words are links in the data", all(used(p) >= n for p, n in links.items()),
       ", ".join("%s %d" % (p, used(p)) for p in links))

shapes = Graph(); shapes.parse(SH, format="turtle")
def warnings(text):
    g = Graph(); g.parse(data="@prefix backlog: <http://example.org/backlog#> .\n@prefix ex: <http://example.org/p#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n" + text, format="turtle")
    _, rg, _ = validate(g, shacl_graph=shapes, advanced=True, inference="none", abort_on_first=False)
    out = set()
    for r in rg.subjects(RDF.type, SHNS.ValidationResult):
        path = str(rg.value(r, SHNS.resultPath)).split("#")[-1]
        if rg.value(r, SHNS.resultSeverity) == SHNS.Warning and path in FIVE:
            out.add(path)
    return sorted(out)
TEXT = ('ex:E a backlog:LineageArchiveEntry ; backlog:entryForLineage "http://example.org/p#L" ; backlog:entryForMission "http://example.org/p#M" ; backlog:entryOutcome "Out_Achieved" .\n'
        'ex:R a backlog:ArchiveConformanceRecord ; backlog:includesRetiredLineage "http://example.org/p#L" .\n'
        'ex:T a backlog:CodeTable ; backlog:tableInModule "tool.py" .\n')
LINK = ('ex:E a backlog:LineageArchiveEntry ; backlog:entryForLineage ex:L ; backlog:entryForMission ex:M ; backlog:entryOutcome backlog:Out_Achieved .\n'
        'ex:R a backlog:ArchiveConformanceRecord ; backlog:includesRetiredLineage ex:L .\n'
        'ex:T a backlog:CodeTable ; backlog:tableInModule ex:TS .\nex:TS a backlog:ToolScript .\n')
wt, wl = warnings(TEXT), warnings(LINK)
expect("5a text where a link belongs draws a warning for each of the five", wt == sorted(FIVE), ",".join(wt))
expect("5b the same values as links draw none", wl == [], ",".join(wl))
print("VERDICT: %s" % ("PASS -- every expectation holds" if not bad else "FAIL -- " + "; ".join(bad)))
sys.exit(1 if bad else 0)
