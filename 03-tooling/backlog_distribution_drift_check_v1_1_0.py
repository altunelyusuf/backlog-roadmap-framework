#!/usr/bin/env python3
"""backlog_distribution_drift_check v1.0.0 — the public copy may not lag.

Exists because saying the risk out loud did not prevent it. Two turns after
writing "two copies of the same vocabulary will drift, and what does not exist
yet is a check that fails when they diverge", this package shipped v1.25.0 to
the governed repository and left the public distribution at v1.24.0 — so the
copy a stranger reads was missing exactly the constraints that release added.

A stated risk is not a control. This is the control.

WHAT IT CHECKS

  1. The public distribution's VERSION.txt equals the governed package's.
  2. Re-deriving the public copy from the governed package RIGHT NOW produces
     the same bytes as what is published — so a divergence introduced by hand
     is caught even when the versions agree.

Point 2 is the load-bearing one. A version equality check alone would pass a
public copy that someone edited in place, which is the failure mode that
matters most: an edit to a derived artifact has no upstream and is lost at the
next derivation, silently.

EXIT

  0  the public copy is current and byte-identical to a fresh derivation
  1  it lags, diverges, or could not be checked — and "could not be checked"
     is a failure, not a pass, because a check that degrades to success when it
     cannot run is the decorative gate this framework refuses.

USAGE

  backlog_distribution_drift_check_v1_0_0.py <governed-pkg> <public-clone-or-url>

If the second argument looks like a URL it is cloned to a temporary directory;
no credential is used or needed, because the distribution is public and a check
that required one would not be runnable by the people it protects.
"""

import os
import shutil
import subprocess
import sys
import tempfile

DERIVER = "make_public_distribution_v1_3_0.py"

# Files the derivation deliberately does not produce: they are authored for the
# public copy and live only there. Listed explicitly rather than ignored by
# pattern, so adding one is a decision someone makes and not a silent exception.
PUBLIC_ONLY = {"README.md", "DISTRIBUTION.md", "LICENSE", ".gitignore"}

# Regenerated per-run and never byte-stable across environments.
VOLATILE = {"MANIFEST_SHA256.txt", "RELEASE_METRICS.txt", "PUBLISH_RECORD.ttl"}


def tree(root):
    out = {}
    for dp, ds, fs in os.walk(root):
        ds[:] = [d for d in ds if d not in (".git", "__pycache__")]
        for f in fs:
            if f.endswith((".pyc", ".pyo")):
                continue
            rel = os.path.relpath(os.path.join(dp, f), root)
            out[rel] = open(os.path.join(dp, f), "rb").read()
    return out


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    governed, published = os.path.abspath(sys.argv[1]), sys.argv[2]
    tmp = tempfile.mkdtemp()
    failures = []

    try:
        if published.startswith("http"):
            r = subprocess.run(["git", "clone", "-q", "--depth", "1", published,
                                os.path.join(tmp, "pub")], capture_output=True, text=True)
            if r.returncode != 0:
                print("FAIL: could not clone %s\n%s" % (published, r.stderr.strip()))
                return 1
            pub = os.path.join(tmp, "pub")
        else:
            pub = os.path.abspath(published)

        gv = open(os.path.join(governed, "VERSION.txt")).read().strip()
        try:
            pv = open(os.path.join(pub, "VERSION.txt")).read().strip()
        except OSError:
            print("FAIL: the published copy has no VERSION.txt")
            return 1

        print("governed  : v%s  (%s)" % (gv, governed))
        print("published : v%s  (%s)" % (pv, published))

        if gv != pv:
            failures.append("the published copy is at v%s while the governed package is at v%s"
                            % (pv, gv))

        # re-derive and compare, which catches an in-place edit that versions cannot
        deriver = os.path.join(governed, "03-tooling", DERIVER)
        if not os.path.exists(deriver):
            deriver = os.path.join(os.path.dirname(governed), DERIVER)
        if not os.path.exists(deriver):
            print("FAIL: %s not found — cannot re-derive, so cannot check" % DERIVER)
            return 1

        fresh = os.path.join(tmp, "fresh")
        r = subprocess.run([sys.executable, deriver, governed, fresh],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("FAIL: derivation failed\n%s" % (r.stderr or r.stdout).strip()[:400])
            return 1

        a, b = tree(fresh), tree(pub)
        ignored = PUBLIC_ONLY | VOLATILE
        only_derived = sorted(set(a) - set(b) - ignored)
        only_published = sorted(set(b) - set(a) - ignored)
        differing = sorted(f for f in set(a) & set(b) if f not in ignored and a[f] != b[f])

        print("\nfiles: %d derived, %d published (%d authored-for-public and volatile files excluded)"
              % (len(a), len(b), len(ignored)))
        for label, items in (("missing from the published copy", only_derived),
                             ("present only in the published copy", only_published),
                             ("differing", differing)):
            print("  %-38s %d" % (label, len(items)))
            for f in items[:8]:
                print("      %s" % f)
        if only_derived or only_published or differing:
            failures.append("the published copy is not byte-identical to a fresh derivation")

        print("\nVERDICT   : %s" % ("PASS — the public copy is current and matches"
                                    if not failures else "FAIL"))
        for f in failures:
            print("  - %s" % f)
        if failures:
            print("\nRe-derive and push before releasing. A governed release that leaves the")
            print("public copy behind ships the hole it just closed to everyone reading the")
            print("public copy.")
        return 0 if not failures else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
