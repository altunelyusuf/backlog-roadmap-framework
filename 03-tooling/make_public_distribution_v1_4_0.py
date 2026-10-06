#!/usr/bin/env python3
# v1.4.0 (Lineage 17, OESC-S04): follows the package's new layout. The alignment file now lives in 06-package-provenance, which is dropped whole.
"""make_public_distribution v1.3.0 — derive the public variant, reproducibly.

A public copy of a governed package is a second copy of the same vocabulary, and
two copies drift. So this is a script, not a hand-scrub: the transformation is
declared here, re-runnable, and its output is regenerable from the governed
package at any time. Per BP-D26 as enriched at OE Pack v20.27.0 — a verification
(or a scrub) performed but not encoded proves the moment, not the property.

WHAT IS REMOVED, and why each is removed rather than edited:

  05-lesson-deposits/          proposals to OEE's lesson catalogue. Correspondence
                               with another session about their artifacts.
  06-package-provenance/       ORCP registration records, publish records, and
                               cross-session proposals — the same.
  07-handover-inbox/           incoming proposals from lineage-consumer sessions
                               (another registrant, code-abundance-rdodi, and others), pending,
                               accepted, rejected or deferred — correspondence
                               with other sessions about their own artifacts,
                               the same reason as the two directories above.
  06-package-provenance/  (the alignment file moved there at v1.339.0; the directory is dropped whole)
                               an alignment to ONE adopting project's private
                               deposit. Useless without that deposit and names it
                               throughout; scrubbing would leave an alignment to
                               nothing.
  04-documentation/Mapping_ProductBacklog_To_Backlog_v1_0_0.md
                               its companion document, likewise.
  04-documentation/ORCP_Submission_Backlog_v1_1_0.md
  04-documentation/OE_Registration_Readiness_Assessment_v1_0_0.md
  04-documentation/Discipline_Ceremony_Record_v1_0_0.md
  04-documentation/Discipline_Ceremony_Record_Addendum_v1_1_0.md
                               OE governance process records naming other
                               registrants and internal pack releases.

WHAT IS REWRITTEN rather than removed:

  Provenance sentences in skos:definition and prose that name the originating
  project are generalised to "an adopting project" / "an adopting project's
  product-backlog deposit". The FACT that the subject was generalised from a
  real deposit is true and worth keeping — L-112's spirit is that a record is
  corrected by stating the correction, not by pretending the history was
  different. What is removed is the identification, not the provenance.

WHAT IS DELIBERATELY KEPT:

  The author's name and institution. This is CC BY 4.0: attribution is not
  private data, it is the licence condition. Stripping it would breach the
  licence the package ships under. Only the unresolvable oe-prov: IRIs are
  replaced by literal attribution, since those dereference to nothing outside
  the ecosystem.

Usage: make_public_distribution_v1_3_0.py <governed-pkg> <output-dir>
"""

import os
import re
import shutil
import sys

DROP_DIRS = ["05-lesson-deposits", "06-package-provenance", "07-handover-inbox"]

DROP_FILES = [
    "04-documentation/Mapping_ProductBacklog_To_Backlog_v1_0_0.md",
    "04-documentation/ORCP_Submission_Backlog_v1_1_0.md",
    "04-documentation/OE_Registration_Readiness_Assessment_v1_0_0.md",
    "04-documentation/Discipline_Ceremony_Record_v1_0_0.md",
    "04-documentation/Discipline_Ceremony_Record_Addendum_v1_1_0.md",
    "04-documentation/Registration_Controls_v1_0_0.md",
    "04-documentation/Packaging_Requirements_v1_0_0.md",
    "03-tooling/backlog_registration_readiness_v1_2_0.py",
    "03-tooling/backlog_package_check_v1_0_0.py",
    "RELEASE_METRICS.txt",
    # the deriver removes ITSELF: its substitution patterns necessarily contain
    # the very names it strips, so shipping it in the public copy would
    # reintroduce them. Found by the leak scan before the first publication, and
    # again by the drift check, which reported the published copy as diverging
    # because the deriver was copying itself into its own output.
    "03-tooling/make_public_distribution_v1_3_0.py",
    "03-tooling/backlog_distribution_drift_check_v1_0_0.py",
]

# Order matters: longest and most specific first, so a later rule cannot
# re-match text an earlier one already generalised.
SUBSTITUTIONS = [
    # identified project -> generic adopter
    # Article-absorbing forms come FIRST. A bare-name rule applied to
    # "an adopting project X" yields "an adopting project X" — the substitution
    # is correct per-occurrence and the sentence is broken. Found by the
    # post-scrub damage check below, not by the residual scan, which is why
    # both exist.
    (r"\bthe an adopting project product-backlog deposit in OE Pack v[\d.]+[^)]*\)?",
     "an adopting project's product-backlog deposit"),
    (r"\bthe an adopting project product-backlog deposit", "an adopting project's product-backlog deposit"),
    (r"\bthe an adopting project\b", "an adopting project"),
    (r"\bThe an adopting project\b", "An adopting project"),
    (r"an adopting project's product-backlog deposit in OE Pack v[\d.]+",
     "an adopting project's product-backlog deposit"),
    (r"the adopting project's (own )?product-backlog deposit", r"an adopting project's product-backlog deposit"),
    (r"the originating project's methodology standard", "the originating project's methodology standard"),
    (r"an adopting project (session|project|register|deposit)", r"an adopting project"),
    (r"the adopting project's", "the adopting project's"),
    (r"\bFizyoVibe\b", "an adopting project"),
    (r"adopter-backlog-pattern", "adopter-backlog-pattern"),
    (r"\bfizyovibe\b", "adopting-project"),
    # other registrants
    (r"\bZT4SWE\b", "another registrant"),
    (r"\bRDODI\b", "another registrant"),
    (r"\bVAF\b", "another registrant"),
    (r"\bgradebook\b", "another registrant"),
    # private infrastructure
    (r"https://github\.com/the maintainer/[A-Za-z0-9_.-]+", "the project repository"),
    (r"github\.com/the maintainer/[A-Za-z0-9_.-]+", "the project repository"),
    (r"\baltunelyusuf\b", "the maintainer"),
    # unresolvable OE-internal provenance IRIs -> literal attribution
    (r""Yusuf Altunel"", '"Yusuf Altunel"'),
    (r""İstanbul Kültür Üniversitesi, Department of Computer Engineering"",
     '"İstanbul Kültür Üniversitesi, Department of Computer Engineering"'),
    (r"<http://example\.org/oe-prov#Agent_YusufAltunel>", '"Yusuf Altunel"'),
    (r"<http://example\.org/oe-prov#Org_IKU_Department_of_ComputerEngineering>",
     '"İstanbul Kültür Üniversitesi, Department of Computer Engineering"'),
    # any remaining oe-prov term or its prefix declaration: that namespace does
    # not resolve outside the ecosystem, so a public consumer gets a dead pointer
    (r"@prefix oe-prov:\s*<[^>]*>\s*\.\n", ""),
    (r"oe-prov:[A-Za-z_]+", '"OE provenance record"'),
    (r"<http://example\.org/oe-prov#[A-Za-z_]+>", '"OE provenance record"'),
    # internal pack paths
    (r"OE Pack v[\d.]+,\s*a registrant deposit[A-Za-z0-9_/-]*", "an OE Pack registrant deposit"),
    (r"a registrant deposit[A-Za-z0-9_/-]*", "a registrant deposit"),
]

# Damage the substitutions themselves can cause. A residual scan asks "is the
# identifier gone"; this asks "is the sentence still English". Different questions,
# and the first cannot answer the second — found when a bare-name rule turned
# "an adopting project deposit" into "an adopting project deposit".
DAMAGE = [
    (r"\bthe an\b", "an"), (r"\ba an\b", "an"), (r"\ban a\b", "a"),
    (r"\bthe the\b", "the"), (r"\bof an\b", "of an"),
]


TEXT_EXT = (".ttl", ".md", ".py", ".sh", ".txt", ".json")


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    if os.path.exists(dst):
        shutil.rmtree(dst)
    # .fixture-suite-stamp is a LOCAL cache key written by the gate after a passing
    # run. It is not part of the package: it records the state of one machine's
    # last run, so copying it makes a fresh derivation differ from any published
    # copy and the drift gate fails on a difference that means nothing. Found by
    # the drift gate refusing a publish for exactly this reason.
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
        "__pycache__", "*.pyc", ".git", ".fixture-suite-stamp",
        # .clause-proof-stamp is the same kind of thing and was missed when it
        # was added: a local cache key, meaningless in another checkout, and
        # shipping it made the drift gate report the public copy stale against
        # a fresh derivation that contained a file the public copy could not
        # have. One exclusion list, two caches, and only one was updated.
        ".clause-proof-stamp"))

    removed = []
    for d in DROP_DIRS:
        p = os.path.join(dst, d)
        if os.path.isdir(p):
            removed.append((d, sum(len(f) for _, _, f in os.walk(p))))
            shutil.rmtree(p)
    for f in DROP_FILES:
        p = os.path.join(dst, f)
        if os.path.exists(p):
            removed.append((f, 1))
            os.remove(p)

    rewritten = {}
    for dp, ds, fs in os.walk(dst):
        ds[:] = [x for x in ds if x != "__pycache__"]
        for f in sorted(fs):
            if not f.endswith(TEXT_EXT):
                continue
            p = os.path.join(dp, f)
            try:
                t = open(p, encoding="utf-8").read()
            except UnicodeDecodeError:
                continue
            orig = t
            n = 0
            for pat, rep in SUBSTITUTIONS:
                t, k = re.subn(pat, rep, t)
                n += k
            for pat, rep in DAMAGE:
                t, k = re.subn(pat, rep, t)
                n += k
            if t != orig:
                open(p, "w", encoding="utf-8").write(t)
                rewritten[os.path.relpath(p, dst)] = n

    print("source : %s" % src)
    print("output : %s" % dst)
    print("\nremoved (%d):" % len(removed))
    for name, n in removed:
        print("   %-58s %d file(s)" % (name, n))
    print("\nrewritten (%d files, %d substitutions):" % (rewritten and len(rewritten) or 0,
                                                        sum(rewritten.values())))
    for f, n in sorted(rewritten.items(), key=lambda kv: -kv[1])[:14]:
        print("   %-58s %d" % (f, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
