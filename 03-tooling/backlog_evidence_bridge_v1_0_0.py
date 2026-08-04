#!/usr/bin/env python3
"""backlog_evidence_bridge v1.0.0 — the one component allowed to assert
backlog:evidenceVerified.

The ontology cannot read a filesystem, so every claim that an item is Done
ultimately rests on a check performed outside the graph. This script performs
those checks and writes the result back as triples. It sets evidenceVerified
to TRUE only when a check actually succeeded; on every other outcome —
missing file, hash mismatch, failing test, unrecognised evidence kind — it
writes FALSE. Absence of a check is never treated as a pass.

Checks by evidence kind:
  TestEvidence     spec file exists under --workspace; if --test-command is
                   given, the command is executed and must exit 0
  ReleaseEvidence  a file under --workspace whose SHA-256 equals the
                   recorded package hash must exist
  ArtifactEvidence the recorded path exists and, when a hash is recorded,
                   matches it
  ReviewEvidence   the recorded reference resolves to an existing file when
                   it looks like a path; otherwise left unverified, because
                   a reference no one can retrieve is not evidence

Usage:
  backlog_evidence_bridge_v1_0_0.py REGISTER.ttl --workspace DIR [-o OUT.ttl]
                                    [--test-command 'npx playwright test {spec} --grep {id}']
"""

import argparse
import datetime
import hashlib
import os
import subprocess
import sys

try:
    import rdflib
    from rdflib import Graph, Literal, URIRef, RDF, XSD
except ImportError:
    sys.exit("rdflib is required: pip install rdflib --break-system-packages")

BL = rdflib.Namespace("http://example.org/backlog#")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def find_by_hash(root, digest):
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            full = os.path.join(dirpath, name)
            try:
                if sha256_file(full) == digest:
                    return full
            except OSError:
                continue
    return None


def check_test(g, ev, workspace, test_command):
    spec = g.value(ev, BL.hasTestSpec)
    test_id = g.value(ev, BL.hasTestId)
    if spec is None:
        return False, "no test spec recorded"
    path = os.path.join(workspace, str(spec))
    if not os.path.isfile(path):
        return False, "spec not found at %s" % path
    if not test_command:
        return False, "spec exists but no --test-command given; existence alone does not prove passing"
    cmd = test_command.format(spec=str(spec), id=str(test_id) if test_id else "")
    proc = subprocess.run(cmd, shell=True, cwd=workspace, capture_output=True, text=True)
    if proc.returncode == 0:
        return True, "%s exited 0" % cmd
    return False, "%s exited %d" % (cmd, proc.returncode)


def check_release(g, ev, workspace):
    digest = g.value(ev, BL.hasPackageSHA256)
    if digest is None:
        return False, "no package hash recorded"
    hit = find_by_hash(workspace, str(digest))
    if hit:
        return True, "package hash matched %s" % os.path.relpath(hit, workspace)
    return False, "no file under the workspace matches the recorded package hash"


def check_artifact(g, ev, workspace):
    path = g.value(ev, BL.hasArtifactPath)
    if path is None:
        return False, "no artifact path recorded"
    full = os.path.join(workspace, str(path))
    if not os.path.isfile(full):
        return False, "artifact not found at %s" % full
    digest = g.value(ev, BL.hasArtifactSHA256)
    if digest is None:
        return True, "artifact exists (no hash recorded to compare)"
    actual = sha256_file(full)
    if actual == str(digest):
        return True, "artifact exists and hash matches"
    return False, "hash mismatch: recorded %s, actual %s" % (str(digest)[:16], actual[:16])


def check_review(g, ev, workspace):
    ref = g.value(ev, BL.hasReviewRecordRef)
    if ref is None:
        return False, "no review record reference recorded"
    candidate = os.path.join(workspace, str(ref).split("#", 1)[0])
    if os.path.exists(candidate):
        return True, "review record resolved at %s" % candidate
    return False, "review record reference does not resolve to a retrievable file"


KINDS = [
    (BL.TestEvidence, lambda g, e, w, c: check_test(g, e, w, c)),
    (BL.ReleaseEvidence, lambda g, e, w, c: check_release(g, e, w)),
    (BL.ArtifactEvidence, lambda g, e, w, c: check_artifact(g, e, w)),
    (BL.ReviewEvidence, lambda g, e, w, c: check_review(g, e, w)),
]


def main():
    ap = argparse.ArgumentParser(description="Verify backlog evidence against a real workspace.")
    ap.add_argument("register", help="register Turtle file")
    ap.add_argument("--workspace", required=True, help="root of the real workspace to check against")
    ap.add_argument("--test-command", default=None,
                    help="shell template run for TestEvidence, e.g. 'npx playwright test {spec} --grep {id}'")
    ap.add_argument("-o", "--output", default=None, help="output Turtle (default: overwrite the register)")
    args = ap.parse_args()

    g = Graph()
    g.parse(args.register, format="turtle")
    now = Literal(datetime.datetime.now().replace(microsecond=0).isoformat(), datatype=XSD.dateTime)

    verified = unverified = 0
    for cls, checker in KINDS:
        for ev in set(g.subjects(RDF.type, cls)):
            ok, method = checker(g, ev, args.workspace, args.test_command)
            for pred in (BL.evidenceVerified, BL.verifiedAt, BL.hasVerificationMethod):
                g.remove((ev, pred, None))
            g.add((ev, BL.evidenceVerified, Literal(ok)))
            g.add((ev, BL.verifiedAt, now))
            g.add((ev, BL.hasVerificationMethod, Literal(method)))
            if ok:
                verified += 1
            else:
                unverified += 1
            print("%-9s %-44s %s" % ("VERIFIED" if ok else "UNVERIF.",
                                     str(ev).rsplit("#", 1)[-1], method))

    out = args.output or args.register
    g.serialize(out, format="turtle")
    print("bridge: %d verified, %d unverified -> %s" % (verified, unverified, out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
