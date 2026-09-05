# Closure Report & Dashboard — Lineage 7 (`L_OntologyDriven`)

**Mission:** *The framework is ontology-driven: classes, relationships, properties and instances that
today live in prose or in source code are exported to the ontology, the governance model is
expressed as ontology rather than as documentation, and rule execution moves from prose and code to
the ontology layer.*

**Outcome:** `Out_Achieved` — computed by this project's own closure-readiness tool
(`backlog_lineage_compass`), not asserted. **Ontology record:** `fw:CR_OntologyDriven`, required to
exist before this outcome could be set, per `MissionClosureRequiresReportShape` (`G70`).

**Report generated:** 2026-09-04, against `backlog_framework_register_abox_v9_42_1.ttl`.

---

## 1. Measures dashboard

| Objective | Baseline | Target | Final | Status |
|---|---:|---:|---:|---|
| Governance held (0 real violations) | 0.0 | 0.0 | **0** | ✅ MET |
| Governance rulings unreachable by query | 18.0 | 0.0 | **0** | ✅ MET |
| Rules still decided in code, not ontology | 3.0 | 0.0 | **0.0** | ✅ MET |
| Tables still unexported to ontology | 23.0 | 0.0 | **0.0** | ✅ MET |
| Standard rows unchecked against ontology | 186.0 | 0.0 | **15.0** | ⚠️ Closed with a recorded reason (see below) |
| Code decisions still unexported | 3.0 | 0.0 | **0.0** | ✅ MET |
| No new classes drift | 0.0 | 0.0 | **0** | ✅ MET |
| No prose lost in conversion | 0.0 | 0.0 | **0** | ✅ MET |

**7 of 8 objectives reached target exactly.** The eighth, standard-rows-unchecked, was closed with a
real `AchievementStatus` (`Ach_Retrospective`) rather than forced to zero: a genuine structural floor
was confirmed by direct test, not argued — the same discipline `Find_G19` (below) records this
lineage learning the hard way.

**Register-wide, at closure:** 0 SHACL violations, 79 advisory warnings (the great majority reflecting
real, deliberate differences in how this project works rather than defects — investigated
individually, not assumed). All six shipped self-checks pass. 42 governance decisions exist as real,
queryable data; 33 as recorded lessons; 0 remain unaccounted-for prose.

---

## 2. History — how this lineage actually unfolded

This lineage carried the framework through **69 real governance rulings across the `G1`–`G70`
range** (`G25` was never used), of which 42 resolved to real, checkable rules and 33 to recorded
lessons with no single enforcing rule to attach to (0 of the 51 rulings currently expressed as prose
headings remain unaccounted for — every one carries either a rule or a recorded finding). A
representative arc, not the full log (see `LINEAGE_OPERATING_DISCIPLINE_v41_0_0.md` for every ruling
in full):

- **Early corrections (`G19`–`G39`)** — a run of process lessons about grounding claims in real,
  re-checked data rather than assertion: floors that turned out not to be floors, evidence that
  covered more than it proved, numbers that agreed with other invented numbers.
- **Mid-lineage (`G40`–`G57`)** — real infrastructure built by ranked priority, not preference or
  sequencing convenience: severity taxonomy researched against real external standards, corrective
  actions enforced structurally, a `Spike`/`KickOff`/`Initiative` build-out each grounded in a real,
  found occasion rather than assumed absent.
- **Late lineage (`G58`–`G70`)** — the framework turned its own scrutiny on itself: autonomous
  re-measurement at checkpoints, a real regression found and honestly recorded rather than adjusted,
  a threshold replaced with evidence-based detection, a real gap between "detected" and "recorded"
  closed, a decision left unresolved for multiple releases surfaced directly and finally made, and
  — closing the loop — the mechanism for recording a deliberately moved deadline widened to actually
  cover the kind of goalpost this lineage itself had quietly moved once.

---

## 3. Lessons learned

Nine real findings, cited directly rather than restated as fresh prose (full text in the register,
`fw:CR_OntologyDriven backlog:citesFinding`):

1. **A floor is measured, not argued** (`G19`) — declared three times, wrong all three; a floor with
   no named experiment is an argument.
2. **Evidence batched across criteria carries the false one** (`G21`) — one verification record
   covering five criteria let an unbuilt property pass unnoticed.
3. **A derived number must answer to what it derives from** (`G24`) — two asserted numbers agreeing
   with each other proves nothing.
4. **State is grounded in re-checked evidence, never in whether a ceremony happened** (`G33`) — moved
   twice in opposite directions, both times on the wrong test.
5. **A legacy source's silence is not a current boundary** — checking one file of an ecosystem and
   generalising from it (`G51`) is the same failure as reading one class definition in isolation.
6. **A prior "no occasion found" is re-checked, not inherited** (`G57`) — re-reading twelve
   previously-dismissed classes fresh found four real, missed occasions.
7. **A corrective action's mere existence is not a decision** (`G67`) — a real choice sat `Proposed`
   for multiple releases because its existence alone was cited as if it settled something.
8. **A claim of "final" is stale the moment it's written down** (`G68`) — a ruling describing its own
   heading count invalidated that same count by existing.
9. **Read warnings individually, not as one number** (`G69`) — a single aggregate count hid two real,
   silent mistakes a grouped total made invisible.

---

## 4. Best practices — worth repeating on purpose

Stated directly on the closure report (`fw:CR_OntologyDriven backlog:statesBestPractice`):

- **Re-verify a claim by re-running the actual check immediately before stating it** — not from
  memory of an earlier run, however recent. Every "still 0 violations" in this lineage's own history
  that skipped this step was wrong at least once.
- **When a warning count looks large, read each distinct message individually** before deciding it
  doesn't matter — a grouped number hides real bugs as easily as it hides harmless, deliberate
  differences in how the work is done.
- **Replace a fixed threshold with a real, evidence-based comparison** wherever the underlying data
  can support one — a threshold is almost always easier to game than the data it stood in for.
- **Check an "unused" concept's own real definition and this project's own real history
  individually** before dismissing it — several turned out to be already-known, already-named,
  simply not-yet-acted-on opportunities.
- **Surface an open decision directly to whoever can actually decide it** the moment it's been
  sitting for more than one release — don't keep citing its existence as if that settled anything.

---

## 5. What remains open — disclosed, not hidden by closure

Closing this mission does not mean nothing is left. Named honestly rather than swept in with the
close:

- **`Imp_RegisterPackageDecisions`** — still blocked on two external proposals this project's own
  governing session cannot resolve unilaterally.
- **Three named opportunities, identified and genuinely not pursued**: retyping the six real
  conversion epics as `Enabler` (real cost confirmed, not worth it at this scale); building a real
  workflow/transition-history apparatus (`TransitionEvent`); formally tracking this session's own
  real bugs as `Defect` records.
- **Full lineage archival was deliberately not performed as part of this closure.** Archiving means
  physically moving this lineage's own data into a separate file — a real, separate operation from
  closing the mission, left as its own future decision rather than bundled in here.

---

*Generated from `backlog_framework_register_abox_v9_42_1.ttl`, re-verified against the live register
at generation time, not recalled from memory or an earlier run.*
