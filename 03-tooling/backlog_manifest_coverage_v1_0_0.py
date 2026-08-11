#!/usr/bin/env python3
"""backlog_manifest_coverage_v1_0_0.py — nothing sits on disk uncovered and unexplained.

WHAT GATE 0 ALREADY DOES, AND WHAT IT CANNOT

Gate 0 verifies that every path LISTED in MANIFEST_SHA256.txt matches its recorded
hash. That is a complete check of the listed set and says nothing at all about the
unlisted one. A file could sit in the package covered by nothing, and Gate 0 would
report a clean pass — because from its side there is no difference between a file
deliberately excluded and a file forgotten.

This package ran that way for several releases. Its own self-check reported 62 OK
and 1 BAD, and separately one file present on disk appeared in no manifest line.
Both were the self-reference class and both were deliberate, but only the builder's
docstring said so, and a docstring is not the artifact anyone verifies.

WHAT THIS CHECKS

  1. every file on disk is either hashed in the manifest or named by an
     `# EXEMPT <path> — <reason>` line
  2. every declared exemption corresponds to a file that actually exists, so the
     list cannot accumulate entries for files long deleted
  3. every exemption carries a reason, because "not listed" and "deliberately not
     listed" are different facts and only the second can be reviewed

WHY THE THIRD MATTERS MOST

An exemption is the one way to remove a file from coverage without deleting it.
That makes it the obvious place to hide something, which is exactly why it must be
a visible line in a generated artifact rather than a silence. An exemption added to
conceal a file is then an edit someone can see and question; an exclusion buried in
a builder is not.

Exit 0 when every file is accounted for, 1 otherwise.

Usage: backlog_manifest_coverage_v1_0_0.py [package-root]
"""

import os
import re
import sys

MANIFEST = "MANIFEST_SHA256.txt"
BUILD_ARTIFACTS = (".pyc", ".pyo")


def read_manifest(path):
    hashed, exempt = set(), {}
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        m = re.match(r"^#\s*EXEMPT\s+(\S+)\s*—\s*(.+)$", line)
        if m:
            exempt[m.group(1)] = m.group(2).strip()
            continue
        m = re.match(r"^([0-9a-f]{64})\s+(.+?)\s+\(\d+b\)$", line)
        if m:
            hashed.add(m.group(2))
    return hashed, exempt


def on_disk(root):
    out = set()
    for dp, ds, fs in os.walk(root):
        ds[:] = [d for d in ds if d not in (".git", "__pycache__")]
        for f in fs:
            if f.endswith(BUILD_ARTIFACTS):
                continue
            out.add(os.path.relpath(os.path.join(dp, f), root))
    return out


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1
                           else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    mpath = os.path.join(root, MANIFEST)
    if not os.path.exists(mpath):
        print("coverage    : no %s in %s" % (MANIFEST, root))
        return 1

    hashed, exempt = read_manifest(mpath)
    disk = on_disk(root)

    uncovered = sorted(disk - hashed - set(exempt))
    stale = sorted(p for p in exempt if p not in disk)
    unreasoned = sorted(p for p, why in exempt.items() if not why)

    print("coverage    : %d hashed, %d declared exempt, %d file(s) on disk"
          % (len(hashed), len(exempt), len(disk)))
    for p, why in sorted(exempt.items()):
        print("  exempt    : %-24s %s" % (p, why[:78]))

    failed = False
    if uncovered:
        failed = True
        print("\n  UNCOVERED AND UNEXPLAINED (%d):" % len(uncovered))
        for p in uncovered:
            print("      %s" % p)
        print("  Gate 0 cannot see these: it verifies what is listed, and these are not.")
        print("  Either hash them or declare an exemption saying why they are not hashed.")
    if stale:
        failed = True
        print("\n  EXEMPT BUT ABSENT (%d): %s" % (len(stale), ", ".join(stale)))
        print("  An exemption for a file that no longer exists is a stale claim; the list")
        print("  would otherwise accumulate permissions nobody rechecks.")
    if unreasoned:
        failed = True
        print("\n  EXEMPT WITHOUT A REASON (%d): %s" % (len(unreasoned), ", ".join(unreasoned)))

    print("\nVERDICT     : %s" % ("PASS — every file is hashed or explained"
                                  if not failed else
                                  "FAIL — the package contains files coverage cannot account for"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
