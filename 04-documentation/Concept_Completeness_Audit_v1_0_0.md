# Concept Completeness Audit — v1.2.0

Run per L-74: a concept counts only where **all three** are true — vocabulary exists in the TBox,
a SHACL shape enforces something about it, and the shipped positive fixture demonstrates it in use.
Vocabulary alone is a schema-only declaration (L-71) and is reported as partial, not present.

| Concept | Vocabulary | Enforced | Demonstrated | Verdict |
|---|---|---|---|---|
| Goal | yes | yes | yes | **complete** |
| Objectives | yes | yes | yes | **complete** |
| Scope (statement + exclusions) | yes | yes | yes | **complete** |
| Product backlog items | yes | yes | yes | **complete** |
| Grooming / refinement | yes | yes | yes | **complete** |
| Package & packaging | yes | yes | yes | **complete** |
| Packaging with scoping | yes | yes | yes | **complete** |
| Coverage | yes | yes | yes | **complete** |
| Containment | yes | yes | yes | **complete** |
| Dependencies | yes | yes | yes | **complete** |
| Benefits | yes | yes | yes | **complete** |
| Opportunities | yes | yes | yes | **complete** |
| Costs | yes | yes | yes | **complete** |
| Risks | yes | yes | yes | **complete** |
| Build vs maintain prioritisation | yes | yes | yes | **complete** |
| Definition of Done (item) | yes | yes | yes | **complete** |
| Definition of Done (project) | yes | yes | yes | **complete** |
| Acceptance criteria | yes | yes | yes | **complete** |
| Ranking | yes | yes | yes | **complete** |
| Gates | yes | yes | yes | **complete** |

**20 of 20 concepts complete on all three axes.**

Baseline before this release, measured the same way against the same checklist: **10 of 20 present**
on vocabulary alone, and fewer on all three axes. The gap was concentrated in the intent layer
(goal, objective, benefit, opportunity), scope, refinement, cost, risk and the build-versus-maintain
question — everything that explains *why* a register looks the way it does, as opposed to *what* it
contains.

## What was deliberately not built

**Risk was not minted.** The pack's risk subject already defines `risk:Risk` as the effect of
uncertainty on objectives per ISO 31000:2018 — exactly the notion delivery work needs. Per L-105 the
framework delegates to it and adds only the binding properties and the constraint that an untreated
risk must be explicitly accepted. Minting a parallel `DeliveryRisk` would have been the failure this
lesson names.

**Metrics and stakeholders were not minted** either: objectives reference `core:Metric` and benefits
reference `core:Stakeholder`, keeping measurement and stakeholder semantics in the subjects that own
them (BP-D21).

## Honest limits

- `EnforcementDomain` and `CapabilityClass` ship unpopulated by design; the classification schemes
  belong to the adopting development, and the fixture demonstrates use rather than prescribing a
  taxonomy.
- Benefit realisation is enforced structurally (a realisation claim needs verified evidence) but the
  framework cannot verify that the measured improvement was *caused* by the work. No ontology can.
- The investment-mix policy is declared and checked for completeness; the actual-versus-target
  comparison is computed by the report tool, not constrained by SHACL, because starving a category
  for one quarter may be a decision rather than a defect.