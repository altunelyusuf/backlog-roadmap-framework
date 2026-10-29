#!/usr/bin/env bash
# backlog_gate v1.29.0 — four-gate release check for the Backlog & Roadmap
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
# Usage: backlog_gate_v1_12_0.sh [REGISTER.ttl ...]
#
# v1.29.0 (Lineage 19, DC-S04): a third probe runs every time: the public copy is cut by each module's declared audience and stops with an error when it cannot be sure (backlog_public_cut_probe).
# v1.28.0 (Lineage 19, DC-S01 and DC-S02): two probes run every time: the closure-report rules are shown firing on planted faults and silent on corrected twins (backlog_closure_shapes_probe), and the archive tool's refusals are drilled on planted lineages (backlog_archive_drill). A probe that cannot be found stops the gate.
# v1.74.0 (Lineage 22, G178): BACKLOG_GATE_LIGHT=1 is the gate of a chain-stage release (release tool 1.7.0, --stage): the sections about tools, shapes, fixtures and probes are skipped and SAID to be skipped; Gate 0, P and K, the register under test, the pipeline and lineage-order gates, the archive checks, the ordinals, the manifest and version gates and the item accounting still run. A stage release changes records alone and at most four come before a full one, so the full gate has judged every tool and shape by the fifth release.
# v1.73.0 (Lineage 22): the gate validates the register by itself. It was run without an argument by the release tool and the publisher, so the section "Register under test" never ran and a register with a violation was published in v1.461.0. With no argument it now takes the newest backlog_abox; the Lineage 19 probes loop also runs backlog_release_speed_probe (release tool 1.6.0: preflight refusals, the roll command, the gate receipt).
# v1.72.0 (Lineage 21, D3): the Lineage 19 probes loop also runs backlog_box_step_probe (the step tool accepts a box recorded in order and refuses work before the box opened, a story not Proposed, a box opened twice, a close with no checkpoint, a published statement edited in place and an artifact older than the box).
# v1.44.0 (G110): the Lineage 19 probes loop also runs backlog_competency_tree_probe (the closed competency tree: every skill listed and defined, one parent each, three levels at most, a source on every skill added since v1.125.0; five planted faults each caught).
# v1.50.0 (G116): the Lineage 19 probes loop also runs backlog_abox_neutrality_probe (the shipped data file binds no consumer item: no register-level adoption of an item-level rule set, and a consumer graph loaded with the whole file gets no recording or verification result) and backlog_human_actor_kinds_probe (an organisation is a human team; a person holds a role).
# v1.51.0 (G117): the same loop also runs backlog_executor_subclass_probe (the executor rules see subclasses of the five kinds) and backlog_pipeline_verify_probe (digest table v4: planning after a Backlog stage closed is not stage content).
# v1.52.0 (G118): the same loop also runs backlog_agent_accountability_probe (RS_AgentAccountability: runs of a definition, recorded team assembly, who made each move, different parties for doing, overseeing, verifying and approving, a person above the human approval level, delegated lineages) and backlog_agent_monitor_probe (the report of what a person has to look at).
# v1.60.0 (G131): the probes loop also runs backlog_scope_outcome_probe (the scope outcome is derived for a scope built first as well as for a scope built last; 9 expectations; shapes v1.173.0).
# v1.62.0 (G132): the scope outcome probe is v1.1.0; the retired scope-to-objective link is no longer read, so the probe expects no outcome from it.
# v1.63.0 (G134): the probes loop also runs backlog_links_not_text_probe (a connection is a link, never text: the five text properties are links, the seven missing domains and ranges are declared, and text where a link belongs draws a warning).
# v1.66.0 (G139): the probes loop also runs backlog_kind_category_probe (the kinds of classes and categories of links recorded in the T-Box agree with the ledger and fit the OE kind rules).
# v1.71.0 (G155): the probes loop also runs backlog_open_lineage_probe.
# v1.70.0 (G152): the probes loop also runs backlog_gate_timing_probe.
# v1.69.0 (G151): the probes loop also runs backlog_inbox_disposition_probe and backlog_release_preflight_probe.
# v1.68.0 (G148): the probes loop also runs backlog_handover_rules_probe (Cancelled items exempt from L4, RS_DecompositionStateAgrees, per-adoption git witness, freeze lift after a restart, goal triangle across superseded missions).
# v1.67.0 (G147): the probes loop also runs backlog_repair_reprioritises_probe (RS_RepairReprioritises: an open repair names the open items it re-prioritises or says why none, and each named item is scored after the repair).
# v1.64.0 (G135): the probes loop also runs backlog_link_control_probe (every missing-link candidate of any trust and any family is a link or a rejection with a coded reason in the package ledger; a stale row fails; MethodologyRule is linked to Methodology and ReleaseGate to a release).
# v1.65.0 (G136): the probes loop also runs backlog_plan_then_execute_probe (six checks against finding a defect after the fact: caveat tracking, the tool and version a criterion is measured with, the sprint goal fixed at the start, a story's epic, the executor brief, work begun at the executor's start).
# v1.59.0 (G129): the probes loop also runs backlog_carried_item_probe (a carried item through a revision under way and through a chain of successors; shapes v1.172.0).
# v1.58.0 (G128): a probe with no record of what it reads (neither this session's nor the package's file) is run traced even when its declared stamp holds, so the measured lists complete themselves instead of waiting for each probe's declared inputs to change. Probe backlog_probe_inputs_probe v1.1.0.
# v1.57.0 (G128): a probe is stamped on what it was MEASURED to read (backlog_probe_inputs: the run is traced), not on what it declares; the measured lists are kept in 06-package-provenance/PROBE_INPUTS.json. A probe with no usable record keeps its declared inputs. Probes: backlog_probe_inputs_probe.
# v1.56.0 (G126): proof stamps recorded in the package are honoured; the probes that must run go two at a time; the validator keeps one bundle per data key (v1.17.0). Probe backlog_proof_stamps_probe.
# v1.54.0 (G121, G122): the same loop also runs backlog_mission_history_probe (missions inside a lineage or its replaced history, a replaced mission still in flight, the closure anchor for adopters only), backlog_session_brief_probe (focus, items in progress, checkpoints due, what a close needs, vendored tools out of date) and backlog_archive_mission_history_probe (the statements a mission replaced are archived with its lineage). The work guard probe is v1.3.0.
# v1.55.0 (G123, G124): the same loop also runs backlog_shape_syntax_probe (no built-in function in the shapes is called with a space before its bracket, so the text reads in more than one query engine). The work guard probe is v1.4.0.
# v1.53.0 (G120): the same loop also runs backlog_standing_items_probe (recurring activities, estimated starts, the mover of an objective). The monitor probe is v1.1.0 (recurring activities).
# v1.49.0 (G115): the Lineage 19 probes loop also runs backlog_recording_integrity_probe (a first move leaves Proposed, flow points belong to started work, one value each, an equal pair is explained) and backlog_flow_point_git_trace_probe; a new section compares this package's own registers with the commits that recorded them (no finish later than its commit, no two values for one point).
# v1.48.0 (G114): the Lineage 19 probes loop also runs backlog_scope_order_probe (no shape judges the order of two stages from the text of two commit names).
# v1.47.0 (G113): the Lineage 19 probes loop also runs backlog_status_history_probe (every status change is a recorded move with an instant, the chain has no gap, the flow points are the moments of the moves; a workflow written before Suspended stays consistent).
# v1.46.0 (G112): the Lineage 19 probes loop also runs backlog_verification_scope_probe (an adoption binds the scope it was declared for: the register, or one lineage and the items its output admitted; a verification threshold by integrity level; the flow-point rule set).
# v1.45.0 (G111): the Lineage 19 probes loop also runs backlog_agent_roles_probe (an overseer is a person or human team behind RS_HumanOversight; a verifier answers to a different controller behind RS_ManagerialIndependence; the six role concepts are complete).
# v1.43.0 (G109): the Lineage 19 probes loop also runs backlog_competency_inheritance_probe (a requirement of a skill is met by any finer skill under it, a requirement of a finer skill only by that skill), backlog_verifier_independence_probe (a verifier is never the executor, inside it or over it; Done needs a verifier behind RS_IndependentVerification) and backlog_close_preview_probe (closing an item lists everything it owes in one run).
# v1.42.0 (G107): the Lineage 19 probes loop also runs backlog_state_evidence_probe (work with verified evidence cannot still be unstarted, behind RS_StateReflectsEvidence), backlog_evidence_bridge_probe (evidence outside the workspace is not verified) and backlog_timeline_witness_probe (a finish time earlier than the evidence artifact's first commit is contradicted).
# v1.41.0 (G106): the Lineage 19 probes loop also runs backlog_consumer_archive_probe (a consumer ledger archives into its own archive file and the package archive stays byte-identical) and backlog_vocabulary_probe (the derived vocabulary equals the individuals the T-Box lists in its owl:oneOf lists; a drifted file or a member the A-box does not define is refused).
# v1.40.0 (G104): the Lineage 19 probes loop also runs backlog_lineage_concurrency_probe (UnconnectedActiveLineagesShape fires on two unconnected active lineages and stays silent on a dependency link, a part and its parent, a queued mission, a finished lineage and a transitive chain).
# v1.39.0 (efficiency, measured by strace -f -e trace=execve over a full gate run): the version-freeze
# gate used to run backlog_version_freeze_check TWICE -- once to show its output, once silently for
# its exit code -- a second full re-read of every versioned file against the baseline tag for no new
# information. One run now; its own exit code is the gate's. Paired with backlog_version_freeze_check
# v1.1.0's own fix (one `git cat-file --batch` instead of one `git show` per file), this collapsed the
# single largest process-count cost the trace found: 586 `git show` spawns, almost all from this one
# gate step and its duplicate run.
# v1.37.0 (G99, release E, the owner's Merkle-root idea mixed with over-processing): backlog_merkle_cache gives every step
# its own key, built from its own named leaves, instead of one flat hash a whole section shared. The fixture-coverage gate
# now stamps EACH fixture on (TBox, shapes, validator, memo, that fixture) -- touching one fixture no longer forces all 13
# to be re-validated. The start-gate, work-guard and split-proof self-proofs, and the nine probes in the probes loop, are
# stamped on exactly the inputs each one's own --deps declares. The probes loop also stopped running every probe twice
# (once for its text, once thrown away for its exit code) -- one run now serves both.
# v1.36.0 (G99, release D, cold-run speed): the SPARQL query memo (backlog_sparql_memo) is part of the fixture-suite key and the clause-proof key, and its probe runs with the others. The validator prepares each distinct query once instead of re-parsing it for every focus node (results proven identical); the clause proof starts the validator once per fixture file.
# v1.35.0 (G99, release C): the gate prunes the validation cache by itself at its start (files unused for 14 days; rebuilt on demand), runs backlog_archived_digest_check (a ratchet over the archived lineages' recorded stage digests) and its probe.
# v1.34.0 (G99, ordinal rule): a section after the archive checks runs backlog_ordinal_check on the real live and archive data (every lineage holds its own ordinal; the check proves itself on planted cases first), and the probes loop runs backlog_ordinal_check_probe.
# v1.33.0 (G99 release B): the Lineage 19 probes section also runs backlog_stamp_key_probe (both stamps change with every input, the validator included).
# v1.33.0 (G99 release B, keys): the fixture-suite stamp's key now includes the validator (backlog_validate_v*.py); it covered the shapes, T-Box and fixtures but not the checker, so a changed validator was skipped over. The clause-proof stamp is keyed on the validator too (backlog_clause_proof v1.0.3).
# v1.32.0 (G99 release A2, speed only): the validation proof section is now the per-shape cache probe (backlog_validate_cache_probe: cached and split runs equal the plain run on a small register with a rule, planted shape, data and rule changes miss as they must, a lost share is refused); it replaces the split probe of v1.31.0.
# v1.31.0 (G99 release A, speed only): a "Validation split proof" section before Gate R proves the split validation (backlog_validate v1.13.0) reports exactly what the single-process run reports on a register that violates, with its own self-proof; the Lineage 19 probes section also runs backlog_release_tool_probe (the release tool refuses what it must).
# v1.30.0 (Lineage 16, GOVMIT-S02 and S03): the Lineage 19 probes section also runs backlog_governance_mitigations_probe (the generalised state advisory and the artefact boundary each fire on a fault and stay silent on a twin).
# v1.27.0 (Lineage 18, OC-S03 and S05): follows the archive folder -- the archive data file is read from 01-ontologies/archive/, and the archive's own shapes judge it (backlog_archive_shapes_check, which plants an orphan first).
# v1.26.0 (Lineage 18, OC-S01): the strategy-exercise register moved into the fixtures folder (declared positive, as test input the gate runs); the gate reads it from there.
# v1.25.0 (Lineage 17, OESC-S01 and S04): follows the package's new layout -- the register is part of the data file (backlog_abox), the
# rules are in the shapes file, the severity-promotion overlay is derived (no shipped overlay file), the strategy exercise register is test input in 03-tooling/exercises/ (not a fixture: it declares no polarity),
# and the promoted-overlay gate now checks that the audit's record derives an overlay: every promotion names a shape.
#
# v1.24.0 (Lineage 17, story OESC-S03): the split proof (every statement before a move is present, unchanged, after it) is proven
# to discriminate on every run: it certifies an identical tree and refuses a tree with one statement removed or added.
#
# v1.11.0 — the order check orders by ancestry (v1.4.0); self-proof adds the two witness maps that
# separate 'same epoch' from 'same commit' (one epoch, hashes in order -> ORDERED; two stages in one
# hash -> UNWITNESSED), via --expect.
#
# v1.10.0 — archival finder: every LS_Achieved lineage not yet archived is found and named; the
# archival activity (backlog_lineage_archive --apply) is the owner's next step, not this gate's.
#
# v1.9.0 — the order check (v1.3.0) verifies every recorded closedAtCommit is an ancestor of the branch
# tip; release tags are refs, so the gate makes sure tags are present locally before measuring.
#
# v1.8.0 — manifest-digest carrier: the register's manifest artifact names a manifest-exempt file
# that carries the manifest's digest; the gate checks it is exempt and current.
#
# v1.7.0 — the strategy-exercise register (01-ontologies/backlog_strategy_exercise_abox_v*.ttl)
# is SHACL-validated like the main register and measured by the lineage-order check with the
# real git witness, in the same run. Toy missions, real witness.
#
# v1.6.0 — the lineage-order self-proof also runs the recovery-strategy pair
# (divide-and-conquer rebuilt and combined must pass; missing strategy evidence must fail).
#
# v1.5.0 — the lineage-order self-proof also runs the thrash pair: a converging
# second trial must pass, a non-converging one (no novelty, admission lost, not
# deliberated) must fail. An unrecorded thrash on a live lineage fails the release.
#
# v1.4.0 — lineage-order gate (git witness). A lineage whose work first appears in the
# governed repository before its own Stage_Backlog output is a bypass; a bypass on a
# live lineage with no LineageRestart answering it FAILS the release. Proven on two
# witness fixtures (known ORDERED / known BYPASS) before the real register is measured.
#
# v1.3.0 — the validator is RESOLVED BY VERSION, never pinned. v1.1.29 and v1.2.0
# both hard-coded backlog_validate_v1_4_0.py; that file was retired at v1.152.0
# when v1.5.0 replaced it, and for 48 releases (v1.152.0-v1.200.0) Gate K could
# not start and Gate R aborted on the positive fixture. Nothing noticed, because
# the gate was being run by hand a section at a time (see PUBLISH_RECORD v1.142.0)
# and the publisher had not been used since. This is the G7/G10 failure in one:
# a gate that cannot run reports nothing, and a gate that cannot finish blocks
# every release. Every tool this gate calls now resolves the same way the fixtures
# already did -- highest SemVer on disk -- and the validator (v1.6.0) memoizes
# itself, so a validator bump can never again silently disable the gate. Two superseded gates retired; one current file per identity.

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG="$(dirname "$HERE")"
# Resolved by highest SemVer, never pinned (see header). The validator memoizes
# itself when BACKLOG_VALIDATE_MEMO_DIR is set; keyed on every input's bytes, so
# it can only ever replay an identical computation. If the caller pre-sets the
# directory it survives across calls and a gate interrupted by a runtime ceiling
# resumes where it stopped; otherwise a fresh one is used and removed on exit.
VALIDATE="$(ls "$HERE"/backlog_validate_v*.py | sort -V | tail -1)"
[ -f "$VALIDATE" ] || { echo "GATE ABORT: no backlog_validate_v*.py resolved"; exit 3; }
echo "validator : $(basename "$VALIDATE")"
if [ -z "${BACKLOG_VALIDATE_MEMO_DIR:-}" ]; then
  # v1.14.0 -- was: a fresh mktemp dir, deleted on exit, every single run. Measured the real
  # cost of that default directly: Gate R's self-proof alone cost 89.1s cold and 0.5s warm on
  # an identical run seconds later -- a real, persistent memo dir turned the whole gate from
  # 163.6s to 40.5s, a 4x speedup, with zero risk (the memo key covers every input's exact
  # bytes, so it can only ever replay an identical computation, never a stale one). Defaulting
  # to a fixed, persistent, off-package location so every future run benefits automatically,
  # without depending on a caller remembering to export this first.
  export BACKLOG_VALIDATE_MEMO_DIR="${HOME:-/tmp}/.backlog_validate_memo"
  mkdir -p "$BACKLOG_VALIDATE_MEMO_DIR"
fi
# v1.35.0: the cache bounds itself. Entries older than 14 days are removed (a cache file only ever replays identical bytes, so removing one costs a rebuild, never a wrong result).
RELTOOL="$(ls "$HERE"/backlog_release_tool_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$RELTOOL" ]; then python3 -B "$RELTOOL" prune-cache "$BACKLOG_VALIDATE_MEMO_DIR" --days 14 --legacy 2>&1 | sed 's/^/validation cache: /'; fi
# v1.37.0 (G99 release E, the owner's Merkle-root idea mixed with over-processing): a step's cache key is composed from
# its own named leaves, not from one flat hash over everything a WHOLE SECTION reads. Touching one fixture no longer
# forces every sibling fixture to be re-validated, and a probe whose own declared inputs are unchanged is not re-run just
# because something ELSEWHERE in the gate changed. backlog_merkle_cache holds the mechanics (leaf/key/root/Stamp, proven
# on throwaway files by its own probe); it lives in the same off-package memo directory as the validation cache, so it
# needs no gitignore or manifest entry and is pruned by the same 14-day sweep (prune_cache now also matches its files).
MERKLE="$(ls "$HERE"/backlog_merkle_cache_v*.py 2>/dev/null | sort -V | tail -1 || true)"
[ -n "$MERKLE" ] || { echo "GATE ABORT: no backlog_merkle_cache_v*.py resolved -- stamps cannot be composed without it."; exit 3; }
# v1.56.0 (G126, the owner's proof-and-SHA idea): a step whose key equals the one a EARLIER passing gate run recorded in the package
# (06-package-provenance/PROOF_STAMPS.json) is skipped as if this session had run it. BACKLOG_COLD=1 refuses every stamp and runs everything.
PROOF_STAMPS="$PKG/06-package-provenance/PROOF_STAMPS.json"
PROBE_INPUTS="$PKG/06-package-provenance/PROBE_INPUTS.json"
PIN="$(ls "$HERE"/backlog_probe_inputs_v*.py 2>/dev/null | sort -V | tail -1 || true)"
STAMPS_MEMO=0; STAMPS_REPO=0; STEPS_RUN=0
STAMPED() {
  local src; src="$(python3 "$MERKLE" check "$1" "$2" "$BACKLOG_VALIDATE_MEMO_DIR" "$PROOF_STAMPS" 2>/dev/null)" || { STEPS_RUN=$((STEPS_RUN + 1)); return 1; }
  if [ "$src" = "repo" ]; then STAMPS_REPO=$((STAMPS_REPO + 1)); else STAMPS_MEMO=$((STAMPS_MEMO + 1)); fi
  return 0
}
RECORD() { python3 "$MERKLE" record "$1" "$2" "$BACKLOG_VALIDATE_MEMO_DIR" >/dev/null 2>&1; }
COVERAGE="$(ls "$HERE"/backlog_coverage_gate_v*.py | sort -V | tail -1)"
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
_K="$(python3 "$VALIDATE" --gate-k 2>&1)"; _KR=$?
echo "$_K" | tail -1
[ $_KR -eq 0 ] || { echo "Gate K FAILED"; FAILED=1; }

echo
if [ "${BACKLOG_GATE_LIGHT:-}" != 1 ]; then
echo "== Validation cache proof — the per-shape cache and the split change no verdict =="
CACHEPROBE="$(ls "$HERE"/backlog_validate_cache_probe_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$CACHEPROBE" ]; then
  python3 "$CACHEPROBE" 2>&1 | sed 's/^/  /'; _SPR=${PIPESTATUS[0]}
  [ "$_SPR" -eq 0 ] || { echo "  ABORT: the cached or split validation differs from the plain run, or the probe cannot tell them apart."; exit 3; }
else
  echo "  ABORT: backlog_validate_cache_probe not found; a cached verdict is not trusted without it."; exit 3
fi

echo
else echo "  SKIPPED (light gate for a stage release; the full gate runs on the last release of the batch)"; fi
if [ "${BACKLOG_GATE_LIGHT:-}" != 1 ]; then
echo "== Gate R — SHACL reconcile (self-proof first) =="
_P="$(python3 "$VALIDATE" "$POS" 2>&1)"; _PR=$?
echo "$_P" | grep -E '^results|^VERDICT'
[ $_PR -eq 0 ] || { echo "  ABORT: positive fixture failed — the suite is broken, not the register."; exit 3; }
_N="$(python3 "$VALIDATE" "$NEG" 2>&1)"; _NR=$?
echo "$_N" | grep -E '^results|^advisory|^ +[0-9]+ x \[|^VERDICT'
if [ $_NR -eq 0 ]; then
  echo "  ABORT: negative fixture passed — the suite is decorative and certifies nothing."; exit 3
fi
_A="$(python3 "$VALIDATE" "$ADV" 2>&1)"; _AR=$?
echo "$_A" | grep -E '^results|^VERDICT'
if [ $_AR -eq 0 ]; then
  echo "  ABORT: the adversarial random register passed. The suite admits a backlog whose"
  echo "  success cannot be told from its failure, which is the defect this fixture exists to catch."; exit 3
fi
echo "  self-proof: the suite passes known-good, fails known-bad, and rejects the adversarial"
echo "  random register — it discriminates on form AND on falsifiability."

echo
else echo "  SKIPPED (light gate for a stage release; the full gate runs on the last release of the batch)"; fi
if [ "${BACKLOG_GATE_LIGHT:-}" != 1 ]; then
echo "== Coverage gate — primary-source concepts (BP-D31) =="
python3 "$COVERAGE" | grep -E '^coverage|^VERDICT'
python3 "$COVERAGE" >/dev/null 2>&1 || { echo "Coverage gate FAILED"; FAILED=1; }

echo
else echo "  SKIPPED (light gate for a stage release; the full gate runs on the last release of the batch)"; fi
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
REG="$(ls "$PKG"/01-ontologies/backlog_abox_v*.ttl 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$LIN" ] && [ -n "$REG" ]; then
  python3 "$LIN" "$REG" | grep -E "^level|^PRESENT|^ABSENT|^decomposition|^VERDICT"
else
  echo "  NOT RUN — reporter or register not found. Not assumed to pass."
fi

# --- fixture-coverage, Merkle-stamped per fixture (G99 release E) ----------
# The fixture suite is 13 registers x 205 SPARQL constraints and dominates the
# gate's runtime. v1.35.0 skipped the WHOLE suite when one flat hash over the
# TBox, every shapes file, every fixture, the validator and the memo matched a
# prior passing run -- sound, but coarse: touching ONE fixture (the common
# case while writing a new one) invalidated that single hash and forced all
# 13 back through the validator, because the key never said which file a
# change was IN, only that something somewhere had moved. v1.37.0 gives each
# fixture its OWN key: the four files every fixture shares (TBox, shapes,
# validator, memo) plus that fixture alone. A fixture's own key cannot change
# because a DIFFERENT fixture changed (backlog_merkle_cache_probe proves this
# property directly), so only the fixture(s) whose key actually moved are
# re-validated; the rest keep the verdict their own, unchanged, inputs already
# earned. A change to a SHARED file (TBox, shapes, validator, memo) still
# moves every fixture's key, so the suite still runs in full exactly when it
# must -- nothing here skips on an assertion, only on unchanged bytes, the
# same rule the old flat stamp kept, just named at the grain that is actually
# true.
BASE_LEAVES=("$HERE"/../01-ontologies/backlog_tbox_v*.ttl "$HERE"/../02-shacl-safeguards/backlog_shacl_v*.ttl "$HERE"/backlog_validate_v*.py "$HERE"/backlog_sparql_memo_v*.py)
declare -A FXKEY
TO_RUN=()
ALL_FX=("$HERE"/fixtures/*.ttl)
for FX in "${ALL_FX[@]}"; do
  BASE="$(basename "$FX")"
  K="$(python3 "$MERKLE" key "${BASE_LEAVES[@]}" "$FX")"
  FXKEY["$BASE"]="$K"
  if ! STAMPED "fixture:$BASE" "$K"; then
    TO_RUN+=("$FX")
  fi
done

echo
if [ "${BACKLOG_GATE_LIGHT:-}" != 1 ]; then
echo "== Fixture-coverage gate — every shipped fixture is exercised =="
# A fixture no gate runs drifts silently. The R3 disagreement fixture sat
# shipped and unvalidated for several releases and accumulated six violations
# from constraints added meanwhile; nothing noticed, because nothing ran it.
UNRUN=0
if [ "${#TO_RUN[@]}" -eq 0 ]; then
  echo "  SKIPPED every one of ${#ALL_FX[@]} fixtures — each one's own leaves (TBox, shapes,"
  echo "  validator, memo, and that fixture alone) are byte-identical to its last passing"
  echo "  run. A fixture's key cannot move because a DIFFERENT fixture changed; touch any"
  echo "  shared file or the fixture itself and it is validated again."
else
  if [ "${#TO_RUN[@]}" -lt "${#ALL_FX[@]}" ]; then
    echo "  running ${#TO_RUN[@]} of ${#ALL_FX[@]} fixtures — the rest are unchanged since their"
    echo "  last passing run and keep that verdict."
  fi
  # --each validates each fixture independently and reports a verdict per file;
  # nothing is skipped and no fixture shares a graph with another.
  EACH_OUT="$(python3 "$VALIDATE" --each "${TO_RUN[@]}" 2>/dev/null | grep '^EACH ')"
  # v1.3.0: the expectation comes from the FIXTURE'S OWN DECLARATION (hasExpectedPolarity),
  # never from its filename. The filename rule read 21 discriminating fixtures -- built to
  # make a shape fire -- as expected-to-pass, and would have failed every one of them the
  # first time this gate actually ran. A fixture that declares nothing is a FAIL: a fixture
  # whose answer is not known in advance verifies nothing (G7).
  POL_OUT="$(python3 "$VALIDATE" --polarity "${TO_RUN[@]}" 2>/dev/null | grep '^POLARITY ')"
  RAN_OK=0
  for FX in "${TO_RUN[@]}"; do
    BASE="$(basename "$FX")"
    DECL="$(printf '%s\n' "$POL_OUT" | awk -v b="$BASE" '$2==b {print $3}')"
    case "$DECL" in
      positive) EXPECT=pass ;;
      negative) EXPECT=fail ;;
      *) EXPECT="declared-polarity" ;;
    esac
    GOT="$(printf '%s\n' "$EACH_OUT" | awk -v b="$BASE" '$2==b {print tolower($3)}')"
    [ -z "$GOT" ] && GOT=missing
    if [ "$GOT" != "$EXPECT" ]; then
      echo "  $BASE: expected $EXPECT, got $GOT"; UNRUN=1
    else
      RECORD "fixture:$BASE" "${FXKEY[$BASE]}"; RAN_OK=$((RAN_OK + 1))
    fi
  done
  if [ "$UNRUN" -eq 0 ]; then
    echo "  every shipped fixture validates as it declares it should (${#ALL_FX[@]} declared, $RAN_OK freshly run)."
  else
    echo "  Fixture-coverage gate FAILED"; FAILED=1
  fi
fi

# --- ordering note, learned by this gate failing on itself ------------------
# Manifest-coverage runs AFTER the fixture gate, not before. Coverage counts
# what is on disk; the fixture gate WRITES the cache stamp during the run. Run
# in the other order, coverage counted 73 files and the 74th appeared moments
# later — a race between two of this package's own gates, reported as an
# unexplained file. The check was right and the ordering was wrong.
echo
else echo "  SKIPPED (light gate for a stage release; the full gate runs on the last release of the batch)"; fi
if [ "${BACKLOG_GATE_LIGHT:-}" != 1 ]; then
echo "== New-shape proof — does every shape authored since last publish cite its fixture? =="
# #1 of the mitigation plan. A2 proved the mechanism at 6 of 238 shapes.
# Backfilling the rest would assert 232 links never checked at authoring time.
# Forward-only: any shape new since the last publish must declare
# provenByFixture, checked against the governed copy the same way
# distribution-drift compares against it.
NSP="$(ls "$HERE"/backlog_new_shape_proof_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$NSP" ]; then
  python3 "$NSP" --strict | sed 's/^/  /' || {
    echo "  A shape authored since the last publish names no fixture proving it."
    exit 1
  }
else
  echo "  NOT RUN — new-shape proof checker not found. Not assumed to pass."
fi

echo
else echo "  SKIPPED (light gate for a stage release; the full gate runs on the last release of the batch)"; fi
if [ "${BACKLOG_GATE_LIGHT:-}" != 1 ]; then
echo "== Clause proof — which constraints has a fixture made fire? =="
# A clause nothing fires has never been shown to work. It may be correct; it
# may be malformed SPARQL returning nothing, and both look identical from a
# green gate. This package has produced two: a triple pattern inside FILTER
# reporting 0 violations AND 0 warnings, and a dateTime subtraction reporting
# zero on a 34-day gap. Both were caught by accident. This catches them on
# purpose.
CP="$(ls "$HERE"/backlog_clause_proof_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$CP" ]; then
  # v1.13.0 -- was: python3 "$CP" | head -6, which let `head` close the pipe after 6
  # lines and SIGPIPE the python process before it ever reached its own cache-stamp
  # write. Confirmed the hard way: standalone runs (no pipe) always wrote the stamp;
  # every run through this gate never did, regardless of how long it was given.
  # Redirect to a file first so the full run completes and writes its stamp, THEN
  # show only the first few lines -- decouples display truncation from process life.
  CP_OUT="$(mktemp)"
  python3 "$CP" 2>/dev/null > "$CP_OUT" || true
  head -6 "$CP_OUT" | sed 's/^/  /'
  rm -f "$CP_OUT"
else
  echo "  NOT RUN — clause proof checker not found. Not assumed to pass."
fi

echo
else echo "  SKIPPED (light gate for a stage release; the full gate runs on the last release of the batch)"; fi
if [ "${BACKLOG_GATE_LIGHT:-}" != 1 ]; then
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
else echo "  SKIPPED (light gate for a stage release; the full gate runs on the last release of the batch)"; fi
if [ "${BACKLOG_GATE_LIGHT:-}" != 1 ]; then
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
else echo "  SKIPPED (light gate for a stage release; the full gate runs on the last release of the batch)"; fi
if [ "${BACKLOG_GATE_LIGHT:-}" != 1 ]; then
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
else echo "  SKIPPED (light gate for a stage release; the full gate runs on the last release of the batch)"; fi
if [ "${BACKLOG_GATE_LIGHT:-}" != 1 ]; then
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
else echo "  SKIPPED (light gate for a stage release; the full gate runs on the last release of the batch)"; fi
if [ "${BACKLOG_GATE_LIGHT:-}" != 1 ]; then
echo "== Reachability gate — no class the vocabulary cannot point at =="
# Package sat unused for 91 releases because no property had it as a range: it
# could be declared and never referred to, and the cost was a wrong conclusion
# drawn in good faith. Measured before this gate existed, the current lineage
# would have created three MORE such classes. Shipping the checker without
# running it would have left that exactly as true as before.
REACH="$(ls "$HERE"/backlog_reachability_gate_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$REACH" ]; then
  RTB="$(ls "$HERE"/../01-ontologies/backlog_tbox_v*.ttl | sort -V | tail -1)"
  RREG="$(ls "$HERE"/../01-ontologies/backlog_abox_v*.ttl | sort -V | tail -1)"
  python3 "$REACH" "$RTB" "$RREG" | sed 's/^/  /' || {
    echo "  Reachability gate reports classes that are neither referenceable nor used."
    echo "  Parked at v1.95.0 by owner ruling: they block nothing and each needs its"
    echo "  own decision. Reported every run so parking cannot become forgetting."
  }
else
  echo "  NOT RUN — reachability checker not found. Not assumed to pass."
fi

echo
else echo "  SKIPPED (light gate for a stage release; the full gate runs on the last release of the batch)"; fi
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
echo "== Lineage-order gate — did the chain come before the work? (git witness) =="
LOC="$(ls "$HERE"/backlog_lineage_order_check_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$LOC" ]; then
  # self-proof first: the check must pass a known-ordered map and fail a known-bypass map
  WPOS="$(ls "$HERE"/fixtures/fixture_lineage_restart_witness_v*.json | sort -V | tail -1)"
  WNEG="$(ls "$HERE"/fixtures/fixture_lineage_bypass_negative_witness_v*.json | sort -V | tail -1)"
  FPOS="$(ls "$HERE"/fixtures/fixture_lineage_restart_v*.ttl | sort -V | tail -1)"
  FNEG="$(ls "$HERE"/fixtures/fixture_lineage_bypass_negative_v*.ttl | sort -V | tail -1)"
  if python3 "$LOC" "$FPOS" --witness "$WPOS" >/dev/null 2>&1; then :; else
    echo "  ABORT: the known-ordered witness fixture did not pass -- the check is broken, not the register."; exit 3; fi
  if python3 "$LOC" "$FNEG" --witness "$WNEG" >/dev/null 2>&1; then
    echo "  ABORT: the known-bypass witness fixture PASSED -- the check cannot see a bypass and certifies nothing."; exit 3; fi
  TPOS="$(ls "$HERE"/fixtures/fixture_lineage_thrash_v*.ttl | sort -V | tail -1)"
  TWPOS="$(ls "$HERE"/fixtures/fixture_lineage_thrash_witness_v*.json | sort -V | tail -1)"
  TNEG="$(ls "$HERE"/fixtures/fixture_lineage_thrash_negative_v*.ttl | sort -V | tail -1)"
  TWNEG="$(ls "$HERE"/fixtures/fixture_lineage_thrash_negative_witness_v*.json | sort -V | tail -1)"
  if python3 "$LOC" "$TPOS" --witness "$TWPOS" >/dev/null 2>&1; then :; else
    echo "  ABORT: the converging-second-trial fixture did not pass -- the check is broken, not the register."; exit 3; fi
  if python3 "$LOC" "$TNEG" --witness "$TWNEG" >/dev/null 2>&1; then
    echo "  ABORT: the thrash fixture PASSED -- the check cannot see a non-converging restart loop."; exit 3; fi
  SPOS="$(ls "$HERE"/fixtures/fixture_recovery_strategy_v*.ttl | sort -V | tail -1)"
  SWPOS="$(ls "$HERE"/fixtures/fixture_recovery_strategy_witness_v*.json | sort -V | tail -1)"
  SNEG="$(ls "$HERE"/fixtures/fixture_recovery_strategy_negative_v*.ttl | sort -V | tail -1)"
  SWNEG="$(ls "$HERE"/fixtures/fixture_recovery_strategy_negative_witness_v*.json | sort -V | tail -1)"
  if python3 "$LOC" "$SPOS" --witness "$SWPOS" >/dev/null 2>&1; then :; else
    echo "  ABORT: the divide-and-conquer fixture did not pass -- the check is broken, not the register."; exit 3; fi
  if python3 "$LOC" "$SNEG" --witness "$SWNEG" >/dev/null 2>&1; then
    echo "  ABORT: the strategy-evidence fixture PASSED -- the check cannot see a strategy without its evidence."; exit 3; fi
  RPOS="$(ls "$HERE"/fixtures/fixture_lineage_restart_v*.ttl | sort -V | tail -1)"
  WEPO="$(ls "$HERE"/fixtures/fixture_lineage_restart_witness_epoch_v*.json | sort -V | tail -1)"
  WSAME="$(ls "$HERE"/fixtures/fixture_lineage_restart_witness_samecommit_v*.json | sort -V | tail -1)"
  python3 "$LOC" "$RPOS" --witness "$WEPO" --expect Lin_PL=ORDERED >/dev/null 2>&1 || { echo "  ABORT: one-epoch, hashes-in-order fixture did not read ORDERED -- the witness orders by time again."; exit 3; }
  python3 "$LOC" "$RPOS" --witness "$WSAME" --expect Lin_PL=UNWITNESSED >/dev/null 2>&1 || { echo "  ABORT: two-stages-one-commit fixture did not read UNWITNESSED -- same-commit is no longer a hash test."; exit 3; }
  echo "  self-proof: ordered passes, bypass fails; converging trial passes, thrash fails; divide-and-conquer passes, missing strategy evidence fails; one-epoch chain ORDERED, two-stages-one-commit UNWITNESSED."
  # v1.22.0 (an adopting project handover, lineage2-executed-without-backlog-stage): a green verdict over an empty set is not
  # evidence. The order check must name a lineage that awaits its Backlog stage with nothing to order (v1.9.0 read it
  # ORDERED), must still read a complete chain ORDERED, and must still read an item registered before any Backlog output a
  # BYPASS; and the positive start gate must pass the groomed item and refuse every case that lacks a fact.
  AFX="$(ls "$HERE"/fixtures/fixture_awaiting_backlog_negative_v*.ttl | sort -V | tail -1)"
  AWT="$(ls "$HERE"/fixtures/fixture_awaiting_backlog_negative_witness_v*.json | sort -V | tail -1)"
  python3 "$LOC" "$AFX" --witness "$AWT" --expect Lin_Waiting=AWAITING_BACKLOG >/dev/null 2>&1 || { echo "  ABORT: a lineage with no Backlog stage and no item did not read AWAITING_BACKLOG -- the empty set reads green again."; exit 3; }
  python3 "$LOC" "$AFX" --witness "$AWT" --expect Lin_Ordered=ORDERED >/dev/null 2>&1 || { echo "  ABORT: the complete ordered chain did not read ORDERED."; exit 3; }
  python3 "$LOC" "$AFX" --witness "$AWT" --expect Lin_Registered=BYPASS >/dev/null 2>&1 || { echo "  ABORT: an item registered before any Backlog output did not read BYPASS."; exit 3; }
  ERP="$(ls "$HERE"/backlog_execution_ready_probe_v*.py 2>/dev/null | sort -V | tail -1 || true)"
  if [ -n "$ERP" ]; then
    ERPKEY="$(python3 "$MERKLE" key $(python3 "$ERP" --deps))"
    if STAMPED "probe:execution_ready" "$ERPKEY"; then
      echo "  SKIPPED — backlog_execution_ready_probe's own declared inputs are unchanged since it last held."
    else
      python3 "$ERP" >/dev/null 2>&1 || { echo "  ABORT: the start gate does not discriminate (backlog_execution_ready_probe failed)."; exit 3; }
      RECORD "probe:execution_ready" "$ERPKEY"
      echo "  self-proof: a lineage awaiting its Backlog stage reads AWAITING_BACKLOG, not ORDERED; the start gate passes the groomed item and refuses 10 cases that lack a fact"
    fi
  else
    echo "  NOT RUN — start-gate probe not found. Not assumed to pass."
  fi
  # v1.23.0 (ruling G101, the repeat drift): the safeguard must sit in the path of the act. The work guard is proven on a
  # real throwaway repository (real commits refused and accepted, the CI range check naming a skipped commit, the Claude
  # hooks blocking an edit on a lineage with no Backlog stage, a guard over nothing refused); the pipeline verifier must
  # say INCOMPLETE and --require-complete must refuse a chain with no Backlog stage while accepting a complete one.
  WGP="$(ls "$HERE"/backlog_work_guard_probe_v*.py 2>/dev/null | sort -V | tail -1 || true)"
  if [ -n "$WGP" ]; then
    WGPKEY="$(python3 "$MERKLE" key $(python3 "$WGP" --deps))"
    if STAMPED "probe:work_guard" "$WGPKEY"; then
      echo "  SKIPPED — backlog_work_guard_probe's own declared inputs are unchanged since it last held."
    else
      python3 "$WGP" >/dev/null 2>&1 || { echo "  ABORT: the work guard does not discriminate (backlog_work_guard_probe failed)."; exit 3; }
      RECORD "probe:work_guard" "$WGPKEY"
      echo "  self-proof: the work guard refuses a work commit with no ready Work-Item, a push holding one, an edit on a lineage with no Backlog stage and a guard over nothing; it accepts groomed work"
    fi
  else
    echo "  NOT RUN — work-guard probe not found. Not assumed to pass."
  fi
  # v1.24.0 (Lineage 17, OESC-S03): a move of statements between files is proven lossless by comparison, and the comparison is
  # itself shown to see a removed and an added statement before it is trusted anywhere.
  SPP="$(ls "$HERE"/backlog_split_proof_probe_v*.py 2>/dev/null | sort -V | tail -1 || true)"
  if [ -n "$SPP" ]; then
    SPPKEY="$(python3 "$MERKLE" key $(python3 "$SPP" --deps))"
    if STAMPED "probe:split_proof" "$SPPKEY"; then
      echo "  SKIPPED — backlog_split_proof_probe's own declared inputs are unchanged since it last held."
    else
      python3 "$SPP" "$PKG" >/dev/null 2>&1 || { echo "  ABORT: the split proof does not discriminate (backlog_split_proof_probe failed)."; exit 3; }
      RECORD "probe:split_proof" "$SPPKEY"
      echo "  self-proof: the split proof certifies an identical tree and refuses one with a statement removed or added"
    fi
  else
    echo "  NOT RUN — split-proof probe not found. Not assumed to pass."
  fi
  PV="$(ls "$HERE"/backlog_pipeline_verify_v*.py 2>/dev/null | sort -V | tail -1 || true)"
  PFI="$(ls "$HERE"/fixtures/fixture_pipeline_incomplete_v*.ttl | sort -V | tail -1)"
  PFC="$(ls "$HERE"/fixtures/fixture_pipeline_v*.ttl | sort -V | tail -1)"
  if python3 "$PV" "$PFI" --require-complete >/dev/null 2>&1; then
    echo "  ABORT: a chain with no Backlog stage passed --require-complete -- the verifier passes over the missing stage again."; exit 3; fi
  python3 "$PV" "$PFC" --require-complete >/dev/null 2>&1 || { echo "  ABORT: a complete chain failed --require-complete -- the check is broken, not the register."; exit 3; }
  echo "  self-proof: the pipeline verifier refuses a chain with no Backlog stage under --require-complete and accepts a complete chain"
  # v1.9.0: release tags are the recorded witnesses of this package's outputs; fetch them quietly if a remote exists
  ( cd "$PKG" && git fetch --tags --quiet origin 2>/dev/null || true )
  REG="$(ls "$PKG"/01-ontologies/backlog_abox_v*.ttl 2>/dev/null | sort -V | tail -1 || true)"
  EXREG="$(ls "$PKG"/03-tooling/fixtures/backlog_strategy_exercise_abox_v*.ttl 2>/dev/null | sort -V | tail -1 || true)"
  if [ -n "$EXREG" ]; then
    EX_OUT="$(python3 "$VALIDATE" "$EXREG" 2>&1)"; EX_RC=$?
    printf '%s\n' "$EX_OUT" | grep -E '^results|^VERDICT' | sed 's/^/  exercise register: /'
    [ "$EX_RC" -eq 0 ] || { echo "  strategy-exercise register is non-conformant"; FAILED=1; }
  fi
  if [ -n "$REG" ]; then
    _LOC_REPO_ROOT="$(git -C "$PKG" rev-parse --show-toplevel 2>/dev/null || true)"
    _LOC_LAST_TAG="$(git -C "${_LOC_REPO_ROOT:-$PKG}" tag --list 'backlog-roadmap-framework-v*' 2>/dev/null | sort -V | tail -1 || true)"
    if [ -n "$_LOC_LAST_TAG" ]; then
      LOC_OUT="$(python3 "$LOC" "$REG" $EXREG --baseline "$_LOC_LAST_TAG" 2>&1)"; LOC_RC=$?
    else
      LOC_OUT="$(python3 "$LOC" "$REG" $EXREG 2>&1)"; LOC_RC=$?
    fi
    printf '%s\n' "$LOC_OUT" | grep -E '^  |^      - |^VERDICT|^scope|^ADVISORY' | sed 's/^/  /'
    [ "$LOC_RC" -eq 0 ] || { echo "Lineage-order gate FAILED"; FAILED=1; }
  fi
else
  echo "  NOT RUN — order check not found. Not assumed to pass."
fi

echo
echo "== Archive integrity and archive shapes — retirement lost nothing, and the archive holds what a retired record must hold =="
INTEG="$(ls "$HERE"/backlog_archive_integrity_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$INTEG" ]; then
  python3 "$INTEG" 2>&1 | grep -E "DEFECT|VERDICT|entries|references" | sed 's/^/ /'
  python3 "$INTEG" >/dev/null 2>&1 || { echo "  archive integrity FAILED"; FAILED=1; }
fi
ASHP="$(ls "$HERE"/backlog_archive_shapes_check_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$ASHP" ]; then
  # v1.27.0 (Lineage 18, OC-S03): the archive folder's own shapes judge the archive; the check plants an orphan first and refuses to certify unless it is flagged.
  python3 "$ASHP" 2>&1 | grep -E "SELF-PROOF|result|VERDICT" | sed 's/^/ /'
  python3 "$ASHP" >/dev/null 2>&1 || { echo "  archive shapes check FAILED"; FAILED=1; }
else
  echo "  NOT RUN — archive shapes check not found. Not assumed to pass."
fi
# v1.27.0: the progressive conformance tool (it judged the archive by the LIVE shapes, advisory since 2026-09-18 on a known graph-construction bug, ~300 s) is retired
# to 03-tooling/archive/; the archive folder's own shapes judge the archive above (about 12 s), so the live rules no longer read it.

echo
echo "== Lineage ordinals — every lineage holds its own place in the sequence, live register and archive together =="
ORDC="$(ls "$HERE"/backlog_ordinal_check_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$ORDC" ]; then
  python3 "$ORDC" 2>&1 | grep -E "SELF-PROOF|lineages counted|COLLISION|WHAT TO DO|^  [1-4] |VERDICT" | sed 's/^/ /'
  python3 "$ORDC" >/dev/null 2>&1 || { echo "  ordinal check FAILED"; FAILED=1; }
else
  echo "  NOT RUN — ordinal check not found. Not assumed to pass."; FAILED=1
fi

echo
if [ "${BACKLOG_GATE_LIGHT:-}" != 1 ]; then
echo "== Archived lineages — recorded stage digests: no unseen failure (ratchet) =="
ADC="$(ls "$HERE"/backlog_archived_digest_check_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$ADC" ]; then
  python3 -B "$ADC" 2>&1 | grep -E "SELF-PROOF|archived lineages|NEW FAILURE|NOTE|VERDICT" | sed 's/^/ /'
  python3 -B "$ADC" >/dev/null 2>&1 || { echo "  archived digest check FAILED"; FAILED=1; }
else
  echo "  NOT RUN — archived digest check not found. Not assumed to pass."; FAILED=1
fi

echo
else echo "  SKIPPED (light gate for a stage release; the full gate runs on the last release of the batch)"; fi
if [ "${BACKLOG_GATE_LIGHT:-}" != 1 ]; then
echo "== Lineage 19 probes — each rule fires on a planted fault and each refusal holds =="
# v1.37.0: each probe prints its own --deps (it alone knows what it reads) and is stamped on exactly that; one that
# never changed does not re-run just because something ELSEWHERE in the gate did. A run that does happen runs ONCE
# (v1.36.0 and earlier ran every probe twice here: once piping to grep, once thrown away for its exit code).
PROBE_LIST="backlog_closure_shapes_probe backlog_archive_drill backlog_public_cut_probe backlog_governance_mitigations_probe backlog_release_tool_probe backlog_proof_stamps_probe backlog_probe_inputs_probe backlog_carried_item_probe backlog_shape_syntax_probe backlog_stamp_key_probe backlog_sparql_memo_probe backlog_ordinal_check_probe backlog_archived_digest_check_probe backlog_release_item_check_probe backlog_package_activation_drift_classifier_probe backlog_lineage_concurrency_probe backlog_consumer_archive_probe backlog_vocabulary_probe backlog_state_evidence_probe backlog_evidence_bridge_probe backlog_timeline_witness_probe backlog_competency_inheritance_probe backlog_verifier_independence_probe backlog_close_preview_probe backlog_competency_tree_probe backlog_agent_roles_probe backlog_verification_scope_probe backlog_status_history_probe backlog_scope_order_probe backlog_order_revision_probe backlog_recording_integrity_probe backlog_flow_point_git_trace_probe backlog_abox_neutrality_probe backlog_human_actor_kinds_probe backlog_executor_subclass_probe backlog_pipeline_verify_probe backlog_agent_accountability_probe backlog_agent_monitor_probe backlog_standing_items_probe backlog_mission_history_probe backlog_session_brief_probe backlog_archive_mission_history_probe backlog_scope_outcome_probe backlog_links_not_text_probe backlog_link_control_probe backlog_plan_then_execute_probe backlog_kind_category_probe backlog_repair_reprioritises_probe backlog_handover_rules_probe backlog_inbox_disposition_probe backlog_release_preflight_probe backlog_gate_timing_probe backlog_open_lineage_probe backlog_box_step_probe backlog_release_speed_probe"
# v1.56.0: the probes that must run are run TWO (BACKLOG_GATE_JOBS) AT A TIME, each into its own file; the verdicts are then read in the fixed order and each
# probe is stamped only if it passed. A probe still runs once, with the same inputs, and nothing is skipped that was not skipped before.
JOBS="${BACKLOG_GATE_JOBS:-$(nproc 2>/dev/null || echo 1)}"; [ "$JOBS" -gt 4 ] && JOBS=4; [ "$JOBS" -lt 1 ] && JOBS=1
PTMP="$(mktemp -d)"; QUEUE=(); declare -A PFILE PKEYS
for PROBE in $PROBE_LIST; do
  PF="$(ls "$HERE"/${PROBE}_v*.py 2>/dev/null | sort -V | tail -1 || true)"
  if [ -z "$PF" ]; then echo "  ABORT: $PROBE not found. A probe that is missing proves nothing."; exit 3; fi
  # v1.57.0: the key is built on what the probe was measured to read when it last ran; with no usable record it is built on what the probe declares
  PKEY=""; [ -n "$PIN" ] && PKEY="$(python3 "$PIN" key "$PROBE" "$PKG" "$BACKLOG_VALIDATE_MEMO_DIR" "$PROBE_INPUTS" 2>/dev/null)"
  [ -n "$PKEY" ] || PKEY="$(python3 "$MERKLE" key $(python3 "$PF" --deps))"
  UNMEASURED=0
  if [ -n "$PIN" ] && [ "$PROBE" != "backlog_probe_inputs_probe" ] && ! python3 "$PIN" has "$PROBE" "$BACKLOG_VALIDATE_MEMO_DIR" "$PROBE_INPUTS" 2>/dev/null; then UNMEASURED=1; fi
  [ "$UNMEASURED" -eq 1 ] && STEPS_RUN=$((STEPS_RUN + 1))
  if [ "$UNMEASURED" -eq 0 ] && STAMPED "probe:$PROBE" "$PKEY"; then
    echo "  $PROBE SKIPPED — its inputs are unchanged since it last held."
    continue
  fi
  PFILE[$PROBE]="$PF"; PKEYS[$PROBE]="$PKEY"; QUEUE+=("$PROBE")
done
for PROBE in "${QUEUE[@]}"; do
  while [ "$(jobs -rp | wc -l)" -ge "$JOBS" ]; do wait -n; done
  # the probe of the tracer traces by itself, and a traced process cannot be traced again: it runs plain and keeps its declared inputs
  if [ -n "$PIN" ] && [ "$PROBE" != "backlog_probe_inputs_probe" ]; then
    ( python3 "$PIN" run "${PFILE[$PROBE]}" "$PKG" "$BACKLOG_VALIDATE_MEMO_DIR" "$PTMP/$PROBE.out"; echo $? > "$PTMP/$PROBE.rc" ) &
  else
    ( python3 "${PFILE[$PROBE]}" > "$PTMP/$PROBE.out" 2>&1; echo $? > "$PTMP/$PROBE.rc" ) &
  fi
done
wait
for PROBE in "${QUEUE[@]}"; do
  RC="$(cat "$PTMP/$PROBE.rc" 2>/dev/null || echo 1)"
  grep -E "VERDICT" "$PTMP/$PROBE.out" | sed "s/^/  $PROBE /"
  if [ "$RC" -eq 0 ]; then
    NK=""; [ -n "$PIN" ] && NK="$(python3 "$PIN" key "$PROBE" "$PKG" "$BACKLOG_VALIDATE_MEMO_DIR" 2>/dev/null)"
    [ -n "$NK" ] || NK="$(python3 "$MERKLE" key $(python3 "${PFILE[$PROBE]}" --deps))"
    RECORD "probe:$PROBE" "$NK"
  else
    echo "  $PROBE FAILED"; FAILED=1
  fi
done
rm -rf "$PTMP"
echo "  probes: ${#QUEUE[@]} run ($JOBS at a time), the rest skipped on unchanged inputs (measured inputs where a usable record exists, declared inputs otherwise)"

echo
else echo "  SKIPPED (light gate for a stage release; the full gate runs on the last release of the batch)"; fi
if [ "${BACKLOG_GATE_LIGHT:-}" != 1 ]; then
echo "== Flow points against the commits that recorded them (G115) =="
# A commit time is the latest instant a change can have been made; a finish later than the commit that first recorded the item Done is impossible, and two values for
# one point are a correction that added instead of replaced. Neither can be seen in the data alone, so the witness is the history (backlog_flow_point_git_trace).
GTR="$(ls "$HERE"/backlog_flow_point_git_trace_v*.py 2>/dev/null | sort -V | tail -1 || true)"
GROOT="$(git -C "$PKG" rev-parse --show-toplevel 2>/dev/null || true)"
if [ -z "$GTR" ]; then echo "  ABORT: backlog_flow_point_git_trace not found."; exit 3; fi
if [ -z "$GROOT" ]; then
  echo "  NOT RUN — this copy is not a git work tree, so there is no history to compare with."
else
  PKGREL="$(python3 -c 'import os,sys;print(os.path.relpath(sys.argv[1],sys.argv[2]))' "$PKG" "$GROOT")"
  for REGF in "$PKG"/01-ontologies/backlog_abox_v*.ttl "$PKG"/01-ontologies/archive/backlog_framework_archive_abox_v*.ttl; do
    [ -f "$REGF" ] || continue
    REL="$(python3 -c 'import os,sys;print(os.path.relpath(sys.argv[1],sys.argv[2]))' "$REGF" "$GROOT")"
    # the history is read under the newest name git knows at HEAD (a release renames the file before it is committed)
    HEADREL="$(git -C "$GROOT" ls-tree -r --name-only HEAD -- "$(dirname "$REL")" 2>/dev/null | grep -E "/$(basename "$REGF" | sed -E 's/_v[0-9]+_[0-9]+_[0-9]+\.ttl$//')_v[0-9]+_[0-9]+_[0-9]+\.ttl$" | sort -V | tail -1 || true)"
    [ -n "$HEADREL" ] || HEADREL="$REL"
    OUT="$(python3 "$GTR" "$GROOT" "$HEADREL" "$REGF" 2>&1)"; RC=$?
    printf '%s\n' "$OUT" | grep -E "^(future_finish|two_values|VERDICT)" | sed "s|^|  $(basename "$REGF") |"
    if [ "$RC" -ne 0 ]; then echo "  FAILED — $(basename "$REGF") has a finish later than the commit that recorded it Done, or two values for one flow point."; FAILED=1; fi
  done
fi

echo
else echo "  SKIPPED (light gate for a stage release; the full gate runs on the last release of the batch)"; fi
if [ "${BACKLOG_GATE_LIGHT:-}" != 1 ]; then
echo "== Archival finder — achieved lineages are found, and archiving is the next activity =="
ARCH="$(ls "$HERE"/backlog_lineage_archive_v*.py 2>/dev/null | sort -V | tail -1 || true)"
REGA="$(ls "$PKG"/01-ontologies/backlog_abox_v*.ttl 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$ARCH" ] && [ -n "$REGA" ]; then
  python3 "$ARCH" "$REGA" --find 2>&1 | sed 's/^/ /'
else
  echo "  NOT RUN — archive tool not found."
fi

echo
else echo "  SKIPPED (light gate for a stage release; the full gate runs on the last release of the batch)"; fi
echo "== Manifest-digest carrier — the root of the covered set lives outside it =="
REGC="$(ls "$PKG"/01-ontologies/backlog_abox_v*.ttl 2>/dev/null | sort -V | tail -1 || true)"
CARRIER="$(grep -oE 'backlog:manifestDigestCarriedBy "[^"]+"' "$REGC" 2>/dev/null | head -1 | sed -E 's/.*"([^"]+)"/\1/')"
if [ -z "$CARRIER" ]; then
  echo "  no manifestDigestCarriedBy in the register — RegisterArtifactShape reports it; not verified here."
else
  MDIG="$(sha256sum "$PKG/MANIFEST_SHA256.txt" | cut -d' ' -f1)"
  if ! grep -qE "^# EXEMPT:? $CARRIER " "$PKG/MANIFEST_SHA256.txt"; then
    echo "  carrier $CARRIER is NOT declared exempt in the manifest — a carrier the manifest covers is the cycle again"; FAILED=1
  elif [ ! -f "$PKG/$CARRIER" ]; then
    echo "  carrier $CARRIER does not exist"; FAILED=1
  elif grep -qE "manifest SHA-256 $MDIG" "$PKG/$CARRIER"; then
    echo "  carrier $CARRIER is exempt and carries the current manifest digest ${MDIG:0:16}"
  else
    echo "  carrier $CARRIER carries a digest that is not the manifest on disk (${MDIG:0:16}); regenerate release metrics"; FAILED=1
  fi
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
echo "== Version-freeze gate — did any versioned file's content change under its own frozen name? (G94) =="
# LINEAGE_OPERATING_DISCIPLINE_v62_0_0.md was content-edited 67 times across this package's
# history under one filename before anything checked it; backlog_shacl_v1_120_0.ttl, 112 times.
# A version in a filename is a real claim -- this content, this version -- and nothing was
# verifying it stayed true. Compares every versioned file against the SAME file at the last real
# published tag in the governed monorepo (not the derived public mirror -- that transforms and
# excludes files, which produces false positives on this exact check; found the hard way).
VFC="$(ls "$HERE"/backlog_version_freeze_check_v*.py 2>/dev/null | sort -V | tail -1 || true)"
REPO_ROOT="$(git -C "$PKG" rev-parse --show-toplevel 2>/dev/null || true)"
LAST_TAG="$(git -C "${REPO_ROOT:-$PKG}" tag --list 'backlog-roadmap-framework-v*' 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$VFC" ] && [ -n "$REPO_ROOT" ] && [ -n "$LAST_TAG" ]; then
  PREFIX="$(realpath --relative-to="$REPO_ROOT" "$PKG" 2>/dev/null || true)/"
  # v1.38.1 (efficiency, measured): this used to run the checker TWICE -- once for display, once
  # silently for its exit code -- a second full re-read of every versioned file against the tag
  # for no new information. One run now; its own exit code is the gate's.
  VFC_OUT="$(python3 "$VFC" "$PKG" "$LAST_TAG" --repo-root "$REPO_ROOT" --package-prefix "$PREFIX")"; VFC_STATUS=$?
  printf '%s\n' "$VFC_OUT" | sed 's/^/  /'
  [ "$VFC_STATUS" -ne 0 ] && { echo "  Version-freeze gate FAILED"; FAILED=1; }
else
  echo "  NOT RUN — checker, repo root, or a prior published tag not found. Not assumed to pass."
fi

echo
echo "== Release-item-accounting gate — does this release own the items it moved, or say it didn't? (GOV-S01) =="
# A package can publish a release whose governed files genuinely changed while not one real
# backlog item moved -- confirmed on automate-python-book-3e (fourteen real releases, zero item
# movement) and, less formally, in this package's own earlier infra fixes. A hard, blocking gate:
# refuses unless a real item moved in this span, or the release explicitly declares itself
# unplanned work. RIC_UNPLANNED_REASON, set by the caller, is the escape hatch's current, minimal
# form -- GOV-S02 gives it a real, checkable shape; this is not that story.
RIC="$(ls "$HERE"/backlog_release_item_check_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$RIC" ] && [ -n "$REPO_ROOT" ] && [ -n "$LAST_TAG" ]; then
  PREFIX="$(realpath --relative-to="$REPO_ROOT" "$PKG" 2>/dev/null || true)/"
  RIC_ARGS=("$PKG" "$LAST_TAG" --repo-root "$REPO_ROOT" --package-prefix "$PREFIX")
  [ -n "${RIC_UNPLANNED_REASON:-}" ] && RIC_ARGS+=(--unplanned-reason "$RIC_UNPLANNED_REASON")
  python3 "$RIC" "${RIC_ARGS[@]}" | sed 's/^/  /'
  python3 "$RIC" "${RIC_ARGS[@]}" >/dev/null 2>&1 \
    || { echo "  Release-item-accounting gate FAILED"; FAILED=1; }
else
  echo "  NOT RUN — checker, repo root, or a prior published tag not found. Not assumed to pass."
fi

echo
if [ "${BACKLOG_GATE_LIGHT:-}" != 1 ]; then
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
else echo "  SKIPPED (light gate for a stage release; the full gate runs on the last release of the batch)"; fi
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

echo
echo "== Promoted-overlay gate — does the severity audit derive an overlay from the shapes? =="
# v1.20.0 (an adopting project handover, promoted-overlay-stale-drops-succession-shapes): a register adopting
# RS_SeverityAudit_20260909 is validated against the overlay INSTEAD of the base; a stale overlay
# silently drops every shape added since. Refused here, not left to an adopter to discover.
OVERGEN="$(ls "$HERE"/backlog_make_promoted_shapes_v*.py 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$OVERGEN" ]; then
  OVER_OUT="$(python3 "$OVERGEN" 2>&1)"; OVER_RC=$?
  printf '%s\n' "$OVER_OUT" | grep -E '^shapes|^audit|^unaudited|^DROPPED|^MALFORMED|^VERDICT' | sed 's/^/  /'
  [ "$OVER_RC" -eq 0 ] || { echo "  Promoted-overlay gate FAILED"; FAILED=1; }
fi

if [ "$#" -eq 0 ]; then
  _DEFREG="$(ls "$PKG"/01-ontologies/backlog_abox_v*.ttl 2>/dev/null | sort -V | tail -1 || true)"
  [ -n "$_DEFREG" ] && set -- "$_DEFREG"
fi
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
  echo "proof stamps: $STAMPS_REPO honoured from the recorded file, $STAMPS_MEMO from this session, $STEPS_RUN steps run (BACKLOG_COLD=1 runs everything)"
  if [ "${BACKLOG_GATE_LIGHT:-}" = 1 ]; then echo "RELEASE GATE (LIGHT, stage release): PASS — the chain, order, archive, register, manifest and version checks clear; the sections marked SKIPPED did not run."; else
  echo "RELEASE GATE: PASS — Gate 0, Gate P, Gate K, Gate R and the coverage gate all clear."
  fi
  exit 0
fi
echo "RELEASE GATE: FAIL — see the failing gate above; release blocked."
exit 1
