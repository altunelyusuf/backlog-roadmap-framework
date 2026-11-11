# Handover: a scope deliverable needs belongsToLineage for RNP_PKG_ORPHAN, but the Scope stage does not ask for it

**From:** the session building a book ontology (production lineage, first lineage of its register).
**To:** the BRSF session.
**Nature:** a framework finding with a reproduction. Nothing here asks BRSF to act on another package.
**Date:** 2026-11-10. Read against BRSF discipline v163.0.5, validator v1.19.0, pipeline verify v1.15.0, shapes v1.219.0.

## What happens

1. The Scope stage closes with deliverables that have a layer, a kind, a text and a area, and no `belongsToLineage`. The validator is clean, and the stage digest records them as absent (a digest counts only the subjects that belong to the lineage, `state_digest`, lines 103-105 of pipeline verify v1.15.0).
2. The Backlog stage then adds packages. `PackageTracesShape` (`RNP_PKG_ORPHAN`) requires `deliversDeliverable ?d . ?d backlog:belongsToLineage ?lin`. With the deliverables as closed, every package fails.
3. Adding `belongsToLineage` to the deliverables clears the shape and moves the Scope, Goal and Objective digests of both lineages (the deliverables become subjects of the stage). `backlog_pipeline_verify` then reports DOES NOT REPRODUCE for all closed stages that count them.

Reproduction: take any register closed through the Objective stage whose deliverables lack `belongsToLineage`; add one package with `deliversDeliverable`; validate (RNP_PKG_ORPHAN), then add the missing triple on the deliverable and run `backlog_pipeline_verify --lineage`.

## How the register handled it

The membership was added, the digests were re-recorded, and each affected output carries an appended comment that says so (the earlier values stay in the git history). This is a disclosed correction, not a silent one, but it is a closed stage moving, which the digest exists to catch.

## Why it matters

A first lineage that follows the order of the stages cannot satisfy the packages rule without moving a closed stage. The cause is that the earlier stages do not require what a later stage reads.

## Candidate remedies (BRSF decides)

1. Require `belongsToLineage` on a scope deliverable at the Scope stage (a shape, with the Scope stage's own message), so it is in the digest from the start.
2. Let `PackageTracesShape` read the deliverable's lineage through the scope statement it belongs to, so the deliverable needs no property of its own.
3. Exclude the lineage-membership property of a deliverable from the stage digest (it is annotation of an element that already exists, as the digest docstring says it should be stable under).
