#!/usr/bin/env python3
"""backlog_class_requirements v1.0.0 -- generic requirements introspection.

Real gap this closes (G73, fw:Find_AutoGap2): authoring a new individual of
any class currently means discovering its own real requirements one
violation at a time, since nothing lists them together before authoring
begins. This is NOT case-specific to Goal or Objective -- it is a real,
structural gap that recurs for any class this suite governs, and this
tool answers it generically: given any class's own local name, walk its
real rdfs:subClassOf chain and report every sh:property and sh:sparql
constraint any current shape imposes on it or any class it inherits from.

Usage:
  python3 backlog_class_requirements_v1_0_0.py ClassName [REGISTER.ttl ...]

Reads the highest-versioned backlog_tbox_v*.ttl and backlog_shacl_v*.ttl
it can find under 01-ontologies/ and 02-shacl-safeguards/ relative to the
package root (two directories up from this script, matching this
package's own real layout), so it always reflects the shapes actually
shipping, not a stale copy. Additional register files are accepted for
context but are not required.
"""
import sys, glob, os, json
import rdflib
from rdflib.namespace import RDF, RDFS

SH = rdflib.namespace.SH
B = rdflib.Namespace("http://example.org/backlog#")


def highest(pattern):
    matches = glob.glob(pattern)
    if not matches:
        return None

    def key(path):
        import re
        m = re.search(r"_v(\d+)_(\d+)_(\d+)", path)
        return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)

    return sorted(matches, key=key)[-1]


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: backlog_class_requirements_v1_0_0.py ClassName"}))
        sys.exit(1)
    class_name = sys.argv[1]

    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)  # 03-tooling/.. -> package root
    tbox_path = highest(os.path.join(root, "01-ontologies", "backlog_tbox_v*.ttl"))
    shacl_path = highest(os.path.join(root, "02-shacl-safeguards", "backlog_shacl_v*.ttl"))
    if not tbox_path or not shacl_path:
        print(json.dumps({"error": "could not locate the highest-versioned tbox/shacl files"}))
        sys.exit(1)

    g = rdflib.Graph()
    g.parse(tbox_path, format="turtle")
    shacl = rdflib.Graph()
    shacl.parse(shacl_path, format="turtle")

    target = B[class_name]
    if (target, RDF.type, None) not in g and not any(g.triples((target, None, None))):
        print(json.dumps({"error": "no class backlog:%s found in %s" % (class_name, os.path.basename(tbox_path))}))
        sys.exit(1)

    # Walk the real rdfs:subClassOf chain, self included.
    hierarchy = {target}
    frontier = [target]
    while frontier:
        node = frontier.pop()
        for parent in g.objects(node, RDFS.subClassOf):
            if parent not in hierarchy and isinstance(parent, rdflib.URIRef):
                hierarchy.add(parent)
                frontier.append(parent)

    results = []
    for shape in set(shacl.subjects(SH.targetClass, None)):
        targets = set(shacl.objects(shape, SH.targetClass))
        if not (targets & hierarchy):
            continue
        severity = shacl.value(shape, SH.severity)
        sev_name = str(severity).split("#")[-1] if severity else "Violation"
        matched_on = [str(t).split("#")[-1] for t in (targets & hierarchy)]
        for prop in shacl.objects(shape, SH.property):
            path = shacl.value(prop, SH.path)
            min_c = shacl.value(prop, SH.minCount)
            max_c = shacl.value(prop, SH.maxCount)
            msg = shacl.value(prop, SH.message)
            results.append({
                "shape": str(shape).split("#")[-1],
                "severity": sev_name,
                "matched_via": matched_on,
                "kind": "property",
                "path": str(path).split("#")[-1] if path else None,
                "minCount": str(min_c) if min_c is not None else None,
                "maxCount": str(max_c) if max_c is not None else None,
                "message": str(msg) if msg else None,
            })
        for sp in shacl.objects(shape, SH.sparql):
            msg = shacl.value(sp, SH.message)
            results.append({
                "shape": str(shape).split("#")[-1],
                "severity": sev_name,
                "matched_via": matched_on,
                "kind": "sparql-conditional",
                "message": str(msg) if msg else None,
            })

    print("class: backlog:%s (hierarchy checked: %s)" % (
        class_name, ", ".join(sorted(str(h).split("#")[-1] for h in hierarchy))))
    print("tbox : %s" % os.path.basename(tbox_path))
    print("shacl: %s" % os.path.basename(shacl_path))
    print("real requirements found: %d\n" % len(results))
    always = [r for r in results if r["kind"] == "property"]
    conditional = [r for r in results if r["kind"] == "sparql-conditional"]
    if always:
        print("ALWAYS required (sh:property, unconditional on this class or an ancestor):")
        for r in sorted(always, key=lambda r: (r["severity"] != "Violation", r["path"] or "")):
            print("  [%s] %-28s minCount=%s maxCount=%s  -- %s" % (
                r["severity"], r["path"], r["minCount"], r["maxCount"], (r["message"] or "")[:100]))
    if conditional:
        print("\nCONDITIONAL (sh:sparql -- read the message for the real trigger, e.g. a lifecycle state):")
        for r in sorted(conditional, key=lambda r: r["severity"] != "Violation"):
            print("  [%s] (%s) -- %s" % (r["severity"], r["shape"], (r["message"] or "")[:160]))
    if not results:
        print("No shape in the current suite targets this class or any of its real ancestors.")


if __name__ == "__main__":
    main()
