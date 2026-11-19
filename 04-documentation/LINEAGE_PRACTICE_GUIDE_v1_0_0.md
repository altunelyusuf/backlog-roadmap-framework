# Lineage Practice Guide — v1.0.0

**What this is.** What a session of any package needs to run its own lineage without asking a BRSF session. It holds no ruling text: rulings are `GovernanceRuling` records in the register (G245 records the Owner's instruction of 2026-11-18, 12:25 Istanbul, that no session should need BRSF to apply the lineage and its discipline). The order of work is in `LINEAGE_OPERATING_DISCIPLINE_v163_0_7.md`; read this guide beside it.

## Who may decide what
| Matter | Decided by | Where it is |
|---|---|---|
| Running any BRSF tool on your package's own register and lineage | You, without asking | call forms below, under "Running the tools on your own register" |
| Opening a box, refining, planning, reviewing, closing a box | You, with the box tool (`backlog_box_step`), in the order of the discipline | discipline, Ceremony |
| Raising and clearing an obstacle | You, the moment work stops | discipline 3a to 3c, `backlog_impediment` |
| Routing an instruction before any file changes | You, by the four routes | discipline 3g |
| Archiving a closed lineage | You, once the Owner has confirmed the closure and the mission outcome is set: `backlog_lineage_archive` in the next release, not inside a box | discipline 6 |
| Open items of a closed lineage | You: a PartialScopeDeclaration names the work left out of scope and why; the closure report names what was delivered and what was cancelled | closure rules below |
| A change to the discipline or its rulings | The Owner's dated ruling, recorded in the same release | discipline 3g (d) |
| A real defect in a BRSF tool | BRSF, by a handover to its inbox (`07-handover-inbox/pending/`), your own fault stated first | the BRSF repository |
| Anything no rule or fact settles | The Owner: one point at a time, with a recommendation | — |

## Running the tools on your own register
Each tool names the register in its own way; read its usage line.
- `backlog_box_step REGISTER --lineage L --prefix P open|act|freeze|close ...`, with `--brsf-root` naming the framework checkout.
- `backlog_impediment REGISTER raise|advise|clear|list ...`: the register is the first argument; the kinds, ways and roles come from the framework's published register when yours holds none.
- `backlog_criterion_resolve --register REGISTER --root PACKAGE`.
- `backlog_release_item_check PACKAGE BASELINE_TAG --register 'GLOB' --governed DIRS --changelog 'GLOB'`: quote the globs, and name the register's directory in `--governed`, or a change to it is not counted.

## Before a box
1. Groom each story before it is planned: text, value, estimate, acceptance criterion, and a task of every needed kind (analysis, design, build, verification). One "Build" task per story is wrong.
2. Write the Definition of Done for this lineage, with a check that runs for every criterion. The box tool uses the Definition of Done a story already applies and writes a generic one only for a story that applies none.
3. State each story's design concerns, or state that none applies. The box tool keeps what the story says; it adds an architecture concern only when an architecture task is planned and the story does not say none applies.
4. Read the validator's warnings, not only its violations, and answer each before opening.
5. A story is ready when its acceptance criterion exists, nothing it depends on is open, no impediment is open on it and its effort fits the box; the box tool refuses a story that is not ready and names why.
6. A story and the story it depends on go in different boxes; a box takes stories of one package.
7. Read the live files of the framework before planning. Take ordinals and identifiers from the register, never from a document.

## When a tool refuses
Read the refusal: it names the cause. Mend your own record first (a missing criterion, an open dependency, a concern statement that contradicts itself). A refusal is a rule applied, not a request to ask: satisfy the obligation in the same step, never waive, skip or defer it. When the tool is wrong for a register that is right, raise a tool-at-fault impediment with `backlog_impediment`, send BRSF the handover, and wait on the fix; do not build a substitute tool.

## During and after a box
- A defect a reviewer finds becomes an item in the running lineage, re-ranks the open items and is repaired in a box before the lineage closes.
- Each box has a fresh independent reviewer; the brief is frozen after the box opens and before the review starts, and defines defect against limit.
- Prove each repair by planting the fault in a copy and seeing a check fail.
- Run `backlog_release_item_check` in the release gate; the unplanned-work line cites a dated Owner ruling, never "None".
- Measure acceptance criteria and objectives with register-native checks and framework tools, not with a package script; `backlog_criterion_resolve --register REGISTER --root PACKAGE` reports each criterion's artefact.
- Close a fully achieved lineage with a closure report, each promised guard read again, the Owner's confirmation and the mission outcome (discipline 6). Add a PartialScopeDeclaration only when scope is left out, and a LineageSuccession only when the mission continues in a successor lineage. Read the register for its real status first.
- After each BRSF release, validate your register, its archive and every tool you use on your own register at once.

## Do not
Write your own lineage or box tooling. Measure a lineage with a package script. State a status or a rationale from memory instead of the register. Leave work stopped without an impediment.
