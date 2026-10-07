#!/usr/bin/env python3
"""backlog_archive_reconcile v3.0.0 -- per-lineage archival confirmation, judged by the archive's own shapes (Lineage 19, DC-S03 and DC-S05).

WHAT IT DOES. For every LineageArchiveEntry in the live data file whose archive copy sits in the archive folder:
  - the archive copy says lineageArchived false, or has no confirmation status -> it is marked archived (lineageArchived true) and set pending;
  - pending -> it is judged by the ARCHIVE's own shapes (01-ontologies/archive/backlog_archive_shacl_v*.ttl), and promoted to confirmed only when none of
    the lineage's own subjects (its items, its Lineage, its Mission and the reports that close it) carries a violation; otherwise it stays pending and the
    violations are listed;
  - confirmed -> left alone, never judged again.
Dry run unless --apply. With --apply the archive data file gets a new minor version, the old file is removed, and the live data file's archiveFile
pointers follow the new name (the live data file's own version is bumped by the release step, not here).

WHAT CHANGED FROM v2.2.0, AND WHY. v2.2.0 judged an archive by the LIVE shapes in a full-context run (about five minutes), found its folders by replacing a
folder name inside a path, and was written for the layout before the archive folder, so it could not be run at all. v3.0.0 takes no path argument: the
register is the highest live data file, the archive is the highest data file in 01-ontologies/archive/, the judge is the shapes file beside it, and
nothing derives a folder by substitution. The live rules never read the archive (G89, G91).

Exit 0 reconcilable or applied, 2 violations keep some lineage pending, 3 the tool could not do its job.
Usage: backlog_archive_reconcile_v3_0_0.py [--apply]
"""
import glob, importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
ONT = os.path.join(PKG, "01-ontologies"); ARC = os.path.join(ONT, "archive")


def latest(directory, pat):
    hits = glob.glob(os.path.join(directory, pat))
    if not hits:
        raise SystemExit("GATE ABORT: no %s in %s" % (pat, os.path.relpath(directory, PKG)))
    return sorted(hits, key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]])[-1]


def block_of(text, local_name):
    m = re.search(rf'fw:{re.escape(local_name)}\s+a\s+backlog:Lineage\b', text)
    if not m:
        return None, None, None
    start = m.start()
    nxt = re.search(r'\nfw:\w+ ', text[start + 1:])
    end = start + 1 + nxt.start() if nxt else len(text)
    return start, end, text[start:end]


def judge_lineages(arc_path, shapes_path, names):
    """{lineage local name: [violation messages on that lineage's own subjects]} under the archive's own shapes."""
    import rdflib, pyshacl
    B = rdflib.Namespace("http://example.org/backlog#"); SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")
    a = rdflib.Graph().parse(arc_path); shg = rdflib.Graph().parse(shapes_path)
    own = {}
    for L in a.subjects(rdflib.RDF.type, B.Lineage):
        n = str(L).split("#")[-1]
        if n not in names:
            continue
        subj = {L} | set(a.subjects(B.belongsToLineage, L))
        m = a.value(L, B.lineageForMission)
        if m is not None:
            subj.add(m); subj |= set(a.subjects(B.closesForMission, m))
        own[n] = subj
    _, rg, _ = pyshacl.validate(a, shacl_graph=shg, inference="none", advanced=True, allow_warnings=True)
    out = {n: [] for n in own}
    for r in rg.subjects(rdflib.RDF.type, SH.ValidationResult):
        if rg.value(r, SH.resultSeverity) != SH.Violation:
            continue
        fn = rg.value(r, SH.focusNode)
        for n, subj in own.items():
            if fn in subj:
                out[n].append("%s: %s" % (str(fn).split("#")[-1], rg.value(r, SH.resultMessage)))
    return out


def main():
    apply = "--apply" in sys.argv[1:]
    reg_path = latest(ONT, "backlog_abox_v*.ttl"); arc_path = latest(ARC, "backlog_framework_archive_abox_v*.ttl"); shapes_path = latest(ARC, "backlog_archive_shacl_v*.ttl")
    reg = open(reg_path, encoding="utf-8").read(); arc = open(arc_path, encoding="utf-8").read()
    arc_rel = os.path.relpath(arc_path, PKG)
    print("register: %s\narchive : %s\nshapes  : %s" % (os.path.basename(reg_path), os.path.basename(arc_path), os.path.basename(shapes_path)))
    entries = re.findall(r'backlog:entryForLineage\s+"[^"]*#(\w+)"\s*;.*?backlog:archiveFile\s+"([^"]+)"', reg, re.DOTALL)
    to_pend, to_confirm, confirmed = [], [], []
    for name, f in entries:
        if os.path.basename(f) != os.path.basename(arc_path):
            continue
        s, e, blk = block_of(arc, name)
        if blk is None:
            print("  SKIP %s: not a Lineage individual in this archive file" % name); continue
        if "backlog:lineageArchived false" in blk or "backlog:hasArchivalConfirmationStatus" not in blk:
            to_pend.append(name)
        elif "AC_Confirmed" in blk:
            confirmed.append(name)
        else:
            to_confirm.append(name)
    print("entries: %d; confirmed and left alone: %d; to mark archived and set pending: %d %s; pending, to judge: %d %s"
          % (len(entries), len(confirmed), len(to_pend), to_pend, len(to_confirm), to_confirm))
    if not to_pend and not to_confirm:
        print("VERDICT : nothing to reconcile"); return 0
    unresolved = {}
    if to_confirm:
        verdicts = judge_lineages(arc_path, shapes_path, set(to_confirm))
        unresolved = {n: v for n, v in verdicts.items() if v}
        for n, v in unresolved.items():
            for m in v:
                print("    stays pending, %s" % m)
    if not apply:
        print("VERDICT : RECONCILABLE -- re-run with --apply to write it"); return 0
    new = arc
    for name in to_pend:
        s, e, blk = block_of(new, name)
        nb = re.sub(r'backlog:lineageArchived\s+false', 'backlog:lineageArchived true', blk, count=1)
        if "hasArchivalConfirmationStatus" not in nb:
            nb, n = re.subn(r'(fw:%s\s+a\s+backlog:Lineage\s*;)' % re.escape(name), r'\1 backlog:hasArchivalConfirmationStatus backlog:AC_PendingConfirmation ;', nb, count=1)
            if n != 1:
                print("GATE ABORT: could not set pending for %s" % name); return 3
        if "backlog:lineageArchived true" not in nb:
            nb = re.sub(r'(fw:%s\s+a\s+backlog:Lineage\s*;)' % re.escape(name), r'\1 backlog:lineageArchived true ;', nb, count=1)
        new = new[:s] + nb + new[e:]
    promoted = [n for n in to_confirm if n not in unresolved]
    for name in promoted:
        s, e, blk = block_of(new, name)
        new = new[:s] + blk.replace("AC_PendingConfirmation", "AC_Confirmed") + new[e:]
    if new == arc:
        print("VERDICT : nothing written"); return 2 if unresolved else 0
    M, m_, p = [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", arc_path)[0]]
    newv = "%d.%d.0" % (M, m_ + 1); oldv = "%d.%d.%d" % (M, m_, p)
    new = new.replace('owl:versionInfo "%s" ;' % oldv, 'owl:versionInfo "%s" ;' % newv, 1)
    new = re.sub(r"(owl:versionIRI <[^>]*/)" + re.escape(oldv) + ">", lambda mm: mm.group(1) + newv + ">", new, count=1)
    new = re.sub(r"owl:priorVersion (<[^>]*/)", lambda mm: "owl:priorVersion " + mm.group(1)[:-1] + oldv + "> , " + mm.group(1), new, count=1)  # the version this one supersedes joins the chain
    new_path = os.path.join(ARC, "backlog_framework_archive_abox_v%d_%d_0.ttl" % (M, m_ + 1))
    open(new_path, "w", encoding="utf-8").write(new); os.remove(arc_path)
    reg2 = reg.replace('backlog:archiveFile "%s"' % arc_rel, 'backlog:archiveFile "%s"' % os.path.relpath(new_path, PKG))
    open(reg_path, "w", encoding="utf-8").write(reg2)
    print("VERDICT : APPLIED -- %d marked archived and set pending, %d confirmed, %d stayed pending; archive now %s, %d live pointer(s) follow it"
          % (len(to_pend), len(promoted), len(unresolved), os.path.basename(new_path), reg.count('backlog:archiveFile "%s"' % arc_rel)))
    return 2 if unresolved else 0


if __name__ == "__main__":
    sys.exit(main())
