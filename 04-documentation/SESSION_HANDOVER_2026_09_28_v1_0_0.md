# Session Handover — `backlog-roadmap-framework`, 2026-09-28

Written at the owner's request to switch this package to a fresh session. The session that wrote it cannot push
release tags, so a new session must take over the package.

Everything below was re-checked on disk and against GitHub immediately before writing. Re-check it again; do not
take it on account.

## 1. First actions for the new session

1. **Run the bootstrap** (`BOOTSTRAP_v1_3_0`) with `OE_SESSION=brsf-session`.
   - Attach `the maintainer/Ontologies` to the session **from the start**, the way the parallel sessions are started.
   - In this session the repository was attached partway through. Commit pushes then worked, but every tag push was
     refused with HTTP 403 by the session's network gateway, before the request reached GitHub.
   - The same token and the same bootstrap method were tried twice, including a fresh bootstrap run at 21:39. The
     parallel `rdodi-ecosystem` session pushed its own tags the same day, so tag pushes are possible where the
     session is set up that way.
2. **Ceremony.** The governing discipline is the highest `oe-method/04-documentation/OE_Operating_Discipline_v*.md`,
   as the owner's instruction says; it was `v2_12_1`, sha `ee2052c9a5b1`.
   - The bootstrap's own step 4 resolves `oe-pack/04-documentation`, which still holds an older copy (`v2_12_0`,
     sha `d60bce059095`).
   - Lineage discipline: highest `backlog-roadmap-framework/04-documentation/LINEAGE_OPERATING_DISCIPLINE_v*.md`;
     it was `v70_0_0`, sha `7860dc89f9eb`.
3. **Push the missing release tags**, annotated, one per published commit:

   | Tag | Commit |
   |---|---|
   | `backlog-roadmap-framework-v1.326.0` | `02e1c81` |
   | `backlog-roadmap-framework-v1.327.0` | `4fbacd5` |
   | `backlog-roadmap-framework-v1.328.0` | `8b26e4c` |
   | `backlog-roadmap-framework-v1.328.1` | the commit that published this document, found by `git log -1 --format=%h -- backlog-roadmap-framework/04-documentation/SESSION_HANDOVER_2026_09_28_v1_0_0.md` |

   Verify with `git ls-remote --tags origin 'backlog-roadmap-framework-v1.32*'`.
   - Why it matters: the gate's version-freeze, new-shape-proof and release-item checks resolve the last existing
     tag. Until these exist they count from `v1.325.0`, so every release since has needed an `**Unplanned work:**`
     line explaining the longer span.
   - Once the tags exist, the next release needs that line only if it is itself unplanned, which handover
     processing is.
4. **Sweep the inboxes:**
   - `backlog-roadmap-framework/07-handover-inbox/pending/`: empty at handover;
   - `oe-pack/07-handover-inbox/pending/`, for items addressed to this package;
   - PIB's `09-handover-inbox/pending/`, public repository `the maintainer/pib`.

## 2. State at handover

- **Version:** v1.328.1. Governed copy in the monorepo; public copy at `the maintainer/backlog-roadmap-framework`,
  where the drift check was PASS at v1.328.0.
- **Current files:**
  - TBox `backlog_tbox_v1_116_0.ttl`
  - shapes `backlog_shacl_v1_144_0.ttl`
  - severity-audit overlay `backlog_shacl_promoted_v1_14_0.ttl`, CURRENT
  - rules `backlog_rules_v1_8_0.ttl`
  - standard `BACKLOG_ROADMAP_FRAMEWORK_STANDARD_v1_112_0.md`
  - severity audit `SEVERITY_AUDIT_2026_09_09_v1_2_0.md`
  - lesson deposit `backlog_framework_lesson_deposit_v2_6_0.ttl`
  - changelog `CHANGELOG_v1_255_0.md`, append-only
- **Release gate:** PASS at v1.328.0 (all 22 fixtures validate as declared). Publisher dry run and publish both
  passed; only the tag push failed.

## 3. This session's releases (2026-09-28)

| Version | What | Handover |
|---|---|---|
| v1.326.0 | A slipped milestone is settled only by a recorded decision (asserted Withdrawn with an outcome rationale), never by the outcome rule R10b derives | an adopting project, milestone-outcome exemption; closed both sides |
| v1.327.0 | An advisory obligation can be met or explained at the stage that owes it: `describesItem` binds from the Backlog stage; an explained waiver silences an advisory; the unmet-advisory constraint split into its own Warning shape; `owesKind` honoured | an adopting project, Goal-stage use-case diagram; closed both sides |
| v1.328.0 | Conformance goals counted per lineage (bound from the Goal stage until closure); `GoalOrigin` (Carried / Repair / New) with `goalAnswersGap`; a later bounded finding is a further succession record | an adopting project, two handovers; **answered, closure not yet received** |
| v1.328.1 | This handover document; OEE's disposition of two lessons logged | none |

**Outgoing to OEE:** both lessons were accepted in oe-pack v20.89.0.
- L-cand-G became **L-124**: an exemption must not read what a rule in the same run derives.
- L-cand-H **extended L-36**: severity grades the shape, not the constraint.

OEE noted that one proposal cited a fixture by its full versioned filename, which was renamed before they read it.
Cite fixtures by stem (L-123).

## 4. Open items and known conditions

- **an adopting project closure on v1.328.0** is outstanding. Expect it, plus possibly:
  - successions for bounded post-closure findings;
  - a check that the predecessor's conformance goal names its lineage.
- **Known, pre-existing, not blocking:**
  - The package's own register fails `backlog_pipeline_verify` (digests recorded before per-lineage scoping). The
    gate runs only the pipeline fixtures.
  - The clause proof lists declared proof cases that did not fire: shapes declared with no case name, and cases the
    90-second per-fixture timeout cannot reach in the large negative fixture.
    - `AdoptionConformanceGoalShape`'s case was repointed at v1.328.0 to one that isolates it.
    - The rest are unchanged.
- **Bootstrap discrepancy** (§1, step 2): the bootstrap resolves the discipline from `oe-pack`, not `oe-method`.
  This is the operator's file, so it is reported to the owner, not changed here.

## 5. Owner rules this session worked under

These are as the owner stated them in conversation. Where a rule is also written into the discipline, the register
or the standard, **the written form governs**; verify against it.

- **Process handovers without being asked.** Decide from existing rules; do not ask the owner when a rule already
  covers the case.
- **G90's criterion:** a detected non-compliance is a Violation; a possibility with a probability is a Warning.
- **Generalizable lessons go to OEE without asking.** They go as proposals in `oe-pack/07-handover-inbox/pending/`,
  duplicate-screened first.
- **Revival needs a reason and evidence.**
  - The reason is improper processing, unfinished work or a non-conformant result.
  - Small changes go to a change request or a maintenance task.
  - Closed work stays closed and committed.
- **Unfinished work is never closed.** Out-scope it first, then close complete; a successor picks it up under the
  same Mission.
  - Unfinished packages are dissolved, not carried.
- **Bugs are mitigated immediately**, not held behind design work.
- **Historical records are never rewritten**, only appended: changelogs, published responses, git history,
  amendments to audits.
- **Never force-push** (L-112).
- **Always run the publisher's dry run first.**
- **Fetch and check freshness before every write.** Parallel sessions push to the same monorepo; this package
  writes only its own directory and its own outgoing proposals.
- **Style:** minimal output, continuous execution, human labels before identifiers.
