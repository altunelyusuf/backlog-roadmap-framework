#!/usr/bin/env python3
"""backlog_lineage_order_check v1.0.0 — did the chain come before the work, or after?

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
  PLANNED_LATE (per item, advisory) a PlanningEvent first appears after the item it
               plans: the work existed, then the planning record was written to fit it.
               Reported on every run; not a gate failure in v1.0.0.
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

Exit: 0 ORDERED/UNWITNESSED only; 2 any BYPASS without an answering restart; 1 on error.
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


def classify(g, L, witness, prefix):
    """Returns (verdict, detail dict) for one lineage."""
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
    # 4. single-commit case
    commits = {f[0] for f in out_first.values()} | {f[0] for f in item_first.values()}
    if problems or bypassed:
        verdict = "BYPASS"
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
                     "planned_late": planned_late}


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
    return "\n".join(lines)


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
        if verdict == "BYPASS":
            answered = any((b, B.bypassedLineage, L) in g and any(True for _ in g.subjects(B.answersBypass, b))
                           for b in g.subjects(RDF.type, B.LineageBypass))
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
        print("VERDICT     : BYPASS — a live lineage's chain was closed after its work; unfreeze and restart it, do not backfill")
    else:
        print("VERDICT     : PASS — every live lineage's chain is witnessed in order, or its order is unwitnessed and disclosed")
    return worst


if __name__ == "__main__":
    sys.exit(main())
