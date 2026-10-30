#!/usr/bin/env python3
"""backlog_flow_point_git_trace v1.1.0 -- compare every item's recorded start, finish and state with the commits that recorded them.

WHY. A commit time is the latest instant a change can have been made. A finish later than the commit that first recorded the item Done is impossible, and the data
alone cannot show it: the witness is the history of the register in the repository that holds it (the same kind of witness backlog_lineage_order_check reads).
Written from the comparison script of a consuming project's handover (2026-10-14); changes: instants without a zone are read as UTC (the original stopped on them),
the check is a gate with an exit code, and the classes are named.

CLASSES (per item): future_finish (a finish later than the commit that first recorded the item Done); two_values (more than one startedAt or finishedAt);
finish_not_after_start; under_2_min (a span below two minutes, a signal to explain, not an error); midnight (a flow point at exactly 00:00:00);
state paths seen in commits (how items moved through the states in the commits that recorded them).

Usage: backlog_flow_point_git_trace.py REPO REGISTER_PATH_IN_REPO [CURRENT_FILE] [--strict]
Exit 0 when no future_finish and no two_values (and, with --strict, no finish_not_after_start and no under_2_min); 2 otherwise; 1 on error. Reads only.
"""
import json, os, re, subprocess, sys, datetime as dt
from collections import Counter
from rdflib import Graph, Namespace
B = Namespace("http://example.org/backlog#")
def utc(x):
    return x if x.tzinfo else x.replace(tzinfo=dt.timezone.utc)
def states_at(git, h, p):
    """(item, state) pairs of the register in commit h, or None when it does not parse. v1.1.0: kept on disk by the blob's hash (a blob never changes), so a
    commit already read is not parsed again; v1.0.0 parsed the whole register at every commit of its history, 30 s of the gate."""
    d = os.environ.get("BACKLOG_VALIDATE_MEMO_DIR")
    f = None
    try:
        blob = git("rev-parse", f"{h}:{p}").strip()
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
def trace(repo, reg, current=None):
    git = lambda *a: subprocess.check_output(("git", "-C", repo) + a, stderr=subprocess.DEVNULL).decode()
    rows, h, t = [], None, None
    for l in git("log", "--follow", "--format=C %H %aI", "--name-only", "--", reg).splitlines():
        if l.startswith("C "):
            _, h, t = l.split()
        elif l.strip():
            rows.append((h, utc(dt.datetime.fromisoformat(t)), l.strip()))
    rows.reverse()
    seq, firstdone = {}, {}
    for h, t, p in rows:
        pairs = states_at(git, h, p)
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
        if f <= s:
            cls["finish_not_after_start"].append(n)
        elif (f - s).total_seconds() < 120:
            cls["under_2_min"].append(n)
        if s.time() == dt.time(0) or f.time() == dt.time(0):
            cls["midnight"].append(n)
    paths = Counter(tuple(x[0] for x in v) for v in seq.values())
    return cls, paths
def main(argv):
    strict = "--strict" in argv
    a = [x for x in argv if x != "--strict"]
    if len(a) < 2:
        print(__doc__); return 1
    cls, paths = trace(a[0], a[1], a[2] if len(a) > 2 else None)
    for k, v in cls.items():
        print(f"{k}: {len(v)}", sorted(v)[:12])
    print("state paths seen in commits:")
    for p, c in paths.most_common():
        print(" ", c, "x", " -> ".join(p))
    bad = len(cls["future_finish"]) + len(cls["two_values"]) + (len(cls["finish_not_after_start"]) + len(cls["under_2_min"]) if strict else 0)
    print("VERDICT:", "PASS" if not bad else "FAIL")
    return 2 if bad else 0
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
