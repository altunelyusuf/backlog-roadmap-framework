#!/usr/bin/env python3
"""backlog_open_lineage v1.1.0 -- write the opening block of a lineage from a profile (G155, G163).

A lineage is judged only by the rule sets it adopts (G89, G91), and the adoption is recorded at its opening (adoptionRecordedAtOpen). Doing that by hand,
rule set by rule set, is why consumers opened lineages that were not agentic: nobody knew the list. A profile (OpeningProfile) in the data file names the
list; this tool reads it and prints the block, so the choice is made once, by name.

  backlog_open_lineage.py --list                                   the profiles in the data file and what each includes
  backlog_open_lineage.py --profile Profile_Agentic --lineage Lineage_3 --prefix fzv
        prints Turtle for the lineage subject: openedWithProfile, adoptionRecordedAtOpen true, and one adoptsRuleSet per rule set of the profile.
        Put it in the commit of the lineage's Mission stage output (the order check witnesses each adoption against that commit, G148).
  --abox FILE overrides the data file (default: the newest backlog_abox in this package's 01-ontologies).
The block also names the profile revision the lineage opens under (openedUnderRevision, the highest in the data file), so a profile that grows later does not judge it (G163).
Exit 0, 2 on an unknown profile.
"""
import glob, os, re, sys
from rdflib import Graph, Namespace, RDF
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
B = Namespace("http://example.org/backlog#")
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]


def profiles(g):
    return {str(p).rsplit("#", 1)[-1]: sorted(str(r).rsplit("#", 1)[-1] for r in g.objects(p, B.profileIncludes)) for p in g.subjects(RDF.type, B.OpeningProfile)}


def latest_revision(g):
    rv = {int(n): str(r).rsplit("#", 1)[-1] for r in g.subjects(RDF.type, B.ProfileRevision) for n in g.objects(r, B.revisionNumber)}
    return rv[max(rv)] if rv else None


def block(profile, lineage, prefix, included, revision=None):
    sets = " ,\n        ".join("backlog:" + r for r in included)
    rev = f"    backlog:openedUnderRevision backlog:{revision} ;\n" if revision else ""
    return (f"{prefix}:{lineage} backlog:openedWithProfile backlog:{profile} ;\n{rev}    backlog:adoptionRecordedAtOpen true ;\n"
            f"    backlog:adoptsRuleSet\n        {sets} .\n")


def main(argv):
    opt = lambda k: argv[argv.index(k) + 1] if k in argv else None
    ab = opt("--abox") or sorted(glob.glob(os.path.join(PKG, "01-ontologies", "backlog_abox_v*.ttl")), key=sv)[-1]
    g = Graph(); g.parse(ab, format="turtle"); P = profiles(g)
    if "--list" in argv:
        for n, rs in sorted(P.items()):
            print(n + ": " + ", ".join(rs))
        return 0
    prof, lin = opt("--profile"), opt("--lineage")
    if not prof or not lin or prof not in P:
        print("REFUSED: give --profile (one of: %s) and --lineage" % ", ".join(sorted(P))); return 2
    print(block(prof, lin, opt("--prefix") or "ex", P[prof], latest_revision(g)), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
