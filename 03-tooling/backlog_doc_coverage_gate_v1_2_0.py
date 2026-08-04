#!/usr/bin/env python3
"""backlog_doc_coverage_gate v1.2.0 — does the standard still describe the subject?

Exists because it silently stopped doing so. Subject versions 1.4.0, 1.5.0 and
1.7.0 added 17 terms that never reached the standard document: decomposition,
commitments, dependency kinds, impediments, flow measures, teams, observations,
re-baselining, register packaging. Every other gate passed throughout — parse,
SHACL, manifest, version identity, coverage against the source methodology —
because none of them compares the ontology with the prose that explains it.

An adopter reads the standard, not the TBox. A standard three releases behind
the subject is a defect that no amount of green gates will surface, so this
check joins the release gate.

Rule 1: every owl:Class in the subject TBox must be named in the standard
document. Properties are not required individually — the standard groups them —
but classes are the vocabulary an adopter navigates by.

Rule 2 (v1.1.0): the standard must contain no RESTATED MEASUREMENT. A reader of
another session found the document claiming "46 violations across 28 planted
defects" while the gate reported 280 on the same fixture, and the header pinning
a package version three releases old. Rule 1 could not see either: it checks that
vocabulary is named, not that stated numbers are current.

L-91 is the governing rule and its remedy is not "recompute the prose" but
"prose points at the authoritative field rather than restating it". So this gate
does not verify the numbers — it forbids them. Measured figures belong in
RELEASE_METRICS.txt, which is generated, carries the manifest SHA it was produced
against, and regenerates byte-identically.

Dated historical citations are exempt: "Ruled at OE Pack v20.23.41" records when
something happened and never goes stale, and rewriting it would be the very
L-112 violation the repoint tool exists to prevent. Only current-state assertions
are flagged.

Rule 3 (v1.2.0): every versioned CURRENT-STATE Markdown document's H1 title must
carry the same version token as its filename. Historical records are exempt — a
dated audit's title names the subject version it audited, not its own, and
rewriting one to satisfy this rule would be the L-112 violation. Caught here after the standard was renamed
to _v1_5_0.md with its title still reading v1.4.0 — the same defect OEE returned
twice before in provenance notes, found this time by the package itself before
shipping. A filename bump with a stale title is a document that disagrees with
itself about which version a reader is holding.

Structural counts are NOT measurements and stay allowed: "a closed set of three",
"eight required sections", "five conformance levels" are facts about the
vocabulary, not about a run.

Usage: backlog_doc_coverage_gate_v1_0_0.py
"""
import glob, os, re, sys
from rdflib import Graph, RDF, OWL, URIRef

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BL = "http://example.org/backlog#"


def main():
    tbox = sorted(glob.glob(os.path.join(PKG, "01-ontologies", "backlog_tbox_v*.ttl")))[-1]
    std = sorted(glob.glob(os.path.join(PKG, "04-documentation",
                                        "BACKLOG_ROADMAP_FRAMEWORK_STANDARD_v*.md")))[-1]
    g = Graph()
    g.parse(tbox, format="turtle")
    classes = sorted({str(c).split("#")[-1] for c in g.subjects(RDF.type, OWL.Class)
                      if isinstance(c, URIRef) and str(c).startswith(BL)})
    text = open(std, encoding="utf-8").read()
    missing = [c for c in classes if not re.search(r"\b%s\b" % re.escape(c), text)]

    # Rule 2 — restated measurements. Narrow by design: each pattern matches a
    # figure only a run can produce, never a structural count.
    MEASUREMENT_PATTERNS = [
        (r"\b\d+\s+violations?\b", "a fixture violation count"),
        (r"\b\d+\s+planted\s+defects?\b", "a planted-defect total"),
        (r"\b\d+\s*/\s*\d+\s*=?\s*\d*\.?\d*%", "a coverage ratio"),
        (r"\b\d+\s+ontology\s+declarations?\b", "a version-identity count"),
        (r"\b\d+\s+classes?\s+named\b", "a documentation-coverage count"),
        (r"`backlog-roadmap-framework`\s+v\d+\.\d+\.\d+", "a distribution package version pin"),
        (r"OE\s+Pack\s+v\d+\.\d+\.\d+", "an OE Pack release pin"),
    ]
    # A dated historical citation is not a stale pin. "Ruled at OE Pack v20.23.41"
    # records when something happened and stays true forever; rewriting it would be
    # the L-112 violation. Only forward-looking or current-state assertions go stale,
    # so the same current-state-versus-historical distinction the repoint tool draws
    # is applied here, inside the gate.
    HISTORICAL_CITATION = re.compile(
        r"(ruled|adopted|catalogued|amended|registered|closed|confirmed|verified|"
        r"raised|deposited|screened)\s+(at|in|by)\s*$", re.I)
    restated = []
    for pattern, what in MEASUREMENT_PATTERNS:
        for m in re.finditer(pattern, text):
            preceding = text[max(0, m.start() - 60):m.start()]
            if HISTORICAL_CITATION.search(preceding):
                continue
            line = text[:m.start()].count("\n") + 1
            restated.append((line, m.group(0).strip(), what))

    print("tbox        : %s" % os.path.basename(tbox))
    print("standard    : %s" % os.path.basename(std))
    print("classes     : %d declared, %d named in the standard" % (len(classes), len(classes) - len(missing)))
    if missing:
        print("undocumented:")
        for c in missing:
            print("   %s" % c)
    print("restated    : %d measurement(s) found in the standard" % len(restated))
    for line, text_found, what in restated:
        print("   L%-5d %-28s %s" % (line, repr(text_found), what))
    if restated:
        print("   L-91: point at RELEASE_METRICS.txt rather than restating a figure a run produces.")
    # Rule 3 — title/filename version agreement across every versioned document
    # Historical records are exempt: a dated audit's title names the SUBJECT version
    # it audited, not the document's own, and that is not a disagreement. Rewriting
    # one to satisfy this rule would be the L-112 violation. Only current-state
    # documents must agree with their own filename.
    HISTORICAL_TITLE_EXEMPT = ("changelog_", "_audit_v", "coverage_report_",
                               "_assessment_v", "oe_ceremony_record", "_note_v",
                               "_response_v", "_proposal_v")
    title_mismatches = []
    for doc in sorted(set(glob.glob(os.path.join(PKG, "0*", "**", "*.md"), recursive=True))):
        base = os.path.basename(doc)
        fm = re.search(r"_v(\d+)_(\d+)_(\d+)\.md$", base)
        if not fm:
            continue
        if any(tok in base.lower() for tok in HISTORICAL_TITLE_EXEMPT):
            continue
        want = ".".join(fm.groups())
        first = open(doc, encoding="utf-8").readline()
        tm = re.search(r"v(\d+\.\d+\.\d+)\s*$", first.strip())
        if tm and tm.group(1) != want:
            title_mismatches.append((base, tm.group(1), want))
    print("titles      : %d versioned document(s) whose H1 disagrees with the filename"
          % len(title_mismatches))
    for base, got, want in title_mismatches:
        print("   %-58s title v%s, filename v%s" % (base, got, want))

    ok = not missing and not restated and not title_mismatches
    print("VERDICT     : %s — the standard %s"
          % ("PASS" if ok else "FAIL",
             "describes the subject, restates no measurement, and agrees with its own filename" if ok
             else ("has fallen behind" if missing
                   else ("restates measurements that go stale" if restated
                         else "carries a title that disagrees with its filename"))))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
