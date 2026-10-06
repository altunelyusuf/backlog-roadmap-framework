#!/usr/bin/env python3
"""backlog_work_guard v1.0.0 -- the safeguard that sits IN THE PATH of the act, not after it.

WHY THIS EXISTS (ruling G101). an adopting project opened Lineage_2 to stop work happening outside the register, closed its
Mission..Objective stages, never built the Backlog stage, and shipped nine releases from a work ledger. Every safeguard
it had was either prose (a "standing practice" written after each of ~20 earlier drifts) or a check run after the act
(order check, validator). Nothing stood between the coordinator and a commit. This tool is that thing.

Four entry points, one rule: no work-path change without a registered, groomed, admitted item.
  status                 print the lineage's start-gate facts and the NEXT REQUIRED ACT (put in front of the session at
                         start, so it does not depend on what a compacted conversation remembers)
  edit FILE              before a file is written: if FILE is a work path, the lineage must be READY (start gate)
  commit-msg MSGFILE     before a commit: if the staged files include a work path, the message must carry
                         `Work-Item: NAME` trailers and each named item must be READY in the register
  range A..B             after the fact, for CI: the same check over every non-merge commit in the range, against the
                         register as it is at B. This is the layer `git commit --no-verify` cannot skip.

CONFIG  (.backlog-guard.json at the repository root, or --config PATH)
  {"register": ["packages/X/register.ttl"], "active_lineage": "Lineage_2",
   "work_paths": ["app/**", "src/**"], "exempt_paths": ["app/README.md"], "governed_from": "<commit sha>"}
  governed_from: commits that are ancestors of it (inclusive) predate the guard and are not examined by `range`; the
  installer sets it to the commit at install time, a restart sets it to the restart commit.
  A work path is a glob (`**` crosses directories, `*` does not). Everything else is not governed work.

THE GUARD MUST NOT BE ABLE TO PASS OVER NOTHING (the failure it exists to prevent):
  - a work_path glob matching no tracked file fails the run: a guard configured over nothing proves nothing
  - an empty work_paths list fails; a missing register fails; an unparseable register fails (fail closed, exit 2)
  - every run prints what it examined: commits, work-touching commits, items

Exit 0 compliant (or not work), 2 a violation or a guard that could not examine anything (block), 1 usage error.
Reads only; never edits the repository or the register. Needs rdflib and git.
"""
import fnmatch, glob, importlib.util, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TRAILER = re.compile(r"^Work-Item:\s*([A-Za-z0-9_.:-]+)\s*$", re.M)


def _ready_module():
    sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
    cands = sorted(glob.glob(os.path.join(HERE, "backlog_execution_ready_v*.py")), key=sv)
    cands = [c for c in cands if "probe" not in os.path.basename(c)]
    if not cands:
        raise SystemExit("guard cannot ask the start gate: backlog_execution_ready is not beside it")
    spec = importlib.util.spec_from_file_location("backlog_execution_ready", cands[-1])
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def glob_re(pat):
    out, i = "", 0
    while i < len(pat):
        if pat.startswith("**/", i):
            out += "(?:.*/)?"; i += 3
        elif pat.startswith("**", i):
            out += ".*"; i += 2
        elif pat[i] == "*":
            out += "[^/]*"; i += 1
        elif pat[i] == "?":
            out += "[^/]"; i += 1
        else:
            out += re.escape(pat[i]); i += 1
    return re.compile("^" + out + "$")


def git(root, *args):
    r = subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


class Guard:
    def __init__(self, config_path, root=None):
        self.root = root or os.path.dirname(os.path.abspath(config_path))
        try:
            self.cfg = json.load(open(config_path))
        except Exception as e:
            raise SystemExit(f"GUARD BLOCKS: cannot read config {config_path}: {e}")
        self.work = [glob_re(p) for p in self.cfg.get("work_paths", [])]
        self.exempt = [glob_re(p) for p in self.cfg.get("exempt_paths", [])]
        self.lineage = self.cfg.get("active_lineage")
        self.ready = _ready_module()

    def is_work(self, path):
        path = re.sub(r"^\./", "", path)
        return any(r.match(path) for r in self.work) and not any(r.match(path) for r in self.exempt)

    def self_check(self):
        """A guard over nothing proves nothing: fail unless the configuration reaches real files."""
        errs = []
        if not self.work:
            errs.append("work_paths is empty: the guard governs nothing")
        if not self.cfg.get("register"):
            errs.append("register is not configured")
        if not self.lineage:
            errs.append("active_lineage is not configured")
        try:
            tracked = git(self.root, "ls-files").splitlines()
        except RuntimeError as e:
            return [str(e)]
        for pat, r in zip(self.cfg.get("work_paths", []), self.work):
            if not any(r.match(t) for t in tracked):
                errs.append(f"work path '{pat}' matches no tracked file (a guard configured over nothing)")
        return errs

    def graph(self, rev=None):
        from rdflib import Graph
        g = Graph()
        for rel in self.cfg.get("register", []):
            try:
                if rev:
                    data = git(self.root, "show", f"{rev}:{rel}")
                    g.parse(data=data, format="turtle")
                else:
                    g.parse(os.path.join(self.root, rel), format="turtle")
            except Exception as e:
                raise SystemExit(f"GUARD BLOCKS: cannot read the register {rel}: {str(e)[:200]}")
        if len(g) == 0:
            raise SystemExit("GUARD BLOCKS: the register is empty (examined: 0 triples)")
        return g

    def item_lineage(self, g, name):
        from rdflib import URIRef
        B = self.ready.B
        X = self.ready.find(g, name)
        if X is None:
            return None
        L = g.value(X, B.belongsToLineage)
        if L is None:
            for o in g.objects(X, B.admittedByOutput):
                L = g.value(o, B.belongsToLineage)
                if L is not None:
                    break
        return str(L).replace("/", "#").rsplit("#", 1)[-1] if L is not None else None

    def check_items(self, g, items, out):
        bad = []
        for name in items:
            lin = self.item_lineage(g, name)
            if lin is None:
                bad.append(f"Work-Item {name}: not found in the register, or it belongs to no lineage")
                continue
            lines = []
            miss = self.ready.evaluate(g, lin, name, emit=lines.append)
            if miss:
                bad.append(f"Work-Item {name} (lineage {lin}) is not ready: " + "; ".join(miss))
            else:
                out(f"  ok    Work-Item {name} (lineage {lin}) is ready")
        return bad

    def next_act(self, g):
        B = self.ready.B
        L = self.ready.find(g, self.lineage)
        if L is None:
            return f"the lineage {self.lineage} does not exist in the register"
        for st in self.ready.STAGES:
            outs = [o for o in g.subjects(B.belongsToLineage, L) if (o, B.outputOfStage, B[st]) in g and self.ready.active(g, o)]
            if not outs:
                return f"build the {st.replace('Stage_', '')} stage (one commit per stage, owner affirms the Mission); no work until then"
        return "register and groom work items (concern, criterion, planning event), then name each as Work-Item in the commit"


def staged_files(root):
    return [l for l in git(root, "diff", "--cached", "--name-only", "--diff-filter=ACMRD").splitlines() if l]


def cmd_status(gd, out=print):
    errs = gd.self_check()
    g = gd.graph()
    lines = []
    miss = gd.ready.evaluate(g, gd.lineage, None, emit=lines.append)
    out(f"BACKLOG GUARD  lineage {gd.lineage}: " + ("READY" if not miss else f"NOT READY ({len(miss)} fact(s) missing)"))
    for l in lines:
        if "FAIL" in l:
            out(l)
    out("NEXT REQUIRED ACT: " + gd.next_act(g))
    for e in errs:
        out("  GUARD CONFIG: " + e)
    out("Work paths are governed: " + ", ".join(gd.cfg.get("work_paths", [])) + ". Every work commit needs `Work-Item:` trailers.")
    return 0


def cmd_edit(gd, path, out=print):
    root = gd.root
    rel = os.path.relpath(os.path.abspath(path), root) if os.path.isabs(path) or os.path.exists(path) else path
    if not gd.is_work(rel):
        return 0
    g = gd.graph()
    lines = []
    miss = gd.ready.evaluate(g, gd.lineage, None, emit=lines.append)
    if miss:
        out(f"GUARD BLOCKS this edit of {rel}: it is governed work and lineage {gd.lineage} is not ready.")
        for m in miss:
            out(f"  missing: {m}")
        out("NEXT REQUIRED ACT: " + gd.next_act(g))
        return 2
    return 0


def cmd_commit_msg(gd, msgfile, out=print):
    errs = gd.self_check()
    if errs:
        for e in errs:
            out("GUARD BLOCKS: " + e)
        return 2
    files = staged_files(gd.root)
    work = [f for f in files if gd.is_work(f)]
    out(f"guard: {len(files)} staged file(s), {len(work)} governed work file(s)")
    if not work:
        return 0
    msg = open(msgfile).read()
    items = TRAILER.findall(msg)
    if not items:
        out("GUARD BLOCKS this commit: it changes governed work but names no `Work-Item: NAME` trailer.")
        out("  work files: " + ", ".join(work[:5]) + (" ..." if len(work) > 5 else ""))
        return 2
    bad = gd.check_items(gd.graph(), items, out)
    for b in bad:
        out("GUARD BLOCKS this commit: " + b)
    return 2 if bad else 0


def cmd_range(gd, rng, out=print):
    errs = gd.self_check()
    if errs:
        for e in errs:
            out("GUARD FAILS: " + e)
        return 2
    tip = rng.split("..")[-1] or "HEAD"
    cmd = ["rev-list", "--no-merges", rng]
    gf = gd.cfg.get("governed_from")
    if gf:
        cmd.append(f"^{gf}")
    revs = git(gd.root, *cmd).split()
    g = gd.graph(tip)
    touched = 0
    bad = []
    cache = {}
    for r in revs:
        files = git(gd.root, "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", r).splitlines()
        work = [f for f in files if gd.is_work(f)]
        if not work:
            continue
        touched += 1
        msg = git(gd.root, "log", "-1", "--format=%B", r)
        items = TRAILER.findall(msg)
        if not items:
            bad.append(f"{r[:9]} changes governed work ({work[0]}{' ...' if len(work) > 1 else ''}) and names no Work-Item")
            continue
        for b in gd.check_items(g, [i for i in items if i not in cache], lambda *_: None):
            bad.append(f"{r[:9]} {b}")
        for i in items:
            cache[i] = True
    out(f"guard range {rng}: examined {len(revs)} commit(s), {touched} touch governed work, {len(set(cache))} item(s) named")
    for b in bad:
        out("  FAIL  " + b)
    out("VERDICT: " + ("PASS" if not bad else f"FAIL -- {len(bad)} work commit(s) outside the register"))
    return 2 if bad else 0


def main(argv):
    cfg = None
    args = list(argv)
    if "--config" in args:
        i = args.index("--config"); cfg = args[i + 1]; del args[i:i + 2]
    if not args or args[0] not in ("status", "edit", "commit-msg", "range"):
        print(__doc__); return 1
    if cfg is None:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or os.getcwd()
        cfg = os.path.join(top, ".backlog-guard.json")
    gd = Guard(cfg)
    cmd = args[0]
    if cmd == "status":
        return cmd_status(gd)
    if len(args) < 2:
        print(__doc__); return 1
    return {"edit": cmd_edit, "commit-msg": cmd_commit_msg, "range": cmd_range}[cmd](gd, args[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
