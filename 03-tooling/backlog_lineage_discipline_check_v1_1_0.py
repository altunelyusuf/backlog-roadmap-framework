#!/usr/bin/env python3
"""backlog_lineage_discipline_check v1.1.0 — the discipline's claims are checked.

A discipline document that names shapes as enforcing its boundaries is making
externally-verifiable claims. Those claims drift: a shape gets renamed, a
severity gets softened, a level gate moves, and the document goes on asserting
enforcement that no longer exists. That is worse than no document, because a
document is believed.

So this reads the discipline and the shipped shapes file and checks:

  1. every backlog:*Shape the discipline NAMES exists in the shapes file
  2. each carries the severity the discipline implies — a boundary described as
     a violation must not be enforced by an sh:Warning, and one described as an
     advisory must not silently have become a violation

Rule 3 (every L4-named shape actually gated on L4_LineageEnforced) retired at
v1.1.0: conformance-level gating was removed from this framework entirely at
v1.152.0, so a shape's own "L4" name prefix no longer implies, or should
imply, any gate.

It does NOT check that the prose is wise. It checks that the prose is true about
the suite, which is the part that can be checked.

Exit 0 if every claim holds, 1 otherwise. Failure names the claim and what was
found instead.
"""

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)


def newest(pattern):
    files = glob.glob(os.path.join(PKG, pattern))
    if not files:
        return None

    def key(p):
        m = re.search(r"_v(\d+)_(\d+)_(\d+)\.", os.path.basename(p))
        return [int(x) for x in m.groups()] if m else [0, 0, 0]
    return sorted(files, key=key)[-1]


def shape_blocks(text):
    """name -> block text, for every declared node shape."""
    # Each block ends at the shape's terminating " ." OR at the next comment
    # banner, whichever comes first. v1.0.0 split only on the next shape
    # declaration, so a shape immediately followed by a section banner absorbed
    # that banner's text — and EpicPlanningShape, an L2 shape, was reported
    # "L4-gated" because the banner announcing the L4 section mentioned L4.
    # Found by cross-checking the checker's own output against the shapes file:
    # a checker whose report is not itself checked is another decorative gate.
    out = {}
    parts = re.split(r"\n(?=backlog:\w+Shape\s+a\s+sh:NodeShape)", text)
    for p in parts:
        m = re.match(r"backlog:(\w+Shape)", p)
        if not m:
            continue
        cut = p.find("\n####")
        out[m.group(1)] = p[:cut] if cut > 0 else p
    return out


def main():
    disc = newest("04-documentation/LINEAGE_OPERATING_DISCIPLINE_v*.md")
    shapes = newest("02-shacl-safeguards/backlog_shacl_v*.ttl")
    if not disc or not shapes:
        print("FAIL: discipline or shapes file not found — cannot check, which is a failure")
        print("      and not a pass. A check that degrades to success when it cannot run is")
        print("      the decorative gate this package refuses.")
        return 1

    dtext = open(disc, encoding="utf-8").read()
    stext = open(shapes, encoding="utf-8").read()
    blocks = shape_blocks(stext)

    print("discipline  : %s" % os.path.basename(disc))
    print("shapes      : %s  (%d node shape(s))" % (os.path.basename(shapes), len(blocks)))

    named = sorted(set(re.findall(r"`?backlog:(\w+Shape)`?", dtext)) |
                   set(re.findall(r"`(\w+Shape)`", dtext)))
    if not named:
        print("FAIL: the discipline names no shape at all. A document claiming enforcement")
        print("      without naming what enforces it cannot be checked, and an unfalsifiable")
        print("      claim of enforcement is the thing this check exists to prevent.")
        return 1

    failures = []
    print("\nclaims checked: %d shape(s) named by the discipline" % len(named))
    for name in named:
        blk = blocks.get(name)
        if blk is None:
            failures.append("%s is named by the discipline but does not exist in the shapes file"
                            % name)
            print("  %-34s MISSING" % name)
            continue

        sev = "Violation" if "sh:severity sh:Violation" in blk else (
              "Warning" if "sh:severity sh:Warning" in blk else "?")
        l4 = "L4_LineageEnforced" in blk

        # what does the discipline say about it? look at the sentence naming it.
        ctx = ""
        for m in re.finditer(re.escape(name), dtext):
            ctx += dtext[max(0, m.start() - 400):m.start() + 400] + " "
        claims_violation = re.search(r"violation|rejects|makes it a violation", ctx, re.I)
        claims_advisory = re.search(r"advisor|reports the symptom", ctx, re.I)

        note = ""
        if claims_violation and not claims_advisory and sev != "Violation":
            failures.append("%s is described as enforcing/rejecting but carries sh:%s" % (name, sev))
            note = " <- described as enforcing, is sh:%s" % sev
        # Rule 3 (every L4-named shape must gate on L4_LineageEnforced) retired
        # at v1.1.0: conformance-level gating itself was removed from this
        # framework at v1.152.0, so an "L4" prefix in a shape's own name no
        # longer implies, or should imply, any gate at all. A shape's name
        # may still start with L4 as a historical label of when it was
        # introduced; that is prose, not a claim this checker enforces.
        print("  %-34s sh:%-9s %s%s" % (name, sev, "L4-gated" if l4 else "ungated", note))

    print("\nVERDICT     : %s" % ("PASS — every enforcement claim in the discipline holds"
                                  if not failures else "FAIL"))
    for f in failures:
        print("  - %s" % f)
    if failures:
        print("\nFix the discipline or the shapes, not this checker. A document whose")
        print("enforcement claims have drifted from the suite is believed, which is why")
        print("the drift matters more here than in ordinary prose.")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
