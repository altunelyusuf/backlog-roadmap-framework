#!/usr/bin/env python3
"""backlog_governance_mitigations_probe v1.0.0 -- the two mechanisms of Lineage 16's last stories, each shown firing on a planted fault and silent on its twin.

  GOVMIT-S02  an item that records a start while its state is still Proposed or Ready, with no batch counter  -> ItemStartedStateStaleShape fires;
              with the state moved, with no start, or batch-tracked (the older rule owns it)                   -> silent
  GOVMIT-S03  a criterion's artefact path that leads outside the package ('..', an absolute path, a link out)    -> backlog_criterion_resolve reports it
              OUTSIDE ITS PACKAGE and does not resolve it; a path inside the package, and a named symbol in it   -> resolves
Exit 0 when every case behaves; 3 otherwise.
Usage: backlog_governance_mitigations_probe_v1_0_0.py
"""
import glob, importlib.util, os, re, sys, tempfile
from rdflib import Graph, Namespace, Literal, RDF
from rdflib.namespace import XSD

HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
B = Namespace("http://example.org/backlog#"); P = Namespace("http://example.org/probe#"); SH = Namespace("http://www.w3.org/ns/shacl#")


def latest(sub, pat):
    hits = glob.glob(os.path.join(PKG, sub, pat))
    return sorted(hits, key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]])[-1]


def fired(shapes, data, marker, focus):
    import pyshacl
    _, rg, _ = pyshacl.validate(data, shacl_graph=shapes, inference="none", advanced=True, allow_warnings=True)
    return any(rg.value(r, SH.focusNode) == focus and marker in str(rg.value(r, SH.resultMessage)) for r in rg.subjects(RDF.type, SH.ValidationResult))


def item(state, started=True, batch=False):
    g = Graph(); g.add((P.Item, RDF.type, B.Story)); g.add((P.Item, RDF.type, B.WorkItem)); g.add((P.Item, B.hasState, state))  # typed WorkItem too: the probe runs without inference
    if started:
        g.add((P.Item, B.startedAt, Literal("2026-10-07T09:00:00Z", datatype=XSD.dateTime)))
    if batch:
        g.add((P.Item, B.hasBatchSize, Literal(10))); g.add((P.Item, B.hasBatchCompleted, Literal(2)))
    return g


def main():
    shapes = Graph().parse(latest("02-shacl-safeguards", "backlog_shacl_v*.ttl"))
    M = "records a start (startedAt) but its hasState is still"
    spec = importlib.util.spec_from_file_location("cr", latest("03-tooling", "backlog_criterion_resolve_v*.py"))
    cr = importlib.util.module_from_spec(spec); spec.loader.exec_module(cr)
    results = [
        ("started, still Proposed, not batch-tracked: rule fires", fired(shapes, item(B.Proposed), M, P.Item), True),
        ("started, still Ready, not batch-tracked: rule fires", fired(shapes, item(B.Ready), M, P.Item), True),
        ("started and InProgress: rule silent", fired(shapes, item(B.InProgress), M, P.Item), False),
        ("Proposed, never started: rule silent", fired(shapes, item(B.Proposed, started=False), M, P.Item), False),
        ("started, Ready, batch-tracked (older rule owns it): silent", fired(shapes, item(B.Ready, batch=True), M, P.Item), False),
    ]
    with tempfile.TemporaryDirectory() as t:
        pkg = os.path.join(t, "pkg"); other = os.path.join(t, "other")
        os.makedirs(os.path.join(pkg, "03-tooling")); os.makedirs(other)
        open(os.path.join(pkg, "03-tooling", "tool.py"), "w").write("def Symbol():\n    pass\n")
        open(os.path.join(other, "tool.py"), "w").write("def Symbol():\n    pass\n")
        os.symlink(other, os.path.join(pkg, "link"))
        inside = "03-tooling/tool.py -- Symbol"
        results += [
            ("path inside the package: resolves", cr.resolve(inside, set(), pkg), True),
            ("path inside the package: not outside", cr.outside_package(inside, pkg), False),
            ("'..' path into a sibling package: named as outside", cr.outside_package("../other/tool.py -- Symbol", pkg), True),
            ("'..' path into a sibling package: does not resolve", cr.resolve("../other/tool.py -- Symbol", set(), pkg), False),
            ("absolute path outside: named as outside", cr.outside_package(os.path.join(other, "tool.py") + " -- Symbol", pkg), True),
            ("a link inside the package that leaves it: named as outside", cr.outside_package("link/tool.py -- Symbol", pkg), True),
            ("an IRI target is never outside", cr.outside_package("backlog:Story", pkg), False),
        ]
    bad = 0
    for label, got, want in results:
        ok = got == want; bad += not ok
        print("  %-62s %s" % (label, "ok" if ok else "FAILED (got %s)" % got))
    print("VERDICT : " + ("PASS -- every mechanism fires on its fault and is silent on its twin" if not bad else "FAIL -- %d case(s) did not discriminate" % bad))
    return 0 if not bad else 3


if __name__ == "__main__":
    sys.exit(main())
