#!/usr/bin/env python3
"""backlog_version_freeze_check v1.0.0 -- G94.

Exists because LINEAGE_OPERATING_DISCIPLINE_v62_0_0.md was content-edited 67 times across this
package's history under one frozen filename, and nothing ever checked it. A version in a filename is
a BP-D7 claim: this content, this version. Nobody was verifying that claim stayed true.

Compares every versioned file in the current package against the SAME-NAMED file at the last real
published release (a real git tag, not a local guess). Same name, different content: the version
claim is false right now, not just historically -- refuse. Same name, same content: fine, nothing
changed. Different name: a real version bump happened, the mechanism this check exists to require.

Deliberately does not flag the 67 historical violations already in this package's git history --
reconstructing a version number nobody assigned at the time would be inventing a record, not proving
one. This checks the boundary going forward: does the CURRENT working tree still make a false claim
relative to the last real release.

Usage: backlog_version_freeze_check_v1_0_0.py <package_root> <baseline_tag>
       [--repo-root <path>] [--package-prefix <rel_path>]

Compares against a real git tag in the governed monorepo (not a derived public mirror -- that
transforms and excludes files, which produces false positives; found the hard way, disclosed.

Exit 0 and PASS, or exit 1 and name every filename whose content moved since the last release while
its own version claim stayed still.
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

VERSIONED_RE = re.compile(r"_v\d+_\d+_\d+\.(md|py|sh|ttl|js)$")
SKIP_DIRS = {".git", "__pycache__", "node_modules"}
# Files whose own convention is "one file, many entries appended under one version" -- a running
# log, not a versioned snapshot. Flagging these would be checking the wrong thing: a CHANGELOG's
# job IS to grow under its own filename across many releases.
APPEND_ONLY_RE = re.compile(r"^CHANGELOG_v\d+_\d+_\d+\.md$")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    argv = sys.argv[1:]
    if len(argv) < 2:
        print("usage: backlog_version_freeze_check_v1_0_0.py <package_root> <baseline_tag> "
              "[--repo-root <path>] [--package-prefix <rel_path>]")
        return 2
    root, tag = argv[0], argv[1]
    repo_root = argv[argv.index("--repo-root") + 1] if "--repo-root" in argv else "."
    prefix = argv[argv.index("--package-prefix") + 1] if "--package-prefix" in argv else ""

    r = subprocess.run(["git", "-C", repo_root, "ls-tree", "-r", "--name-only", tag, "--", prefix],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"error: could not read tag {tag}: {r.stderr.strip()}")
        return 2
    tag_files = [f for f in r.stdout.splitlines()
                 if VERSIONED_RE.search(f) and not APPEND_ONLY_RE.match(f.split("/")[-1])]

    violations = []
    checked = 0
    for f in tag_files:
        rel = f[len(prefix):] if prefix and f.startswith(prefix) else f
        local_path = Path(root) / rel
        if not local_path.exists():
            continue
        checked += 1
        old = subprocess.run(["git", "-C", repo_root, "show", f"{tag}:{f}"], capture_output=True).stdout
        if hashlib.sha256(old).hexdigest() != sha(local_path):
            violations.append(rel)

    print(f"versioned files checked  : {checked} (present in both current tree and {tag})")
    if violations:
        print(f"VERDICT     : FAIL - {len(violations)} file(s) content-changed with no version bump:")
        for v in sorted(violations):
            print(f"   {v}")
        return 1

    print("VERDICT     : PASS - every versioned file present in both is byte-identical, "
          "or its version changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
