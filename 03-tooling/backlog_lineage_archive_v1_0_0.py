#!/usr/bin/env python3
"""backlog_lineage_archive v1.0.0 — set an achieved lineage down, out of every processing path.

WHY. A lineage whose mission is settled keeps costing every run until it is ARCHIVED: the SHACL
suite validates its every individual, the git witness re-measures its every subject, the roadmap
report ranks its items. Six early lineages were set down by hand into
backlog_framework_archive_abox (807 individuals, "the work was finished"); lineages 7 and 8
stayed live for a week after they were achieved because nothing archived them. The owner's rule,
2026-09-09: an archived lineage is not a subject of processing unless consciously revived, and an
ACHIEVED lineage found un-archived triggers the archival activity.

WHAT IT DOES.  backlog_lineage_archive.py <register.ttl> <LineageLocalName>... [--apply]
  1. Checks the lineage is archivable: hasMissionOutcome Out_Achieved on its mission; a
     ClosureReport closes that mission; no work item of the lineage is InProgress; not frozen.
     (Whether its chain reads ORDERED is the order check's verdict and is required by the gate,
     not repeated here.)
  2. Computes the ARCHIVAL PARTITION: every subject that belongsToLineage the lineage, plus --
     iterated to a fixed point -- every subject that belongs to no live lineage and references a
     subject already in the partition (closure reports, change requests, events about the
     lineage's items). Measured on lineages 7+8: 411 direct members, 493 after closure.
  3. Reports what stays live and still points into the partition (a pointer into a named archive
     is a reference, not a dangling edge -- the archive ABox says so itself).
  4. With --apply: writes the partition's triples into a NEW archive ABox version, removes them
     from a NEW register version, and leaves on the Lineage individual: lineageArchived true,
     archiveFile <path>, archivedAt, archivalTrigger. The Lineage, its Mission and its ClosureReport
     STAY in the live register as the record that points into the archive (as lineages 1-6 do).
     Nothing is deleted; it moves, and the archive ABox is loaded by the lineage-history checks.
  Revival is the inverse (--revive), an owner act recorded as lineageRevivedAt.

Exit 0 archivable / applied; 2 not archivable (reasons printed); 1 error.
"""
import glob, os, re, sys, time
from rdflib import Graph, Namespace, RDF, RDFS, Literal, URIRef, XSD

B = Namespace("http://example.org/backlog#")
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
ITEM_TYPES = ["Story", "Epic", "ExecutionTask", "Initiative", "Spike", "Task", "Defect", "Feature", "Enabler"]
def local(x): return str(x).split("#")[-1]
def prefix_of(g, x):
    ns = str(x).rsplit("#", 1)[0] + "#"
    return next((p + ":" for p, n in g.namespaces() if str(n) == ns), "fw:")
def semver(p):
    m = re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)
    return [int(x) for x in m[0]] if m else [0, 0, 0]
def bump(path, minor=True):
    M, m, p = semver(path)
    if (M, m, p) == (0, 0, 0):
        return re.sub(r"\.ttl$", "_v0_1_0.ttl", path)   # an unversioned working copy
    tok = f"_v{M}_{m+1}_0" if minor else f"_v{M}_{m}_{p+1}"
    return re.sub(r"_v\d+_\d+_\d+\.", tok + ".", path)

def archivable(g, L):
    reasons = []
    m = g.value(L, B.lineageForMission)
    if m is None: reasons.append("no lineageForMission")
    else:
        if g.value(m, B.hasMissionOutcome) != B.Out_Achieved: reasons.append(f"mission {local(m)} is not Out_Achieved")
        if not any(True for cr in g.subjects(B.closesForMission, m)): reasons.append(f"no ClosureReport closes {local(m)}")
    a = g.value(L, B.lineageArchived)
    if a is not None and bool(a.toPython()): reasons.append("already archived")
    f = g.value(L, B.lineageFrozen)
    if f is not None and bool(f.toPython()):
        # the CURRENT freeze (as the order check reads it): a thrash without a ruling, or a bypass no restart answers
        restarts = list(g.subjects(B.restartsLineage, L))
        for fb in g.objects(L, B.frozenBy):
            if (fb, RDF.type, B.LineageThrash) in g and g.value(L, B.frozenRuling) is None: reasons.append(f"frozen by thrash {local(fb)} without a ruling")
            if (fb, RDF.type, B.LineageBypass) in g and not any((r, B.answersBypass, fb) in g for r in restarts): reasons.append(f"frozen by bypass {local(fb)} with no answering restart")
    for i in g.subjects(B.belongsToLineage, L):
        if g.value(i, B.hasState) == B.InProgress: reasons.append(f"{local(i)} is InProgress")
    return reasons

def partition(g, lineages):
    live_lin = {l for l in g.subjects(RDF.type, B.Lineage) if l not in lineages
                and not (g.value(l, B.lineageArchived) is not None and bool(g.value(l, B.lineageArchived).toPython()))}
    live_subj = {s for l in live_lin for s in g.subjects(B.belongsToLineage, l)}
    part = {s for l in lineages for s in g.subjects(B.belongsToLineage, l)}
    # the Lineage and its Mission stay live as the pointer into the archive; the ClosureReport goes
    # WITH the work it reports on (its objectives are in the partition; a report kept live would
    # then report on nothing -- measured, 14 violations, on the first application)
    keep_live = set(lineages) | {g.value(l, B.lineageForMission) for l in lineages}
    part -= keep_live
    changed, rounds = True, 0
    while changed and rounds < 20:
        changed = False; rounds += 1
        for s in set(g.subjects()):
            if not isinstance(s, URIRef) or s in part or s in live_subj or s in keep_live: continue
            if (s, RDF.type, B.Lineage) in g or (s, RDF.type, B.Mission) in g: continue
            if any(o in part for o in g.objects(s, None) if isinstance(o, URIRef)):
                part.add(s); changed = True
    # reverse closure: a subject in no live lineage whose EVERY incoming reference comes from the
    # partition (a domain entity only the archived epics cover, an increment only archived items fill)
    # goes with them; kept live it would be an entity nothing covers, an increment with no member
    changed = True
    while changed:
        changed = False
        for s in set(g.subjects()):
            if not isinstance(s, URIRef) or s in part or s in live_subj or s in keep_live: continue
            if (s, RDF.type, B.Lineage) in g or (s, RDF.type, B.Mission) in g: continue
            incoming = [x for x in g.subjects(None, s) if isinstance(x, URIRef) and x != s]
            if incoming and all(x in part for x in incoming):
                part.add(s); changed = True
    # cluster closure: subjects in no live lineage that hang together with the partition and touch
    # nothing live (an entity and the gaps that name it, both referenced only by archived items)
    cand = {s for s in set(g.subjects()) if isinstance(s, URIRef) and s not in part and s not in live_subj and s not in keep_live
            and (s, RDF.type, B.Lineage) not in g and (s, RDF.type, B.Mission) not in g}
    changed = True
    while changed:
        changed = False
        for s in list(cand):
            inc = [x for x in g.subjects(None, s) if isinstance(x, URIRef) and x != s]
            out = [o for o in g.objects(s, None) if isinstance(o, URIRef) and o != s and not str(o).startswith("http://example.org/backlog#")]
            touches = any(x in part for x in inc) or any(o in part for o in out)
            if touches and all(x in part or x in cand for x in inc) and all(o in part or o in cand for o in out):
                part.add(s); cand.discard(s); changed = True
    return part, keep_live

def main():
    argv = sys.argv[1:]
    apply = "--apply" in argv; names = [a for a in argv if not a.startswith("--")]
    if len(names) < 2: print(__doc__); return 1
    reg = names[0]; g = Graph().parse(reg, format="turtle")
    lineages = []
    for n in names[1:]:
        L = next((l for l in g.subjects(RDF.type, B.Lineage) if local(l) == n), None)
        if L is None: print(f"ERROR: no Lineage named {n}"); return 1
        lineages.append(L)
    bad = False
    for L in lineages:
        r = archivable(g, L)
        print(f"  {local(L):22} {'ARCHIVABLE' if not r else 'NOT archivable: ' + '; '.join(r)}")
        bad = bad or bool(r)
    if bad: return 2
    part, keep_live = partition(g, set(lineages))
    live_refs = [(s, p, o) for s, p, o in g if o in part and s not in part and isinstance(o, URIRef)]
    print(f"  partition   : {len(part)} subjects set down; {len(keep_live)} stay live as the record (lineage and mission)")
    print(f"  live pointers into the archive after the move: {len(live_refs)} (references, not dangling edges)")
    if not apply:
        print("VERDICT     : ARCHIVABLE — re-run with --apply to move the partition into the archive ABox"); return 0
    arch_path = sorted(glob.glob(os.path.join(PKG, "01-ontologies", "backlog_framework_archive_abox_v*.ttl")), key=semver)[-1]
    new_arch = bump(arch_path); new_reg = bump(reg)
    # TEXT-LEVEL MOVE. The register is a record: its dated comment blocks ARE the history (L-112), and
    # an rdflib re-serialization would drop every one of them. Statements are moved verbatim: a
    # statement starts at a column-0 line whose first token is the subject and runs to the line that
    # ends with " ." ; every statement whose subject is in the partition moves, comments stay.
    lines = open(reg).read().split("\n")
    names = {local(s) for s in part}
    prefixes = {}
    for ln in lines:
        m = re.match(r"@prefix\s+(\w+):\s+<([^>]+)>", ln)
        if m: prefixes[m.group(1)] = m.group(2)
    def subj_of(line):
        m = re.match(r"([A-Za-z_]\w*):([A-Za-z_][\w\-]*)\s", line)
        if not m: return None
        pfx, ln_ = m.groups(); ns = prefixes.get(pfx)
        return ln_ if ns else None
    out_live, out_arch = [], []; i = 0; moved = 0
    while i < len(lines):
        ln = lines[i]
        sub = subj_of(ln) if ln and not ln.startswith((" ", "\t", "#", "@")) else None
        if sub is not None and sub in names:
            j = i
            while j < len(lines) and not lines[j].rstrip().endswith(" ."): j += 1
            out_arch.extend(lines[i:j + 1]); moved += 1; i = j + 1
        else:
            out_live.append(ln); i += 1
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    oldv = ".".join(map(str, semver(reg))); newv = ".".join(map(str, semver(new_reg)))
    live_txt = "\n".join(out_live)
    live_txt = live_txt.replace(f'owl:versionInfo "{oldv}" ;', f'owl:versionInfo "{newv}" ;', 1)
    live_txt = re.sub(r"(owl:versionIRI <[^>]*/)" + re.escape(oldv) + ">", lambda m: m.group(1) + newv + ">", live_txt, count=1)
    rel = os.path.relpath(new_arch, PKG)
    live_txt = live_txt.rstrip("\n") + f"\n\n#################################################################\n#  {now} -- ARCHIVAL by backlog_lineage_archive_v1_0_0: {len(part)} subjects of\n#  {', '.join(local(L) for L in lineages)} set down into {rel}; the lineage,\n#  its mission and its closure report stay here as the record that points in.\n#################################################################\n"
    for L in lineages:
        # lineageArchived is a functional current-state pointer: the existing 'false' on this lineage's own
        # statement is moved in place (L-112 pointer rule); the dated block below is the history
        pat = re.compile(r"(^" + re.escape(prefix_of(g, L) + local(L)) + r" a backlog:Lineage\b[^\n]*(?:\n[ \t][^\n]*)*?)backlog:lineageArchived false", re.M)
        live_txt, n = pat.subn(lambda m: m.group(1) + "backlog:lineageArchived true", live_txt, count=1)
        live_txt += f'{prefix_of(g, L)}{local(L)}' + (' backlog:lineageArchived true ;' if n == 0 else '') + f' backlog:archiveFile "{rel}" ;\n    backlog:archivedAt "{now}"^^xsd:dateTime ; backlog:hasLineageStatus backlog:LS_Archived ;\n    backlog:archivalTrigger "Found achieved and un-archived by backlog_lineage_archive_v1_0_0: mission Out_Achieved, closure report present, no item InProgress, not frozen. Owner\'s rule 2026-09-09: an achieved lineage found triggers the archival activity." .\n'
    arch_txt = open(arch_path).read().rstrip("\n")
    olda = ".".join(map(str, semver(arch_path))); newa = ".".join(map(str, semver(new_arch)))
    arch_txt = arch_txt.replace(f'owl:versionInfo "{olda}" ;', f'owl:versionInfo "{newa}" ;', 1)
    arch_txt = re.sub(r"(owl:versionIRI <[^>]*/)" + re.escape(olda) + ">", lambda m: m.group(1) + newa + ">", arch_txt, count=1)
    # prefixes the moved statements need
    need = {m.group(1) for ln in out_arch for m in re.finditer(r"\b([A-Za-z_]\w*):[A-Za-z_]", ln)}
    have = set(re.findall(r"@prefix\s+(\w+):", arch_txt))
    extra = "".join(f"@prefix {pfx}: <{prefixes[pfx]}> .\n" for pfx in sorted(need & set(prefixes)) if pfx not in have)
    arch_txt = extra + arch_txt + f"\n\n#################################################################\n#  {now} -- {moved} statements of {', '.join(local(L) for L in lineages)} set down here by\n#  backlog_lineage_archive_v1_0_0 (verbatim, comments of the live register kept there).\n#################################################################\n" + "\n".join(out_arch) + "\n"
    open(new_reg, "w").write(live_txt); open(new_arch, "w").write(arch_txt)
    print(f"  written     : {os.path.basename(new_reg)} ({moved} statements moved out, comments kept) and {os.path.basename(new_arch)}")
    print("VERDICT     : APPLIED — the old versions are retired by the release that ships these")
    return 0

if __name__ == "__main__":
    sys.exit(main())
