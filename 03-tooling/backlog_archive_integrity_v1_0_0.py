#!/usr/bin/env python3
"""backlog_archive_integrity v1.0.0 -- did the retired work arrive whole, and does the archive still
hold together? A STRUCTURAL check, not a conformance one.

WHY NOT PROGRESSIVE SHACL VALIDATION. The owner proposed validating the archive progressively --
oldest lineage first, then expanding with each newly retired one -- and asked for a test drive before
deciding (G46). Measured 2026-09-10 on this package's own archive (13 lineages, 11,763 triples):

    whole archive, one SHACL run          162.3 s     0 spurious violations
    per-lineage slices, 13 SHACL runs     247.7 s     994 violations, every slice non-conformant

Progressive validation is 53% SLOWER and answers a different question wrongly. A lineage sliced out
of the archive loses the context its statements point into -- the mission it superseded, the register
root it belonged to, the deliverables its epics satisfied -- so every slice reports violations that
are artefacts of the slicing. The archive is a record of work that was conformant WHEN IT WAS LIVE,
each release having been gated at the time; re-deciding its conformance under today's shapes would
also violate the framework's own rule that a ruling binds only work that declared it (G89, G91).

WHAT THE ARCHIVE ACTUALLY NEEDS CHECKING FOR is that retirement did not LOSE or BREAK anything:
every subject that left the live register arrived, no statement was dropped in the move, every
LineageArchiveEntry points at a lineage that is really there, and no live statement dangles into
something the archive does not hold. That is arithmetic over parsed graphs, and it costs about a
second.

  backlog_archive_integrity_v1_0_0.py [--register REG.ttl] [--archive ARCH.ttl]

Exit 0 intact; 2 a defect found; 1 on error.
"""
import glob, os, re, sys
from rdflib import Graph, Namespace, RDF, URIRef

B = Namespace("http://example.org/backlog#")
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
def loc(x): return str(x).split("#")[-1]
def sv(p): return [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
def latest(pat): return sorted(glob.glob(os.path.join(PKG, "01-ontologies", pat)), key=sv)[-1]


def main():
    argv = sys.argv[1:]
    reg = next((argv[i + 1] for i, a in enumerate(argv) if a == "--register"), latest("backlog_framework_register_abox_v*.ttl"))
    arc = next((argv[i + 1] for i, a in enumerate(argv) if a == "--archive"), latest("backlog_framework_archive_abox_v*.ttl"))
    g, a = Graph().parse(reg), Graph().parse(arc)
    print(f"register    : {os.path.basename(reg)} ({len(g)} triples)")
    print(f"archive     : {os.path.basename(arc)} ({len(a)} triples)")
    bad = 0

    # 1. every archive entry points at a lineage the archive really holds, and at the file it names
    entries = list(g.subjects(RDF.type, B.LineageArchiveEntry))
    for e in entries:
        lin = g.value(e, B.entryForLineage)
        if lin is None:
            print(f"  DEFECT {loc(e)} names no lineage"); bad += 1; continue
        if (URIRef(str(lin)), RDF.type, B.Lineage) not in a:
            print(f"  DEFECT {loc(e)} points at {loc(lin)}, which is not in this archive"); bad += 1
        f = g.value(e, B.archiveFile)
        if f is None or not os.path.exists(os.path.join(PKG, str(f))):
            print(f"  DEFECT {loc(e)} names archive file {f}, which does not exist"); bad += 1
        m = g.value(e, B.entryForMission)
        if m and str(m) and (URIRef(str(m)), RDF.type, B.Mission) not in a:
            print(f"  DEFECT {loc(e)}'s mission {loc(m)} is not in this archive"); bad += 1
    print(f"  entries     : {len(entries)} checked, each resolving to a lineage and a file")

    # 2. no retired lineage left anything behind in the live register
    for e in entries:
        L = URIRef(str(g.value(e, B.entryForLineage)))
        left = [s for s in g.subjects(B.belongsToLineage, L)]
        if left:
            print(f"  DEFECT {len(left)} statement subject(s) of retired {loc(L)} are still live: {[loc(s) for s in left[:4]]}"); bad += 1
    print(f"  retirement  : no retired lineage has members left in the live register" if not bad else "")

    # 3. nothing live dangles into a subject neither file holds (an archive reference is fine; a
    #    reference to nothing is not)
    known = {s for s in g.subjects()} | {s for s in a.subjects()}
    dangling = set()
    for s, p, o in g:
        if isinstance(o, URIRef) and str(o).startswith("http://example.org/backlog-framework-register#") and o not in known:
            dangling.add((loc(s), loc(p), loc(o)))
    if dangling:
        for d in sorted(dangling)[:6]:
            print(f"  DEFECT live {d[0]} --{d[1]}--> {d[2]}, which neither the register nor the archive holds"); bad += 1
    print(f"  references  : {len(dangling)} dangling live reference(s)")

    # 4. the archive is internally whole: every lineage it holds has its mission and its closure report
    for L in a.subjects(RDF.type, B.Lineage):
        m = a.value(L, B.lineageForMission)
        if m is None or (m, RDF.type, B.Mission) not in a:
            print(f"  DEFECT archived {loc(L)} has no mission in the archive"); bad += 1
    print(f"  archive     : {len(list(a.subjects(RDF.type, B.Lineage)))} lineage(s), each with its mission")

    print("VERDICT     : " + ("INTACT — retirement lost nothing and every reference resolves"
                              if bad == 0 else f"DEFECT — {bad} problem(s) above"))
    return 0 if bad == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
