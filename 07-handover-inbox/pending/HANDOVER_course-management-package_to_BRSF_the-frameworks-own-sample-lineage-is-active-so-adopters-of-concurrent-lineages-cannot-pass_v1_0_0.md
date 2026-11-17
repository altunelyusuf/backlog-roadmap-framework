# Handover to BRSF: the framework's own sample lineage is active, so a lineage adopting the concurrent-lineages rule set cannot pass

Date: 2026-11-17. From: the course-management package session. To: BRSF. Kind: defect in framework data.

## What happened

A register opened an urgent lineage under the standard profile, which adopts the concurrent-lineages rule set (`RS_ConcurrentLineages`). The urgent lineage is connected to the interrupted one: the interruption names its seed item, and a held item depends on its story.

The full shapes (data file 1.212.0, shapes 1.227.0) still report, on the urgent lineage: "this lineage and another are both active and nothing connects them". The other lineage is not the interrupted one. It is `L_ImpedimentsKnown`, a sample lineage in the framework's own data file with status rank 6. Any adopter of the rule set is checked against it, because the data file is loaded with every register.

## What it costs

One violation on every lineage that adopts the rule set, whatever its own connections. The only way to avoid it is not to adopt the rule set.

## What is asked

Either the sample lineage leaves the active statuses in the data file, or the shape considers only lineages of the register being checked. Please say which, and which release carries it.

## Kept as it is

The register is left as it is; the violation stays visible until the answer.
