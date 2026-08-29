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

def resolve(target, graph_subjects, pkg, reg_graph=None):
    if target.startswith("backlog:") or target.startswith("http"):
        iri = target.replace("backlog:", "http://example.org/backlog#")
        if iri not in graph_subjects:
            return False
        # #3 of the mitigation plan. A criterion naming a PROPERTY resolved
        # true the moment the property was declared in the TBox, whether or
        # not anyone had ever used it — AC_S_Tables_B3 named
        # bridgeCoversEvidence, the property existed, and the four
        # statements it was meant to carry did not. Now checked directly:
        # a property target must have at least one real triple using it in
        # the register, or the resolution is a schema check wearing a data
        # check's clothes.
        if reg_graph is not None:
            from rdflib import URIRef, RDF
            OWL = URIRef("http://www.w3.org/2002/07/owl#")
            is_property = any(True for t in (URIRef(str(OWL)+"ObjectProperty"),
                                              URIRef(str(OWL)+"DatatypeProperty"))
                               for _ in reg_graph.triples((URIRef(iri), RDF.type, t)))
            if is_property:
                has_use = any(True for _ in reg_graph.triples((None, URIRef(iri), None)))
                if not has_use:
                    return False
        return True
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
    # #3 of the mitigation plan: the strengthened "is this property actually
    # used" check produced a false positive on hasExpectedPolarity, whose own
    # definition says it lives on FIXTURES, not the register. A use-check
    # that does not load the population a property is documented to inhabit
    # reproduces exactly the false confidence this check exists to remove,
    # one layer along. Fixtures are loaded into the same graph for the test.
    for fx in sorted(glob.glob(os.path.join(pkg, "03-tooling", "fixtures", "*.ttl"))):
        try:
            g.parse(fx, format="turtle")
        except Exception:
            pass
    subjects = {str(s) for s in set(g.subjects())}
    named = unresolved = 0
    for ac, _, target in g.triples((None, B.satisfiedByArtifact, None)):
        named += 1
        if not resolve(str(target), subjects, pkg, reg_graph=g):
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
