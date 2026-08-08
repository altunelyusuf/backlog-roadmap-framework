#!/usr/bin/env bash
# backlog_gate v1.1.9 — four-gate release check for the Backlog & Roadmap
# Semantic Framework. Nothing about the package's state is trusted until all
# four pass, and the SHACL gate refuses to certify anything until it has just
# demonstrated, in this run, that it can fail a known-bad register.
#
#   Gate 0  MANIFEST self-verify   every shipped file hashes as recorded
#   Gate P  Turtle parse           every shipped Turtle file parses
#   Gate K  version identity       versionInfo == versionIRI == filename token
#   Gate R  SHACL reconcile        Done => verified evidence, 0 violations
#   +       coverage gate          >= 80% of primary-source concepts (BP-D31)
#   +       doc-coverage gate      every TBox class named in the standard document
#
# Usage: backlog_gate_v1_1_9.sh [REGISTER.ttl ...]

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG="$(dirname "$HERE")"
VALIDATE="$HERE/backlog_validate_v1_3_0.py"
COVERAGE="$HERE/backlog_coverage_gate_v1_1_1.py"
DOCGATE="$(ls "$HERE"/backlog_doc_coverage_gate_v*.py | sort -V | tail -1)"
# fixtures resolved by pattern, not pinned filename: a fixture version bump
# must never silently disable the self-proof that guards every other gate.
POS="$(ls "$HERE"/fixtures/fixture_positive_v*.ttl | sort -V | tail -1)"
NEG="$(ls "$HERE"/fixtures/fixture_negative_v*.ttl | sort -V | tail -1)"
ADV="$(ls "$HERE"/fixtures/fixture_adversarial_random_v*.ttl | sort -V | tail -1)"
[ -f "$POS" ] && [ -f "$NEG" ] || { echo "GATE ABORT: self-proof fixtures not found"; exit 3; }
FAILED=0

echo "== Gate 0 — MANIFEST self-verify =="
python3 - "$PKG" <<'PY'
import hashlib, os, re, sys
root = sys.argv[1]
ok = bad = miss = 0
path = os.path.join(root, "MANIFEST_SHA256.txt")
if not os.path.exists(path):
    print("  no MANIFEST_SHA256.txt present (working tree, not a release bundle)"); sys.exit(0)
for line in open(path):
    m = re.match(r'^([0-9a-f]{64})\s+(.+?)\s+\(\d+b\)$', line.strip())
    if not m: continue
    h, rel = m.groups()
    full = os.path.join(root, rel)
    if not os.path.exists(full): miss += 1; print("  MISSING", rel); continue
    d = hashlib.sha256(open(full, "rb").read()).hexdigest()
    ok += d == h
    if d != h: bad += 1; print("  MISMATCH", rel)
print("  %d OK, %d mismatched, %d missing" % (ok, bad, miss))
sys.exit(1 if (bad or miss) else 0)
PY
[ $? -ne 0 ] && { echo "Gate 0 FAILED"; FAILED=1; }

echo
echo "== Gate P — Turtle parse =="
python3 - "$PKG" <<'PY'
import glob, os, sys
from rdflib import Graph
root = sys.argv[1]; bad = 0; n = 0
for f in sorted(glob.glob(os.path.join(root, "0*", "**", "*.ttl"), recursive=True)):
    n += 1
    try: Graph().parse(f, format="turtle")
    except Exception as e: bad += 1; print("  PARSE FAIL %s: %s" % (os.path.basename(f), str(e)[:90]))
print("  %d Turtle files, %d parse failures" % (n, bad))
sys.exit(1 if bad else 0)
PY
[ $? -ne 0 ] && { echo "Gate P FAILED"; FAILED=1; }

echo
echo "== Gate K — version identity =="
python3 "$VALIDATE" --gate-k | tail -1
python3 "$VALIDATE" --gate-k >/dev/null 2>&1 || { echo "Gate K FAILED"; FAILED=1; }

echo
echo "== Gate R — SHACL reconcile (self-proof first) =="
python3 "$VALIDATE" "$POS" | grep -E '^results|^VERDICT'
python3 "$VALIDATE" "$POS" >/dev/null 2>&1 || { echo "  ABORT: positive fixture failed — the suite is broken, not the register."; exit 3; }
python3 "$VALIDATE" "$NEG" | grep -E '^results|^advisory|^ +[0-9]+ x \[|^VERDICT'
if python3 "$VALIDATE" "$NEG" >/dev/null 2>&1; then
  echo "  ABORT: negative fixture passed — the suite is decorative and certifies nothing."; exit 3
fi
python3 "$VALIDATE" "$ADV" | grep -E '^results|^VERDICT'
if python3 "$VALIDATE" "$ADV" >/dev/null 2>&1; then
  echo "  ABORT: the adversarial random register passed. The suite admits a backlog whose"
  echo "  success cannot be told from its failure, which is the defect this fixture exists to catch."; exit 3
fi
echo "  self-proof: the suite passes known-good, fails known-bad, and rejects the adversarial"
echo "  random register — it discriminates on form AND on falsifiability."

echo
echo "== Coverage gate — primary-source concepts (BP-D31) =="
python3 "$COVERAGE" | grep -E '^coverage|^VERDICT'
python3 "$COVERAGE" >/dev/null 2>&1 || { echo "Coverage gate FAILED"; FAILED=1; }

echo
echo "== Self-proof of the register path — the plumbing, not the shapes =="
# The suite self-proof above invokes the validator directly; the register path
# formats its output. A defect in the formatting layer therefore escaped it once
# already. This runs the known-bad fixture through the EXACT register path and
# requires it to fail.
PROBE_OUT="$(python3 "$VALIDATE" "$NEG")"; PROBE_STATUS=$?
printf '%s\n' "$PROBE_OUT" | grep -E '^results' | sed 's/^/  /'
if [ "$PROBE_STATUS" -eq 0 ]; then
  echo "  ABORT: the register path reported success for the known-bad fixture."
  echo "  The gate cannot fail a failing register, so it certifies nothing."
  exit 3
fi
echo "  register path returns non-zero on known-bad input — the verdict survives formatting."

echo
echo "== Fixture-coverage gate — every shipped fixture is exercised =="
# A fixture no gate runs drifts silently. The R3 disagreement fixture sat
# shipped and unvalidated for several releases and accumulated six violations
# from constraints added meanwhile; nothing noticed, because nothing ran it.
UNRUN=0
for FX in "$HERE"/fixtures/*.ttl; do
  BASE="$(basename "$FX")"
  case "$BASE" in
    *negative*|*adversarial*) EXPECT=fail ;;
    *) EXPECT=pass ;;
  esac
  if python3 "$VALIDATE" "$FX" >/dev/null 2>&1; then GOT=pass; else GOT=fail; fi
  if [ "$GOT" != "$EXPECT" ]; then
    echo "  $BASE: expected $EXPECT, got $GOT"; UNRUN=1
  fi
done
if [ "$UNRUN" -eq 0 ]; then
  echo "  every shipped fixture validates as its name declares it should."
else
  echo "  Fixture-coverage gate FAILED"; FAILED=1
fi

echo
echo "== Determinism gate — same register in, same answer out =="
# A report that answers the same question differently on identical input is
# unreproducible in the sense this package refuses everywhere else. Measured
# before the fix: six equally-scored items, five fresh runs, five different
# answers. Fresh interpreters, because the cause is per-process hash seeding.
TIEFX="$(ls "$HERE"/fixtures/fixture_item_tie_v*.ttl 2>/dev/null | sort -V | tail -1 || true)"
RPT="$(ls "$HERE"/backlog_roadmap_report_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$TIEFX" ] && [ -n "$RPT" ]; then
  FIRST=""; STABLE=1
  for _i in 1 2 3 4 5; do
    OUT="$(python3 "$RPT" "$TIEFX" 2>/dev/null | sed -n '/== 1\. NEXT/,+1p' | tail -1)"
    [ -z "$FIRST" ] && FIRST="$OUT"
    [ "$OUT" = "$FIRST" ] || STABLE=0
  done
  if [ "$STABLE" -eq 1 ]; then
    echo "  5 fresh runs over a 6-way score tie agree:$FIRST"
  else
    echo "  ABORT: the report gave different answers on identical input."
    FAILED=1
  fi
else
  echo "  NOT RUN — tie fixture or report tool not found. Not assumed to pass."
fi

echo
echo "== Distribution-drift gate — is the public copy current? =="
# Runs only when a published URL is supplied, and reports NOT RUN otherwise
# rather than passing: a check that degrades to success when it cannot run is
# the decorative gate this suite refuses. Set BACKLOG_PUBLIC_URL to enable.
DRIFT="$(ls "$HERE"/backlog_distribution_drift_check_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$DRIFT" ] && [ -n "${BACKLOG_PUBLIC_URL:-}" ]; then
  python3 "$DRIFT" "$PKG" "$BACKLOG_PUBLIC_URL" | grep -E '^governed|^published|^VERDICT|^  - '
  python3 "$DRIFT" "$PKG" "$BACKLOG_PUBLIC_URL" >/dev/null 2>&1 || { echo "Distribution-drift gate FAILED"; FAILED=1; }
else
  echo "  NOT RUN — set BACKLOG_PUBLIC_URL to the published distribution to enable."
  echo "  Not assumed to pass: an unchecked public copy is how v1.25.0 shipped with"
  echo "  the public copy left at v1.24.0."
fi

echo
echo "== Doc-coverage gate — does the standard still describe the subject? =="
python3 "$DOCGATE" | grep -E '^classes|^VERDICT'
python3 "$DOCGATE" >/dev/null 2>&1 || { echo "Doc-coverage gate FAILED"; FAILED=1; }

if [ "$#" -gt 0 ]; then
  echo
  echo "== Register under test =="
  # The verdict is taken from the validator itself, never from the tail of a
  # display pipeline. Introduced as a bug at v1.1.5: `cmd | grep` followed by
  # `$?` reads GREP's status, and grep almost always finds a header line to
  # print, so a register with real violations was reported PASS. Capturing the
  # status before formatting decouples the two permanently — PIPESTATUS would
  # also work but breaks silently the moment another stage is inserted.
  REG_OUT="$(python3 "$VALIDATE" "$@")"; REG_STATUS=$?
  printf '%s\n' "$REG_OUT" | grep -vE '^  \[(Warning|Info)'
  [ "$REG_STATUS" -ne 0 ] && FAILED=1
fi

echo
if [ "$FAILED" -eq 0 ]; then
  echo "RELEASE GATE: PASS — Gate 0, Gate P, Gate K, Gate R and the coverage gate all clear."
  exit 0
fi
echo "RELEASE GATE: FAIL — see the failing gate above; release blocked."
exit 1
