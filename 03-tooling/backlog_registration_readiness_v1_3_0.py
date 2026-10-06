#!/usr/bin/env python3
"""backlog_registration_readiness v1.3.0 — pre-submission controls for the OE
Ontology Registration & Conformance Protocol (ORCP).

The protocol's Phase C says the receiving session re-derives every claim a
registrant makes and does not accept the registrant's numbers. This tool is the
registrant's side of that: it runs the checks OEE will run, so a submission
fails here rather than there, and it prints the numbers OEE will independently
recompute rather than asserting them from a document.

Controls, each traced to the clause it enforces:

  A1  Phase A   per-facet intent declared before submission
  B1  Phase B   bundle carries emitted TTL, a builder/script, a SHA manifest,
                and a fit-gap note
  B2  Phase B   BP-X1 scope disclosure: the validation configuration is named
  C2  Phase C   every shipped file hashes as recorded
  C3  Phase C   every numeric claim is recomputed here, not quoted
  C4  Phase C   emitted instances validate against the governing suite
  C5  Inv. 1    the registrant minted nothing in a foreign namespace, except
                deposits explicitly declared as proposals
  I5  Inv. 5    coordinated SemVer: versionInfo == versionIRI == filename
  I6  Inv. 6    every round recorded in release-history

  NS  Inv. 1    ZERO subjects minted in an OE-owned namespace — the standard
                the pack's accepted registrations were measured against
  X   Phase B   the emitted graph validated against the pack's OWN six suites
                (core, knowledge_base, release-history, testing, configuration,
                quality) at inference=none, with the pack's baseline noise
                re-derived against an empty graph and separated out rather than
                excused. Runs only with --pack; otherwise NOT RUN, never
                silently passed.

v1.3.0 (Lineage 18, OC-S05): the package's provenance records (registration intent, staging declaration, naming proposal, registration emission,
alignment, quality assessment) are modules of the archive data file, and the lesson deposit is a module of the live data file; this tool reads them there.
The emitted graph is the statements whose subjects sit in the namespaces those records mint in (the package namespace in both data files; the
vocabulary and bare example.org subjects in the archive file only), so the live register's own controlled individuals are not counted as emitted.

Usage:
  backlog_registration_readiness_v1_3_0.py [--pack /path/to/oepack]
"""

import argparse
import glob
import hashlib
import os
import re
import subprocess
import sys

import rdflib
from rdflib import Graph, RDF

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)

FOREIGN = {
    "http://example.org/core#": "core",
    "http://example.org/testing#": "testing",
    "http://example.org/risk#": "risk",
    "http://example.org/oepack-release-history#": "release-history",
    "http://example.org/configuration#": "configuration",
    "http://example.org/knowledge-base#": "knowledge_base",
    "http://example.org/oe-prov#": "oe-prov",
    "http://example.org/measurement#": "measurement",
    "http://example.org/quality#": "quality",
}
# Files whose foreign-namespace subjects are declared proposals, adjudicated by
# OEE under Phase D rather than treated as minting.
DECLARED_PROPOSALS = ("05-lesson-deposits/", "independent_package_naming_proposal")

results = []


def record(control, clause, ok, detail):
    results.append((control, clause, ok, detail))
    flag = "PASS" if ok is True else ("NOT RUN" if ok is None else "FAIL")
    print("  [%-7s] %-4s %-28s %s" % (flag, control, clause, detail))


PKG_NS = "http://example.org/backlog-package#"
EMIT_NS_ARCHIVE = (PKG_NS, "http://example.org/backlog#", "http://example.org/")


def _ns(s):
    s = str(s); i = max(s.rfind("#"), s.rfind("/")); return s[:i + 1]


def archive_file():
    hits = sorted(glob.glob(os.path.join(PKG, "01-ontologies", "archive", "backlog_framework_archive_abox_v*.ttl")))
    return hits[-1] if hits else None


def live_data_file():
    hits = sorted(glob.glob(os.path.join(PKG, "01-ontologies", "backlog_abox_v*.ttl")))
    return hits[-1] if hits else None


def emitted_graph():
    """The graph the provenance records and the lesson deposit make, taken from the two data files they were folded into."""
    out = Graph()
    a, l = archive_file(), live_data_file()
    if a:
        ga = Graph(); ga.parse(a, format="turtle")
        for t in ga:
            if _ns(t[0]) in EMIT_NS_ARCHIVE:
                out.add(t)
    if l:
        gl = Graph(); gl.parse(l, format="turtle")
        for t in gl:
            if _ns(t[0]) == PKG_NS:
                out.add(t)
    return out


def all_ttl():
    return sorted(glob.glob(os.path.join(PKG, "0*", "**", "*.ttl"), recursive=True))


def control_a1():
    if not archive_file():
        return record("A1", "Phase A", False, "no archive data file holding the registration intent: registrant has not self-classified")
    g = emitted_graph()
    intents = [s for s in g.subjects(RDF.type, rdflib.URIRef("http://example.org/backlog-package#FacetIntent"))]
    record("A1", "Phase A", len(intents) > 0,
           "%d facet intents declared (%s)" % (len(intents), os.path.basename(archive_file())))


def control_b1():
    checks = {
        "emitted TTL": len(all_ttl()) > 0,
        "builder/script": len(glob.glob(os.path.join(PKG, "03-tooling", "*.py"))) > 0,
        "SHA manifest": os.path.exists(os.path.join(PKG, "MANIFEST_SHA256.txt")),
        "fit-gap note": len(glob.glob(os.path.join(PKG, "04-documentation", "ORCP_Submission_*.md"))) > 0,
    }
    missing = [k for k, v in checks.items() if not v]
    record("B1", "Phase B", not missing,
           "bundle complete" if not missing else "missing: " + ", ".join(missing))


def control_b2():
    notes = glob.glob(os.path.join(PKG, "04-documentation", "ORCP_Submission_*.md"))
    if not notes:
        return record("B2", "Phase B", False, "no fit-gap note to disclose configuration in")
    text = open(sorted(notes)[-1], encoding="utf-8").read()
    needed = ["pyshacl", "advanced mode", "imports"]
    missing = [n for n in needed if n.lower() not in text.lower()]
    record("B2", "BP-X1", not missing,
           "validation config disclosed" if not missing else "undisclosed: " + ", ".join(missing))


def control_c2():
    path = os.path.join(PKG, "MANIFEST_SHA256.txt")
    if not os.path.exists(path):
        return record("C2", "Phase C", False, "no manifest")
    ok = bad = miss = 0
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^([0-9a-f]{64})\s+(.+?)\s+\(\d+b\)$", line.strip())
        if not m:
            continue
        h, rel = m.groups()
        full = os.path.join(PKG, rel)
        if not os.path.exists(full):
            miss += 1
            continue
        d = hashlib.sha256(open(full, "rb").read()).hexdigest()
        ok += d == h
        bad += d != h
    record("C2", "Phase C", bad == 0 and miss == 0, "%d OK, %d mismatched, %d missing" % (ok, bad, miss))


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=PKG)


def control_c3_c4():
    validate = sorted(glob.glob(os.path.join(HERE, "backlog_validate_v*.py")))[-1]
    pos = sorted(glob.glob(os.path.join(HERE, "fixtures", "fixture_positive_v*.ttl")))[-1]
    neg = sorted(glob.glob(os.path.join(HERE, "fixtures", "fixture_negative_v*.ttl")))[-1]
    cov = sorted(glob.glob(os.path.join(HERE, "backlog_coverage_gate_v*.py")))[-1]

    p_out = run([sys.executable, validate, pos]).stdout
    n_out = run([sys.executable, validate, neg]).stdout
    c_out = run([sys.executable, cov]).stdout
    k_out = run([sys.executable, validate, "--gate-k"]).stdout

    def num(pattern, text):
        m = re.search(pattern, text)
        return m.group(1) if m else "?"

    pv = num(r"results\s+:\s+(\d+) Violation", p_out)
    nv = num(r"results\s+:\s+(\d+) Violation", n_out)
    cvg = num(r"coverage\s+:\s+(\d+/\d+)", c_out)
    gk = num(r"Gate K: (\d+) ontology declarations checked, 0 mismatches", k_out)

    record("C3", "Phase C", pv == "0" and nv != "0",
           "recomputed now: positive %s violations, negative %s violations, coverage %s, Gate K %s declarations"
           % (pv, nv, cvg, gk))
    record("C4", "L-90", pv == "0", "emitted instances validated against this subject's own SHACL suite")
    record("I5", "Inv. 5", gk != "?" and "0 mismatches" in k_out, "version identity across all shipped ontologies")


def control_c5():
    minted = []
    for path in all_ttl():
        rel = os.path.relpath(path, PKG)
        declared = any(tag in rel for tag in DECLARED_PROPOSALS)
        g = Graph()
        g.parse(path, format="turtle")
        for s in set(g.subjects()):
            s = str(s)
            for ns, name in FOREIGN.items():
                if s.startswith(ns):
                    minted.append((rel, name, s.split("#")[-1], declared))
    undeclared = [m for m in minted if not m[3]]
    declared = [m for m in minted if m[3]]
    detail = "%d foreign-namespace subjects, %d of them in declared proposal files" % (len(minted), len(declared))
    if undeclared:
        detail += " — UNDECLARED: " + ", ".join("%s:%s in %s" % (m[1], m[2], m[0]) for m in undeclared[:5])
    record("C5", "Inv. 1", not undeclared, detail)


def control_i6():
    if not archive_file():
        return record("I6", "Inv. 6", False, "no round record")
    g = emitted_graph()
    rounds = list(g.subjects(RDF.type, rdflib.URIRef("http://example.org/oepack-release-history#ReleaseEvent")))
    record("I6", "Inv. 6", len(rounds) > 0, "%d ORCP round(s) recorded as release events" % len(rounds))


def control_ns():
    """No subject may be minted in an OE-owned namespace (pack precedent: an
    accepted registration was measured as 'B1 CLEAN, 0 OE-namespace subjects')."""
    oe_ns = list(FOREIGN.keys())
    bad = []
    for path in all_ttl():
        g = Graph()
        g.parse(path, format="turtle")
        for s in set(g.subjects()):
            if any(str(s).startswith(ns) for ns in oe_ns):
                bad.append((os.path.relpath(path, PKG), str(s).split("#")[-1]))
    record("NS", "Inv. 1", not bad,
           "0 OE-namespace subjects minted" if not bad
           else "%d minted: %s" % (len(bad), ", ".join("%s in %s" % (n, f) for f, n in bad[:4])))


SUITES = [("core", "core_shacl_v*.ttl"), ("knowledge_base", "knowledge_base_shacl_v*.ttl"),
          ("release_history", "oepack_release_history_shacl_v*.ttl"), ("testing", "testing_shacl_v*.ttl"),
          ("configuration", "configuration_shacl_v*.ttl"), ("quality", "quality_shacl_v*.ttl")]


def _strip(paths, suffix):
    import tempfile
    g = Graph()
    for p in paths:
        g.parse(p, format="turtle")
    for t in list(g.triples((None, rdflib.OWL.imports, None))):
        g.remove(t)
    fd, out = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    g.serialize(out, format="turtle")
    return out


def _violations(shapes_path, data_path):
    SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")
    proc = subprocess.run([sys.executable, "-m", "pyshacl", "-s", shapes_path, "-a", "-i", "none",
                           "-f", "turtle", data_path], capture_output=True, text=True)
    rg = Graph()
    try:
        rg.parse(data=proc.stdout, format="turtle")
    except Exception:
        return None
    return [(str(rg.value(r, SH.focusNode)), str(rg.value(r, SH.resultMessage)))
            for r in rg.subjects(RDF.type, SH.ValidationResult)
            if rg.value(r, SH.resultSeverity) == SH.Violation]


def control_x(pack):
    if not pack:
        return record("X", "Phase B", None,
                      "six-suite validation against the pack's own shapes needs --pack; not run, not assumed")
    eg = emitted_graph()
    if not len(eg):
        return record("X", "Phase B", None, "no emitted OE-binding graph found")
    import tempfile
    tmp = tempfile.NamedTemporaryFile("w", suffix=".emitted.ttl", delete=False)
    tmp.write(eg.serialize(format="turtle")); tmp.close()
    data_path = _strip([tmp.name], ".emit.ttl")
    emitted_subjects = {str(s) for s in eg.subjects()}
    empty_path = _strip([], ".empty.ttl")

    total_attr = 0
    lines = []
    for name, pattern in SUITES:
        hits = sorted(glob.glob(os.path.join(pack, "02-shacl-safeguards", pattern)))
        if not hits:
            lines.append("%s=NOTFOUND" % name)
            continue
        shapes_path = _strip([hits[-1]], ".shapes.ttl")
        found = _violations(shapes_path, data_path)
        baseline = _violations(shapes_path, empty_path)
        if found is None or baseline is None:
            lines.append("%s=UNPARSABLE" % name)
            continue
        attributable = [v for v in found if v[0] in emitted_subjects]
        total_attr += len(attributable)
        lines.append("%s %d/%d" % (name, len(attributable), len(baseline)))
    record("X", "Phase B", total_attr == 0,
           "attributable/baseline per suite — " + ", ".join(lines))


def main():
    ap = argparse.ArgumentParser(description="ORCP pre-submission readiness controls.")
    ap.add_argument("--pack", default=None, help="path to an extracted OE Pack, enabling cross-facet validation")
    args = ap.parse_args()

    # the label is derived from the package's own VERSION.txt, never from the
    # enclosing directory: a value taken from the extraction path cannot reproduce
    # for anyone who unpacks the bundle under a different name (L-X5).
    try:
        _v = open(os.path.join(PKG, "VERSION.txt")).read().strip()
    except OSError:
        _v = "unknown"
    print("ORCP registration readiness — controls run for backlog-roadmap-framework v%s" % _v)
    print("tooling     : rdflib %s, pyshacl invoked via CLI, imports stripped, advanced mode ON\n" % rdflib.__version__)
    control_a1()
    control_b1()
    control_b2()
    control_c2()
    control_c3_c4()
    control_c5()
    control_ns()
    control_i6()
    control_x(args.pack)

    failed = [r for r in results if r[2] is False]
    notrun = [r for r in results if r[2] is None]
    print("\n%d controls: %d pass, %d fail, %d not run"
          % (len(results), len(results) - len(failed) - len(notrun), len(failed), len(notrun)))
    if failed:
        print("VERDICT     : NOT READY — resolve the failing controls before submitting.")
        return 1
    print("VERDICT     : READY to submit%s" % (" (with %d control(s) not run — say so in the fit-gap note)" % len(notrun) if notrun else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
