#!/usr/bin/env python3
"""backlog_next_act v1.2.0 (box 61, G247; repairs of review rounds 1 and 2) -- the rules are enforced before the act, carry their own repair, and are corrected in rounds.

  check REGISTER... [--shapes PATH] [--tbox PATH] [--repairs REGISTER] [--all] [--warnings]
      Before a step: runs the shapes that carry a repair record (every shape with --all) over the T-box and the register(s), as the validator runs them
      (advanced, no inference), and prints each refusal with the repair of its rule: the condition, the correct method, who decides it, and when the Owner is
      asked. A refusal whose rule has no repair record says so. Only a Violation refuses (an advisory is listed with --warnings). Writes nothing. Exit 0 when nothing refuses, 2 when something does.
  armed [--root DIR]
      Exit 0 when the clone is armed: the guard configuration .backlog-guard.json, the git hooks (core.hooksPath .githooks with a commit-msg hook) and the
      session hooks (.claude/settings.json naming the guard hook) are in place; or the clone is the framework's own, guarded by its release gate (G194).
      A package under the system temporary directory that is not inside a git work tree is a throwaway sandbox for probes and is not checked unless BACKLOG_ARMED_STRICT=1; a real clone is always checked.
      The framework's own clone is the package directory backlog-roadmap-framework (VERSION.txt, a release tool) of a git repository whose origin is the maintainer/ontologies; a vendored copy is not.
      Exit 2 otherwise, saying how to arm it (backlog_guard_install).
  round REGISTER --for NAME --repairs TEXT (here TEXT is what was repaired) [--satisfied] [--prefix PFX] [--now TIME]
      Appends a repair round to the register: the next number for the subject, what was repaired, whether every rule held at the recheck. Appends only; an
      earlier round is never edited, and a round after a satisfied one is refused.
Repairs are records (backlog:RuleRepair), not prose of this tool; the register that carries them is read beside the one checked (--repairs REGISTER, default
the framework register beside this tool). Needs rdflib and pyshacl."""
import os, re, sys, glob, json, subprocess, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.join(HERE, "..")
BL = "http://example.org/backlog#"; SHN = "http://www.w3.org/ns/shacl#"
def newest(folder, stem):
    fs = glob.glob(os.path.join(PKG, folder, stem + "_v*.ttl"))
    return sorted(fs, key=lambda f: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", f)[0]])[-1]
def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default
def local(x): return str(x).split("#")[-1].split("/")[-1]

def armed(pkg):
    import tempfile
    inrepo = subprocess.run(["git", "-C", pkg, "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    if not inrepo and os.path.realpath(pkg).startswith(os.path.realpath(tempfile.gettempdir()) + os.sep) and os.environ.get("BACKLOG_ARMED_STRICT") != "1":
        return True, "a throwaway package in the temporary directory (a sandbox for probes): its guard is not checked"
    top = subprocess.run(["git", "-C", pkg, "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or pkg
    cfg = os.path.exists(os.path.join(top, ".backlog-guard.json"))
    hp = subprocess.run(["git", "-C", top, "config", "core.hooksPath"], capture_output=True, text=True).stdout.strip()
    hooks = hp == ".githooks" and os.path.exists(os.path.join(top, ".githooks", "commit-msg"))
    st = os.path.join(top, ".claude", "settings.json")
    sess = os.path.exists(st) and "backlog_guard_claude_hook" in open(st, encoding="utf-8").read()
    url = subprocess.run(["git", "-C", top, "config", "remote.origin.url"], capture_output=True, text=True).stdout.strip().lower()
    own = (os.path.basename(os.path.realpath(pkg)) == "backlog-roadmap-framework" and re.search(r"the maintainer/ontologies(\.git)?/?$", url) is not None
           and os.path.exists(os.path.join(pkg, "VERSION.txt")) and bool(glob.glob(os.path.join(pkg, "03-tooling", "backlog_release_tool_v*.py"))))
    if cfg and hooks and sess: return True, "armed: guard configuration, git hooks and session hooks are in place"
    if own: return True, "the framework's own clone: guarded by its release gate (G194)"
    miss = [n for n, ok in (("the guard configuration .backlog-guard.json", cfg), ("the git hooks (core.hooksPath .githooks with a commit-msg hook)", hooks), ("the session hooks in .claude/settings.json", sess)) if not ok]
    return False, "NOT ARMED: missing " + "; ".join(miss) + ". Arm the clone with backlog_guard_install (REPO --tooling-dir DIR --register FILE --lineage NAME --work-path GLOB), then run the step again."

def repairs_of(rg):
    from rdflib import Graph, URIRef
    out = {}
    for r in rg.subjects(URIRef(BL + "repairsShape"), None):
        for sh in rg.objects(r, URIRef(BL + "repairsShape")):
            g = lambda p: next(iter(rg.objects(r, URIRef(BL + p))), None)
            who = g("repairDecidedBy")
            out[str(sh)] = {"condition": str(g("hasRepairCondition") or ""), "method": str(g("hasRepairMethod") or ""), "who": local(who) if who else "", "asks": str(g("repairAsksOwnerWhen") or "")}
    return out

def cmd_check(files):
    from rdflib import Graph, URIRef, BNode
    from rdflib.namespace import RDF
    import pyshacl
    SHP = Graph(); SHP.parse(arg("--shapes") or newest("02-shacl-safeguards", "backlog_shacl"), format="turtle")
    dg = Graph(); dg.parse(arg("--tbox") or newest("01-ontologies", "backlog_tbox"), format="turtle")
    for f in files: dg.parse(f, format="turtle")
    rg = Graph(); rg.parse(arg("--repairs") or newest("01-ontologies", "backlog_abox"), format="turtle")
    reps = repairs_of(rg)
    if "--all" in sys.argv: names = {str(s) for s in SHP.subjects(RDF.type, URIRef(SHN + "NodeShape")) if isinstance(s, URIRef)}
    else: names = set(reps)
    red = Graph(); seen = set()
    def walk(n):
        if n in seen: return
        seen.add(n)
        for p, o in SHP.predicate_objects(n):
            red.add((n, p, o))
            if isinstance(o, BNode) or p in (URIRef(SHN + "prefixes"), URIRef(SHN + "declare")): walk(o)
    for n in sorted(names): walk(URIRef(n))
    if not len(red): print("NEXT ACT: no shape to check (no repair record names a shape in the shapes file)"); return 2
    _, vg, _ = pyshacl.validate(dg, shacl_graph=red, advanced=True, inference="none")
    owner = {}
    for n in names:
        for o in red.transitive_objects(URIRef(n), None):
            if isinstance(o, BNode): owner[o] = n
    bad = []
    for r in vg.subjects(RDF.type, URIRef(SHN + "ValidationResult")):
        sh = vg.value(r, URIRef(SHN + "sourceShape")); node = str(sh) if str(sh) in names else owner.get(sh)
        sev = vg.value(r, URIRef(SHN + "resultSeverity"))
        if sev == URIRef(SHN + "Violation") or "--warnings" in sys.argv: bad.append((node, vg.value(r, URIRef(SHN + "focusNode")), str(vg.value(r, URIRef(SHN + "resultMessage")) or "")))
    if not bad: print("NEXT ACT: nothing refuses (%d shape(s) checked)" % len(names)); return 0
    print("NEXT ACT: %d refusal(s) before the step; repair each, then run this check again:" % len(bad))
    for node, focus, msg in sorted(bad, key=lambda b: (str(b[0]), str(b[1]))):
        print("- %s on %s: %s" % (local(node) if node else "a shape", local(focus), msg[:200]))
        rp = reps.get(node)
        if rp:
            print("    when: %s\n    do: %s\n    decided by: %s\n    ask the Owner when: %s" % (rp["condition"], rp["method"], rp["who"] or "the session", rp["asks"] or "no rule or fact settles it"))
        else: print("    no repair record for this rule: state what is missing and ask the Owner one point at a time")
    return 2

def cmd_round(reg):
    from rdflib import Graph, URIRef, Literal
    original = open(reg, encoding="utf-8").read(); text = original; subject = arg("--for"); repairs = arg("--repairs"); av = sys.argv[1:]; sat = any(x == "--satisfied" and (i == 0 or av[i-1] not in ("--for", "--repairs", "--prefix", "--now")) for i, x in enumerate(av))
    if not subject or not repairs: print("ERROR: round needs --for NAME and --repairs TEXT"); return 1
    if not re.fullmatch(r"[A-Za-z0-9_]+", subject): print("ERROR: --for NAME is a local name of letters, digits and underscores"); return 1
    pfx = arg("--prefix", "RR"); ns = re.search(r"@prefix fw:\s*<([^>]+)>", text)
    if not ns: print("ERROR: the register declares no fw: prefix"); return 1
    g = Graph(); g.parse(reg, format="turtle"); who = URIRef(ns.group(1) + subject)
    nums, ended = [], False
    for r in g.subjects(URIRef(BL + "roundFor"), who):
        nums += [int(x) for x in g.objects(r, URIRef(BL + "hasRoundNumber"))]
        ended = ended or any(x.toPython() is True for x in g.objects(r, URIRef(BL + "roundSatisfied")))
    if ended:
        print("ERROR: a satisfied round already ends the series for %s; a later problem is a new refusal on a new subject" % subject); return 2
    n = max(nums, default=0) + 1; now = arg("--now") or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rep = repairs.replace("\\", "\\\\").replace('"', '\\"').replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")
    rec = 'fw:Round_%s_%s_%d a backlog:RepairRound ; backlog:roundFor fw:%s ; backlog:hasRoundNumber %d ; backlog:hasRoundRepairs "%s" ; backlog:roundSatisfied %s ; backlog:roundAt "%s"^^xsd:dateTime .\n' % (pfx, subject, n, subject, n, rep, "true" if sat else "false", now)
    open(reg, "a", encoding="utf-8").write(("" if text.endswith("\n") else "\n") + rec)
    try: Graph().parse(reg, format="turtle")
    except Exception as e:
        open(reg, "w", encoding="utf-8").write(original); print("ERROR: the round would leave the register unparsable (%s); nothing written" % str(e)[:120]); return 2
    print("round %d appended for %s (%s)" % (n, subject, "satisfied: the series ends" if sat else "not yet satisfied: repair and append the next round")); return 0

def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"): print(__doc__); return 1
    if a[0] == "--deps": print(os.path.abspath(__file__)); print(newest("01-ontologies", "backlog_tbox")); print(newest("02-shacl-safeguards", "backlog_shacl")); print(newest("01-ontologies", "backlog_abox")); return 0
    if a[0] == "armed":
        ok, why = armed(os.path.abspath(arg("--root", PKG))); print(why); return 0 if ok else 2
    if a[0] == "check":
        regs, skip = [], False
        for x in a[1:]:
            if skip: skip = False
            elif x in ("--shapes", "--tbox", "--repairs"): skip = True
            elif not x.startswith("--"): regs.append(x)
        return cmd_check(regs)
    if a[0] == "round": return cmd_round(a[1])
    print("ERROR: unknown command %s" % a[0]); return 1
if __name__ == "__main__": sys.exit(main())
