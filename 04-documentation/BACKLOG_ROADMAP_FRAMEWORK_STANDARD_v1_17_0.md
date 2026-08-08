# Backlog & Roadmap Semantic Framework — Standard v1.17.0

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
| `scopeRealizesObjective` | What completing this scope is supposed to achieve |
| `scopeCompletionState` / `scopeOutcome` | Derived: is the scoped work finished, and did it work — computed separately, in that order |
| `ScopeChange` | Owner-decided, rationale-bearing admission of work into a set scope |
| `ExternalDependency` + `ExternalDependencyType` | Something outside the development, over six types: vendor, upstream component, peer team, regulatory, infrastructure, customer |
| `requiresExternalEnhancement` | This item needs an external party to change something — triggers the proposal rule |
| `EnhancementProposal` + `ProposalStatus` | The request to that party; never a work item, never scheduled here |
| `RegisterSession` | Provenance of register edits: verified before changing, and what was left alone |

### 2.5c-i Intent, scope, refinement, cost and investment mix (subject v1.2.0)

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
python3 03-tooling/backlog_roadmap_report_v1_4_0.py my_register.ttl --emit report.ttl

# 5. Run the four-gate release check (self-proving)
bash 03-tooling/backlog_gate_v1_1_8.sh my_register.ttl
```

Start at L1, move to L2 once a bridge exists, and to L3 when releases carry manifest hashes and the
blueprint sweep is real. Raising the level is a one-line edit to the profile.

---

## 5. What the gates prove, and what they do not

`backlog_gate_v1_1_8.sh` runs Gate 0 (manifest self-verify), Gate P (every Turtle file parses),
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

Not a project-management tool (no velocity, capacity or burndown), not an issue-tracker
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
