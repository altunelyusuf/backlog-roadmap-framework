#!/usr/bin/env python3
"""backlog_clause_proof_v1_0_0.py — which clauses has a fixture proven fire?

A constraint that no fixture makes fire has never been shown to work. It may be
correct; it may be malformed SPARQL returning nothing. Both look identical from
a green gate.

That is not hypothetical. Twice in this package's history a clause was written,
looked right, and returned no rows:

  v1.105.0  a triple pattern inside FILTER — the gate reported 0 violations AND
            0 warnings, and only the second number gave it away
  v1.110.0  subtracting two dateTimes and comparing to a duration — reported
            zero on a 34-day gap

Both were caught by accident. This catches them on purpose: it runs every
negative fixture, collects the clauses that actually fire, and reports the
level-gated clauses that no fixture has ever exercised.

Reports rather than fails by default. A gate that fails on 96 unproven clauses
gets suppressed; one that reports 96 gets worked down.

Exit 1 under --strict.
"""
import sys, os, glob, subprocess, re

def main():
    strict = "--strict" in sys.argv
    here = os.path.dirname(os.path.abspath(__file__))
    pkg = os.path.dirname(here)
    validate = sorted(glob.glob(os.path.join(here, "backlog_validate_v*.py")))[-1]
    fixtures = [f for f in sorted(glob.glob(os.path.join(here, "fixtures", "*.ttl")))
                if any(k in os.path.basename(f)
                       for k in ("negative", "adversarial", "digestfail"))]
    fired = set()
    for f in fixtures:
        try:
            out = subprocess.run([sys.executable, validate, f],
                                 capture_output=True, text=True, timeout=90).stdout
        except Exception:
            continue
        for m in re.findall(r"L[1-4]: [^\"\n]{0,50}", out):
            fired.add(m.strip())

    from rdflib import Graph, URIRef
    SH = "http://www.w3.org/ns/shacl#"
    g = Graph()
    g.parse(sorted(glob.glob(os.path.join(
        pkg, "02-shacl-safeguards", "backlog_shacl_v*.ttl")))[-1], format="turtle")
    clauses = set()
    for _, _, msg in g.triples((None, URIRef(SH + "message"), None)):
        t = str(msg)
        if t.startswith(("L1:", "L2:", "L3:", "L4:")):
            clauses.add(t[:50].strip())

    unproven = sorted(c for c in clauses
                      if not any(c[:38] in f for f in fired))
    print("negative fixtures run     : %d" % len(fixtures))
    print("level-gated clauses       : %d" % len(clauses))
    print("proven to fire            : %d" % (len(clauses) - len(unproven)))
    print("NEVER proven to fire      : %d" % len(unproven))
    for c in unproven[:25]:
        print("   %s" % c)
    if len(unproven) > 25:
        print("   ... and %d more" % (len(unproven) - 25))
    print("VERDICT     : %s" % (
        "PASS - every level-gated clause has a fixture that fires it"
        if not unproven else
        "REPORTED - %d clause(s) unproven; a clause nothing fires has "
        "never been shown to work" % len(unproven)))
    sys.exit(1 if (unproven and strict) else 0)

if __name__ == "__main__":
    main()
