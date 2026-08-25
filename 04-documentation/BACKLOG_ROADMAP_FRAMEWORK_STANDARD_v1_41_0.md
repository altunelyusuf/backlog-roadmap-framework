# Backlog & Roadmap Semantic Framework — Standard v1.41.0

**Subject:** `backlog` 1.7.0 · **Namespace:** `http://example.org/backlog#` · **Prefix:** `backlog:`
**Status:** REGISTERED as `orh:Subject_backlog`; independently distributable and usable without the pack
**Governed by:** OE Operating Discipline v2.2.0

*This document states the subject's version, which is what it describes. It deliberately pins
neither the distribution package's version nor the OE Pack release it was last verified against:
both move independently of the vocabulary and would go stale here by construction. For the package
version see `VERSION.txt`; for every measured figure see `RELEASE_METRICS.txt`, which is generated
and regenerable (L-91: prose points at the authoritative field rather than restating it).*
**Primary source:** `BACKLOG_ROADMAP_STANDARD_v1_0_0.md` (adopted 2026-07-27), SHA-256 `a58a6c89…`
**Coverage against that source: 36/36 concepts = 100%** (BP-D31 gate, threshold 80%)

---

## 1. What this standardises

Every development that ships anything maintains four claims: what we intend to build, where each
piece stands, what proves the finished ones are finished, and what to do next. In prose those
claims drift apart within weeks. This framework makes them machine-checkable, project-independently,
so a second development adopts the same discipline without re-deriving it.

Ten commitments carry the design. The first five are structural, the second five govern the
methodology around the register.

1. **Three layers stay distinct.** A *blueprint* models what the domain is; a *backlog* registers
   scoped work against it; a *roadmap* is the computed view of that backlog. A roadmap document
   decays the moment the register moves — the fix is structural, not a reminder to update it.
2. **Done is a constrained fact.** At conformance level L2 and above an item cannot hold `Done`
   without Evidence whose `evidenceVerified` flag was set true by a bridge that checked the real
   workspace. The ontology cannot read a filesystem, so that fact must come from outside the graph.
3. **Roll-ups are derived.** Container and milestone states come from members and contributors by
   rule; an asserted state disagreeing with the derived one is a violation.
4. **The roadmap projects the backlog.** An item on a horizon or against a milestone must exist in
   a register. The roadmap cannot introduce scope.
5. **Priority carries its method.** Scores are reified individuals naming their method and the
   moment they were computed.
6. **Two prioritisation models, never conflated.** Throughput ranking answers what the best next
   increment of capacity is; launch readiness answers what must be complete before first
   deployment and is an owner declaration, never computed. Rule R3 keeps them apart and prints
   both answers, so a disagreement is displayed rather than silently resolved.
7. **Gap discipline is binary.** Every open item is either scored or explicitly flagged
   not-yet-scoreable with a written reason. An item that is neither is a *silent gap* — a defect
   in the register, driven to zero by tooling rather than by judgement in conversation.
8. **A dependency said out loud is an edge.** A dependency stated in prose or in a cost-benefit
   judgement must exist as `dependsOn`; an undisclosed-but-real dependency is worse than no
   dependency modelling at all, because the register looks resolved.
9. **Completion is not deployability.** A container whose members are all Done but which has an
   unresolved external blocker is not ready; completeness is one input to job size, not a
   substitute for checking real dependency edges.
10. **A rule keeps its incident.** Every methodology rule records the disagreement it closes, its
    exact logic, and the concrete failure that produced it. A rule stripped of its incident is a
    convention nobody can argue with or retire.

---

## 2. Concept dictionary

### 2.1 Blueprint layer

| Term | Meaning |
|---|---|
| `Blueprint` | The domain model a backlog is scoped against (`blueprintFor` one `Backlog`) |
| `DomainEntity` | A first-class thing the product is about |
| `EntityLifecycleStage` | Closed set: `Stage_Creation`, `Stage_ActiveUse`, `Stage_SuspensionException`, `Stage_Termination` |
| `ComplianceObligation` | A duty the domain imposes independently of any feature request |
| `BlueprintGap` | An explicitly recorded absence of coverage — a defect, not a silence |
| `CapabilityClass` | A first-class business concern (e.g. business continuity), owned rather than scattered |
| `EnforcementDomain` | How a capability's correctness is enforced; the scheme belongs to the adopter |
| `coversEntity` / `coversStage` / `coversObligation` | What a work item covers |
| `verifiedAgainstCode` + `hasCodeVerificationNote` | The coverage claim was checked against running code, and what that found |

The stage name is `EntityLifecycleStage`, deliberately not `LifecycleStage`, so it cannot be
confused with `LifecycleState` — the delivery state of a work item. The two are unrelated.

### 2.2 Work items, containers, lifecycle

| Term | Meaning |
|---|---|
| `WorkItem` + 8 disjoint kinds | Initiative, Epic, Feature, Story, Task, Defect, Spike, Enabler |
| `Backlog`, `Package`, `Increment`, `Iteration` | Containers; state derived from members |
| `LifecycleState` | Closed set: `Proposed`, `Ready`, `InProgress`, `Done`, `Cancelled` |
| `hasState` (functional), `derivedState`, `derivedMilestoneState` | Asserted and computed states |
| `hasIdentifier`, `hasTitle`, `hasRationale` | Identity, summary, and the reason for withdrawal |

### 2.3 Evidence and Definition of Done

| Term | Meaning |
|---|---|
| `Evidence` ⊂ `core:Artifact` | `TestEvidence`, `ReleaseEvidence`, `ArtifactEvidence`, `ReviewEvidence` |
| `evidenceVerified`, `verifiedAt`, `hasVerificationMethod` | The bridge's world-check, its time and its method |
| `DefinitionOfDone`, `DoDCriterion` | Each clause carries `hasCheckQuery`, `hasExpectedResult`, `hasCriterionStatus` |
| `AcceptanceCriterion` | Per-item Given/When/Then held on the item |

The shipped baseline Definition of Done has six executable criteria: evidence exists, evidence is
verified, acceptance criteria are present, no Done item depends on unfinished work, no open item is
a silent gap, and every launch gate is an owner decision with a rationale.

### 2.4 Prioritisation and the two models

| Term | Meaning |
|---|---|
| `PrioritizationMethod` (open) | Six shipped: WSJF, RICE, RICE+DepFactor, MoSCoW, Cost of Delay, Value/Effort |
| `PriorityScore`, `WSJFScore`, `RICEScore` | Reified scores retaining their components |
| `isAveragedFromMembers` | Rejected on container scores — averaging re-uses numbers computed for unrelated reasons |
| `rankedOnRoadmap`, `hasRoadmapRank` | Placement and order on a roadmap, for **work items and containers alike** — an epic may be ranked, not only a package. Ranks are **unique per roadmap**: a rank that does not order is not a rank. Contrast the launch model below; the difference is that launch priority orders gates that must *all* clear, while a roadmap rank answers *what next*, and a tie there leaves unanswered the question the rank exists to answer |
| **NEXT ties** | When startable items share the top score, NEXT names one **and prints the whole tied set**. The order is a total one — score, then `hasJobSize` ascending, then identifier — so the same register always yields the same answer; the tie itself is **not resolved**, because equal value per cost is a real answer and promoting one item by its sort position would present an accident of ordering as a decision. The same convention as R3, which prints both models' answers and resolves neither |
| **two rank rules, different defaults** | `WorkItemRoadmapRankShape` (targets `WorkItem`) never objects to an item having **no** rank — a rank answers "what next", and an unanswered question is not itself a defect at item level. The roadmap-placement clause in `ContainerLinkageShape` (targets `WorkItemContainer`) **requires** a rank on any launch-gated container at L2. Same vocabulary, opposite default for absence, and the two shapes sit about a thousand lines apart. An adopting session read the first, applied it to eight launch-gated containers, and left eight real violations standing for a full register pass. Each shape now carries an `rdfs:comment` pointing at the other |
| `isLaunchGate`, `hasLaunchPriority` | The owner-declared launch model. Priorities may **tie**: co-equal mandatory preconditions are real, and every gate tied at the lowest open priority is unioned into the launch-scoped scope rather than one being chosen. Unlike `hasRoadmapRank`, ties are deliberately not forbidden — forcing an owner to invent a sequence that does not exist is the fabrication the framework refuses elsewhere |
| `Role` (`Owner`, `Builder`), `decidedBy`, `hasDecisionRationale` | Who may decide what, and why they decided it |
| `RankingModel` (`ThroughputRanking`, `LaunchScopedRanking`) | Which question a ranking answers |
| `hasRankingForkResolution` | The model an owner has decided governs pickup when the two disagree, recorded once with `decidedBy` and `hasDecisionRationale`. Printed **beside** the disagreement, never instead of it; absent is the default and means the fork keeps asking |
| `notYetScoreable`, `hasScoreabilityReason` | The honest alternative to a fabricated number |
| `isBusinessCapability` | False marks a real but non-shippable grouping, excluded from capability ranking |
| `DependencyDisclosure`, `hasExternalBlocker` | Prose dependencies made into edges; completion versus deployability |

### 2.5 Roadmap, reports, documents

| Term | Meaning |
|---|---|
| `Roadmap`, `RoadmapHorizon` (`Now`/`Next`/`Later`), `Milestone` | The projection and its bands |
| `RoadmapReport`, `ReportSection`, `hasRunTimestamp` | A report is a run, not a document |
| `derivedInReport`, `underRankingModel` | A recommendation points at the run and model that produced it |
| `GovernedDocument`, `DocumentStatus` (`Live`/`Superseded`), `supersededBy`, `hasSupersessionReason` | Retirement marked in place, never deleted |

The eight mandatory report sections: NEXT under throughput, NEXT under launch scope, full ranked
backlog, flagged items, silent-gap check (must read zero), launch readiness by package, package
level multi-factor ranking, and the orphan/coverage check.

### 2.5b Linkage between concepts (v1.3.0)

| Term | Meaning |
|---|---|
| `containerDependsOn` / `derivedContainerDependency` | Declared package-to-package dependency, and the one computed from member edges; a disagreement between them is reported |
| `rankedOnRoadmap`, `hasRoadmapRank` | A container's place and declared order on a roadmap; ranks are unique, launch gates must be placed |
| `attestsCriterion` | The acceptance criterion a piece of evidence proves |
| `TestHarness`, `harnessComplete` | The checks proving one item; completeness is derived when every criterion is attested by verified evidence |
| `effectiveDefinitionOfDone` | The DoD governing an item, derived from the item or an owning container |
| `Workflow`, `StateTransition`, `TransitionEvent` | Which moves between lifecycle states are permitted, under what guard, and which moves actually happened |

### 2.5c Intent chain, scope boundary and external parties (v1.6.0)

| Term | Meaning |
|---|---|
| `Mission` | Why the development exists; owner-declared root of the intent chain |
| `contributesToMission` | Goal → mission; goals must in turn carry measurable objectives |
| `fillsScope` | **Objective → scope.** The link a scope-first lineage uses: an objective cannot name a boundary that does not yet exist, so asserting it is only possible where the scope was fixed first. Direction records the order — no date needed |
| `scopeRealizesObjective` | **Scope → objective.** The reverse, and the record of a lineage whose boundary was drawn around objectives already decided. Kept, because which link a lineage uses *is* the fact worth recording; asserting both records no order at all and is rejected |
| `scopeCompletionState` / `scopeOutcome` | Derived: is the scoped work finished, and did it work — computed separately, in that order |
| `ScopeChange` | Owner-decided, rationale-bearing admission of work into a set scope |
| `ExternalDependency` + `ExternalDependencyType` | Something outside the development, over six types: vendor, upstream component, peer team, regulatory, infrastructure, customer |
| `requiresExternalEnhancement` | This item needs an external party to change something — triggers the proposal rule |
| `EnhancementProposal` + `ProposalStatus` | The request to that party; never a work item, never scheduled here |
| `RegisterSession` | Provenance of register edits: verified before changing, and what was left alone |

### 2.5c-i Intent, scope, refinement, cost and investment mix (subject v1.2.0)

**Build order: `Mission` → `ScopeStatement` with its exclusions → `Goal` → `Objective`.** Scope
precedes goals and objectives rather than summarising them. Written last, a boundary is drawn around
objectives already fixed, so every objective is inside it by construction and it can never refuse
anything — the step reads like a check while being structurally incapable of failing.

The layer that explains *why* a register looks the way it does. Without it a backlog can be
delivered in full and deliver nothing.

| Term | Meaning |
|---|---|
| `Goal` | A durable outcome the product exists to achieve; owner-decided, measured through its objectives |
| `Objective` | A measurable, time-bounded target advancing a goal — metric, baseline, target, deadline. An objective without a metric cannot be missed |
| `Benefit` | A specific improvement expected from completing work, owned by a `core:Stakeholder`; a realisation claim needs verified evidence, exactly like a Done claim |
| `Opportunity` | Identified upside not yet committed as work, converted into an item explicitly when someone decides to pursue it |
| `ScopeStatement` / `ScopeExclusion` | The declared boundary and the owner-decided things deliberately outside it, each with a rationale |
| `RefinementEvent` | The dated act that makes an item Ready — readiness is done to an item, not drifted into |
| `EstimationBasisKind` — `hasBasisKind`, `basisObservation`, `analogousTo` | Whether an estimate or score was **Measured**, **Analogous** or **Judged**. `hasCostBasis` records *what* a figure rested on; this records whether that basis was **run**. A Measured claim must name the `MetricObservation` that produced it, an Analogous one the completed item it was drawn from. Judgement is legitimate and is the majority case — what is refused is a judgement being indistinguishable from a measurement. An advisory fires where measuring pays best: a judged estimate on an item inside a launch gate |
| `CostEstimate` | Unit-neutral estimate carrying its basis and confidence; a naked number fails |
| `InvestmentCategory` | New capability / maintenance / technical debt / compliance — because a score cannot arbitrate between categories that answer to different arguments |
| `ProductLifecyclePhase` | Pre-launch / live / sunsetting; the phase decides which prioritisation question governs |
| `PortfolioPolicy` + `CapacityAllocation` | Declared capacity shares that must sum to one, so no capacity is allocated by default |
| `ImplementationProject` | The funded, bounded effort the project-level Definition of Done applies to |

Three structural umbrellas hold the vocabulary together: `BacklogConcept` (everything this subject
introduces, under `core:Concept`), `WorkItemContainer` (any grouping whose state is derived from its
members), and `RoadmapElement` (everything in the time-facing projection).

### 2.5c-ii Two lineages: development and operational (worked example)

Raised by an adopting project that carried six goals without an objective for weeks, each with a
locally-reasonable rationale of the form *"no real number exists to set a target against yet"*.

**The failure is undecidability, not inconvenience.** A lineage whose objectives require real
operational data cannot be decided during development, because the deciding fact cannot exist until
the development it would govern has shipped and been used. The register is not merely awkward to
fill in; it is unclosable by construction, and an unclosable register stops being consulted.

**The resolution is two lineages, not one deferred claim.** They run in parallel, each complete in
its own terms, and the framework expresses both today — nothing limits a register to one `Mission`,
and none of `contributesToMission`, `contributesToGoal` or `pursuesObjective` is functional.

| | root | objectives measure | satisfied by | closable |
|---|---|---|---|---|
| **Development lineage** | the development's own mission — *why this is being built* | that the development did what it set out to do | test data driven through the real system, automated test suites, a count computed over the register's own structure | **before** launch |
| **Operational lineage** | the operational mission — *what the running product must achieve* | the business consequence | real measurement of real usage | **after** real usage exists |

**The bridge, which is the load-bearing part.** Where the operational lineage names a measure that
does not yet exist, that measure becomes a **development objective**: build the instrument, test it,
and return its results. The development lineage's own objectives therefore include *"the operational
measure exists, is wired to the real path, and has been exercised"* — and satisfying them is
precisely what makes the operational lineage satisfiable later. The operational lineage is not
parked; it is being *constructed* by the development lineage, one measure at a time.

This is the same shape the framework already uses for `CrossCuttingInvariant`: a check declared with
`hasCheckQuery`, reported `NotYetEnforceable`, and `tracksItem` naming the work that would make it
runnable. An operational objective awaiting its instrument is that pattern applied to measurement
rather than to enforcement.

**Where the development lineage gets its facts.** Test data driven through the **real** creation path
— with authorisation, validation and audit engaged rather than bypassed — produces real facts about
the real system even though its input is synthetic. That is the empirical standard any test already
relies on, applied to volume and behaviour instead of correctness alone.

**`Benefit` remains the place for the business claim itself**, attached via `benefitFor` with
`benefitRealized` left `false` until verified `Evidence` of real usage arrives. Recording a business
figure that does not exist yet as an `Objective` baseline is fabrication; recording it as an
unrealised `Benefit`, with a development objective building the instrument that will eventually
measure it, is a plan.

**The line, and an honest note about it.** A synthetic measurement may satisfy a development
objective. It must never satisfy a `Benefit`'s `benefitRealized`, which is gated on real usage by
definition. **The framework cannot currently enforce that line** — `Evidence` carries a verification
method and a tool but nothing distinguishing synthetic input from real, so a suite handed a load-test
artifact as benefit-realisation evidence will not object. It is a discipline the adopter keeps, not a
constraint the suite applies, and it is said here rather than left to be discovered.

### 2.5c-iii Product backlog items versus execution tasks (subject v1.13.0)

| Term | Meaning |
|---|---|
| `ProductBacklogItem` | Work carrying value in its own right, ordered against other work. All eight original kinds are these — **including `Task`**, whose definition has always said it must be *tracked, prioritised and evidenced like any other work item*. `Task` is non-user-facing product work, **not** a sprint task, and was deliberately not repurposed |
| `ExecutionTask` | A step produced by planning a backlog item into an iteration. Subordinate by construction: **not scored, not ranked**, existing only as part of its parent. Scoring it would double-count the parent's value — the error the framework already refuses for decomposed parents and children |
| `PlanningEvent` — `plansItem`, `plannedInto`, `producesTask`, `plannedAt`, `plannedBy` | The dated act of taking an item into an iteration and breaking it into tasks. The boundary between ordering work and doing it |

An `ExecutionTask` is **excluded from eight product-backlog constraints** — scoreability, silent-gap,
objective traceability, investment category, acceptance criteria on leaving Proposed. Without that
exclusion the suite is jointly unsatisfiable for any task: one constraint forbids a score, another
requires one. A backlog item may not be `Done` while a task planned from it is still open.

### 2.5c-iv Flow, velocity and forecast (subject v1.14.0)

**Almost nothing here is stored.** Cycle time, item age, throughput and velocity are **computed by
the report** from `startedAt`, `finishedAt` and the iteration period. Recording them as triples would
duplicate a derivable fact, which could then disagree with its own inputs — the defect L-91 names,
one level down.

Only two things could not be derived:

| Term | Why it must be stored |
|---|---|
| `iterationStart`, `iterationEnd` | Velocity is work completed **per iteration**; without a period there is no denominator and the measure cannot exist |
| `Forecast` — `forecastFor`, `forecastMadeAt`, `forecastCompletion`, `forecastAssumption`, `forecastObservedVelocity`, `forecastIterationsObserved` | A forecast is a **claim about the future**. At least one assumption is required: a forecast presented without them asks to be believed rather than checked, and when it misses there is nothing to point at as the thing that failed. The velocity and the iteration count are required so the arithmetic is checkable and so a forecast built on one iteration is distinguishable from one built on a settled average |

The report prints remaining-work arithmetic and says explicitly that **it is arithmetic, not a
`Forecast`** — the projection is free, the claim carries obligations. An advisory fires when a
forecast's date passes with work still open.

### 2.5c-v Lineage completeness — why absence needs its own check

**`sh:targetClass` cannot see absence.** A shape guarding `ScopeStatement` has no target in a
register containing zero of them, so the constraints written to govern a layer are exactly the ones
that go silent when the layer is omitted entirely. This is a structural property of SHACL, not a gap
in any particular suite.

The consequence is not hypothetical. This framework's own development register declared **L2**,
reported **zero violations**, and contained no scope, no exclusions, no Definition of Done, no
decomposition and nothing below epic level. It was called a lineage; it was four epics and a sentence
each. The same pattern was reported independently in parallel sessions.

**`LineageCompletenessShape` targets the register itself** — the one node guaranteed to exist — and at
L2 refuses a register with no `Mission`, no `Objective`, no `ScopeStatement`, or no
`DefinitionOfDone`. At L3 it refuses scored `Epic`s that decompose into nothing: an epic is by
definition delivered across multiple features or stories, so one with no children is an estimate with
no plan behind it. Advisories cover thinness rather than absence — epics with no work beneath them, a
scope statement with no exclusion.

**`backlog_lineage_completeness_v1_1_0.py`** complements the shape rather than duplicating it: it
reports at **any** level, names every absent layer, and states what each omission costs — so a
register can be improved before it is failed. It runs inside the release gate.

The division is deliberate. The shape is the gate; the reporter is the map. A register climbing
toward a level needs to see the gap before the gap fails it.

### 2.5c-v The plan alongside the roadmap (subject v1.15.0)

A **roadmap orders**; a **plan dates**. They now coexist and are deliberately different artifacts —
horizons stay ordinal, `hasRoadmapRank` stays an ordering, and neither acquired a date.

| Term | Purpose |
|---|---|
| `KickOff` — `kickedOffAt`, `hasKickOffMode` / `KickOffMode` (`Declared`/`Triggered`), `hasKickOffTrigger` | Day zero. A baseline of dates anchors to nothing without it. A declared kick-off must name who; a triggered one must name the trigger, so a start that was *claimed* is distinguishable from one that was *recorded* |
| `plannedStart`, `plannedFinish` | The baseline. Kept distinct from `startedAt`/`finishedAt`: the gap between them **is** schedule variance, and collapsing them would make every plan appear met |
| `hasDuration` | Elapsed days, **not** effort — two people for a day and one for two days share an effort and differ in duration. A critical path is the longest chain of durations |
| `PlanBaseline` — `baselinedAt`, `isCurrentBaseline` | Moving a plan is a recorded `Rebaseline`, not an edit. Superseded baselines are **retained**, so performance stays computable against the original as well as the current — the figure a rebaselined project would rather not show |

`backlog_views` derives **Gantt, burn-down, cumulative flow, network/AON and earned value** from these
plus facts already recorded. **Nothing is stored.** Where a view needs day zero and no `KickOff`
exists it **refuses and says so** rather than defaulting to today, which would make every plan appear
on schedule on the day it is read.

**This reverses a standing scope exclusion.** `Ex_Schedule` refused a time-phased baseline; it is
**not deleted** — it records a decision that was true when taken. A `ScopeChange` supersedes it and
both stay readable.

### 2.5c-vi Multi-dimensional cost (subject v1.17.0)

An increment worked by an automated agent under human supervision has a **token** cost *and* a
**compute** cost *and* a **human** cost. Collapsing them into one effort figure loses the fact that
they trade off against each other.

| Term | Purpose |
|---|---|
| `CostDimension` — `hasDimensionUnit`, `hasDimensionRate`, `hasRateCurrency` | A named axis with its own unit. **Deliberately open**: tokens, compute, review time and assessed complexity are *instances*, not predicates. A property called `tokenCost` would privilege LLM-driven development the way a story-point property would privilege one estimation practice |
| `DimensionalCost` — `costOfItem`, `alongDimension`, `hasQuantity`, `isEstimatedCost` | One quantity of one dimension for one item, reified so an item can carry several at once. `isEstimatedCost` keeps forecast and observed separable — a total mixing them without saying so reads as measurement |
| `Budget` — `budgetFor`, `budgetDimension`, `hasBudgetCeiling` | Per-dimension, not per-project-total: an aggregate budget cannot say *which* thing overran, and unpriced dimensions have no aggregate to belong to |

A rate is **optional**. An unpriced dimension is reported separately and contributes to no monetary
total — a choice, not an omission, because some costs are constraints rather than bills.

**Roll-up is derived, never asserted.** Recording a cost on a parent *and* its decomposition child
along the same dimension is rejected: it double-counts, exactly as a parent and child both carrying
priority scores would.

### 2.5c-vii Human in the loop and on the loop (subject v1.18.0)

A register of automated development that cannot say **where a person decided** is not auditable
afterwards — every item looks the same.

| Term | Purpose |
|---|---|
| `ExecutionModality` — `Human` / `Automated` / `Hybrid` | Who produced the output. `Human` work **competes for capacity**; hiding it over-commits the one resource that does not scale. `Hybrid` means a person materially changed the output, which is a different answer to *who is answerable* than automated-with-review |
| `SupervisionMode` — `Sup_InTheLoop` / `Sup_OnTheLoop` / `Sup_None` | **A fact about gating, not attitude.** In-the-loop: the work *cannot advance* until a person acts. On-the-loop: it advances and a person may intervene. *"We review everything"* and *"nothing proceeds without review"* are different systems that sound identical in prose |
| `HumanInteraction` — `interactsWith`, `hasInteractionKind`, `interactedAt`, `interactedBy`, `gatesTransition` | An **event**, deliberately not a work item: per the governing scope exclusion, human *interaction with* work does not compete for capacity, or every review needs a score and the backlog fills with process. Its cost rides the same dimensional machinery, so review time is **budgetable without being schedulable** |
| `InteractionKind` — Confirm, Reject, Correct, Propose, Review, Respond | Confirm and Reject **gate**; the rest inform. A vocabulary with only *"review"* cannot distinguish a person who approved from one who merely looked |

**Supervision claims are checkable, not declarative.** Claiming in-the-loop with nothing recorded as
gating is rejected — the claim would describe an intention rather than a mechanism. Claiming no
supervision while a person gated it is rejected. Correcting an output while claiming `Automated` is
rejected.

An **advisory** fires where gating confirmations exist and no rejection ever has: *a check never
observed to fail has not been shown to be a check* — the same reasoning this framework applies to its
own gates, turned on human ones.

### 2.5c-viii Epics are decomposed before they are planned

The type system says `Epic ⊑ ProductBacklogItem` and `plansItem` ranges on `ProductBacklogItem`, so a
`PlanningEvent` **may be asserted** over an Epic. The **definitions** say otherwise:

- an **Epic** is *"a large body of work decomposed into, or delivered across, **multiple** features or
  stories; its completion **typically derived from the completion of its constituent work**"*
- a **Story** is *"small enough to be **completed within one iteration**"*
- an **Iteration** is *"a fixed-length time box"*

An epic with no children committed to one time box can neither fit it nor derive a completion from
anything. `EpicPlanningShape` rejects it at L2. **Decompose first, then plan the parts.**

The gap is worth naming because a subclass relation answers *what may be asserted* and a definition
answers *what the term means* — different questions, and reading only the first is how this
arrangement came to be described as permitted.

### 2.5c-ix A story fits its iteration; a deployment says how it chose

**`StoryIterationFitShape` (L4)** — a story planned into more than one iteration, or still open after
its iteration closed, is rejected. Each message names **splitting** as the remedy and says not to
widen the iteration: *a box sized by what it contains always fits, and its velocity can then never
report a miss.* Splitting needs no new relation — `decomposesInto` already reads *"a feature into
stories"*.

**`SelectionBasis` — `Sel_HighestScored` / `Sel_Dependency` / `Sel_Committed` / `Sel_Opportunistic`**,
with `passedOver` and `hasSelectionRationale`. At L4 a `DeploymentUnit` must say on what basis its
contents were chosen; a release grouped by theme and a release of the most valuable available work are
otherwise indistinguishable, and only one is a prioritisation decision.

**This is not a rule that a release must always take the top score.** An ordering is a model and is
sometimes wrong, and a rule with no exception path is bypassed the first time it is. What is enforced
is that the departure is **visible**: claim `Sel_HighestScored` while a higher-scored deliverable item
waits, and it must be named in `passedOver` with a reason. `Sel_Opportunistic` is a legitimate answer;
not answering is not.

### 2.5c-x Adapting a lineage to scope-first, under gates

`LineageAdaptation` converts one scope-last boundary, through four ordered stages —
**Assess → Fit-gap → Ruling → Re-link** — each controlled by an `AdaptationGate` carrying an
executable check, an expected result and an observed one. `AdaptationStage` and `AdaptationOutcome`
are the closed sets; `FitGapFinding` names each item found outside the boundary, with a reason.

| Rule | Why |
|---|---|
| The fit-gap gate passes on having **measured**, not on the boundary being intact | A gate that only passed when it found nothing would report its own preferred answer |
| `Adapt_BoundaryHolds` is rejected if any finding exists | It is the outcome an inspection reaches by default — a boundary drawn around past work fits that work by construction |
| `Adapt_BoundaryRewritten` requires a **new** `ScopeStatement` and a `ScopeChange` | The old boundary records what was believed at the time; editing it erases the reason the adaptation was needed |
| `Stage_Relink` requires a recorded outcome | Re-linking before the ruling **is** the in-place conversion the procedure exists to prevent |
| A gate marked passed whose observed result contradicts its expectation is rejected | Otherwise the verdict is whatever the author wanted |

### 2.5c-xi Initiative kind, and the version increment that decides it

`InitiativeKind` classifies the **Initiative** — portfolio granularity — never an epic or a story. An
epic is a theme *within* an initiative and inherits its classification; an advisory fires if one
carries a kind of its own.

**Project scale — forces a MAJOR increment**

| Kind | What it is |
|---|---|
| `Kind_InitialDevelopment` | The first build. No installed base, no compatibility to preserve — decisions are unconstrained in a way they never are again |
| `Kind_EvolutionaryDevelopment` | A new version after an earlier one is complete. Still a project, still a major, but constrained: something exists and is in use |
| `Kind_Migration` | Same capability, new environment or platform. A distinct ISO 14764 process |
| `Kind_Retirement` | Withdrawal from service. Ends a version line rather than advancing it |

**Maintenance scale — a MINOR or PATCH, never a major.** `VersionIncrement` carries that movement. Maintenance is classified on the ISO 14764 grid, whose axes are `MaintenanceTiming` and `MaintenanceGoal` and whose derived cell is `MaintenanceCategory`:

| | **Correction** | **Enhancement** |
|---|---|---|
| **Reactive** | `Maint_Corrective` | `Maint_Adaptive` |
| **Proactive** | `Maint_Preventive` | `Maint_Perfective` / `Maint_Additive` |

**The version increment is the discriminator, and it is enforced.** *"Does this create new
capability"* is a judgement; *"did this force a major"* is a fact about what shipped. So:

- maintenance producing a **major** is rejected — that is evolutionary development mislabelled,
  which is the commonest miscategorisation and happens because the work touched an existing product
- initial or evolutionary development producing anything **less than a major** is rejected — if the
  increment is right, the kind is wrong
- retirement producing a versioned increment is rejected
- at L3 an initiative must state both its kind and its increment

`ModificationRequest` and `ProblemReport` are 14764's terms for what arrives and triggers maintenance;
at L3 reactive maintenance must name one, because reactive work answers something that arrived and its
scope has no other source.

### 2.5c-xii A mission says where its words came from

`MissionOrigin` — `Origin_OwnerStated` / `Origin_SessionDrafted` / `Origin_Derived` — with
`missionSource` and `supersedesMission`.

`decidedBy` records who is **accountable** for a mission. Nothing recorded who **authored** it, and
the two diverge silently when a session drafts a statement and attributes it to the owner. That
divergence is not hypothetical: this package's own register carried five missions marked
`decidedBy Owner` that a session had written, each after the work it described, each narrower than
the last.

**It is the scope-first failure one level higher.** A mission written after the work summarises that
work, and a summary cannot contradict its source — so the mission stops being able to refuse anything,
exactly as a scope drawn around fixed objectives does.

At **L2** a mission must state its origin. At **L3** an owner-stated or derived mission must name its
source, because *"the owner said so"* with no pointer to a dated instruction or document is
indistinguishable from a session's paraphrase. An advisory reports a session-drafted mission; another
reports a mission no goal advances. Superseded missions are **retained**, since the distance between a
drifted mission and its correction is the most useful record the drift leaves.

### 2.5c-xiii The intent chain closes

```
Mission ← scopeForMission ← ScopeStatement ← fillsScope ← Objective
   ↑                                                          ↑
   └── contributesToMission ← Goal ← contributesToGoal ────────┘
                                                               ↑
                          WorkItem ── pursuesObjective ────────┘
                          Roadmap  ── roadmapRealises ─────────┘
```

Every link points from the later-written element to the earlier, so the chain records its own build
order and can be walked in one query.

**`scopeForMission` closed the gap that mattered.** The ceremony order is Mission → Scope → Goal →
Objective, and the step it puts *second* was the one the vocabulary never recorded: a scope hung off
its container, the mission hung off the same container, and the two met only through a join on what
they shared. With more than one mission on a container — this package's own register had **six
missions and four scopes** — which scope served which was unanswerable, and no rule could check that
work sat inside the right boundary.

**`roadmapRealises`** puts the roadmap on the chain. Without it a roadmap connects to its backlog and
nothing above: the ordering can be read, and what the ordering is *for* cannot.

| Level | Rule |
|---|---|
| L2 | A scope names the mission it serves |
| L3 | An objective reaches a Mission through a Goal — an objective advancing no goal measures something nothing has a stated reason to want |
| L4 | **No forked chain**: an objective filling a scope drawn for one mission while its goal advances another is rejected. The boundary that admitted the work and the purpose it serves must agree, or every downstream figure is computed over two different intents |
| advisory | A roadmap naming no objective |

### 2.5c-xiv Grooming: what a story was analysed for

`DesignConcern` — `Concern_Data` / `Interface` / `Interaction` / `Architecture` / `Security` — from
the design activities in **Satzinger, Jackson & Burd, ch.6**. Adopted as *concerns* rather than
activities: the framework governs the register a method produces, so what it can check is whether a
story was analysed against the dimensions that apply to it, never whether a team performed a named
activity in a named order.

`RefinementEvent` already carried an outcome, a time and an actor, and **one event of any kind
satisfied Ready** — so a story with five applicable concerns and a single meeting was indistinguishable
from one fully analysed. `addressesConcern` records what a refinement looked at.

`hasApplicableConcern` is **declared per story, not derived**: whether a story touches persistent state
is a judgement about the work, and no query can make it. The declaration is what makes grooming
checkable at all.

`hasNoApplicableConcern` requires a **written reason** rather than allowing silence, because a story
that was never groomed and one that genuinely needs no design analysis are otherwise identical in the
data — and the first is the common case.

At L3: a story past Proposed must declare concerns or state that none apply; every declared concern
must have a refinement addressing it. At L1, claiming both is rejected. An advisory reports a
refinement naming no concern — it still counts as a refinement and can count toward nothing.

### 2.5c-xv Task types: which technical process a task performs

`TaskType`, from **ISO/IEC/IEEE 12207 clause 6.4**, taken whole rather than sampled:

| | |
|---|---|
| `Task_MissionAnalysis` | 6.4.1 — what problem, and why. Domain engineering |
| `Task_StakeholderNeeds` | 6.4.2 — what people need, as stated requirements |
| `Task_RequirementsDefinition` | 6.4.3 — what the system must therefore do |
| `Task_ArchitectureDefinition` | 6.4.4 — structure, and what cannot change cheaply later |
| `Task_DesignDefinition` | 6.4.5 — detail sufficient to implement |
| `Task_SystemAnalysis` | 6.4.6 — trade studies and feasibility. Technical analysis |
| `Task_Implementation` | 6.4.7 — builds the element |
| `Task_Integration` | 6.4.8 — correct parts that do not compose |
| `Task_Verification` | 6.4.9 — was it built right |
| `Task_Validation` | 6.4.11 — was the right thing built |
| `Task_Transition` | 6.4.10 — into operation. Deployment |
| `Task_Operation` · `Task_MaintenanceTask` · `Task_Disposal` | 6.4.12–14 |

`ExecutionTask` previously carried **no properties of its own** — a task could say what it was called
and not what kind of work it was. `hasTaskType` is functional: a task spanning two processes is two
tasks, and splitting it is what makes either estimable.

**`coversTaskType` is the join between grooming and execution.** A design concern implies work of
particular kinds — Data implies design definition, Architecture implies architecture definition,
Interaction implies validation. A story groomed for a concern whose implied task type never appears
among its tasks was **analysed and then not acted on**, which is the state where grooming becomes
ceremony. Reported as an advisory.

A second advisory fires on a register holding implementation tasks and neither verification nor
validation: a backlog can look full while every process other than building is invisible.

**Not a workflow.** The framework records what kind of work a task was, never that the processes were
performed in a prescribed order.

### 2.5c-xvi Iteration capacity, and the roles the framework ships

**`hasCommittedEffort` is recorded, not derived.** Derived would be the sum of what is planned in
*now*, which moves as work is added — and a number that moves cannot report an over-commitment. The
question the discipline asks is what was committed **at commitment**, against the capacity known then.

At L3 an iteration committing beyond its capacity is rejected: an iteration is a fixed time box, and
committing beyond capacity means the box was sized by the work rather than the work by the box.

At L4 **a deployment carrying an item its iteration never planned is rejected.** A package shipped
from an iteration is what that iteration committed to and finished; work entering by another route
makes the iteration's record of itself untrue and cadence stops being measurable.

**Six `TeamRole` individuals ship**, each naming its source: systems analyst and design authority
(Satzinger et al.), architect (ISO/IEC/IEEE 42010), HCI researcher (ISO 9241-210), tester and test
manager (ISO/IEC/IEEE 29119-3).

`TeamRole` is **open**, so this prescribes nothing — a register using none stays conformant, and one
needing a role not listed adds it. `hasRoleSource` is checked on the **framework namespace only**:
the framework must defend its own vocabulary, and cannot demand a citation for a role an adopter
needs locally.

### 2.5c-xvii Four mechanisms against intent drift

**`IntentOrigin`** — `IOrigin_OwnerStated` / `IOrigin_SessionDrafted` / `IOrigin_Derived` — on
`ScopeStatement`, `Goal` and `Objective`, alongside `MissionOrigin` on `Mission`. `decidedBy` records
who is accountable; nothing recorded who authored. Applying the fix to the mission alone moved the
blind spot one level down rather than closing it.

**`derivesFromScope`** (Goal → ScopeStatement) — the chain is **Mission → Scope → Goals →
Objectives**, and goals are derived from the scope so that the scope's fit to the mission is what gets
tested. Without it, `Goal` carried only `contributesToMission` and the scope sat outside the path
between a goal and its mission. At L4 a goal serving a mission its scope was not drawn for is rejected:
the chain must read the same in both directions.

**`metricMovableBy`** (Objective → WorkItem) — `pursuesObjective` records *intent*; this records
*capability*. An epic can pursue an objective and be unable to shift its metric by construction, which
is how a register reaches every epic Done with its objectives untouched. When the two disagree,
**adjust the backlog, not the objective**.

**Deployment coverage** — an advisory on any Done item in no `DeploymentUnit`. Work reaches users
through regularly deployable packages; a register where completion and delivery are separate records
measures the first and assumes the second.

### 2.5c-xviii Every shipped term declares its provenance

`Ex_InventedPractice` says no practice the framework **requires** may lack a named external source. It
was a scope exclusion a reader had to honour, with **nothing checking it** — so two ungrounded
practices sat in the framework for twenty releases while the objective measuring them never moved.

`PracticeGroundingShape` makes it checkable: every term the framework ships in its own namespace must
carry either a `dcterms:source` or an `isFrameworkOriginal` declaration.

**`isFrameworkOriginal` requires a written reason**, not a flag. A practice nobody sourced and a
practice deliberately invented are otherwise identical in the data — and the first is the common case.
`Sel_Opportunistic` is the framework's one declared original: release-planning literature names value,
dependency and commitment, and does not name a category for a release that was not a prioritisation
decision at all.

The point is not that every term has a citation. It is that **no term is silent about its provenance**.

### 2.5c-xix A scope enumerates what it requires

`ScopeDeliverable` with `requiresDeliverable` (Scope → Deliverable) and `satisfiesDeliverable`
(WorkItem → Deliverable).

**A scope of prose has nothing to measure work against.** Coverage then gets computed over the work
that happens to exist, and both sides of the fraction are the backlog — so the figure reads complete
whether the scope was satisfied or merely emptied. Whatever the epics deliver becomes the definition of
what the scope wanted.

A deliverable states **what must be true**, not what someone will do, and is enumerated when the scope
is written — before any goal, epic or story. `satisfiesDeliverable` points from work to requirement, so
work cannot name a deliverable that does not yet exist.

At L3 a scope enumerating nothing is rejected. Advisories report a deliverable nothing satisfies, and
an epic satisfying no deliverable — work the scope never asked for.

**The test of a real boundary is that its coverage figure can fall.** Add a deliverable nothing
satisfies and it drops immediately; a figure that cannot fall is not measuring anything.

### 2.5c-xx The lineage as a pipeline

`LineageStage` — Mission → Scope → Goal → Objective → Backlog, chained by `stagePredecessor`. Each
stage closes with a `StageOutput` carrying `hasStateDigest` and `closedAtCommit`; the next stage's
output `consumesOutput` the previous. Elements reference their stage via `producedByStage`.

**The dependency is an artifact, not a claim.** An element cannot reference an output that does not
exist.

**What is enforceable, established by experiment rather than argument:**

| | |
|---|---|
| Digests **catch fabrication** | A backwards lineage with invented digests fails recomputation on every stage |
| Digests **do not catch careful backwards construction** | An author who computes each digest by restricting the *final* graph per stage passes every check — a digest over the register is computable at the end |
| Order needs an **external witness** | `closedAtCommit` names a commit: append-only, held by a remote the author does not control |
| The witness has a **measured limit** | Git orders *between* commits, not *within* one. A lineage authored in a single commit is unordered evidence however it was built — reported by advisory |

`backlog_pipeline_verify` recomputes every digest and checks the chain is a line; the release gate runs
it over both pipeline fixtures and requires each to verify as its name declares.

### 2.5d Decomposition, commitments, dependency kinds, impediments, flow, team (subject v1.4.0)

| Term | Meaning |
|---|---|
| `decomposesInto` / `partOf` | The epic-feature-story ladder as a part-whole relation; non-transitive so roll-up cannot double-count. A parent may not be Done over an open child, and parent and children may not both carry scores |
| `decompositionState` | The state a parent's children support, derived by rule R8 |
| `Commitment` + `commitsToGoal` / `commitsToObjective` / `commitsToDefinitionOfDone` | What an artifact commits to: a backlog to a goal, an iteration to an objective, an increment to a Definition of Done |
| `Dependency` + `DependencyKind` | Reified dependency over a closed set — knowledge, task, resource — because the kind determines what would release it |
| `Impediment` | An obstacle that is not a dependency: cleared by someone acting outside the register, not by finishing work. Unresolved ones must be owned |
| `startedAt` / `finishedAt`, `WipLimit` | The well-defined points every flow measure is defined against, and work-in-progress as a *policy* distinct from the measure |
| `Team`, `TeamRole` (open), `hasCapacity` | Who delivers. `Role` stays closed at Owner/Builder because it governs who may *decide*; team organisation is the adopting method's business |
| `asRole` / `wantsCapability` / `soThat` | The canonical user-story clauses, with an advisory when the "so that" is missing |

### 2.5e Falsifiability — how a register can be wrong (subject v1.5.0)

Added after an adversarial register — arbitrary scores, "asserted" verification, an unobserved
objective past its deadline, Gherkin-shaped noise — validated at L3 with **zero** violations. Every
term here exists so that a plan can fail visibly.

| Term | Meaning |
|---|---|
| `MetricObservation` | A dated, method-bearing measurement of a metric — the missing half of an objective |
| `hasTargetDirection`, `MetricDirection` | Which way the metric must move; without it a target cannot be contradicted |
| `objectiveOutcome`, `milestoneOutcome`, `AchievementStatus` | Derived Met / Missed / Pending — **Missed** is a first-class computed outcome |
| `Rebaseline` | Owner-decided target moves, previous value retained, rationale required — the control against quietly editing the target until the outcome matches |
| `hasActualEffort` | Required on completed estimated work, so an estimate can be shown to have been wrong |
| `verifiedByTool` | Required at L3; closes the loophole that let a human write `evidenceVerified true` with the method "asserted" |

Enforcement added with them: WSJF and RICE values checked against their own components; scores
predating the last completion rejected at L3 (BP-D11); objectives whose target equals their baseline
rejected; Gherkin-shaped but empty acceptance criteria rejected; items tracing to no objective
rejected at L3; a roadmap rank contradicting the score order required to carry a rationale.

### 2.5f Register packaging (subject v1.7.0)

| Term | Meaning |
|---|---|
| `RegisterPackage` | The shippable unit of an adopter's governance data: version, manifest, and the artifacts below |
| `RegisterArtifact` + `ArtifactRole` | Closed five-role set: register data, progress report run, evidence index, manifest, profile declaration |
| `conformsToNamingConvention` | Points at a `configuration:NamingConvention` **by IRI**; patterns are never copied, and the package checker reads them from the pack at check time |
| `hasManifestSHA256`, `reportRunRetainedAs` | The manifest carries its own digest; progress runs survive the terminal |

**Which convention governs which file** — settled under the conventions as ruled, no local minting:

| Role | Convention | Basis |
|---|---|---|
| Register data (`.ttl`) | `configuration:ABoxFileConvention` | Ruled at OE Pack v20.23.41: that convention governs governance-register data |
| Progress report run (`.ttl`) | `configuration:ABoxFileConvention` | A retained run is register data in the same sense; follows the pattern exactly, no form divergence, so L-110 says enrich rather than mint |
| Progress report run (`.md`) | `configuration:AuditReportMarkdownConvention` | Follows `{name}_v{M}_{m}_{p}.md` exactly; again no form divergence |
| Profile declaration, evidence index (`.ttl`) | `configuration:ABoxFileConvention` | Instance data of this subject |
| Manifest | none | Not an ontology artifact; named `MANIFEST_SHA256.txt` by pack practice |

### 2.6 Governance

| Term | Meaning |
|---|---|
| `MethodologyRule` | `hasRuleLogic` + `closesDisagreement` + `hasMotivatingIncident`, all required |
| `ReleaseGate` | Gate 0 (manifest), Gate P (parse), Gate K (version identity), Gate R (SHACL reconcile) |
| `CrossCuttingInvariant`, `InvariantStatus` | Executable standing checks with an honest third value. `NotYetEnforceable` + `tracksItem` is the framework's record that **a mechanism is disclosed broken and the work that would fix it is named** — and at L1 that record now carries two obligations: the tracked fix cannot reach `Done` without Evidence, and the invariant cannot stay `NotYetEnforceable` once every item it tracks is `Done`. The trigger is **derived from the invariant**, never self-declared, so it catches the case whether or not anyone remembers to flag it |
| `AdoptionProfile`, `ConformanceLevel`, `FrameworkFacet` | The reuse mechanism |
| `lastAuditedAt`, `hasAuditNote` | Per-item re-verification; absence means unchecked |

---

## 3. Conformance levels

| Level | Enforced |
|---|---|
| **L1 Core** | Unique identifiers, one state, well-typed references, no dependency cycles, rationale on cancellation, one live score per method, containers non-empty and consistent with their derived state, roadmap items present in a register, milestones dated and backed by work, launch gates owner-decided with a priority, launch priority only on declared launch gates, container scores judged not averaged, scoreability flags carrying reasons, disclosures matching edges, gaps and rules and reports and documents well-formed |
| **L2 Evidence-Bound** | L1 + Done requires at least one verified Evidence; a Done item may not depend on unfinished work; **no silent gaps**; profile must adopt the Evidence facet |
| **L3 Governed** | L2 + Done anchored by verified test or release evidence; `lastAuditedAt` recorded; **full life-cycle sweep per domain entity**, every stage covered or explicitly gapped; profile must adopt Invariant and Audit facets |

**The rule that generates the split**, stated because a careful reader had to ask for it: **L1
constrains the well-formedness of what you author; L2 and above require that you author it.** If a
register declares an `Objective`, an L1 shape insists it carry a metric, a baseline and a target —
authoring a half-built one is a structural defect at any level. Whether the register must *have* an
objective at all, whether a scope must *realise* one, whether every item must *trace* to one: those
are claims about coverage, and they arrive with the conformance level that promises them.

This is why, for example, `ScopeMeasurabilityShape` is silent below L2. An L1 adopter has claimed
structural integrity and nothing about intent, so demanding that its scope statements name objectives
would fail it against a promise it never made. The same reasoning places `GoalMeasurabilityShape`,
`IntentTraceabilityShape` and the mission-coverage constraint above L1, while `GoalShape`,
`BenefitShape`, `ScopeExclusionShape`, `CostEstimateShape` and their siblings stay unconditional.

L2 and L3 shapes fire only when an `AdoptionProfile` claims that level.

**L4_LineageEnforced** is the fourth level, for a register that must **prove a mission was
accomplished** rather than report that work was done — the difference being that completion is a fact
about effort and accomplishment is a fact about the world, and only the second requires a
measurement. At L4 the checks that are advisory below become **violations**:

| L4 requires | Why |
|---|---|
| Every item traces to an objective | An item nothing can measure the value of has a completion but no accomplishment |
| Every objective carries a `MetricObservation` | A target with no reading is an intention; a mission cannot be shown accomplished from intentions, however many are Done |
| Every epic decomposes | Ungroomed it schedules nothing and can be picked up by no one |
| **No epic in an Iteration** | An iteration is a time box; an epic is delivered *across* stories. Putting a theme in a sprint looks like planning and commits nothing anyone can finish |
| **No epic in a `DeploymentUnit`** | A deployment answers *what users received*; an epic answers *why* |
| Stories reaching execution passed through a `PlanningEvent` | Work that reached execution without planning has no recorded commitment behind it |
| A closed iteration connects to a `DeploymentUnit` via `deploysFrom` | Otherwise an iteration closing and a release shipping are unrelated events, and a slipped iteration cannot be connected to a delayed release |
| **Every deployed item is Done, carries bridge-verified Evidence, and has every acceptance criterion attested** | A release is the claim work reached users. Carrying unfinished or unproven work makes that claim false for part of what shipped, and nothing downstream can tell which part. The criterion check is **coverage at release time**: a suite can be green while the thing everyone cared about is untested |
| **A deployment records who released it** | Shipping is an act someone performed; a release nobody authorised cannot be questioned afterwards |
| No item pursues an objective the scope does not realise | Scope drift in its literal form: either record a `ScopeChange`, or the work does not belong here |

**Test coverage is not new vocabulary.** `TestHarness.harnessComplete` is derived true only when
**every** acceptance criterion of an item is attested by a bridge-verified evidence artifact — that
*is* per-item coverage, and it existed long before L4. What was missing was consulting it at release
time: a deployment could ship an item that was `InProgress`, carried no evidence and had no attested
criterion, and nothing objected.

`DeploymentUnit` is new and exists to separate three things this framework has repeatedly seen
conflated: **what shipped** (deployment), **when it was worked** (iteration), and **why** (epic).

**A companion discipline document ships with the package.**
`04-documentation/LINEAGE_OPERATING_DISCIPLINE_v*.md` states the six boundaries the shapes cannot
reach — granularity by momentum, advisory blindness, permitted-is-not-intended, completion-is-not-
accomplishment, the why/when/what conflation, and drift as the default — each with the shape that
catches it where one can. It governs building a lineage; the OE Operating Discipline governs building
and releasing the ontology, and where both apply the OE ceremony runs first. **Its enforcement claims
are themselves gated**: `backlog_lineage_discipline_check` fails the release if a shape the document
names has been renamed, softened, or re-levelled, because a discipline document whose claims have
drifted is believed.

**L4 is a separate level, not a promotion inside L3.** Promoting checks inside an existing level
would silently break every adopter who made a different claim, and a level is a claim an adopter
makes rather than one imposed on them.

**The declaration is itself governed, and those constraints are never level-gated.** Declaring
`L1_Core` suppresses every level-gated constraint at once — on the shipped negative fixture,
changing that one token removes most of the violations without changing another byte. The figures
are in `RELEASE_METRICS.txt` and on every validator run; they are not restated here, because a
number in prose goes stale the moment the suite changes. Every other opt-out in this
framework — `notYetScoreable`, `ScopeExclusion`, `Rebaseline`, `ScopeChange`, an accepted risk, a
ranking-fork resolution — already requires a written rationale, and four require an owner decision.
The conformance level suppressed more than all of them combined and required neither.

The tier mechanism is an **adoption ramp**: a framework demanding everything on day one is adopted
by nobody. Its misuse is as **permanent shelter** — a ramp used as a parking space. So the framework
does not forbid a low level. It requires the choice to be:

| | |
|---|---|
| **owner-decided** | `decidedBy backlog:Owner` — the largest opt-out cannot be made by nobody in particular |
| **reasoned** | `hasDecisionRationale` — why this level and not a higher one |
| **directional** | `hasTargetConformanceLevel` — a ramp with no destination is a parking space; a target equal to the current level is rejected as standstill encoded as ambition |
| **dated** | `hasLevelReviewDate` — not a deadline to reach the target, a date on which someone must look again; an advisory fires once it passes |
| **irreversible-in-the-open** | `hasPriorConformanceLevel` + `hasDowngradeRationale` — downgrading is permitted, downgrading silently is not |

**Wiring the ramp into the work — a recommended pattern, not a requirement.** `hasTargetConformanceLevel`
names a direction; it does not by itself create any work that would get you there. An adopting project
carried a declared L2 target for over a week while the work that would satisfy it proceeded as
separately-motivated casework, with no goal anywhere in the register naming *"reach L2"* as what it
was for — so advancing the level took a dedicated conversation rather than falling out of the
register's own priority computation.

The pattern that closed it uses vocabulary the framework already ships: a `Goal` for the governance
maturity, an `Objective` whose metric is the target level's **own SHACL violation count measured by
declaring it in a trial run** — falsifiable, re-runnable, and not a number anyone invented — and
`WorkItem`s that `pursuesObjective` it, scored like everything else. The ramp then competes for
capacity on the same terms as feature work instead of losing to it by default.

**But note the framework's own answer to that competition**, which is stronger than scoring meta-work
higher: `PortfolioPolicy` and `CapacityAllocation` exist precisely so categories that answer to
different arguments are not arbitrated by one score. Governance maturity, technical debt and new
capability compete badly on a single ranking; an allocated share is the instrument for that, and a
declared target with no allocation behind it will lose whatever its score says.

**The formal link does not exist, deliberately.** `hasTargetConformanceLevel` is on `AdoptionProfile`,
which is a `BacklogConcept` and cannot carry `pursuesObjective` — so the connection between a declared
target and the objective pursuing it is narrative, not a checked triple. A property closing that gap
was flagged by the reporting project and **not requested by it**, on the grounds that one producer's
evidence is not enough (L-110). That judgement is accepted and recorded here so a second adopter
meeting the same wall finds the option already on the table.

Every run also reports the **suppression cost** on its own `level:` line — how many level-gated
constraints did not run, computed from the suite at run time rather than written down. A clean
result at a low level and a clean result at a high level previously printed identically. They are
not the same claim.

**None of this stops a determined party**, and the framework does not pretend otherwise: the
register is authored by the same people who declare its level. What these constraints do is make
the choice attributable, reasoned and dated — which is the whole of what governance can do about a
self-declaration, and considerably more than nothing. Conformance means zero
results at `sh:Violation` severity; advisory results never constitute failure. Every verdict is
printed with the shapes file, its hash, the tool versions and the mode.

---

## 4. Adoption

```bash
pip install rdflib pyshacl --break-system-packages

# 1. Declare adoption (namespace, level, facets) — see the positive fixture
# 2. Write the register: blueprint, items, containers, evidence
# 3. Verify evidence against the real workspace
python3 03-tooling/backlog_evidence_bridge_v1_0_0.py my_register.ttl \
        --workspace /path/to/repo --test-command 'npx playwright test {spec} --grep {id}'

# 4. Compute the roadmap — never write one by hand
python3 03-tooling/backlog_roadmap_report_v1_5_0.py my_register.ttl --emit report.ttl

# 5. Run the four-gate release check (self-proving)
bash 03-tooling/backlog_gate_v1_1_20.sh my_register.ttl
```

Start at L1, move to L2 once a bridge exists, and to L3 when releases carry manifest hashes and the
blueprint sweep is real. Raising the level is a one-line edit to the profile.

---

## 5. What the gates prove, and what they do not

`backlog_gate_v1_1_20.sh` runs Gate 0 (manifest self-verify), Gate P (every Turtle file parses),
Gate K (`versionInfo` == `versionIRI` token == filename token), Gate R (SHACL reconcile), and the
BP-D31 coverage gate. Gate R first validates a positive fixture that must pass and a negative
fixture that must fail, and aborts if either outcome inverts: a suite never shown to reject a
known-bad register verifies nothing about a good one.

**Measured figures are not restated here.** Every number the gates produce — fixture violation
counts, planted-defect totals, version-identity checks, source and documentation coverage — lives in
`RELEASE_METRICS.txt`, which is generated by `backlog_release_metrics_v1_1_0.py`, records the
manifest SHA-256 it was produced against, and regenerates byte-identically from any directory.

That is L-91 applied: prose that duplicates a machine-readable fact goes stale the moment the fact
moves, and the discipline is to point at the field rather than mirror it. This document previously
mirrored a fixture measurement and was three releases out of date before a reader caught it — the
gates all passed throughout, because none of them compared a stated number with a computed one.
`backlog_doc_coverage_gate_v1_2_0.py` now refuses any restated measurement in this document.

What does not go stale, and is therefore stated here: the gate runs **three** mandatory fixtures —
a positive one that must pass, a negative one that must fail, and an adversarial register that must
be rejected — and aborts if any outcome inverts.

Two of these deserve emphasis because they test the tester: one planted defect (a container
asserting Done over an in-progress member) is detectable only if the derivation rules executed,
and the R3 fixture exists because a rule whose disagreement branch has never been seen firing is a
branch nobody has tested.

---

## 6. Extending without forking

- **New item kind, capability class, enforcement domain, or prioritisation method:** create it in
  your own namespace. These classes are open for exactly this.
- **Project-specific constraints:** ship your own shapes importing `http://example.org/backlog`;
  run both suites.
- **Never widen the closed enumerations** (`LifecycleState`, `RoadmapHorizon`, `InvariantStatus`,
  `ConformanceLevel`, `FrameworkFacet`, `EntityLifecycleStage`, `Role`, `RankingModel`,
  `DocumentStatus`) locally — adding an individual to an `owl:oneOf` class from outside makes the
  merged graph inconsistent rather than richer. Propose a MINOR version of this subject instead.
- **Never re-declare framework classes** in your file; reference the IRIs.

---

## 7. Upstream anchoring

Scrum Guide 2020 (Backlog, Increment, Definition of Done); SAFe 6.0 (Epic/Feature/Story ladder,
WSJF, Enabler); Intercom RICE; DSDM MoSCoW; Now/Next/Later roadmap practice; Reinertsen on cost of
delay; W3C OWL 2, SHACL and SHACL-AF; OE Pack subjects (`core:Artifact`, `core:Concept`,
`testing:Test`, `orh:ReleaseEvent`); and the primary source named above for the methodology layer
— the launch model, gap discipline, report sections, gates, rule provenance and role split.

---

## 8. Non-goals

Not an issue-tracker
replacement, not a workflow engine, and it carries no project data: the shipped ABox holds
framework-level individuals only.

---

## 9. Honest disclosures

- **v1.0.0 covered 22.2% of this document and passed every intrinsic gate while doing so.** It was
  built from an adopting project deposit because the source was unreachable (HTTP 404). The deposit
  encodes the register; the document encodes the methodology governing it, which is most of what
  was missing. The full measurement is in `Coverage_Report_v1_1_0.md`.
- **Coverage measures representation, not modelling quality.** A probe proves a concept is present
  as vocabulary, constraint or tooling; it does not prove the modelling is the best available.
- **`EnforcementDomain` ships unpopulated** by design — the source anchors it to another project's
  classification, and importing that would drag foreign vocabulary into a project-neutral subject.
- **No HermiT attestation.** Validation is SHACL (pyshacl 0.40.0, advanced mode) plus rdflib
  parsing. No OWL 2 DL consistency claim is made. The design avoids the two usual traps — no
  irreflexive or asymmetric characteristic on the transitive `dependsOn`, and no OWL equivalence
  across enumerations of different cardinality — but avoidance by design is not an attestation.
- **An adopting project deposit was not modified.** Supersession of `product-backlog` 1.3.0 is proposed
  in the mapping report, not asserted; the owning session decides.
- **One candidate lesson was rejected as a duplicate** during this release rather than recorded to
  satisfy a checklist; see the changelog.
