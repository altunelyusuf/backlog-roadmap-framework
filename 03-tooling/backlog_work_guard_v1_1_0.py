#!/usr/bin/env python3
"""backlog_work_guard v1.1.0 -- the safeguard that sits IN THE PATH of the act, not after it.

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
  range A..B             after the fact, for CI: the same check over every non-merge commit in the range. This is the
                         layer `git commit --no-verify` cannot skip. v1.1.0 (G119): the CONFIGURATION is read at A, so a
                         commit that loosens it takes effect only in the next range; each commit's Work-Items are judged
                         against the register at THAT COMMIT'S PARENT (ready before the commit, as the commit-msg hook
                         judges it), and an item that became ready inside the range is reported. --strict-base turns that
                         report into a failure for an adopter that wants readiness established before the range.

CONFIG  (.backlog-guard.json at the repository root, or --config PATH)
  {"register": ["packages/X/register.ttl"], "active_lineage": "Lineage_2",
   "work_paths": ["app/**", "src/**"], "exempt_paths": ["app/README.md"], "governed_from": "<commit sha>"}
  governed_from: commits that are ancestors of it (inclusive) predate the guard and are not examined by `range`; the
  installer sets it to the commit at install time, a restart sets it to the restart commit.
  A work path is a glob (`**` crosses directories, `*` does not). Everything else is not governed work.
  protected_paths (v1.1.0): always governed, and no exempt path can release them: the configuration, .githooks/**,
  .claude/settings.json, the CI workflow and the vendored tooling directory ("tooling_dir"). Changing the guard needs a
  ready Work-Item like any other work. The installer writes them; a configuration without the key gets the defaults.

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
    def __init__(self, config_path, root=None, cfg=None):
        self.root = root or os.path.dirname(os.path.abspath(config_path))
        self.config_path = config_path
        if cfg is None:
            try:
                cfg = json.load(open(config_path))
            except Exception as e:
                raise SystemExit(f"GUARD BLOCKS: cannot read config {config_path}: {e}")
        self.cfg = cfg
        self.work = [glob_re(p) for p in self.cfg.get("work_paths", [])]
        self.exempt = [glob_re(p) for p in self.cfg.get("exempt_paths", [])]
        prot = self.cfg.get("protected_paths")
        if prot is None:
            prot = [os.path.relpath(os.path.abspath(config_path), self.root), ".githooks/**", ".claude/settings.json", ".github/workflows/backlog-work-guard.yml"]
            if self.cfg.get("tooling_dir"):
                prot.append(self.cfg["tooling_dir"].strip("/") + "/**")
        self.protected = [glob_re(p) for p in prot]
        self.lineage = self.cfg.get("active_lineage")
        self.ready = _ready_module()

    def is_work(self, path):
        path = re.sub(r"^\./", "", path)
        if re.search(r"(^|/)__pycache__/", path) or path.endswith(".pyc"):
            return False        # interpreter bytecode is never work; running the tools writes it into their own directory
        if any(r.match(path) for r in self.protected):
            return True
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

    def graph(self, rev=None, tolerant=False):
        """The register at REV (the working tree when None). tolerant: return None instead of stopping when the register
        did not exist or could not be read at REV (a commit before the register was committed judges nothing ready)."""
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
                if tolerant:
                    return None
                raise SystemExit(f"GUARD BLOCKS: cannot read the register {rel}: {str(e)[:200]}")
        if len(g) == 0:
            if tolerant:
                return None
            raise SystemExit("GUARD BLOCKS: the register is empty (examined: 0 triples)")
        return g

    def blob_key(self, rev):
        """Identity of the register files at REV, so one parse serves every commit that sees the same bytes."""
        out = []
        for rel in self.cfg.get("register", []):
            try:
                out.append(git(self.root, "rev-parse", f"{rev}:{rel}").strip())
            except RuntimeError:
                out.append("absent")
        return tuple(out)

    def item_problem(self, g, name):
        """None when NAME is ready in G, else the sentence saying why not."""
        lin = self.item_lineage(g, name)
        if lin is None:
            return f"Work-Item {name}: not found in the register, or it belongs to no lineage"
        miss = self.ready.evaluate(g, lin, name, emit=lambda *_: None)
        return f"Work-Item {name} (lineage {lin}) is not ready: " + "; ".join(miss) if miss else None

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


def cmd_range(gd, rng, out=print, strict_base=False):
    base, tip = (re.split(r"\.{2,3}", rng, maxsplit=1) + [""])[:2] if ".." in rng else ("", rng)
    base, tip = base or "HEAD", tip or "HEAD"
    # v1.1.0 (G119): the configuration that judges a range is the one in force BEFORE it. A commit in the range that
    # loosens it (adds an exempt path, raises governed_from) takes effect in the next range, not in this one.
    rel_cfg = os.path.relpath(os.path.abspath(gd.config_path), gd.root)
    try:
        base_cfg = json.loads(git(gd.root, "show", f"{base}:{rel_cfg}"))
    except Exception:
        base_cfg = None
    if base_cfg is None:
        out(f"guard range {rng}: no configuration at {base}; the configuration at the tip is used (this range installs the guard)")
    elif base_cfg != gd.cfg:
        out(f"guard range {rng}: the configuration changed inside this range; it was read at {base}, so the change governs the next range")
        gd = Guard(gd.config_path, gd.root, cfg=base_cfg)
    errs = gd.self_check()
    if errs:
        for e in errs:
            out("GUARD FAILS: " + e)
        return 2
    cmd = ["rev-list", "--no-merges", "--reverse", rng]
    gf = gd.cfg.get("governed_from")
    if gf:
        cmd.append(f"^{gf}")
    revs = git(gd.root, *cmd).split()
    touched = 0
    bad = []
    named = set()
    graphs, verdicts, readied = {}, {}, []
    g_base = gd.graph(base, tolerant=True)
    def at(rev):
        k = gd.blob_key(rev)
        if k not in graphs:
            graphs[k] = gd.graph(rev, tolerant=True)
        return k, graphs[k]
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
        has_parent = subprocess.run(["git", "-C", gd.root, "rev-parse", "-q", "--verify", f"{r}^"], capture_output=True).returncode == 0
        k, g = at(f"{r}^") if has_parent else (("root",), None)
        for i in items:
            named.add(i)
            if g is None:
                bad.append(f"{r[:9]} Work-Item {i}: there was no register before this commit")
                continue
            if (k, i) not in verdicts:
                verdicts[(k, i)] = gd.item_problem(g, i)
            if verdicts[(k, i)]:
                bad.append(f"{r[:9]} {verdicts[(k, i)]}")
            elif g_base is None or gd.item_problem(g_base, i):
                readied.append((r[:9], i))
    out(f"guard range {rng}: examined {len(revs)} commit(s), {touched} touch governed work, {len(named)} item(s) named")
    for r9, i in readied:
        out(f"  NOTE  {r9} Work-Item {i} was not ready at {base}; it became ready inside this range" + (" (a failure under --strict-base)" if strict_base else ""))
        if strict_base:
            bad.append(f"{r9} Work-Item {i} was not ready before the range began")
    for b in bad:
        out("  FAIL  " + b)
    out("VERDICT: " + ("PASS" if not bad else f"FAIL -- {len(bad)} work commit(s) outside the register"))
    return 2 if bad else 0


def main(argv):
    cfg = None
    args = list(argv)
    strict = "--strict-base" in args
    args = [a for a in args if a != "--strict-base"]
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
    if cmd == "range":
        return cmd_range(gd, args[1], strict_base=strict)
    return {"edit": cmd_edit, "commit-msg": cmd_commit_msg}[cmd](gd, args[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
