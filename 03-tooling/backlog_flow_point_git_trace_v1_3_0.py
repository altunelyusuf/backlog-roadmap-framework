#!/usr/bin/env python3
"""backlog_flow_point_git_trace v1.3.0 -- compare every item's recorded start, finish and state with the commits that recorded them.

WHY. A commit time is the latest instant a change can have been made. A finish later than the commit that first recorded the item Done is impossible, and the data
alone cannot show it: the witness is the history of the register in the repository that holds it (the same kind of witness backlog_lineage_order_check reads).
Written from the comparison script of a consuming project's handover (2026-10-14); changes: instants without a zone are read as UTC (the original stopped on them),
the check is a gate with an exit code, and the classes are named.

CLASSES (per item): future_finish (a finish later than the commit that first recorded the item Done); two_values (more than one startedAt or finishedAt);
finish_not_after_start; under_2_min (a span below two minutes, a signal to explain, not an error); midnight (a flow point at exactly 00:00:00);
state paths seen in commits (how items moved through the states in the commits that recorded them).

v1.3.0 (Lineage 31, story Fixed; speed only): the blob of the register in each commit is read from the same `git log --raw` walk that lists the commits, not by one `git rev-parse` per commit (391 calls, 37 of the 38 seconds of a warm run); the findings are the same.
v1.2.0 (Lineage 29, G193): a future_finish may be EXPLAINED by a row of the ledger (--ledger FILE: stem, item, first-Done time, finish, gap in hours, commit, reason).
A row explains an item only when the item, its first-Done time and its finish all equal the measurement; an unexplained item fails as before; a row that explains
nothing (the item no longer shows the fault, or any value differs) is stale and fails. A ledger holds history that cannot be corrected (append-only), may only shrink,
and never excuses a new item. Without --ledger the tool behaves as v1.1.0.

Usage: backlog_flow_point_git_trace.py REPO REGISTER_PATH_IN_REPO [CURRENT_FILE] [--strict] [--ledger FILE]
Exit 0 when no future_finish and no two_values (and, with --strict, no finish_not_after_start and no under_2_min); 2 otherwise; 1 on error. Reads only.
"""
import hashlib, json, os, re, subprocess, sys, datetime as dt
from collections import Counter
from rdflib import Graph, Namespace
B = Namespace("http://example.org/backlog#")
def utc(x):
    return x if x.tzinfo else x.replace(tzinfo=dt.timezone.utc)
def states_at(git, h, p, blob=None):
    """(item, state) pairs of the register in commit h, or None when it does not parse. v1.1.0: kept on disk by the blob's hash (a blob never changes), so a
    commit already read is not parsed again; v1.0.0 parsed the whole register at every commit of its history, 30 s of the gate."""
    d = os.environ.get("BACKLOG_VALIDATE_MEMO_DIR")
    f = None
    try:
        blob = blob or git("rev-parse", f"{h}:{p}").strip()
        if d and re.fullmatch(r"[0-9a-f]{40,64}", blob):
            f = os.path.join(d, "flowstates_%s.json" % blob)
            if os.path.exists(f):
                return [tuple(x) for x in json.load(open(f))]
    except Exception:
        f = None
    try:
        g = Graph().parse(data=git("show", f"{h}:{p}"), format="turtle")
    except Exception:
        return None
    pairs = [(str(i).split("#")[-1], str(st).split("#")[-1]) for i, st in g.subject_objects(B.hasState)]
    if f:
        try:
            tmp = f + ".%d.tmp" % os.getpid(); json.dump(pairs, open(tmp, "w")); os.replace(tmp, f)
        except Exception:
            pass
    return pairs
MEASURED = {}
def trace(repo, reg, current=None):
    git = lambda *a: subprocess.check_output(("git", "-C", repo) + a, stderr=subprocess.DEVNULL).decode()
    rows, h, t = [], None, None
    # v1.3.0: `git log --follow` costs 35 s on the repository (rename detection over every commit). The history before a commit never changes, so the rows of a walk are kept in the memo directory with the
    # head they were read at, and a later run walks only the commits since that head (when it is an ancestor of the present head) and appends them.
    head = git("rev-parse", "HEAD").strip()
    stem = re.sub(r"_v\d+_\d+_\d+", "", reg)
    wf = None
    d0 = os.environ.get("BACKLOG_VALIDATE_MEMO_DIR")
    shallow = git("rev-parse", "--is-shallow-repository").strip() == "true"
    if d0 and not shallow:       # a shallow clone's walk is not the history
        wf = os.path.join(d0, "aux_flowwalk_%s.json" % hashlib.sha256((os.path.abspath(repo) + "|" + stem).encode()).hexdigest()[:24])
    old_rows, old_head = [], None
    if wf and os.path.isfile(wf):
        try:
            c = json.load(open(wf))
            old_head, old_rows = c["head"], c["rows"]
            if not (isinstance(old_head, str) and all(isinstance(r, list) and len(r) == 4 for r in old_rows)):
                raise ValueError("malformed walk cache")
            for r in old_rows:
                dt.datetime.fromisoformat(r[1])
            subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", old_head, head], check=True, stderr=subprocess.DEVNULL)
        except Exception:
            old_head, old_rows = None, []
    rng = (old_head + "..HEAD") if old_head else "HEAD"
    walk = git("log", "--follow", "--no-abbrev", "--format=C %H %aI", "--raw", rng, "--", reg) if old_head != head else ""
    fam = None
    for l in walk.splitlines():
        if l.startswith("C "):
            _, h, t = l.split()
        elif l.startswith(":"):
            meta, _, paths = l.partition("\t")
            f = meta.split()
            nb = f[3] if len(f) >= 5 else None
            pth = paths.split("\t")[-1].strip()
            if fam is not None and not fam.fullmatch(pth):
                continue
            rows.append((h, utc(dt.datetime.fromisoformat(t)), pth, nb if nb and set(nb) != {"0"} else None))
    rows = rows + [tuple([r[0], utc(dt.datetime.fromisoformat(r[1])), r[2], r[3]]) for r in old_rows]
    if wf:
        try:
            tmp = wf + ".%d.tmp" % os.getpid(); json.dump({"head": head, "rows": [[r[0], r[1].isoformat(), r[2], r[3]] for r in rows]}, open(tmp, "w")); os.replace(tmp, wf)
        except Exception:
            pass
    rows.reverse()
    seq, firstdone = {}, {}
    for h, t, p, nb in rows:
        pairs = states_at(git, h, p, nb)
        if pairs is None:
            continue
        for n, s in pairs:
            q = seq.setdefault(n, [])
            if not q or q[-1][0] != s:
                q.append((s, t))
            if s == "Done":
                firstdone.setdefault(n, t)
    cur = Graph().parse(current or (repo.rstrip("/") + "/" + reg), format="turtle")
    cls = {k: [] for k in ("future_finish", "two_values", "finish_not_after_start", "midnight", "under_2_min")}
    for i in set(cur.subjects(B.hasState, None)):
        n = str(i).split("#")[-1]
        S = [utc(x.toPython()) for x in cur.objects(i, B.startedAt) if hasattr(x.toPython(), "tzinfo")]
        F = [utc(x.toPython()) for x in cur.objects(i, B.finishedAt) if hasattr(x.toPython(), "tzinfo")]
        if len(set(S)) > 1 or len(set(F)) > 1:
            cls["two_values"].append(n)
        if not S or not F:
            continue
        s, f = min(S), max(F)
        if n in firstdone and f > firstdone[n]:
            cls["future_finish"].append(n)
            MEASURED[n] = (firstdone[n].strftime("%Y-%m-%dT%H:%M:%SZ"), f.strftime("%Y-%m-%dT%H:%M:%SZ"))
        if f <= s:
            cls["finish_not_after_start"].append(n)
        elif (f - s).total_seconds() < 120:
            cls["under_2_min"].append(n)
        if s.time() == dt.time(0) or f.time() == dt.time(0):
            cls["midnight"].append(n)
    paths = Counter(tuple(x[0] for x in v) for v in seq.values())
    return cls, paths
def read_ledger(path, stem):
    rows = {}
    for ln in open(path, encoding="utf-8"):
        if not ln.strip() or ln.startswith("#"):
            continue
        c = ln.rstrip("\n").split("\t")
        if len(c) >= 7 and c[0] == stem and c[6].strip():
            rows[c[1]] = (c[2], c[3])
    return rows
def main(argv):
    strict = "--strict" in argv
    led = None
    if "--ledger" in argv:
        i = argv.index("--ledger"); led = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    a = [x for x in argv if x != "--strict"]
    if len(a) < 2:
        print(__doc__); return 1
    cls, paths = trace(a[0], a[1], a[2] if len(a) > 2 else None)
    stale = []
    if led:
        stem = re.sub(r"_v\d+_\d+_\d+\.ttl$", "", os.path.basename(a[1]))
        rows = read_ledger(led, stem)
        explained = [n for n in cls["future_finish"] if rows.get(n) == MEASURED.get(n)]
        stale = sorted(n for n in rows if n not in explained)
        cls["future_finish"] = [n for n in cls["future_finish"] if n not in explained]
        cls["explained_by_ledger"] = explained
        cls["stale_ledger_rows"] = stale
    for k, v in cls.items():
        print(f"{k}: {len(v)}", sorted(v)[:12])
    print("state paths seen in commits:")
    for p, c in paths.most_common():
        print(" ", c, "x", " -> ".join(p))
    bad = len(cls["future_finish"]) + len(cls["two_values"]) + len(stale) + (len(cls["finish_not_after_start"]) + len(cls["under_2_min"]) if strict else 0)
    print("VERDICT:", "PASS" if not bad else "FAIL")
    return 2 if bad else 0
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
