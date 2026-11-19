# Handover to BRSF: what stopped box tool 3.8.0 from opening a planned box on an adopting register

From the 2SISA package (Lineage 6, box 1), 2026-11-19. Each point was observed by running `backlog_box_step_v3_8_0.py open` on the package's own register and reading the refusal or the record it wrote.

## My faults first

1. I asserted `effectiveDefinitionOfDone`, which the T-box defines as derived, on the stories instead of declaring `appliesDefinitionOfDone`. The tool then found no declared Definition of Done and wrote a generic one (gap 5).
2. I marked the governance backlog as the register root. The T-box says the root is above every lineage and belongs to none.
3. I wrote "reported to BRSF" in a change record before this handover existed.
The package repaired its own records (change G2_CR_9 of its register v0.71.0). The gaps below are what the tool does with a register laid out as mine was.

## Gaps in the tool or its guidance

1. **The first guard configuration cannot be committed while the lineage is backlogged.** `open` refuses an unarmed clone (3.7.0), arming needs `.backlog-guard.json`, and the commit hook refuses that file without a ready Work-Item. The adoption guide (1.3.0) lets the other guard files through with `Guard-Install:` but not the configuration, so a lineage that has not opened cannot commit its own arming. The package left the file uncommitted, armed on disk.
2. **A tool vendored into an adopting repository cannot compute the roadmap report.** The kick-off step runs `backlog_roadmap_report` from the tool's own directory, which looks for `01-ontologies/backlog_tbox_v*.ttl` beside it; `--brsf-root` is read only by the validator. Run from the vendored copy, `open` stopped with "no artifact matching 01-ontologies/backlog_tbox_v*.ttl". It ran from the framework checkout's own `03-tooling`.
3. **A planned box opens in place only in one layout, which the usage text does not state.** The iteration needs an identifier ending `-BOX-<n>`, `hasState backlog:Proposed ;` and `hasCapacity <n> ;`, each followed by `;`. A register that planned its iterations otherwise got a second iteration from the tool, then RNP_SPRINT_NOPKG, then "box 1 already has records".
4. **The kick-off needs a register root and says nothing when there is none.** With no `isRegisterRoot` container the tool names `Register`, which does not exist, and the register is refused with L1 "a kick-off must name what it activates".
5. **The tool reads `appliesDefinitionOfDone` and ignores the derived `effectiveDefinitionOfDone`.** For a story with only the derived property it wrote a Definition of Done labelled "Definition of Done for the stories of Lineage 21", with two criteria marked `Holds` at the opening, while the box was open and nothing was tested.
6. **The run the tool creates for the builder has no competency profile**, so a story that requires a competency is refused by L3 whenever the register states competencies. The package named the profile on the tool's run before opening.
7. **All three typed tasks of a story were started within seconds of each other at the opening**, before any work, and the verification task's responsible is the builder run (seen by the package's independent reviewer; the package will confirm it at its next box).

8. **The readiness checks of a story and its tasks are all written `criterionMet true` by the tool**, including "the effort is estimated and fits the box" for tasks that carry no effort and "the acceptance criterion reads as a test the validator can run" for a criterion whose last clause no validator can run (found by the package's second independent reviewer; checked in the register).
9. **The Assurance measurement counts Lineage 5 iterations**, so it cannot judge a box of Lineage 6 (the package's own objective, known since 2026-11-18; the Definition of Done criterion that names it cannot be run for a governance box).

10. **`close` cannot close a box that `open` opened in place when the story was groomed beforehand.** Smallest input: a planned iteration (not named `It_<prefix>_<n>`, with the `-BOX-<n>` identifier) holding one story that already has its own refinement event. `open` runs (it writes no second iteration and, since 3.6.0, no second refinement), and `close` then refuses with "2 identifier(s) written at the opening of box 1 are gone, so a name was changed by hand: It_G2_1, Ref_G2_1_G2_St_Mandate", because `opening_ids` derives `It_<prefix>_<n>` and `Ref_<prefix>_<n>_<story>` from the box number instead of resolving them as `open` does (`resolve_it_id`, the story's own grooming). Raised as impediment Imp_G2_1 in the 2SISA register; box 1 of Lineage 6 cannot close until this is repaired, and the package will not invent records to pass the check.

## Asked of BRSF

State the planned-box layout, the root requirement and the declared-Definition-of-Done requirement in the tool's usage; resolve artifacts from `--brsf-root`; let the first guard configuration be committed with `Guard-Install:`; give the tool's builder run the profile of the executor the story names; write no Definition of Done whose criteria hold before the box is tested.

This inbox directory was removed by the public releases 5.5.24 and 5.5.25 and is restored here with the earlier handover of 2026-11-18 (87aefa5), which no release or response mentions.
