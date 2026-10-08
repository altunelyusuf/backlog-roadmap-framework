#!/usr/bin/env python3
"""backlog_package_activation_drift_classifier v1.1.0 -- the owner's ruling (2026-10-08) on the adopting project's package-
activation handover: a dependent package should not be activated before what it depends on is resolved; correct
planning should make that unreachable; if it IS reached, that is a drift, and a root-cause classification should
run -- not a per-instance decision -- before any remedy.

Detection is PackageActivationOrderAdvisoryShape (backlog_shacl, FM_PackageActivationDrift): fires on a Package
whose derivedState is InProgress/Done while a package it containerDependsOn is neither Done nor Cancelled. This
tool runs AFTER that advisory has already identified a drifted package, and answers the question the owner asked
next: which case produced it. Checked in this order, each on the same real member-level dependsOn edges
ContainerLinkageShape already requires as the dependency's basis:

1. **MistakenDependency** (owner, 2026-10-08): "maybe there is no reason but mistakenly a dependency is set
   between the packages." No real dependsOn edge exists in EITHER direction between the two packages' members --
   the containerDependsOn edge has no basis at all. Remedy: remove the containerDependsOn edge, then re-run the
   order check / start gate to see whether a replan is now needed.
2. **WrongDirection** (owner, 2026-10-08): "or direction of the link is incorrect." No real dependsOn edge runs
   from the drifted (dependent) package to the still-open one, but a real edge runs the OTHER way -- an item in
   the still-open package actually depends on an item in the already-active one. The containerDependsOn edge
   points backwards relative to its own real basis. Remedy: flip the containerDependsOn edge (and the two
   packages' position in the lineage/roadmap) to match the real, evidenced direction.
3. **PackageScopePlanning** (owner, 2026-10-08): "a pre-PBI is added to a later package." A real dependsOn edge
   runs the claimed direction (drifted package's member depends on the still-open package's member), AND the
   still-open package's own earliest planned start (targetsIteration -> iterationStart) is no earlier than the
   drifted package's own -- the prerequisite was scheduled to arrive no sooner than the work that needs it.
   Remedy: dissolve and repack so the prerequisite lands in a package sequenced before its dependents.

A real edge runs the claimed direction, but the timing signature does not match case 3, is reported
UNCLASSIFIED: the owner has said other cases exist beyond these three with their own clear methods; this tool
does not guess at them, and "maybe you can find similar cases" (2026-10-08) is answered in the changelog entry,
not invented here as a fourth code path without a named method behind it.

Usage: backlog_package_activation_drift_classifier_v1_1_0.py REGISTER.ttl [REGISTER2.ttl ...]
Exit 0 and prints one block per drifted package (classified or not); exit 0 with "no drift found" if the
advisory shape finds nothing on this register; exit 2 on a file/parse error.
"""
import sys
from rdflib import Graph, Namespace, URIRef

BL = Namespace("http://example.org/backlog#")


def label(g, n):
    if not isinstance(n, URIRef):
        return str(n)
    s = str(n)
    frag = s.split("#")[-1] if "#" in s else s.rsplit("/", 1)[-1]
    lbl = g.value(n, Namespace("http://www.w3.org/2000/01/rdf-schema#").label)
    return "%s (%s)" % (frag, lbl) if lbl else frag


def derived_states(g):
    """Reproduces R1a/R1b/R1c directly (this tool does not require a SHACL engine): a container's derivedState
    is a pure function of its own members' hasState, exactly as backlog:ContainerStateRule defines it."""
    states = {}
    containers = set(g.subjects(BL.containerDependsOn, None)) | set(g.objects(None, BL.containerDependsOn))
    for c in containers:
        members = [m for m in g.subjects(BL.memberOfContainer, c)]
        member_states = [g.value(m, BL.hasState) for m in members]
        member_states = [s for s in member_states if s is not None]
        if not member_states:
            continue
        if all(s in (BL.Done, BL.Cancelled) for s in member_states) and any(s == BL.Done for s in member_states):
            states[c] = BL.Done
        elif any(s in (BL.InProgress, BL.Done) for s in member_states) and any(s not in (BL.Done, BL.Cancelled) for s in member_states):
            states[c] = BL.InProgress
        else:
            states[c] = BL.Proposed
    return states


def earliest_start(g, pkg):
    starts = []
    for it in g.objects(pkg, BL.targetsIteration):
        s = g.value(it, BL.iterationStart)
        if s is not None:
            starts.append(str(s))
    return min(starts) if starts else None


def dependency_basis(g, dependent_pkg, dependency_pkg):
    """A real member-level dependsOn edge from an item in dependent_pkg to an item in dependency_pkg (the basis
    ContainerLinkageShape already requires to exist for the containerDependsOn edge to be real, not a phantom)."""
    out = []
    for item in g.subjects(BL.memberOfContainer, dependent_pkg):
        for target in g.objects(item, BL.dependsOn):
            if (target, BL.memberOfContainer, dependency_pkg) in g:
                out.append((item, target))
    return out


def classify(g, drifted, dependency):
    forward = dependency_basis(g, drifted, dependency)
    reverse = dependency_basis(g, dependency, drifted)

    if not forward and not reverse:
        return "MistakenDependency", (
            "no real member-level dependsOn edge exists between these two packages in EITHER direction -- the "
            "containerDependsOn edge has no basis at all. Remedy (owner, 2026-10-08): remove the containerDependsOn "
            "edge, then re-run the order check / start gate to see whether a replan is now needed.")

    if not forward and reverse:
        names = ", ".join("%s -> %s" % (label(g, a), label(g, b)) for a, b in reverse)
        return "WrongDirection", (
            "no real dependsOn edge runs from the drifted package to the still-open one, but a real edge runs "
            "the OTHER way (%s) -- the containerDependsOn edge points backwards relative to its own evidenced "
            "basis. Remedy (owner, 2026-10-08): flip the containerDependsOn edge (and the two packages' position "
            "in the lineage/roadmap) to match the real direction." % names)

    s_drifted, s_dependency = earliest_start(g, drifted), earliest_start(g, dependency)
    if s_drifted is not None and s_dependency is not None and s_dependency >= s_drifted:
        names = ", ".join("%s -> %s" % (label(g, a), label(g, b)) for a, b in forward)
        return "PackageScopePlanning", (
            "a real dependency basis exists (%s), and the dependency package's own earliest planned start "
            "(%s) is not before the drifted package's (%s) -- the prerequisite was scheduled to arrive no "
            "sooner than the work that needs it. Remedy (owner's ruling): dissolve and repack so the "
            "prerequisite item moves into a package sequenced before its dependents." % (names, s_dependency, s_drifted))
    return "UNCLASSIFIED", (
        "a real dependency basis exists in the claimed direction, but it does not fit case 3's timing signature "
        "(dependency start=%s, drifted start=%s) -- this may be one of the owner's other named cases, not yet "
        "built into this tool." % (s_dependency, s_drifted))


def main(argv):
    if not argv:
        print(__doc__); return 2
    g = Graph()
    for p in argv:
        try:
            g.parse(p, format="turtle")
        except Exception as e:
            print("PARSE ERROR on %s: %s" % (p, e)); return 2
    states = derived_states(g)
    drifts = []
    for pkg, state in states.items():
        if state not in (BL.InProgress, BL.Done):
            continue
        for dep in g.objects(pkg, BL.containerDependsOn):
            dep_state = states.get(dep)
            if dep_state is not None and dep_state not in (BL.Done, BL.Cancelled):
                drifts.append((pkg, dep))
    if not drifts:
        print("no drift found: no Package is InProgress/Done while a containerDependsOn target is open")
        return 0
    for pkg, dep in drifts:
        verdict, reason = classify(g, pkg, dep)
        print("DRIFT: %s depends on %s (still %s)" % (label(g, pkg), label(g, dep), label(g, states[dep])))
        print("  classification: %s" % verdict)
        print("  %s" % reason)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
