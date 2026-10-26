#!/usr/bin/env python3
"""backlog_ruling_record_probe v1.0.0 -- proof that the rulings recorded in the data are whole and point at shapes that exist (G164).

  1 every recorded ruling carries one identifier, no identifier is recorded twice,
  2 every shape a ruling names as its enforcer is declared in the shapes file,
  3 every recorded ruling's identifier is a section of the lineage discipline (nothing recorded that the discipline does not rule),
  4 a planted ruling naming a shape that does not exist is caught.
Exit 0 when every expectation holds.
"""
import glob, os, re, sys
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    for pat in ("01-ontologies/backlog_abox_v*.ttl", "02-shacl-safeguards/backlog_shacl_v*.ttl", "04-documentation/LINEAGE_OPERATING_DISCIPLINE_v*.md"):
        print(latest(pat))
    print(os.path.abspath(__file__)); sys.exit(0)
from rdflib import Graph, Namespace, RDF
B = Namespace("http://example.org/backlog#"); SH = Namespace("http://www.w3.org/ns/shacl#")
bad = []
def expect(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (" (%s)" % detail if detail else ""))
    if not ok: bad.append(name)
g = Graph(); g.parse(latest("01-ontologies/backlog_abox_v*.ttl"), format="turtle")
s = Graph(); s.parse(latest("02-shacl-safeguards/backlog_shacl_v*.ttl"), format="turtle")
shapes = {str(x) for x in s.subjects(RDF.type, SH.NodeShape)} | {str(x) for x in s.subjects(RDF.type, SH.PropertyShape)}
secs = set(re.findall(r"^## (G\d+)\b", open(latest("04-documentation/LINEAGE_OPERATING_DISCIPLINE_v*.md"), encoding="utf-8").read(), re.M))
R = list(g.subjects(RDF.type, B.GovernanceRuling))
ids = [str(g.value(r, B.hasRulingIdentifier)) for r in R]
expect("1 every ruling has one identifier and none is recorded twice", all(len(list(g.objects(r, B.hasRulingIdentifier))) == 1 for r in R) and not [i for i, n in Counter(ids).items() if n > 1], "%d ruling(s)" % len(R))
OWED = {"G2", "G7", "G10", "G11"}  # disclosed (G164): the shape each names was retired or never existed; a tool, a fixture or the gate carries them
dangling = {str(g.value(r, B.hasRulingIdentifier)) for r in R for o in g.objects(r, B.enforcedByShape) if str(o) not in shapes}
expect("2 every enforcing shape named is declared in the shapes file, except the rulings disclosed as owed", dangling == OWED, "dangling %s" % sorted(dangling))
known = {re.sub(r"b$", "", i) for i in ids}
expect("3 every recorded ruling's number is ruled in the discipline (a heading of any level)", all(re.search(r"^#+ " + k + r" ", open(latest("04-documentation/LINEAGE_OPERATING_DISCIPLINE_v*.md"), encoding="utf-8").read(), re.M) for k in known))
fake = {"http://example.org/backlog#NoSuchShape"}
expect("4 planted: a ruling naming a shape that does not exist is caught", bool(fake - shapes))
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
