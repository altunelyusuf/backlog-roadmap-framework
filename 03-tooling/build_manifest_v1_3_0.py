#!/usr/bin/env python3
"""build_manifest v1.3.0 — regenerate MANIFEST_SHA256.txt for this package.

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

Order is therefore: build the manifest, then generate the metrics against the
finished state.

Excludes build artifacts: __pycache__ directories and .pyc files are produced by
importing a module, not authored, and a manifest that lists them invites Gate 0
to certify bytes nobody wrote. Gate 0 verifies that what is listed matches; it
cannot know that something should never have been listed, which is why the
exclusion belongs here in the builder.

Usage: build_manifest_v1_3_0.py "one-line summary of this release"
"""
import hashlib, os, sys

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    version = open(os.path.join(PKG, "VERSION.txt")).read().strip()
    note = sys.argv[1] if len(sys.argv) > 1 else "Release build."
    lines = ["# backlog-roadmap-framework v%s — SHA-256 Manifest" % version,
             "# Built by build_manifest_v1_0_0.py. %s" % note, ""]
    for dirpath, dirs, files in os.walk(PKG):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        for f in sorted(files):
            if f in ("MANIFEST_SHA256.txt", "RELEASE_METRICS.txt") or f.endswith((".pyc", ".pyo")):
                continue
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, PKG)
            lines.append("%s  %s  (%db)" % (hashlib.sha256(open(full, "rb").read()).hexdigest(),
                                            rel, os.path.getsize(full)))
    open(os.path.join(PKG, "MANIFEST_SHA256.txt"), "w").write("\n".join(lines) + "\n")
    print("manifest: %d files, version %s" % (len(lines) - 3, version))

if __name__ == "__main__":
    main()
