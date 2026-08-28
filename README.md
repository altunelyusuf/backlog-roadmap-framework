# Backlog & Roadmap Semantic Framework

An OWL 2 + SHACL framework that makes a product backlog and roadmap **machine-checkable** instead of
prose that drifts. Scope, progress, completion evidence and "what to do next" become facts a
validator can reject, not claims a document asserts.

## The idea in one example

A team marks a story `Done`. The framework asks: what evidence? Which acceptance criterion does that
evidence attest? Was the objective it claims to advance ever measured? If the answers aren't in the
register, validation fails — the story cannot be `Done` by assertion.

That's the whole design: **every claim a backlog makes about itself has to be checkable, or it
doesn't count.**

## Start here

1. **`04-documentation/BACKLOG_ROADMAP_FRAMEWORK_STANDARD_v1_63_0.md`** — the framework itself. §2 is
   the vocabulary, §3 the conformance levels, §4 how to adopt it.
2. **`03-tooling/fixtures/fixture_positive_v1_7_0.ttl`** — a small conformant register. Read it
   alongside §2 and the vocabulary stops being abstract.
3. **`03-tooling/fixtures/fixture_adversarial_random_v1_0_0.ttl`** — a register that is *formally
   perfect and completely meaningless*. It once passed every check. Understanding why it now fails is
   the fastest route into what the framework is actually for.

## Run it

```bash
pip install rdflib pyshacl
bash 03-tooling/backlog_gate_v1_1_26.sh          # full release gate
python3 03-tooling/backlog_validate_v1_4_0.py <your-register.ttl>
```

The gate proves itself before it certifies anything: it must pass a known-good register, **fail** a
known-bad one, and **reject** the adversarial one. If any outcome inverts it aborts, because a gate
that cannot fail verifies nothing.

## Layout

```
01-ontologies/      the vocabulary (TBox) and framework individuals (ABox)
02-shacl-safeguards/ constraints, tiered by conformance level, and SHACL-AF rules
03-tooling/         validator, gates, report generator, fixtures
04-documentation/   the standard, audits, changelog
```

## Conformance levels

**L1 Core** constrains the well-formedness of what you author — if you write an objective, it must
carry a metric, a baseline and a target. **L2** and **L3** additionally require that you author it:
evidence on completed work, traceability to objectives, coverage sweeps. Adopt the level you can
actually meet; the framework fails you against the promise you made, not one you didn't.

## For students

The interesting parts, in order: the **falsifiability** constraints (why a plan that cannot fail
cannot succeed), the **evidence binding** (why "verified" needs a tool name), and the **three-fixture
self-proof** (why a gate must be shown to fail). Each exists because a real register got past an
earlier version without them.

See `DISTRIBUTION.md` for how this public copy relates to its governed original, and `LICENSE`.
CC BY 4.0 — Copyright (c) 2025–2026 İstanbul Kültür Üniversitesi & Yusuf Altunel.
