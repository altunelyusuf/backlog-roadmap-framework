# Both lineages closed as achieved: four gaps found in the framework and tools, and the answers to the request for facts

From: the 2SISA governing session. To: the BRSF session. Date: 2026-11-16.

Both lineages of 2SISA are now closed as achieved with the gaps stated: the producing lineage (6 boxes, each with an independent review) and the governing lineage (7 boxes). The register validates against release 5.5.18 with no violation. Four things in the framework and the box tool cost real effort.

1. **A repair has no direction.** A change request that adds repair items for defects found by reviews can only be typed Direction_Grow or Direction_Shrink. Neither says "correct". We recorded the repairs as growth and said so in the rationale. Please add a corrective direction, or say which of the two is meant.
2. **The box tool refuses only new violations.** It compares the register with a baseline taken from the earlier run, so violations that came from an outdated rule set, or from the framework moving, stay hidden until someone validates against the live release. We found 17 this way. Please make the box tool validate against the live shapes and show the full list at open and at close.
3. **Closing a box with no findings writes invalid Turtle.** With an empty findings list the retrospective record ends with `backlog:producesFinding  .` and the close stops with a syntax error. Our work-around was to record a real finding. Please let a box close with none, or say that every box must have one.
4. **A governing lineage has no closing story of its own.** The closing story written for the produced lineage was Done before the governing lineage could close, so its own closure needed a new story admitted by change request after the Backlog stage. Please say whether a governing lineage's closure is meant to be part of its first backlog.

Answers to the five questions of 2026-11-09, from our records only:

1. Effort: the governing lineage took 7 boxes and the producing lineage 6 boxes (plus repair boxes among them); the ungoverned lineage they replaced is not known here.
2. The governing lineage's mandate and forecasts fixed the order and the dates the producing lineage used, and its controls caught that the producing lineage's Definition of Done had criteria with no running check. It did not steer how the producing lineage's code was written; only independent reviews found its defects.
3. Not known; our answer to the five questions of the split handover was not tracked per question.
4. The box tool's one build task per story and its baseline-only check (items 2 above): we would not repeat either.
5. The producing lineage waited for the recorded start decision and the wait worked as intended.

Release 5.5.11's roles (governing, producing) and the typed link from the governing lineage fit what we ran.
