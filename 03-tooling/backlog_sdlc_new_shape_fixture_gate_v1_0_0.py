#!/usr/bin/env python3
"""backlog_sdlc_new_shape_fixture_gate v1.0.0 -- SDLC-S05.

Exists because "the count of unproven obligation shapes is zero" was a claim nobody re-checked
after the count was first taken (SDLC-S05's own rationale said zero; a direct count on 2026-09-14
found three: StageOutputShape, SingleCommitLineageShape, StageOrderWitnessShape). That gap predates
this gate and is not what this gate closes -- its own acceptance criterion scopes it to a NEW shape,
not the existing suite, so retrofitting the three pre-existing gaps is real, separate, undecided
scope (recorded, not silently absorbed here).

What this checks: every sh:NodeShape in the current shapes file whose sh:targetClass is
backlog:StageObligation or backlog:StageOutput, that is NOT present (by name) in the shapes file at
the given prior git ref, must carry backlog:provenByFixture. Absence of the check at that ref is
what makes a shape "new" here -- not its own declared version comment, which is prose and can drift.

Usage: backlog_sdlc_new_shape_fixture_gate_v1_0_0.py <shapes_file> <prior_git_ref>
Exit 0 and prints PASS, or exit 1 and names every newly-added, unfixtured shape.
"""
import re
import subprocess
import sys

TARGETS = ("backlog:StageObligation", "backlog:StageOutput")


def shape_blocks(text):
    """Name -> body, for every `backlog:<Name> a sh:NodeShape ...` block."""
    parts = re.split(r"\nbacklog:(\w+) a sh:NodeShape", text)
    out = {}
    for i in range(1, len(parts), 2):
        out[parts[i]] = parts[i + 1]
    return out


def targeted_shapes(blocks):
    return {
        name: body
        for name, body in blocks.items()
        if any(f"sh:targetClass {t}" in body for t in TARGETS)
    }


def main():
    if len(sys.argv) != 3:
        print("usage: backlog_sdlc_new_shape_fixture_gate_v1_0_0.py <shapes_file> <prior_git_ref>")
        return 2
    shapes_path, prior_ref = sys.argv[1], sys.argv[2]

    current_text = open(shapes_path, encoding="utf-8").read()
    current = targeted_shapes(shape_blocks(current_text))

    try:
        prior_text = subprocess.run(
            ["git", "show", f"{prior_ref}:{shapes_path}"],
            capture_output=True, text=True, check=True, cwd="."
        ).stdout
        prior_names = set(shape_blocks(prior_text).keys())
    except subprocess.CalledProcessError:
        # No prior ref reachable (e.g. shapes file didn't exist there) -- treat everything as new.
        prior_names = set()

    new_and_unfixtured = [
        name for name, body in current.items()
        if name not in prior_names and "provenByFixture" not in body
    ]

    if new_and_unfixtured:
        print("FAIL: new StageObligation/StageOutput shape(s) with no provenByFixture:")
        for name in new_and_unfixtured:
            print(f"  - {name}")
        return 1

    print(f"PASS: {len(current)} shape(s) checked against {prior_ref}, no new unfixtured shape.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
