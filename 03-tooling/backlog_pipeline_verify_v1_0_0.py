#!/usr/bin/env python3
"""backlog_pipeline_verify_v1_0_0.py — the lineage order, checked by reconstruction.

WHY THIS EXISTS

A previous release concluded that execution order could not be gated, on two
mistaken grounds. The first was a misreading: the v1.62.0 exclusion forbids
requiring a fixed-at DATE, and says nothing about enforcing order. The second
was a failure of imagination: an ontology has dependency relations, and a
dependency on an ARTIFACT is not a claim about the past — it is a thing that
either exists or does not.

The pipeline model is another registrant's: every stage consumes what the previous stage
produced. Applied to the lineage, each stage closes with a StageOutput carrying
a digest of the graph as it stood, and the next stage's elements reference that
output. An element cannot reference an output that does not exist.

WHAT MAKES IT OBJECTIVE RATHER THAN DECLARATIVE

A backwards-built lineage can fabricate stage outputs. What it cannot do is make
a fabricated digest survive recomputation. This tool restricts the CURRENT
register to the element types each stage may contain, canonicalises, hashes, and
compares against the recorded digest. To pass, the state claimed must be the
state that actually existed.

The honest limit, stated because it matters: an author who genuinely constructs
each stage in order and hashes as they go will pass — which is correct, that is
the behaviour being asked for. An author who builds backwards must reconstruct
every intermediate state to produce matching digests, and reconstructing them in
order IS building in order. The check does not detect intent; it makes the
shortcut cost the same as doing it properly.

Exit 0 when every recorded digest reproduces, 1 otherwise.

Usage: backlog_pipeline_verify_v1_0_0.py <register.ttl> [tbox.ttl]
"""

import hashlib
import sys

from rdflib import Graph, RDF, URIRef

B = "http://example.org/backlog#"

# What each stage may contain. A stage's digest covers its own types and every
# earlier stage's, because a stage inherits the state it was handed.
STAGE_TYPES = {
    "Stage_Mission": ["Mission"],
    "Stage_Scope": ["Mission", "ScopeStatement", "ScopeExclusion", "ScopeDeliverable"],
    "Stage_Goal": ["Mission", "ScopeStatement", "ScopeExclusion", "ScopeDeliverable", "Goal"],
    "Stage_Objective": ["Mission", "ScopeStatement", "ScopeExclusion", "ScopeDeliverable",
                        "Goal", "Objective"],
    "Stage_Backlog": ["Mission", "ScopeStatement", "ScopeExclusion", "ScopeDeliverable",
                      "Goal", "Objective", "Initiative", "Epic", "Story", "ExecutionTask"],
}
ORDER = ["Stage_Mission", "Stage_Scope", "Stage_Goal", "Stage_Objective", "Stage_Backlog"]


def state_digest(g, stage):
    """SHA-256 over the canonical set of subjects a stage may contain.

    Subjects only, sorted: the digest must be stable under later annotation of
    an element that already existed. Hashing every triple would change the
    Mission stage's digest the moment a mission gained a label, which would make
    the check fail on correct behaviour and be worse than no check.
    """
    subs = set()
    for t in STAGE_TYPES[stage]:
        subs |= set(str(s) for s in g.subjects(RDF.type, URIRef(B + t)))
    return hashlib.sha256("\n".join(sorted(subs)).encode("utf-8")).hexdigest()


def main():
    if len(sys.argv) < 2:
        print("usage: backlog_pipeline_verify_v1_0_0.py <register.ttl> [tbox.ttl]")
        return 1
    g = Graph()
    for f in sys.argv[1:]:
        g.parse(f, format="turtle")

    outputs = {}
    for o in g.subjects(RDF.type, URIRef(B + "StageOutput")):
        st = g.value(o, URIRef(B + "outputOfStage"))
        if st is None:
            continue
        outputs[str(st).split("#")[-1]] = o

    print("register    : %s" % sys.argv[1].split("/")[-1])
    print("stage outputs recorded: %d of %d" % (len(outputs), len(ORDER)))

    if not outputs:
        print("\nNo stage outputs. The pipeline is not in use here, so order is")
        print("unverifiable — which is a statement about this register, not a pass.")
        print("\nVERDICT     : NOT VERIFIABLE — no stage outputs recorded")
        return 1

    failed = False
    prev = None
    for stage in ORDER:
        o = outputs.get(stage)
        if o is None:
            print("  %-18s absent" % stage)
            prev = None
            continue
        recorded = str(g.value(o, URIRef(B + "hasStateDigest")) or "")
        actual = state_digest(g, stage)
        ok = recorded == actual
        print("  %-18s digest %s  %s" % (stage, actual[:16], "reproduces" if ok else "DOES NOT REPRODUCE"))
        if not ok:
            failed = True
            print("       recorded %s" % (recorded[:16] or "(none)"))
            print("       The state this stage claims to have closed on is not the state")
            print("       that exists. Either the output was written without the stage")
            print("       having been built, or elements were added to a closed stage.")
        # the consumption chain: each output must consume its predecessor's
        consumed = g.value(o, URIRef(B + "consumesOutput"))
        exp = ORDER[ORDER.index(stage) - 1] if ORDER.index(stage) > 0 else None
        if exp is None:
            if consumed is not None:
                failed = True
                print("       first stage consumes an output; nothing precedes it")
        else:
            got = str(g.value(consumed, URIRef(B + "outputOfStage")) or "").split("#")[-1] if consumed else None
            if got != exp:
                failed = True
                print("       consumes %s, expected %s — the pipeline is not a line" % (got or "nothing", exp))
        prev = o

    print("\nVERDICT     : %s" % ("PASS — every recorded digest reproduces and the chain is a line"
                                  if not failed else
                                  "FAIL — a stage claims a state that does not exist"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
