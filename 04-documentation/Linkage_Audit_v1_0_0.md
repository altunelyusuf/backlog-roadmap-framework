# Linkage Audit — are the concepts connected, not just present?

A concept inventory answers "does the vocabulary contain X". This audit answers the harder question:
**is X connected to the things that make it mean something**, and does a constraint enforce the
connection. Run against v1.2.0 before the work below; every gap it found is closed in v1.3.0.

## Findings and dispositions

| Linkage the review asked for | Before | Now |
|---|---|---|
| Package contains product backlog items | present (`memberOfContainer` / `hasMember`) | unchanged |
| **Package depends on another package** | **missing** — dependency existed only between items | `containerDependsOn` (transitive, cycle-checked) plus `derivedContainerDependency` computed from member edges by rule R5 |
| **Package ranked within the roadmap** | **missing** — `scheduledInHorizon` and `contributesToMilestone` were item-only, and nothing linked a container to a roadmap | domains widened to containers; `rankedOnRoadmap` + `hasRoadmapRank`, with uniqueness enforced and launch-gated containers required to be on the plan at L2 |
| Every PBI has a Definition of Done | partial — `appliesDefinitionOfDone` existed but nothing required an item to resolve to one | `effectiveDefinitionOfDone` derived by rule R7 from the item or any container it belongs to; L2 violation if none resolves |
| Every PBI has acceptance criteria | partial — required only at `Ready` | required for every item that has left `Proposed` (L2) |
| **Acceptance criterion proved by a test** | **missing** — evidence pointed at a test but not at the criterion it proved | `attestsCriterion`; at L3 every criterion of a Done item must be attested by bridge-verified evidence |
| **Test harness proving Done** | **missing** | `TestHarness` with `harnessComplete` derived by rule R6 — true only when every criterion of the item is attested by verified evidence; at L3 a Done item without a complete harness is a violation |
| **Lifecycle workflow of permitted transitions** | **missing** — five states, no transitions | `Workflow` / `StateTransition` (guarded) / `TransitionEvent`, a shipped default workflow of 8 transitions, and constraints that a recorded move used a permitted transition and that an item's state matches its latest move (L2) |

## Why the transitions carry executable guards

A closed state enumeration says which states exist. It says nothing about whether an item may jump
from Proposed straight to Done, which is exactly the move a status field permits and a process does
not. Each transition therefore carries a guard in the same executable form as Definition-of-Done
criteria: refine requires acceptance criteria and a refinement event, start requires dependencies
Done, complete requires a complete harness and verified evidence, withdraw requires a rationale.
Two transitions are deliberately unguarded — returning work to Ready and deferring it to Proposed —
because pretending work cannot be put back down is how paused work hides as in progress.

## What the audit itself caught

Widening `disclosesDependencyOn` to accept containers left the shape that governs it still demanding
an item-level `dependsOn` edge, so the first run of the new positive fixture failed with two
violations against the framework's own example. That is L-42 exactly — a relationship was changed on
one side and verified on one side. The shape now branches on the disclosed target's type and accepts
either edge, and the type check walks `rdfs:subClassOf*` rather than matching the root class
literally, since a `Story` is not asserted to be a `WorkItem` without inference.

## Measured after the change

Positive fixture 0 violations; negative fixture **150 violations across 44 planted defects**, seven
of them new in this release: container dependency cycle, rank without a roadmap, a move using a
transition no workflow permits, a workflow leaving a state unreachable, a self-looping unguarded
transition, a harness with no evidence, and an item whose state contradicts its own history.
