# Changelog

## v1.33.0 — 2026-08-06 (PATCH-class: an open item closed by the adopting project, not by us)

`Report_GoalMeasurabilityShapeDiscrepancyReconciled_v1_0_0.md` — twelfth artifact in their proposals
directory, eleven already processed, found by the same one-command coverage check.

**It answers a question this package recorded rather than corrected.** The v1.29.0 entry proved by
construction that `GoalMeasurabilityShape` is L2-gated and noted their §2 claim of *"six goals with
GoalMeasurabilityShape violations while declaring L1 Core"* could not reproduce, offering two
readings — a run at their target level, or loose naming — and explicitly declining to pick, since
their register was not readable from here.

**The answer is both.** Their profile genuinely was `L1_Core` at the time; the six goals were found by
**test-driving the target profile against a scratch copy**, per their own test-drive-before-declaring
discipline, and §2 then named the shape that *would* flag the condition once that profile applied
rather than reporting L1-gate output. **No register content was ever wrong**; the prose was imprecise
about which profile the check ran against.

**Re-verified here, because the earlier proof was against shapes 1.13.0 and the suite has moved.**
Re-run at 1.14.0: a goal with no `Objective` under an L1 profile still yields no
`GoalMeasurabilityShape` result. Flipping the same graph to `L3_Governed` yields **6 violations** —
their number, from their scenario, reproduced independently.

**A control added for another reason already prevents this recurring.** The `level:` line introduced
at v1.25.0 prints which conformance level ran and how many constraints were suppressed. Had their §2
quoted validator output rather than paraphrasing it, the level would have travelled with the claim and
the ambiguity could not have arisen.

**The symmetry is worth naming.** Two rounds ago this package read a rendered rank table as asserted
RDF and drew a wrong conclusion about their register; here they described a test-driven result in
language that reads as a measurement of the declared one. Same failure from opposite directions —
prose that does not carry the conditions the number was produced under.

**Their filing choice is noted with thanks:** they filed this as a distinct report rather than editing
the original proposal *"so a coverage pass over this directory's filenames finds it"* — adapting to a
mechanism this package only fixed at v1.31.0. That is the coverage check working as a shared
instrument rather than a local one.

**Nothing in the framework changed.** This entry closes the item.


## v1.32.0 — 2026-08-05 (MINOR: wiring the conformance ramp into the work)

**Coverage check first.** The adopting project's proposals directory was re-listed from their
repository — **11 files now, 10 processed, 1 new**: `Proposal_ConformanceTargetInLineage_v1_0_0.md`.
The check that made this a one-line answer is the record-naming fix from v1.31.0.

**Accepted as documentation.** Verified against bytes: `hasTargetConformanceLevel`'s domain is
`AdoptionProfile`; `pursuesObjective`'s domain is the `WorkItem`/`WorkItemContainer` union;
`AdoptionProfile` is a `BacklogConcept` and therefore genuinely **cannot** carry `pursuesObjective`.
Their quoted `skos:definition` reproduces exactly. Their diagnosis holds.

**The gap is real:** `hasTargetConformanceLevel` names a direction and creates no work that would get
you there. They carried a declared L2 target for over a week while the work satisfying it proceeded
as separately-motivated casework, with no goal in the register naming *"reach L2"* as its purpose — so
advancing took a dedicated conversation instead of falling out of the priority computation.

**Their pattern is sound and needs nothing new:** a `Goal` for governance maturity, an `Objective`
whose metric is the target level's **own SHACL violation count from a trial declaration** — a
falsifiable, re-runnable number nobody invented — and scored `WorkItem`s pursuing it.

**One correction to their framing, in their favour.** They argue meta-work loses to feature work
unless given a competing WSJF score. True, and the framework already has a better instrument than
scoring it higher: `PortfolioPolicy` + `CapacityAllocation` exist so categories answering to different
arguments are not arbitrated by one score. A declared target with no allocation behind it will lose
whatever its score says. Now stated alongside their pattern.

**Their §5 restraint is accepted and recorded.** They identified that a property such as
`targetLevelPursuedBy` would close the narrative-only link formally, and **declined to request it**
under L-110's single-producer threshold. That judgement is right, and the option is now on the record
so a second adopter hitting the same wall finds it already considered.


## v1.31.0 — 2026-08-05 (MINOR: two roadmap-rank rules cross-referenced; one advisory message corrected)

A **coverage check** over the adopting project's whole proposals directory — ten artifacts, listed
from their repository rather than recalled — found two this package had never processed and three it
had processed without naming in its own records. Both gaps are closed here.

### Accepted — `Proposal_RoadmapRankShapeCrossReference`

Verified against bytes, and every claim reproduces. `WorkItemRoadmapRankShape` (targets `WorkItem`)
never objects to an absent rank. The roadmap-placement clause in `ContainerLinkageShape` (targets
`WorkItemContainer`) requires one on any launch-gated container at L2. Same vocabulary, **opposite
default for absence**, and — measured — the two shapes sit **1035 lines apart**, against their
estimate of "roughly a thousand".

They read the item-level rule's philosophy, applied it to eight launch-gated `Package` containers,
and left eight real L2 violations standing for a full register pass. Their correction matches this
package's own `fixture_tied_gates_v1_0_0.ttl`: distinct roadmap ranks, co-equal launch priorities
untouched.

Each shape now carries an `rdfs:comment` naming the other, and the standard states the difference.
No behaviour changed.

### Ruled, not accepted as framed — `Proposal_IntentTraceabilityCommitmentGap`

They ask whether the intent-traceability advisory should treat a container's
`hasCommitment`/`commitsToGoal` as satisfying traceability, or whether the Warning is working as
intended. **It is working as intended — and its message was wrong**, which is why it read as a false
positive.

The shape checks `pursuesObjective` three ways and deliberately does not accept a Goal, because a
**Goal states what matters while an Objective states what would settle it**; an item reaching only a
Goal has no measurable target, which is exactly what the advisory exists to surface. But the old
message claimed the value claim "cannot be traced to anything the product is trying to achieve" — and
for an item in a committed container that is **false**. It is traced; it is traced to something
unmeasurable.

The message now says that, and says which reading was overstated. **The check is unchanged.**

### A defect in this package's own record-keeping, found by the coverage check

Three processed proposals — `DevTimeObjectiveVsBusinessTimeBenefit`,
`PreLaunchSyntheticLoadMethodology`, and this round's two — were handled without their **filenames**
appearing in any round record. The work was done; the record said "two proposals from an adopting
project". That makes a later coverage check impossible without re-reading every entry, which is how
one unprocessed proposal sat unnoticed. Round records now name the artifact.


## v1.30.0 — 2026-08-05 (MINOR: the two-lineage framing, which is better than v1.29.0's)

The v1.29.0 text treated this as **one** intent chain with a `Benefit` deferred off the end. The
owner's framing is two parallel lineages, and it is better in three specific ways this entry records
rather than absorbing silently.

**Undecidability, not inconvenience.** v1.29.0 said the single-lineage reading made the framework
"unusable". The sharper statement: a lineage whose objectives require real operational data is
**undecidable during development**, because the deciding fact cannot exist until the development it
would govern has shipped. Unclosable by construction, and an unclosable register stops being
consulted.

**Two lineages, each closable in its own terms** — development and operational — rather than one
chain permanently waiting. This matters structurally: the development lineage can *close*.

**The bridge is an objective, not a note.** v1.29.0 mentioned measuring a collection-and-analysis
capability as one option among several. It is the mechanism: where the operational lineage names a
measure that does not exist, **that measure becomes a development objective** — build the instrument,
test it, return its results — and satisfying it is what makes the operational lineage satisfiable
later. The operational lineage is not parked; it is being constructed, one measure at a time.

**Verified expressible today, so nothing is minted:** no shape limits a register to one `Mission`,
and `contributesToMission`, `contributesToGoal` and `pursuesObjective` are all non-functional. Two
parallel lineages are already writable.

**Connected to existing vocabulary:** an operational objective awaiting its instrument is the same
shape as a `CrossCuttingInvariant` declared with `hasCheckQuery`, reported `NotYetEnforceable`, and
`tracksItem` naming the work that would make it runnable — measurement instead of enforcement.

**Unchanged from v1.29.0:** the honest note that the synthetic/real line is a discipline the adopter
keeps, not a constraint the suite applies.


## v1.29.0 — 2026-08-05 (MINOR: documentation — measuring before there is anything to measure)

Two proposals from an adopting project, both fetched from their own repository and read in full,
both asking for **documentation only** and both explicitly offering to be deferred under L-110's
single-producer threshold. Accepted, because L-110 governs minting structure and they asked for
none: every pattern they describe uses vocabulary the framework already ships.

**Their evidence, verified against this package's bytes rather than accepted:** all three
`skos:definition` quotations reproduce exactly; `benefitFor`, `benefitRealized`, `benefitRealizedBy`,
`hasSuccessMetric`, `hasBaselineValue`, `hasTargetValue` all exist; and the `Objective` definition
contains no clause requiring a production, revenue or business figure. Their reading is right.

**The misreading was worth documenting.** Six goals sat blocked on a shared premise — that an
Objective's metric must be a live business fact — which makes the framework unusable for precisely
the work it exists to discipline, since development necessarily precedes the users it serves.

**Added to the standard, §2.5c-ii:** the Objective/Benefit split as a table; synthetic load against
the real system as a legitimate source of real facts; measuring a collection-and-analysis capability
where the eventual truth is business-time; and the line that a synthetic measurement may satisfy an
Objective but never a `benefitRealized`.

**One thing they did not ask about, disclosed with their own line:** the framework **cannot enforce**
that line. `Evidence` carries a verification method and a tool but nothing distinguishing synthetic
input from real, so a suite handed a load-test artifact as benefit-realisation evidence will not
object. It is a discipline the adopter keeps, not a constraint the suite applies, and the standard
now says so rather than leaving an adopter to assume the gate is watching.

**One claim of theirs that does not reproduce.** They report six goals with
`GoalMeasurabilityShape` violations while declaring conformance level L1 Core.
`GoalMeasurabilityShape` is **L2-gated** — proven here by constructing a goal with no objective under
an L1 profile, which yields no such violation. Either the observation came from a run at their
declared *target* level, or the shape was named loosely. Their register is not readable from here, so
this is recorded as a discrepancy for them to reconcile, not as a correction. It does not affect the
proposals: the misreading is real at L2, which is where they are heading.


## v1.28.0 — 2026-08-05 (MINOR: correcting my own claim, and the reporting defect that caused it)

**The v1.27.0 entry below contains an unfounded claim and is left unedited.** It says *"their
register now fails. The rank-6 tie between FG-EP11 and FG-EP14 is a real violation."* That was
asserted about a file this session never read. Correcting a historical entry in place is the L-112
failure this package's own tooling exists to prevent, so the correction is this entry.

**What the adopting session established**, and this session accepts as their artifact to read:
`rankedOnRoadmap` and `hasRoadmapRank` appear **zero times** in `fitgap_backlog_v1_4_0.ttl`. The
"Rank" column in the handover document was a **report-time sort over `hasScoreValue`** — a table
printed, never an RDF fact asserted. Their register validates **0 Violation, CONFORMANT** against
the real v1.27.0 validator. This session cannot re-derive that independently, having no copy of the
file, and says so rather than implying otherwise.

**My error, named precisely.** I inferred an RDF assertion from a rendered table in a `.docx`. That
is **B4** — trusting a presentation over parsed content — and because the inference grounded a
disposition, **B3** as well. What I had was a column headed "Rank" with two rows reading 6; what I
needed was the register, which I never asked for. The corroborating detail should have stopped me:
their own prose says the tie is at **0.40**, a score, not a rank.

**The defect underneath is mine, not theirs, and is fixed here.** `backlog_roadmap_report` printed
`== 3. Full ranked backlog ==` with no indication that the ordering was computed. A reader — this
one — took such a table for asserted data. Section 3 now states plainly that its position is derived
from `hasScoreValue` at run time, is **not** `backlog:hasRoadmapRank`, and that ties in it are ties
in the score carrying none of the uniqueness obligation a declared rank does. It also prints how
many declared roadmap ranks the register actually contains, so the two can never again be confused
by a reader of the output.

**What stands from v1.27.0:** the constraints themselves. Rank uniqueness genuinely did not reach
ranked work items, and a work item carrying a container-only property is genuinely OWL-inconsistent
while SHACL reports clean. The adopting session independently reproduced both in a scratch copy and
corroborated the fix. The fix was right; only my claim about who it applied to was wrong.


## v1.27.0 — 2026-08-05 (MINOR: a register was SHACL-clean and logically inconsistent)

A parallel session's handover document reported its fit-gap register validating at **0 sh:Violation**
and described a tie at rank 6 as the framework "treating ties as real rather than forcing an
artificial order". Both statements were true of what the suite did. Neither was true of what it
should have done.

**Re-derived here, not accepted.** Their register ranks **epics**. `rankedOnRoadmap` and
`hasRoadmapRank` were domained on `WorkItemContainer` alone, and the rank-uniqueness constraint
lives on a shape targeting `WorkItemContainer` — so it never examined a ranked work item. The tie
was a gap in reach, not a designed tolerance.

**And it is worse than a missed check.** `WorkItem` and `WorkItemContainer` are declared
**disjoint**. An `rdfs:domain` is an inference rule, not a constraint: under OWL 2 DL, ranking an
epic infers that epic to be a container, and the register becomes **logically inconsistent** while
every SHACL gate still reports clean. This package has never carried a reasoner attestation and
disclosed that at registration. This is the first time it cost an adopter a silently unsound
register.

**Also incoherent on its own terms:** `scheduledInHorizon` already unioned both classes, so an epic
could be *placed* in a horizon but not *ranked* in it.

**Fixed — TBox 1.10.0 → 1.11.0, domain widening, backwards compatible:** both properties now union
`WorkItem` and `WorkItemContainer`, matching `scheduledInHorizon` and how roadmaps are actually used.

**Fixed — shapes 1.12.0 → 1.13.0:**
- `WorkItemRoadmapRankShape` — rank uniqueness now reaches ranked work items, and a rank without a
  named roadmap is rejected.
- `DisjointDomainMisuseShape` — a work item carrying any of the eight container-only properties is
  rejected, because SHACL cannot see the inconsistency an OWL reasoner would derive.

**Consequence the reporting session must know:** their register now **fails**. The rank-6 tie
between FG-EP11 and FG-EP14 is a real violation. Launch *priority* may tie — co-equal preconditions
that must all clear are a genuine situation — but a roadmap rank answers *what next*, and a tie
there is the unanswered question the rank exists to answer.


## v1.26.0 — 2026-08-04 (MINOR: the public copy may not lag, and the gate now says so)

Two turns before this release, this package wrote: *"two copies of the same vocabulary will drift.
What does not exist yet is a check that fails when they diverge — that's the thing I'd build before
the next release, not after."* Then it shipped v1.25.0 to the governed repository and left the
public distribution at v1.24.0. The copy a stranger reads was missing exactly the constraints that
release added.

**A stated risk is not a control.** Same lesson OEE catalogued from this session's own
scratch-directory finding, arriving from the other direction: a check that is not encoded does not
run.

**Added:** `backlog_distribution_drift_check_v1_0_0.py`, wired into the release gate. It fails when
the public distribution's version lags the governed package, **and** when re-deriving the public
copy right now produces different bytes from what is published. The second is the load-bearing
half: a version check alone would pass a public copy someone edited in place, and an edit to a
derived artifact has no upstream and disappears at the next derivation, silently.

When no published URL is supplied it reports **NOT RUN**, never PASS — a check that degrades to
success when it cannot run is the decorative gate this suite refuses.

**Proven discriminating in both directions**, per L-95: PASS against the current public copy, FAIL
against the `v1.24.0` tag, naming both the version lag and the byte divergence.

**Found by the new check on its first run:** the derivation script was copying itself into its own
output, while the publication step removed it — so the published copy could never match a fresh
derivation. Fixed in the deriver, which now excludes itself and the drift check, rather than by
adding an exception to the checker.


## v1.25.0 — 2026-08-04 (MINOR: the conformance declaration is itself governed)

**Reported misuse:** teams lowering the declared conformance level so the gates pass. Confirmed by
construction before anything was designed — the shipped negative fixture, unchanged except for the
level token, drops from 308 violations to 105. One word, most of the suite silenced.

**The real reason the mechanism exists, and the real reason it is abusable.** Tiering is an
**adoption ramp**: a framework demanding everything on day one is adopted by nobody. That purpose is
sound. What made it abusable is a design inconsistency that was ours: measured across the suite,
every other opt-out — `notYetScoreable`, `ScopeExclusion`, `Rebaseline`, `ScopeChange`, an accepted
risk, a ranking-fork resolution — already requires a written rationale, and four require an owner
decision. **The conformance level suppressed more than all of them combined and required neither.**
The ramp had no destination, no date, no author and no reason, so nothing distinguished a team
starting from a team hiding.

**Added — TBox 1.9.0 → 1.10.0:** `hasTargetConformanceLevel`, `hasLevelReviewDate`,
`hasPriorConformanceLevel`, `hasDowngradeRationale`.

**Added — shapes 1.11.0 → 1.12.0, and these fire ALWAYS.** They are deliberately not level-gated: a
constraint on the level declaration that the level declaration could switch off would be the defect
it exists to prevent, one turn later.

- the level must be **owner-decided** and carry a **rationale**
- below L3, a **target level** and a **review date** are required
- a target equal to the current level is rejected — standstill encoded as ambition
- a **downgrade** from a previously declared level needs its own rationale, separate from the
  original one, because giving up a claim is a different decision from making it
- advisory once the review date passes

**Added — validator 1.2.0 → 1.3.0:** every run reports the **suppression cost** —
`level: L1_Core — N of M level-gated constraint(s) did NOT run`. A clean result at a low level and a
clean result at a high level previously printed identically. They are not the same claim.

**What this does not do, stated rather than glossed:** it does not stop a determined party. The
register is authored by the same people who declare its level. What it does is make the choice
attributable, reasoned, dated and directional — the whole of what governance can do about a
self-declaration.

**Caught by our own gate during this work:** the standard initially restated the measured figures
(32 constraints, 308→105). The doc-coverage gate rejected it under the restated-measurement rule
added at v1.19.0. The numbers now live only where they are generated.


## v1.24.0 — 2026-08-04 (MINOR: fixing a disclosed-broken mechanism must leave durable proof)

**Raised by an adopting project at L1 Core**, from four incidents in its own history — the last
found the same day it was written: a Story that fixed a previously-disclosed-broken dispatcher
reached `Done` with the fix verified only in a throwaway scratch directory. `grep -rl` over the
committed test suite returned zero files at the moment of the `Done` claim. Nothing in the
repository would have caught it silently regressing.

**Their diagnosis verified against bytes:** `EvidenceBoundDoneShape` does require `hasEvidence` on
`Done`, and does gate on `hasConformanceLevel IN (L2, L3)`. At L1 nothing rejected the claim. Exact.

**Their proposed mechanism is not adopted as offered — two reasons, both structural.**

*No new vocabulary is minted* (L-110, single-producer evidence). The relation already exists: a
`CrossCuttingInvariant` whose status is `NotYetEnforceable` and whose `tracksItem` names a work item
**is**, by its own shipped definition, "a mechanism disclosed broken, pointing at the work that
would fix it". The trigger is therefore **derived** from data the project already maintains, not
declared.

*A self-declared flag creating an obligation is opt-in rigor.* Setting
`fixesDisclosedUnreachableMechanism true` would cost an evidence requirement, so the projects that
set it honestly are the ones already disclosing in prose — the ones that least need catching. Their
own fourth incident proves it: that Story's registration **did** disclose the gap in prose and still
reached `Done`.

**Their ask for conformance-level independence is granted, and it never conflicted with the tiering
principle.** Both new constraints are ordinary L1 well-formedness — *you asserted X, therefore carry
Y* — the same shape as cancellation requiring a rationale or a launch gate requiring an owner. They
looked level-independent; structurally they were always L1.

**Added — `backlog-shapes` 1.10.0 → 1.11.0, no TBox change:**

- `DisclosedBrokenMechanismFixShape` — a `Done` item that is the tracked fix for a still
  `NotYetEnforceable` invariant must carry `Evidence`.
- `StaleInvariantStatusShape` — an invariant may not stay `NotYetEnforceable` once every item it
  tracks is `Done`. This closes the other half the proposal did not reach: not only *was the fix
  evidenced*, but *was the thing the fix was for actually re-checked*.

**Measured:** positive fixture 0 violations; negative fixture 306 across 68 planted defects, both
new ones firing.

**Their alternative — enrich OE Pack's L-99 instead — is correctly routed and not ours.** L-99 read
verbatim this session; the diagnosis fits it. That catalogue is OEE's, and per B1 a finding about it
is raised, not applied.


## v1.23.0 — 2026-08-01 (MINOR: four adopter findings — enrich, reuse, answer, document)

An adopting project raised four findings from real migration work. All verified against bytes. **None
required minting a term** — on one producer's evidence L-110 says make an existing term say what it
already meant, and that was available every time.

**1. Definition of Done had no way to distinguish "which files change" from "how it behaves"** —
upheld. Their user-facing story passed as conformant with a DoD naming files and fields. My own first
grep for UI vocabulary was case-insensitive and returned 91 false positives; re-run their way it
returns 0, and their finding stands. **No `UIScope` flag minted:** `Story` is already defined as the
user-facing kind and `AcceptanceCriterion` already invokes observable behaviour — both enriched
instead, with the test stated explicitly ("could someone who never sees the diff tell whether it
works"). Enforcement is **advisory by construction**: no regex can honestly decide whether prose
describes behaviour, and a heuristic that blocked a release would be the decorative gate this
framework refuses. Proven discriminating on both polarities.

**2. Asked whether a pattern exists for auditing decorative "ontology-governed" claims** — it does,
under a name they would not have searched: `CrossCuttingInvariant` + `hasCheckQuery` +
`InvariantStatus{Holds, Violated, NotYetEnforceable}` + `tracksItem` + `verifiedAgainstCode`. Their
28-of-41 finding *is* the NotYetEnforceable-reported-as-Holds failure at file scale, and their four
root causes become four items rather than twenty-eight. No new vocabulary (L-105).

**3. Asked whether `knowledge_base` is an adoptable domain/regulatory meta-ontology** — answered by
reading the pack they cannot see: it holds **116 LessonsLearned, 59 BestPractice, 27 RegressionTest**.
It is the OE governance lesson catalogue, not domain knowledge, and no pack subject is. Their fear of
ecosystem-level duplication is unfounded — there is nothing there to duplicate.

**4. `hasSuccessMetric` range never `sh:class`-enforced** — confirmed independently and intentional;
the *intent* was the undocumented part. TBox now states the range is nominal and an L1 adopter may
use a project-local metric class and stay conformant. Their own disclosure called this a workaround;
it was the intended latitude, and they were more conformant than they credited themselves.


## v1.22.0 — 2026-07-29 (MINOR: three adopter findings — one of them severe)

Three artifacts from an adopting project session migrating a real development onto this framework.
All three verified against bytes before acting. **The first is the most serious defect this package
has shipped, and I introduced it one release ago.**

### 1. The gate reported PASS on a register full of violations — SEVERE, mine, fixed

At v1.21.0 I piped the register-under-test path through a filter to hide advisory lines:

```bash
python3 "$VALIDATE" "$@" | grep -vE '^  \[(Warning|Info)'
[ $? -ne 0 ] && FAILED=1
```

`$?` after a pipeline is the **last** command's status — grep's, not the validator's — and grep
almost always prints a header line, so it returns 0 regardless. Reproduced exactly as reported:
running the shipped negative fixture through that path prints `VERDICT: NON-CONFORMANT (288
violations)` and then `RELEASE GATE: PASS`. **A register with 288 real violations passed the gate.**

Fixed by taking the verdict from the command rather than from the tail of a display pipeline —
capture the status first, format afterwards. `PIPESTATUS[0]` would also work but breaks silently the
moment another stage is inserted, so the decoupling is permanent instead.

**Why every gate stayed green while this was live:** the three-fixture self-proof invokes the
validator *directly*; only the register path formats its output, so a defect in the formatting layer
was invisible to the proof. `backlog_gate_v1_1_7.sh` now runs the known-bad fixture through the
**exact register path** and aborts if it does not fail. The self-proof covered the shapes; it had
never covered its own plumbing.

### 2. Tied launch gates silently resolved by URI string — upheld, fixed

`active_gate()` sorted `(priority, container)` tuples, so gates tied at the lowest open priority fell
through to comparing URIs as strings and the alphabetically first won. The reporting project carries
**six** co-equal gates at priority 0, each independently owner-decided; the launch-scoped answer was
under-covering the real launch-blocking set every run — and, as they noted, inflating the
throughput/launch disagreement into an artefact of the bug.

Ties are legitimate and stay unconstrained: `hasRoadmapRank` must be unique because a rank that does
not order is not a rank, but co-equal launch preconditions are a real situation, and forcing an owner
to invent a sequence would be the fabrication this framework refuses elsewhere. `active_gates()` now
returns every gate at the lowest open priority and the caller unions members and cross-cutting
prerequisites across all of them. The report says so explicitly: *"scoped to 3 co-equal open launch
gates … all are unioned, none is chosen."*

New fixture `fixture_tied_gates_v1_0_0.ttl` covers it — three tied gates where the best work sits in
the **alphabetically last** one, which the old code could never have selected. The single-gate R3
fixture is unchanged, confirming no regression.

### 3. Nowhere to record a resolved ranking fork — accepted, with a design correction

Their friction is real: `RankingModel`'s definition deliberately keeps the disagreement visible, but
a register that has *already decided* had no way to say so, and every session re-argued it.

Accepted with one change to the proposed shape. Rather than a bare preference property, the recorded
resolution must be an **owner decision with reasons**: `hasRankingForkResolution` (functional, on
`Backlog`) reuses the existing `decidedBy` and `hasDecisionRationale`, and shapes 1.9.0 fails a
register that sets it without naming the Owner or recording why. Choosing between two legitimate
answers is a business judgement, and a standing answer nobody can review is worse than a fork that
keeps asking.

The disagreement notice is unchanged. The resolution prints **beside** it, labelled, with its
rationale — the same pattern as `ScopeChange`, `Rebaseline` and `riskAcceptedBy`: an unavoidable
judgement gets a place to be recorded, or it is remade informally every time.

### Process note, credited

Two of the three proposals disclose that this session had previously patched its vendored copy and
self-assigned version bumps — one colliding with this package's own independent v1.21.0 — then
reverted and re-raised properly. That correction is the discipline working, and it is the reason
these three findings arrived as evidence rather than as a fork.


## v1.21.0 — 2026-07-29 (MINOR: advisories made legible; tiering principle documented)

**Two observations from a parallel session. The first is a real defect and is fixed; the second was
intentional, and answering it exposed a documentation gap worth closing.**

**1. Advisory results collapsed to a number nobody reads — upheld.** Verified against bytes: the gate
script greps `^results|^VERDICT`, so at gate level every advisory became part of a total. The
reporter's phrasing was exact — "175 Warning" with no content is a number a human learns to skip
past, and the advisory tier then protects nothing it was built to surface. One line per result is the
opposite failure at that scale.

`backlog_validate_v1_3_0.py` now prints a **grouped digest**: count per distinct message, the first
few focus nodes for each, sorted by frequency, with individual advisory lines still printed while the
total stays under twenty. Violations are unchanged — always listed individually, because each blocks
a release. On the shipped negative fixture the difference is `39 Warning, 5 Info` becoming
`36 x advances no recorded objective`, `5 x no priority score and no not-yet-scoreable flag`,
`2 x Ready but dependencies not Done`, `1 x advertised in Now but neither Ready nor InProgress` —
the count per kind is the decision-relevant fact, and it was previously invisible.

**2. `ScopeMeasurabilityShape` silent below L2 — intentional, and now confirmed by measurement rather
than recollection.** Every intent-layer shape was checked for whether its constraints query an
`AdoptionProfile`. The split is clean and follows one rule: **L1 constrains the well-formedness of
what you author; L2 and above require that you author it.** `GoalShape`, `BenefitShape`,
`ObjectiveShape`, `ScopeExclusionShape`, `CostEstimateShape` and their siblings are unconditional —
authoring a half-built objective is a structural defect at any level. `ScopeMeasurabilityShape`,
`GoalMeasurabilityShape`, `IntentTraceabilityShape` and the mission-coverage constraint are gated,
because they are claims about *coverage* and arrive with the level that promises them.

**The gap that answering it revealed:** that rule had never been written down. §3 of the standard
listed *what* each level enforces and never the principle generating the split, which is why a
careful reader had to ask. Now stated, with `ScopeMeasurabilityShape` named as the worked example.


## v1.20.0 — 2026-07-29 (MINOR: a shape defect reported by an adopter, fixed at the root)

**An adopting project session (an adopting project, at L1 Core) reported that `LaunchGateShape` is jointly
unsatisfiable for a container that is both `isLaunchGate=true` and `isBusinessCapability=false`.
Upheld — and the report was not stale: it quotes `backlog_shacl_v1_7_0.ttl` with SHA-256
`66af443b1fb89141…`, which re-computes byte-for-byte against the file this package still shipped at
v1.19.1.**

**Proven by construction, not by reading the argument.** A four-case probe run against the shipped
suite: a gate + non-capability with no priority fires rule 1; the same with a priority fires rule 3;
no assignment satisfies both. Their two real packages — cross-cutting platform and continuity work the
owner named launch-blocking but that nobody would buy as a standalone capability — are correctly
modelled on both flags. The shape was wrong, not the data.

**Diagnosis, narrower than the one proposed.** The superseded constraint's own message described
protecting *capability-level ranking*, but it constrained `hasLaunchPriority` — which the TBox defines
as an owner-declared launch ordinal that is never a computed ranking value. Capability ranking runs on
`hasPriorityScore`, and `backlog_roadmap_report` already excludes non-capability containers from it
(verified: the exclusion is at lines 246 and 263, and is the *only* other place `isBusinessCapability`
is enforced). **The constraint guarded the wrong predicate.**

**Fix taken: not the proposed exception.** the adopting project's Option A adds
`FILTER NOT EXISTS { isLaunchGate true }` to the old constraint, which resolves the contradiction but
keeps a rule aimed at the wrong property. Shapes **1.7.0 → 1.8.0** replaces it with the coherent rule:
**a launch priority may only exist on a container declared a launch gate** — on anything that is not a
gate it orders nothing.

That replacement is strictly stronger than both the old constraint and Option A. Verified across four
cases: gate + non-capability + priority now **clean** (their case); non-gate + non-capability +
priority still caught (the old protection); and **non-gate + business-capability + priority now
caught — which nothing in 1.7.0 detected**, because the old constraint only looked at containers
tagged *not* a capability.

**Disclosure for adopters:** this can fail a register that previously conformed — specifically case
(d) above. Re-run the gate after upgrading. Shipped as MINOR consistent with this package's prior
practice for added constraints, with the breaking direction stated rather than left to be discovered.

**Fixtures extended** per the reporter's own verification method: the positive fixture now carries a
launch-gated non-capability with a priority (their exact combination, 0 violations), and the negative
fixture plants both new cases as defects 65 and 66.


## v1.20.0 — 2026-07-29 (MINOR: a shape defect reported by an adopter, fixed at the root)

**An adopting project session (an adopting project, at L1 Core) reported that `LaunchGateShape` is jointly
unsatisfiable for a container that is both `isLaunchGate=true` and `isBusinessCapability=false`.
Upheld — and the report was not stale: it quotes `backlog_shacl_v1_7_0.ttl` with SHA-256
`66af443b1fb89141…`, which re-computes byte-for-byte against the file this package still shipped at
v1.19.1.**

**Proven by construction, not by reading the argument.** A four-case probe run against the shipped
suite: a gate + non-capability with no priority fires rule 1; the same with a priority fires rule 3;
no assignment satisfies both. Their two real packages — cross-cutting platform and continuity work the
owner named launch-blocking but that nobody would buy as a standalone capability — are correctly
modelled on both flags. The shape was wrong, not the data.

**Diagnosis, narrower than the one proposed.** The superseded constraint's own message described
protecting *capability-level ranking*, but it constrained `hasLaunchPriority` — which the TBox defines
as an owner-declared launch ordinal that is never a computed ranking value. Capability ranking runs on
`hasPriorityScore`, and `backlog_roadmap_report` already excludes non-capability containers from it
(verified: the exclusion is at lines 246 and 263, and is the *only* other place `isBusinessCapability`
is enforced). **The constraint guarded the wrong predicate.**

**Fix taken: not the proposed exception.** the adopting project's Option A adds
`FILTER NOT EXISTS { isLaunchGate true }` to the old constraint, which resolves the contradiction but
keeps a rule aimed at the wrong property. Shapes **1.7.0 → 1.8.0** replaces it with the coherent rule:
**a launch priority may only exist on a container declared a launch gate** — on anything that is not a
gate it orders nothing.

That replacement is strictly stronger than both the old constraint and Option A. Verified across four
cases: gate + non-capability + priority now **clean** (their case); non-gate + non-capability +
priority still caught (the old protection); and **non-gate + business-capability + priority now
caught — which nothing in 1.7.0 detected**, because the old constraint only looked at containers
tagged *not* a capability.

**Disclosure for adopters:** this can fail a register that previously conformed — specifically case
(d) above. Re-run the gate after upgrading. Shipped as MINOR consistent with this package's prior
practice for added constraints, with the breaking direction stated rather than left to be discovered.

**Fixtures extended** per the reporter's own verification method: the positive fixture now carries a
launch-gated non-capability with a priority (their exact combination, 0 violations), and the negative
fixture plants both new cases as defects 65 and 66.


## v1.19.1 — 2026-07-29 (PATCH: title/filename agreement, caught in-house)

Cutting v1.19.0 renamed the standard to `_v1_5_0.md` and left its H1 reading **v1.4.0** — the same
title-versus-filename defect OEE returned twice before in provenance notes. This time the package
found it in its own verification pass, before shipping.

Fixed, and gated: `backlog_doc_coverage_gate_v1_2_0.py` adds a third rule — every versioned Markdown
document's H1 must carry the same version token as its filename. A filename bump with a stale title
is a document disagreeing with itself about which version a reader is holding.

## v1.19.0 — 2026-07-29 (MINOR: restated measurements forbidden, not just corrected)

**A parallel session reported two staleness defects in the standard. Both genuine, and the header
was worse than reported.**

Verified on bytes before touching anything: the header read `Package: backlog-roadmap-framework
v1.14.0` against an actual v1.18.0, pinned `OE Pack v20.24.0` against an actual v20.26.2, **and
carried `Subject:` twice** — a duplication the report had not seen. Section 5 stated
"46 violations across 28 planted defects"; the negative fixture now produces 280 violations across
63 distinct planted defects. Their structural point was also correct: the doc-coverage gate checked
that classes are *named*, never that stated numbers are *current*.

**L-91 is the governing rule, and it prescribes a better remedy than updating the numbers.** Screened
all 178 definitions: L-111 is scoped to vocabulary coverage and explicitly distinguishes itself from
L-91, which governs prose duplicating an authoritative machine-readable fact. Its clause (3) is
decisive — *prefer to have prose POINT AT the field rather than re-state it*. So no new lesson was
minted; this is an L-91 instance, and correctly identifying an existing rule is not the withholding
error of round 10.

**Fixed at the root, not at the instance:**

- The header now states the **subject** version — which is what the document describes — and
  deliberately pins neither the distribution package nor the OE Pack release, because both move
  independently of the vocabulary and go stale here by construction. The duplicate `Subject:` is gone.
- Section 5 no longer restates any figure. It points at `RELEASE_METRICS.txt`, which is generated,
  carries the manifest SHA it was produced against, and regenerates byte-identically. What remains
  stated is what cannot go stale: that the gate runs **three** mandatory fixtures and aborts if any
  outcome inverts.
- `backlog_doc_coverage_gate_v1_2_0.py` now **forbids** restated measurements rather than checking
  them — violation counts, planted-defect totals, coverage ratios, declaration counts, and package or
  pack version pins. Structural counts ("a closed set of three", "eight required sections") stay
  allowed, because they are facts about the vocabulary, not about a run.

**The gate found two more than the report did**, both pack pins — and one of them taught the narrowing
that matters: *"Ruled at OE Pack v20.23.41"* is a **dated historical citation**, true forever, and
rewriting it would be the exact L-112 violation the repoint tool exists to prevent. The gate now
exempts dated citations and flags only current-state assertions — the same current-state-versus
-historical distinction, applied inside the gate itself. The other, an anchor naming the release
upstream terms were read at, was de-pinned.

**Discrimination proven by re-inserting the reported defect:** the exact sentence
"46 violations across 28 planted defects" put back into the standard makes the gate **FAIL** on both
figures; removing it returns PASS.


## v1.18.0 — 2026-07-29 (MINOR: L-112 amendment adopted; extension-sensitivity closed)

**Our tool found a defect in the lesson it implements.** A dry run repointing an ontology filename
token reported `MANIFEST_SHA256.txt` as editable. Under L-112's original two-way split that was
*correct* — a manifest is not a record of the past — so the split was wrong, not the tool. OEE
amended L-112 to three classes (`kb_abox` v2.19.0 → v2.19.1, PATCH, definition correction only,
handled as an amendment rather than a sibling lesson per L-110).

**Adopted:** `backlog_repoint_v1_1_0.py` now classifies into current-state / historical / **generated**.
Generated artifacts are excluded for a different reason and with a different remedy — they are derived
from the current tree, so a text edit desynchronises them from what they describe, and a manifest is
the worst case because repointing inside it rewrites the integrity instrument itself. The tool prints
the two remedies separately: *append a dated correction* for historical, *regenerate* for generated.

**Their finding closed by classifying on role, not extension.** The first version guarded
`06-package-provenance` for `*.md` only, so `backlog_quality_assessment_v1_0_0.ttl` — a dated
measurement — sat in the editable set with 10 occurrences, while its Markdown analogue was protected.
The same class landing differently by suffix was the actual defect. Role tokens
(`*_assessment_v*`, `*_proposal_v*`, `*_emission_v*`, `*_declaration_v*`, `*_note_v*`,
`*_response_v*`, `changelog_v*`, `registration_intent_v*`, …) are now matched case-insensitively
against the filename **whatever the suffix**, and the quality assessment is classified generated
rather than historical, because regenerating it is the correct remedy.

**Proven by re-running their own dry run:** repointing `backlog_tbox_v1_7_0.ttl` now reports
**0 editable, 0 historical, 3 generated** — manifest, metrics and the quality assessment, each with
the regenerate remedy attached. The two files they identified by inspection,
`oee_registration_emission_v1_0_0.ttl` and `independent_package_naming_proposal_v1_1_0.ttl`, are
protected by the `*_emission_v*` and `*_proposal_v*` role tokens.


## v1.17.0 — 2026-07-29 (MINOR: L-112 adopted as a tool, not a note)

**L-112 catalogued at OE Pack v20.26.0** — *a mechanical repoint is correct for files that describe
the current state and corrupting for files that record a past one; exclude historical records by
class* — adopted from this package's screened-but-withheld candidate, carrying OE Pack's own earlier
instance as the second application. Catalogue 115 → 116.

**A correction accepted, and it is the more useful half of the round.** We screened the candidate
against all 177 definitions, found nothing covering it, and then **withheld it because the ceremony
was closed**. OEE: *"The screen was right; the withholding was not."* A closed registration round
does not close the catalogue — L-84 governs lesson recording independently of registration state, and
declining a genuinely new lesson for a procedural reason is the mirror image of the padding L-71
forbids: the same error with the sign flipped. Recorded here because we will otherwise repeat it the
next time a round feels finished.

**Adopted mechanically, per L-112's own operative clause** — *"a repoint script names its exclusions
explicitly, so that the exclusion is a property of the tool rather than of whoever remembers to pass
a flag."* The v1.16.1 remedy was a maintenance note in the README, which is precisely
whoever-remembers. `backlog_repoint_v1_0_0.py` replaces it: corpus-wide rename with the historical
classes hard-coded and no option to disable them — changelogs, the metrics file, registration intent,
lesson deposits, past-exchange notes in package provenance, ceremony records, and dated audits,
coverage reports and assessments.

**Proven by replaying the original defect.** Running the exact repoint that caused it
(`backlog_release_metrics_v1_0_0.py` → `_v1_1_0.py`) as a dry run now reports **0 files editable, 2
protected** — the changelog entry and the registration intent, each named with why. The tool also
prints the correct remedy for a genuinely wrong historical record: append a dated correction or ship
a new versioned entry, never rewrite the earlier text.

**Also noted:** OEE verified that the generated-metrics discipline survived a version bump — the file
names v1.16.1, records a manifest SHA that re-computes to the shipped manifest, and regenerates
byte-identically from a differently-named directory. A generator that survives its own package's
version change is worth more than the finding that prompted it.


## v1.16.1 — 2026-07-29 (PATCH: record hygiene; no artifact changed)

**ORCP ceremony CLOSED by OEE at pack v20.25.2.** Round 9 verified: manifest 48/48, 15 TTL / 6,686
triples, 0 subjects in OEE namespaces, gate PASS, readiness 11/11 with the qualifier disclosed. The
metrics fix was re-proven on their side by copying the package to a differently-named directory and
diffing — byte-identical, with the recorded manifest SHA re-computing to the shipped manifest.

**Two standing conditions from our own §6 were explicitly disposed**, each on bytes, rather than left
implicit: the **HermiT attestation is not required** — no pack ontology or shape imports or references
the backlog namespace, the only occurrence being the anchor's own `rdfs:seeAlso`, so the pack makes no
OWL 2 DL claim over our vocabulary (it becomes required again only if ratification into
`01-ontologies/` is ever sought); and **`product-backlog` 1.3.0 is carried alongside, not retired** —
it remains the originating project record while `backlog` is the generalisation on its own ORIGINATION
track, so no `Supersession` is warranted and none exists.

**Two findings returned — both mine, both in prose, both fixed here.** Inside the v1.15.0 entry as
re-shipped:

1. It claimed `RELEASE_METRICS.txt` is a file *"which the manifest then hashes."* It is not, at
   v1.15.0 or since — contradicted by our own v1.16.0 entry and by both tool docstrings. Removed.
2. It named `backlog_release_metrics_v1_1_0.py`, which did not exist at v1.15.0; that bundle shipped
   `v1_0_0`. Verified against the deposit held at pack v20.25.1. Restored.

**Root cause, and it is worth naming:** a global `sed` repoint across `04-documentation/*.md`
rewrote a *historical* entry. A changelog entry is a factual record of a past release; repointing
artifact names across it makes the record silently false. The governing discipline already says this
about itself — "global repoint scripts must exclude this file" — and the same reasoning extends to
any historical record. **Rule adopted here: repoints never touch CHANGELOG entries.**

**L-84 screen, result recorded rather than acted on:** the candidate — *a global repoint across
documentation rewrites historical records and must exclude them* — was duplicate-screened against all
177 definitions in `knowledge_base_abox_v2_18_0.ttl`. Nothing covers it; the nearest are BP-D6
(naming verified at creation, not retrofitted — about files, not prose) and the discipline's own
self-exclusion clause. It is therefore **deposit-ready but not deposited**: the ceremony is closed,
the item is non-blocking, and minting into a closed ceremony to round out a session is the failure
L-71 names. Available on request.

**Nothing open on either side.**


## v1.16.0 — 2026-07-29 (registration closed; two findings fixed)

**Round 8 closed by OEE at pack v20.25.1.** All three prior findings verified fixed at the root;
submitted digest re-computed and matched; candidate lesson screened and **declined** as an existing
L-X5 instance — the same restraint that admitted L-110 and L-111 when they were genuinely new.

**Two findings returned, both upheld, both wider than reported.**

**1. An L-X5 instance in the metrics file.** `RELEASE_METRICS.txt` carried
`controls run brsf` — a label taken from the enclosing directory. Because the file is excluded from
the manifest, reproducibility is its *only* integrity guarantee, and a value from the extraction path
cannot reproduce for anyone unpacking the bundle under a different name.

Scanning for the class rather than the reported instance found **a second environment-derived value
OEE had not flagged**: a wall-clock generation stamp, which defeats byte-reproduction on *every* run,
not just on a rename. Both removed — the label now derives from `VERSION.txt`, and the stamp is
replaced by the **manifest SHA-256**, which is file-derived and ties the figures to an exact package
state. Proven, not asserted: the file was generated twice and diffed — **identical**.

**2. The exclusion rationale was wrong.** Both docstrings said the metrics file is excluded "for the
same self-reference reason `MANIFEST_SHA256.txt` excludes itself." A manifest *cannot* contain its
own hash — that is containment. This file *could* be hashed; it is excluded because it **reports the
manifest gate**, so covering it creates a generation-order cycle. The consequence differs and is
exactly why finding 1 matters: the manifest's integrity is self-evident on verification, this file's
is not covered at all. Both tools now state the accurate distinction.

**Qualifier kept attached:** the readiness figure of 11/11 is measured **with `--pack` supplied**;
without it the same tool reports 10 pass / 1 not run, and the metrics file discloses which.

**Recorded:** round 9; registration intent 1.7.0 → 1.8.0.


## v1.15.0 — 2026-07-29 (PATCH-class fixes, MINOR for the new generator)

**Three findings returned by OEE at pack v20.25.0. All three upheld on our own bytes; one is worse
than reported.**

**1. A number that does not reproduce — upheld.** The v1.14.0 entry claimed "32 undocumented
classes". No tool produced that figure: it was a manual probe of 17 *terms* (classes **and**
properties) added to a later gate run of 15 *classes* — two different populations, summed while
writing prose. Re-derived this session by running the shipped doc-coverage gate against the v1.13.0
bundle's standard, recovered from an earlier clean-extraction directory: **62 of 91 classes named,
29 undocumented** — matching OEE's figure exactly. The changelog entry is corrected to the
reproducible number.

*Structural fix, not a resolution to be careful:* `backlog_release_metrics_v1_0_0.py` runs every
gate and writes their verbatim output to `RELEASE_METRICS.txt`.
Release figures are quoted from that file rather than computed while writing. B3 requires an
externally-verifiable claim to be re-executed; a release note is a dense collection of such claims,
so the numbers now come from a generated artifact a reader can regenerate.

**2. `06-audit-artifacts` is not new — upheld.** Present at v20.23.42 with the same two files and
listed twice in that manifest. We asserted "new" from an impression of a directory listing rather
than from the delta we had already computed — L-80 exactly. Corrected in place.

**3. Half-fixed version line — upheld, and it was two files, not one.** Both
`backlog_framework_bpd46_citation_note_v1_1_0.md` **and**
`backlog_framework_round6_response_v1_1_0.md` still read `v1.0.0` in their title lines. The two
sibling documents were fixed by a regex that happened to match them and not these. Both corrected,
each carrying a line recording why.

**L-111 adopted.** Catalogued from our own gap: documentation-coverage drift is invisible to every
structural gate. Our doc-coverage gate is the mechanism it names, and it is now part of the release
gate rather than a script someone remembers to run.


## v1.14.0 — 2026-07-28 (MINOR: everything closed; the real drift found and gated)

**Open items: none.** Both remaining questions are settled without spending OEE attention, and a
mechanical scan found the defect that mattered more than either of them.

**The progress-report naming question — closed under the conventions as ruled**, not escalated. A
retained run emitted as Turtle follows `ABoxFileConvention`, which v20.23.41 ruled governs
governance-register data; emitted as Markdown it follows `AuditReportMarkdownConvention`. Neither
diverges in *form*, so L-110's own test says record the binding rather than mint structure. The
full role-to-convention table is now in the standard, §2.5f.

**The quality-facet item — closed by reading, not by asking.** Re-read in full, closure §7 says these
items *remain ours* in the sense of ownership; v20.23.41 had already recorded the assessment as
requiring no OEE action. There was no ambiguity worth raising, and flagging one was over-caution.

**The defect that was actually costing something: the standard had fallen three subject releases
behind the ontology.** The shipped doc-coverage gate, run against the v1.13.0 bundle, reports
**62 of 91 classes named — 29 undocumented** — the entire v1.2.0 intent layer (goals, objectives, benefits,
opportunities, scope, refinement, cost, investment mix), v1.4.0 (decomposition, commitments,
dependency kinds, impediments, flow, teams, story form), v1.5.0 (observations, outcomes,
re-baselining, actuals, tool-named verification) and v1.7.0 (register packaging). An adopter reads
the standard, not the TBox.

Every gate had passed throughout — parse, SHACL, manifest, version identity, source-concept coverage
— because **none of them compares the ontology with the prose that explains it**.

**Fixed:** standard v1.3.0 → v1.4.0, now documenting all 91 classes, with the registered status and
pack version corrected. **Gated:** `backlog_doc_coverage_gate_v1_0_0.py` joins the release gate as a
sixth check — every TBox class must be named in the standard, or the release is blocked.

**Also fixed:** four stale claims elsewhere (registered status in the standard header, quality facet
described as unexercised in the readiness assessment, a reference to a retired filename, and
"pending ORCP evaluation" in the README).

**Closed and retained as records:** the BP-D46 citation note and the round-6 response, both bumped to
`v1_1_0` with status banners rather than edited in place — the BP-D7 lesson from last round applied
before it had to be pointed out again.

**Recorded:** round 7; registration intent 1.5.0 → 1.6.0.


## v1.13.0 — 2026-07-28 (MINOR: round 5 closed; two returned findings fixed)

**OE Pack v20.24.0 verified on this side:** manifest 136/136, discipline file unchanged, delta 8
added / 3 changed / 5 removed. The pack ships inside a top-level directory this release — noted, no action. (An earlier draft of
this entry also called `06-audit-artifacts/` new; it is not. It was present at v20.23.42 with the
same two files, `redo_v3_0_0.ttl` and its provenance README, and appears twice in that manifest.
Corrected at v1.15.0.)

**Our BP-D46 finding was upheld and both remedies applied.** `L-110` is catalogued —
*do not mint new governance structure on a single producer's evidence; enrich the governing term and
defer the structure until a second divergent case exists* — authored by OEE, attributed to OEE's own
two applications, with `dcterms:source` recording that we surfaced the gap and declined to propose
it. `configuration:ABoxFileConvention` now cites L-110 (ABox v2.6.0 → v2.6.1, citation text only).
The lesson improves on our framing: we said "a set of one", L-110 states the *test* —
pattern-conformance versus form-divergence — which is the part that survives the next case.

**Two findings returned to us, both upheld and fixed:**

1. **BP-D7 slip.** Two documents gained a status banner at v1.12.0 while keeping their `v1_0_0`
   token. We re-derived the SHAs before fixing; OEE's figures matched ours exactly. Now shipped as
   `v1_1_0`, each recording why the version moved.
2. **Packaging hygiene.** A compiled `.pyc` — created when our *own* discrimination test imported the
   package checker as a module — was shipped and manifest-listed at line 19. Fixed in
   `build_manifest_v1_3_0.py`, which now prunes `__pycache__` and skips `.pyc`/`.pyo`, rather than by
   deleting the file: Gate 0 verifies that what is listed matches, and cannot know that something
   should never have been listed.

**One clarification raised back, non-blocking:** closure §7 lists the quality-facet assessment as
remaining ours, which reads either as still open — conflicting with the v20.23.41 record and with the
held deposits — or as a standing responsibility to re-run it as the subject changes. We read it as
the latter and will re-run whenever the subject version moves.

**Recorded:** round 6; registration intent 1.4.0 → 1.5.0.


## v1.12.0 — 2026-07-28 (MINOR: Phase-D ruling adopted; two corrections recorded)

**The register-data question is RULED.** At OE Pack v20.23.41: `ABoxFileConvention` governs
governance-register data files. No new convention, no exception individual — the convention's own
`skos:definition` was enriched instead, and it now points a reader at `backlog:RegisterSession`
rather than the filename for telling a live register from a released ABox.

**Verified on bytes, not accepted from prose:** configuration ABox v2.5.0 → v2.6.0 with exactly
three changed triples and zero new subjects; the amended definition read in full; 16 conventions and
7 exception individuals unchanged; package checker re-run against v20.23.42 — **PASS**, because the
pattern did not change.

**Our error, recorded rather than absorbed.** We proposed option D — an exception individual on the
`SafeguardDotDelimiterException` / `USODelimiterException` precedent — and justified it as "the
pack's own mechanism, already used twice". We verified those individuals *exist*; we never checked
what class they *are*. OEE did: both are `configuration:VersionInFilenamePolicy`, scoped to
filename-delimiter-format divergence, which our lifecycle-cadence divergence is not. That is L-75
exactly — overlap assumed from a name.

**One finding raised back, non-blocking.** The amended definition cites "BP-D46 restraint on a
single-producer set". BP-D46 is `SemanticOverlapAnnotationDiscipline` — 918 characters entirely
about cross-subject local-name collisions, containing no restraint language; and no catalogued BP or
L states that principle at all. It matters because the mis-citation now sits in a governed
definition every future adopter reads. Two options offered, both OEE's:
`backlog_framework_bpd46_citation_note_v1_0_0.md`.

**Closed:** the Phase-D proposal and the re-raise cover note, both retained as records with their
outcome in the header. The re-raise and the ruling crossed in transit.

**Recorded:** round 5; registration intent 1.3.0 → 1.4.0.

**Sequencing note taken:** future rounds verify against the newest pack — this one against
v20.23.42, not the release the previous bundle was authored on.


## v1.11.0 — 2026-07-28 (MINOR: closure acknowledged; Phase-D ask re-raised)

**OE Pack v20.23.40 (PATCH) verified on this side:** manifest 128/128, discipline file unchanged,
release-history ABox v1.51.0 → v1.51.1 with exactly one new subject. OEE re-derived all five
bookkeeping claims from v1.10.0 on bytes and confirmed them, and independently re-confirmed 21/21
held deposits byte-identical.

**Our ProjectArchive observation was verified — with a better diagnosis than ours.** Exactly four
`configuration:ProjectArchive` individuals exist (`v17_30_0` … `v17_32_0`), none since; BP-D24
governs ontology-header predicates, not archive minting. So it is a **lapsed archive-metrics
practice, not a violated rule** — disclosed, not fixed, no urgency. Recorded that way on our side.

**Probe-method correction accepted:** `L-107` / `L-108` are `hasLessonId` **values**, not IRI
local-name substrings, which is why our first grep missed the adopted lessons. Probe by exact IRI or
by property value, never by IRI substring.

**Phase-D ask re-raised, unchanged.** The release event concludes "nothing to adopt, nothing to
decide" — accurate for the five bookkeeping items, not for the submission as a whole, which also
carried the register-data-convention proposal. Measured against v20.23.40 rather than assumed:
configuration ABox unchanged at v2.5.0, 16 conventions and 7 exception individuals with none naming
register or instance data, the proposal not held among the deposits, and no mention of it by filename
anywhere in the pack. The conclusion recorded is that the ask **did not surface** — not that it was
refused, since a refusal would itself be a complete answer.

Added `backlog_framework_phase_d_reraise_cover_note_v1_0_0.md`: one page, the question in one
sentence, the measured checks, and an explicit statement that nothing is blocked. The proposal
document itself needed no revision and is re-shipped as it stands.

**Recorded:** rounds 3 and 4 as `orh:ReleaseEvent` individuals; registration intent 1.2.0 → 1.3.0.


## v1.10.0 — 2026-07-28 (MINOR: Phase-D proposal handed over)

The register-data-convention question moved from an internal note to a **formal handover proposal**,
`06-package-provenance/backlog_framework_register_data_convention_proposal_v1_0_0.md`, addressed to
OEE and shaped by L-X7's operational form: measured evidence, alternatives, verification method.

**Why a handover rather than a decision:** the naming conventions live in the configuration subject,
which is OEE's. L-X7 is explicit that a ruling on a decision is not authorisation to act on another
session's artifacts, and round 1 demonstrated the correct shape end to end — we proposed the
independent-package archive convention, OEE ratified and minted it.

**Contents:** the ask in one sentence; three measured facts establishing that the question is real
(16 conventions, none naming register data; a register is structurally an ABox; a register versions
per working session rather than per release); five alternatives — `ABoxFileConvention`,
`OntologyFileConvention`, a 17th convention, `ABoxFileConvention` plus a named exception following
the `SafeguardDotDelimiterException` / `USODelimiterException` precedent, or out of scope — each with
its justification *and* its counter-argument; our recommendation with the evidence that would
overturn it; the cost to us of every possible ruling (none blocking, all one edit or less because the
binding is by IRI); and the commands by which OEE can re-derive every claim.

**Superseded:** the internal note `PhaseD_Question_RegisterDataConvention_v1_0_0.md`, retired rather
than carried alongside its successor.

**Recorded:** round 2 as an `orh:ReleaseEvent` in the registration intent (ORCP invariant 6),
registration intent 1.1.0 → 1.2.0.

**Also flagged, deliberately not asked this round:** which convention governs retained progress
report runs — ABox as Turtle, `AuditReportMarkdownConvention` as Markdown.


## v1.9.0 — 2026-07-28 (MINOR: quality facet closed; Phase-D question prepared)

**Quality facet — closed with computed numbers, not a token instance.** The pack ships a large
quality subject (OQuaRE and OntoQA frameworks) but **zero** QualityAssessment individuals, and the
quality SHACL suite has **no shape targeting QualityAssessment or QualityMetric** — so nothing
structural was required and a one-line instance would have passed. The registrant precedent in the
pack is exactly that: type, label, `assessesArtifact`, source. We measured instead.

`backlog_quality_assessment_v1_0_0.py` computes nine OntoQA structural metrics from the shipped TBox
and ABox at run time, so every value is re-derivable rather than asserted:

| Metric | Value |
|---|---|
| RelationshipRichness | 0.633 |
| AttributeRichness | 1.176 |
| InheritanceRichness | 0.802 |
| ClassRichness | 0.275 framework-only · **0.835** with the adopter fixture |
| AveragePopulation | 1.198 framework-only · **2.077** with the adopter fixture |
| Deepness | 3 |
| NumberOfRootClasses / NumberOfLeafClasses | 18 / 85 |
| AnnotationRichness | **1.000** — all 324 terms carry a `skos:definition` |

Both population readings are recorded rather than the flattering one: the framework ABox holds
framework-level individuals only, so measuring population against it alone understates the subject
by design.

**Scope stated, not implied (L-74):** structural metrics only. No OQuaRE tier-weighted scoring, no
OOPS! pitfall scan, no usability profiling, nothing requiring a stakeholder judgement. The emitted
assessment says so in its own `skos:definition`, so the limitation travels with the data.

**Found and fixed while measuring:** the population metrics counted only instances whose IRI was in
our namespace, so merging the adopter fixture changed nothing — a second reading that silently
reproduced the first. Population now counts every instance of our classes whatever namespace it
lives in, and the second reading moved from 0.275 to 0.835. A number that fails to move when it
should is the quietest kind of broken measurement.

**Phase-D question prepared, deliberately not closed.** `PhaseD_Question_RegisterDataConvention_v1_0_0.md`
states the question, the three candidate conventions, our recommendation (`ABoxFileConvention`, and
no sixteenth convention), and the fair argument against it. The ruling is OEE's: the configuration
subject is theirs, and minting a register-data convention locally would be the parallel-source-of-truth
failure this package has avoided everywhere else. Either ruling costs us one edit, because the
binding is by IRI.

**Validated:** emitted graph 280 triples, 0 attributable violations across all six pack suites at
`inference=none`, baseline 3/3 reproduced.


## v1.8.0 — 2026-07-28 (MINOR: registration outcome recorded)

**Registration CONFIRMED** against OE Pack v20.23.39, token `BACKLOG-FRAMEWORK-REGISTERED`. The
submitted archive was re-derived by OEE in full: manifest 41/41, parse 14/14, and the three-fixture
self-proof reproduced rather than trusted — positive 0, negative 280, adversarial 13, coverage 36/36.

**Verified on this side before recording anything** (BP-D2, L-80 — a confirmation is a summary like
any other): archive digest matches; roster anchor `orh:Subject_backlog` present as the 19th subject
with `facetRole=registration`; both candidate lessons present in kb ABox v2.16.0 as **L-107** and
**L-108** with attribution to our deposit; `configuration:IndependentPackageArchiveConvention`
present in configuration ABox v2.5.0 with the proposed pattern; all 21 held deposit files
byte-identical to those shipped; the six-suite Phase-B check still 0 attributable on the new pack.

**Updated:** staging declaration 1.1.1 → 1.2.0 (registered; target release now names v20.23.39, with
`integratesInto` still unusable because the pack declares no `ProjectArchive` individual after
v17.32.0 — stated rather than worked around); naming proposal 1.0.0 → 1.1.0 (marked ratified,
superseded by the governed individual, referenced not re-declared); lesson deposit 2.0.0 → 2.1.0
(marked adopted, pointing at the governed IRIs); registration intent 1.0.0 → 1.1.0 (round-1 outcome
recorded as a release event).

**No ontology, shape, rule, fixture or tool content changed.** The subject stays at 1.7.0.

**Still open, ours to close:** the quality-facet assessment, and the Phase-D question of whether
`ABoxFileConvention` is the right fit for governance-register data — logged by OEE as live, to be
brought whenever a ruling is wanted.


## v1.7.0 — 2026-07-28 (MINOR: register packaging)

**Trigger.** An audit question: are there packaging requirements for backlog, roadmap and progress
files, and do they match OE configuration management? Measured answer: **no packaging vocabulary
existed at all** — 417 terms, none about shipping. The framework demanded evidence discipline of
adopters while its own package followed OE's configuration rules release after release.

**Added — subject `backlog` 1.6.0 → 1.7.0 (MINOR):** `RegisterPackage` (versioned, naming its
register), `RegisterArtifact` with a closed five-role set, `conformsToNamingConvention` pointing at
`configuration:NamingConvention` **by IRI** rather than restating patterns, `hasManifestSHA256`, and
`reportRunRetainedAs` so progress runs survive the terminal.

**Added — enforcement (`backlog-shapes` 1.7.0):** exactly one manifest carrying its own digest;
register data always present; profile declaration at L2; at least one retained report run at L3; and
a retained run older than the register's latest transition is a violation.

**Added — tooling:** `backlog_package_check_v1_0_0.py` reads the pack's 15 naming conventions at
check time, translates each `filenamePattern` to a regex mechanically, and validates declared
filenames. Without `--pack` it reports NOT RUN rather than passing.

**Found and fixed during the work:** the package version pattern was first written with an escaped
dot that survived two levels of Turtle/SHACL escaping incorrectly — it passed the positive fixture
while being unable to match anything, a check that looked green because nothing tested it
negatively. Replaced with a character class and proven to reject `1.3`.

**Open, disclosed:** OE has no convention for a governance-register data file; `ABoxFileConvention`
is used as the natural fit, which is this framework's judgement and a Phase-D question for OEE.


## v1.6.0 — 2026-07-28 (MINOR: OE registration compliance)

**Trigger.** A readiness question, assessed against the pack's physical files rather than its
protocol text. The pack contains two completed registration confirmations; those record what was
actually verified before acceptance, and the standard they set is stricter than the protocol
document. Measured against it, this package was **not ready** — three gaps.

**Fixed:**
- **B1 compliance.** The lesson deposit minted two `kb:` subjects. The accepted precedent required
  **zero OE-namespace subjects** from a registrant. Deposit re-emitted at v2.0.0 (MAJOR — subject
  IRIs changed) with registrant-local individuals typed by the OE class, relating to `kb:` IRIs only
  as objects.
- **Phase-B emission added** (`oee_registration_emission_v1_0_0.ttl`): registrant-local subject
  anchor with `orh:lifecycleStatus`, five ontology artifacts as `core:Artifact` at
  `core:Profile_Standard` (reused, not minted), five release gates as `testing:Test`.
- **Readiness tool v1.1.0**: new `NS` control (zero OE-namespace subjects) and a rebuilt `X` control
  validating the emission against all six pack suites at `inference=none`, re-deriving the pack's
  baseline against an empty graph so baseline noise is separated by measurement, not by citation.

**Measured:** 0 attributable violations across core / knowledge_base / release-history / testing /
configuration / quality; baseline 0/0/0/0/3/3 re-derived; B1 clean; emission 196 triples, 29
subjects. Readiness controls **11/11 pass**.

**Found and fixed during the work:** the new namespace control was defined with the same function
name as the existing bundle-completeness control and silently shadowed it — the bundle check stopped
running while still appearing to pass under a different label. Caught by reading the control output
against the documented control list.


## v1.5.0 — 2026-07-27 (MINOR: mission, scope boundary, external dependencies, session hygiene)

**Added — subject `backlog` 1.5.0 → 1.6.0 (MINOR):**
- **`Mission`** as the root of the intent chain, owner-declared, with goals contributing to it. Every
  value claim now traces mission → goal → objective → observation and terminates in something an
  observation can contradict. Goals must carry at least one objective at L2 and must reach a mission
  at L3, so "objectively measurable" is enforced transitively rather than asserted.
- **Scope bound to intent and outcome:** `scopeRealizesObjective`, plus rules R11 and R12 deriving
  `scopeCompletionState` and then `scopeOutcome`. Completion and success are derived separately and
  in that order, so a development can report that it delivered everything it promised and still
  failed — the outcome most plans are structurally unable to express. At L2 a scope must realise an
  objective, must state at least one exclusion, and once complete must carry an outcome.
- **`ScopeChange`** — owner-decided, rationale-bearing admission of work into a set scope. The
  framework does not forbid scope from growing; it forbids scope growing invisibly.
- **`ExternalDependency`** over a closed six-type taxonomy (vendor, upstream component, peer team,
  regulatory, infrastructure, customer), orthogonal to the knowledge/task/resource dependency kinds:
  the kind says what would release it, the type says who must act.
- **`EnhancementProposal`** with a closed status set, and the rule this release exists for: an item
  that `requiresExternalEnhancement` must have a proposal raised for it (L1); may not be Ready or In
  Progress until that proposal is Accepted (L2); and if the proposal is Rejected must be re-planned,
  cancelled, or admitted locally by an explicit `ScopeChange` (L2). A proposal may not itself be a
  work item.
- **`RegisterSession`** — provenance of register edits: a session that changed items must record that
  it verified the register's state first, and must state what it deliberately left alone. Scoped
  narrowly to edit provenance; meeting and ceremony modelling remains a declared non-goal.

**Measured:** positive fixture 0 violations; negative fixture 268 violations across 61 planted
defects; adversarial register 13 violations; coverage 36/36; Gate K clean; readiness 10/10.


## v1.4.0 — 2026-07-27 (MINOR: falsifiability)

**Trigger.** A parallel session reported that a register built with the framework could be
arbitrary, with no way to tell success from failure. The claim was tested rather than accepted: an
adversarial register was authored to be maximally meaningless while formally correct, and against
v1.3.0 of this package it validated at **L3 with 0 violations**. The claim was true. Every
constraint written until then checked whether a register was well *formed*; none checked whether it
could be *wrong*.

**Added — subject `backlog` 1.4.0 → 1.5.0 (MINOR):** `MetricObservation` with method and timestamp;
`hasTargetDirection` and the closed `MetricDirection`; derived `objectiveOutcome` and
`milestoneOutcome` over a closed `AchievementStatus` that includes **Missed**; `achievedAt` on
milestones; `Rebaseline` recording owner-decided target moves with the previous value retained;
`hasActualEffort`; `verifiedByTool`.

**Added — enforcement (`backlog-shapes` 1.5.0):** WSJF and RICE values checked against their own
components; scores without components or rationale rejected; scores predating the last completion
rejected at L3 per BP-D11; objectives without a direction, or with target equal to baseline, or past
deadline with neither observation nor re-baseline, rejected; milestones past date with no outcome
and no re-baseline rejected; bare-assertion verification methods rejected and a naming tool required
at L3; Gherkin-shaped but empty acceptance criteria rejected; completed items with an estimate but
no actual rejected at L3; items tracing to no objective upgraded from advisory to L3 violation; a
roadmap rank contradicting the score order required to carry a rationale.

**Added — rules R9 and R10** deriving objective and milestone outcomes from observations and dates.

**Added — third mandatory self-proof.** `fixture_adversarial_random_v1_0_0.ttl` ships with the
package and the release gate aborts if it ever passes again. Against v1.5.0 it produces 13
violations.

**Measured:** positive fixture 0 violations; negative fixture 235 violations across 52 planted
defects; adversarial fixture 13 violations; coverage 36/36; Gate K clean; readiness controls 10.

**Still open, recorded not fixed:** the framework cannot verify that a metric observation was
honestly obtained (only an execution bridge extended with metric collectors could), and it cannot
establish that delivered work *caused* an observed improvement. Both are stated in
`Falsifiability_Audit_v1_0_0.md` rather than left implicit.


## v1.3.0 — 2026-07-27 (MINOR: fit-gap against the agile literature)

**Trigger.** A comprehensive fit-gap review against agile ontologies and standards in the
literature. Sources were retrieved and read this session per BP-D41 rather than recalled: the Scrum
Guide 2020, OntoAgile (DYNA 86(209), 2019), Strode's dependency taxonomy (Information Systems
Frontiers 18(1), 2016) and the Kanban flow measures. Seven gaps were found.

**Added — subject `backlog` 1.3.0 → 1.4.0 (MINOR):** `decomposesInto` / `partOf` with derived
`decompositionState` — the epic-feature-story ladder previously had no part-whole relation at all;
`Commitment` binding goals and the Definition of Done to the artifacts they qualify; `Dependency`
with `hasDependencyKind` over Strode's knowledge/task/resource set; `Impediment` as distinct from
dependency; `startedAt` / `finishedAt` and `WipLimit` so flow is measurable; `Team`, open-ended
`TeamRole` and `hasCapacity`; and the canonical story clauses `asRole` / `wantsCapability` /
`soThat`.

**Added — enforcement (`backlog-shapes` 1.4.0):** decomposition cycles, parent Done over an open
child, parent-and-child double scoring, empty commitments, registers without a goal commitment,
increments without a Definition of Done, untyped dependency records, unowned impediments, malformed
flow points, WIP-limit policy integrity plus a breach advisory, teams without a register, and a
story-form advisory. Rule R8 derives decomposition state.

**Declared non-goals with reasons:** agile values and principles, practice/activity/task/tool
process modelling, agility assessment, ceremony modelling, and story-point scales — each explained
in `Agile_FitGap_Analysis_v1_0_0.md` rather than left as an unexplained absence.

**Measured:** positive fixture 0 violations; negative fixture 186 violations across 52 planted
defects; coverage 36/36; Gate K clean; readiness controls 10.


## v1.2.0 — 2026-07-27 (MINOR: linkage between concepts)

**Trigger.** A review question with a different shape from the last one: not *are the concepts
present*, but *are they connected*. A package should contain items, depend on other packages and hold
a rank on the roadmap; every item should carry both a Definition of Done and acceptance criteria,
with a test harness proving both before it can be called complete; and the lifecycle should have a
workflow of permitted transitions, not just a set of states. A linkage audit found five of those
connections missing outright and two only partly enforced.

**Added — subject `backlog` 1.2.0 → 1.3.0 (MINOR):**
- `containerDependsOn` (transitive, cycle-checked) and `derivedContainerDependency` computed from
  member-level edges by rule R5, so a declared package dependency with no basis and a real dependency
  never declared are both visible.
- `rankedOnRoadmap` and `hasRoadmapRank` for containers; `scheduledInHorizon`,
  `contributesToMilestone` and `hasDependencyDisclosure` widened to containers.
- `attestsCriterion` linking evidence to the acceptance criterion it proves, and `TestHarness` with
  `harnessComplete` derived by rule R6 — true only when every criterion of the item is attested by
  bridge-verified evidence.
- `effectiveDefinitionOfDone` derived by rule R7 from the item or an owning container.
- `Workflow`, `StateTransition` (guarded) and `TransitionEvent`, with a shipped default workflow of
  eight transitions covering every state.

**Added — enforcement (`backlog-shapes` 1.3.0):** container dependency cycles, phantom container
dependencies at L2, roadmap rank uniqueness and mandatory placement of launch gates, acceptance
criteria for every item past Proposed, a resolvable Definition of Done, complete harness and
per-criterion attestation at L3, workflow reachability, transitions that are typed/named/guarded and
non-self-looping, moves that use a permitted transition, and state matching the latest recorded move.

**Added — report section 9, Lifecycle and workflow:** state counts, the permitted moves with their
guards, and any item whose state its own history does not explain. Sections 6 and 7 now print
container dependencies and the declared roadmap rank beside the score-implied rank, showing a
disagreement rather than resolving it.

**Found by the change, fixed here:** widening `disclosesDependencyOn` to containers left its shape
still requiring an item-level edge, so the framework's own positive fixture failed — L-42, a
relationship changed on one side and verified on one side. The type check also had to walk
`rdfs:subClassOf*`, since a `Story` is not asserted to be a `WorkItem` without inference. The report
tool was treating `ImplementationProject` as an item and reporting the project as an orphan.

**Measured:** positive fixture 0 violations; negative fixture 150 violations across 44 planted
defects; coverage 36/36; Gate K clean; readiness controls 10.


## v1.1.0 — 2026-07-27 (MINOR: concept completeness + registration controls)

**Trigger.** A review question: are goal, objectives, scope, backlog items, grooming, packaging,
coverage, containment, dependencies, benefits, opportunities, costs, risks, build-versus-maintain
prioritisation, Definition of Done, acceptance criteria and ranking all present, unambiguous and
gated? An audit against that twenty-concept checklist measured **10 of 20** present on vocabulary
alone. This release closes the gap and adds the controls a future OE registration round needs.

**Added — subject `backlog` 1.1.0 → 1.2.0 (MINOR, nothing removed or renamed):**
- **Intent layer:** `Goal`, `Objective` (success metric via `core:Metric`, baseline, target,
  deadline), `Benefit` (owned via `core:Stakeholder`, attached to an objective, realisation claim
  requires verified evidence), `Opportunity` (with explicit conversion into a work item).
- **Scope:** `ScopeStatement` and owner-decided `ScopeExclusion` with mandatory rationale.
- **Refinement:** `RefinementEvent`, and an L2 gate that refuses the `Ready` state to an item with no
  acceptance criterion or no recorded refinement — readiness is now earned rather than assumed.
- **Cost:** unit-neutral `CostEstimate` carrying basis, confidence and date; a naked number fails.
- **Risk:** delegated to the pack's `risk:Risk` / `risk:Mitigation` per ISO 31000 rather than minted,
  with binding properties and the constraint that an untreated risk must name its acceptor.
- **Build versus maintain:** `InvestmentCategory` (new capability / maintenance / technical debt /
  compliance), `ProductLifecyclePhase` (pre-launch / live / sunsetting) deciding which prioritisation
  question governs, and `PortfolioPolicy` with capacity shares that must sum to one.
- **`ImplementationProject`** as the container the project-level Definition of Done applies to.

**Added — enforcement (`backlog-shapes` 1.2.0):** thirteen new shapes covering objectives, benefits,
opportunities, goals, exclusions, refinements, the readiness gate, cost basis, risk treatment,
capacity policy, projects, investment categorisation at L3, and an advisory for items that trace to
no objective.

**Added — `DoD_ProjectBaseline`:** eight executable project-level criteria (launch gates cleared,
zero silent gaps, blueprint sweep complete, Done items evidenced, objectives measurable, benefit
claims evidenced, risks treated or accepted, capacity policy complete).

**Added — ORCP registration controls:** `backlog_registration_readiness_v1_2_0.py` (10 controls
traced to protocol clauses, all numbers recomputed at run time), `registration_intent_v1_0_0.ttl`
(Phase A self-classification across 8 facets plus the round-1 release event), and
`Registration_Controls_v1_0_0.md`.

**Measured:** concept completeness 20/20 on all three axes (vocabulary, enforcement, demonstration);
positive fixture 0 violations; negative fixture 94 violations across 37 planted defects; coverage
36/36; Gate K 8 declarations; readiness controls 10, with cross-facet validation of the round record
against the pack's own release-history suite returning 0 violations.

**Found by the new controls, fixed here:** the manifest had been generated before the final
`VERSION.txt` write, leaving one hash stale — caught by control C2 on its first run. A second
coverage probe (C29) proved brittle for the same reason as C10 in v1.0.1: it matched a single
formatted line rather than the fact it tested, and broke when the `priorVersion` chain gained a
second entry. Both probes now test the fact, not the formatting.


**Bundle lineage note.** From v1.0.0 of the `backlog-roadmap-framework` lineage, the archive is
named `backlog-roadmap-framework-v{M}_{m}_{p}.zip`. The three entries below it — 1.1.1, 1.1.0 and
1.0.0 — shipped under the retired name `oepack-backlog-framework` and are kept with their original
numbers rather than renumbered. A new scope label is an ORIGINATION under BP-D13, so the bundle
counter restarts; **no ontology identity was renumbered by the rename**, and their version chains
continue unbroken. See `Naming_Decision_Record_v1_0_1.md`.

## v1.0.1 — 2026-07-27 (PATCH: filenames only)

Comprehensive case-insensitive scan of every file and directory name for OE-ecosystem tokens. Two
document filenames carried "OE" as a bare qualifier and were renamed to
`Discipline_Ceremony_Record_v1_0_0.md` and `Discipline_Ceremony_Record_Addendum_v1_1_0.md`; each
document now names the OE Operating Discipline v2.2.0 in its opening lines instead. Five further
matches were kept with reasons — `ORCP_` is the proper name of the protocol the submission is
addressed to, `01-ontologies/` is a load-bearing path, and two "pack" hits were substring false
positives on "package". `oe-prov:` attribution IRIs inside ontology headers are untouched: BP-D24
requires attribution through shared IRIs and L-82 forbids re-declaring foreign terms. Full
disposition table in `Naming_Decision_Record_v1_0_1.md`. No ontology, shape, rule, fixture or tool
content changed.

The same scan also exposed a stray empty directory literally named
`{01-ontologies,02-shacl-safeguards,03-tooling` — the residue of a brace expression that the shell
running the very first scaffold command did not expand. It contained no files and was shipped,
harmlessly but untidily, in every bundle up to and including v1.0.0. Removed here. Worth naming
rather than quietly deleting: `MANIFEST_SHA256.txt` hashes files, so Gate 0 cannot see a directory
that contains none, and the defect survived four release-gate runs because nothing in the gate set
inspects directory structure. The filename scan the owner asked for is what caught it.

## v1.0.0 (new lineage) — 2026-07-27 (rename only)

Archive renamed from `oepack-backlog-framework` to `backlog-roadmap-framework` because the
`oepack-` prefix is a fixed token of the OE Pack archive convention and therefore reads as a
membership claim this independently distributed package does not make, and because the scope label
omitted the roadmap, prioritisation and ranking methodology the package governs. Contents are those
of bundle 1.1.1 plus the rename record, the proposed independent-package naming convention, and
this decision record. No ontology, shape, rule, fixture or tool content changed.

## v1.1.1 — 2026-07-27 (PATCH: packaging metadata only)

**Trigger.** A question about why the archive carries the `oepack-` prefix surfaced a BP-D15 gap:
the bundle's contents are authored for future integration into an OE ecosystem release, and
BP-D15 makes declaring that target mandatory in the README *and*, where the bundle ships an
ontology, machine-readably. v1.1.0 said "evaluated deposit, not a ratified OE Pack release" in
prose, which is honest but is not the mandated form and is not machine-checkable.

**Added:** `06-package-provenance/backlog_staging_declaration_v1_0_0.ttl` — declares the archive a
`configuration:StagingArchive` with `configuration:targetRelease`, chosen over
`configuration:integratesInto` because the target archive has not been authored and that property
requires a real `ProjectArchive` IRI. README gains a Provenance section stating lineage
(ORIGINATION), "Derived from:", and "Integrates into:" in BP-D14/BP-D15 wording.

**Scope of the declaration (L-X6).** It states that the subject is offered for integration and
that this archive stops being canonical once an integration ships. It does **not** state that the
contents are part of any OE Pack release, that any pack file was modified, or that an adopting project
deposit is superseded.

**Also fixed in this PATCH, both found by running the gates after the change:**
- **Gate K had a blind spot.** It globbed only `01-*`/`02-*`, so the new provenance ontology —
  which carries version metadata like any other — was never checked. Widened to every shipped
  Turtle file; the gate now inspects 6 declarations instead of 5.
- **A coverage probe was passing for the wrong reason.** C10 (TBox/ABox/Rules separation) probed
  for filename strings, which matched only because the tooling pinned those paths. Making the
  tooling resolve pointers by pattern removed the pins and dropped coverage to 35/36, exposing a
  probe that had never tested the concept. It now probes the three distinct ontology IRIs, which
  is what separation actually means. This is L-95 under-applied: the coverage gate had no negative
  fixture, so a false-positive probe survived. Recorded here rather than as a new lesson, because
  the governing rule already exists.
- **Tooling now resolves ontology pointers by pattern** (highest `stem_v*.ttl`), the same
  version-independent rule the OE Operating Discipline applies to its own references, so future
  ontology bumps no longer require editing tools.

**Not changed:** no ontology, shape, rule, fixture or tool content. The subject remains `backlog`
1.1.0; no version of any ontology identity was bumped, because none of them changed.

## v1.1.0 — 2026-07-27 (MINOR: additions only)

**Trigger.** The governing standard document was supplied after v1.0.0 shipped. v1.0.0 had been
built without it: the URL returned HTTP 404 (private repository), and the framework was
generalised instead from an adopting project's product-backlog deposit, with the coverage gate declared
NOT RUN and recorded as an open dependency. With the document on disk the gate ran and measured
**22.2% (8/36)**. Every intrinsic gate had passed at that coverage — parse, SHACL, manifest, gate
self-proof — which is exactly the blindness a primary-source gate exists to close.

**Added — vocabulary** (`backlog` 1.0.0 → 1.1.0, no term removed or renamed):
- Blueprint layer: `Blueprint`, `DomainEntity`, `EntityLifecycleStage` (four stages),
  `ComplianceObligation`, `BlueprintGap`, `CapabilityClass`, `EnforcementDomain`, with coverage
  and gap properties.
- Launch-readiness model: `isLaunchGate`, `hasLaunchPriority`, `Role` (Owner / Builder),
  `decidedBy`, `hasDecisionRationale`, `RankingModel` (Throughput / LaunchScoped).
- Gap discipline: `notYetScoreable`, `hasScoreabilityReason`.
- Capability and dependency: `isBusinessCapability`, `DependencyDisclosure`, `hasExternalBlocker`,
  `isAveragedFromMembers`.
- Documents and reports: `GovernedDocument`, `DocumentStatus` (Live / Superseded), `supersededBy`,
  `RoadmapReport`, `ReportSection`, `hasRunTimestamp`, `derivedInReport`, `underRankingModel`.
- Governance: `MethodologyRule` with `hasRuleLogic` / `closesDisagreement` /
  `hasMotivatingIncident`, and `ReleaseGate` with command and order.
- `hasPriorityScore` domain widened to include containers (backwards-compatible).

**Added — enforcement** (`backlog-shapes` 1.0.0 → 1.1.0): silent-gap violation at L2, scoreability
flag integrity, launch gates as owner decisions, non-capabilities barred from launch priority,
container scores judged not averaged, disclosed dependencies must exist as edges, deployability
versus completion, full life-cycle sweep at L3, code-verification claims carry their method,
supersession marked in place, reports complete and timestamped, rules keep their incident, gates
executable and ordered.

**Added — derivation** (`backlog-rules` 1.0.0 → 1.1.0): R4 external-blocker derivation; R3
arbitration documented and implemented in the report tool.

**Added — tooling:** `backlog_roadmap_report_v1_3_0.py` (eight sections, both NEXT answers, silent
-gap check), `backlog_coverage_gate_v1_1_1.py` (BP-D31), `backlog_gate_v1_1_7.sh` (Gate 0 / P / K /
R plus coverage), Gate K version-identity check in the validator.

**Changed:** the v1.0.0 advisory "item carries no priority score" now excludes items correctly
flagged not-yet-scoreable, and its message points at the L2 violation that supersedes it.

**Retired:** the v1.0.0 ontology, shapes, rules, tooling and fixtures are not carried alongside
their successors — one current file per identity, with the lineage in `owl:priorVersion`.

**Measured this release:** coverage 36/36 (100%); positive fixture 0 violations; negative fixture
46 violations across 28 planted defects; R3 disagreement fixture 0 violations with the
disagreement branch observed firing; Gate K 9 declarations, 0 mismatches.

**Lesson screening (L-84 / L-71):** one candidate lesson was considered for this release — that a
derivative artifact is not a proxy for the standard governing it — and was **rejected as a
duplicate** of L-58 (pipeline metrics do not measure source fidelity) combined with BP-D31.
Recording it would have been checklist compliance, not a new lesson. The two candidates deposited
with v1.0.0 stand unchanged.

## v1.0.0 — 2026-07-27

First release. Domain-neutral generalisation of an adopting project's product-backlog deposit
(`product-backlog` 1.3.0): work items and containers, closed lifecycle, evidence-bound completion,
method-parameterised priority scores, roadmap as a projection, conformance levels L1-L3, a
self-proving gate, and an execution bridge. Built without access to the governing standard
document; see the trigger note above.
