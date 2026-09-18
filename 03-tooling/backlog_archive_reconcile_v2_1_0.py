#!/usr/bin/env python3
"""backlog_archive_reconcile v2.1.0 -- per-lineage archival confirmation, deferred by one cycle.

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


def run_conformance_full(archive_path, register_path):
    """Computes the REAL, complete violation set directly -- not the archive-conformance tool's
    own console output, which prints only the first 8 of what can be dozens of real violations
    (viol[:8] in that tool). A promotion decision this permanent cannot be made from a truncated
    sample; every real focus node with a real violation must be seen, not just whichever eight
    happened to print first. Replicates that tool's own, now-fixed (v1.2.0) graph construction --
    shapes+rules combined, widened focus including each item's own harness and evidence chain --
    rather than shelling out to it and re-parsing a sample."""
    tool_dir = os.path.dirname(os.path.abspath(archive_path)).replace("01-ontologies", "03-tooling")
    shapes_dir = os.path.dirname(os.path.abspath(archive_path)).replace("01-ontologies", "02-shacl-safeguards")
    def latest(pat, d=tool_dir):
        c = sorted(f for f in os.listdir(d) if re.match(pat, f))
        return os.path.join(d, c[-1]) if c else None
    onto_dir = os.path.dirname(os.path.abspath(archive_path))
    sh_f = latest(r"backlog_shacl_v.*\.ttl$", shapes_dir)
    ru_f = latest(r"backlog_rules_v.*\.ttl$", shapes_dir)
    tb_f = latest(r"backlog_tbox_v.*\.ttl$", onto_dir)
    ab_f = latest(r"backlog_abox_v.*\.ttl$", onto_dir)
    if not all([sh_f, ru_f, tb_f, ab_f]):
        return None

    import rdflib
    import pyshacl
    B = rdflib.Namespace("http://example.org/backlog#")
    SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")
    g, a = rdflib.Graph().parse(register_path), rdflib.Graph().parse(archive_path)
    tb, ab = rdflib.Graph().parse(tb_f), rdflib.Graph().parse(ab_f)
    shg = rdflib.Graph().parse(sh_f); shg.parse(ru_f)
    arrivals = list(a.subjects(rdflib.RDF.type, B.Lineage))
    focus = set()
    for L in arrivals:
        items = {s for s in a.subjects(B.belongsToLineage, L)}
        focus |= items | {L}
        m = a.value(L, B.lineageForMission)
        if m is not None:
            focus.add(m)
        for item in items:
            for h in a.subjects(B.harnessFor, item):
                focus.add(h)
                for ev in a.objects(h, B.hasHarnessEvidence):
                    focus.add(ev)
            for ev in a.objects(item, B.hasEvidence):
                focus.add(ev)
    _, rg, _ = pyshacl.validate(a + g + tb + ab, shacl_graph=shg, advanced=True, inference="none",
                                 focus_nodes=[str(f) for f in focus])
    by_lineage = {}
    for L in arrivals:
        items = {s for s in a.subjects(B.belongsToLineage, L)} | {L}
        by_lineage[str(L).split("#")[-1]] = items
    result = {}
    for r in rg.subjects(rdflib.RDF.type, SH.ValidationResult):
        if rg.value(r, SH.resultSeverity) != SH.Violation:
            continue
        fn = rg.value(r, SH.focusNode)
        msg = str(rg.value(r, SH.resultMessage))
        for lname, items in by_lineage.items():
            if fn in items:
                result.setdefault(lname, []).append(f"{str(fn).split('#')[-1]}: {msg}")
    return result


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

    conformance_map = None
    if to_confirm:
        conformance_map = run_conformance_full(archive_path, register_path)
        if conformance_map is None:
            print("  GATE ABORT: could not compute real conformance for promotion")
            sys.exit(3)
        for name in to_confirm:
            hits = conformance_map.get(name, [])
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
