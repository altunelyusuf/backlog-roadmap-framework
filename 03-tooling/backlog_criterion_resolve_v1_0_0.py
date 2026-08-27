#!/usr/bin/env python3
"""backlog_criterion_resolve_v1_0_0.py — does the thing a criterion names exist?

Built after a story was closed with its work undone. EP_RuleExec_S1 specified an
expected-polarity property on every fixture and a gate reading it instead of the
filename. The story was Done, had a test case, test data, a task and evidence.
The property did not exist.

Every clause in the suite was satisfied. None asked whether the thing existed,
because one evidence record attested five criteria across three stories and
described the iteration as a whole.

This resolves each criterion's satisfiedByArtifact independently:

  backlog:Something       -> must be a subject in the shipped TBox or register
  path/to/file.py         -> must exist
  path/to/file.py#symbol  -> must exist AND contain the symbol

Reports every criterion it cannot resolve. Exit 1 under --strict.
"""
import sys, os, glob

def resolve(target, graph_subjects, pkg):
    if target.startswith("backlog:") or target.startswith("http"):
        iri = target.replace("backlog:", "http://example.org/backlog#")
        return iri in graph_subjects
    path, _, symbol = target.partition("#")
    full = os.path.join(pkg, path)
    hits = glob.glob(full) or glob.glob(full.replace(".py", "_v*.py"))
    if not hits:
        # A versioned artefact cited at the version current when the criterion
        # closed. The file is superseded, not missing: backlog_tbox_v1_29_0.ttl
        # became v1.53.0 through releases that carried its content forward.
        # Reporting it unresolved would say the work vanished when it was
        # only renamed — and rewriting the citation to the current version
        # would erase which version actually verified it.
        import re as _re
        generic = _re.sub(r"_v[\d_]+(\.\w+)$", r"_v*\1", path)
        if generic != path:
            hits = glob.glob(os.path.join(pkg, generic))
        if not hits:
            return False
    if not symbol:
        return True
    return any(symbol in open(h, encoding="utf-8", errors="ignore").read()
               for h in hits)

def main():
    strict = "--strict" in sys.argv
    from rdflib import Graph, Namespace
    B = Namespace("http://example.org/backlog#")
    here = os.path.dirname(os.path.abspath(__file__))
    pkg = os.path.dirname(here)
    g = Graph()
    for pat in ("01-ontologies/backlog_tbox_v*.ttl",
                "01-ontologies/backlog_framework_register_abox_v*.ttl"):
        g.parse(sorted(glob.glob(os.path.join(pkg, pat)))[-1], format="turtle")
    subjects = {str(s) for s in set(g.subjects())}
    named = unresolved = 0
    for ac, _, target in g.triples((None, B.satisfiedByArtifact, None)):
        named += 1
        if not resolve(str(target), subjects, pkg):
            unresolved += 1
            print("   UNRESOLVED  %-30s -> %s"
                  % (str(ac).split("#")[-1], target))
    print("criteria naming an artefact : %d" % named)
    print("unresolved                  : %d" % unresolved)
    print("VERDICT     : %s" % (
        "PASS - every named artefact resolves" if not unresolved else
        "FAIL - %d criterion artefact(s) do not exist" % unresolved))
    sys.exit(1 if (unresolved and strict) else 0)

if __name__ == "__main__":
    main()
