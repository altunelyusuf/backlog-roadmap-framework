# Changelog

## v1.66.0 — 2026-08-11 (MINOR: initiative kind and the ISO 14764 maintenance grid)

Taken from the literature, verified rather than recalled: **ISO/IEC/IEEE 12207** for the
development/maintenance split, **ISO/IEC/IEEE 14764:2022** for the maintenance classification, back to
**Lientz & Swanson (1980)** for the original three categories the standard formalised.

**The standard's structure is a 2×2, not a list** — and that is the hierarchy the owner was reaching
for. Maintenance is classified by the **timing** of the change (reactive or proactive) and its **goal**
(correction or enhancement); the four familiar names are the cells. Corrective is reactive correction,
preventive is proactive correction, adaptive is reactive enhancement, perfective is proactive
enhancement. `Maint_Additive` is 14764:2022's optional fifth.

**The framework records the axes and treats the category as derived**, and checks that the two agree.
A reader can disagree with *"this was proactive"* on evidence; they cannot usefully disagree with
*"this was perfective"*. And 14764 is explicit that an enhancement is **not** a correction — calling
one a fix is how unbudgeted scope enters a maintenance stream.

`ModificationRequest` and `ProblemReport` are the standard's own terms. At L3 reactive maintenance must
name one, because reactive work answers something that arrived and its scope has no other source.

### Test drive: all eleven epics classified

**Eight are Development**, one is **Corrective**, one **Adaptive**, one **Preventive**:

- **BRF-EP8** *(story fits one iteration)* — **Corrective**. The owner reported stories spanning
  iterations in applied lineages: something had already happened, and the goal was restoring intended
  behaviour.
- **BRF-EP10** *(chain records its order)* — **Adaptive**. A new requirement arrived from outside; the
  environment moved rather than something breaking.
- **BRF-EP11** *(artifacts teaching the retired order)* — **Preventive**, not corrective. Nothing has
  failed; the defect is latent and will mislead the next reader. Proactive correction.

The EP10/EP11 pair is the case the grid earns its keep on: both are order-repair work, and a flat list
would have collected them under one label. The axes separate them, because one answers an arriving
request and the other anticipates a reader who has not yet been misled.

### A defect the new check caught immediately

`EP_OrderCorrect` carried `Cat_Rework` — **an investment category the vocabulary never declared**. It
had survived several releases because `owl:oneOf` closes an enumeration for a reasoner but is **not a
SHACL check**, so an invented IRI passes silently. Corrected to `Cat_TechnicalDebt`, and
`DeclaredCategoryShape` now rejects the class of error.


## v1.65.0 — 2026-08-11 (MINOR: the adaptation completes — boundary rewritten, lineage re-linked)

**The ruling did not need a decision.** This session asked the owner to confirm whether the views and
schedule work was in scope. It was already recorded: `SC_Schedule`, owner-decided, 2026-08-09,
admitting `EP_Views` and `EP_Schedule` by name. **The answer was on disk and the question was a
lapse** — L-78 exists for exactly this, and the correction was to read the register rather than ask
again.

So the gap was never a question about intent. It was **a scope statement that failed to record a
decision already taken**, and the two disagreed for eleven releases because a boundary written after
the work is never asked to refuse anything.

**Outcome: `Adapt_BoundaryRewritten`.** `fw:Scope_v2` says what the boundary always meant; `fw:Scope`
is **not edited** — it records what the boundary said at the time, which is the evidence the
adaptation rested on. `SC_ScopeCorrection` records the correction and states plainly that it is not a
widening. Seven objectives now point at their governing boundary with `fillsScope`.

**A finding was withdrawn, visibly.** The second fit-gap finding — `EP_OrderRecord` and
`EP_OrderCorrect` — was an **instrument error, not a gap**: those epics are governed by
`Scope_Order`, and the drift check compared every item against one scope instead of the scope that
governs it. The withdrawal is left in the register as a comment rather than deleted, because
`Adapt_BoundaryHolds` is refused while any finding stands, so a finding that turns out to be wrong
must be retracted where a reader can see it.

**The check is fixed**, not just the record: the drift clause now compares an item against **every**
declared boundary. A register may hold several scopes, one per mission, and the old form reported
work that was exactly where it belonged.

**`MixedOrderShape` fired during the re-link**, on `Scope_Order` — which briefly carried both link
directions while the new ones were added. Precisely the case it was written for, catching its author
mid-conversion.

**Re-measured: 0 work items outside every boundary.** Scope_v2 covers 5 objectives, Scope_Order
covers 2, and the retired Scope keeps its 4 as history.


## v1.64.0 — 2026-08-11 (MINOR: the adaptation becomes a gated procedure, and this register runs it)

The adaptation was a document someone follows carefully. It is now a `LineageAdaptation` with four
ordered stages — **Assess, Fit-gap, Ruling, Re-link** — each gated by an `AdaptationGate` carrying an
executable check, an expected result and an observed one. Built mostly from reuse:
`CrossCuttingInvariant` already had check-plus-expectation, and `ScopeChange`, `hasRationale` and
`decidedBy` already existed.

**Two design points worth stating.**

The fit-gap gate **passes on having measured, not on the boundary being intact.** A gate that only
passed when it found nothing would be an instrument reporting its own preferred answer.

`Adapt_BoundaryHolds` is **rejected if any finding exists.** It is the outcome an inspection reaches
by default — a boundary drawn around past work fits that work by construction — so it must rest on a
recorded fit-gap rather than on looking.

**This register ran the procedure on itself, and the boundary did not hold.**

```
Assess  : fillsScope 0, scopeRealizesObjective 6  -> scope-last, one direction, PASS
Fit-gap : scope covers 4 objectives; 4 work items pursue objectives it does not  -> PASS
Ruling  : OPEN — awaiting the owner
```

The findings are real and one is a genuine defect: `EP_Views` and `EP_Schedule` pursue `Obj_Views`,
which `SC_Schedule` admitted but which was **never added to what the scope says it realises**. The
change record and the boundary disagreed for eleven releases, and nothing noticed — because the
boundary was never asked to refuse anything.

**Stage 4 is deliberately not reached.** The stage-order shape refuses `Stage_Relink` without a
recorded outcome, so the framework's own constraint is holding this session at the ruling gate rather
than letting it re-link on its own judgement.

**The gate shape caught its author immediately:** the fit-gap gate was written with expectation
*"enumerated, whatever the count"* against observation *"4 items outside the boundary"* — marked
passed while the two texts disagreed. Rejected, and rewritten so the comparison is meaningful.

`fixture_adaptation_negative_v1_0_0.ttl` defeats every gate — a straight jump to Re-link, a
boundary-holds claim contradicted by a finding, a rewrite naming no new scope and no `ScopeChange`,
and a passed gate whose observation contradicts its expectation. All five clauses fire.


## v1.63.0 — 2026-08-11 (MINOR: the order was always recordable — by link direction)

**An owner correction to this session's own analysis.** v1.62.0 reported that the ceremony order was
unrecordable because no element of the intent chain carries a date. That was wrong, and the answer was
already in the vocabulary.

**Every link in the chain points from the later-written element to the earlier one.** A `Goal` points
at its `Mission`. An `Objective` points at its `Goal`. Direction *is* order — no date required. And
`scopeRealizesObjective` points a `ScopeStatement` at its `Objective`, which encodes
scope-written-last: the retired order, baked into the vocabulary itself.

**`fillsScope` is the missing reverse:** an `Objective` names the boundary it fills, and cannot name
one that does not yet exist. Asserting it is only possible where the scope came first.

**Deliberately not `owl:inverseOf`.** Declaring the two properties inverse would let a reasoner
materialise either from the other, and every lineage would then appear to be built both ways at once —
erasing exactly the signal the direction carries.

**Three shapes.** At L4 an objective must name the scope it fills. At every level, a scope and an
objective pointing at *each other* is rejected: that records no order at all, which is worse than
recording the old one honestly — and it is what a re-pointing done in place looks like. An advisory
reports a scope-last lineage without treating it as a defect.

**Two existing clauses had assumed the old direction** and would have failed a scope-first lineage:
the L2 "scope realises no objective" check and the L4 drift check. Both now accept either link.

**`Scope_First_Adaptation_Procedure_v2_0_0.md`** ships for lineages already built scope-last. Its
first instruction is to **change nothing that exists**: re-pointing the links would derive a boundary
from objectives that already exist, producing the self-confirming scope this change prevents while
labelling it as the fix. Adaptation happens at the next increment — let the old scope close, write the
next boundary before its goals, and link forward with `fillsScope`. Two scopes recording two different
orders in one register is history, not inconsistency.

**BRF-EP10 was re-specified before it was built.** Its acceptance criterion had assumed dates; the
owner's correction gated the change, and the interaction is recorded on the epic.


## v1.62.0 — 2026-08-11 (MINOR: impact of the scope-first ruling, measured; fifth mission registered)

**Four impacts measured before anything was proposed.**

1. **Nothing enforces the order, and nothing can.** Two shape clauses reference
   `scopeRealizesObjective`; both check that the link *exists*, neither could check when either end
   was written.
2. **The order is unrecordable.** Every property domained on `Mission`, `Goal`, `Objective` and
   `ScopeStatement` was enumerated — 2, 1, 7 and 5 respectively — and **none carries a date.** The
   ceremony order therefore lives only in prose, and no reader can tell how a lineage was built
   without asking the session that wrote it.
3. **Two shipped artifacts still teach the retired order.** `backlog_lineage_completeness` lists its
   layers as Mission → Goal → Objective → ScopeStatement, presented to everyone who runs it; the
   standard's intent-chain section reads the same way. The changelog matches too but is a historical
   record and is excluded under L-112.
4. **The amendment pattern reproduced itself while registering this work.** Admitting it required a
   **third** `ScopeChange` against the original scope — which is exactly the symptom that motivated
   the reordering, occurring again in the act of fixing it.

**A fifth mission, and the first in this register built scope-first.** `Scope_Order` and its three
exclusions were written before any goal existed, so the goals had a boundary to be argued against.
The exclusions refuse three things worth naming: **no re-deriving old scopes** (it would manufacture
the self-confirming boundary v3.0.0 prevents), **no shape rejecting old-order lineages** (they are
weaker in one respect, not wrong, and such a rule gets bypassed), and **no mandated timestamps** (a
required date nobody can verify produces backfilled claims — optional and honest beats required and
fabricated).

**Two epics, computed not chosen:** BRF-EP10 *an intent element can record when it was fixed* (5.00),
BRF-EP11 *shipped artifacts stop teaching the retired order* (4.00).

**The suite caught the author twice while registering.** A WSJF value of 4.5 where (6+4+5)/3 = 5.0 —
arithmetic asserted rather than computed. And `Scope_Order` realising no objective, which in a
scope-first order is the honest transient state: the scope text and exclusions are fixed first, and
the link to objectives is asserted last, once they exist.


## v1.61.0 — 2026-08-11 (MINOR: scope precedes goals — Lineage Operating Discipline v3.0.0)

The owner reported scope problems in applied lineages and proposed reordering the ceremony: fix the
mission, then the **scope**, and produce goals and objectives to fill it. **Both orders were
test-driven as validatable constructions before ruling.**

**The suite cannot tell them apart.** Order A (Mission→Goal→Objective→Scope) and order B
(Mission→Scope→Goal→Objective) validate identically — 3 violations each, the same three. Inject an
objective the scope does not realise and `L4DriftShape` fires in **both**. So this is not an
enforcement gap and cannot be closed by a shape.

**What the order changes is whether the boundary can ever refuse anything.** Written last, a scope is
drawn around objectives already fixed: every objective is in scope *by construction*, and the step
reads like a check while being structurally incapable of failing. Written second, the boundary exists
before the work that would test it.

**Measured on this package's own register rather than argued:** **five objectives declared, five
admitted, none ever refused**, with the scope amended twice afterwards by `ScopeChange` to catch up.
A boundary drawn after the fact always fits.

### Why this matters more for a generative model, not less

An LLM produces plausible continuations of what it has already written. Asked to write a scope
**after** its own goals, it summarises itself — and **a self-summary cannot contradict its source**.
Asked to write goals **against** a scope fixed earlier, each generated goal meets a constraint the
generator did not author in the same breath, and a goal outside the boundary surfaces as a conflict
instead of being absorbed as context.

Ordering is one of the few controls that survives a probabilistic generator, because it changes what
the model is conditioned on rather than asking it to be more careful.

**Recorded as MAJOR on the discipline (v2.1.0 → v3.0.0)**: every lineage already built follows the old
order, and re-deriving their scopes now would produce exactly the self-confirming boundary the
reversal exists to prevent. **Existing lineages are not rewritten** — they record a real past order.

`fixture_scope_first_v1_0_0.ttl` ships the new order as a reference chain, validating at 0.


## v1.60.0 — 2026-08-11 (MINOR: BRF-EP9 — a deployment says how it chose, and the fourth mission closes)

The last epic of `Mission_Executable`, unblocked by EP8 exactly as the register predicted: selecting
the most valuable stories was meaningless while a story could span iterations, because what is
*available* at a release boundary was undefined until stories were made to fit.

**`SelectionBasis`**, closed at four — `Sel_HighestScored`, `Sel_Dependency`, `Sel_Committed`,
`Sel_Opportunistic` — plus `passedOver` and `hasSelectionRationale`. At L4 a `DeploymentUnit` must say
on what basis its contents were chosen.

**Deliberately NOT a rule that a release must always take the top score.** An ordering is a model and
is sometimes wrong; a rule with no exception path is bypassed the first time it is. What is enforced
is that the departure is **visible** — claim `Sel_HighestScored` while a higher-scored deliverable
item waits, and it must be named in `passedOver` with a reason. This is the same shape as the
ranking-fork resolution this subject already carried.

`Sel_Opportunistic` exists for the honest case: **a release that was not a prioritisation decision.**
Without it in the vocabulary, such a release would have to be recorded as though it had been.

An **advisory** fires where every deployment in a register was selected on some basis other than
score — *prioritisation recorded and not used*.

**Three clauses, all proven firing:** no stated basis; a Highest-scored claim contradicted by a Done
item scoring 99 that is neither carried nor named; a pass-over with no rationale.

**The mission's objective is met, measured rather than inferred.**
`Metric_UnfinishableCommitments`: baseline **3** → **0**, re-measured by re-running all three original
as-is probes against the current suite, not concluded from the work being Done.


## v1.59.0 — 2026-08-11 (MINOR: BRF-EP8 — a story is consumed whole within one iteration)

**G9 turned into a constraint.** The owner examined and rejected sizing the iteration to its longest
story: a box sized by what it contains always fits, so its velocity can never report a miss.

**No vocabulary was minted.** Splitting *is* decomposition — `decomposesInto` already reads *"a
feature into stories"*, and a story split into smaller stories is the same relation. The remedy each
message names is therefore expressible the moment the message is read.

**Two clauses at L4**, both proven firing on the negative fixture:

- a story planned into **more than one iteration** — *"either too large when it was committed or
  never finished and recommitted, and both read the same afterwards"*
- a story **still open after its iteration closed** — *"the iteration measured something it did not
  deliver, so its velocity overstates what the team can finish and the forecast inherits the error"*

Each message names **splitting** as the remedy and says explicitly not to widen the iteration.

An **advisory** fires earlier, where splitting is still cheap: a story whose estimate exceeds its
iteration's capacity cannot be completed within one by arithmetic, though it has not failed yet.

**The conformant fixture demonstrates the remedy rather than describing it** — a story too large for
one iteration, split into two that each fit, validating at 0.

**Adding the rule immediately failed the framework's own conformant fixture**, correctly: its
in-progress story had outlived the iteration it was planned into. Fixed by moving the story to the
open iteration, not by relaxing the rule.

**Re-measured, not assumed:** `Metric_UnfinishableCommitments` moves from its baseline of **3** to
**1**. Two of the three as-is gaps are closed; the remaining one is that a deployment still cannot say
how its contents were chosen, which is BRF-EP9.


## v1.58.0 — 2026-08-11 (MINOR: BRF-EP7 — structural views carry progress)

The register put EP7 first at 6.00 and its acceptance criterion, written before the build, was the
specification. **No vocabulary was minted**: `decomposesInto` and `hasState` already carry everything
progress needs, and a stored percentage could disagree with the states it summarises — the defect
L-91 names, one level down.

**Each node is now filled to its derived completion**, in the Mermaid graph and in a text table that
names the basis for every figure:

```
E-1   █████░░░░░   50%  (2/4 children)
S-1   ██████████  100%  (leaf, Done)
S-2   ??????????    ?   (started, no children to measure against)
S-3   ░░░░░░░░░░    0%  (leaf, Proposed)
S-4   ██████████  100%  (leaf, Cancelled)
```

**Three judgements worth stating, because a percentage-shaped answer gets each of them quietly
wrong:**

- **A started leaf reports `?`, not `0`.** It has nothing to measure against, and drawing it empty
  would claim no progress had been made when the register simply cannot say. The acceptance criterion
  named this case explicitly.
- **Cancelled counts as resolved, not as progress lost.** It is work that will not be done and does
  not remain outstanding; counting it incomplete leaves a parent permanently short of full through no
  remaining effort.
- **An unstarted node and a finished one must not render alike** — unknowns get a dashed border,
  complete nodes a heavy one, so the distinction survives even where a reader ignores the numbers.

`fixture_progress_v1_0_0.ttl` ships all five cases and validates at 0. Building it caught a real slip:
the cancelled story first used an invented `hasWithdrawalRationale`; the governed term is
`hasRationale`, and the suite rejected the invention rather than accepting a plausible name.

**Register 1.8.0 → 1.9.0**: EP7 Done with evidence attesting its criterion, and `Obs_ProgressDelivered`
moving `Metric_ProgressLegible` from its measured baseline of 0 to 1.


## v1.57.0 — 2026-08-11 (PATCH-class: Gate 0 passed on an empty set)

Prompted by an OEE advisory that `release_check` may report `0/0 OK` when it hard-codes an
unversioned manifest name. **This package ships no `release_check`, so the advisory did not apply as
written — and checking the same class in the gate it does ship found the defect twice.**

**Proven by construction, not inferred:**

```
manifest present      -> Gate 0 exit 0
manifest ABSENT       -> Gate 0 exit 0   <- passed on nothing
manifest VERSIONED    -> Gate 0 exit 0   <- passed on nothing
```

The second is the worse one. A package following **the pack's own recommended
`MANIFEST_SHA256_v1_2_3.txt` convention** would never have been checked at all: the hard-coded name
matched nothing and the gate printed success. *A gate that passes because it found nothing to check
is indistinguishable from one that checked everything and found it sound.*

A third of the same class was fixed while there: the line regex `continue`d on any non-matching line,
so a malformed manifest parsed to zero entries and still reported `0 OK`.

**Fixed** — Gate 0 resolves by highest-SemVer glob over `MANIFEST_SHA256*.txt`, prints **which**
manifest it used and **how many entries it parsed**, and aborts when either set is empty:

```
manifest  : MANIFEST_SHA256.txt
63 OK, 0 mismatched, 0 missing of 63 listed

absent -> ABORT: no MANIFEST_SHA256*.txt found ... Gate 0 FAILED
```

**Verified against the other two advisories rather than assumed.** Attribution: the publication gate
returns 0 for this package and `PUBLISH_RECORD.ttl` carries `authoringSession "brsf-maintainer"`. Its
first run reported `UNTAGGED` at v1.56.0 — a **local-clone artifact**, since `git fetch main` does not
bring tags; after `--tags` it returned `VERDICT: PUBLISHED`. Reported here because the wrong reading
would have looked like a missing release.

**Gate P is not affected**: it globs `01-ontologies/`, which is this package's actual layout. The
advisory notes it remains unfixed generally and is to be raised rather than worked around; this
package has nothing to raise, because it happens to match.


## v1.56.0 — 2026-08-11 (MINOR: two rulings, and a gate too slow to publish)

**Register v1.7.0 was this session's own**, not a parallel session's. Commit `e30fec0`,
"backlog-roadmap-framework v1.53.0", transcript sha `43461c3b`. The previous turn asserted it was
someone else's; the check was one `git log` and was not run. The file is a **renamed v1.6.0** —
`remediation markers: 0` — which is why a version bump targeting 1.6.0 later matched nothing.

Note what the record could and could not settle: that commit carries **no `Session:` trailer**, so
git identity was useless as always. Only the transcript SHA identified it, and only because it could
be matched to a publish this session made.

**Ruling G9 — a constant iteration, stories split to fit.** The alternative — assess iteration length
after story-writing and size it to the longest story — was examined and rejected: if the box is sized
by what it contains, you always fit, and **velocity becomes a tautology that can never tell you that
you did not**. It also fails one step later, when the next change produces a bigger story. Splitting
is what the vocabulary already implies: a `Story` is *"small enough to be completed within one
iteration"*, so splitting restores the term's meaning while resizing redefines it.

**Ruling G10 — publish each increment, do not batch.** Two increments accumulated unpublished and
cannot now be separated into the releases they should have been.

**Its corollary, learned the hard way in this release: a gate that cannot finish blocks every
release.** The publisher re-runs the package gate — correctly, so it never trusts the caller's claim
— and this package's gate had grown to **eleven full validator invocations at ~11s each**, exceeding
the publisher's runtime. Three publish attempts died mid-run, including one detached. A package that
passed its own gate **could not be published at all**.

`backlog_validate` **1.3.0 → 1.4.0** gains `--each`: validate several files independently inside one
process. Nothing is skipped and no fixture shares a graph with another; only the repeated interpreter
and load cost goes. The fixture-coverage gate now makes one call instead of eight.

**Whole gate: 242s, down from beyond the publisher's limit.**


## v1.55.0 — 2026-08-11 (MINOR: as-is measured, and a fourth mission registered before any work item)

**Snapshot:** `the maintainer/Ontologies` HEAD after fast-forward, 0 behind, re-checked. Discipline
`OE_Operating_Discipline_v2_3_0.md` sha `cf469352`; lineage discipline v2.0.0 sha `93026f28`;
governance `knowledge_base_abox_v2_21_0.ttl`. Session `brsf-maintainer`.

### As-is, each gap proven by construction rather than asserted

**1. The network view shows structure and no progress.** Its function body contains no reference to
`hasState`, `Done`, or any completion term — only `graph LR` and arrow edges. A started node and an
untouched one render identically. Everything needed to derive progress already exists
(`hasState`, `decomposesInto`, `decompositionState`); nothing consumes it.

**2. A story may span iterations.** Constructed one planned into two iterations by two planning
events: **22 violations at L4, none about the span.** `Story` is defined as *"small enough to be
completed within one iteration"* — and nothing enforces it. **This is G3 again**: a definition says
what the term means, and only a constraint says what may be asserted.

**3. A deployment cannot say how its contents were chosen.** `deploysItem` ranges on
`ProductBacklogItem` with no notion of selection: `spansIterations`, `fitsIteration`,
`selectedByScore`, `hasSelectionBasis` are all absent. A release grouped by theme and a release of the
highest-scoring available work are **indistinguishable in the record**.

### Lineage registered before the first work item, per ceremony step 2

`Mission_Executable` with two goals and two objectives whose baselines are the **measured** as-is —
0 progress-bearing views, 3 permitted-but-forbidden commitment classes — not estimates. Admitted by
`SC_Executable`, which reverses no existing exclusion: `Ex_Scale`, `Ex_Method`, `Ex_Modality` and
`Ex_Complexity` are untouched. Value-based release selection constrains **what a deployment may claim
about how its contents were chosen**, not how a team runs planning.

**The order is computed, not chosen:**

```
BRF-EP7  progress in structural views   6.00  startable
BRF-EP8  a story fits one iteration     4.00  startable
BRF-EP9  value-selected deployments     2.40  blocked on EP8
```

EP9 is blocked because selecting the most valuable stories is meaningless while a story can span
iterations — what is *available* at a release boundary is undefined until EP8 lands. The register
worked that out from the declared dependency; it was not sequenced by opinion.

**No implementation in this release.** The as-is is measured, the lineage is registered and validates
at 0 violations, and the three epics are `Proposed`.


## v1.54.0 — 2026-08-11 (MINOR: what is unlisted was never verified either)

**Snapshot:** `the maintainer/Ontologies` HEAD `3b62ca2`, 0 behind at time of work. Discipline
`OE_Operating_Discipline_v2_3_0.md` sha `cf469352`; governance `knowledge_base_abox_v2_21_0.ttl`;
lineage discipline v2.0.0 sha `93026f28`. Session `brsf-maintainer`.

**The open item, reproduced first:** this package's manifest self-check read **62 OK, 1 BAD** with
`PUBLISH_RECORD.ttl` mismatching, and `RELEASE_METRICS.txt` present on disk in no manifest line.

**Both are the self-reference class and both were deliberate — but only one was declared, and the
declaration lived in a docstring.** A docstring is not the artifact anyone verifies.

**`PUBLISH_RECORD.ttl` was listed and should not have been.** The publisher writes it *after* the
manifest, so listing it guarantees a mismatch: the hash describes a file that no longer exists in
that form by the time anyone checks. **A permanent, expected mismatch is worse than an exclusion,**
because a reader cannot distinguish it from a real one — which is precisely what happened for several
releases.

**Exemptions are now declared in the artifact.** `build_manifest` **1.3.0 → 1.4.0** emits an
`# EXEMPT <path> — <reason>` line for each of the three, so *"not listed"* and *"deliberately not
listed"* are different facts a reader can tell apart.

### The gap underneath, which is the real finding

**Gate 0 verifies that what is LISTED matches. Nothing verified that what is UNLISTED was meant to
be.** From Gate 0's side there is no difference between a file deliberately excluded and a file
forgotten, so a package could carry an uncovered file and still report a clean pass.

`backlog_manifest_coverage_v1_0_0.py` closes it: every file on disk is either hashed or exempted by
name; every exemption names a file that exists; every exemption carries a reason. Wired into the
release gate.

**The reason clause matters most.** An exemption is the one way to remove a file from coverage
without deleting it, which makes it the obvious place to hide something — and therefore the one place
that must be a *visible line in a generated artifact* rather than a silence. An exemption added to
conceal a file is then an edit someone can see and question.

**Proven both ways per L-95, exit codes recorded directly rather than through a pipeline:**

```
clean tree                  -> exit 0
uncovered file planted      -> exit 1
exemption naming no file    -> exit 1
restored                    -> exit 0
```

**Attribution:** this release is the first from this package to carry `rel:authoringSession`. Its 31
prior commits read `UNDECLARED` and stay that way — an absent claim cannot be added later (L-112).


## v1.53.0 — 2026-08-10 (MINOR: L4 was not a superset — it was a replacement)

**Found by test-driving a trial declaration**, which is what the lineage ceremony's step 1 is for.
Driving one register through all three levels produced a result that could not be right: **L3 reported
more violations than L4**. The `ConformanceLevel` definition says each level is *"a strict superset of
the previous"*. It was not.

Measured: **57 clauses excluded `L4_LineageEnforced` entirely** — 37 gated `IN (L2, L3)` and 20 gated
on `L3_Governed` exactly. **Declaring the strictest level silently switched off every L2 and L3
check**, including all evidence anchoring, harness completeness and release anchoring. The level that
enforced the most enforced the least, and a register could have moved from L3 to L4 and lost ground
without a single message saying so.

**This is G8 of the Lineage Operating Discipline, committed one release after writing it down:**
*every rule naming a member of a closed set has an unstated dependency on that set's membership.*
Adding a fourth member to a three-member enumeration broke 57 rules. The fix at v1.48.0 caught the
three that tested "below L3" and stopped there — it repaired the symptom it had tripped over rather
than searching for the class.

**Repointed, and monotonic now**, verified by driving one register through all three levels:

```
L2_EvidenceBound     0 violations
L3_Governed         83 violations
L4_LineageEnforced 120 violations
```

**The fix immediately failed the L4 conformant fixture**, correctly — it had been written when L4
enforced nothing below itself, so it had never been held to L2 or L3. Brought up to standard: test
harnesses with derived completeness, finish points on execution tasks, an acceptance criterion on the
epic, and a score no longer predating the register's most recent completion. Both polarities verified:
conformant 0, adversarial 24.

**Published against origin after a third collision.** A parallel session shipped v1.52.0 — the drift
gate no longer depending on an ambient environment variable — while this work was local. B5's
freshness clause and BP-D7's already-published guard both fired; origin is authoritative, and this
re-applied on top rather than overwriting.

**Not in this release, and stated rather than implied:** a remediation of the framework's own register
— epics lifted out of iterations, decomposed into the stories actually delivered, with planning events
and deployment units — was completed and then **lost to a container reset between turns**. It was
never published and is not claimed here. The register remains at L2 with the L4 gap now precisely
measured.


## v1.52.0 — 2026-08-10 (MINOR: the drift gate stops depending on ambient state)

**G7 of the Lineage Operating Discipline, walked into while writing the section about it.**

The public distribution was **ten releases behind** — v1.41.0 against a governed v1.51.0, with the
Lineage Operating Discipline returning 404 to anyone reading the public copy. The drift check has
existed since **v1.26.0** and works: run against the stale copy it reported the version gap and the
byte divergence correctly, first try.

It simply never ran. It was wired to `BACKLOG_PUBLIC_URL`, an environment variable set once and lost
when the container was rebuilt, after which the gate printed `NOT RUN` for ten consecutive releases.
*A check that does not run tells you nothing* — and a check depending on ambient state that does not
travel with the package will eventually not run.

**Fixed by recording the URL in the package.** `.public-distribution-url` ships alongside the
manifest, so the gate resolves its target from the artifact rather than the environment. The
environment variable still works as an override; what changed is that its absence no longer means
silence.

**Proven immediately.** With the URL recorded, the gate ran unprompted and **failed** — the gate
rename in this very release had made the working tree diverge from what was published minutes
earlier. That is the check catching its own author within one release of being fixed.

**The public copy is current:** v1.51.0 pushed and verified by unauthenticated fetch, drift check
PASS against a fresh derivation, and the Lineage Operating Discipline reachable publicly for the
first time.


## v1.51.0 — 2026-08-10 (MINOR: the Lineage Operating Discipline, under this package's own authorship)

**An authorship correction, not a rejection.** `LINEAGE_OPERATING_DISCIPLINE_v1_0_0.md` was written by
a parallel session and shipped inside this package. The owner has ruled that only the session owning
the framework maintains it. v1.0.0's ceremony, its six boundaries and — most valuable — its
self-checking mechanism were sound, and are carried forward substantially unchanged rather than
rewritten for the sake of it.

**Deleting it was considered and rejected.** Its enforcement claims *held*: the shipped checker
reported every named shape present at the claimed severity. Removing it would have removed a passing
check. Rewriting keeps the mechanism and puts the authorship right.

**Three things it predated, now folded in:**

- **Ceremony step 4** — decide how work reaches users (`PlanningEvent` → `Iteration` →
  `DeploymentUnit`) **before the first story**, because at L4 a closed iteration with no deployment is
  a violation and retrofitting a release history is fabrication.
- **G7 — a tool that refuses is not thereby correct.** Three defects in this framework's own tooling
  were plausible refusals or meaningless clean passes. **No shape catches this**; the check that does
  is a fixture whose answer is known in advance.
- **G8 — every rule naming a member of a closed set depends on that set's membership.** Adding
  `L4_LineageEnforced` broke three *"below L3"* clauses that fired on a level above L3. **No shape
  catches this either.** It was caught only because a fixture exercised the new member — G7 applied
  to vocabulary.

Both are recorded in the document precisely *because* they are unreachable by SHACL, which is what the
document is for.

**One correction to v1.0.0's content.** Its G1 note implied `LineageDepthAdvisoryShape` was missed
because a session ran at L2. Measured: the shape is **not level-gated** and fires at L1. "We ran at
L2" does not explain the silence — the shapes file was not run at all. Corrected in place, since
v1.0.0 is superseded rather than a historical record.

**The checker now verifies six shapes rather than four** — `EpicPlanningShape`,
`LineageDepthAdvisoryShape`, and the four L4 shapes including `L4DeploymentVerifiedShape` — and passes
without modification, because it resolves the discipline by pattern rather than by pinned name.


## v1.50.0 — 2026-08-09 (MINOR: a deployment carries only proven work)

**Written against origin after a collision.** A parallel session published v1.49.0 — the Lineage
Operating Discipline and its enforcement checker — while this work was in progress locally under the
same number. Origin is authoritative: this session discarded its local numbering, resynced, checked
whether v1.49.0 had already covered this ground (it had not — that release governs *building* a
lineage; this gates *shipping* from one), and re-applied on top as v1.50.0. B5's freshness clause is
what made the collision visible rather than silently overwritten.

**Asked whether test coverage and confirmation exist in the lineage. Measured before answering.**

**Per item the framework was already strong:** `Evidence`/`TestEvidence` with `evidenceVerified`,
`verifiedByTool`, `hasVerificationMethod`; `attestsCriterion` linking a passing test to the criterion
it proves; and `TestHarness`, whose `harnessComplete` is derived true **only when every acceptance
criterion of the item is attested by a bridge-verified artifact**. That is per-item test coverage and
it long predates L4.

**At release time none of it was consulted.** Proven by construction: a `DeploymentUnit` shipping a
story that was `InProgress`, carried no Evidence and whose acceptance criterion nothing attested
validated at **0 violations at L4**. Every existing deployment clause checked the *shape* of the
release — a date, at least one item, no epic, an iteration link — and none checked whether what it
carried had been proven.

**Added at L4, four clauses on `DeploymentUnit`:** every deployed item is `Done`; carries
bridge-verified Evidence; has **every** acceptance criterion attested; and the deployment records
**who released it**. The third is coverage at release time — a suite can be green while the criterion
everyone cared about is untested, which is what `attestsCriterion` exists to expose.

**No coverage vocabulary was minted.** `harnessComplete` already carried the notion; the gap was
never a missing concept, only a check that never ran.

**Fixtures on both polarities:** the conformant L4 register carries a harness and a releasing
decision and validates at 0 with 0 of 46 constraints suppressed; the adversarial one ships an
unfinished, unevidenced, unattested story and fires all four clauses.


## v1.49.0 — 2026-08-09 (MINOR: the Lineage Operating Discipline, and a gate on its own claims)

A companion to the OE Operating Discipline, in its form and deliberately not a restatement of it:
**that document governs building and releasing an ontology; this governs building a lineage inside
one.** Where both apply the OE ceremony runs first, because a lineage grounded on unverified bytes is
a lineage about nothing.

**A lineage ceremony, executed before the FIRST work item rather than after the twentieth:** declare
the level with its rationale, target and review date; build Mission→Goal→Objective→Scope and
**validate it empty**; state the granularity chosen and why. A chain that does not validate empty will
not validate full, and every item written before the chain exists must be revisited once it does.

**Six boundaries the shapes cannot reach**, each a failure this ecosystem has actually observed:
granularity by momentum · advisory blindness · permitted-is-not-intended · completion-is-not-
accomplishment · the why/when/what conflation · drift as the default. Each names the shape that
catches it, and says plainly where none can.

**The document is honest about its own limits**, which is the point of the last section: it enforces
nothing. SHACL enforces; the document makes boundaries visible at the moment several of them are
still cheap to observe.

**But its claims about enforcement are checked.** `backlog_lineage_discipline_check` reads the
discipline and the shipped shapes and fails the release if a named shape is missing, has been softened
from Violation to Warning, or is described as L4-gated while firing at every level. **A discipline
document whose enforcement claims have drifted is worse than none, because it is believed.** Wired
into the release gate; proven to fail by renaming one shape reference.

**A defect in the checker, caught by cross-reading its own output.** v1.0.0 split shape blocks only on
the next shape declaration, so a shape immediately followed by a section banner absorbed that banner's
text — `EpicPlanningShape`, an L2 shape, was reported *"L4-gated"* because the banner announcing the L4
section mentioned L4. Fixed at v1.0.1 by cutting each block at the banner. **A checker whose report is
not itself checked is another decorative gate**, and this one was caught only because its output was
compared against the shapes file rather than read.


## v1.48.0 — 2026-08-09 (MINOR: L4_LineageEnforced — the lineage as violations, not advice)

Requested by the framework owner: enforce the lineage with full measurement, so a register can
**prove a mission was accomplished** rather than report that work was done. The distinction is the
whole of this release — completion is a fact about effort, accomplishment is a fact about the world,
and only the second requires a measurement.

**A fourth conformance level, not a promotion inside L3.** Promoting the advisory checks inside an
existing level would silently break every adopter who made a different claim, and this framework's
own documented principle is that a level is a claim an adopter **makes**. L1, L2 and L3 behaviour is
byte-identical; the positive fixture still validates at 0.

**Eight clauses fire only at L4**, each proven to fail on an adversarial fixture built by mutating
the conformant one:

- every item traces to an objective; every objective carries a `MetricObservation`
- every epic decomposes; **no epic in an Iteration**; **no epic in a DeploymentUnit**
- a story reaching execution passed through a `PlanningEvent`
- a closed iteration connects to what shipped via `deploysFrom`
- no item pursues an objective the scope does not realise — **scope drift, stated literally**

**`DeploymentUnit` is new** and exists to separate three things this framework has repeatedly seen
conflated: **what shipped**, **when it was worked**, and **why**. The epic-as-deployment-subject
misuse becomes stateable rather than merely discouraged.

**A defect this release created and then caught.** Widening a closed enumeration broke three rules
that had tested against its old top member by name: `AdoptionRampShape`'s *"an adoption below
L3_Governed must declare a target"* fired on **L4**, which is above it. Found by the L4-conformant
fixture failing on its first run. Repointed to `NOT IN (L3, L4)`.

That is the cost of widening a closed enumeration, and it is worth stating plainly: **every rule that
names a member of a closed set has an unstated dependency on the set's membership.** The suite caught
it, but only because a fixture existed that exercised the new member.


## v1.47.0 — 2026-08-09 (MINOR: epics are decomposed before they are planned — correcting this session's own advice)

**This session told an adopting session something wrong and is correcting it here.** Reviewing their
handover, this session read `Epic ⊑ ProductBacklogItem` and `plansItem range ProductBacklogItem`,
concluded that planning an Epic into an Iteration was permitted, and told them their guidance to
decompose first was unnecessary.

**The definitions say the opposite**, and they were not read:

- **Epic** — *"a large body of work decomposed into, or delivered across, **multiple** features or
  stories; its completion **typically derived from the completion of its constituent work**"*
- **Story** — *"small enough to be **completed within one iteration**"*
- **Iteration** — *"a fixed-length time box"*

An epic with no children committed to one time box can neither fit it nor derive a completion from
anything. **The adopting session was right**; only their stated reason was imprecise, and this
session corrected a conclusion that was sound using a hierarchy check that could not settle it.

**BP-D4 in its plainest form:** a subclass relation answers *what may be asserted*; a definition
answers *what the term means*. Reading only the first is how a forbidden arrangement came to be
described as permitted.

**`EpicPlanningShape`** rejects a `PlanningEvent` committing an undecomposed Epic to an Iteration at
L2. Nothing had objected before — verified by construction first, so the gap was measured rather
than assumed. Planted defect 95 covers it.


## v1.46.0 — 2026-08-09 (PATCH-class: the cumulative flow never worked, and said so for the wrong reason)

**A parallel session's finding, verified against the published TBox and upheld exactly.**
`backlog_views` read a single-hop `backlog:transitionedTo`. That property **has never existed in this
subject's TBox at any version**. The declared model is two hops: a `TransitionEvent` points at a
`StateTransition` via `viaTransition`, and the `StateTransition` carries `toState`.

**Why it survived a release and a public publication.** The section could only ever print its refusal
— *"no TransitionEvent carries a timestamp"* — and that refusal was reported here as correct
behaviour, twice. **A refusal that is correct for the wrong reason is indistinguishable from one that
is correct.** The finding required reading the declared model against the code, which is what the
reporting session did and what this session did not.

**A second defect behind the first**, surfaced by the corrected diagnostic within a minute of writing
it: the tool loaded the TBox but **not the framework ABox**, where every `StateTransition` individual
lives. So even with the right path the second hop dangled. The new message says *why* resolution
failed rather than only that it did, and that is what exposed it.

**Both fixed.** The positive fixture has carried **8 TransitionEvents since v1.7.0** and now produces
a real cumulative flow — Ready accumulating from 17 July, InProgress from the 18th, a cancellation on
the 24th and the first Done on the 27th.

**The gap underneath both:** no gate exercised the transition path, because the CFD's refusal was
accepted as data-driven rather than checked against the model. A tool that refuses is not thereby
correct, and this package had no check distinguishing the two.


## v1.45.0 — 2026-08-09 (MINOR: BRF-EP4 — the register's last epic, and three defects it exposed)

Ceremony under **v2.3.0**, pack v20.30.0 (197/197), freshness confirmed against origin before and
after. The scope exclusion `Ex_Modality` had settled EP4's design before the build, so nothing was
asked.

**Human involvement is now a register fact.** `ExecutionModality` (Human/Automated/Hybrid),
`SupervisionMode` (in-the-loop / on-the-loop / none), `HumanInteraction` as an **event** carrying its
own cost on the existing dimensional machinery — so review time is **budgetable without being
schedulable** — and six `InteractionKind`s of which Confirm and Reject **gate** and the rest inform.

**In-the-loop is a fact about gating, not attitude.** *"We review everything"* and *"nothing proceeds
without review"* sound identical in prose and are different systems. Claiming in-the-loop with nothing
recorded as gating is rejected; so is claiming no supervision while a person gated it, and correcting
an output while claiming `Automated`.

**An advisory turns the framework's own reasoning on human gates:** where confirmations exist and no
rejection ever has, *a check never observed to fail has not been shown to be a check.*

### Three defects the build exposed, all mine

**1. My own constraint caught me overstating supervision.** I marked five completed epics
`Sup_InTheLoop`. Only EP4 had an explicit authorisation with a recorded confirmation; the rest ran
under *"proceed as far as you need no response from me"* — which is **on-the-loop**. Corrected to
match what happened rather than adding gates that never existed.

**2. A category error in my own measurements.** Term counts were attached as observations of the
*outcome* metrics. Terms delivered is **effort**, not questions answered. Replaced by measuring what
the objectives actually name: ran every view and counted answers versus refusals — **6 of 8
answerable, 75% against a target of 80**. The objective is **not met**, and is not recorded as met.
Cumulative flow and per-dimension cost remain unanswerable for this register, so the adopter metric
reads **2 against a target of 0** — improved, not achieved.

**3. A jointly-unsatisfiable rule.** With the work complete and objective deadlines in 2027, neither
R12a (all Met) nor R12b (any Missed) could derive a scope outcome — yet the suite demanded one.
Unsatisfiable unless someone fabricated an outcome, which is what the constraint exists to prevent.
**R12c** derives `Ach_Pending`, keyed on the **absence** of a derived outcome rather than on a Pending
state no rule produces.

**Estimate 17, actual 19.** The two extra are `Sup_None` and `Int_Reject` — the honest-negative
members. Without them, unsupervised work would have to be recorded as supervised, and a gate would
have no way to record a refusal.

**The register is closed.** All six epics Done with verified evidence; scope outcome **Pending**,
which is the truthful state.


## v1.44.0 — 2026-08-09 (MINOR: BRF-EP3 built — multi-dimensional cost)

**Ceremony under v2.3.0 from a fresh origin clone**, pack v20.30.0, 197/197. The container had been
wiped — toolchain and working tree both gone, which is B5's stated scenario — so both were
rehydrated from the governed store before anything was read.

**The register chose the work and had already specified it.** EP3 at 2.75, its acceptance criterion
written before the build, and four execution tasks planned into an iteration. Neither of the two
design questions that once interrupted development came back: `Ex_Complexity` and `Ex_Modality` had
settled them in the scope statement.

**No modality-specific predicate was minted** — no `tokenCost`, no `gpuHours`. Tokens, compute,
review time and complexity are **instances** of `CostDimension`, each with its own unit. A property
named for one modality would privilege it the way a story-point property would privilege one
estimation practice.

**A rate is optional, and that is load-bearing.** Human review time ships unpriced in the fixture:
the cost view reports it separately and says plainly that it contributes to no monetary total —
*a choice, not an omission, because some costs are constraints rather than bills.*

**Roll-up is derived, never asserted.** A cost on a parent *and* its decomposition child along the
same dimension is rejected — the same double-count the framework already refuses for priority scores.

**Four checks the suite made on its own author while recording completion:**

1. `StaleInvariantStatusShape` refused to let `Inv_NoModalityPredicate` stay `NotYetEnforceable` once
   EP3 shipped. The check query was **executed** — no `tokenCost`/`gpuCost`/`humanHours` predicate
   exists — and the status moved to `Holds` on that result, not on assertion.
2. EP3 could not be `Done` while three decomposition stories were still `Proposed`.
3. Every completed execution task needed its own evidence at L2.
4. One evidence method was rejected as **a bare assertion**; it now names the check that could have
   failed — the negative fixture rising from 90 to 94 planted defects, each confirmed firing by
   identifier.

**Estimate 12, actual 13.** The extra term is `hasRateCurrency`, which the estimate folded into the
rate and which summing two currencies shows must be separate.


## v1.43.0 — 2026-08-09 (MINOR: the shipped history backfilled; period domain widened)

**Ceremony run under OE Operating Discipline v2.3.0**, fetched from origin — the local pack was at
v20.28.0 while origin held **v20.30.0**. v2.3.0's new clause is exactly about that: B5 previously
prescribed only a manifest self-check, which proves a snapshot is undamaged and is equally true of one
six months stale. The enriched boundary requires `git fetch` and zero-commits-behind before any
governed action. It caught this session before this session read it.

**Twenty shipped releases backfilled — from bytes, not recollection.** Every date is a git commit
timestamp, every title a changelog headline, every evidence record a real commit SHA and tag. Emitted
programmatically so no figure passes through memory.

**`hasActualEffort` is deliberately absent from all twenty.** Elapsed time between releases is not
effort; no effort was measured at the time, and inventing one would be the fabrication this framework
exists to refuse. `hasDuration` carries the elapsed days, which is what was actually observed.

**Twenty advisories stand, unresolved on purpose:** *"advances no recorded objective"*. True — those
releases predate the objectives, and linking them would retrofit an intent nobody held. The advisory
is the correct reading of a real fact.

**A defect found by using the vocabulary rather than reading it.** `iterationStart`/`iterationEnd`
were domained on `Iteration` alone, so an `Increment` — defined as *"the releasable body of work
completed by a stated point in time"*, which has a period by construction — could not carry one. The
burn-down skipped a container of twenty items **in silence**. Same shape as the roadmap-rank widening
at subject v1.11.0, and caught the same way. TBox → **1.16.0**, domain widened to the union; views →
**1.2.0**, which now reads both and would have said so rather than skipping.


## v1.42.0 — 2026-08-09 (PATCH-class: the burn-down reached zero over open work)

Found by rendering the views for a real register rather than for a fixture.

`backlog_views` v1.0.0 summed **effort** for an iteration's total but fell back to
**one unit per item** when burning. An item with no estimate therefore contributed nothing to the
total and one unit to the burn — and the chart reached **0.0 left while four execution tasks were
still Proposed**.

A burn-down hitting zero over unfinished work is the *looks-complete* failure this framework exists
to refuse, produced by the framework's own tool. The defect was an inconsistent basis, which is the
same class as comparing a naive date against an aware one: two quantities that appear comparable and
are not.

**v1.1.0** picks one basis for the whole iteration and prints it. Where any member lacks an
estimate the iteration is counted in **items**, and the members that forced that choice are named —
because an effort burn-down would have omitted them silently, which is how the defect arose. A
belt-and-braces warning fires if remaining ever reaches zero with members still open.

Same register, after: `6.0 items committed`, **4.0 left** across the whole iteration, with the four
unestimated tasks named.


## v1.41.0 — 2026-08-09 (MINOR: the plan alongside the roadmap — Gantt, SPI, and five views)

**The scope exclusion is reversed on the record, not deleted.** `Ex_Schedule` refused a time-phased
baseline because horizons are ordinal by design. That reasoning still holds **for the roadmap** and is
unchanged: horizons stay ordinal, `hasRoadmapRank` stays an ordering, neither gained a date. What is
admitted is a **plan alongside** the roadmap. A `ScopeChange` supersedes the exclusion and both remain
readable — L-112 forbids editing a record of a past decision to match a later one.

**`KickOff` answers the start-time problem directly**, and carries a mode: **Declared** must name who
declared it, **Triggered** must name the automated event, so a start that was *claimed* is
distinguishable from one that was *recorded*. Until a kick-off exists a plan is a proposal — its dates
compare with each other but not with reality.

**`plannedStart`/`plannedFinish` are deliberately distinct from `startedAt`/`finishedAt`**: the gap
between them is the whole of schedule variance, and collapsing them would make every plan appear met.
`hasDuration` is elapsed days, not effort — two people for a day and one for two days share an effort
and differ in duration, and a critical path is a chain of durations.

**`PlanBaseline` retains superseded baselines** so performance stays computable against the original
plan, not only the current one. That is the number a rebaselined project would rather not show, and
retaining it is the answer to the criticism earned-value practice most often attracts.

**`backlog_views_v1_5_0.py` derives five views** — Gantt and network as Mermaid, burn-down as text
bars, cumulative flow and earned value as tables. Mermaid because it diffs, reviews, and renders in
GitHub with no toolchain and no new dependency. **Nothing is stored.**

**The refusal is the part under test as much as the drawing.** With no `KickOff`, Gantt prints *"NOT
DRAWN — planned dates anchor to nothing"* and SPI prints *"NOT COMPUTED"*, because assuming today
would make every plan appear on schedule on the day it is read. Verified in both states.

**A stale non-goal corrected.** §8 still read *"not a project-management tool (no velocity, capacity
or burndown)"* — velocity and capacity shipped at v1.38.0 and burndown ships here. The standard was
describing a framework three releases out of date.

**Registered as a third mission**, not appended to an existing one: `Mission_Plan` with its own goal,
objective and metric, and two epics — BRF-EP5 (views, 5.00) and BRF-EP6 (kick-off and schedule, 2.50).
Both Done with evidence; EP6 actual **14.0 against an estimate of 12.0**.


## v1.40.0 — 2026-08-09 (MINOR: the register's absent layers filled; two overstatement defects corrected)

**A state correction first.** The previous turn reported *"No, I did not build a lineage"* against a
working tree that had since moved. **v1.39.0 already performed the relocation** — register out of
`03-tooling/fixtures/` into `01-ontologies/`, with scope, five exclusions, a Definition of Done, six
stories and six decomposition edges, plus `LineageCompletenessShape` and a completeness reporter. The
governed remote was authoritative and the local tree stale; resynced from it rather than rebuilt.
The diagnosis stands; the claim that nothing had been done about it did not.

**Both questions asked mid-build are now settled in the scope statement, where they belonged.**
`Ex_Complexity` rules that complexity is a cost dimension, not a property, citing Wood 1986's
component/coordinative/dynamic decomposition. `Ex_Modality` rules that human *work* assigned to a
person is a `WorkItem` competing for capacity, while human *interaction with* work is an event. Those
are the two questions that interrupted development; a scope statement is where they stop being
questions.

**Defect in v1.39.0's own tool, found by running it.** The completeness reporter marked six layers
`L2`/`L3` that `LineageCompletenessShape` does not reach — it enforces three. So the report asserted
a consequence the suite would not deliver, which is the same defect as prose overstating a
measurement, one level up. **v1.0.2** marks only what the shape enforces, and states the conditional
case (a `PlanningEvent` is required at L2 **only where execution tasks exist**) in the consequence
text rather than encoding it as an unconditional mark.

**Register 1.1.0 → 1.2.0: the six absent layers filled**, because a report that names a gap and is
then ignored is a decorative gate with an extra step. Two iterations with real periods, so velocity
has a denominator. A planning event breaking EP3 into four execution tasks. A dated milestone that
can be missed. Two cross-cutting invariants with executable check queries — one `Holds`, one
`NotYetEnforceable` tracking EP3. A forecast carrying three assumptions, including that its velocity
rests on a single closed iteration.

**Completeness report: 0 layers absent.** Register validates 0 violations at L2.


## v1.39.0 — 2026-08-08 (MINOR: lineage completeness — the drift, its cause, and the gate)

**The owner asked whether a lineage had actually been built. It had not.** Measured from disk: the
register sat in `03-tooling/fixtures/` as test data while declaring its own ontology IRI and version;
it held 2 Missions, 2 Goals, 2 Objectives and 4 Epics, and **zero** ScopeStatements, ScopeExclusions,
DefinitionOfDone, Stories, ExecutionTasks, PlanningEvents, Iterations, Milestones, Risks or
CrossCuttingInvariants, with **zero decomposition edges**. Four epics that broke down into nothing.

**Why nothing caught it, measured rather than supposed.** `sh:targetClass` cannot see absence. On
this suite: 1 shape guards `Mission`, 1 guards `ScopeStatement`, 2 guard `Objective`, 2 guard `Goal`
— every one unreachable when the concept has zero instances. So the register declared L2, reported 0
violations, and omitted whole layers. The owner reports the same in parallel sessions, which is what
makes this a framework defect rather than a lapse in one register.

**The gate, as the owner asked — a feature of the lineage, not a note.**
`LineageCompletenessShape` targets `Backlog`, the one node guaranteed present, and at L2 refuses a
register with no Mission, no Objective, no ScopeStatement or no DefinitionOfDone; at L3 it refuses
scored Epics that decompose into nothing. Advisories cover thinness: epics with nothing beneath them,
a scope with no exclusion. **Verified against the defective register: it now fails.**

**`backlog_lineage_completeness_v1_0_2.py`** reports every layer at any level and states what each
omission costs, so a register can be improved before being failed. Wired into the release gate.

**The register repaired** and promoted to `01-ontologies/backlog_framework_register_abox_v1_7_0.ttl`:
scope with **five recorded exclusions**, a Definition of Done with **six executable criteria**, and
the unbuilt epics decomposed into six stories with acceptance criteria.

**The mid-build question is now answered by the scope, where it belonged.** `Ex_Complexity` records
that no dedicated complexity property will be added — Wood's task complexity is largely derivable
from dependencies and decomposition, McCabe's code complexity belongs to an artifact as a measured
observation, and what remains is a named cost dimension. `Ex_Modality` settles human review as an
event, not a work item. Both were asked of the owner mid-build; both should have been settled at
scope-definition time, and now are.

**Still absent and reported, not hidden:** PlanningEvent, Iteration, Milestone, ExecutionTask,
CrossCuttingInvariant, Forecast. The reporter names them and says PlanningEvent is the one L2 wants.


## v1.38.0 — 2026-08-06 (MINOR: BRF-EP2 — flow, velocity and forecast)

Second by the register's own ranking, at 4.00. Acceptance criterion: *cycle time, item age and
per-iteration velocity are computed, and any forecast states the assumptions it rests on.*

**Almost nothing was added, because almost nothing needed to be.** Cycle time, item age, throughput
and velocity are **computed by the report** from `startedAt`, `finishedAt` and the iteration period.
Storing them would duplicate a derivable fact that could then disagree with its own inputs — L-91 one
level down. The estimate assumed 11 net-new terms; the actual was **9**, *under* because four of the
five headline measures needed no vocabulary at all.

**Two things genuinely could not be derived.** `iterationStart`/`iterationEnd`, because velocity is
work per iteration and without a period there is no denominator. And `Forecast`, because a forecast is
a **claim about the future**: at least one `forecastAssumption` is required, since a forecast
presented without assumptions asks to be believed rather than checked, and when it misses there is
nothing to point at as the thing that failed. The observed velocity and the iteration count are
required too, so the arithmetic is checkable and a forecast built on **one** iteration is
distinguishable from one built on a settled average.

**The report says which is which.** It prints remaining-work arithmetic and states explicitly that
*this is arithmetic, not a Forecast* — the projection is free, the claim carries obligations. Where
velocity rests on a single iteration it says so unprompted: *one iteration is a data point, not a
rate.*

**Found while building:** a function-scope `from datetime import datetime` shadowed the module import
and broke `main()` for every register, not just those with flow data. Caught by running the tool
rather than by reading it.

**Next by the register: BRF-EP3, cost dimensions, 2.75.**


## v1.37.0 — 2026-08-06 (MINOR: BRF-EP1 built — the register chose it, the register records it)

The framework's own register ranked **BRF-EP1 first at 6.50**. Its acceptance criterion was the
specification; each clause below enforces one phrase of it.

**A naming trap, avoided by reading the definition.** `Task` looks like a sprint task. Its shipped
definition says a Task *"must still be tracked, **prioritised** and evidenced like any other work
item"* — so it is non-user-facing **product** work, and repurposing it would have silently redefined
every register already using it. The R3 fixture's legitimately-scored `ex:Fast` Task is exactly such a
case. `ExecutionTask` is therefore a **new ninth kind**, not a re-reading of an existing one. L-75:
the name misled, the definition corrected.

**Added — TBox 1.12.0 → 1.13.0:** `ProductBacklogItem` over the eight original kinds; `ExecutionTask`,
disjoint from it; `PlanningEvent` with `plansItem`, `plannedInto`, `producesTask`, `plannedAt`,
`plannedBy`.

**Added — shapes 1.15.1 → 1.16.0:** an execution task may carry no priority score and no roadmap rank,
must belong to a backlog item, and at L2 must trace to a planning event; a planning event must name
item, iteration, time and at least one task; a backlog item may not be Done while a task planned from
it is open.

**A contradiction I introduced and then fixed at the root.** With `ExecutionTask ⊑ WorkItem`, eight
product-backlog constraints applied to tasks — including the silent-gap rule, which *requires* a
score while the new rule *forbids* one. **Jointly unsatisfiable for every task.** The same defect class
an adopting project reported to this package about `LaunchGateShape`, reproduced by its author within
one release of ruling on it. Fixed by excluding execution tasks from all eight, not by relaxing
either.

**A new gate, from a defect the work exposed.** The R3 disagreement fixture had drifted through
several releases and accumulated six violations, because **no gate ran it**. The fixture-coverage
gate now validates every shipped fixture against the expectation its filename declares — and caught a
**second** drifted fixture, `fixture_tied_gates`, on its first run.

**Recorded in the register, per the framework's own rules.** BRF-EP1 is Done with verified evidence
attesting its acceptance criterion, `startedAt`/`finishedAt`, and `hasActualEffort` **9.0 against an
estimate of 7.0**. The overrun is recorded with its cause: the estimate enumerated seven terms and
missed the disjointness axiom and `plannedBy`. That is the estimate being falsified by its own actual,
which is what `hasActualEffort` exists for.

**Next, by the register rather than by opinion: BRF-EP2, Flow & progress, 4.00.**


## v1.36.0 — 2026-08-06 (MINOR: the framework's own register — and a date bug it immediately found)

The owner declined an ad hoc ordering of the maintenance-and-progress work and asked for the lineage
approach instead. That was the right call: the previous turn's numbered list was an ad hoc decision
wearing the clothes of a recommendation, and this framework exists to refuse exactly that.

**`fixture_framework_register_v1_0_0.ttl`** registers the framework's own development under the
framework: two missions (development and operational, per §2.5c-ii), two goals, two objectives with
metrics, baselines, targets and directions, an owner-decided profile at **L2 targeting L3** — L3 was
declined because nothing is Done yet and claiming it would assert a discipline no completed work has
been held to — and the four candidate subjects as scored epics.

**The job sizes are measured, not judged.** Each subject's estimate is the counted number of net-new
terms it must add, recorded as a `MetricObservation` and referenced by `basisObservation` with
`Basis_Measured` — the vocabulary shipped one release earlier, used in earnest. **The first probe was
discarded as worthless**: it tested only terms already known to exist and returned 100% for every
subject. Recorded in the observation's own method text, because a discarded measurement is part of
how the kept one was obtained.

**The order is computed, and it agrees with the intuition it was meant to check** — which is a weaker
result than disagreement would have been, and is stated as such.

**The dogfooding immediately found a real defect in the framework's own shapes.** A future review date
of 2026-11-06 was reported as *passed*. Cause: comparing a timezone-**naive** stored `xsd:dateTime`
against a timezone-**aware** `NOW()`, which rdflib evaluates as `true` for a future date. Verified in
isolation — naive November `< NOW()` returns `true`, the same value with an explicit `+00:00` returns
`false`.

**Five comparisons across two files were affected**, and they are not cosmetic: they decide whether an
objective is reported **Missed**, whether a milestone is overdue, and whether R9/R10 derive an outcome
at all. Every one could fire on a deadline that has not arrived. Fixed by comparing lexical prefixes,
which is timezone-independent and total for ISO-8601; shapes → **1.15.1**, rules → **1.5.1**, PATCH
because no vocabulary changed.

**This is what the register was for.** Four subjects were about to be built on shapes that
misjudged every date they touched.


## v1.35.0 — 2026-08-06 (MINOR: measured versus judged — test-driving an estimate)

The first increment of the maintenance-and-progress lineage, and the one the owner authorised
directly: make it visible whether an estimate or a score was **executed** or **reasoned**.

**The gap, verified before designing.** `hasCostBasis` already recorded *what* a figure rested on, in
prose. Nothing recorded whether that basis was **run**. So a number produced by a timed spike and a
number produced by a confident opinion were indistinguishable in the register, and the weaker
evidence inherited the stronger one's authority.

**Precedent, not invention.** An adopting project had already demonstrated the better practice
without vocabulary to declare it — setting an objective's baseline by test-driving a trial
conformance declaration against a scratch copy of its live register, and recording the figure as
measured rather than estimated, before any planning discussion. This release names what they were
already doing.

**Added — TBox 1.11.0 → 1.12.0:** `EstimationBasisKind` closed at **Measured / Analogous / Judged**;
`hasBasisKind` on both `CostEstimate` and `PriorityScore`, because a ranking whose inputs were
test-driven is different evidence from one whose inputs were argued; `basisObservation` linking a
measured figure to the `MetricObservation` that produced it; `analogousTo` naming the completed item
a comparison was drawn from.

**Added — shapes 1.14.0 → 1.15.0:** a Measured claim must name its observation; an Analogous claim
must name its comparable; at L3 an estimate must declare a basis kind at all. Plus an **advisory**,
not a violation, where measuring pays best — a judged estimate on an item inside a launch gate.

**Judgement is not forbidden and is the majority case.** What is forbidden is a judgement that reads
as a measurement once whoever made it is no longer in the room. The same distinction this framework
draws between evidence marked verified and evidence marked verified by a named tool.


## v1.34.0 — 2026-08-06 (MINOR: NEXT was not reproducible — ruling on the item-level tie)

`Proposal_ItemLevelNextTieBreak_v1_0_0.md`, fetched from the adopting project's own repository rather
than worked from the handoff summary, as the handoff itself instructed.

**The defect is worse than reported, measured not recalled.** They observed two different answers in
three runs. Constructing six items at an identical score and running five fresh interpreters against
an unchanged register: **five different answers.** Root cause confirmed in the source — `ranked()`
iterated a Python `set` and sorted on score alone; `sort()` is stable, so it preserved the set's
iteration order among equals, and that order depends on per-process string hash randomisation.

**The ruling: none of A, B or C as framed — because the framing misses the actual defect.**

The proposal treats this as a missing tie-break, and offers minting `hasDuration`/`hasComplexity`
(A), using existing vocabulary only (B), or reporting the tied set (C). But **the defect is
non-determinism, not the absence of a tie-break.** A report that answers the same question
differently on identical input is unreproducible in exactly the sense this package refuses
everywhere else — the same principle that governs `RELEASE_METRICS.txt`. Determinism is not a design
option among three; it is the bug, and it must be fixed under any of them.

**So: determinism unconditionally, and C for the tie.**

- `ranked()` now imposes a **total** order: score descending, `hasJobSize` ascending, identifier.
  Score because that is what ranking means; job size because among equally-valuable work the smaller
  job finishes sooner, and it is an existing first-class WSJF input populated on every scored item;
  identifier last, purely to close the order, carrying no meaning.
- NEXT names one item **and prints the whole tied set**, with the tie explicitly unresolved. This is
  the convention this framework already runs for R3, which prints both models' answers and resolves
  neither.

**Declined, with reasons rather than silence.** `hasDuration` and `hasComplexity` are not minted:
L-110 forbids structure on one producer's evidence, and the requesting owner defined neither term —
minting an undefined concept encodes the framework's guess as the adopter's meaning. "Launch-ready
package containment" is declined for the sharper reason that the request itself said *"however you
choose to operationalize it"*: inventing the metric would put a number in the owner's mouth.

**Gated, so it cannot regress.** `fixture_item_tie_v1_0_0.ttl` ships six items at one score with six
distinct job sizes, and the release gate runs the report through **five fresh interpreters** and
aborts unless all five agree.


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
was invisible to the proof. `backlog_gate_v1_1_16.sh` now runs the known-bad fixture through the
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

`backlog_validate_v1_4_0.py` now prints a **grouped digest**: count per distinct message, the first
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
   `build_manifest_v1_4_0.py`, which now prunes `__pycache__` and skips `.pyc`/`.pyo`, rather than by
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

**Added — tooling:** `backlog_roadmap_report_v1_5_0.py` (eight sections, both NEXT answers, silent
-gap check), `backlog_coverage_gate_v1_1_1.py` (BP-D31), `backlog_gate_v1_1_16.sh` (Gate 0 / P / K /
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
