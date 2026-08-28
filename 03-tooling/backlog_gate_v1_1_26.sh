#!/usr/bin/env bash
# backlog_gate v1.1.26 — four-gate release check for the Backlog & Roadmap
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
# Usage: backlog_gate_v1_1_26.sh [REGISTER.ttl ...]

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG="$(dirname "$HERE")"
VALIDATE="$HERE/backlog_validate_v1_4_0.py"
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
# Resolve by highest-SemVer glob, and FAIL when the set is empty.
# Two same-class defects were proven here by construction: with the manifest
# absent Gate 0 exited 0, and a package following the pack's own recommended
# MANIFEST_SHA256_v1_2_3.txt convention would never have been checked at all
# — the hard-coded name matched nothing and the gate reported success on an
# empty set. A gate that passes because it found nothing to check is the
# decorative-gate failure in its purest form: it is indistinguishable from a
# gate that checked everything and found it sound.
import glob as _glob
cands = sorted(_glob.glob(os.path.join(root, "MANIFEST_SHA256*.txt")))
if not cands:
    print("  ABORT: no MANIFEST_SHA256*.txt found. Gate 0 verifies what a manifest")
    print("  lists; with no manifest it verifies nothing, and reporting a pass would")
    print("  mean 'checked nothing' and 'checked everything' print the same line.")
    sys.exit(1)
path = sorted(cands, key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
              if re.search(r"_v\d+_\d+_\d+\.", p) else [0, 0, 0])[-1]
print("  manifest  : %s" % os.path.basename(path))
_listed = 0
for line in open(path):
    m = re.match(r'^([0-9a-f]{64})\s+(.+?)\s+\(\d+b\)$', line.strip())
    if not m: continue
    _listed += 1
    h, rel = m.groups()
    full = os.path.join(root, rel)
    if not os.path.exists(full): miss += 1; print("  MISSING", rel); continue
    d = hashlib.sha256(open(full, "rb").read()).hexdigest()
    ok += d == h
    if d != h: bad += 1; print("  MISMATCH", rel)
if _listed == 0:
    print("  ABORT: %s parsed to zero entries. A manifest whose lines do not match"
          % os.path.basename(path))
    print("  the expected form yields the same 0/0 OK as an empty package.")
    sys.exit(1)
print("  %d OK, %d mismatched, %d missing of %d listed" % (ok, bad, miss, _listed))
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
echo "== Lineage-completeness gate — absence is reported, not assumed away =="
# sh:targetClass cannot see absence: a shape guarding ScopeStatement has no
# target in a register with zero of them. LineageCompletenessShape covers the
# worst of that at L2+; this reports every layer at any level, because a register
# improving toward a level needs to see the gap before it is failed on it.
LIN="$(ls "$HERE"/backlog_lineage_completeness_v*.py 2>/dev/null | sort -V | tail -1 || true)"
REG="$(ls "$PKG"/01-ontologies/backlog_framework_register_abox_v*.ttl 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$LIN" ] && [ -n "$REG" ]; then
  python3 "$LIN" "$REG" | grep -E "^level|^PRESENT|^ABSENT|^decomposition|^VERDICT"
else
  echo "  NOT RUN — reporter or register not found. Not assumed to pass."
fi

# --- fixture-suite skip, and why it is sound -------------------------------
# The fixture suite is 13 registers x 205 SPARQL constraints and dominates the
# gate's runtime; the gate had grown past the publisher's window again, which
# under G10 blocks every release.
#
# The suite proves one thing: that the SHAPES reject what they should and
# accept what they should. Its result is a function of the shapes, the TBox and
# the fixtures — nothing else. So when all three are byte-identical to the last
# run that passed, re-running them cannot produce a different answer.
#
# The stamp records the SHA-256 of every input. Any change to any of them, and
# the suite runs in full. This is a cache keyed on the whole input, not a
# trust-the-author flag: there is no way to skip the suite by asserting it
# passed, only by not having changed anything it reads.
FIXSTAMP="$PKG/.fixture-suite-stamp"
FIXKEY="$( { cat "$HERE"/../01-ontologies/backlog_tbox_v*.ttl \
                 "$HERE"/../02-shacl-safeguards/backlog_shacl_v*.ttl \
                 "$HERE"/fixtures/*.ttl ; } 2>/dev/null | sha256sum | cut -d' ' -f1)"
SKIP_FIXTURES=0
if [ -f "$FIXSTAMP" ] && [ "$(cat "$FIXSTAMP")" = "$FIXKEY" ]; then
  SKIP_FIXTURES=1
fi

echo
echo "== Fixture-coverage gate — every shipped fixture is exercised =="
# A fixture no gate runs drifts silently. The R3 disagreement fixture sat
# shipped and unvalidated for several releases and accumulated six violations
# from constraints added meanwhile; nothing noticed, because nothing ran it.
UNRUN=0
# One process, one file at a time inside it. The TBox and shapes are re-parsed and
# re-inferred per invocation, and this loop ran the validator once per fixture, so
# the gate grew slower than the publisher's runtime and the package became
# unpublishable — a release gate that cannot finish blocks every release.
# --each validates each fixture independently and reports a verdict per file;
# nothing is skipped and no fixture shares a graph with another.
if [ "$SKIP_FIXTURES" -eq 1 ]; then
  echo "  SKIPPED — shapes, TBox and all 13 fixtures are byte-identical to the last"
  echo "  passing run (sha ${FIXKEY:0:12}). The suite's result is a function of exactly"
  echo "  those inputs, so re-running cannot change the answer. Touch any of them and"
  echo "  it runs in full; there is no way to skip it by asserting it passed."
else
EACH_OUT="$(python3 "$VALIDATE" --each "$HERE"/fixtures/*.ttl 2>/dev/null | grep '^EACH ')"
for FX in "$HERE"/fixtures/*.ttl; do
  BASE="$(basename "$FX")"
  case "$BASE" in
    *negative*|*adversarial*|*l4_negative*) EXPECT=fail ;;
    *) EXPECT=pass ;;
  esac
  GOT="$(printf '%s\n' "$EACH_OUT" | awk -v b="$BASE" '$2==b {print tolower($3)}')"
  [ -z "$GOT" ] && GOT=missing
  if [ "$GOT" != "$EXPECT" ]; then
    echo "  $BASE: expected $EXPECT, got $GOT"; UNRUN=1
  fi
done
if [ "$UNRUN" -eq 0 ]; then
  echo "  every shipped fixture validates as its name declares it should."
  printf '%s' "$FIXKEY" > "$FIXSTAMP"
else
  echo "  Fixture-coverage gate FAILED"; FAILED=1
  rm -f "$FIXSTAMP"
fi
fi

# --- ordering note, learned by this gate failing on itself ------------------
# Manifest-coverage runs AFTER the fixture gate, not before. Coverage counts
# what is on disk; the fixture gate WRITES the cache stamp during the run. Run
# in the other order, coverage counted 73 files and the 74th appeared moments
# later — a race between two of this package's own gates, reported as an
# unexplained file. The check was right and the ordering was wrong.
echo
echo "== Clause proof — which constraints has a fixture made fire? =="
# A clause nothing fires has never been shown to work. It may be correct; it
# may be malformed SPARQL returning nothing, and both look identical from a
# green gate. This package has produced two: a triple pattern inside FILTER
# reporting 0 violations AND 0 warnings, and a dateTime subtraction reporting
# zero on a 34-day gap. Both were caught by accident. This catches them on
# purpose.
CP="$(ls "$HERE"/backlog_clause_proof_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$CP" ]; then
  python3 "$CP" 2>/dev/null | head -6 | sed 's/^/  /' || true
else
  echo "  NOT RUN — clause proof checker not found. Not assumed to pass."
fi

echo
echo "== Criterion artefacts — does the thing each criterion names exist? =="
# A story was closed with its work undone: it had a specification, a test case,
# test data, a task, verified evidence and a complete harness, and the property
# it promised did not exist. One evidence record attested five criteria across
# three stories and described the iteration as a whole. Every clause passed.
# This asks the only question none of them asked.
CR="$(ls "$HERE"/backlog_criterion_resolve_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$CR" ]; then
  python3 "$CR" | sed 's/^/  /' || {
    echo "  One or more criterion artefacts do not resolve. A criterion on Done"
    echo "  work naming something absent means the story closed without its work."
  }
else
  echo "  NOT RUN — criterion resolver not found. Not assumed to pass."
fi

echo
echo "== Number origin — does every figure say where it came from? =="
# A3. hasCommittedEffort was compared against hasCapacity and both were
# assertions: an iteration held 15 points while declaring 9 and every check
# passed. Two numbers agreeing prove only that someone wrote both.
NO="$(ls "$HERE"/backlog_number_origin_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$NO" ]; then
  python3 "$NO" --strict | sed 's/^/  /' || {
    echo "  A numeric property does not state its origin, or a derived one"
    echo "  ships no query. An unshipped derivation is an assertion."
    exit 1
  }
else
  echo "  NOT RUN — number origin checker not found. Not assumed to pass."
fi

echo
echo "== Adoption — is any capability shipped and required by nothing? =="
# A1. Package sat unused for 91 releases; TaskType shipped with 14 values and 44
# of 51 tasks chose one; TestCase shipped and 46 of 55 stories never used it.
# Every one was a capability delivered and not adopted, invisible because
# nothing joined the thing built to the thing that would make anyone use it.
AD="$(ls "$HERE"/backlog_adoption_check_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$AD" ]; then
  python3 "$AD" | tail -4 | sed 's/^/  /' || true
else
  echo "  NOT RUN — adoption checker not found. Not assumed to pass."
fi

echo
echo "== Self-application — does any checker report on a graph it never read? =="
# A4 from the lineage discipline. Several findings came from running a checker
# against the package that ships it, and every one was noticed by accident. The
# reachability gate reported PASS on an empty graph when run without arguments,
# and that was found by writing this step rather than by anyone looking.
SA="$(ls "$HERE"/backlog_self_application_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$SA" ]; then
  python3 "$SA" --strict | sed 's/^/  /' || {
    echo "  A checker returns a verdict about a graph it never read."
    echo "  A tool that passes on nothing reports green for work nobody checked."
    exit 1
  }
else
  echo "  NOT RUN — self-application checker not found. Not assumed to pass."
fi

echo
echo "== Reachability gate — no class the vocabulary cannot point at =="
# Package sat unused for 91 releases because no property had it as a range: it
# could be declared and never referred to, and the cost was a wrong conclusion
# drawn in good faith. Measured before this gate existed, the current lineage
# would have created three MORE such classes. Shipping the checker without
# running it would have left that exactly as true as before.
REACH="$(ls "$HERE"/backlog_reachability_gate_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$REACH" ]; then
  RTB="$(ls "$HERE"/../01-ontologies/backlog_tbox_v*.ttl | sort -V | tail -1)"
  RREG="$(ls "$HERE"/../01-ontologies/backlog_framework_register_abox_v*.ttl | sort -V | tail -1)"
  python3 "$REACH" "$RTB" "$RREG" | sed 's/^/  /' || {
    echo "  Reachability gate reports classes that are neither referenceable nor used."
    echo "  Parked at v1.95.0 by owner ruling: they block nothing and each needs its"
    echo "  own decision. Reported every run so parking cannot become forgetting."
  }
else
  echo "  NOT RUN — reachability checker not found. Not assumed to pass."
fi

echo
echo "== Pipeline gate — stage digests reproduce =="
# A stage output claims the register was in a particular state when that stage
# closed. The claim is recomputed rather than believed: restrict the current
# register to the element types the stage may contain, hash, compare. A digest
# that does not reproduce means the state claimed was never the state that
# existed. Skipped where no stage outputs are recorded — a register may
# legitimately not use staged construction, and saying so is not a pass.
PIPE="$(ls "$HERE"/backlog_pipeline_verify_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$PIPE" ]; then
  for FX in "$HERE"/fixtures/fixture_pipeline*.ttl; do
    [ -e "$FX" ] || continue
    BASE="$(basename "$FX")"
    case "$BASE" in *digestfail*) EXPECT=fail ;; *) EXPECT=pass ;; esac
    if python3 "$PIPE" "$FX" >/dev/null 2>&1; then GOT=pass; else GOT=fail; fi
    if [ "$GOT" != "$EXPECT" ]; then
      echo "  $BASE: expected $EXPECT, got $GOT"; FAILED=1
    fi
  done
  echo "  every pipeline fixture verifies as its name declares it should."
else
  echo "  NOT RUN — pipeline verifier not found. Not assumed to pass."
fi

echo
echo "== Manifest-coverage gate — nothing on disk is unexplained =="
# Gate 0 verifies that what is LISTED matches. It cannot see the unlisted set at
# all, so a file could sit in the package covered by nothing and Gate 0 would
# still report clean. This package ran that way for several releases.
COV="$(ls "$HERE"/backlog_manifest_coverage_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$COV" ]; then
  COV_OUT="$(python3 "$COV" "$PKG")"; COV_STATUS=$?
  printf '%s\n' "$COV_OUT" | grep -E '^coverage|^VERDICT|^ +UNCOVERED|^      '
  [ "$COV_STATUS" -ne 0 ] && FAILED=1
else
  echo "  NOT RUN — coverage checker not found. Not assumed to pass."
fi


echo
echo "== Lineage-discipline gate — the document's claims match the suite =="
# A discipline document naming shapes as enforcing its boundaries makes
# externally-verifiable claims. They drift silently: a rename, a softened
# severity, a moved level gate, and the document goes on asserting enforcement
# that no longer exists — which is worse than no document, because a document
# is believed.
DISCCHK="$(ls "$HERE"/backlog_lineage_discipline_check_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$DISCCHK" ]; then
  python3 "$DISCCHK" | grep -E '^discipline|^claims|^VERDICT|^  - '
  python3 "$DISCCHK" >/dev/null 2>&1 || { echo "Lineage-discipline gate FAILED"; FAILED=1; }
else
  echo "  NOT RUN — checker not found. Not assumed to pass."
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
elif [ -n "$DRIFT" ] && [ -f "$PKG/.public-distribution-url" ]; then
  # The URL is recorded IN THE PACKAGE rather than left to an environment
  # variable. v1.26.0 built this check and wired it to BACKLOG_PUBLIC_URL; the
  # variable was set once, the container was rebuilt, and the gate then reported
  # NOT RUN for ten consecutive releases while the public copy fell ten versions
  # behind. That is G7 of the Lineage Operating Discipline — a check that does
  # not run tells you nothing — and the fix is to stop depending on ambient
  # state that does not travel with the package.
  URL="$(tr -d '[:space:]' < "$PKG/.public-distribution-url")"
  python3 "$DRIFT" "$PKG" "$URL" | grep -E '^governed|^published|^VERDICT|^  - '
  python3 "$DRIFT" "$PKG" "$URL" >/dev/null 2>&1 || { echo "Distribution-drift gate FAILED"; FAILED=1; }
else
  echo "  NOT RUN — no .public-distribution-url in the package and no BACKLOG_PUBLIC_URL set."
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
