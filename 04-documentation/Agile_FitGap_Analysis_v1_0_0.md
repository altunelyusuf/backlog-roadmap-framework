# Fit-Gap Analysis against the agile literature and standards

Run 2026-07-27 against the framework at subject version 1.3.0; every gap it found is closed in
1.4.0. Sources were retrieved and read this session rather than recalled — BP-D41 requires every
reference to be verified against an authoritative source before publication, and LL-35 records a
measured 5–10% hallucination rate in generated bibliographies.

## Reference set (all retrieved and read, 2026-07-27)

| Source | Retrieved from | What was taken |
|---|---|---|
| Scrum Guide 2020 | scrumguides.org/scrum-guide.html, with the commitment explanations on scrum.org | The artifact–commitment structure: Product Backlog↔Product Goal, Sprint Backlog↔Sprint Goal, Increment↔Definition of Done |
| OntoAgile — Ortega-Ordoñez, Pardo-Calvache & Pino-Correa, *DYNA* 86(209), 79–90, 2019, DOI 10.15446/dyna.v86n209.76670 | redalyc.org full text | Concept set (Process, Stage, Activity, Task, Tool, Role, Product, agile value, agile principle, Indicator); integration with PrMO and the Software Measurement Ontology; role/artifact/event structure |
| Strode, D.E., *A dependency taxonomy for agile software development projects*, Information Systems Frontiers 18(1), 23–46, 2016, DOI 10.1007/s10796-015-9574-1 | cited in the OntoAgile reference list, retrieved this session | The three dependency kinds: knowledge, task, resource |
| Kanban flow measures — Kanban Pocket Guide ch. 6 (prokanban.org); Kanban Guide for Scrum Teams via scrum.org | prokanban.org, scrum.org | WIP, cycle time, work item age, throughput, each defined against well-defined start and finish points; WIP limit as a *policy* distinct from the WIP measure |
| Already anchored in earlier releases | — | SAFe WSJF, Intercom RICE, DSDM MoSCoW, Now/Next/Later, Reinertsen cost of delay, W3C OWL 2 / SHACL |

Adjacent works seen in the search and **not** used, so the reader knows the boundary: K-CRIO (Scrum
conceptualisation), XPO, FDD ontologies, OSDAS, and the agility-assessment reference models. They
model *method performance*, which the section on non-goals explains this framework does not.

## Fit

| Literature concept | Framework term | Verdict |
|---|---|---|
| Product Backlog, Increment, ordered register | `Backlog`, `Increment`, `PriorityScore` | fit |
| Definition of Done as a commitment | `DefinitionOfDone` + executable criteria | fit, and stronger — criteria are runnable |
| Acceptance criteria | `AcceptanceCriterion` with Gherkin text | fit |
| Epic / Feature / Story ladder | eight disjoint `WorkItem` kinds | **was partial** — see gap 1 |
| Dependencies | `dependsOn`, `containerDependsOn`, disclosures | **was partial** — see gap 3 |
| Roles | `Role` (Owner / Builder) | **was partial** — see gap 6 |
| Estimation | `CostEstimate` with basis and confidence | fit |
| Prioritisation | WSJF, RICE, MoSCoW, launch model, R3 arbitration | fit, and beyond most of the literature |
| Impediments | — | **gap** — see gap 4 |
| Flow metrics | — | **gap** — see gap 5 |
| Agile values and principles | — | non-goal, stated below |

## Gaps found, and what was added

1. **No decomposition relation at all.** The ladder existed as eight disjoint kinds, but nothing
   said an epic *contains* its stories. Every agile source treats this as the primary structural
   relation. Added `decomposesInto` / `partOf`, deliberately non-transitive so roll-up cannot
   double-count, with a derived `decompositionState`, cycle detection, a rule that a parent may not
   be Done while a child is open, and a rule that parent and children may not both carry scores —
   the undecomposed-epic error an adopting project methodology standard records as an incident.
2. **Artifact commitments were missing.** The framework had goals and objectives but nothing binding
   a goal *to* an artifact. Added `Commitment` with `commitsToGoal` / `commitsToObjective` /
   `commitsToDefinitionOfDone`, plus L2 constraints that a register commits to a goal and an
   increment names a Definition of Done.
3. **Dependencies were untyped.** An untyped dependency says work must wait but not what would
   release it. Added `Dependency` with `hasDependencyKind` over Strode's closed set — knowledge,
   task, resource — each released by a different action.
4. **Impediments had no home.** Dependencies are cleared by finishing something; impediments are
   cleared by someone acting outside the register. Added `Impediment` with owner, statement, raised
   and resolved timestamps, and a constraint that an unresolved impediment must be owned.
5. **Flow was unmeasurable.** Added `startedAt` / `finishedAt` — the well-defined points every flow
   measure is defined against — plus `WipLimit` as a policy, with an advisory when actual
   work-in-progress exceeds it, and an L3 rule that a Done item must record its finish point.
6. **Team, team roles and capacity were absent**, and `Role` was closed at Owner/Builder. Added
   `Team`, `hasCapacity`, and an **open** `TeamRole` class: `Role` stays closed because it answers
   who may *decide*, which the framework constrains; `TeamRole` is open because how a team is
   organised is the adopting method's business.
7. **The canonical user-story clauses were unmodelled.** Added `asRole`, `wantsCapability`,
   `soThat`, with an advisory when a story states a beneficiary but no reason — the clause most
   often dropped and the one carrying the value argument.

## Deliberate non-goals, with reasons

- **Agile values, principles, practices, activities, tasks and tools** (OntoAgile's process layer).
  These describe how a *method* is performed; this framework governs the *register* a method
  produces and consumes. Adopting them would double the vocabulary and duplicate an existing
  published ontology, which L-105 forbids. An adopting development that needs both should align
  `backlog:WorkItem` with OntoAgile's Product and keep the two subjects separate.
- **Agility assessment / maturity scoring.** Out of scope for the same reason, and adjacent to the
  OQuaRE-style assessment the registration intent already records as an unexercised facet.
- **Ceremony/event modelling** (planning, review, retrospective). The framework records the
  *effects* of those events — refinement events, transition events, report runs — rather than the
  meetings, because the effects are checkable and the meetings are not.
- **Story-point-specific estimation scales.** `CostEstimate` is unit-neutral by design; a scale is a
  team convention, and encoding one would privilege a practice the framework has no business
  choosing.

## Measured after the change

Positive fixture 0 violations; negative fixture **186 violations across 52 planted defects**, eight
of them new: decomposition cycle, parent Done over an open child, parent and child both scored,
commitment to nothing, increment with no Definition of Done, dependency record with no kind,
unresolved impediment with no owner, finish before start, and a WIP limit with no target.
