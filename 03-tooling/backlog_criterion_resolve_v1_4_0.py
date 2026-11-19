#!/usr/bin/env python3
# v1.4.0 (Lineage 29, IK-S86): takes --register PATH and --root DIR, so a package that adopts the framework resolves the criteria of its own register against its own root. The framework T-box (beside this tool) is loaded for backlog: terms; without options the framework behaves as before.
# v1.3.0 (Lineage 16, GOVMIT-S03): an artefact path that leads outside the package is reported as OUTSIDE ITS PACKAGE, named, counted, and never resolves -- a path joined to the package root used to follow '..' or an absolute path silently, so a criterion satisfied by another package's file read as satisfied here.
# v1.2.0 (Lineage 17, OESC-S04): follows the package's new layout -- one vocabulary, one data and one shapes file per subject. The register is in the data file.
"""backlog_criterion_resolve_v1_4_0.py — does the thing a criterion names exist?

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

  --register PATH   the register to read (default: the framework's latest A-box)
  --root DIR        the package root artefact paths resolve against (default: the framework root)
A package that adopts the framework passes both; the framework T-box beside this tool supplies the backlog: terms.
"""
import sys, os, glob

def outside_package(target, pkg):
    """True when a file-path target leads outside the package (a '..' segment, an absolute path, or a link that leaves it).
    A backlog: IRI or http target names no file and is never outside. Versioned citations are judged on the path as written."""
    if target.startswith("backlog:") or target.startswith("http"):
        return False
    path = target.partition(" -- ")[0] if " -- " in target else target.partition("#")[0]
    root = os.path.realpath(pkg)
    full = os.path.realpath(os.path.join(pkg, path))
    return not (full == root or full.startswith(root + os.sep))


def resolve(target, graph_subjects, pkg, reg_graph=None):
    if outside_package(target, pkg):
        return False
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
    # Real bug found and fixed here, 2026-09-21: this package's own established convention for
    # a file-path artefact target is "path -- SymbolName" (matching how this framework's own
    # changelog entries cite shapes throughout), not a "#"-style URI fragment -- the only
    # convention this function actually implemented. Nobody had hit this before because
    # satisfiedByArtifact had never been used with a file-path target until GOVMIT-S01/S04;
    # every other resolved criterion used a backlog: IRI target instead, the first branch above.
    if " -- " in target:
        path, _, symbol = target.partition(" -- ")
    else:
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
    def opt(name):
        if name in sys.argv:
            i = sys.argv.index(name)
            if i + 1 >= len(sys.argv):
                print("%s needs a value" % name); sys.exit(2)
            return sys.argv[i + 1]
        return None
    here = os.path.dirname(os.path.abspath(__file__))
    fwroot = os.path.dirname(here)
    register = opt("--register")
    root = opt("--root")
    pkg = os.path.abspath(root) if root else fwroot
    if register and not os.path.isfile(register):
        print("register not found: %s" % register); sys.exit(2)
    if root and not os.path.isdir(pkg):
        print("root not found: %s" % pkg); sys.exit(2)
    g = Graph()
    g.parse(sorted(glob.glob(os.path.join(fwroot, "01-ontologies/backlog_tbox_v*.ttl")))[-1], format="turtle")
    regfile = register if register else sorted(glob.glob(os.path.join(fwroot, "01-ontologies/backlog_abox_v*.ttl")))[-1]
    g.parse(regfile, format="turtle")
    mine = Graph().parse(regfile, format="turtle") if register else None  # the criteria read are those of the register given, never the framework's fixtures
    # #3 of the mitigation plan: the strengthened "is this property actually
    # used" check produced a false positive on hasExpectedPolarity, whose own
    # definition says it lives on FIXTURES, not the register. A use-check
    # that does not load the population a property is documented to inhabit
    # reproduces exactly the false confidence this check exists to remove,
    # one layer along. Fixtures are loaded into the same graph for the test.
    for fx in sorted(glob.glob(os.path.join(pkg, "03-tooling", "fixtures", "*.ttl")) + (glob.glob(os.path.join(fwroot, "03-tooling", "fixtures", "*.ttl")) if pkg != fwroot else [])):
        try:
            g.parse(fx, format="turtle")
        except Exception:
            pass
    subjects = {str(s) for s in set(g.subjects())}
    named = unresolved = outside = 0
    for ac, _, target in (mine if mine is not None else g).triples((None, B.satisfiedByArtifact, None)):
        named += 1
        if outside_package(str(target), pkg):
            outside += 1; unresolved += 1
            print("   OUTSIDE ITS PACKAGE  %-30s -> %s" % (str(ac).split("#")[-1], target))
            continue
        if not resolve(str(target), subjects, pkg, reg_graph=g):
            unresolved += 1
            print("   UNRESOLVED  %-30s -> %s"
                  % (str(ac).split("#")[-1], target))
    print("criteria naming an artefact : %d" % named)
    print("unresolved                  : %d  (of which outside the package: %d)" % (unresolved, outside))
    print("VERDICT     : %s" % (
        "PASS - every named artefact resolves" if not unresolved else
        "FAIL - %d criterion artefact(s) do not exist" % unresolved))
    sys.exit(1 if (unresolved and strict) else 0)

if __name__ == "__main__":
    main()
