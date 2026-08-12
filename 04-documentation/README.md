# Backlog & Roadmap Semantic Framework — `backlog-roadmap-framework` v1.25.0

An ontology-based, project-independent framework for governing backlogs and roadmaps, so that
scope, progress, completion evidence and "what's next" are machine-checkable facts rather than
prose that drifts. Generalised from an adopting project's product-backlog deposit
  backlog_abox_v1_1_0.ttl                      framework individuals: methods, DoD, sections, gates, rules
  backlog_alignment_productbacklog_v1_0_0.ttl  optional alignment to product-backlog 1.3.0
02-shacl-safeguards/
  backlog_shacl_v1_1_0.ttl                     constraints, tiered L1/L2/L3 + advisory
  backlog_rules_v1_1_0.ttl                     SHACL-AF derivations + R3/R4 + next-item query
03-tooling/
  backlog_validate_v1_4_0.py                   validator + Gate K (--gate-k), --next selection
  backlog_roadmap_report_v1_5_0.py             the computed roadmap: 8 sections, both NEXT answers
  backlog_coverage_gate_v1_1_1.py              BP-D31 primary-source concept coverage
  backlog_evidence_bridge_v1_0_0.py            the only component allowed to assert verification
  backlog_registration_readiness_v1_2_0.py     ORCP pre-submission controls (11, all recomputed)
  backlog_package_check_v1_0_0.py              register package vs the pack's own naming conventions
  backlog_doc_coverage_gate_v1_2_0.py          every TBox class named in the standard; no restated measurements
  backlog_release_metrics_v1_1_0.py            generates RELEASE_METRICS.txt; changelog figures are quoted from it
  backlog_repoint_v1_1_0.py                    corpus-wide rename; historical records excluded by class
  backlog_quality_assessment_v1_0_0.py         nine OntoQA structural metrics, computed not asserted
  backlog_gate_v1_1_17.sh                       four-gate release check (0/P/K/R) + coverage, self-proving
  fixtures/                                    positive, negative, R3 disagreement, and the adversarial random register
06-package-provenance/
  backlog_staging_declaration_v1_1_1.ttl       BP-D15 staging declaration, rename record, retired name
  registration_intent_v1_5_0.ttl               ORCP Phase A facet intents + round records (6)
  backlog_framework_round6_response_v1_0_0.md  findings fixed + one clarification
  backlog_framework_bpd46_citation_note_v1_0_0.md  non-blocking finding on a citation in the ruling
  backlog_framework_phase_d_reraise_cover_note_v1_0_0.md  one-page re-raise of the open ask
  backlog_framework_register_data_convention_proposal_v1_0_0.md  Phase-D proposal to OEE
  independent_package_naming_proposal_v1_0_0.ttl  proposed convention for OE-governed independent packages
04-documentation/
  BACKLOG_ROADMAP_FRAMEWORK_STANDARD_v1_32_0.md the standard: concepts, levels, adoption
  Coverage_Report_v1_1_0.md                    BP-D31 measurement: 22.2% at v1.0.0 -> 100% at v1.1.0
  CHANGELOG_v1_25_0.md                          what changed and what incident triggered it
  Naming_Decision_Record_v1_0_1.md             why the package is named what it is, and the L-88 scrub record
  Concept_Completeness_Audit_v1_0_0.md         20 concepts x vocabulary/enforcement/demonstration
  Linkage_Audit_v1_0_0.md                      are the concepts connected, and is the connection enforced
  Agile_FitGap_Analysis_v1_0_0.md              fit-gap vs the agile literature, with verified references
  Falsifiability_Audit_v1_0_0.md               can a register be wrong? the adversarial test and the fix
  Registration_Controls_v1_0_0.md              ORCP clause -> executable control map
  OE_Registration_Readiness_Assessment_v1_0_0.md  readiness measured against the pack's physical files
  Packaging_Requirements_v1_0_0.md             what an adopter must ship, bound to OE configuration rules

  Mapping_ProductBacklog_To_Backlog_v1_0_0.md  term-by-term mapping + migration queries
  Discipline_Ceremony_Record_v1_0_0.md                 governing BP/L with verbatim definitions
  Discipline_Ceremony_Record_Addendum_v1_1_0.md        ceremony for the coverage-gate action
  ORCP_Submission_Backlog_v1_1_0.md            registration proposal
  source_concept_inventory_v1_1_2.json         36 source concepts with line refs and probes
05-lesson-deposits/
  backlog_framework_lesson_deposit_v1_0_0.ttl  two candidate lessons (proposal, not ratified)
MANIFEST_SHA256.txt, VERSION.txt
```

## Quick start

```bash
pip install rdflib pyshacl --break-system-packages
bash 03-tooling/backlog_gate_v1_1_17.sh                      # four gates + self-proof + coverage
bash 03-tooling/backlog_gate_v1_1_17.sh my_register.ttl      # ... plus a register
python3 03-tooling/backlog_roadmap_report_v1_5_0.py my_register.ttl
```

Read `04-documentation/BACKLOG_ROADMAP_FRAMEWORK_STANDARD_v1_32_0.md` first; section 4 is the
adoption procedure and section 9 lists what this release does and does not claim.

## Provenance (BP-D13 / BP-D14 / BP-D15)

- **Lineage:** ORIGINATION — its own scope label, its own SemVer starting at v1.0.0, not a continuation of any OE Pack lineage. Renamed from `oepack-backlog-framework` on 2026-07-27; the retired name is marked superseded in place, and no ontology identity was renumbered. See `Naming_Decision_Record_v1_0_1.md`.
- **Derived from:** an adopting project's product-backlog deposit `product_backlog_tbox_v1_3_0.ttl` (OE Pack v20.23.38) — generalised, with a term-by-term alignment. The deposit itself is unmodified.
- **Integrates into:** an OE Pack MINOR release absorbing the `backlog` subject, ruled and closed; registered in OE Pack v20.24.0. Declared machine-readably in `06-package-provenance/backlog_staging_declaration_v1_0_0.ttl` via `configuration:targetRelease`, which its own definition reserves for exactly this case.
- **Until that integration ships, this archive is the canonical form** and is usable without the OE Pack.

## Maintenance note

Corpus-wide renames go through `03-tooling/backlog_repoint_v1_1_0.py`, which excludes historical
records by file class and cannot be told not to. Per L-112 the exclusion is a property of the tool,
not of whoever remembers — a changelog entry, a metrics file, a round record or a dated assessment
states what was true at a past release, and repointing it makes the record false rather than current.

## Registration

**REGISTERED** in OE Pack v20.23.39 and **ORCP ceremony CLOSED** at v20.25.2, 2026-07-29 — token `BACKLOG-FRAMEWORK-REGISTERED`, roster
anchor `orh:Subject_backlog` (19th subject, `facetRole=registration`). Two lessons from this work
were adopted into the governed catalogue as L-107 and L-108, and the archive-naming convention this
package proposed was ratified as `configuration:IndependentPackageArchiveConvention`. Deposits are
held in `a registrant deposit`.

## Status

Registered subject; this archive remains the canonical distributable form and is usable without the OE Pack. No file in the uploaded pack was modified.
No HermiT attestation is made. The primary-source coverage gate now runs and reports 36/36 (100%);
v1.0.0 measured 22.2% against the same document, which is why this version exists.
