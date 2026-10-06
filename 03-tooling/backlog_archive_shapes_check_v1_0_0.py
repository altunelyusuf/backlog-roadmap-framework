#!/usr/bin/env python3
"""backlog_archive_shapes_check v1.0.0 -- the archive is judged by the archive's own shapes, and by nothing else (Lineage 18, OC-S03).

The archive folder (01-ontologies/archive/) holds one data file and one shapes file. The shapes file asks only what a retired record must still
hold: an archived item names a lineage the archive holds, and a lineage held there says it is archived (a warning while two earlier lineages
are still unmarked). The live shapes never read this folder, so settled history is not re-judged by rules written for live work.

THE CHECK PROVES ITSELF EVERY RUN. Before it reports the real archive it adds one orphaned item (an item that names a lineage the archive does
not hold) to a copy and requires the shapes to flag it; if they do not, it refuses to certify and exits 3.

Exit 0 conformant (warnings counted and printed), 2 violation, 3 the check could not discriminate.
Usage: backlog_archive_shapes_check_v1_0_0.py
"""
import glob, os, re, sys, time
from rdflib import Graph, URIRef, Namespace

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = Namespace("http://example.org/backlog#")


def latest(pat):
    hits = glob.glob(os.path.join(PKG, "01-ontologies", "archive", pat))
    if not hits:
        raise SystemExit("no %s in 01-ontologies/archive" % pat)
    return sorted(hits, key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]])[-1]


def run(data, shapes):
    import pyshacl
    ok, rg, txt = pyshacl.validate(data, shacl_graph=shapes, inference="none", advanced=True, allow_warnings=True)
    return ok, txt


def main():
    a, s = latest("backlog_framework_archive_abox_v*.ttl"), latest("backlog_archive_shacl_v*.ttl")
    data, shapes = Graph().parse(a), Graph().parse(s)
    print("archive : %s (%d triples)" % (os.path.basename(a), len(data)))
    print("shapes  : %s" % os.path.basename(s))
    planted = Graph()
    for t in data:
        planted.add(t)
    planted.add((URIRef("http://example.org/planted#Orphan"), B.belongsToLineage, URIRef("http://example.org/planted#NoSuchLineage")))
    ok_p, txt_p = run(planted, shapes)
    if ok_p or "planted#Orphan" not in txt_p:
        print("SELF-PROOF : FAILED -- a planted orphaned item was not flagged. Nothing is certified.")
        return 3
    print("SELF-PROOF : ok -- a planted orphaned item is flagged")
    t0 = time.time()
    ok, txt = run(data, shapes)
    warn = len(re.findall(r"Severity: sh:Warning", txt)); viol = len(re.findall(r"Severity: sh:Violation", txt))
    print("result  : %d violation(s), %d warning(s) in %.1fs" % (viol, warn, time.time() - t0))
    for m in sorted(set(re.findall(r"Focus Node: (\S+)", txt)))[:6]:
        print("   -", m)
    print("VERDICT : " + ("CONFORMANT" if ok else "VIOLATIONS"))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
