#!/usr/bin/env python3
"""backlog_gate_digest v1.1.0 -- a gate log reduced to what a reader must see (G195).

A release gate log runs to hundreds of lines of passing checks. This prints the verdict lines, every section that failed with its first failing lines, and the three
slowest sections from the timing sidecar when it exists -- usually under fifteen lines. Nothing is hidden: the log path is printed for the full text.

v1.1.0 (Lineage 30, review of box 1): more failure words are seen (FAILURE, REFUSE, ABORT, ERROR, Traceback, NEW FAILURE, NOT PASS); the gate's own closing line (RELEASE GATE:) is the authority when it exists, so a failing closing line is never read as a pass; a log with a Traceback is shown even when the last verdict passes.

Usage: backlog_gate_digest.py GATE_LOG
Exit 0 only when the gate's own closing line passes (full or light) and no failure line is shown; 1 otherwise (a log with no closing line is 1). A failing check is recognised by the words listed in FAILWORD and by a VERDICT line that says FAIL; a VERDICT line that says NON-CONFORMANT is not counted, because the negative fixtures print it by design, so a failure that prints only that, or only a count, is read from the closing line. The pending-version drift failure is shown with a note and the exit stays 1."""
import os, re, sys
FAILWORD = re.compile(r"\b(FAIL|FAILED|FAILURE|REFUSE|REFUSED|ABORT|ABORTED|VIOLATION|NON-CONFORMANT|ERROR|Traceback|NOT PASS)\b|NEW FAILURE|FileNotFoundError")
def main(argv):
    if not argv:
        print(__doc__); return 2
    log = argv[0]
    lines = open(log, encoding="utf-8", errors="replace").read().splitlines()
    out, section, shown = [], "", {}
    verdicts = [l.strip() for l in lines if re.match(r"\s*(RELEASE GATE\b|VERDICT\b)", l)]
    for l in lines:
        if l.startswith("== "):
            section = l.strip("= ").strip()
        elif l.strip() in verdicts:
            if re.match(r"\s*VERDICT\b", l) and re.search(r"\bFAIL\b", l) and "NON-CONFORMANT" not in l:
                shown.setdefault(section, []).append(l.strip()[:220])      # a failing verdict line of a check is a failure; a negative fixture's NON-CONFORMANT is not
            continue
        elif FAILWORD.search(l) and not re.search(r"(FAILED|declaration FAILED)\s*:\s*0\b|self-proof|fails\b|FAIL on", l, re.I):
            shown.setdefault(section, []).append(l.strip()[:220])
    for sec, ls in shown.items():
        out.append("FAIL in: %s" % (sec or "(before the first section)"))
        out += ["    " + x for x in ls[:4]] + (["    ... %d more" % (len(ls) - 4)] if len(ls) > 4 else [])
    side = log + ".timing.tsv"
    if os.path.exists(side):
        rows = []
        for l in open(side):
            c = l.rstrip("\n").split("\t")
            try: rows.append((float(c[0]), c[1]))
            except Exception: pass
        out.append("slowest: " + "; ".join("%ds %s" % (s, n[:40]) for s, n in sorted(rows, reverse=True)[:3]))
    closing = [v for v in verdicts if v.startswith("RELEASE GATE")]
    last = (closing or verdicts or ["no verdict line"])[-1]
    out.append("last verdict: %s" % last[:200])
    out.append("full log: %s" % log)
    print("\n".join(out))
    passing = bool(closing) and "PASS" in last and "FAIL" not in last and "NOT PASS" not in last     # only the gate's own closing line passes a log; a truncated log has none
    if bool(closing) and last.startswith("RELEASE GATE: FAIL") and len(shown) == 1 and all(k.startswith("Distribution-drift gate") for k in shown):
        print("note: only the drift check failed, as it does for every version not yet published (the release tool tolerates exactly that); the exit stays 1")
    return 0 if passing and not shown else 1
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
