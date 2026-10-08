# Root-cause analysis — G99 shipped four releases without the minimal Lineage it requires (v1.0.0)

Owner's instruction, 2026-10-08: "Why did you skip G99 requirements? How to prevent such things to happen again?"
Evidence base: this session's own four releases (v1.367.0-v1.370.0), the live register, the real saved gate logs
under `BRSF_WORK`, and a replay of the real release-time gate against the exact committed trees, all checked
directly in this turn. Anything not re-run is marked.

## What the evidence shows
- **G99's own text requires a minimal Lineage, not a Lineage-free WorkItem.** Re-read in full from
  `LINEAGE_OPERATING_DISCIPLINE_v72_0_0.md`: "What this ruling actually licenses is a minimal Lineage... Skipping
  the Lineage entirely is therefore not structurally available." This session's carried-over, pre-compaction
  summary of the same ruling instead read "maintenance task sets... may proceed without a lineage" -- the word
  "minimal" lost in compression. Four releases (v1.367.0-v1.370.0) were built and their own changelog entries
  written from that lossy summary, each one literally stating "Maintenance, no lineage (G99)" -- checked directly
  against `CHANGELOG_v1_255_0.md` lines 11263-11327, the exact wrong framing, in this session's own words, four
  times running.
- **This is not the first time.** `CHANGELOG_v1_255_0.md` line 10147-10149, an earlier session, 2026-09-22: "this
  session's own earlier application of G99 (the fixture-consolidation work) was disclosed in prose but never
  given the minimal, real WorkItem/Lineage structure G99 itself requires. Not retroactively fixed here." That gap
  was later closed by opening `L_OEStructureCleanup` (Lineage 17) through five dedicated releases (v1.333.0-
  v1.337.0), Mission through Backlog, each stage its own release, Mission affirmed by the owner directly
  (line 11010 ff.). The remedy this package already used once is on record; this session did not check for it
  before writing four more "no lineage" entries.
- **No register individual was ever created for this session's work.** The abox diff for all four releases,
  checked directly (`git diff <old-abox>:<new-abox>` per release): v1.367.0 added only two `OrdinalSharingDeclaration`
  individuals (an unrelated, pre-existing ordinal-collision fix); v1.368.0, v1.369.0, v1.370.0 touched no abox
  file at all. No `backlog:Story`, no `backlog:Lineage`, nothing for `belongsToLineage` to ever attach to. The
  existing, correct safeguard -- a `Story` with no `belongsToLineage` fails immediately, tested and confirmed in
  G99's own ruling text -- never had a subject to examine, because none was ever registered. A safeguard that
  checks a Story cannot catch work that was never turned into one.
- **A second, independent, more consequential defect, found only by asking why the register-side safeguard
  (GOV-S01, `backlog_release_item_check`) did not catch this either.** GOV-S01 exists specifically to refuse a
  release whose governed files changed with no item moved and no declared unplanned-work marker -- exactly this
  session's situation. Replayed directly against the real, committed v1.368.0 -> v1.369.0 span: `governed files
  changed: 0, PASS`. The real, saved gate log from that actual release (`/tmp/bk2/gate_1.369.0.log:329-333`) shows
  the identical line. The cause: the tool compared `{baseline_tag}..HEAD`, but this gate always runs from inside
  `backlog_release_tool` BEFORE the release it is gating is committed -- at that moment HEAD still equals the
  baseline, so the range is always empty. Reproduced on a real git worktree carrying v1.369.0's actual uncommitted
  edits against the v1.368.0 tag: the buggy form gives 0; the correct comparison gives 11 real governed files.
  Reproduced again on an unrelated earlier release's own saved log (`/tmp/gate_1.350.0.log`): the identical
  `governed files changed: 0, PASS`. **This gate has examined nothing and passed on every release in this
  package's history, not only this session's four** -- a defect older and wider than this session's own mistake.
  A second, compounding defect in the same method: `git diff` never lists a file that was never `git add`ed, so
  even comparing against the true working tree still misses every brand-new governed file a release introduces
  before the publisher stages it -- confirmed directly: of the 11 real governed files in that replay, 4 were
  modified-tracked (caught by dropping `..HEAD` alone) and 7 were new and untracked (still missed until unioned
  with `git ls-files --others --exclude-standard`).
- **The tool itself had no self-proof before this analysis.** `backlog_release_item_check` is a hard, release-
  blocking gate and had never once been run against a known-bad case to show it actually fires -- the same
  pattern G100 and G101 both name directly: "a gate shown only on good input proves nothing."

## Root causes (each tied to evidence and to what now answers it)
| # | Root cause | Answered by |
|---|---|---|
| 1 | A carried-over, pre-compaction summary compressed G99's ruling lossily, dropping the one word ("minimal") that makes the whole ruling non-optional; this session built on the summary instead of re-reading the source text before citing G99 four times. | The standing ceremony already requires re-reading the source discipline file every turn rather than trusting memory or a summary; this session's own failure to apply that to its own carried-over state, not just the owner's statements, is the first-order cause and has no new mechanical answer beyond continuing to honor the existing ceremony literally, including against inherited session state |
| 2 | No mechanical check ties a changelog's ruling citation to whether the register was actually touched; a `Story`'s own mandatory `belongsToLineage` shape can only examine a `Story` that exists. | Not fixed in this analysis (see "What is not claimed"); the honest gap is that admitting already-shipped work (recovery, below) is the only way to give that shape something to check, and nothing yet forces a release citing a reduced-ceremony ruling to create one |
| 3 | GOV-S01 (`backlog_release_item_check`) compared `{baseline}..HEAD`, a span that is always empty at the moment this gate runs, because the release it is meant to gate is never committed yet when it runs. A rule that exists only as a check still did not hold, because the check examined the wrong span -- not prose this time, but a check with nothing in its view. | `backlog_release_item_check_v1_5_0.py`: compares `{baseline_tag}` against the real working tree, not a commit range |
| 4 | The same tool only reads `git diff`, which never lists a file that was never `git add`ed -- a brand-new governed file (most of what a real release actually introduces) was invisible to it even after cause 3's fix. | `backlog_release_item_check_v1_5_0.py`: unions `git ls-files --others --exclude-standard` into the governed-file set |
| 5 | The gate had no self-proof, so a regression in causes 3/4 could ship silently and nothing would ever show it firing on a real bad case. | `backlog_release_item_check_probe_v1_0_0.py`: six cases, including the exact historical bug (a modified-uncommitted and a new-untracked governed file, both previously invisible) |
| 6 | This exact failure mode -- G99 work shipped, disclosed, not given its register structure -- happened once before (2026-09-22) and was fixed by precedent (open the lineage in dedicated stage releases) rather than by a check; nothing was built then to stop a future session from repeating it, and this session did, four times. | Not closed by this analysis alone; the recovery below follows the same precedent again, and item 2's gap is why a repeat is still possible |

## Classification (L-114)
Would the outcome have occurred without the safeguards that existed? For causes 1 and 2: yes -- the
`belongsToLineage` shape is real and would have fired the moment a Story existed, but no Story was ever created,
so this is a **genuine gap upstream of where that safeguard operates**, not a safeguard that worked. For causes
3 and 4: also yes, and more starkly -- GOV-S01 existed, ran, and printed PASS every single time, on every release
in this package's history; it is a **safeguard that has never once worked**, not one defeated by this session's
throughput. Neither is "a safeguard that worked."

## Dispositions of what the owner asked (why / how to prevent)
| Asked | Disposition |
|---|---|
| Why | Cause 1 (this session's own misreading, evidenced above) is the proximate cause of the four "no lineage" changelog lines. It is not the whole story: causes 3-4 (GOV-S01's own, independent, pre-existing defect) mean the one safeguard positioned to catch exactly this situation was never capable of catching it, for anyone, before this session existed |
| Prevention | Built and proven: `backlog_release_item_check_v1_5_0.py` + its new self-proof. The next release whose governed files change with no item moved and no declared unplanned-work marker is refused by the release tool itself, mechanically, before it ships -- not a promise to read more carefully |
| Recovery of the gap already shipped | Not decided unilaterally here. The package's own `RECOVERY_RUNBOOK_work_executed_outside_the_register_v1_1_0.md` (G100) governs exactly this shape of gap and reserves two of its steps to the owner by name: the restart act (step 5) and the Mission re-affirmation (step 6, G14). Proposed next action, pending that affirmation: open one Lineage covering the v1.367.0-v1.370.0 work (precedent: `L_OEStructureCleanup`, five dedicated stage releases), admit the four releases' real work as `preLineageItem` Stories once the Backlog stage output exists, each carrying the required fact shapes (evidence, criterion, harness, `lastAuditedAt`, finish point) and exempt only from the two act-record shapes the runbook names (concern declaration, planning event) that cannot be honestly produced after the fact |
| Other | Declined, with reason: rewriting the carried-over summary format itself is outside this analysis's evidence -- this session saw one lossy compression, not a pattern across many, and a fix aimed at one observed instance would be guessing at the mechanism |

## What is not claimed
- Cause 2 (nothing ties a ruling citation in a changelog to a required register change) is named but not closed
  here. Closing it risks exactly the kind of rushed, unverified cache-key or batching change already flagged and
  declined elsewhere in this session's own parked items; it is left for deliberate, separate work, not bundled
  into this fix under time pressure.
- GOV-S01's historical blindness (causes 3-4) is shown on this session's four releases and on one other saved
  log (v1.350.0); it is not re-run against every release in this package's history, only shown to be the general
  mechanism, not a one-off.
- Whether the owner wants the four releases backfilled via the runbook's restart path, or some other disposition,
  is the owner's decision (runbook steps 5-6, G14) -- nothing here performs that restart.
- This analysis does not revisit the adopting project's package-dependency subject, which the owner has separately ruled
  needs no Lineage and a different, classification-based treatment.
