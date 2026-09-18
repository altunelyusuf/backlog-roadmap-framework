#!/usr/bin/env python3
"""backlog_archive_reconcile v2.0.0 -- per-lineage archival confirmation, deferred by one cycle.

WHY. Two real, separate gaps, both from the owner's own review, 2026-09-18:

(1) lineageArchived on an archived Lineage's own copy was never flipped from false to true --
    a dead loop (`for L in []:`) in backlog_lineage_archive meant the fix-up code that was always
    there never ran. Fixed at the source now (v2.2.0); this tool still backfills any pre-existing
    case the source fix predates.

(2) A much bigger one: re-validating the WHOLE archive file every time its digest changes means a
    single new arrival forces every already-settled lineage back through today's complete shape
    suite -- the exact retroactive-enforcement mistake G89/G91 already rules against, just applied
    per-file instead of per-lineage. The owner's fix: an archived lineage that holds the standards
    of its own era is a confirmation, not a fault, and once confirmed it must never be
    re-litigated against later rules. The exemption unit moves from one whole-file digest to one
    ArchivalConfirmationStatus per lineage.

WHAT IT DOES. For every real LineageArchiveEntry in the register:
  - No hasArchivalConfirmationStatus yet -> sets AC_PendingConfirmation. Not confirmed yet on
    purpose: confirming requires the archive commit carrying this lineage to already be real, the
    same reason closedAtCommit/closureCommittedAt are deferred, self-referencing tags rather than
    asserted at write time.
  - Already AC_PendingConfirmation -> its own commit is now real (this is a later, real run).
    Validates it for real via backlog_archive_conformance's own full-context run, parses the real
    violations, and promotes to AC_Confirmed only if none are attributed to this lineage's own
    subjects. If real violations are found, stays Pending and reports them honestly -- not silently
    promoted, not silently dropped.
  - Already AC_Confirmed -> left alone. Never re-validated again, regardless of what later rules
    the shape suite gains.

Usage: backlog_archive_reconcile_v2_0_0.py <register.ttl> <archive.ttl> [--apply]
  --apply writes status changes and, before applying a promotion, the real conformance
  violations checked. Without --apply, reports what would happen without writing anything.
"""
import re
import subprocess
import sys
import os


def block_of(text, local_name):
    m = re.search(rf'fw:{re.escape(local_name)}\s+a\s+backlog:Lineage\b', text)
    if not m:
        return None, None, None
    start = m.start()
    next_subj = re.search(r'\nfw:\w+ ', text[start + 1:])
    end = start + 1 + next_subj.start() if next_subj else len(text)
    return start, end, text[start:end]


def run_conformance(archive_path):
    """Runs the real, existing archive-conformance tool and returns its raw stdout -- the same
    tool already proven this session to correctly validate the full archive context; reused
    rather than re-implemented, since a second, parallel validator is a second place to be wrong."""
    tool_dir = os.path.dirname(os.path.abspath(archive_path)).replace(
        "01-ontologies", "03-tooling")
    candidates = [f for f in os.listdir(tool_dir) if f.startswith("backlog_archive_conformance_v")]
    if not candidates:
        return None
    tool = os.path.join(tool_dir, sorted(candidates)[-1])
    register_dir = os.path.dirname(archive_path)
    reg_candidates = [f for f in os.listdir(register_dir)
                       if f.startswith("backlog_framework_register_abox_v")]
    if not reg_candidates:
        return None
    reg_path = os.path.join(register_dir, sorted(reg_candidates)[-1])
    r = subprocess.run(["python3", tool, reg_path], capture_output=True, text=True)
    return r.stdout


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        sys.exit(2)
    register_path, archive_path = args[0], args[1]
    apply = "--apply" in args

    with open(register_path) as f:
        reg = f.read()
    with open(archive_path) as f:
        arc = f.read()

    entries = []
    for m in re.finditer(
        r'backlog:entryForLineage\s+"[^"]*#(\w+)"\s*;.*?backlog:archiveFile\s+"([^"]+)"',
        reg, re.DOTALL):
        entries.append((m.group(1), m.group(2)))

    to_pend, to_confirm, already_confirmed, unresolved = [], [], [], []

    for local_name, archive_file in entries:
        if not archive_file.endswith(archive_path.split("/")[-1]):
            continue
        start, end, block = block_of(arc, local_name)
        if block is None:
            print(f"  SKIP {local_name}: not found as a Lineage individual in this archive file")
            continue
        if "backlog:lineageArchived false" in block:
            to_pend.append((local_name, "lineageArchived_fix_and_pend"))
        elif "backlog:hasArchivalConfirmationStatus backlog:AC_Confirmed" in block:
            already_confirmed.append(local_name)
        elif "backlog:hasArchivalConfirmationStatus backlog:AC_PendingConfirmation" in block:
            to_confirm.append(local_name)
        else:
            to_pend.append((local_name, "pend_only"))

    print(f"entries checked: {len(entries)}")
    print(f"already confirmed, left alone: {len(already_confirmed)}")
    print(f"to set pending: {len(to_pend)}  -- {[n for n, _ in to_pend]}")
    print(f"pending -> attempting confirmation: {len(to_confirm)}  -- {to_confirm}")

    if not to_pend and not to_confirm:
        print("VERDICT: nothing to reconcile")
        return

    conformance_out = None
    if to_confirm:
        conformance_out = run_conformance(archive_path)
        if conformance_out is None:
            print("  GATE ABORT: could not run backlog_archive_conformance for real validation")
            sys.exit(3)
        for name in to_confirm:
            hits = [l for l in conformance_out.splitlines() if l.strip().startswith(name + ":")]
            if hits:
                unresolved.append((name, hits))
            else:
                pass  # clean -- promoted below

    print(f"real violations found on pending lineages: {sum(len(h) for _, h in unresolved)}")
    for name, hits in unresolved:
        for h in hits:
            print(f"    {h.strip()}")

    if not apply:
        print("VERDICT: RECONCILABLE -- re-run with --apply to write the real status changes")
        return

    new_arc = arc
    for local_name, mode in to_pend:
        start, end, block = block_of(new_arc, local_name)
        cleaned = re.sub(r'\s*backlog:lineageArchived\s+false\s*;', '', block)
        already_true = "backlog:lineageArchived true" in cleaned
        pattern = re.compile(rf'(fw:{re.escape(local_name)}\s+a\s+backlog:Lineage\s*;)')
        insertion = (
            r'\1 backlog:hasArchivalConfirmationStatus backlog:AC_PendingConfirmation ;'
            if already_true else
            r'\1 backlog:lineageArchived true ; backlog:hasArchivalConfirmationStatus backlog:AC_PendingConfirmation ;'
        )
        cleaned, n = pattern.subn(insertion, cleaned, count=1)
        if n != 1:
            print(f"  GATE ABORT: could not set pending for {local_name}")
            sys.exit(3)
        new_arc = new_arc[:start] + cleaned + new_arc[end:]

    unresolved_names = {n for n, _ in unresolved}
    for local_name in to_confirm:
        if local_name in unresolved_names:
            continue
        start, end, block = block_of(new_arc, local_name)
        new_block = block.replace(
            "backlog:hasArchivalConfirmationStatus backlog:AC_PendingConfirmation",
            "backlog:hasArchivalConfirmationStatus backlog:AC_Confirmed")
        new_arc = new_arc[:start] + new_block + new_arc[end:]

    with open(archive_path, "w") as f:
        f.write(new_arc)
    promoted = [n for n in to_confirm if n not in unresolved_names]
    print(f"VERDICT: APPLIED -- {len(to_pend)} set pending, {len(promoted)} confirmed, "
          f"{len(unresolved)} stayed pending with real violations disclosed above")


if __name__ == "__main__":
    main()
