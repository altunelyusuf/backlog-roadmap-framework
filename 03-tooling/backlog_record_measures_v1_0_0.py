#!/usr/bin/env python3
"""backlog_record_measures v1.0.0 -- the counted measures of Lineage 19, computed from the data files and the tools (Lineage 19).

Each objective of the lineage counts something this package controls, and this tool is the method its observations cite: it reads the live data file,
the archive data file and 03-tooling, and prints each measure with the rows behind it, so a number can be re-derived by anyone.

  closure_gaps      ended missions (Achieved or Abandoned) with no closure report, plus cancelled items of an ended mission's lineage that its report does not name
  unmarked          lineage records in the archive file that do not say lineageArchived true
  modules_no_aud    module records (dcterms:isPartOf) that declare no moduleAudience
  archive_tools     tools in 03-tooling that find an archive folder by replacing a folder name in a path, or judge the archive with the live validator
  findings          retrospective findings about objective design (named Find_Objective...)
  silent_skips      places in the public-copy deriver that skip a module it cannot find without stopping (a 'continue' after a failed find of an END MODULE line)

Usage: backlog_record_measures_v1_0_0.py [--rows]
"""
import glob, os, re, sys
from rdflib import Graph, Namespace, RDF
from rdflib.namespace import DCTERMS

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = Namespace("http://example.org/backlog#")


def latest(sub, pat):
    hits = glob.glob(os.path.join(PKG, sub, pat))
    return sorted(hits, key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]])[-1]


def loc(x):
    return str(x).split("#")[-1]


def measures():
    live, arc = latest("01-ontologies", "backlog_abox_v*.ttl"), latest("01-ontologies/archive", "backlog_framework_archive_abox_v*.ttl")
    gl, ga = Graph().parse(live), Graph().parse(arc)
    g = Graph(); [g.add(t) for t in gl]; [g.add(t) for t in ga]
    rows = {}
    reports = {}
    for r in g.subjects(RDF.type, B.ClosureReport):
        reports.setdefault(g.value(r, B.closesForMission), []).append(r)
    missing, unnamed = [], []
    for m in sorted(set(g.subjects(B.hasMissionOutcome, None))):
        if g.value(m, B.hasMissionOutcome) not in (B.Out_Achieved, B.Out_Abandoned):
            continue
        if m not in reports:
            missing.append(loc(m))
        named = {x for r in reports.get(m, []) for x in g.objects(r, B.reportsCancelledItem)}
        for L in g.subjects(B.lineageForMission, m):
            for i in g.subjects(B.belongsToLineage, L):
                if g.value(i, B.hasState) == B.Cancelled and i not in named:
                    unnamed.append(loc(i))
    rows["closure_gaps"] = ([("no report: " + x) for x in sorted(set(missing))] + [("unnamed cancellation: " + x) for x in sorted(set(unnamed))])
    rows["unmarked"] = sorted(loc(L) for L in ga.subjects(RDF.type, B.Lineage) if (L, B.lineageArchived, None) in ga and not bool(ga.value(L, B.lineageArchived).toPython()))
    rows["modules_no_aud"] = sorted(loc(s) for s in set(g.subjects(DCTERMS.isPartOf, None)) if g.value(s, B.moduleAudience) is None)
    tools = []
    for f in sorted(glob.glob(os.path.join(PKG, "03-tooling", "*.py")) + glob.glob(os.path.join(PKG, "03-tooling", "*.sh"))):
        if os.path.basename(f).startswith("backlog_record_measures"):
            continue
        t = open(f, encoding="utf-8", errors="ignore").read()
        if re.search(r'replace\(\s*"01-ontologies"', t) or "run_conformance_full" in t:
            tools.append(os.path.basename(f))
    rows["archive_tools"] = tools
    rows["findings"] = sorted(loc(s) for s in gl.subjects(RDF.type, B.RetrospectiveFinding) if loc(s).startswith("Find_Objective"))
    sk = []
    for f in sorted(glob.glob(os.path.join(PKG, "03-tooling", "make_public_distribution_v*.py"))):
        t = open(f, encoding="utf-8").read()
        if re.search(r"if end < 0|e < 0:\s*\n\s*continue|text\.find\(end\)\s*\n\s*if e < 0:\s*\n\s*continue", t):
            sk.append(os.path.basename(f))
    rows["silent_skips"] = sk
    return rows


def main():
    rows = measures()
    show = "--rows" in sys.argv[1:]
    for k, v in rows.items():
        print("%-16s %d" % (k, len(v)))
        if show:
            for x in v:
                print("    -", x)
    return 0


if __name__ == "__main__":
    sys.exit(main())
