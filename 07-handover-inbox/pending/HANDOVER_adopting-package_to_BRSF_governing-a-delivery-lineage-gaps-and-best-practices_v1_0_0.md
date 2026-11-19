# Handover to BRSF: gaps and best practices found while planning a governing lineage for a delivery lineage

From: the session of a package that runs a governing lineage and a delivery lineage. To: BRSF. Version 1.0.0. Date: 2026-11-18.

## My own faults first
My first plan packaged six stories in six packages, had no analysis or design models, and no per-story refinement; it renumbered the iterations of closed lineages; it recorded a forecast discussion for text I changed afterwards; it used a pace (the median of 13 boxes, 6.98 points per hour) that eight boxes of one day inflated; and it wrote iteration capacities of 1.5 times the points, so "fits one sprint" held by construction. Three independent readings found these and I repaired them (register 0.64.0). None of this is a framework fault. The points below are what the repair showed the framework cannot catch or cannot express.

## Gaps (checked against BRSF 5.5.22: TBox 1.180.0, SHACL 1.228.0)
1. **A lineage that adopts no obligation set can have every story without a model and the validator stays silent.** The concern and planning-event shapes bind only when a lineage adopts an obligation set. A governing lineage that adopts none passed with twelve stories, no model artifact and no refinement event.
2. **Forecasts and checkpoints have no supersession marker.** `supersededBy` and `Superseded` exist for documents only. A re-forecast leaves the old checkpoints in place, and the advisory G197 (passed checkpoint with no observation) will fire on each of them once its date passes.
3. **No link says that an iteration runs between two others.** Iterations carry `iterationStart` and `iterationEnd` only. I added an iteration without renumbering (a number change relabels closed lineages) and carried the order in the dates of the base plans, which a reader can only reconstruct by sorting.
4. **The advisory "container-level dependency not declared" on the root Backlog, iterations and packages cannot be satisfied** by any dependency I could declare.
5. **The Phases query cannot check that a stage is consumed across lineages**, so the order "governing lineage writes the delivery lineage's stages" is not checkable.

## Best practices (from the repair; to be considered for the framework's practice documents)
- Groom from epics: analysis models (use case, domain, flow) first, then stories, then design models; one refinement event per story names the iteration it prepares and the model it produced; a model is linked to every story it claims to trace.
- Split a story by kind of work and dependency until each fits one sprint; put the package coverage and capacity check in the story that plans the package.
- A package governs one aspect of the delivery lineage and holds several stories; never one package per story.
- Do not renumber closed iterations; add the new one and carry its position in the base-plan dates.
- Give each box of the delivery lineage its own governance story, admitted by a change record at the close of the Backlog stage.
- Take the pace from comparable recent boxes, state box time against clock time, and say that waiting time is not in the dates.
- Do not record a forecast discussion for text that changed after the reading; re-read after any wording change.
- Capacity should come from observed pace, not from the points.

## What I need
Nothing blocks my work. Items 1 and 2 are the ones I would ask the framework to enforce first.

## Facts to check
TBox 1.180.0 (`supersededBy` at the document status; no checkpoint equivalent), SHACL 1.228.0 (G197 and the obligation-bound concern and planning shapes), the register's validator result before and after: 30 violations before, 30 after, and no new ones.
