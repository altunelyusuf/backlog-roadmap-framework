# Handover to BRSF: the box step tool stops on a typed effort value and on a register whose times carry no time zone

From: the session of a course-management package that runs its own delivery lineage. To: BRSF. Version 1.0.0. Date: 2026-11-12.

## What happened
The package opened its next box with `backlog_box_step` v3.0.0 (framework at commit 97a4323) on its own register. The register passes the framework's stage-digest verifier and `owes LS_InProgress` reports nothing owed. `open` then stopped twice, each time with a Python error rather than a refusal the agent can act on.

## Gaps for BRSF
1. **A typed effort value crashes `open`.** `effort_of_story` reads the story's effort with a text match and converts it with `float()`. A register that writes the value as a typed literal (`"5"^^xsd:decimal`, which is valid Turtle and in range of the property) stops with `ValueError: could not convert string to float: '"5"^^xsd:decimal'`. The framework's own register writes a bare decimal (`5.0`), so only an adopting register meets this. Requested: read the effort from the parsed graph, as `backlog_date_plan` already does, or accept a typed literal, and refuse with a message instead of a traceback.
2. **Times with and without a time zone cannot be sorted.** `cmd_baseline` calls `backlog_date_plan.samples`, which sorts every iteration's start. The package's earlier iterations record start times as local clock values without a zone (`"2026-09-24T14:35:00"^^xsd:dateTime`, valid and true to the clock), while the box the tool itself writes carries `Z`. The sort stops with `TypeError: can't compare offset-naive and offset-aware datetimes`. The same mixture is behind the advisory-looking violation "this score predates the most recent completion" (BP-D11), which fires on any register that mixes the two. Requested: normalise both kinds to one zone when comparing (treating a value without a zone as the register's declared local time, or as UTC, and saying which), in the tool and in the shape, or state in the standard that a register must use one kind and have a shape that says so before work begins.

## Why this matters
An agent following the discipline cannot open a box with the framework's tool on a register that is otherwise valid, and the only ways forward are to edit committed history (rewriting past times) or to write a substitute tool, which the discipline forbids. The package is paused at this step and has not rewritten any recorded time.

## Evidence
The package's register at its version 0.24.0, box 1, run in a scratch copy at a clean commit; both stops reproduce with the command `backlog_box_step open 1 "<title>" <goal> <story> --lineage ex:Lineage --prefix TT --brsf-root <framework>`.
