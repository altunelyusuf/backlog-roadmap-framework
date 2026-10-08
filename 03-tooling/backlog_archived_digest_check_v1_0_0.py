#!/usr/bin/env python3
"""backlog_archived_digest_check v1.0.0 -- every archived lineage's recorded stage digests are measured, and none may start failing unseen (G99).

The pipeline verifier recomputes each recorded stage digest. The gate ran it only on fixtures, never on the real lineages, and the archive is where all of them are.
Measured on 2026-10-08: of 21 archived lineages, 11 do not reproduce, 3 do, 7 record no stage outputs. This tool runs the verifier (unchanged) once per lineage,
in parallel, and keeps a RATCHET: archived_digest_baseline lists the 11; a lineage that fails and is not listed fails this check; a listed lineage that passes is
reported for removal. It proves itself first on the pipeline fixtures (the passing chain classifies PASS, a copy with one tampered digest classifies FAIL).
Options: --archive FILE  --baseline FILE (for the probe). Exit 0 within the baseline, 2 a new failing lineage, 3 the classification could not discriminate.
"""
import concurrent.futures as cf, glob, hashlib, json, os, re, subprocess, sys
from rdflib import Graph, Namespace, RDF

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
B = Namespace("http://example.org/backlog#")


def newest(pat):
    hits = glob.glob(pat)
    if not hits:
        raise SystemExit("not found: " + pat)
    return sorted(hits, key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]])[-1]


VERIFY = newest(os.path.join(HERE, "backlog_pipeline_verify_v*.py"))


def classify(data, lineage=None):
    # The verifier reads the T-Box itself; every file named on its command line is merged into the graph it measures, so none is passed here.
    cmd = [sys.executable, "-B", VERIFY, data] + (["--lineage", lineage] if lineage else [])
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    v = [x for x in out.splitlines() if x.startswith("VERDICT")]
    t = v[0] if v else ""
    if "PASS" in t:
        return "PASS"
    if "NOT VERIFIABLE" in t:
        return "NOT VERIFIABLE"
    if "FAIL" in t:
        return "FAIL"
    return "UNKNOWN"


def self_proof():
    bad = []
    good = newest(os.path.join(HERE, "fixtures", "fixture_pipeline_v*.ttl"))
    if classify(good) != "PASS":
        bad.append("the passing pipeline fixture did not classify PASS")
    # A tampered twin: one recorded digest changed in a temporary copy must classify FAIL.
    import tempfile
    txt = open(good).read()
    m = re.search(r'backlog:hasStateDigest "([0-9a-f]{64})"', txt)
    if not m:
        bad.append("no recorded digest found in the passing fixture to tamper with")
    else:
        with tempfile.TemporaryDirectory() as d:
            tp = os.path.join(d, "tampered.ttl")
            open(tp, "w").write(txt.replace(m.group(1), "0" * 64, 1))
            if classify(tp) != "FAIL":
                bad.append("a fixture with one tampered digest did not classify FAIL")
    return bad


BASELINE_OVERRIDE = None


def baseline():
    p = BASELINE_OVERRIDE or newest(os.path.join(HERE, "archived_digest_baseline_v*.txt"))
    return {l.strip() for l in open(p) if l.strip() and not l.startswith("#")}


def _key(arch):
    """Everything the result stands on, by bytes (OE rule R9): the archive, the verifier, this tool, the baseline, the stage table (T-Box and live data file), the pass fixture."""
    h = hashlib.sha256()
    files = [arch, VERIFY, os.path.abspath(__file__), BASELINE_OVERRIDE or newest(os.path.join(HERE, "archived_digest_baseline_v*.txt")),
             newest(os.path.join(PKG, "01-ontologies", "backlog_tbox_v*.ttl")), newest(os.path.join(PKG, "01-ontologies", "backlog_abox_v*.ttl")),
             newest(os.path.join(HERE, "fixtures", "fixture_pipeline_v*.ttl"))]
    for f in files:
        h.update(os.path.basename(f).encode()); h.update(open(f, "rb").read())
    return h.hexdigest()


def main():
    global BASELINE_OVERRIDE
    arch = None
    a = sys.argv[1:]
    while a:
        x = a.pop(0)
        if x == "--archive":
            arch = a.pop(0)
        elif x == "--baseline":
            BASELINE_OVERRIDE = a.pop(0)
        else:
            print("unknown argument: " + x); return 2
    arch = arch or newest(os.path.join(PKG, "01-ontologies", "archive", "backlog_framework_archive_abox_v*.ttl"))
    memo = os.environ.get("BACKLOG_VALIDATE_MEMO_DIR")
    cache = os.path.join(memo, "archdigest_" + _key(arch) + ".json") if memo and os.path.isdir(memo) else None
    res = None
    if cache and os.path.exists(cache):
        try:
            res = json.load(open(cache)); print("SELF-PROOF: kept from an earlier run on identical bytes (a reproducing chain classifies PASS, a chain with one tampered digest classifies FAIL)")
        except Exception:
            res = None
    if res is None:
        bad = self_proof()
        for b in bad:
            print("SELF-PROOF FAILED: " + b)
        if bad:
            print("VERDICT: could not discriminate; not certifying"); return 3
        print("SELF-PROOF: a reproducing chain classifies PASS, a chain with one tampered digest classifies FAIL")
        g = Graph(); g.parse(arch, format="turtle")
        names = sorted(str(l).split("#")[-1] for l in set(g.subjects(RDF.type, B.Lineage)))
        with cf.ThreadPoolExecutor(max_workers=8) as ex:
            # A file holding exactly one lineage is measured unscoped (the verifier documents the two as identical there); the probe relies on this to use a one-lineage fixture.
            res = dict(zip(names, ex.map(lambda n: classify(arch, n if len(names) > 1 else None), names)))
        if cache:
            json.dump(res, open(cache, "w"))
    names = sorted(res)
    base = baseline()
    count = {k: sum(1 for v in res.values() if v == k) for k in ("PASS", "FAIL", "NOT VERIFIABLE", "UNKNOWN")}
    print("archived lineages: %d  reproduce: %d  do not reproduce: %d (baseline %d)  no stage outputs: %d  unclassified: %d" % (
        len(names), count["PASS"], count["FAIL"], len(base), count["NOT VERIFIABLE"], count["UNKNOWN"]))
    new = [n for n, v in res.items() if v in ("FAIL", "UNKNOWN") and n not in base]
    gone = [n for n in base if res.get(n) == "PASS"]
    for n in gone:
        print("NOTE: %s now reproduces; remove it from the baseline" % n)
    for n in new:
        print("NEW FAILURE: %s -- its recorded stage digests do not reproduce and it is not in the baseline" % n)
    print("VERDICT: %s" % ("FAIL (%d new)" % len(new) if new else "within the baseline"))
    return 2 if new else 0


if __name__ == "__main__":
    sys.exit(main())
