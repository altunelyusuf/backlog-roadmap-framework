#!/usr/bin/env python3
"""backlog_vocabulary_derive v1.0.0 -- the controlled vocabulary of the framework, as a file a consumer can pin (G106).

The T-Box names its closed enumerations (lifecycle states, investment categories, ...) as owl:oneOf lists; the individuals themselves are defined in the A-box, which also
carries the framework's own register. The vocabulary IS the set of individuals the T-Box lists in its owl:oneOf lists -- no other rule, nothing chosen by hand. This tool
derives that set, with every statement the A-box makes about each member, into 01-ontologies/backlog_vocabulary_vX_Y_Z.ttl, and checks the file against a fresh derivation.

  backlog_vocabulary_derive_v1_0_0.py --check       exit 0 when the newest vocabulary file equals the derivation from the newest T-Box and A-box
  backlog_vocabulary_derive_v1_0_0.py --write FILE  write the derivation to FILE (a new version name; an existing file is never overwritten)
  --tbox FILE --abox FILE --vocab FILE              override the newest files in 01-ontologies/

Refuses (exit 3) when a member is not defined in the A-box, or a member's statements point at a subject that is not itself a member (it would not stand alone).
"""
import glob, os, re, sys
from rdflib import Graph, OWL, RDF, URIRef
from rdflib.collection import Collection
from rdflib.compare import isomorphic
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE); ONT = os.path.join(PKG, "01-ontologies")
def newest(pat):
    return sorted(glob.glob(os.path.join(ONT, pat)), key=lambda x: [int(n) for n in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", x)[0]])[-1]
def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default
def derive(tbox, abox):
    t = Graph().parse(tbox); a = Graph().parse(abox)
    members = set()
    for _, l in t.subject_objects(OWL.oneOf):
        members |= set(Collection(t, l))
    v = Graph()
    for p, n in a.namespaces(): v.bind(p, n)
    missing = sorted(str(m) for m in members if (m, None, None) not in a)
    stray = []
    for m in members:
        for p, o in a.predicate_objects(m):
            v.add((m, p, o))
            if isinstance(o, URIRef) and p != RDF.type and o not in members and (o, None, None) in a:
                stray.append((str(m), str(p), str(o)))
    return v, members, missing, stray
def main():
    tbox = arg("--tbox", newest("backlog_tbox_v*.ttl")); abox = arg("--abox", newest("backlog_abox_v*.ttl"))
    v, members, missing, stray = derive(tbox, abox)
    print(f"vocabulary: {len(members)} individual(s) listed by the T-Box ({os.path.basename(tbox)}), {len(v)} statement(s) from {os.path.basename(abox)}")
    if missing or stray:
        for m in missing: print("  NOT DEFINED in the A-box:", m)
        for s in stray: print("  POINTS OUT of the vocabulary:", s)
        return 3
    if "--write" in sys.argv:
        out = arg("--write", None)
        if os.path.exists(out): print("REFUSED: not overwriting", out); return 3
        v.serialize(out, format="turtle"); print("written", out); return 0
    voc = arg("--vocab", newest("backlog_vocabulary_v*.ttl"))
    cur = Graph().parse(voc)
    body = lambda g: {x for x in g if not (isinstance(x[0], URIRef) and str(x[0]).startswith("http://example.org/backlog-vocabulary"))}
    ok = body(cur) == body(v)
    print(f"  {os.path.basename(voc)}: " + ("equals the derivation" if ok else "DIFFERS from the derivation -- derive a new version (a changed file takes a new name)"))
    return 0 if ok else 3
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); sys.exit(0)
sys.exit(main())
