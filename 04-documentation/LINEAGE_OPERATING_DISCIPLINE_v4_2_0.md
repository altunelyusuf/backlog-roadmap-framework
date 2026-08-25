# Lineage Operating Discipline — v4.2.0

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
2. **Fix the mission, then the SCOPE, and only then goals and objectives.**
   `Mission` → `ScopeStatement` **with its exclusions** → `Goal` → `Objective` (metric, baseline,
   target, direction, deadline). Validate this chain empty, before a single work item exists. A chain
   that does not validate empty will not validate full.

   **Scope precedes goals; it does not summarise them.** Written last, a scope is drawn around
   objectives already fixed, so every objective is in scope *by construction* and the boundary can
   never refuse anything — it records a decision instead of constraining one. Written second, the
   boundary exists before the work that would test it, and a new objective must be argued against it.

   The measured evidence is in this package's own register: **five objectives declared, five
   admitted, none ever refused**, with the scope amended twice afterwards to catch up. That is what a
   boundary drawn after the fact does — it always fits.

   **This matters more, not less, for a generative model.** An LLM produces plausible continuations
   of what it has already written. Asked to write a scope *after* its own goals, it summarises itself,
   and a self-summary cannot contradict its source: the step reads like a check and is structurally
   incapable of failing. Asked to write goals *against* a scope fixed earlier, each generated goal
   meets a constraint the generator did not author in the same breath, and a goal outside the
   boundary becomes visible as a conflict rather than absorbed as context. The order is what turns
   scope from something the model narrates into something it is measured against.
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
second. *Enforced by* `L4MeasuredObjectiveShape`: every objective carries a `MetricObservation`,
whatever the reading said.

### G5 — Why, when, and what are three questions
`Epic` answers **why**, `Iteration` answers **when**, `DeploymentUnit` answers **what users
received**. Conflating them is the commonest drift observed here: an epic in a sprint looks like
planning and commits nothing anyone can finish; an epic in a release names something that cannot
ship. *Enforced by* `L4GroomingShape`.

### G6 — Drift is the default, not the exception
**Corollary from v3.0.0:** drift is *detected* identically whichever order the chain was built in —
`L4DriftShape` fires on an item pursuing an unrealised objective either way, verified by construction
on both. What the order changes is **when a human notices**: scope-first surfaces the conflict while
the objective is being written, scope-last surfaces it only once work exists to be rejected.
Work migrates outside the declared boundary unless something objects. *Enforced by* `L4DriftShape`:
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
  release. *Enforced by* `L4DeploymentVerifiedShape`.

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
