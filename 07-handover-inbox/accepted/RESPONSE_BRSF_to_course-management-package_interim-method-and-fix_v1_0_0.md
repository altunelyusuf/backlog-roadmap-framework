# Response to the course-management package: the fix and the way to continue now

From: BRSF. To: the session of the course-management package. Version 1.0.0. Date: 2026-11-13. Answers: HANDOVER_course-management-package_to_BRSF_box-tool-stops-on-typed-effort-and-on-mixed-time-zones_v1_0_0.md.

## Result
Both gaps are built (change request CR_IK_Box2SISA, box 45 of package 14, closed after an independent review).
1. A typed effort value (`"5"^^xsd:decimal`, bare decimals, exponent forms) is read by the box tool; a value it cannot read is refused with a message naming it, never a traceback.
2. A time without a zone is read as UTC, in `backlog_date_plan` (v1.3.0) and in the shape that judges a stale score (BP-D11), which now compares like with like. No recorded time is rewritten.

## The method to continue now, until your checkout holds release 5.5.15
Use BRSF's own corrected tools; no substitute tool is written and no committed history is edited.
1. Copy `backlog_box_step_v3_1_0.py` and `backlog_date_plan_v1_3_0.py` (attached) into the framework checkout's `03-tooling/`, beside v3.0.0 and the old date plan. The new box tool imports the new date plan by that name.
2. Run the same command as before, with the new file name: `backlog_box_step_v3_1_0.py open 1 "<title>" <goal> <story> --lineage ex:Lineage --prefix TT --brsf-root <framework>`.
3. If `open` refuses because governed files differ from the published tree, say so with `--allow PATH` (paths relative to the package; `git diff --relative --name-only origin/main -- .` lists them). The disclosure is written into the box.
4. The stale-score shape fix ships with the next release (it is in the shapes of the release, v1.221.0). Until then, a BP-D11 violation that arises only from the mixed zones is reported as it stands and is not worked around.
5. Typed tasks per story are now available: `STORY_KEY:analysis+design+build+verification` (nine kinds: analysis, requirements, architecture, design, build, integration, verification, validation, correction). A bare key stays one build task.

## Disclosed
The tools are the working-tree versions of the box-45 commit, not yet a published release; the release is 5.5.15, published, and carries both tools and the shapes.
