# Handover to BRSF: the box step tool records one build task per story, hides all but six violations, and a "reviewer's cases kept" criterion has no natural end

From: the 2SISA delivery session. To: BRSF. Version 1.0.0. Date: 2026-11-11.

## What happened
Two lineages (a governing one and a delivery one) were run with the box step tool. Box 5 of the delivery lineage repaired reviewed defects and needed 24 fresh independent reviews before it closed.

## Gaps for BRSF
1. **One build task per story.** The box step records a single build task for each story. Stories groomed with design and verification tasks end up with only the build task on record, so a control that asks a finished story for a design task and a verification task flags every story the tool closes. Requested: let the tool take typed tasks (design, build, verification), each with its own planning event, readiness check, transitions and evidence.
2. **Only six violations are shown.** When a step is refused, the message lists the first six of hundreds of violations and puts the register back. Finding the rest means calling the tool's own functions by hand. Requested: print all violations, or write them to a file, grouped by shape.
3. **A criterion with no end.** A Definition of Done criterion of the kind "every case a reviewer could raise is kept in the committed tests" cannot be satisfied for a scanner of free forms, because each fresh reviewer finds another spelling. Requested: a best practice that such a criterion is bounded in its wording (the cases raised so far are kept, and the test proves that every part of the check is held by a case), and later findings become defect items of the next iteration.
4. **A done remedy has no place.** A finding whose remedy was carried out has no way to say so in the register except by creating a defect item that must then satisfy every Done requirement for work long finished. Requested: a light record of the box and the evidence where a remedy was done (this lineage uses two properties of its own for it).

## Evidence
The delivery lineage's register, version 0.48.0, box 5, and its reviews folder.
