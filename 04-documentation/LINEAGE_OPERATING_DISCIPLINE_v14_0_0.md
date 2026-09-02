# Lineage Operating Discipline — v14.0.0

**Authorship.** Maintained by the session that owns `backlog-roadmap-framework`. v1.0.0 was written
elsewhere and shipped inside this package; its ceremony, its six boundaries and its self-checking
mechanism were sound and are carried forward substantially unchanged. What v2.0.0 adds is authorship
in the right place and three things v1.0.0 predates: deployment gating, release-time test coverage,
and a lesson about closed enumerations that this framework learned by breaking itself.

**Relationship to the OE Operating Discipline.** That document governs how an ontology is *built and
released*; this governs how a *lineage is built inside one*. Where both apply the OE ceremony runs
first — a lineage grounded on unverified bytes is a lineage about nothing.

**Governance source.** The highest-versioned file matching `name_v*.<ext>` in this package.
`MANIFEST_SHA256.txt` is authoritative for what is present. Never resolve by a pinned filename
remembered from a previous session; this document's own tooling references have moved four times.

---

## The lineage ceremony — execute before the FIRST work item, not after the twentieth

1. **Declare the level.** `L1_Core`, `L2_EvidenceBound`, `L3_Governed`, `L4_LineageEnforced`. Record
   it as an owner decision carrying a **rationale**, a **target level** and a **review date**. Every
   validator run prints what the declaration *suppresses*; read that line. A clean result at a low
   level is a **narrower claim**, not a better one.
2. **Build the chain as a PIPELINE, one commit per stage.**

   `Mission` → `ScopeStatement` (text, exclusions **and deliverables**) → `Goal` → `Objective` →
   `Backlog`. Five stages, and **each closes in its own commit** before the next begins.

   Closing a stage means: write its elements, run the validator, commit, then record a `StageOutput`
   naming the stage, the digest of the state it closed on, and **the commit it closed at**. The next
   stage's output `consumesOutput` that one.

   **Why one commit per stage, and not merely one instruction.** A digest over the register is
   computable from the finished state — proven by experiment, where an author building backwards and
   computing each digest from the final graph passed every digest check. Only an external witness
   orders the stages, and a commit is the only one available: append-only, held by a remote the author
   does not control. Git orders **between** commits and says nothing **within** one, so two stages
   sharing a commit are unordered evidence however they were built.

   **The scope stage is not closed until its deliverables exist.** Text alone is a boundary that can
   refuse nothing. Measured on this package: `Scope_Build`'s text was written at `a20c9eb` and its
   deliverables arrived at `90c433b` — after the epics they were meant to constrain.

   Validate the chain empty at each stage. A chain that does not validate empty will not validate full.

3. **State the granularity you are choosing and why.** `Initiative`, `Epic`, `Feature`, `Story`,
   `Task`, `Defect`, `Spike`, `Enabler`. Epic is the **coarsest ordinary choice**, not the neutral
   one. A granularity nobody chose is one nobody can defend later.
4. **Decide how work reaches users.** `PlanningEvent` → `Iteration` → `DeploymentUnit`. Decide this
   before the first story, because at L4 a closed iteration with no deployment is a violation and
   retrofitting a release history is fabrication.

If you cannot complete steps 1–4, **STOP and ask.** Creating work items against an unbuilt chain is
the failure this ceremony exists to prevent, and it is not cheaply recoverable.

---

## Eight standing boundaries the ceremony does not structurally reach

### G1 — Granularity by momentum
The first class reached for becomes the default and is never revisited. One session ran fifteen turns
with 29 work items, every one an `Epic`, and found it only when directly asked to audit.
*Surfaced by* `LineageDepthAdvisoryShape` — which is **not** level-gated and fires at L1. If it never
fired for you, the full shapes file was never run.

### G2 — Advisory blindness
A warning nobody reads protects nothing. The validator groups advisories by message rather than
printing a total, because *"175 Warning"* is a number a reader learns to skip. **L4 exists because
this boundary is not solvable by better wording.**

### G3 — Permitted is not intended
`Epic ⊑ ProductBacklogItem` is true, and does not license planning an undecomposed epic into an
iteration. **A subclass relation answers what may be asserted; a definition answers what the term
means.** Two sessions made this error from opposite ends within a day.
*Enforced by* `EpicPlanningShape` at L2.

### G4 — Completion is not accomplishment
Completion is a fact about **effort**; accomplishment is a fact about the **world**, and only the
second requires a measurement. A register of Done items proves the first and says nothing about the
second. *Enforced by* `L4MeasuredObjectiveShape` (unconditional since v1.152.0, when
conformance-level gating was removed entirely): every objective carries a `MetricObservation`,
whatever the reading said.

### G5 — Why, when, and what are three questions
`Epic` answers **why**, `Iteration` answers **when**, `DeploymentUnit` answers **what users
received**. Conflating them is the commonest drift observed here: an epic in a sprint looks like
planning and commits nothing anyone can finish; an epic in a release names something that cannot
ship. *Enforced by* `L4GroomingShape` (unconditional since v1.152.0).

### G6 — Drift is the default, not the exception
**Corollary from v3.0.0:** drift is *detected* identically whichever order the chain was built in —
`L4DriftShape` fires on an item pursuing an unrealised objective either way, verified by construction
on both. What the order changes is **when a human notices**: scope-first surfaces the conflict while
the objective is being written, scope-last surfaces it only once work exists to be rejected.
Work migrates outside the declared boundary unless something objects. *Enforced by* `L4DriftShape`
(unconditional since v1.152.0):
an item pursuing an objective the scope does not realise is a violation. Reversing an exclusion is
legitimate — record a `ScopeChange`; **the exclusion is superseded, never deleted.**

### G7 — A tool that refuses is not thereby correct
Three defects in this framework's own tooling were plausible refusals or meaningless clean passes: a
cumulative flow reading a property that never existed, a burn-down reaching zero over open work, a
date comparison reporting future deadlines as passed. Each *looked* like the tool working.
*No shape catches this.* The check that does is a **fixture whose answer is known in advance**.

### G18 — The lineage is a pipeline; order is enforced by artifact, not by claim
An earlier release concluded that execution order could not be gated. **That was wrong on two counts,
and the owner named both.** The v1.62.0 exclusion forbids requiring a fixed-at *date* and says nothing
about enforcing order; and an ontology has dependency relations, through which order can be enforced.

The model is another registrant's: **each stage consumes the artifact the previous stage produced.** A `StageOutput`
closes a stage; the next stage's elements reference it. An element cannot reference an output that does
not exist, so the dependency is a thing rather than an assertion.

**What the experiments established, in order:**

| Experiment | Result |
|---|---|
| A — stages built in order, digests taken as each closed | every digest reproduces, **PASS** |
| B — same elements, digests fabricated | every digest fails recomputation, **FAIL** |
| C — built backwards, digests computed from the *final* graph per stage | **PASS** |

**C is the finding that matters.** A digest over the register is computable from the finished state, so
it proves nothing about order. Any check that reads only the register can be satisfied at the end.

**Order therefore requires an externally witnessed anchor.** `closedAtCommit` names the governed-repo
commit at which a stage closed — append-only, held by a remote the author does not control. Its limit
is equally measured and equally stated: **git witnesses order between commits and says nothing about
order within one**, so a lineage authored in a single commit is unordered evidence however it was
actually built. An advisory reports exactly that case.

### G17 — A scope must have content of its own, or the backlog defines it
Writing the scope before the goals is not enough. A scope of prose has nothing to measure work
against, so coverage is computed over **the work that happens to exist** — and both sides of the
fraction become the backlog.

Measured here: `Obj_ScopeDelivered` counted stories pursuing an objective under the scope and divided
by the same set. It read **100% whether the scope was satisfied or merely emptied**, and would have
read 100% with a single story or with none.

That is the epic-driven lineage in its exact form. Not that epics are written first — they may
correctly come after — but that **whatever the epics deliver becomes the definition of what the scope
wanted.**

`ScopeDeliverable` fixes it: enumerate what the scope requires when the scope is written, read from
the mission clause by clause. A deliverable states **what must be true**, not what someone will do.
The test of a real boundary is that its coverage figure **can fall** — add a deliverable nothing
satisfies and it drops immediately. A figure that cannot fall is not measuring anything.

### G13 — The chain is Mission → Scope → Goals → Objectives, and it reads the same both ways
Goals are **derived from the scope**, not attached to the mission. The scope is built to satisfy the
mission; goals are derived from the scope so that *the scope's fit to the mission is what gets tested*;
objectives are set to measure the goals. Read downward or upward, the same answer must come out.

The failure this prevents was structural and invisible for the whole life of this package: `Goal`
carried exactly one property, `contributesToMission`, so **the scope sat outside the path between a
goal and its mission**. A goal could serve a mission the scope never admitted and nothing objected.

### G14 — Every intent element records who authored it, not only the mission
`MissionOrigin` was added at v1.70.0 after a session wrote five missions and attributed them to the
owner. It was applied to `Mission` **and nowhere else** — so the same failure moved one level down and
recurred *in the release that corrected it*: the same session then wrote the scope, the goals and the
objectives beneath the corrected mission, and attributed those to the owner too.

**A fix applied to one node of a chain moves the blind spot rather than closing it.** When a mechanism
catches a class of error, apply it to the whole class.

### G15 — Pursuing an objective and being able to move it are different claims
`pursuesObjective` records intent. `metricMovableBy` records capability. A register can reach every
epic Done with every objective unmet and flag nothing, because no constraint ever asked whether the
work beneath an objective could shift its metric.

When they disagree, **adjust the backlog, not the objective**. Re-targeting an objective to meet the
work is moving the goalpost to meet the shot.

### G16 — Development is anchored on packages, not iterations
Work reaches users through regularly deployable packages built from the highest-priority items. A
register where completion and delivery are separate records measures the first and assumes the second.
Measured here: **43 of 47 Done items sat in no package**, while the framework shipped 78 real releases
its own register never recorded.

### G11 — Run at the level you enforce, or the rules are decoration
A package that declares a conformance level below the one its own framework enforces exempts itself
from the rules it publishes. Measured on this package: **16 of 57 level-gated constraints did not run
and 166 violations were invisible**, including fourteen forked chains that the L4 rule *written to
catch them* could not see.

**This is the mechanism behind every drift in this package's history.** A rule is built at L3 or L4 to
prevent a class of error, and then never runs against the register containing that error. Nothing
lies: the gate reports green, the level is declared honestly, and the suppression count is printed —
and read past.

A declared level below the target is legitimate; that is how adoption works. What is not legitimate is
leaving the distance unmeasured. **Test-drive the target level and record what it reports.** A target
nobody has measured against is a wish, and a target with no review date is a permanent exemption
wearing the language of a plan.

### G12 — A superseded lineage is a record, not a claim
When a mission is superseded, the chain beneath it stays. Re-pointing goals to remove an inconsistency
would assert an intent never held — the fabrication L-112 forbids one level up. Constraints on chain
integrity must therefore exempt superseded lineage: the defect is real, stays visible, and must not
block a live release.

The corollary is the warning: **fourteen forks arose because missions were invented one per release
batch**, each summarising work already shipped. Scope-first fixes the boundary; nothing yet fixes a
mission written the same way, which is why mission provenance became a constraint.

### G9 — A constant iteration, and stories split to fit it
An iteration is a **fixed** time box. Sizing it to the longest story inverts the control: if its
length is set by the work it contains, you always fit, and velocity becomes a tautology that can
never tell you that you did not. Assessing iteration length after story-writing fails for the same
reason one step later — the next change produces a bigger story and the question reopens.

**Set the iteration length once and split stories until they fit.** This is also what the vocabulary
already says: a `Story` is *"small enough to be completed within one iteration"*, so splitting
restores the term's meaning while resizing redefines it. A story outliving its iteration makes
velocity meaningless, and velocity feeds the forecast, so the error propagates into a claim about
the future.

### G10 — Publish each increment, do not batch
A release gate that passes and is not then published leaves the governed store behind the work, and
two unpublished increments cannot be separated afterwards into the releases they should have been.
**Publish immediately after each gate PASS, before starting the next increment.**

Its corollary is easy to miss: **a release gate that cannot finish blocks every release.** This
package's gate grew to eleven full validator invocations and exceeded the publisher's runtime, so a
package that passed its own gate could not be published at all. A gate is part of the release path,
and its cost is a release constraint rather than a detail.

### G8 — Every rule naming a member of a closed set depends on that set's membership
Adding `L4_LineageEnforced` to a four-member enumeration broke three rules that had tested *"below
L3"* by name — they fired on L4, which is above it. *No shape catches this either.* It was caught
because a fixture existed that exercised the new member, which is G7 applied to vocabulary.

---

## Standing operating rules

- **Read the standard in full before the first work item**, SHA-verified — not a fragment, not a
  prior session's summary, including this one's.
- **Version identity**: `owl:versionInfo` = `versionIRI` token = filename token, verified
  programmatically.
- **Gate coverage is re-derived, not hardcoded.** A gate reading a subset reports clean about what it
  did not read.
- **Never fabricate history a project did not have.** Gantt and SPI refusing for a register with no
  kick-off is accurate information, not a gap to paper over.
- **Historical records are corrected by appending, never by editing.** A record edited to look right
  was never a record.
- **A deployment carries only proven work** — at L4 every deployed item is `Done`, carries
  bridge-verified `Evidence`, and has **every** acceptance criterion attested. That last is coverage
  at release time: a suite can be green while the criterion everyone cared about is untested.
  `TestHarness.harnessComplete` already computed this per item long before anything consulted it at
  release. *Enforced by* `L4DeploymentVerifiedShape` (unconditional since v1.152.0).

---

## What this document can and cannot do

It cannot enforce anything. **SHACL enforces; this makes the boundaries visible before the tooling is
reached**, which is the only point at which several of them are still cheap to observe. G7 and G8 in
particular are unreachable by any shape — they are recorded here because that is the only place they
can be.

Its claims about what *is* enforced are themselves checkable, and are checked:
`03-tooling/backlog_lineage_discipline_check_v*.py` verifies that every shape this document names
exists in the shipped shapes file and carries the severity claimed. **A discipline document whose
enforcement claims have drifted from the suite is worse than none, because it is believed.**

---

## v5.0.0 (2026-08-25)

**MAJOR: ceremony step 2 becomes a five-stage pipeline, one commit per stage.** Owner ruling after the
pipeline experiments. The previous step said *fix the mission, then the scope, then goals and
objectives* — one instruction covering four stages, which is why all four could close in a single
commit and their order be unwitnessed. MAJOR because every existing lineage was built under the old
step and none carries stage outputs; they are not rewritten, and the advisories report what their
history actually shows.

## v4.2.0 (2026-08-25)

**G18: the lineage is a pipeline.** Owner correction of two errors in v1.84.0 — a misread exclusion and
a failure to use dependency relations. Settled by three experiments rather than argument: digests catch
fabrication but not careful backwards construction, so order requires a commit anchor, whose own limit
is stated rather than hidden.

## v4.1.0 (2026-08-25)

**G17: a scope must enumerate what it requires.** Owner finding — the lineage was epic-based, with
selected epics becoming the scope and mission subjects. Confirmed by measurement: the coverage metric
divided the backlog by itself. `ScopeDeliverable` gives the boundary content of its own, and the
coverage figure can now fall.

## v4.0.0 (2026-08-24)

**MAJOR: four drift mechanisms, from an owner review of a long session.** The owner observed that the
same failure kept recurring and asked for mechanisms rather than another correction. Four root causes
were found by measuring the register, and each now has a constraint rather than a paragraph:
**G13** the chain must read the same both ways and goals derive from the scope; **G14** authorship is
recorded on every intent element, not just the mission; **G15** pursuing an objective and being able to
move it are different claims; **G16** development is anchored on packages.

MAJOR because G13 changes the shape of the chain: `Goal` gains `derivesFromScope` and every existing
lineage is missing it.

## v3.2.0 (2026-08-20)

Two rulings from a comprehensive fit-gap run as a governed adaptation. **G11**: a package running below
the level it enforces exempts itself from its own rules, which is the mechanism behind every drift this
package has recorded. **G12**: superseded lineage is a record and constraints must exempt it, because
re-pointing it would fabricate intent.

The adaptation's own gates caught this session twice — claiming `BoundaryRewritten` while rewriting no
boundary, and filing two findings as fit-gap findings when neither was work outside a boundary. Both
rejections were correct.

## v3.1.0 (2026-08-11)

Owner correction, and a straightforward one: **the order never needed timestamps.** v3.0.0 treated it
as unrecordable because no intent element carries a date. But the chain's links already run from later
to earlier, so the direction of a single link records the order — the vocabulary was simply missing
the reverse of `scopeRealizesObjective`. `fillsScope` supplies it. An adaptation procedure ships for
lineages built the other way; its first instruction is to change nothing that exists.

## v3.0.0 (2026-08-11)

**MAJOR: ceremony step 2 reorders.** Scope now precedes goals and objectives rather than following
them. Ruled after test-driving both orders as validatable constructions: the suite cannot distinguish
them — both validate identically, and drift fires in both — so this is not an enforcement change but a
change to what a human, or a generative model, is asked to write against. Recorded as MAJOR because
every lineage already built follows the old order, and re-deriving a scope from its objectives after
the fact would produce exactly the self-confirming boundary this reversal exists to prevent. Existing
lineages are NOT rewritten; they record a real past order.

## v2.1.0 (2026-08-11)

Two owner rulings recorded. **G9**: a constant iteration length with stories split to fit, rather
than an iteration sized to its longest story — the second was proposed, examined, and rejected
because it makes velocity unfalsifiable. **G10**: publish per increment, with the corollary that a
gate too slow to finish is a release blocker; both were learned by this package failing at them in
the same session.

## v2.0.0 (2026-08-10)

Authorship moved to the owning session. Ceremony step 4 added (deployment decided before the first
story). G7 and G8 added, both unreachable by shape. Deployment verification and release-time coverage
added to the standing rules. G1's note corrected: `LineageDepthAdvisoryShape` is not level-gated, so
"we ran at L2" does not explain a silence — the shapes file was not run.

## v1.0.0 (2026-08-09)

Authored by a parallel session. Ceremony, six boundaries, and the self-checking mechanism, all
carried forward.

---

## G19 — A floor is measured, not argued

An objective that stops short of its target is either unfinished work or a real
limit, and the two look identical from the inside. **Three times in one session an
objective was declared to have reached a structural floor, and every time the
floor was smaller than claimed. Twice it vanished entirely.**

- **Packages before delivery.** Believed impossible; `Package` existed unused for
  91 releases. The concept was there the whole time.
- **Reachability in the ontology.** Argued twice as a query a register cannot
  hold. Tested: SPARQL returns 25 classes, a SHACL shape returns the same 25.
  The rule was never about classes that do not exist — it was about classes that
  do and are unreachable, all of them already subjects in the shipped graphs.
- **Uncheckable standard rows.** Called 17 on the argument that a finding has no
  IRI. Read one by one: three were display forms of real terms.

Before an objective is accepted as floored, name the experiment. A floor with no
experiment is an argument, and this framework has produced three sound arguments
with wrong premises.

## G20 — A capability available and not obligatory is a capability skipped

`TaskType` shipped with fourteen values from ISO 12207 and 44 of 51 tasks chose
`Task_Implementation`. `TestCase` and `TestData` shipped at v1.97.0 and 46 of 55
stories never used them. `Package` sat unused for 91 releases. `CodeTable`
carried `hasTableKind` with nothing requiring it, while the whole table migration
turned on that distinction.

**Building a capability and adopting it are separate acts, and nothing notices the
gap between them.** Under time pressure the cheapest shape wins every time — and
development is always under time pressure.

Ship the constraint in the same increment as the capability, or record why not.

## G21 — Evidence batched across criteria carries the false one

A story was Done with a specification, ordered steps, a test case, test data, a
planned task, verified evidence and a complete harness. **The property it promised
did not exist.**

It passed because one `TestEvidence` attested five criteria across three stories
and described what the iteration did as a whole. Every clause was satisfied; none
asked whether the thing existed. **24 of 49 evidence records attested more than
one criterion.**

Evidence records that testing HAPPENED. A criterion must separately name the
artefact whose existence makes it true, per criterion — because a criterion
covered by a claim about its neighbours is not covered.

## G22 — A clause nothing fires has never been shown to work

96 of 276 level-gated clauses had never been made to fire by any fixture, and all
six clauses one lineage built were among them.

A clause may be correct, or it may be malformed SPARQL returning nothing. **Both
look identical from a green gate.** This package produced two — a triple pattern
inside `FILTER` reporting zero violations *and* zero warnings, and a `dateTime`
subtraction reporting zero on a 34-day gap — and both were caught by accident.

Write the negative fixture in the same increment as the clause. A negative fixture
that passes is either a missing clause or a broken one, and only looking tells you
which — one such case, written knowing it might be silent, exposed a missing
constraint.

## G23 — Verifying closed work is not backfilling it

Backfilling tasks onto closed stories records work that was never planned, which
is a defect. **Verifying that closed stories built the right thing is not the same
act**, and refusing the second because the first is wrong leaves the register
asserting completeness it has never checked.

Closed does not mean verified. It means nobody looked again.

## G24 — A derived number must answer to what it derives from

`hasCommittedEffort` was compared against `hasCapacity` and **both were asserted**.
An iteration held 15 points while declaring 9 and every check passed.
`iterationStart` and `iterationEnd` were asserted dateTimes compared to nothing —
two closed iterations took 32 and 28 minutes against a declared fourteen days, an
overstatement of 667 times, with the calendar sitting five months in the future.

A number that agrees with another number proves nothing. Derive it from the
contents, or state that it is a judgement.

---

## Architectural mitigations for the next lineage

These are not fixes to apply now; they are shape changes worth scoping.

**A1 — Capability adoption as a first-class link.** G20 recurs because a class and
its enforcing constraint are separate objects with no relation between them. A
`requiresConstraint` on a shipped term, checked at release, would make an
unadopted capability visible rather than silent.

**A2 — Fixture obligation per clause.** G22 recurs because a clause and its proof
are separate files. Naming the fixture on the shape itself would make an unproven
clause a structural fact rather than a report from a separate tool.

**A3 — Derivation provenance on every measure.** G24 recurs because nothing marks
a number as derived or asserted. `MeasurementKind` does this for objectives and
nothing else; extending it to every numeric property would let a single query find
every figure that answers to nothing.

**A4 — Self-application as a gate, not a habit.** Several findings came from
running a checker against the package that ships it — the audit that caught its
own author, the exclusion list with two caches and one entry. Making
self-application a required step would catch these on purpose rather than by
noticing.

---

## G26 — Test a mission draft's structural cardinality before its wording

A two-part Mission draft was rejected on a mechanical ground, not a stylistic one:
`lineageForMission` is `owl:FunctionalProperty` — two missions would need two lineages. The fix
was not softer wording; it was restructuring into one mission with an internal development
sequence, found by checking the property's own cardinality before touching the text again.

**Verified against a real, external adoption of this framework** (another registrant, commit history:
`missionSource` on the corrected mission literally quotes the owner naming this exact
constraint as the reason for rejection).

Before formalizing or amending a Mission, check the target property's cardinality for hidden
structural constraints before revising the prose.

## G27 — A legacy source's silence is not a current boundary

A Mission draft leaned on a foundational document as a scope *authority* — "the thesis didn't
cover this, so neither should we." Corrected on the ground that a foundational document is a
theoretical base, not a boundary on current work: silence in an old source is not evidence of
exclusion.

Any clause whose justification rests on what an old source *doesn't* say, rather than on the
current owner's stated intent, is ungrounded and should be re-tested against the mission
directly.

## G28 — Scope is derived by testing the Mission against an external taxonomy's own structure, not brainstormed from the Mission's prose

Where a Mission's domain has a real external body of theory behind it, Scope areas are found by
building a reference table from that theory's own structure, then testing the Mission's concepts
against every cell of it — not by paraphrasing the Mission text into areas. A domain-blind
fit-gap misses exactly the sub-concepts the Mission's own author didn't happen to phrase
explicitly, and produces defensible non-goals with reasons tied to the external source rather
than house preference.

## G29 — Goal generation is complete by construction once GoalFacing is treated as a closure test

One mission-facing Goal per mission clause (checked: does the clause appear as a literal
substring in a Goal's citation). Exactly one scope-facing Goal covering every Area. Exactly one
containment-facing Goal covering every Area. One exclusion-facing Goal per Exclusion.

**Verified against a real external adoption**: 2 Exclusions produced exactly 2 exclusion-facing
Goals, exactly one scope-facing and one containment-facing Goal existed, and mission-facing
Goals matched the mission's own clause count. Under-generation (an Area with no Goal) and
over-generation (a Goal citing nothing real) are both mechanically detectable this way, and a
bidirectional coverage check closes the stage.

## G30 — A metric family is chosen by testing it against a real case, not by category default

Before assigning a measurement dimension to a Goal, ask which of the available standards-grounded
dimensions (quality, testing, risk, efficiency, performance, project management) actually answers
that Goal's own failure mode — then walk a real case from the project through that one dimension
before trusting it with a target.

**Verified against a real external adoption**: two FMEA objectives were walked through with real
Severity/Occurrence/Detection scores before adoption (7×8×8=448→7×3×2=42, a 91% reduction;
8×9×9=648→8×3×2=48, a 93% reduction) — both arithmetically exact, not asserted. A dimension
chosen by category default (whatever module happens to be handy) is indistinguishable, at
adoption time, from one chosen because it answers the real question; only the test-drive tells
them apart. This generalizes G11 (test-drive before trusting a gate) to metric *selection*, not
only gate verification.

## G31 — "When to measure" is a condition, not a fabricated date, unless the timing is genuinely calendar-bound

A calendar deadline invented for a technical objective whose real timing depends on unpredictable
engineering work is decoration, not information — it adds false precision. Where the honest "when"
is a condition on another artifact's state (an Objective is measurable once a specific WorkItem is
Done), that condition should be recorded directly rather than approximated with a date. Some
objectives genuinely are calendar-bound (a regulatory date, an external commitment); both forms
are real, and the choice between them is itself something to verify, not default.

## G32 — An exclusion's rationale must cite the mission or a checked current fact, not a legacy or unverified authority

Before trusting an Exclusion, check whether its `hasExclusionRationale` cites (a) the lineage's
own current Mission text, or (b) a checked, current fact about the project — versus (c) an
external, legacy, or unverified authority. (c) should prompt re-examination before the exclusion
is trusted: verified against a real case where an exclusion's stated authority ("another registrant's own scope
note restricts it to software") was checked against the actual bytes and found false — the real
note was about something unrelated.

## G33 — State is grounded in re-checked evidence, never in whether a ceremony happened

A `WorkItem`'s state was moved twice on the wrong basis, in opposite directions: first marked
`Done` because a `PlanningEvent`/`ExecutionTask` had been freshly created to frame the claim,
without the owner ever authorizing the kick-off those records implied; then, once corrected,
reverted a second time reasoning "no kick-off was authorized" — still a process test, just now
answering no instead of yes. Both were wrong for the same reason: state was tied to whether a
procedural artifact existed, not to whether the deliverable objectively satisfies its DoD.

**Verified against a real external adoption**: the owner's own correction was explicit and general
— *"State changes should be based on reality... not my or anybody else's free will."* — applied
first to a scoring dispute, then again, independently, to this exact state-reversion. A state
change grounded in "was a ceremony performed" is checking the wrong thing regardless of which
answer the ceremony gives; check the evidence directly, every time, in both directions.

## G34 — A "what's next" claim queries the full scored set, never a pairwise or small-group comparison

Two items were compared against each other in isolation, and the winner treated as the answer,
without checking the other twelve-plus already-scored items in the same backlog. A later, real
full-backlog review found a third, previously-uncompared item scored far higher than either.

**Verified against a real external adoption**: the pairwise comparison used real WSJF scores
(2.29 vs 4.80) and was not itself wrong about those two items — the error was in never asking
whether a wider comparison existed. Any prioritization claim answering "what's next" must query
every currently-scored item in the relevant set; a comparison scoped smaller than the real
candidate set can be locally correct and globally wrong at the same time.

## G35 — Attributed rationale must be traceable to an actual statement, never extrapolated and then presented as specific

A ranking's own `hasDecisionRationale` claimed a specific instruction — "by the owner's own direct
instruction" — that the owner never gave. A real, general instruction ("continue with the first
package") had been extrapolated into a specific claim and then recorded as if directly stated.

**Verified against a real external adoption**: the owner's own correction was direct — *"I don't
rank anything... Why do you say such a thing?"* Before writing `hasDecisionRationale` (or any
prose framed as the owner's own words) as attributed to a person, check it names something that
person actually said, at that level of specificity — a general instruction supports a general
rationale, not a specific one built on top of it.

## G36 — A Deliverable joins an existing Goal only if that Deliverable alone would satisfy the Goal's own stated purpose

A second, genuinely different activity was bundled under an existing Goal rather than given its
own — the existing Goal named one kind of work (code-to-ontology conversion), and the new
deliverable was a different kind (ontology-to-ontology reconciliation), found and corrected only
after direct challenge.

**Verified against a real external adoption**: the two activities were real and distinct enough
that separating them was uncontroversial once named — the failure was in not asking the question
before bundling, not in a genuinely hard borderline case. Before adding a Deliverable to an
existing Goal, check whether completing that Deliverable alone would satisfy the Goal's own
stated name and purpose; if not, it needs its own Goal.

## G37 — A changelog entry is a mechanical, checked step, not a habit remembered by discipline alone

At least three separate releases in one lineage shipped without their own changelog entry,
caught and backfilled one or more releases later in each case — the same rigor already applied
mechanically to manifest regeneration was not applied with the same consistency to the
changelog, because nothing checked for its absence at commit time.

**Verified against a real external adoption**: three distinct instances across one lineage's own
history (`v1.47.0`; `v1.49.1`; the `v1.52.0`/`v1.52.1`/`v1.53.0` sequence) — not a single lapse,
a pattern. A step that depends on being remembered, with nothing else checking for it, will be
skipped at the same rate discipline alone is skipped everywhere else; where a mechanical check is
possible (does this version's own changelog section exist), prefer it over relying on the habit.

## G38 — A conformance-level claim requires its own real infrastructure underneath it, not just that the destination sounds right

A session was about to propose a new control for a gap that, checked directly, already existed
and already worked — it had simply never fired, because the adopting lineage's own declared
conformance level gated it out three levels below where the control lived. The deeper version of
the same mistake was avoided only by checking further: adopting the higher level to receive the
control would itself have required real, unbuilt infrastructure (cross-cutting invariant checks,
audit timestamps) the lineage did not yet have — declaring the level without that work would
repeat, at the conformance-level layer, the exact "claim true because it sounds right" error this
correction was already about.

**Verified against a real external adoption, test-driven not assumed**: conformance was
temporarily raised to the target level and validation re-run (reverted immediately after,
investigation only, never committed) — 154 real violations and 61 warnings surfaced, including
the exact control the session had almost proposed as missing, firing correctly on every item it
should have. Before recommending a lineage adopt a higher conformance level, check what facets
and infrastructure that level actually requires and whether the real work behind them already
exists — a level is not a label to declare toward, it is a set of real checks that must already
be survivable.

## G39 — Check the handover inbox at session start, and prefer the cheaper mechanism over the more complete one

A proposal to track incoming lineage-consumer handovers was first drafted as reified TBox/SHACL
provenance (a new class, a shape, a fixture, a registry of every consumer lineage's repository) —
built to the same standard as everything else in this package, but for a problem that turned out
to be simpler than that: whether a file has been read yet is bookkeeping, not domain knowledge
worth a shape proving it. Challenged on the comparison, not the design in isolation, a
cost/benefit/risk analysis of the alternatives found a plain folder plus a plain-text log
inside this package's own already-cloned repository did the same job at a fraction of the cost,
with no per-consumer registry to maintain and no extra clone per session.

**Standing rule**: `07-handover-inbox/pending/` is checked at the start of any session working on
this package — free, since the whole repository is already cloned for the freshness ceremony
regardless. An item found there is reviewed and moved to `accepted/`, `rejected/`, or `deferred/`
(a real third category, not folded into `rejected`: several real items were genuinely offered and
left open, not declined), with one line added to `07-handover-inbox/HANDOVER_LOG.md`.

**The general lesson, not just this specific mechanism**: when a proposal's own first draft
reaches for a fuller, more general-purpose structure by default, check what the problem actually
needs before building it — the same discipline `G30` already names for metrics and shapes, here
applied to a proposal about this package's own governance tooling.

## G40 — Conformance-level gating is retired for current and new lineages; a done lineage's own history is left alone

A real, scoped bug (`L3_Governed`'s own facet requirements silently never applying to
`L4_LineageEnforced`, because two shapes checked for an exact level match instead of "at or
above") was traced to its true cause during a direct cost comparison of L2 versus L3 versus L4.
Challenged on whether the tiering itself, not just this one asymmetry, was worth its own cost:
most of this package's own real, valuable corrections were already ungated, firing at every level
regardless — the tiering machine was protecting a minority of its own shapes while adding a
surface area a bug like this one could recur on indefinitely.

**The scale was found before anything was removed, not discovered by removing and finding the
damage.** A search for every place `hasConformanceLevel` participated in shape logic found over
90 distinct SPARQL blocks, not the ~24 the `L4`-labelled shapes alone suggested — level-gating was
load-bearing through most of this framework's real constraint set, not a contained subsystem.
Given that real scale, the removal was executed as an explicit multi-pass plan rather than a
single sweeping edit, each pass verified before the next began.

**What changed.** Level-gating logic removed from every content-checking shape; five shapes whose
entire subject was the level mechanism itself — not a shape that happened to be gated, but a
shape *about* declaring, targeting, downgrading, or reviewing a level — retired outright, each
with its historical incident comment preserved unedited rather than deleted. `AdoptionProfileShape`
no longer requires declaring a level; all four facets are now unconditionally required, which also
resolves the original asymmetry as a side effect. `hasConformanceLevel` and its five companion
properties are kept, not deleted, and their own TBox definitions now say plainly that they are
historical and no longer read by any shape — a done lineage's own asserted level is left exactly
as it was recorded, honestly labelled rather than silently orphaned.

**What the repair pass found, disclosed rather than smoothed over.** Making every constraint
unconditional broke 13 previously-clean positive fixtures, each built to be minimally complete for
whatever level it once declared. Of those, only the ones load-bearing for a shape's own proof or
for Gate R's self-proof triad were repaired this pass — `fixture_positive_v1_7_0` rebuilt to
genuine, unconditional completeness, verified clean. The remaining fixtures, and a handful of
tooling scripts that still reference conformance levels for reporting rather than enforcement, are
real, tracked, disclosed follow-up — not treated as done because the highest-priority pieces were.
Two further, genuinely unrelated bugs surfaced only because this repair forced a re-check nothing
had needed before: a case-sensitivity mismatch in a `fixtureCaseName` declaration, and a
fabricated file-path artefact citation — both real, both fixed, neither caused by the level
removal itself.

**The standing rule going forward**: no new or currently-active lineage declares a conformance
level; every constraint this framework ships is unconditional for all of them. A lineage whose own
register already carries historical `hasConformanceLevel` data from before this change keeps that
data unedited — retired as a mechanism, not rewritten as history.

## G41 — A closed lineage is exempt from further advisory processing; an active one earns full conformance, nothing less

Asked to separate lineage-specific gaps from methodology gaps: the great majority of this
package's own real advisory warnings are lineage-specific, not methodology defects — real facts
about real backlog items in `L_OntologyDriven`, this package's own still-active lineage, that stay
fully enforced. Only three shapes concerned a `Mission` whose entire lineage was already marked
`lineageArchived true`: `SessionDraftedMissionAdvisoryShape`, `MissionReachShape`, and
`UnfinishedLineageShape`. Fixed by making each check the flag `Lineage` already carried, not by
building a new mechanism — `Lineage`, `belongsToLineage`, and `lineageArchived` already existed,
six of seven lineages were already marked archived, and the framework's own comment already named
the gap: they "sat validated on every run" without any shape respecting the flag.

**The standing rule**: a mission-level advisory checks whether its own `belongsToLineage` points at
a `Lineage` with `lineageArchived true`, and stays silent if so — the same disclosure the lineage
already carries, not a second, duplicated notice. This exemption is scoped to advisories that
concern the *quality of how a mission was built*, not to structural or data-integrity requirements,
which continue to apply to every individual regardless of lineage status. An active lineage's own
gaps are never exempted this way, however old the individual item inside it — `Ev_It7` and
`EP_CodeTables` belong to `L_OntologyDriven`, not an archived lineage, and their own warnings stay
exactly as strict as everything else the still-open lineage is held to.

## G42 — Every adopting lineage carries a real, enforced goal for its own conformance, built at kickoff

Adopted from another registrant's own real fix to itself (`07-handover-inbox/accepted`), enforced rather than
merely documented per the owner's own explicit direction: `AdoptionConformanceGoalShape` requires
every `AdoptionProfile` to carry a `Goal` (`isConformanceGoal true`, `Facing_Mission`) with a real
`Objective` — success metric, checkpoint, and at least one actual measurement, the full goal ->
objective -> metric -> time-to-measure chain this framework already requires of every product
claim, applied reflexively to the register's own trustworthiness. `WI_L4ConformanceGapClosure` had
nowhere honest to attach in another registrant's own register precisely because no product `Objective` was
honestly about this; forcing it onto one would have been the dishonest fit this framework's own
checks exist to catch elsewhere.

**Built at lineage kickoff, not reactively.** another registrant's own revision of the handover, following a
direct request to specify exactly which measure belongs at which event, makes the case precisely:
a lineage that waits until conformance work is needed to build this goal has already lost the
ability to attach that work anywhere honest. BRSF's own register now carries its own real instance
— `Dir_Hold`, not `Dir_Increase`, since the honest objective is proving a count that has never
moved continues not to, not closing a gap that was never real.

**The companion finding — `observedDuringCeremony`, advisory-only** — is deliberately not a
violation and never will be by the same reasoning `G7` already gives: whether a reading was taken
at the honestly right moment is a judgement no git-commit-ordered chain can verify the way stage
order can, so the property lets a disciplined lineage say so structurally rather than accusing an
undisciplined one of dishonesty it cannot actually detect. The full measure-to-ceremony timing
table this same handover proposes is documentation (Standard 2.5c-xxxvi), not SHACL, for the
identical reason — a temporal check nobody can fixture honestly is worse than no check.

## G43 — Three severities, researched against external standards before finalizing, not four

Asked to discipline violation versus warning versus opportunity, and whether a fourth category
exists, checked against real external standards rather than decided from this framework's own
prior habit. SHACL 1.2 Core itself defines exactly `sh:Violation`, `sh:Warning`, `sh:Info` — the
last explicitly documented as not signalling a problem. Independently, ISO 9001/13485/14001/45001
audit practice converges on the identical three-way split: Nonconformity (a requirement breached),
Observation (a risk, not yet a breach, addressed as best practice not obligation), Opportunity for
Improvement (a suggestion, no response required). No standard checked names a fourth severity
tier; ISO's own Major/Minor is a subdivision of Nonconformity's consequence, not a fourth kind of
finding — and this framework has just removed the one graded-severity mechanism it had
(`hasConformanceLevel`, `G40`); grading inside `sh:Violation` itself would reintroduce that in
miniature.

**The standing definition** (Standard 2.5c-xxxvii): `sh:Violation` — a stated rule is broken.
`sh:Warning` — no rule is broken, but a real risk exists that one will be, or that a claim the
register makes is weaker than it looks. `sh:Info` — nothing is wrong or at risk; a genuine
opportunity to be more complete, precise, or useful than required.

**The one shape this taxonomy was first applied to failed it, and was retired rather than
relabelled.** `UnscoredItemAdvisoryShape`, this framework's only `sh:Info` shape before this
ruling, shared its exact condition with `SilentGapShape`'s own real `sh:Violation` — something was
already wrong there, and a real rule already said so; calling it an opportunity would have been
the dishonest fit this same ruling exists to prevent. Retired per `G40`'s own precedent, historical
comment kept. `sh:Info` now governs zero shapes, an honest starting point for the audit, not a gap
papered over.

**Not retroactively re-graded across the whole suite in this pass.** The 66 `sh:Warning` shapes
were written before this three-tier definition existed and have not been individually checked
against it; this ruling sets the standard future audit work checks against, not a claim the audit
already happened. A `Violation` newly added under this same session — `AdoptionConformanceGoalShape`
— is confirmed correctly graded by this same standard: a lineage lacking the enforced conformance
goal has broken a stated rule, not merely risked breaking one.

