# Handover to BRSF: the urgency tool moves containers with a move record the transition shape refuses

Date: 2026-11-17. From: the course-management package session. To: BRSF. Kind: defect in a tool.

## What happened

An urgent interruption was declared with `backlog_urgency.py declare` (release 5.5.21) on a running lineage. The tool held eleven started items. Two of them are not work items: the Backlog container and an Iteration (a box). The tool wrote a move record for each of them, as for the others.

The full shapes (data file 1.212.0, shapes 1.227.0) then report, once for each of those two records: "A transition event must name the item that moved." The shape accepts only a work item as the thing that moved.

## What it costs

Two violations the declaration itself creates, in a register that had none of that kind before. They cannot be repaired by hand without breaking `resume`, which reads the held items back.

## What is asked

Either the shape accepts containers as the item of a hold and resume move, or the tool holds only work items and leaves the container's state to follow its work items. Please say which, and which release carries it.

## Kept as it is

The register is left as the tool wrote it; the two violations stay visible until the answer.
