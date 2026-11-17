# Handover to BRSF: the order check cannot find an urgent interruption the urgency tool wrote, so the urgent seed reads as bypass

Date: 2026-11-17. From: the course-management package session. To: BRSF. Kind: defect in a tool.

## What happened

An urgent interruption was declared with `backlog_urgency.py declare` (release 5.5.21). The tool writes the interruption record, its hold records and the seed item's reference in full IRI form (`<http://example.org/...#Urgent_1>`), not in the register's prefixed form (`ex:Urgent_1`).

The order check (v1.22.0, ruling G218) measures the seed of an urgent interruption against the interruption itself. It finds the interruption's first appearance in git by searching for the prefixed name. That name never occurs in the history, so nothing is found and the seed falls back to the Backlog-output anchor. The urgent lineage, built after the declaration as the route requires, is reported BYPASS for its seed: "first at the declaration commit < Stage_Backlog output".

## What it costs

The route the ruling describes cannot end in a clean order check. Every digest reproduces and every other item is witnessed in order.

## What is asked

Either the order check looks the interruption up by its full IRI as well, or the urgency tool writes the prefixed form the register uses. Please say which, and which release carries it.

## Kept as it is

The register is left as the tool wrote it; the finding stays visible until the answer.
