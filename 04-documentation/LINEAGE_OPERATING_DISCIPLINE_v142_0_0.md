# Lineage Operating Discipline — v142.0.0

**What this is.** How a lineage is started and run, in one page. SHACL enforces; this file only tells the agent the order of work and the principles behind it. It holds no ruling text.

**Where everything else is.** Every ruling is a `GovernanceRuling` in the register (statement, enforcing shapes, source): query it, do not look for it here. Rule sets and profiles are in the register too. How each ruling came about is in `LINEAGE_RULING_NARRATIVES_v142_0_0.md`: history, read only when working on that ruling.

**Order of precedence.** The OE ceremony and OE Operating Discipline run first; a lineage grounded on unverified bytes is a lineage about nothing.

## Ceremony — before the first work item

1. **Declare the profile and level** as an owner decision with rationale, target and review date. A clean result at a low level is a narrower claim, not a better one.
2. **Build the chain as a pipeline, one commit per stage:** Mission → ScopeStatement (text, exclusions, deliverables) → Goal → Objective → Backlog. Each stage closes in its own commit and records a `StageOutput` naming the commit; the next stage consumes it. Git is the only witness of order, and it orders between commits, not within one.
3. **State the granularity** you chose and why (`LineageDepthAdvisoryShape` shows the symptom as an advisory).
4. **Decide how work reaches users:** planning event, iteration, deployment unit.

If a step cannot be completed from rules and facts, stop and state plainly what input is needed. Never backfill a bypassed chain; restart it.

## Principles (ontology-native)

- **A rule is a shape.** A lesson becomes a shape and a `GovernanceRuling` that names it. Rulings are never kept as prose. What no shape can reach is recorded as a ruling that says so.
- **Connections are links, never text.** A reference to a modelled thing is an object link.
- **Order is witnessed, not declared.** A digest computed from the finished state proves nothing about order. Checked by `backlog_lineage_order_check` in the release gate.
- **A ruling binds only work not yet started.** Lineages adopt rule sets when they open; the register adopts rule sets by owner decision (`ObligationAdoptionShape`).
- **Append, never edit.** Corrections are added with a note; history is not fabricated; a superseded item stays visible.
- **Completion is not accomplishment.** Objectives are measured; a scope has deliverables of its own (`L4MeasuredObjectiveShape`, `ClosureReportShape`); a figure that cannot fall measures nothing.
- **A tool that refuses is not thereby correct.** Check tools with fixtures whose answer is known; run at the level you enforce.
- **Publish each increment** after its gate passes. The gate is part of the release path and has a cost budget; a chain-stage release that only adds records passes the light gate, and the fifth release of a batch runs the full one (G178).
- **Simplify how a lineage is run, never the obligations it owes.**
- **Keep this file short.** It is checked against the shapes and held to a size ceiling by `backlog_lineage_discipline_check`.
