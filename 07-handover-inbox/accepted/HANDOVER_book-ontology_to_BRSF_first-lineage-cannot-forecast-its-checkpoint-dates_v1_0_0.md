# Handover: a brand-new register cannot satisfy RS_PlannedDates at its Objective stage

**From:** the session building a book ontology (production lineage, first lineage of its register).
**To:** the BRSF session.
**Nature:** a framework finding with a reproduction. Nothing here asks BRSF to act on another package.
**Date:** 2026-11-10. Read against BRSF discipline v163.0.5, validator v1.19.0, date plan v1.1.0, shapes v1.219.0, profile revision Pr_17.

## What happens

A lineage opened under the default profile (Agentic Adaptive, which includes `RS_PlannedDates` and `RS_ForecastDiscussed`) writes its Objective stage, as the discipline orders (step 3: date the objectives from a forecast). The validator then refuses every objective checkpoint with `PD_UNPLANNED`: the checkpoint needs a `checkpointDate` and a `datePredictedBy` forecast that carries a made-at time, a completion, an assumption and an **observed velocity above zero**.

The tool that makes the forecast cannot run on a first register:

```
backlog_date_plan.py REGISTER.ttl predict --lineage Lineage --now 2026-11-10T18:00:00Z --effort Obj_Divisions=3
ERROR: no pair of consecutive boxes with effort in the register: there is no observed velocity to predict from
```

`--effort` supplies planned points but the velocity still comes only from earlier boxes of the same register. A first lineage has none, and its Backlog stage, which creates boxes, comes after the Objective stage. The same error appears on another consumer's register that has no completed box pair.

## Why it matters

- The Objective stage of a first lineage under the default profile cannot close while the rule is adopted at opening. Waiving the rule is not allowed, so the lineage stops.
- `backlog_impediment raise` requires `--box`, and no box exists before the Backlog stage, so the obstacle itself cannot be recorded in the register at this point either.
- The two together leave an agent with no route that keeps the rules: the discipline's step 3 and its obstacle rule (step 3c) cannot both be followed.

## Candidate remedies (BRSF decides)

1. Let a first register state an explicit, owner-recorded seed velocity (with its source) that the shape accepts as observed until two boxes exist.
2. Move the forecast and the checkpoint dates to the first box's opening, as for the box base plan (G187), and let the Objective stage close without dates.
3. Allow an impediment to name the lineage's stage when no box exists yet.

## What the sender did meanwhile

The Objective-stage objectives are written and validated: the only violations are `PD_UNPLANNED` on the checkpoints and the packages that come with the Backlog stage. The stage is not closed, no Objective stage output is recorded, and no date was invented. The Owner will be asked, in the sender's own session, to discuss a forecast when one can be made.
