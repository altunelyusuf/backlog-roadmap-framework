#!/usr/bin/env python3
"""backlog_repoint v1.1.0 — corpus-wide rename that cannot corrupt the record.

Adopting L-112, catalogued at OE Pack v20.26.0 from this package's own defect: a
mechanical repoint is correct for every file that DESCRIBES the current state and
wrong for every file that RECORDS a past one. A global `sed` across the
documentation directory rewrote a historical changelog entry to name a tool
version that did not exist at the release the entry describes. Every match was a
genuine occurrence; the repoint was correct per-occurrence and still made the
record false.

L-112's operative clause is why this file exists rather than a note in a README:

    "A repoint script names its exclusions explicitly, so that the exclusion is a
    property of the tool rather than of whoever remembers to pass a flag."

So the exclusions below are not a flag, a default, or a convention. They are the
tool. There is no option to disable them.

THREE CLASSES, per L-112 as amended at OE Pack v20.26.1. The two-way split this
tool first implemented was incomplete, and its own dry run is what surfaced the
gap: repointing an ontology filename token reported MANIFEST_SHA256.txt as a file
it would edit. Under the two-way split that was correct — a manifest is not a
record of the past — which is what made the split wrong rather than the tool.

  (a) CURRENT-STATE DESCRIPTIONS — ontologies, shapes, rules, fixtures, tools,
      README, the standard, packaging requirements. Editable; the actual target.

  (b) HISTORICAL RECORDS — statements of fact about a past release. Excluded by
      class. Corrected only by appending a dated correction or shipping a new
      versioned entry that says what the earlier one got wrong.
        CHANGELOG_v*, registration_intent_v*, OE_Ceremony_Record*,
        *_audit_v*, Coverage_Report_v*, *_assessment_v* (prose),
        *_proposal_v*, *_emission_v*, *_declaration_v*, *_note_v*,
        *_response_v*, 05-lesson-deposits/*, 06-package-provenance/*.md

  (c) GENERATED ARTIFACTS — derived from the current tree, not records of the
      past. Excluded for a different reason and with a different remedy: a text
      edit desynchronises them from what they describe, and a manifest is the
      worst case because repointing a filename token inside it rewrites the
      integrity instrument itself. REGENERATE after the repoint; never edit.
        MANIFEST_SHA256.txt, RELEASE_METRICS.txt, *_quality_assessment_v*.ttl

Classification is by ROLE, not by file extension. The first version guarded
06-package-provenance for *.md only, so a dated measurement in Turtle sat in the
editable set while its Markdown analogue was protected — the same class landing
differently by suffix. Role tokens are matched case-insensitively against the
filename whatever the suffix.

A historical record that is wrong is corrected by appending a dated correction or
by a new versioned entry saying what the earlier one got wrong — never by
rewriting the earlier text.

Usage:
  backlog_repoint_v1_1_0.py OLD NEW [--apply]      # dry-run unless --apply
"""

import argparse
import fnmatch
import os
import sys

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GENERATED = [
    "manifest_sha256.txt",
    "release_metrics.txt",
    "*_quality_assessment_v*",
]
HISTORICAL = [
    "changelog_v*",
    "registration_intent_v*",
    "oe_ceremony_record*",
    "*_audit_v*",
    "coverage_report_v*",
    "*_assessment_v*",
    "*_proposal_v*",
    "*_emission_v*",
    "*_declaration_v*",
    "*_note_v*",
    "*_response_v*",
]
HISTORICAL_DIRS = ["05-lesson-deposits"]
HISTORICAL_DIR_GLOBS = [("06-package-provenance", "*.md")]
SKIP_DIRS = {"__pycache__"}


def classify(relpath, name):
    """Return (class, reason) for a file, matching role tokens case-insensitively
    and never on the extension alone."""
    low = name.lower()
    for pattern in GENERATED:
        if fnmatch.fnmatch(low, pattern):
            return "generated", "generated artifact — regenerate, never edit"
    if any(relpath.startswith(d + os.sep) or relpath == d for d in HISTORICAL_DIRS):
        return "historical", "deposit record"
    for d, pattern in HISTORICAL_DIR_GLOBS:
        if relpath.startswith(d + os.sep) and fnmatch.fnmatch(low, pattern):
            return "historical", "past exchange record"
    for pattern in HISTORICAL:
        if fnmatch.fnmatch(low, pattern):
            return "historical", "historical record"
    return "current", None


def main():
    ap = argparse.ArgumentParser(description="Repoint a name across current-state files only.")
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--apply", action="store_true", help="write changes; omit for a dry run")
    args = ap.parse_args()

    edited, historical, generated, untouched = [], [], [], 0
    for dirpath, dirs, files in os.walk(PKG):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in sorted(files):
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, PKG)
            try:
                text = open(full, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            if args.old not in text:
                untouched += 1
                continue
            cls, why = classify(rel, name)
            if cls == "historical":
                historical.append((rel, text.count(args.old), why))
                continue
            if cls == "generated":
                generated.append((rel, text.count(args.old), why))
                continue
            edited.append((rel, text.count(args.old)))
            if args.apply:
                open(full, "w", encoding="utf-8").write(text.replace(args.old, args.new))

    print("repoint     : %r -> %r  (%s)" % (args.old, args.new, "APPLIED" if args.apply else "dry run"))
    print("\nwould edit (current-state files):" if not args.apply else "\nedited:")
    for rel, n in edited:
        print("   %-56s %d occurrence(s)" % (rel, n))
    if not edited:
        print("   none")
    print("\nPROTECTED — historical records. A match here is a fact about a past release:")
    for rel, n, why in historical:
        print("   %-56s %d occurrence(s)   [%s]" % (rel, n, why))
    if not historical:
        print("   none")
    print("\nPROTECTED — generated artifacts. A text edit would desynchronise them:")
    for rel, n, why in generated:
        print("   %-56s %d occurrence(s)   [%s]" % (rel, n, why))
    if not generated:
        print("   none")
    print("\n%d editable, %d historical, %d generated, %d without a match."
          % (len(edited), len(historical), len(generated), untouched))
    if historical:
        print("Historical: append a dated correction or ship a new versioned entry saying what the")
        print("earlier one got wrong. Do not rewrite it.")
    if generated:
        print("Generated: REGENERATE after the repoint — build_manifest, then release_metrics.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
