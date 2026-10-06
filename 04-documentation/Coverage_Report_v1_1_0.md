# Primary-Source Coverage Report — BP-D31 gate

**Source:** `BACKLOG_ROADMAP_STANDARD_v1_0_0.md` (Blueprint / Product Backlog / Product Roadmap
Construction), adopted 2026-07-27
**SHA-256:** `a58a6c8911b391c4e3ac45b800013ed96de964ac89ae4133057a474a43389106`
**Inventory:** `source_concept_inventory_v1_1_2.json` — 36 concepts
**Gate:** `03-tooling/backlog_coverage_gate_v1_1_1.py`, threshold 80%

## Result

| Framework version | Coverage | Verdict |
|---|---|---|
| v1.0.0 (built without the source; URL returned 404) | **8/36 = 22.2%** | FAIL |
| v1.1.0 (this release) | **36/36 = 100%** | PASS |

## Method

Concepts were enumerated per BP-D31 step 1 from the document's headings, defined terms, named
flags and enumerated rules, each recorded with its source line range. Each concept carries one or
more regex probes; a concept counts as demonstrated only when **every** probe matches in at least
one shipped framework artifact (ontologies, shapes, rules, tooling, fixtures). A concept with no
probes is not demonstrated by construction, so silence never reads as coverage. Measured with
Python 3 `re` over 20 artifacts; the gate is re-runnable and ships with the package.

## What v1.0.0 missed, and why the number was that low

v1.0.0 was generalised from an adopting project product-backlog **deposit** — the ontology derived from
this methodology — rather than from the methodology document itself. The deposit encodes the
register: items, statuses, evidence, packages, WSJF. It does not encode the methodology that
governs the register, which is most of what the source document is about. The 28 missing concepts
clustered into six areas:

1. **The blueprint layer entirely** (C01, C05-C09) — the domain model the backlog is scoped
   against, its life-cycle sweep, and the rule that a coverage gap is a defect to be written down.
2. **The second prioritisation model** (C19-C23) — launch readiness as an owner declaration, and
   R3, the arbitration that keeps it from being reconciled with throughput ranking by arithmetic.
   This is the document's own "single most expensive lesson", recurring three times before it was
   written as a rule.
3. **Binary gap discipline** (C12, C17, C33) — scored or explicitly flagged with a reason, never
   silently blank. v1.0.0 had this as an advisory note; it is now an L2 violation.
4. **Capability tagging and dependency disclosure** (C15, C16, C21, C22) — non-shippable groupings
   excluded from ranking, container scores judged rather than averaged, dependencies stated in
   prose becoming edges, and full member completion not meaning deployable.
5. **The computed report** (C04, C24, C26, C27, C34) — eight required sections, a run timestamp,
   and recommendations traceable to the run that produced them.
6. **Governance mechanics** (C25, C28, C30, C31, C35, C36) — supersession in place, Gate K version
   identity, the four-gate release check, rule provenance, and the owner/builder split.

## Honest note on what this measurement is and is not

The gate measures whether each source concept is **represented** in the framework — as vocabulary,
as a constraint, or as executable tooling. It does not measure whether each representation is the
best possible modelling of that concept, and a probe is a proxy for presence, not for quality. Two
specific weaknesses worth naming:

- `backlog:EnforcementDomain` (C05) ships as an open, unpopulated class. The source anchors this
  to a specific project's compliance-domain classification; importing that project's individuals
  would drag foreign vocabulary into a subject that must stay project-neutral, so the framework
  supplies the slot and the adopting development supplies the scheme. The positive fixture
  populates it to demonstrate use.
- C07 (checking against running code rather than titles) is represented as an assertion an item
  carries plus a constraint that the assertion must record its method. The framework cannot verify
  that the check actually happened; only the evidence bridge can, and only for evidence artifacts.

Three concepts (C10, C29, C30) are demonstrated by the package's own structure and tooling rather
than by domain vocabulary — TBox/ABox/rules separation, the priorVersion chain, and the four gates.
That is representation in the strict sense the gate measures, and it is disclosed here because a
reader could reasonably expect vocabulary and find structure instead.
