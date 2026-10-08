#!/usr/bin/env python3
"""backlog_package_activation_drift_classifier v1.0.0 -- the owner's ruling (2026-10-08) on the adopting project's package-
activation handover: a dependent package should not be activated before what it depends on is resolved; correct
planning should make that unreachable; if it IS reached, that is a drift, and a root-cause classification should
run -- not a per-instance decision -- before any remedy.

Detection is PackageActivationOrderAdvisoryShape (backlog_shacl, FM_PackageActivationDrift): fires on a Package
whose derivedState is InProgress/Done while a package it containerDependsOn is neither Done nor Cancelled. This
tool runs AFTER that advisory has already identified a drifted package, and answers the question the owner asked
next: which case produced it.

Classified here (the one case the owner named explicitly, 2026-10-08): "package scope planning, i.e. a pre-PBI
is added to a later package" -- a real member-level dependsOn edge exists from an item in the drifted (already-
active) package to an item in the still-open dependency package, AND that dependency package's own planned
start (earliest targetsIteration -> iterationStart) is no earlier than the drifted package's -- i.e. the
prerequisite was scheduled to arrive no sooner than the work that needs it, not before it. Remedy for this case,
per the owner's ruling: dissolve and repack the two packages so the prerequisite lands in a package sequenced
before its dependents.

Any flagged package whose real dependsOn basis does not fit this signature is reported UNCLASSIFIED, by design:
the owner has stated other cases exist with their own clear methods, not yet in this tool's hands, and this
probe does not guess at them.

Usage: backlog_package_activation_drift_classifier_v1_0_0.py REGISTER.ttl [REGISTER2.ttl ...]
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
    basis = dependency_basis(g, drifted, dependency)
    if not basis:
        return "UNCLASSIFIED", "no real member-level dependsOn edge found backing the containerDependsOn edge -- the advisory's own precondition for a real (non-phantom) dependency is not met by this tool's own check either; verify ContainerLinkageShape's own finding before trusting this containerDependsOn edge at all."
    s_drifted, s_dependency = earliest_start(g, drifted), earliest_start(g, dependency)
    if s_drifted is not None and s_dependency is not None and s_dependency >= s_drifted:
        names = ", ".join("%s -> %s" % (label(g, a), label(g, b)) for a, b in basis)
        return "PackageScopePlanning", (
            "a real dependency basis exists (%s), and the dependency package's own earliest planned start "
            "(%s) is not before the drifted package's (%s) -- the prerequisite was scheduled to arrive no "
            "sooner than the work that needs it. Remedy (owner's ruling): dissolve and repack so the "
            "prerequisite item moves into a package sequenced before its dependents." % (names, s_dependency, s_drifted))
    return "UNCLASSIFIED", (
        "a real dependency basis exists, but it does not fit the one named case's timing signature "
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
