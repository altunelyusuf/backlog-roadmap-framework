#!/usr/bin/env python3
"""build_manifest v1.4.0 — regenerate MANIFEST_SHA256.txt for this package.

Exists because the manifest is the one artifact that must be written last, and
doing it by hand put a stale hash in the bundle twice: once caught by the
release gate, once by ORCP control C2. A builder that always walks the tree at
call time removes the ordering mistake rather than asking anyone to remember it.

RELEASE_METRICS.txt is excluded from the manifest, and NOT for the reason the
first version of this note gave. A manifest cannot contain its own hash — that is
containment, a physical impossibility. This file *could* be hashed; it is excluded
because it **reports the result of the manifest gate**, so covering it creates a
generation-order cycle: hash the metrics, and the metrics describe a manifest that
no longer matches. The consequence is different and worse, which is why it must be
stated accurately: the manifest's integrity is self-evident the moment anyone
verifies it, while this file's integrity is not covered at all. Its only guarantee
is that it regenerates byte-for-byte — so it must contain nothing derived from the
environment it ran in.

PUBLISH_RECORD.ttl is excluded for the same class of reason and was not, which is
why the package's own self-check reported 62 OK and 1 BAD for several releases.
The publisher writes that record AFTER the manifest, so listing it guarantees a
mismatch: the hash is of a file that no longer exists in that form by the time
anyone verifies. A permanent, expected mismatch is worse than an exclusion,
because a reader cannot distinguish it from a real one.

EXEMPTIONS ARE NOW DECLARED IN THE ARTIFACT, not only in this docstring. Every
excluded file gets an `# EXEMPT <path> — <reason>` line in the manifest itself.
Gate 0 verifies that what is LISTED matches; nothing verified that what is
UNLISTED was meant to be unlisted, so a file could sit on disk uncovered and
indistinguishable from one that was forgotten. With the exemptions declared, a
checker can require that every file on disk is either hashed or exempted by
name — and an exemption added to hide something is then a visible edit to a
generated artifact rather than a silence.

Order is therefore: build the manifest, then generate the metrics against the
finished state.

Excludes build artifacts: __pycache__ directories and .pyc files are produced by
importing a module, not authored, and a manifest that lists them invites Gate 0
to certify bytes nobody wrote. Gate 0 verifies that what is listed matches; it
cannot know that something should never have been listed, which is why the
exclusion belongs here in the builder.

Usage: build_manifest_v1_4_0.py "one-line summary of this release"
"""
import hashlib, os, sys

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Each exemption states WHY, because "not listed" and "deliberately not listed"
# are different facts and a reader of the artifact cannot otherwise tell them apart.
EXEMPT = {
    "MANIFEST_SHA256.txt":
        "a manifest cannot contain its own hash; containment is a physical impossibility",
    "RELEASE_METRICS.txt":
        "reports the result of the manifest gate, so covering it creates a generation-order "
        "cycle; its integrity rests on regenerating byte-for-byte instead",
    "PUBLISH_RECORD.ttl":
        "written by the publisher AFTER the manifest, so listing it guarantees a permanent "
        "mismatch a reader cannot distinguish from a real one",
}


def main():
    version = open(os.path.join(PKG, "VERSION.txt")).read().strip()
    note = sys.argv[1] if len(sys.argv) > 1 else "Release build."
    lines = ["# backlog-roadmap-framework v%s — SHA-256 Manifest" % version,
             "# Built by build_manifest_v1_4_0.py. %s" % note, ""]
    for name, why in EXEMPT.items():
        lines.append("# EXEMPT %s — %s" % (name, why))
    lines.append("")
    for dirpath, dirs, files in os.walk(PKG):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        for f in sorted(files):
            if f in EXEMPT or f.endswith((".pyc", ".pyo")):
                continue
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, PKG)
            lines.append("%s  %s  (%db)" % (hashlib.sha256(open(full, "rb").read()).hexdigest(),
                                            rel, os.path.getsize(full)))
    open(os.path.join(PKG, "MANIFEST_SHA256.txt"), "w").write("\n".join(lines) + "\n")
    print("manifest: %d files, %d declared exemption(s), version %s"
          % (len(lines) - 4 - len(EXEMPT), len(EXEMPT), version))

if __name__ == "__main__":
    main()
