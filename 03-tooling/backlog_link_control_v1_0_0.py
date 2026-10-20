#!/usr/bin/env python3
"""backlog_link_control v1.0.0 -- every missing-link candidate has a recorded disposition (G135).

The OE missing-links check (oe_link_discovery) finds, in three families, relations that are stated, used or implied but not carried as a link:
  syntactic  SYN-1 text names another thing, SYN-2 a term is used but declared nowhere;
  semantic   SEM-1 / SEM-2 a property without a domain or a range;
  temporal   TEM-1 text says one thing supersedes another, TEM-2 a change note names a version the prior-version chain lacks.
It counts only the candidates of high trust against a ratchet. The rest were listed and, in practice, handled case by case. This tool closes that.

Rule: a candidate, of ANY trust and ANY family, is resolved in exactly one of two ways:
  1 the link is made (the candidate then no longer exists), or
  2 it is rejected in the package ledger (03-tooling/link_decisions_v*.tsv: set, family, from, to, reason), the reason starting with a coded category:
    [carried-by-path] [negation] [positional] [rationale-only] [register-pointer] [stale-text] [wrong-sense] [word-coincidence]
A candidate that is neither is UNDECIDED and fails. A ledger row that no longer matches a candidate is STALE and fails (the link was made, or the text went), so the ledger cannot rot.
The OE baseline and decisions ledger are the OE discipline's; this ledger is the package's own and never edits them.
Where the OE tool is not beside the package (a public copy), the check says SKIPPED and exits 0.

Usage: backlog_link_control.py [--root REPO_ROOT] [--package NAME] [--ledger FILE]
Exit 0 all decided (or skipped), 1 undecided or stale, 2 refused (a ledger row without a coded reason, or the OE tool failed)."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
CODES = ("carried-by-path", "negation", "positional", "rationale-only", "register-pointer", "stale-text", "wrong-sense", "word-coincidence")
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]


class Refused(Exception):
    pass


def find_oe(root):
    d = os.environ.get("BRSF_PUBLISHER_DIR") or os.path.join(root, "repo-tooling")
    c = sorted(glob.glob(os.path.join(d, "oe_link_discovery_v*.py")), key=sv)
    c = [x for x in c if "_test_" not in x]
    return c[-1] if c else None


def read_ledger(path):
    rows = {}
    for n, ln in enumerate(open(path, encoding="utf-8"), 1):
        if not ln.strip() or ln.startswith("#"):
            continue
        f = ln.rstrip("\n").split("\t")
        if f[0] == "set":
            continue
        if len(f) < 5 or not f[4].strip():
            raise Refused("ledger line %d: a rejection needs a reason" % n)
        if not re.match(r"\[(%s)\] \S" % "|".join(CODES), f[4].strip()):
            raise Refused("ledger line %d: the reason must start with a coded category, one of %s" % (n, ", ".join(CODES)))
        rows[(f[0], f[1], f[2], f[3])] = f[4].strip()
    return rows


def candidates(root, package, oe):
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "c.tsv")
        r = subprocess.run([sys.executable, "-B", oe, root, "--only", package, "--candidates", out], capture_output=True, text=True)
        if r.returncode == 2 or not os.path.exists(out):
            raise Refused("the OE link discovery did not run: " + (r.stderr or r.stdout).strip()[-200:])
        rows = [l.rstrip("\n").split("\t") for l in open(out, encoding="utf-8")][1:]
    return {(x[0], x[1], x[4], x[5]): (x[2], x[3], x[6]) for x in rows}


def control(root, package, ledger, oe):
    """-> (undecided, stale, total, rejected) -- undecided and stale are lists of printable lines"""
    cand = candidates(root, package, oe)
    led = read_ledger(ledger) if ledger and os.path.exists(ledger) else {}
    short = lambda u: u.rsplit("#", 1)[-1] if "#" in u else u.rsplit("/", 1)[-1]
    undecided = ["%-9s %-6s %-6s %s -> %s  [%s]" % (k[1], cand[k][0], cand[k][1], short(k[2]), short(k[3]), cand[k][2]) for k in sorted(cand) if k not in led]
    stale = ["%s -> %s (%s)" % (short(k[2]), short(k[3]), k[1]) for k in sorted(led) if k not in cand]
    return undecided, stale, len(cand), len([k for k in cand if k in led])


def main(argv):
    root = os.path.dirname(PKG); package = os.path.basename(PKG); ledger = None; i = 0
    while i < len(argv):
        if argv[i] == "--root": root = argv[i + 1]
        elif argv[i] == "--package": package = argv[i + 1]
        elif argv[i] == "--ledger": ledger = argv[i + 1]
        else:
            print("REFUSED: unknown argument " + argv[i]); return 2
        i += 2
    if ledger is None:
        g = sorted(glob.glob(os.path.join(HERE, "link_decisions_v*.tsv")), key=sv)
        ledger = g[-1] if g else None
    oe = find_oe(root)
    if not oe:
        print("SKIPPED: the OE link discovery is not beside this package (a public copy); the check runs where it is")
        return 0
    try:
        undecided, stale, total, rejected = control(root, package, ledger, oe)
    except Refused as e:
        print("REFUSED: " + str(e)); return 2
    print("candidates of every trust and family: %d; rejected with a coded reason: %d; undecided: %d; stale ledger rows: %d" % (total, rejected, len(undecided), len(stale)))
    for u in undecided: print("  UNDECIDED  " + u)
    for s in stale: print("  STALE      " + s)
    if undecided or stale:
        print("VERDICT: FAIL -- make the link, or reject it in the ledger with a coded reason; remove a stale row"); return 1
    print("VERDICT: PASS -- every candidate is a link or a recorded rejection")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
