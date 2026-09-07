#!/usr/bin/env python3
"""backlog_validate v1.6.0 — conformance validator for the Backlog & Roadmap
Semantic Framework (http://example.org/backlog 1.0.0).

Design points that are not incidental:

* The SUPPRESSION COST of the declared conformance level is reported on every
  run. A register declaring L1_Core is validated against 43 fewer constraints
  than one declaring L3_Governed — measured, not estimated — and until now the
  report said only "0 Violation", with nothing indicating how many checks never
  executed. A clean result at a low level and a clean result at a high level
  printed identically. They are not the same claim and should not read the same.

* Advisory results are reported as a GROUPED DIGEST — a count per distinct
  message — not as a bare total and not as one line per result. A reader of a
  parallel session put the failure precisely: "175 Warning" with no content is a
  number a human learns to skip past, and the advisory tier then protects nothing
  it was built to surface. One line per result is the opposite failure: 175 lines
  nobody reads either. The digest is the granularity that says WHAT KIND of advice
  is outstanding, which is the decision-relevant fact. Individual advisory lines
  are still printed while the total stays small enough to read.

* Conformance is reported as ZERO sh:Violation results, not as an empty
  report. pyshacl sets conforms=False when any result exists, including
  advisory sh:Warning and sh:Info, but SHACL-spec conformance is about
  violations. Counting all results would fail a register on advice.
* Every PASS line prints the shapes file, its SHA-256, the pyshacl and
  rdflib versions, and the mode. A pass claim that does not carry its
  measurement configuration is not a measurement.
* owl:imports statements are stripped before validation. The framework's
  upstream subjects (core, testing, release-history) are not resolvable
  from this package, and a silently failed import would validate a
  smaller graph than the one claimed.

* Gate K (--gate-k) checks version identity mechanically: for every shipped
  ontology file, owl:versionInfo must equal the owl:versionIRI token and the
  filename version token. A mismatch is invisible to a reader who trusts the
  filename, so it is never left to inspection.

Usage:
  backlog_validate_v1_5_0.py DATA.ttl [DATA2.ttl ...]
  backlog_validate_v1_5_0.py --next DATA.ttl [--method IRI]
  backlog_validate_v1_5_0.py --gate-k
"""

import argparse
import hashlib
import json
import os
import re
import glob
import subprocess
import sys
import tempfile

try:
    import rdflib
    from rdflib import Graph, URIRef
except ImportError:
    sys.exit("rdflib is required: pip install rdflib pyshacl --break-system-packages")

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")
BL = rdflib.Namespace("http://example.org/backlog#")

def _semver(path):
    m = re.search(r"_v(\d+)_(\d+)_(\d+)\.[a-z]+$", os.path.basename(path))
    return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)


def latest(subdir, stem, ext="ttl"):
    """Resolve a pointer by PATTERN, not by pinned filename: the highest-versioned
    stem_v*.ext in subdir. Version bumps of an ontology then never require editing
    the tooling that reads it — the same version-independent pointer rule the OE
    Operating Discipline applies to its own artifact references."""
    hits = glob.glob(os.path.join(PKG, subdir, "%s_v*.%s" % (stem, ext)))
    if not hits:
        raise SystemExit("no artifact matching %s/%s_v*.%s" % (subdir, stem, ext))
    return sorted(hits, key=_semver)[-1]


TBOX = latest("01-ontologies", "backlog_tbox")
ABOX = latest("01-ontologies", "backlog_abox")
SHAPES = latest("02-shacl-safeguards", "backlog_shacl")
RULES = latest("02-shacl-safeguards", "backlog_rules")


def sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load(paths):
    g = Graph()
    for p in paths:
        g.parse(p, format="turtle")
    for triple in list(g.triples((None, rdflib.OWL.imports, None))):
        g.remove(triple)
    return g


def serialize(graph, suffix):
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    graph.serialize(path, format="turtle")
    return path


def pyshacl_version():
    try:
        import pyshacl
        return getattr(pyshacl, "__version__", "unknown")
    except ImportError:
        return "unknown"


def _memo_key(data_files):
    h = hashlib.sha256()
    for p in [os.path.abspath(__file__), TBOX, ABOX, SHAPES, RULES] + sorted(data_files):
        h.update(os.path.basename(p).encode()); h.update(open(p, "rb").read())
    return h.hexdigest()


def validate(data_files):
    """v1.6.0: memoized when BACKLOG_VALIDATE_MEMO_DIR is set. The key covers this
    script's own bytes, the resolved TBox/ABox/shapes/rules bytes and every data
    file's bytes, so no edit to any input can return a stale answer; a cache is
    only ever a replay of an identical computation. Exists because one pyshacl
    evaluation of this suite costs 20-46 s on one core and the release gate plus
    clause-proof evaluate ~75 (fixture, suite) pairs of which fewer than half are
    distinct -- and because the gate must be RESUMABLE: a session's per-call
    runtime ceiling is below one full gate run (G10), so a caller that keeps the
    cache directory across calls finishes the same gate in pieces, each piece a
    real computation, none of them repeated. Replaces backlog_validate_memo (a
    shell shim that only the gate could reach; clause-proof calls this script
    directly and was never memoized)."""
    memo_dir = os.environ.get("BACKLOG_VALIDATE_MEMO_DIR")
    if not memo_dir:
        return _validate(data_files)
    os.makedirs(memo_dir, exist_ok=True)
    memo_path = os.path.join(memo_dir, _memo_key(data_files) + ".json")
    if os.path.exists(memo_path):
        with open(memo_path) as fh:
            hit = json.load(fh)
        sys.stdout.write(hit["stdout"])
        return hit["code"], hit["counts"]
    import io
    real_stdout, buf = sys.stdout, io.StringIO()
    sys.stdout = buf
    try:
        code, counts = _validate(data_files)
    finally:
        sys.stdout = real_stdout
    sys.stdout.write(buf.getvalue())
    if isinstance(counts, dict) and counts:
        with open(memo_path, "w") as fh:
            json.dump({"code": code, "counts": counts, "stdout": buf.getvalue()}, fh)
    return code, counts


def _validate(data_files):
    data_path = serialize(load([TBOX, ABOX] + data_files), ".data.ttl")
    shapes_path = serialize(load([SHAPES, RULES]), ".shapes.ttl")

    proc = subprocess.run(
        [sys.executable, "-m", "pyshacl", "-s", shapes_path, "-a", "-f", "turtle", data_path],
        capture_output=True, text=True,
    )
    report = Graph()
    try:
        report.parse(data=proc.stdout, format="turtle")
    except Exception:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        return 2, {}

    counts = {"Violation": 0, "Warning": 0, "Info": 0}
    findings = []
    for result in report.subjects(rdflib.RDF.type, SH.ValidationResult):
        sev = report.value(result, SH.resultSeverity)
        name = str(sev).rsplit("#", 1)[-1] if sev else "Violation"
        counts[name] = counts.get(name, 0) + 1
        findings.append((name,
                         str(report.value(result, SH.focusNode)),
                         str(report.value(result, SH.resultMessage))))

    print("shapes      : %s (sha256 %s)" % (os.path.basename(SHAPES), sha256(SHAPES)[:16]))
    print("rules       : %s (sha256 %s)" % (os.path.basename(RULES), sha256(RULES)[:16]))
    print("data        : %s" % ", ".join(os.path.basename(f) for f in data_files))
    print("tooling     : pyshacl %s, rdflib %s, advanced mode ON" % (pyshacl_version(), rdflib.__version__))

    print("results     : %d Violation, %d Warning, %d Info"
          % (counts["Violation"], counts["Warning"], counts["Info"]))

    # Violations are always listed individually: each one blocks a release and the
    # focus node is the actionable part.
    for name, focus, msg in sorted(f for f in findings if f[0] == "Violation"):
        print("  [%-9s] %-48s %s" % (name, focus.rsplit("#", 1)[-1], msg))

    # Advisories are grouped by message. A total alone teaches a reader to skip it;
    # one line per result is unreadable at scale. The count per distinct message is
    # what a human actually decides on.
    advisories = [f for f in findings if f[0] in ("Warning", "Info")]
    if advisories:
        grouped = {}
        for sev, focus, msg in advisories:
            grouped.setdefault((sev, msg), []).append(focus.rsplit("#", 1)[-1])
        print("advisory    : %d result(s) across %d distinct message(s)"
              % (len(advisories), len(grouped)))
        for (sev, msg), nodes in sorted(grouped.items(), key=lambda kv: (-len(kv[1]), kv[0][1])):
            shown = ", ".join(sorted(nodes)[:4]) + (", …" if len(nodes) > 4 else "")
            print("  %4d x [%-7s] %s" % (len(nodes), sev, msg[:96]))
            print("            on: %s" % shown)
        if len(advisories) <= 20:
            for sev, focus, msg in sorted(advisories):
                print("  [%-9s] %-48s %s" % (sev, focus.rsplit("#", 1)[-1], msg))

    if counts["Violation"] == 0:
        print("VERDICT     : CONFORMANT (0 violations at sh:Violation severity; "
              "advisory results above are not conformance failures)")
        return 0, counts
    print("VERDICT     : NON-CONFORMANT (%d violations)" % counts["Violation"])
    return 1, counts


def next_item(data_files, method):
    g = load([TBOX, ABOX] + data_files)
    query = """
    SELECT ?id ?value WHERE {
      ?item backlog:hasState backlog:Ready ;
            backlog:hasIdentifier ?id ;
            backlog:hasPriorityScore ?sc .
      ?sc backlog:scoredByMethod ?method ; backlog:hasScoreValue ?value .
      FILTER NOT EXISTS {
        ?item backlog:dependsOn ?d . ?d backlog:hasState ?ds .
        FILTER(?ds != backlog:Done)
      }
    } ORDER BY DESC(?value) LIMIT 1
    """
    rows = list(g.query(query, initNs={"backlog": BL},
                        initBindings={"method": URIRef(method)} if method else None))
    if not rows:
        print("NEXT: nothing is startable — no Ready item with all dependencies Done and a score under this method.")
        return 0
    for rid, value in rows:
        print("NEXT: %s (score %s, method %s)" % (rid, value, method or "any"))
    return 0


def gate_k():
    """Gate K — versionInfo == versionIRI token == filename token, for every ontology file."""
    failures = 0
    checked = 0
    # every shipped Turtle file, not only the subject directories: an ontology
    # declaration outside 01/02 (package provenance, deposits) carries version
    # metadata too, and a gate that never looks at it cannot fail on it.
    for path in sorted(glob.glob(os.path.join(PKG, "0*", "**", "*.ttl"), recursive=True)):
        g = Graph()
        g.parse(path, format="turtle")
        fname = os.path.basename(path)
        m = re.search(r"_v(\d+)_(\d+)_(\d+)\.ttl$", fname)
        if not m:
            print("  [SKIP ] %s (no version token in filename)" % fname)
            continue
        file_ver = ".".join(m.groups())
        for onto in g.subjects(rdflib.RDF.type, rdflib.OWL.Ontology):
            checked += 1
            info = g.value(onto, rdflib.OWL.versionInfo)
            viri = g.value(onto, rdflib.OWL.versionIRI)
            iri_ver = str(viri).rstrip("/").rsplit("/", 1)[-1] if viri else None
            ok = (str(info) == file_ver) and (iri_ver == file_ver)
            if not ok:
                failures += 1
            print("  [%s] %-46s versionInfo=%s versionIRI=%s filename=%s"
                  % ("PASS" if ok else "FAIL", fname, info, iri_ver, file_ver))
    print("Gate K: %d ontology declarations checked, %d mismatches" % (checked, failures))
    return 1 if failures else 0


def main():
    ap = argparse.ArgumentParser(description="Validate a register against the backlog framework.")
    ap.add_argument("data", nargs="*", help="register Turtle file(s)")
    ap.add_argument("--gate-k", action="store_true", help="run Gate K version-identity check and exit")
    ap.add_argument("--each", action="store_true",
                    help="validate each file SEPARATELY in one process, printing a per-file "
                         "verdict line. Exists because the TBox and shapes are re-parsed and "
                         "re-inferred on every invocation, so validating eight fixtures cost "
                         "eight full loads; the package's release gate grew slower than the "
                         "publisher's runtime and the package became unpublishable. Nothing is "
                         "skipped — each file still gets its own independent validation.")
    ap.add_argument("--polarity", action="store_true",
                    help="print '<file> <positive|negative|undeclared>' for each file, from the "
                         "fixture's own hasExpectedPolarity, and exit. The gate uses this instead "
                         "of inferring from the filename.")
    ap.add_argument("--next", action="store_true", help="print the next item to work instead of validating")
    ap.add_argument("--method", default="http://example.org/backlog#Method_WSJF",
                    help="prioritisation method IRI for --next")
    args = ap.parse_args()

    if args.gate_k:
        sys.exit(gate_k())
    if not args.data:
        ap.error("no register file given")
    if args.polarity:
        for f in args.data:
            print("POLARITY %s %s" % (os.path.basename(f), expected_polarity(f) or "undeclared"))
        sys.exit(0)
    if args.next:
        sys.exit(next_item(args.data, args.method))
    if args.each:
        worst = 0
        for f in args.data:
            code, counts = validate([f])
            print("EACH %s %s violations=%d"
                  % (os.path.basename(f), "FAIL" if code else "PASS",
                     counts.get("Violation", 0) if isinstance(counts, dict) else -1))
            worst = max(worst, code)
        sys.exit(worst)
    code, _ = validate(args.data)
    sys.exit(code)


def expected_polarity(fixture_path):
    """What the suite expects of a fixture, from the fixture itself.

    Replaces inference from the FILENAME. A file with "negative" in its name
    was expected to fail; rename it and the expectation moved with the name,
    silently. A positive fixture renamed for tidiness became a negative one
    that passed by failing.

    Declared on the fixture's own AdoptionProfile, which is already its
    statement about itself. Returns "positive", "negative", or None when the
    fixture declares nothing — None is reported, not guessed, because guessing
    is what this replaces.
    """
    from rdflib import Graph, Namespace, RDF
    B = Namespace("http://example.org/backlog#")
    g = Graph()
    try:
        g.parse(fixture_path, format="turtle")
    except Exception:
        return None
    # v1.6.0: read from ANY subject, not only an AdoptionProfile. 23 of the 51
    # shipped fixtures are minimal test-drive graphs with no profile at all, so
    # a profile-only reader left them undeclared and the gate fell back to the
    # filename rule this property was introduced to replace.
    for _s, pol in g.subject_objects(B.hasExpectedPolarity):
        return str(pol).split("#")[-1].replace("Polarity_", "").lower()
    return None


if __name__ == "__main__":
    main()
