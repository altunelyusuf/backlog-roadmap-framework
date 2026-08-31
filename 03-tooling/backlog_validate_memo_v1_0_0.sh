#!/usr/bin/env bash
# backlog_validate_memo v1.0.0 — pure memoization shim around backlog_validate.
#
# WHAT THIS IS: a cache, not a validator. It never parses RDF, never touches
# pyshacl, and never changes a single byte of what backlog_validate_v1_4_0.py
# computes. It exists because the release gate calls that script on the SAME
# (TBox, ABox, shapes, fixture) input combination from several independent
# sections (Gate R, the register-path self-proof, the fixture-coverage sweep,
# and clause-proof's own internal loop) -- 25 fixtures + the register produce
# ~48 validate() invocations across one gate run, of which only 26 are for
# genuinely distinct inputs. The other ~22 recompute an already-computed,
# deterministic, pure function.
#
# CORRECTNESS: cache key = sha256 of every argument's file content, plus the
# real validate script's own sha256 (a shapes/TBox/rules edit invalidates
# every cache entry automatically, since those file bytes flow into every
# key). Cache is a fresh temp directory per gate run (not persisted across
# runs, not shared across packages) -- it cannot go stale between sessions
# because it does not outlive one.
#
# USAGE: identical to backlog_validate_v1_4_0.py -- this is a drop-in
# replacement at the call site, not a different tool.

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REAL="$HERE/backlog_validate_v1_4_0.py"
CACHE_DIR="${BACKLOG_VALIDATE_MEMO_DIR:-$(mktemp -d /tmp/backlog_validate_memo.XXXXXX)}"
mkdir -p "$CACHE_DIR"

# Build the cache key from: the real script's own bytes (so a tooling change
# invalidates everything), plus every CLI argument that is a real file's
# bytes, plus the literal argv (so --gate-k / --each / a different file list
# never collide).
KEY_INPUT="$(sha256sum "$REAL" | cut -d' ' -f1)"
for a in "$@"; do
  if [ -f "$a" ]; then
    KEY_INPUT="$KEY_INPUT $(sha256sum "$a" | cut -d' ' -f1)"
  else
    KEY_INPUT="$KEY_INPUT $a"
  fi
done
KEY="$(printf '%s' "$KEY_INPUT" | sha256sum | cut -d' ' -f1)"
CACHE_FILE="$CACHE_DIR/$KEY.out"
CACHE_RC="$CACHE_DIR/$KEY.rc"

if [ -f "$CACHE_FILE" ] && [ -f "$CACHE_RC" ]; then
  printf '%s\n' "$(cat "$CACHE_FILE")"
  exit "$(cat "$CACHE_RC")"
fi

OUT="$(python3 "$REAL" "$@" 2>&1)"
RC=$?
printf '%s' "$OUT" > "$CACHE_FILE"
printf '%s' "$RC" > "$CACHE_RC"
printf '%s\n' "$OUT"
exit "$RC"
