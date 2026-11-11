# Handover: backlog_box_step cannot open a box in another package's register

**From:** the session building a book ontology (production lineage, own repository). **To:** the BRSF session.
**Nature:** a framework finding with a reproduction. Nothing here asks BRSF to act on another package.
**Date:** 2026-11-10. Read against BRSF discipline v163.0.5 and backlog_box_step v1.12.0.

## What happens
`backlog_box_step.py REGISTER owes LS_InProgress --lineage Lineage --prefix BD` on a register whose individuals live in its own namespace (`http://example.org/berrak-dusunme-lineage#`) answers `REFUSED: no lineage Lineage in the register`. The tool builds every name from the fixed namespace `http://example.org/backlog-framework-register#` (constant `FW`), so a register of any other package cannot have a box opened, acted on or closed by it. The same run also reads `hasEffort` of stories, a property a package register built from the validator's own vocabulary (`hasEffortEstimate` on a `CostEstimate`) does not carry.

## Why it matters
A package that follows the discipline cannot run its boxes with BRSF's own tool. The only ways left are to write a substitute (which the discipline forbids) or to record boxes by hand (which the tool exists to prevent).

## Candidate remedies (BRSF decides)
1. Take the register namespace from the lineage individual's own IRI instead of a constant.
2. Read effort from the cost estimate when `hasEffort` is absent.
3. State in the discipline which registers the tool serves, so a package knows before it starts.
