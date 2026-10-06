# Decision analysis — where the SDLC analysis/design vocabulary belongs

**Prepared by:** `brsf-session`, 2026-09-09, for the owner.
**Occasion:** lineage 9 (`L_SDLCObligations`) needs to name, by IRI, the artifacts each pipeline stage
owes. This session filed a proposal to another registrant (commit `1b65620`) asking for four artifact kinds. The
owner's correction: *"we have defined all of them in the context of BRSF, you need to check your own
files. another registrant is the research and documentation specific ecosystem."*

---

## 1. What is already in BRSF — measured, not recalled

Read from `01-ontologies/backlog_tbox_v1_89_0.ttl` and the two registers on 2026-09-09.

| Concept needed by a stage obligation | Already in BRSF | Enforcement today | Individuals on record |
|---|---|---|---|
| Model artifact of a named kind | `ModelArtifact` + `hasModelKind` → `ModelKind`, **14 UML 2.5 kinds** incl. `Kind_UseCaseDiagram`, `Kind_ActivityDiagram`, `Kind_SequenceDiagram`, `Kind_ClassDiagram`, `Kind_StateMachineDiagram` | 2 Violation clauses (must name kind; must name the item it describes) + 2 advisories | 8 (archive) |
| Structure vs behaviour | `ModelCategory` → `Cat_Structure`, `Cat_Behaviour` | typed on kinds | — |
| What a story *does* (use-case body) | `Specification` + `hasInteractionStep` → `InteractionStep` + `hasStepActor` → `TeamRole`, and `hasStateChange` → `StateChange` | shape-checked | 9 specs, 18 steps |
| Main / alternative / exception paths | `TestScenario` + `scenarioKind` → **4 kinds**: `Scen_Nominal`, `Scen_Boundary`, `Scen_Rejection`, `Scen_Absent` | 1 Violation clause | — |
| Acceptance, checkable | `AcceptanceCriterion` + `hasGherkinText`, `coveredByCase`, `satisfiedByArtifact`; `TestCase`, `TestData`, `TestEvidence`, `TestHarness` | several | 113 criteria, 35 cases |
| Analysis dimensions before build | `DesignConcern` → **5** (`Data`, `Interface`, `Interaction`, `Architecture`, `Security`), `coversTaskType` → `TaskType` | 1 clause | — |
| SDLC task types | `TaskType` → **14 ISO/IEC 12207 types** (`Task_MissionAnalysis` … `Task_Disposal`) | DoD machinery | many |
| Domain entities and blueprint | `DomainEntity`, `Blueprint`, `BlueprintGap`, `coversEntity`, `coversStage` | `EpicPlanningShape` (L3/L4) | 5 + 20 gaps (lineage 9) |

**Finding.** BRSF already carries the entire vocabulary the four asked-for kinds would have named,
and carries it *better*: `Kind_UseCaseDiagram`/`Kind_ActivityDiagram`/`Kind_SequenceDiagram` are
grounded in UML 2.5 with the taxonomy closed at fourteen for a stated reason; `Scen_*` distinguishes
the four ways a scenario fails; `Specification`/`InteractionStep`/`hasStepActor` is a use-case body
with actors. The proposal to another registrant asked for definitions this framework had already made. **My error,
and the direct cause was the one this week keeps repeating: I searched my memory of the framework
instead of its files.** The scope exclusion `Ex_SDLC_NoNewKinds` (L-64) is sound as a rule; I applied
it to vocabulary that was never external.

**What is genuinely missing** is not vocabulary but *obligation*: nothing says a stage owes a
`ModelArtifact` of a given `ModelKind`, or that a `Goal` stage owes a `Specification` with
`InteractionStep`s and `TestScenario`s of the four kinds, before its output may close. That is
exactly lineage 9's four approved points, and it is a relation between things BRSF already owns.

---

## 2. Options

**A. Reference another registrant kinds** (the filed proposal). Wait for four `doc:ArtifactKindSpec` individuals
and point `stageOwesArtifactKind` at them.

**B. Use BRSF's existing vocabulary as-is.** `stageOwesArtifactKind` ranges over `ModelKind` and the
existing classes; the obligation says "Stage_Objective owes a `ModelArtifact` of `Kind_ActivityDiagram`
and one of `Kind_SequenceDiagram`", "Stage_Goal owes a `Specification` with ≥1 `InteractionStep` and
`TestScenario`s covering `Scen_Nominal` and at least one non-nominal kind".

**C. Extract an SDLC/modelling ontology from BRSF** (`sdlc_tbox`), moving `ModelArtifact`, `ModelKind`,
`Specification`, `InteractionStep`, `TestScenario`, `DesignConcern`, `TaskType`, `DomainEntity`,
`Blueprint` and their properties out of `backlog_tbox`, which then imports it. Other packages
(vaf-agentic-pipeline, future adopters) import the same.

**D. B now, C later** — build the obligations on the existing vocabulary; extract the ontology as its
own lineage once the obligations are shipped and exercised.

---

## 3. Cost, benefit, risk, opportunity

| | **A — another registrant kinds** | **B — BRSF as-is** | **C — extract now** | **D — B now, C later** |
|---|---|---|---|---|
| **Cost** | Zero build; unbounded wait. Then a second vocabulary alongside the one BRSF has. | ~1 release: `stageOwesArtifactKind`/`refinementProduces`, 3–4 shapes, 2 fixtures. | 4–6 releases: split the TBox (6,200 lines), re-point ~300 shape references, re-version both registers, update every adopter, re-run every fixture. Blocks lineage 9 meanwhile. | B's cost now; C's cost later, paid with the obligations already proven. |
| **Benefit** | Ecosystem-wide kinds — *if* they were needed. | Obligations shipped in one release, on vocabulary already grounded (UML 2.5, ISO 12207, Satzinger) and already validated in a 113-criterion register. | Clean separation; reusable by any package; the modelling vocabulary stops being buried in a backlog ontology. | Both, in the order that keeps evidence ahead of structure. |
| **Risk** | **Wrong owner** — another registrant is the research/documentation ecosystem; asking it to own UML kinds pushes vocabulary into a package whose subject it is not (the L-64 error inverted). Duplicate kinds with BRSF's own. Indefinite block. | The modelling vocabulary stays inside `backlog_tbox`, which grows. Adopters import a backlog ontology to get UML kinds. | Big-bang refactor of a live, adopted, 246-release package. Every adopter breaks at once. A refactor with no new capability is the least testable kind of change. | The TBox stays large for a few more weeks — the risk that C removes, deferred, not increased. |
| **Opportunity** | — | Lineage 9 closes its debt in its own next stage; the Goal stage's owed artifacts become buildable immediately. | A reusable SDLC ontology for the whole ecosystem, including the course package. | Same as C, but the obligations exist first and *tell the extraction where the seams are* — the shapes written in B are the evidence for which terms belong together. |

**Reversibility.** B is fully reversible (an obligation naming `Kind_ActivityDiagram` still names it
after extraction — same IRI if the namespace is preserved, or one mechanical rename if not). C is
expensive to reverse. A is reversible but its cost is other people's time.

**Precedent in this framework.** Every mechanism built this week — witness, restart, thrash,
strategies, status, archival — was built on existing vocabulary first and generalised only after the
evidence existed. G85's eighth finding: a strategy shipped without being exercised is untested. C now
would be structure before evidence.

---

## 4. Recommendation

**D.** Build the stage obligations on BRSF's existing vocabulary in the next release (B), and open the
extraction as its own lineage afterwards (C), scoped by what the obligations turn out to need.

**Withdraw the another registrant proposal** with the reason stated plainly — the definitions existed here and
the sender did not check — and record it in both inboxes. Keep `Ex_SDLC_NoNewKinds` in lineage 9's
scope; it is still right, and it is now satisfied without asking anyone: **nothing new is minted,
because it already exists.** Close `Imp_SDLCArtifactKinds` as resolved-by-finding, not by decision,
and state on `Out_Goal_SDLC` that its owed artifacts are buildable after all.

**What needs your word:** whether the extraction (C) becomes lineage 10 after the obligations ship,
and whether it should also carry `TaskType`, `DomainEntity` and `Blueprint` out of `backlog_tbox` or
only the modelling terms.
