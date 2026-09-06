# Closure Report & Dashboard — Lineage 8 (`L_ChangeDiscipline`)

**Mission:** *Scope change is a formal, enforced discipline, not an implicit one: any request to
grow or shrink a lineage's own declared scope is proposed, assessed for real impact before any
decision, decided explicitly as accepted, rejected or deferred, and recorded either way — and a
lineage's own conduct toward other, concurrently active lineages is itself a first-class, checkable
concern, not an assumed courtesy.*

**Run autonomously**, per the owner's own direct instruction, as a test drive of this framework's
full lifecycle without interruption. **Outcome:** `Out_Achieved`, computed by
`backlog_lineage_compass`, not asserted. **Ontology record:** `fw:CR_ChangeDiscipline`.

**Report generated:** 2026-09-05, against `backlog_framework_register_abox_v9_44_0.ttl`.

---

## 1. Measures dashboard

| Objective | Baseline | Target | Final | Status |
|---|---:|---:|---:|---|
| A real, typed Change Request exists and was exercised | 0 | 1 | **1** | ✅ MET |
| A real, typed Impact Assessment exists and was exercised | 0 | 1 | **1** | ✅ MET |
| Disposition covers all three real outcomes | 1 | 3 | **3** | ✅ MET |
| Existing baseline mechanism confirmed, not duplicated | 1 | 1 | **1** | ✅ MET |
| A real cross-lineage risk signal exists and fires | 0 | 1 | **1** | ✅ MET |
| This lineage's own register held 0 real violations | 0 | 0 | **0** | ✅ MET |
| No work traced to no real scope area | 0 | 0 | **0** | ✅ MET |

**All 7 of 7 objectives reached target exactly.** Register-wide at closure: 0 SHACL violations, 111
advisory warnings. All six shipped self-checks pass. Doc-coverage gate passes.

---

## 2. What was actually built

- **`ChangeRequest`** — a real, typed request to grow or shrink a scope, existing *before* any
  decision, naming its own scope, direction and rationale.
- **`ImpactAssessment`** — a dedicated assessment produced before a request's disposition may move
  past pending, explicitly covering risk to other, active lineages.
- **`ChangeDisposition`** — the real, three-way outcome (accepted / rejected / deferred) plus the
  waiting state, closing the gap where only the accepted branch had ever left a trace.
- **Four real enforcement rules**, each proven against a dedicated adversarial fixture before being
  trusted: a request must be complete; an assessment must be complete; a disposition past pending
  needs a real assessment first; an accepted request needs a real `ScopeChange` naming it
  specifically as the request it fulfills (not merely touching the same scope — see the bug below).
- **A real cross-lineage risk signal**, surfaced as an advisory the framework does not use to veto a
  decision, only to make sure a real risk was seen.

---

## 3. Real test cases exercised

Three real decisions, not fixtures, applied against this session's own real scope:

| Request | Direction | Disposition | Why |
|---|---|---|---|
| Retroactively convert past `ScopeChange` records | Grow | **Rejected** | Directly excluded by this lineage's own scope, decided by the owner before the request was raised |
| Build a full, multi-party Change Control Board | Grow | **Deferred** | No real occasion today — this project's decisions are made by a single owner, not a board |
| Add a short guidance note for future lineages | Grow | **Accepted** | Small, real, bounded; a real `ScopeChange` records the admission |

---

## 4. A real bug found and fixed before it shipped

The first version of the "accepted request needs a `ScopeChange`" rule checked only whether *some*
`ScopeChange` touched the same scope — not whether one specifically recorded *this* request. A
second, unrelated accepted request could have silently satisfied the first one's own requirement by
coincidence. This was caught only because a dedicated, adversarial fixture was built before shipping
— the real register's own data, with one request per scope, would never have exposed it. Fixed by
adding `fulfillsRequest`, checked per request, not per scope.

---

## 5. Methodology gaps found during autonomous execution — the record you asked for

Five real gaps, logged as they occurred, each with a possible remedy for later discussion rather
than resolved unilaterally (full text in `fw:Find_AutoGap1`–`5`):

1. **A new mission has no default outcome.** The very first real violation this run hit was simply
   that `Out_InFlight` was never declared, by omission. *Possible remedy:* a rule that derives it
   automatically the moment a mission exists with none asserted — not built, since it changes
   behaviour for every lineage, not only this one.
2. **Building a goal or objective needs six to ten required properties**, discoverable only by
   hitting each one's own violation in turn, with no single place listing them up front. *Possible
   remedy:* a real introspection tool — given a class name, list everything the current rules
   require for it.
3. **A real editing mistake** (a multi-line edit deleted a subject-declaration line) was caught
   immediately by re-parsing right after — confirming the existing discipline works under real,
   unsupervised pressure. No new mechanism proposed.
4. **A real logic bug survived until adversarial testing**, not before. Confirms an existing
   practice rather than proposing a new one: a new rule needs a fixture built to attack its own
   failure mode, not only a positive case drawn from whatever the real data happens to contain.
5. **The new cross-lineage check could only be proven with a fixture**, because no second,
   genuinely active lineage exists right now to test the real, positive case against. Not a defect —
   a limitation of this exact moment, worth re-checking against real data once a second active
   lineage exists.

---

## 6. Best practices worth repeating

- Give a new mission its outcome, even the default, in the same breath as its statement.
- Re-parse and re-validate after every multi-line edit during autonomous work, not only before a
  claim is shipped.
- Build a real, adversarial fixture for any new rule before trusting it against real data — real
  data only exercises the pattern it already contains, never the failure mode a rule exists to
  prevent.

---

*Generated from `backlog_framework_register_abox_v9_44_0.ttl`, re-verified against the live register
at generation time, not recalled from memory or an earlier run.*
