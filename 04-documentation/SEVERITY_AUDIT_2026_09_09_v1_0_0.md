# Severity audit — all 78 advisories, read against their SPARQL

**Run by:** `brsf-session`, 2026-09-09, at the owner's instruction. **Supersedes `G44`'s first pass,**
which judged 63 of 66 shapes from message text alone and reported "0 of 66 reclassified".

**Criterion** (the owner's, sharper than `G43`'s): a rule of the lineage is an **obligation** and its
breach is a violation, whatever the consequence. A **risk** is a condition below certainty, or a
condition certainly true that no rule yet covers. An **opportunity** is neither.

**Result: 58 obligations, 16 risks, 4 opportunities.** Fourteen of the 58 were promoted only after the
owner challenged the first classification — a passed forecast has been missed, a breached limit is
breached, a refinement naming no iteration is missing a datum. One promotion (`ClassReachabilityShape`)
was reverted on measurement: see the changelog.

| Shape | Disposition | Reason |
|---|---|---|
| `AchievedLineageNotArchivedAdvisoryShape` | Obligation → `sh:Violation` | An achieved lineage not archived breaks the archival rule (G87): archiving is the activity an achieved lineage triggers. |
| `AnalysisArtifactShape` | Obligation → `sh:Violation` | A state machine artefact listing no states cannot constrain what points at it; the artefact rule is unmet. |
| `AreaWithoutGoalShape` | Obligation → `sh:Violation` | A scope area no goal answers for breaks the scope-facing goal rule. |
| `BatchCompleteButNotDoneShape` | Obligation → `sh:Violation` | hasBatchCompleted equal to hasBatchSize with hasState not Done is a contradiction between two asserted facts. |
| `BatchStartedStateStaleShape` | Obligation → `sh:Violation` | Verified work recorded against an item still Proposed/Ready is the same contradiction one step earlier. |
| `CapacityDeclaredShape` | Obligation → `sh:Violation` | An iteration with no capacity cannot be checked against its commitment; the planning rule is unmet. |
| `CeremonyLinkAdvisoryShape` | Obligation → `sh:Violation` | An observation taken at a ceremony that does not say so breaks the ceremony-link rule. |
| `CheckpointBreachShape` | Obligation → `sh:Violation` | An observation at or after a checkpoint below its expected value: the objective is behind its own plan -- a broken commitment, not a risk of one. |
| `CriterionCoverageShape` | Obligation → `sh:Violation` | A criterion tested on fewer than two scenario kinds breaks the coverage rule ScenarioKind exists to state. |
| `DeliverableCoverageShape` | Obligation → `sh:Violation` | A scope deliverable no item satisfies breaks the scope-to-backlog rule. |
| `DeploymentCoverageShape` | Obligation → `sh:Violation` | A Done item in no DeploymentUnit breaks the delivery rule: finished is not delivered. |
| `DesignTaskProducesShape` | Obligation → `sh:Violation` | A design/architecture task Done with no model breaks the task-type obligation the framework states. |
| `GroomingToExecutionShape` | Obligation → `sh:Violation` | Analysis for a concern with no task of the implied type: grooming linked to execution is the rule (coversTaskType), and it is unmet. |
| `HarnessCoverageAdvisoryShape` | Obligation → `sh:Violation` | A harness that leaves a criterion unattested breaks the attestation rule the harness exists to satisfy. |
| `IntentTraceabilityAdvisoryShape` | Obligation → `sh:Violation` | An item advancing no recorded objective breaks the traceability the ceremony requires: intent -> objective -> work. |
| `IterationEndedIncompleteShape` | Obligation → `sh:Violation` | A story left unfinished in an ended iteration must be carried forward or recovered; leaving it is the rule broken. |
| `LineageDepthAdvisoryShape` | Obligation → `sh:Violation` | A register of epics with nothing beneath them schedules nothing; the ceremony requires decomposition. |
| `MeasurementDueAfterReviewShape` | Obligation → `sh:Violation` | A review closing metric-moving work with no observation breaks the measurement rule. |
| `MissionClauseCitationShape` | Obligation → `sh:Violation` | A mission-clause quote that appears in no mission statement is a false citation. |
| `MissionReachShape` | Obligation → `sh:Violation` | A mission no goal contributes to breaks the chain: the ceremony requires goals derived from the mission's scope. |
| `ObjectiveStalledShape` | Obligation → `sh:Violation` | Every mover Done and the observation still at baseline: the measurement rule (work moves the metric) is broken, not at risk. |
| `OpenIterationBaselineAdvisoryShape` | Obligation → `sh:Violation` | An open iteration with a planned window and no PlanBaseline breaks the baseline rule; later change becomes unmeasurable. |
| `PracticeGroundingShape` | Obligation → `sh:Violation` | Same exclusion, same breach: a shipped term grounded in nothing. |
| `PreLineageItemUnadmittedAdvisoryShape` | Obligation → `sh:Violation` | A pre-lineage item never admitted breaks the restart rule: admission is how an item re-enters. |
| `ProcessCoverageAdvisoryShape` | Obligation → `sh:Violation` | Implementation with no verification or validation task anywhere breaks the ISO 12207 process coverage the framework asserts. |
| `RefinementProducesShape` | Obligation → `sh:Violation` | Grooming that produces nothing breaks the refinement rule the owner named on 2026-09-09. |
| `RetrospectiveNotStartedShape` | Obligation → `sh:Violation` | A review that closed work with no retrospective following it breaks the ceremony sequence. |
| `RoadmapIntentShape` | Obligation → `sh:Violation` | A roadmap realising no objective breaks the roadmap-to-intent rule. |
| `ScopeContentLateShape` | Obligation → `sh:Violation` | Scope deliverables recorded after the backlog stage breaks the stage order itself. |
| `ShippedRoleSourceShape` | Obligation → `sh:Violation` | A framework-namespace term with no source breaks Ex_InventedPractice, a stated scope exclusion. |
| `SingleCommitLineageShape` | Obligation → `sh:Violation` | Two stages closing in one commit leaves the ceremony's own order unwitnessed (G18); the one-commit-per-stage rule is unmet. |
| `SpecificationAdvisoryShape` | Obligation → `sh:Violation` | Interaction concern analysed with no specification: the analysis-to-specification rule is unmet. |
| `StageOrderWitnessShape` | Obligation → `sh:Violation` | A consuming stage that cannot be shown to follow its predecessor breaks the witnessed-order rule (G81). |
| `StageOutputOwesAdvisoryShape` | Obligation → `sh:Violation` | A waived obligation is a debt against a stated rule; it is reported as owed, and owing is a breach until paid. |
| `StagedElementShape` | Obligation → `sh:Violation` | An element naming no stage output sits outside the pipeline the ceremony requires. |
| `StaleVerificationAdvisoryShape` | Obligation → `sh:Violation` | Evidence marked verified with no date and no method breaks the evidence rule: a claim of checking that cannot be checked. |
| `StoryFormAdvisoryShape` | Obligation → `sh:Violation` | A story without its benefit clause is not a story in this framework's own definition (asRole/wantsCapability/soThat). |
| `StoryReadyToCloseShape` | Obligation → `sh:Violation` | Every task Done and the story not moved is a state the register must not hold; the item-level state rule is broken. |
| `StoryTestAnalysisShape` | Obligation → `sh:Violation` | A Done story with no test case exercising any criterion breaks the Definition of Done. |
| `UnaddressedRefinementShape` | Obligation → `sh:Violation` | A refinement that names no concern cannot satisfy the grooming rule it is counted against. |
| `UndeclaredContainerDependencyAdvisoryShape` | Obligation → `sh:Violation` | A cross-container dependency not declared at container level breaks the dependency-declaration rule. |
| `UndeclaredIndividualShape` | Obligation → `sh:Violation` | An individual outside its class's own owl:oneOf breaks the closed enumeration. |
| `UnguardedExclusionShape` | Obligation → `sh:Violation` | An exclusion no goal guards breaks the exclusion-facing goal rule. |
| `UnrequestedWorkShape` | Obligation → `sh:Violation` | An epic satisfying no deliverable breaks the containment rule the scope states. |
| `ArtifactEnumerationAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | Enumerating criteria may still verify the change; it risks describing files rather than behaviour. |
| `BatchConcealmentShape` | Risk / rule-not-yet-written → `sh:Warning` | A large batch under one criterion risks concealing a blocked unit. |
| `BatchedEvidenceShape` | Risk / rule-not-yet-written → `sh:Warning` | Evidence covering many criteria risks describing an iteration rather than a check. |
| `ClassReachabilityShape` | Risk / rule-not-yet-written → `sh:Warning` | An unreachable class risks a wrong conclusion drawn in good faith (a documented incident). |
| `CrossLineageRiskAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | An identified risk to a live lineage -- risk by construction. |
| `CrossProjectCommitAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | A remote commit under our prefix risks a conflict needing reconciliation. |
| `DeliverableIntentionShape` | Risk / rule-not-yet-written → `sh:Warning` | A deliverable met only by open work risks the boundary being met in intention only. |
| `GroomedAheadShape` | Risk / rule-not-yet-written → `sh:Warning` | Detail written far ahead risks being rewritten. |
| `HorizonCoherenceAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | A Now-horizon item not yet Ready may still become Ready in time. |
| `IneffectiveCorrectiveAttemptAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | An attempt that moved nothing risks a second one repeating it. |
| `JustInTimeGroomingShape` | Risk / rule-not-yet-written → `sh:Warning` | Grooming that names no iteration risks being too early or too late. |
| `LegacyOrderAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | A scope written after its objectives risks a boundary drawn around decisions already made. |
| `LineageLocalModeRecurrenceAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | A recurring local mode risks being a general pattern mis-scoped. |
| `LineageLocalSuccessModeRecurrenceAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | Same, for success modes. |
| `MeasuredBasisAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | A judged estimate inside a launch gate risks being wrong; it is not yet wrong. |
| `OversizedStoryAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | An oversized story risks not landing; it has not failed. |
| `PackageRegularityShape` | Risk / rule-not-yet-written → `sh:Warning` | Uneven package sizes risk an unreadable roadmap. |
| `PbiKindAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | A misplaced kind risks a wrong reading; nothing downstream is yet wrong. |
| `PlannedFromEvidenceShape` | Risk / rule-not-yet-written → `sh:Warning` | A span far above measured durations risks a plan built on hope. |
| `PrematureExclusionShape` | Risk / rule-not-yet-written → `sh:Warning` | Exclusions before areas risk narrowing before the need is known. |
| `RubberStampAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | A gate that never refused may be working; it risks being decorative. |
| `ScopeCreepAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | Work outside the scope's derivation risks creep; a ScopeChange may still admit it. |
| `ScopeGapAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | A boundary no goal derives from risks being unworked. |
| `ScoringIgnoredAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | Selection on another basis risks the scoring being decorative. |
| `SessionDraftedIntentAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | Same, for intent elements. |
| `SessionDraftedMissionAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | A session-drafted mission is legitimate and risks unowned intent. |
| `StaleForecastAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | A missed forecast risks the commitments built on it. |
| `StoryTaskSpreadShape` | Risk / rule-not-yet-written → `sh:Warning` | All-implementation tasks risk analysis and testing being skipped. |
| `UnfinishedLineageShape` | Risk / rule-not-yet-written → `sh:Warning` | A mid-construction lineage is legitimate under the staged ceremony and risks being abandoned there. |
| `WipBreachAdvisoryShape` | Risk / rule-not-yet-written → `sh:Warning` | An overrun WIP limit predicts late delivery; nothing is yet late. |
| `BothLayersShape` | Opportunity → `sh:Info` | All areas in one layer may be exactly right for the boundary. |
| `IntentEchoShape` | Opportunity → `sh:Info` | Objective and work being the same set is an observation about redundancy, not a risk. |
| `MirroredScopeShape` | Opportunity → `sh:Info` | Boundary and backlog mirroring each other exactly is a completeness observation. |
| `ProductScopeKindShape` | Opportunity → `sh:Info` | One product-scope kind throughout may be exactly right. |
