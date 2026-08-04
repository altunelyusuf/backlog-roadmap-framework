# Naming Decision Record — `backlog-roadmap-framework`

**Decided:** 2026-07-27, by the package owner, from four alternatives.
**Retires:** the archive name `oepack-backlog-framework` (bundle versions 1.0.0, 1.1.0, 1.1.1).
**Adopts:** `backlog-roadmap-framework-v1_0_0.zip`.

## Why the old name was wrong

`oepack-` is not a free-choice label. `configuration:ProjectArchiveConvention` fixes it literally —
pattern `oepack-{scope}-v{M}_{m}_{p}.zip`, regex `^oepack-[a-z][a-z0-9_-]*-v\d+_\d+_\d+\.zip$`. Only
the scope segment varies. On an archive that is OE-governed but **distributed independently and not
part of any pack release**, that fixed token reads as a membership claim the artifact does not make.
The scope label was also too narrow: the package covers roadmap projection, prioritisation and
ranking arbitration as well as the backlog register.

## Alternatives considered

| Candidate | Rejected because |
|---|---|
| `oepack-backlog-roadmap-standard` | Conformant and needs no exception, but keeps the exact prefix ambiguity that prompted the review |
| `backlog-roadmap-standard` | "Standard" belongs to the owner's adopted methodology document; this package is the machine-checkable framework derived from it, and reusing the word would blur which artifact governs |
| `delivery-planning-framework` | Broadest coverage, but least discoverable for a reader who knows the work by its backlog and roadmap anchors |
| **`backlog-roadmap-framework`** | **Selected**: names both governed layers, matches the subject vocabulary and the name already used throughout the documentation, and carries no acronym requiring decoding (L-69) |

## Consequences, and the rules that decide them

**Version lineage restarts at 1.0.0 (BP-D13).** A scope label with no predecessor is an ORIGINATION,
not a continuation, and BP-D14 explicitly warns against compound labels that imply a lineage which
does not exist. The bundle therefore ships as `v1_0_0` even though its contents are those that
shipped as bundle 1.1.1 under the retired name. Maturity is recorded in the changelog, not in the
digit.

**No ontology identity is renumbered.** The subject `backlog` stays at 1.1.0, its shapes and rules
at 1.1.0, the alignment at 1.0.0, and every `owl:priorVersion` chain continues unbroken. The rename
retires an archive name and its bundle-version lineage — nothing else (L-X6: a disposition must say
exactly what it retires, what remains intact, and what becomes of the residual).

**The retired name is marked in place, not deleted.** Recorded in
`06-package-provenance/backlog_staging_declaration_v1_1_1.ttl` as a `backlog:GovernedDocument` with
`hasDocumentStatus backlog:Superseded`, `supersededBy` the new archive, and a written reason —
using this framework's own supersession vocabulary, which makes the rename a working test of that
rule rather than an assertion about it.

**The convention gap is named, not hidden.** Dropping the prefix means the archive no longer matches
`configuration:ProjectArchiveConvention`. Rather than ship a silent exception,
`06-package-provenance/independent_package_naming_proposal_v1_0_0.ttl` proposes
`IndependentPackageArchiveConvention` — identical to the existing convention in every element except
the mandatory prefix — for the OE governance session to accept, amend or reject. No pack file was
modified (L-X7).

## L-88 scoped-scrub record

Before touching anything, every distinct string containing `oepack` inside the package was
enumerated programmatically, with counts, and categorised:

| Variant | Count | Disposition |
|---|---|---|
| `oepack-parallel-integration-v1_0_1.zip` | 3 | **KEEP** — inside verbatim BP-D6/BP-D8 definitions quoted in the ceremony record |
| `oepack-{scope}-v{M}_{m}_{p}.zip` | 1 | **KEEP** — verbatim convention pattern in a quoted definition |
| `http://example.org/oepack-release-history` | 2 | **KEEP** — a real upstream ontology IRI the TBox imports |
| `oepack-full-v20_23_38.zip` | 1 | **KEEP** — the actual OE Pack bundle this session verified |
| `` `oepack-` `` (prose, changelog) | 1 | **KEEP** — the history of why the rename happened |

**The retired archive name did not occur anywhere inside the package**, so the scrub surface was the
archive filename and the top-level directory only. The historical ceremony record for v1.0.0 was
deliberately **not** rewritten: its statement that the archive followed the `oepack-` convention was
true when written, and editing a dated record to match a later decision would falsify the audit
trail rather than correct it.

Post-rename verification (L-88 step 4): every keep-token above was re-counted after the change and
all survived; the four release gates and the coverage gate were re-run.


---

## Second pass — comprehensive filename scan (bundle v1.0.1)

After the package rename, every file and directory name in the bundle was scanned
programmatically, case-insensitively, for `oe`, `ontolog`, `orcp`, `pack` and `engineering`. Seven
names matched; each was given a disposition rather than a blanket rewrite, because L-88's keep-token
classes — bibliographic citations, structural identifiers, package names, methodology descriptions —
are exactly the kind of match a blind scrub corrupts.

| Name | Token | Disposition |
|---|---|---|
| `OE_Ceremony_Record_v1_0_0.md` | OE | **RENAMED** → `Discipline_Ceremony_Record_v1_0_0.md` |
| `OE_Ceremony_Record_Addendum_v1_1_0.md` | OE | **RENAMED** → `Discipline_Ceremony_Record_Addendum_v1_1_0.md` |
| `ORCP_Submission_Backlog_v1_1_0.md` | ORCP | **KEPT** — barrier below |
| `01-ontologies/` | ontolog | **KEPT** — generic description of contents, and every tool path, the Gate P glob and the manifest resolve through it |
| `06-package-provenance/` | pack | **KEPT** — matched on "package", not "pack" as an OE token |
| `independent_package_naming_proposal_v1_0_0.ttl` | pack | **KEPT** — same false positive |
| root directory `backlog-roadmap-framework-v1_0_1` | — | already renamed in the previous pass |

**The principle applied.** A token is dropped when it is a bare *qualifier* — "OE" in
`OE_Ceremony_Record` says only "something OE-ish", which is precisely the ambiguity under review. A
token is kept when it is the *proper name of an external artifact the document addresses*. The
ceremony records lose nothing by the rename: each one now names the OE Operating Discipline v2.2.0
in its own opening lines, where the reference cannot be misread as a claim about the package.

**Barrier — `ORCP_Submission_Backlog_v1_1_0.md`.** ORCP is the Ontology Registration Conformance
Protocol, a named protocol artifact shipped in the OE Pack
(`Ontology_Registration_Conformance_Protocol_v1_0_0.md`). This document is a submission *under* that
protocol, addressed to the session that operates it. Renaming it would break the identifier a
receiving session matches on, which is a citation failure, not a cosmetic one. Kept deliberately.

**Barrier — `oe-prov:` identifiers in ontology content.** Every ontology header attributes creator,
publisher and rights-holder through `"Yusuf Altunel"` and
`"İstanbul Kültür Üniversitesi, Department of Computer Engineering"`. These are upstream IRIs owned by the OE Pack.
BP-D24 requires attribution through shared machine-linkable IRIs rather than literal strings, and
L-82 forbids re-declaring a foreign namespace's terms locally. Rewriting them would silently
de-link the package from its own provenance graph. Untouched, and not a filename matter in any case.
