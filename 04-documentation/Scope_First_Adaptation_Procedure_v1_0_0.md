# Adapting a lineage built scope-last — v1.0.0

For a lineage whose `ScopeStatement` points at its objectives via `scopeRealizesObjective`. That
direction records that the boundary was drawn **after** the objectives existed, and it is an accurate
record of how the work went. This describes what to do about it.

---

## What is wrong, and what is not

Nothing in the data is wrong. The lineage validates, the links are correct, and the order it records
is the order it was built in.

What is weak is one specific thing: **that boundary has never refused anything, and cannot.** It was
drawn around work already decided, so every objective inside it is inside by construction. The scope
reads like a constraint and has never functioned as one.

The evidence for this is usually easy to find in your own register. Count the objectives ever
declared, and count the ones the scope turned away. If the second number is zero and the scope has
been amended more than once, the boundary was catching up rather than constraining.

---

## What NOT to do

**Do not re-point the existing links.** Replacing `scopeRealizesObjective` with `fillsScope` on a
lineage that already has objectives produces a boundary derived from those objectives — which is
precisely the self-confirming scope the change exists to prevent, now wearing the label of a
scope-first one. The links would say the scope came first. It did not.

**Do not rewrite the scope text.** Rewording a boundary to fit work already underway is the same
error in prose.

**Do not backfill dates.** They would assert an order that was never followed, and no reader can
check them.

A lineage that honestly records scope-last is more useful than one that falsely records scope-first.
The advisory that reports it is a description, not a defect to be silenced.

---

## What to do instead: adapt at the next increment boundary

The order is a property of **when things were written**, so it can only be fixed going forward. The
procedure is to leave the past alone and change the next one.

**1. Let the existing scope close.** Its objectives run to their outcomes as they are. Do not extend
it to cover new work — extending is what produced the pattern.

**2. Before writing any goal for the next increment, write its scope.** The boundary text and its
exclusions, fixed. This is the only step that matters; everything else follows from it.

**3. Write the exclusions properly.** An exclusion is what makes a boundary capable of refusing. Name
the things you are deliberately not doing and why. A scope with an inside and no outside has not been
drawn.

**4. Then write goals and objectives, and link each objective with `fillsScope`.** The link is
assertable only because the scope already exists — that is what records the order. If you find
yourself wanting to widen the scope to fit a goal you have just written, that is the boundary doing
its job. Either the goal is out, or the scope was wrong and you change it deliberately with a
`ScopeChange` that says so.

**5. Leave the old scope's links exactly as they are.** Two scopes in one register, one recording
each order, is not an inconsistency. It is the history.

---

## What the suite will tell you

- `LegacyOrderAdvisoryShape` — advisory, at every level. Reports a scope that points at its
  objectives. Expected on any lineage built before this change; it does not go away and is not
  supposed to.
- `ScopeFirstOrderShape` — violation, **L4 only**. An objective that names no scope it fills. A
  lineage that has not adapted should not declare L4 for that increment; declaring a lower level and
  saying why is the honest move.
- `MixedOrderShape` — violation, **all levels**. A scope and an objective pointing at each other.
  This is the shape that catches a re-pointing done in place: assert both and the lineage records no
  order at all, which is worse than recording the old one.

---

## If you are adapting a register with several scopes

Take them one at a time, at each one's own next increment. There is no batch conversion, because
there is nothing to convert — the property being changed is the order of authorship, and that only
exists in the moment of writing.
