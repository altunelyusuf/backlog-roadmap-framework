# Falsifiability Audit — can a register built with this framework be wrong?

A parallel session reported that a backlog and roadmap could be built with the framework that were
effectively arbitrary, with no way to tell success from failure. This document records the
investigation, the measurement, and the fix.

## The claim was true, and it was measured

An adversarial register was authored to be maximally meaningless while formally correct:

- a WSJF score of **9.9** over components computing to **0.3** — the number unrelated to its inputs
- evidence marked verified with the method **"asserted"**
- an objective with metric, baseline and target, **never observed**, deadline already passed
- a milestone whose date passed months ago with **no outcome recorded**
- acceptance criteria reading **"Given, When, Then."**
- scores dated six months before the last completion, never re-run
- a roadmap rank contradicting the score order, with no rationale
- a cost estimate never compared with anything actual

Against framework v1.4.0 this register validated at conformance level **L3 with 0 violations** and
two advisory warnings. The claim is therefore **confirmed**: every gate the framework had checked
whether the register was *well formed*, and none checked whether it could be *wrong*.

The fixture ships as `03-tooling/fixtures/fixture_adversarial_random_v1_0_0.ttl` and is now the
third mandatory self-proof: the gate aborts if it ever passes again.

## Why it happened

Every constraint written before v1.5.0 was a constraint on **form** — this field is present, that
reference is typed, this state matches that derivation. Form is checkable without reference to the
world, which is exactly why a register can satisfy all of it and mean nothing. The framework had no
place to put an **observation**, so an objective could state a target that nothing would ever
contradict; no notion of an **outcome**, so nothing could be recorded as missed; no comparison of a
score with **its own components**, so a ranking could be decorative; and no distinction between
verification and the **assertion** of verification.

## What was added (subject 1.4.0 → 1.5.0)

| Route the adversarial register took | Now closed by |
|---|---|
| Score unrelated to its components | WSJF and RICE arithmetic checked against the recorded components (L1); a score with neither components nor rationale rejected (L2) |
| Stale ranking | A score predating the last completion in the register is a violation (L3), grounded in BP-D11: a ranking is a snapshot, not a committed order |
| Target that can never be missed | `hasTargetDirection` mandatory; target equal to baseline rejected; a passed deadline with no observation and no re-baseline rejected (L3) |
| No way to record failure | `MetricObservation` + derived `objectiveOutcome` and `milestoneOutcome` over a closed `AchievementStatus` including **Missed** |
| Silently moved goalposts | `Rebaseline` — owner-decided, previous target retained, rationale required |
| "asserted" verification | Method must not be a bare assertion and must name a check; `verifiedByTool` required at L3 |
| Gherkin-shaped noise | Each of Given / When / Then must carry substantive text (L2) |
| Estimates never wrong | `hasActualEffort` required on completed items carrying an estimate (L3) |
| Work tracing to nothing | Items must trace to an objective directly, through a container, or through a parent (L3) — upgraded from advisory |
| Arbitrary roadmap order | A container ranked ahead of a higher-scored one must record a rationale (L2) |

Against v1.5.0 the same adversarial register produces **13 violations**.

## Other gaps this audit surfaced for industrial and academic use

Two are closed above and worth naming separately because they bite hardest in practice:

- **Estimate quality was unfalsifiable.** Without actuals, no team using the framework could ever
  demonstrate that its estimates were improving or degrading. Academic use is worse affected than
  industrial: an estimation study needs the pair.
- **Re-baselining was invisible.** The most common way a plan "succeeds" is that its target moved.
  A framework that permits silent target edits measures nothing over time.

Two remain open and are recorded rather than fixed:

- **Observation trust.** The framework requires an observation to name its method; it cannot verify
  that the method was run or that the number is honest. Only an execution bridge could, and the
  bridge covers evidence artifacts, not business metrics. Adopters wanting this should extend the
  bridge with metric collectors.
- **Attribution.** A benefit realisation claim requires a verified observation, but nothing
  establishes that the delivered work *caused* the improvement. No ontology can settle causation;
  the framework's honest position is to record the claim, the observation and their dates, and to
  leave the inference to a human who can see confounders.

## Honest note on strictness

The arithmetic shapes compare declared score values with components at a tolerance of 0.05 and
require the components to be typed `xsd:decimal`, matching the declared ranges. Registers that wrote
integer components now fail a datatype check they previously passed silently; the shipped positive
fixture was corrected accordingly rather than the check loosened.
