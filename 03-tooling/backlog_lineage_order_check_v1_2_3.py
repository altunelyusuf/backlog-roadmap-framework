#!/usr/bin/env python3
"""backlog_lineage_order_check v1.2.3 — did the chain come before the work, or after?

THE ESCAPE THIS CATCHES. A lineage is Mission -> Scope -> Goal -> Objective -> Backlog,
one commit per stage, and only then work items (LINEAGE_OPERATING_DISCIPLINE, ceremony
step 2). Observed in a parallel session and then measured in this package's own register:
the work is built first and the chain is written afterwards to fit it. Every stage digest
reproduces (G18 experiment C -- a digest computed from the finished graph proves nothing
about order), every shape passes, and the lineage is a story told backwards.

THE WITNESS. The register's own dates are the author's. The one anchor the author does not
control is the governed repository: the commit at which a subject FIRST APPEARS under the
register path (`git log --reverse -S<local name> -- 01-ontologies`). This tool measures,
for every non-archived lineage that has stage outputs:

  ORDERED      every stage output first appears in pipeline order, each strictly before
               the next, and every work item first appears at or after Stage_Backlog's
               output.
  UNWITNESSED  the outputs and the items all first appear in ONE commit. Git orders
               between commits and says nothing within one (G18); this is exactly what
               G77 disclosed for lineage 8. Reported, not a bypass -- it cannot be told
               from an honest single-commit build. Advisory.
  RESTARTED    a LineageRestart exists and no active (non-retracted) output yet: the
               chain is being rebuilt from Mission. Disclosed, exit 0.
  v1.1.1: a thrash already recorded as a LineageThrash is settled and not re-raised;
               a frozen lineage with a frozenRuling is measured normally again.
  PLANNED_LATE (per item) a PlanningEvent first appears after the item it plans: the
               work existed, then the planning record was written to fit it. v1.2.0, on the
               owner's decision: a late-planned item IS a bypassed item -- the escape one
               level down -- and is named in the bypass finding like any other.
  FOUND        (v1.2.0) a bypass is recorded and the lineage is frozen by it, and no
               restart answers it yet: the state between the finding's commit and the
               restart's. Exit 0 -- the restart must come in its own commit.
  Strategies (v1.2.0): a restart's hasRecoveryStrategy selects extra git checks --
               Strat_TransformSimplify: its ScopeChange first appears before the restart;
               Strat_TransformReduce: its templateLineage reads ORDERED;
               Strat_DivideAndConquer: the parent is ORDERED only when every part is and
               its combine output is active. --emit also prints, for the NEXT restart, the
               reductionObserved of the last trial (admitted / named), never hand-written.
  BYPASS       at least one work item first appears BEFORE the lineage's Stage_Backlog
               output does (or that output is absent), or the outputs appear out of
               pipeline order. The chain was closed after the work.

WHAT IT DOES WITH A BYPASS. Prints it, exits 2, and with --emit writes the finding as
Turtle (`backlog:LineageBypass`, TBox v1.83.0) for the owner to append to the register.
It never appends anything itself and never decides what follows: the shapes do
(BypassRequiresRestartShape -- a bypass on a live lineage obliges a LineageRestart).

WHAT IT DOES AFTER A RESTART. Outputs marked outputRetracted are ignored; the rebuilt
outputs must first appear AFTER the restart itself does; items flagged preLineageItem
are the restart's business (admitted or not, the shapes decide) and are not measured
again -- they are older than the rebuilt chain by definition.

FIXTURE PATH. --witness <json> replaces git with a {local_name: [commit, epoch]} map so a
fixture with a known answer can exercise all three verdicts (G7) without a repository.
Both modes run the identical classification code.

v1.1.0 -- THE LOOP'S STOP CONDITION, by convergence, never by count (TBox v1.84.0).
A restart answers a bypass; nothing in v1.0.0 stopped bypass -> restart -> bypass forever,
and every turn can lose work. Three measurements, from the trials themselves:
  DELIBERATION  (git) the restart first appears strictly after the bypass it answers, and
                the rebuilt Stage_Mission output strictly after the restart. Same commit =
                no separate act of deciding was witnessed -> THRASH (Thrash_NotDeliberated).
  NOVELTY       (register) a later bypass on a restarted lineage names at least one item no
                earlier bypass on that lineage named. If not -> THRASH (Thrash_NoNovelty).
  ADMISSION     (register) an item admitted by an earlier rebuild is named again by a later
                bypass -> THRASH (Thrash_AdmissionLost). (Retraction without re-admission is
                RestartKeepsAdmissionsShape's business.)
A thrash is printed, exit 2, and with --emit written as a backlog:LineageThrash for the
owner to append; the shapes then require the lineage frozen until the owner rules.
A frozen lineage (lineageFrozen true, no frozenRuling) is reported FROZEN and not measured
further -- it is waiting, not failing.

Exit: 0 ORDERED/UNWITNESSED/RESTARTED/FROZEN; 2 BYPASS unanswered or THRASH unrecorded; 1 on error.
"""
import glob, json, os, re, subprocess, sys, time
from rdflib import Graph, Namespace, RDF, URIRef

B = Namespace("http://example.org/backlog#")
ORDER = ["Stage_Mission", "Stage_Scope", "Stage_Goal", "Stage_Objective", "Stage_Backlog"]
ITEM_TYPES = ["Story", "Epic", "ExecutionTask", "Initiative", "Spike", "Task", "Defect", "Feature", "Enabler"]
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
TOOL = os.path.basename(__file__).replace(".py", "")


def local(x):
    return str(x).split("#")[-1]


class GitWitness:
    """First-appearance commit of a subject under the register path, via git log -S."""
    def __init__(self, repo_root, rel_path):
        self.root, self.rel = repo_root, rel_path
        self.cache = {}

    def first(self, local_name, prefix):
        key = prefix + local_name
        if key in self.cache:
            return self.cache[key]
        r = subprocess.run(["git", "log", "--reverse", "--format=%h %ct", "-S", key + " ", "--", self.rel],
                           cwd=self.root, capture_output=True, text=True)
        line = r.stdout.strip().split("\n")[0] if r.stdout.strip() else ""
        val = (line.split()[0], int(line.split()[1])) if line else None
        self.cache[key] = val
        return val


class MapWitness:
    def __init__(self, path):
        self.m = json.load(open(path))

    def first(self, local_name, prefix):
        v = self.m.get(local_name)
        return (v[0], int(v[1])) if v else None


def prefix_for(g, L):
    ns_of = str(L).rsplit("#", 1)[0] + "#" if "#" in str(L) else None
    return next((p + ":" for p, ns in g.namespaces() if ns_of and str(ns) == ns_of), "fw:")


def classify(g, L, witness, prefix):
    """Returns (verdict, detail dict) for one lineage. v1.2.1: the prefix used for git
    lookups is the LINEAGE'S own (several registers may be loaded in one graph)."""
    prefix = prefix_for(g, L)
    outs = {}
    for o in g.subjects(B.belongsToLineage, L):
        if (o, RDF.type, B.StageOutput) not in g:
            continue
        if g.value(o, B.outputRetracted) is not None and bool(g.value(o, B.outputRetracted).toPython()):
            continue
        st = local(g.value(o, B.outputOfStage))
        outs.setdefault(st, []).append(o)
    items = [i for i in g.subjects(B.belongsToLineage, L)
             if any((i, RDF.type, URIRef(B + t)) in g for t in ITEM_TYPES)]
    restarts = list(g.subjects(B.restartsLineage, L))
    restart_at = None
    if restarts:
        rc = g.value(restarts[-1], B.restartedAtCommit)
        restart_at = witness.first(local(restarts[-1]), prefix) if rc else None

    out_first = {}
    for st in ORDER:
        for o in outs.get(st, []):
            f = witness.first(local(o), prefix)
            if f and (st not in out_first or f[1] < out_first[st][1]):
                out_first[st] = f
    item_first = {}
    for i in items:
        f = witness.first(local(i), prefix)
        if f:
            item_first[local(i)] = f

    problems = []
    # 1. stage order between outputs
    prev = None
    for st in ORDER:
        if st in out_first:
            if prev and out_first[st][1] < out_first[prev][1]:
                problems.append(f"{st} output first appears ({out_first[st][0]}) before {prev}'s ({out_first[prev][0]})")
            prev = st
    # 2. rebuilt outputs must post-date the restart
    if restart_at:
        for st, f in out_first.items():
            if f[1] < restart_at[1]:
                problems.append(f"{st} output ({f[0]}) predates the restart ({restart_at[0]}) and is not retracted")
    # 3. items vs Stage_Backlog output
    backlog_first = out_first.get("Stage_Backlog")
    bypassed = []
    for i in items:
        ln = local(i)
        if ln not in item_first:
            continue
        pre = g.value(i, B.preLineageItem)
        if pre is not None and bool(pre.toPython()):
            # owned by a restart: older than the rebuilt chain by definition. Admission
            # (or its absence) is the shapes' business, not a second bypass finding.
            continue
        anchor = backlog_first
        if anchor is None:
            bypassed.append((ln, item_first[ln], "absent"))
        elif item_first[ln][1] < anchor[1]:
            bypassed.append((ln, item_first[ln], anchor[0]))
    # 3b. item-level: an item planned after it already existed (PlanningEvent first
    #     appears AFTER the item it plans). The same escape one level down: the work
    #     is done, then the planning record is written to fit it. Reported as
    #     PLANNED_LATE per item; it does not by itself make the lineage BYPASS in
    #     v1.0.0 -- disclosed on every run, promotion to a gate failure is an owner
    #     decision once the measurement has been read on a real register.
    planned_late = []
    for i in items:
        ln = local(i)
        if ln not in item_first:
            continue
        for pe in g.subjects(B.plansItem, i):
            pf = witness.first(local(pe), prefix)
            if pf and pf[1] > item_first[ln][1]:
                planned_late.append((ln, item_first[ln], local(pe), pf))
    # 3c. deliberation (v1.1.0): restart after its bypass, rebuilt Mission after restart
    thrash = []   # (kind, bypass, restart, lost_items, detail)
    for r in restarts:
        rf = witness.first(local(r), prefix)
        for b in g.objects(r, B.answersBypass):
            bf = witness.first(local(b), prefix)
            if rf and bf and rf[1] <= bf[1]:
                thrash.append(("Thrash_NotDeliberated", b, r, [], f"restart {local(r)} first {rf[0]} not after its bypass {local(b)} first {bf[0]}"))
        mf = out_first.get("Stage_Mission")
        if rf and mf and mf[1] <= rf[1]:
            for b in g.objects(r, B.answersBypass):
                thrash.append(("Thrash_NotDeliberated", b, r, [], f"rebuilt Stage_Mission output first {mf[0]} not after restart {local(r)} first {rf[0]}"))
    # 3d. novelty + admission across successive bypasses (v1.1.0)
    all_b = [b for b in g.subjects(B.bypassedLineage, L)]
    def when(b):
        v = g.value(b, B.detectedAt); return str(v) if v is not None else ""
    all_b.sort(key=when)
    seen = set()
    for idx, b in enumerate(all_b):
        names = {local(i) for i in g.objects(b, B.bypassedItem)}
        answered = [r for r in restarts if (r, B.answersBypass, b) in g]
        if idx > 0:
            prior_r = [r for r in restarts if any((r, B.answersBypass, pb) in g for pb in all_b[:idx])]
            if names and not (names - seen):
                thrash.append(("Thrash_NoNovelty", b, prior_r[-1] if prior_r else None, [],
                               f"bypass {local(b)} names {sorted(names)} -- all named by earlier bypasses"))
            # admitted by the chain that existed when this bypass was measured (its own
            # bypassedOutput set) and named again: work an earlier rebuild had taken in
            pre_chain = set(g.objects(b, B.bypassedOutput))
            lost = sorted({local(i) for i in g.objects(b, B.bypassedItem)
                           if g.value(i, B.admittedByOutput) in pre_chain})
            if lost:
                thrash.append(("Thrash_AdmissionLost", b, prior_r[-1] if prior_r else None, lost,
                               f"bypass {local(b)} names admitted items {sorted(lost)}"))
        seen |= names
    # 3e. v1.1.1: a thrash already RECORDED as a LineageThrash (same lineage, kind and
    #     repeated bypass) is a settled finding, not a new one. Once the owner has ruled
    #     (frozenRuling), the register carries the whole story -- finding, freeze, ruling
    #     -- and raising it again on every run would be the duplicate-screen failure
    #     (L-71) applied by a tool. Unrecorded thrash is still raised.
    def recorded(kind, b):
        return any((t, B.hasThrashKind, URIRef(B + kind)) in g and (t, B.repeatedBypass, b) in g
                   for t in g.subjects(B.thrashedLineage, L))
    thrash = [t for t in thrash if not recorded(t[0], t[1])]
    # 3f. v1.2.0: late planning is a bypass of the item (owner's decision, G83)
    for ln, f, pe, pf in planned_late:
        if not any(x[0] == ln for x in bypassed):
            i = next(x for x in items if local(x) == ln)
            pre = g.value(i, B.preLineageItem)
            if pre is not None and bool(pre.toPython()):
                continue
            bypassed.append((ln, f, f"planned-late by {pe} ({pf[0]})"))
    # 3f2. v1.2.2: postRestartItem is verified, not trusted -- the item must first appear after its restart
    for i in items:
        r = g.value(i, B.postRestartItem)
        if r is not None:
            rf = witness.first(local(r), prefix); f = item_first.get(local(i))
            if rf and f and f[1] <= rf[1]:
                problems.append(f"{local(i)} claims postRestartItem {local(r)} but first appears at {f[0]}, not after the restart ({rf[0]})")
    # 3g. strategy-specific git checks
    for r in restarts:
        st = local(g.value(r, B.hasRecoveryStrategy) or "")
        rf = witness.first(local(r), prefix)
        if st == "Strat_TransformSimplify":
            for sc in g.objects(r, B.simplifiedBy):
                sf = witness.first(local(sc), prefix)
                if rf and sf and sf[1] >= rf[1]:
                    problems.append(f"ScopeChange {local(sc)} ({sf[0]}) does not precede the simplify restart {local(r)} ({rf[0]})")
        if st == "Strat_TransformReduce":
            t = g.value(r, B.templateLineage)
            if t is not None and t != L:
                tv, _ = classify(g, t, witness, prefix)
                if tv != "ORDERED":
                    problems.append(f"template lineage {local(t)} reads {tv}, not ORDERED; it cannot serve as a reduction target")
    # 3h. divide and conquer: parent is ORDERED only when its parts are and the combine exists
    parts = [pl for pl in g.subjects(B.parentLineage, L)]
    dc = [r for r in restarts if local(g.value(r, B.hasRecoveryStrategy) or "") == "Strat_DivideAndConquer"]
    part_verdicts = {}
    if dc and parts:
        for pl in parts:
            pv_, _ = classify(g, pl, witness, prefix)
            part_verdicts[local(pl)] = pv_
        bl_out = [o for o in outs.get("Stage_Backlog", []) if any(True for _ in g.objects(o, B.combinesOutput))]
        if not bl_out:
            problems_dc = "no combine output yet"
        else:
            problems_dc = None
    # 4. single-commit case
    commits = {f[0] for f in out_first.values()} | {f[0] for f in item_first.values()}
    fro = g.value(L, B.lineageFrozen)
    frozen = fro is not None and bool(fro.toPython())
    # v1.2.3: a lineage frozen more than once carries several frozenBy values (append-only
    # register); the CURRENT freeze is any freezing finding not yet answered or ruled
    frozen_bys = list(g.objects(L, B.frozenBy))
    thrash_open = any((fb, RDF.type, B.LineageThrash) in g for fb in frozen_bys) and g.value(L, B.frozenRuling) is None
    bypass_open = any((fb, RDF.type, B.LineageBypass) in g and not any((r, B.answersBypass, fb) in g for r in restarts)
                      for fb in frozen_bys)
    if frozen and thrash_open:
        verdict = "FROZEN"
    elif frozen and bypass_open:
        verdict = "FOUND"
    elif thrash:
        verdict = "THRASH"
    elif problems or bypassed:
        verdict = "BYPASS"
    elif dc and parts and (problems_dc or any(v != "ORDERED" for v in part_verdicts.values())):
        verdict = "DIVIDING"
    elif len(commits) == 1 and out_first and item_first:
        verdict = "UNWITNESSED"
    elif not out_first and restarts:
        verdict = "RESTARTED"      # chain retracted, nothing rebuilt yet: disclosed, not silent
    elif not out_first:
        verdict = "NO_OUTPUTS"
    else:
        verdict = "ORDERED"
    return verdict, {"outputs": out_first, "items": item_first, "bypassed": bypassed,
                     "problems": problems, "restart": restart_at, "all_outputs": [o for v in outs.values() for o in v],
                     "planned_late": planned_late, "thrash": thrash,
                     "parts": part_verdicts if (dc and parts) else {}, "restarts": restarts}


def emit_bypass(g, L, d, prefix_iri):
    fw = prefix_iri
    name = f"Bypass_{local(L)}_{time.strftime('%Y%m%d')}"
    lines = [f"{fw}{name} a backlog:LineageBypass ;",
             f"    backlog:bypassedLineage {fw}{local(L)} ;",
             f"    backlog:hasFailureMode backlog:FM_LineageBypass ;",
             f"    backlog:hasFindingScope backlog:Scope_Methodology ;",
             f'    backlog:hasRootCause "The chain was written after the work: the items below first appear in the governed repository before the lineage\'s own Stage_Backlog output does. Measured by git first-appearance, not by the register\'s own dates." ;']
    for ln, f, anchor in d["bypassed"]:
        lines.append(f"    backlog:bypassedItem {fw}{ln} ;")
        lines.append(f'    backlog:itemFirstCommit "{ln} {f[0]} {f[1]}" ;')
    for o in d["all_outputs"]:
        lines.append(f"    backlog:bypassedOutput {fw}{local(o)} ;")
    bf = d["outputs"].get("Stage_Backlog")
    lines.append(f'    backlog:chainClosedCommit "{bf[0] + " " + str(bf[1]) if bf else "absent"}" ;')
    lines.append(f'    backlog:detectedAt "{time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}"^^xsd:dateTime ;')
    lines.append(f'    backlog:detectedBy "{TOOL}" ;')
    lines.append('    backlog:hasRationale "' + "; ".join(d["problems"] + [f"{ln} first appears {f[0]} before Stage_Backlog output {a}" for ln, f, a in d["bypassed"]]).replace('"', "'") + '" .')
    lines.append(f"{fw}{local(L)} backlog:lineageFrozen true ; backlog:frozenBy {fw}{name} .   # found: frozen until a restart answers it, in its own commit")
    return "\n".join(lines)


def emit_thrash(g, L, d, fw):
    out = []
    for n, (kind, b, r, lost, detail) in enumerate(d["thrash"], 1):
        name = f"Thrash_{local(L)}_{time.strftime('%Y%m%d')}_{n}"
        lines = [f"{fw}{name} a backlog:LineageThrash ;",
                 f"    backlog:thrashedLineage {fw}{local(L)} ;",
                 f"    backlog:hasFailureMode backlog:FM_LineageThrash ;",
                 f"    backlog:hasFindingScope backlog:Scope_Methodology ;",
                 f"    backlog:hasThrashKind backlog:{kind} ;",
                 f"    backlog:repeatedBypass {fw}{local(b)} ;"]
        if r is not None:
            lines.append(f"    backlog:priorRestart {fw}{local(r)} ;")
        for i in lost:
            lines.append(f"    backlog:lostItem {fw}{i} ;")
        lines.append(f'    backlog:hasRootCause "{detail.replace(chr(34), chr(39))}. Successive trials on this lineage are not converging; a further restart would be a turn of the loop, not a correction." ;')
        lines.append(f'    backlog:detectedAt "{time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}"^^xsd:dateTime ;')
        lines.append(f'    backlog:detectedBy "{TOOL}" ;')
        lines.append(f"    backlog:belongsToLineage {fw}{local(L)} .")
        lines.append(f"{fw}{local(L)} backlog:lineageFrozen true ; backlog:frozenBy {fw}{name} .")
        lines.append(f"# owner's ruling goes here when made: {fw}{local(L)} backlog:frozenRuling \"...\" ; backlog:decidedBy backlog:Owner .")
        out.append("\n".join(lines))
    return "\n\n".join(out)


def main():
    argv = sys.argv[1:]
    witness_path = argv[argv.index("--witness") + 1] if "--witness" in argv else None
    args = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--witness")]
    if not args:
        print(__doc__); return 1
    reg = args[0]
    emit = "--emit" in sys.argv
    g = Graph()
    for f in args:
        g.parse(f, format="turtle")
    # the register's own namespace prefix, for names in git and in emitted Turtle
    # the prefix is the one bound to the namespace the lineages themselves live in;
    # rdflib binds dozens of defaults, so "first non-standard prefix" is a guess
    lin = next(iter(g.subjects(RDF.type, B.Lineage)), None)
    ns_of = str(lin).rsplit("#", 1)[0] + "#" if lin is not None and "#" in str(lin) else None
    prefix = next((p + ":" for p, ns in g.namespaces() if ns_of and str(ns) == ns_of), "fw:")
    if witness_path:
        witness = MapWitness(witness_path)
        print(f"witness     : {os.path.basename(witness_path)} (fixture map)")
    else:
        root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=PKG, capture_output=True, text=True).stdout.strip()
        rel = os.path.relpath(os.path.join(PKG, "01-ontologies"), root)
        witness = GitWitness(root, rel)
        print(f"witness     : git first-appearance under {rel}")
    print(f"register    : {os.path.basename(reg)}")
    worst = 0; n = 0
    emitted = []
    for L in sorted(g.subjects(RDF.type, B.Lineage), key=local):
        arch = g.value(L, B.lineageArchived)
        if arch is not None and bool(arch.toPython()):
            continue
        prefix = prefix_for(g, L)
        verdict, d = classify(g, L, witness, prefix)
        if verdict == "NO_OUTPUTS":
            continue
        n += 1
        bl = d["outputs"].get("Stage_Backlog")
        print(f"  {local(L):24} {verdict:12} outputs={len(d['outputs'])} items={len(d['items'])} backlog_output={bl[0] if bl else 'absent'}"
              + ("  (chain retracted; rebuild from Mission pending)" if verdict == "RESTARTED" else "")
              + (f" restart={d['restart'][0]}" if d['restart'] else ""))
        for p in d["problems"]:
            print(f"      - {p}")
        for ln, f, a in d["bypassed"]:
            print(f"      - {ln} first {f[0]} < Stage_Backlog output {a}")
        for ln, f, pe, pf in d["planned_late"]:
            print(f"      - PLANNED_LATE {ln} first {f[0]} < its PlanningEvent {pe} first {pf[0]}")
        for kind, b, r, lost, detail in d["thrash"]:
            print(f"      - THRASH {kind}: {detail}")
        for pn, pvv in d["parts"].items():
            print(f"      - PART {pn}: {pvv}")
        if emit and d["restarts"]:
            # reductionObserved for a NEXT restart: of the items the last bypass named, how many are admitted now
            last_r = d["restarts"][-1]
            for b in g.objects(last_r, B.answersBypass):
                named = list(g.objects(b, B.bypassedItem))
                adm = [i for i in named if g.value(i, B.admittedByOutput) is not None
                       and not (g.value(g.value(i, B.admittedByOutput), B.outputRetracted) or False)]
                if named:
                    print(f"      # reductionObserved for a next restart of {local(L)}: {len(adm)}/{len(named)} = {len(adm)/len(named):.3f}")
        if verdict == "THRASH":
            recorded = any((t, B.thrashedLineage, L) in g for t in g.subjects(RDF.type, B.LineageThrash))
            if not recorded:
                worst = 2
                if emit:
                    emitted.append(emit_thrash(g, L, d, prefix))
        if verdict == "BYPASS":
            # v1.2.3: "answered" means every item bypassed NOW is named by a recorded bypass of this
            # lineage that a restart answers. v1.2.2 asked only whether ANY bypass of the lineage had
            # ever been answered -- so a second, new bypass on a once-restarted lineage was neither
            # emitted nor failed. Found on the toy exercise's second trial (only the unrelated
            # lineage's finding came out of --emit).
            def named_and_answered(ln):
                for b in g.subjects(B.bypassedLineage, L):
                    if any(local(i) == ln for i in g.objects(b, B.bypassedItem)) \
                            and any(True for _ in g.subjects(B.answersBypass, b)):
                        return True
                return False
            answered = all(named_and_answered(ln) for ln, _, _ in d["bypassed"]) and not d["problems"]
            if not answered:
                worst = 2
                if emit:
                    emitted.append(emit_bypass(g, L, d, prefix))
    if n == 0:
        print("VERDICT     : NOT VERIFIABLE — no non-archived lineage carries stage outputs")
        return 0
    if emitted:
        print("\n# --- emitted findings (append to the register; the shapes then require a LineageRestart) ---")
        print("\n\n".join(emitted))
    if worst:
        print("VERDICT     : FAIL — a live lineage is bypassed without a restart, or its restarts are not converging without a thrash record; see above")
    else:
        print("VERDICT     : PASS — every live lineage's chain is witnessed in order, or its order is unwitnessed and disclosed")
    return worst


if __name__ == "__main__":
    sys.exit(main())
