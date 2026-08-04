#!/usr/bin/env python3
"""backlog_coverage_gate v1.1.1 — primary-source concept-coverage gate (BP-D31).

Intrinsic gates (parse, SHACL, manifest) measure whether the artifact is
internally sound. They cannot detect that it never covered the document it
claims to standardise: v1.0.0 of this framework passed every intrinsic gate
while the source document had not been read. This gate closes that blindness.

Method: the inventory enumerates concepts named by the source document, each
with a line range and one or more regex probes. A concept counts as
DEMONSTRATED only when EVERY probe matches somewhere in the framework's
shipped artifacts. A concept with no probes is not demonstrated by
construction, so silence never reads as coverage.

Threshold: 80% (BP-D31). Exit 0 at or above, 1 below.
"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
INVENTORY = sorted(glob.glob(os.path.join(PKG, "04-documentation", "source_concept_inventory_v*.json")))[-1]
THRESHOLD = 0.80
SCAN = ["01-ontologies/*.ttl", "02-shacl-safeguards/*.ttl", "03-tooling/*.py",
        "03-tooling/*.sh", "03-tooling/fixtures/*.ttl"]

def corpus():
    blobs = {}
    for pattern in SCAN:
        for path in sorted(glob.glob(os.path.join(PKG, pattern))):
            with open(path, encoding="utf-8") as fh:
                blobs[os.path.relpath(path, PKG)] = fh.read()
    return blobs

def main():
    inv = json.load(open(INVENTORY, encoding="utf-8"))
    blobs = corpus()
    demonstrated, missing = [], []
    for c in inv["concepts"]:
        probes = c.get("probes") or []
        hits = {}
        for p in probes:
            where = [f for f, text in blobs.items() if re.search(p, text)]
            hits[p] = where
        ok = bool(probes) and all(hits[p] for p in probes)
        (demonstrated if ok else missing).append((c, hits))

    total = len(inv["concepts"])
    n = len(demonstrated)
    pct = n / total if total else 0.0

    print("source      : %s (sha256 %s)" % (inv["source_document"], inv["source_sha256"][:16]))
    print("inventory   : %s (%d concepts)" % (os.path.basename(INVENTORY), total))
    print("scanned     : %d framework artifacts" % len(blobs))
    print("coverage    : %d/%d = %.1f%% (threshold %.0f%%, all probes must match)"
          % (n, total, pct * 100, THRESHOLD * 100))
    if missing:
        print("not demonstrated:")
        for c, hits in missing:
            unmatched = [p for p, w in hits.items() if not w] or ["<no probes defined>"]
            print("  %-4s %-62s lines %-8s missing probe: %s"
                  % (c["id"], c["name"][:62], c["lines"], unmatched[0]))
    verdict = "PASS" if pct >= THRESHOLD else "FAIL"
    print("VERDICT     : %s" % verdict)
    return 0 if pct >= THRESHOLD else 1

if __name__ == "__main__":
    sys.exit(main())
