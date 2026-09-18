#!/usr/bin/env python3
"""backlog_release_item_check v1.2.0 -- GOV-S01, GOV-S02.

The real, agreed gap: a package can publish a release whose governed files genuinely changed, while
not one real backlog item moved -- checked and confirmed on automate-python-book-3e (fourteen real
releases, zero item movement) and on this framework's own earlier, less formal infra fixes. This
tool closes it for both directions the owner agreed to: detecting whether a real WorkItem left
Proposed in the same commit span a release's governed files changed in (GOV-S01), and, failing
that, whether the release explicitly declared itself unplanned work in its own permanent record
(GOV-S02) -- not a throwaway --unplanned-reason flag with nothing behind it, but a real statement
written into the same changelog every real release in this package already carries.

Method: compares the register's own WorkItem hasState values at the baseline tag against the
current working tree. A real movement is either an existing item whose hasState differs, or a new
item introduced already past Proposed. Governed files are 01-ontologies/, 02-shacl-safeguards/,
03-tooling/ under the package root -- documentation-only changes (CHANGELOG, README, standard prose)
never trigger this check, since they carry no claim about backlog-relevant work.

Failing that, looks for a real unplanned-work statement: the changelog entry matching the package's
own current VERSION.txt must contain a line starting with "**Unplanned work:**" -- a specific,
deliberate marker, not any prose that happens to mention the phrase. A version bump with no matching
changelog entry, or a changelog entry with no such marker, is read as no declaration at all.

Usage: backlog_release_item_check_v1_1_0.py <package_root> <baseline_tag>
       [--repo-root <path>] [--package-prefix <rel_path>]

Exit 0 and PASS if nothing governed changed, a real item moved, or the changelog carries a real
unplanned-work marker for the current version. Exit 1 and FAIL, naming the span checked, otherwise.
"""
import subprocess
import sys
import re
import glob
import os

GOVERNED_DIRS = ("01-ontologies/", "02-shacl-safeguards/", "03-tooling/")
UNPLANNED_MARKER = re.compile(r'^\*\*Unplanned work:\*\*\s*(.+)$', re.MULTILINE)


def sh(args, cwd):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def changed_governed_files(repo_root, package_prefix, baseline_tag):
    rc, out, err = sh(["git", "diff", "--name-only", f"{baseline_tag}..HEAD"], repo_root)
    if rc != 0:
        print(f"GATE ABORT: git diff against {baseline_tag} failed: {err.strip()}")
        sys.exit(3)
    changed = []
    for line in out.splitlines():
        if not line.startswith(package_prefix):
            continue
        rel = line[len(package_prefix):]
        if any(rel.startswith(d) for d in GOVERNED_DIRS):
            changed.append(rel)
    return changed


def register_path(repo_root, package_prefix):
    rc, out, err = sh(["bash", "-c",
                        f"ls {repo_root}/{package_prefix}01-ontologies/backlog_framework_register_abox_v*.ttl "
                        f"| sort -V | tail -1"], repo_root)
    p = out.strip()
    if not p:
        print("GATE ABORT: no backlog_framework_register_abox_v*.ttl resolved")
        sys.exit(3)
    return p


def register_path_at_tag(repo_root, package_prefix, tag):
    """The register is a versioned file, renamed almost every real publish -- its filename at an
    old tag is not necessarily the same as the current one. Resolved independently via git
    ls-tree, not assumed to match the current working tree's own glob result."""
    rc, out, err = sh(["git", "ls-tree", "-r", "--name-only", tag,
                        f"{package_prefix}01-ontologies/"], repo_root)
    if rc != 0:
        print(f"GATE ABORT: git ls-tree at {tag} failed: {err.strip()}")
        sys.exit(3)
    candidates = sorted(
        l for l in out.splitlines()
        if re.search(r'backlog_framework_register_abox_v[\d_]+\.ttl$', l))
    if not candidates:
        print(f"GATE ABORT: no backlog_framework_register_abox_v*.ttl found at {tag}")
        sys.exit(3)
    return candidates[-1]


def item_states(ttl_text):
    """Real subjects with a real hasState, by identifier pattern -- deliberately regex-based,
    not rdflib: this must read the register AT AN OLD TAG via git show, where importing the
    file into a full graph would need every co-versioned TBox/shapes file at that same tag too.
    A regex over 'subject a backlog:Story/ExecutionTask' blocks and their hasState is a narrower,
    honest tool for exactly this one comparison."""
    states = {}
    for m in re.finditer(
        r'(fw:\S+)\s+a\s+backlog:(?:Story|ExecutionTask)\s*;.*?backlog:hasState\s+backlog:(\w+)',
        ttl_text, re.DOTALL):
        subj, state = m.group(1), m.group(2)
        if subj not in states:
            states[subj] = state
    return states


def declared_unplanned_reason(package_root, package_prefix, repo_root):
    """Reads the package's own current VERSION.txt and the changelog, and returns the real
    unplanned-work statement for that exact version if one is written -- never a runtime flag."""
    vpath = os.path.join(package_root, "VERSION.txt")
    if not os.path.exists(vpath):
        return None
    with open(vpath) as f:
        version = f.read().strip()
    changelogs = glob.glob(os.path.join(package_root, "04-documentation", "CHANGELOG_v*.md"))
    if not changelogs:
        return None
    changelog_path = sorted(changelogs)[-1]
    with open(changelog_path) as f:
        text = f.read()
    # Find the section for this exact version: "## vVERSION —" through the next "## v" or EOF.
    pattern = re.compile(
        rf'^## v{re.escape(version)}\b.*?(?=^## v|\Z)', re.MULTILINE | re.DOTALL)
    m = pattern.search(text)
    if not m:
        return None
    marker = UNPLANNED_MARKER.search(m.group(0))
    return marker.group(1).strip() if marker else None


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        sys.exit(2)
    package_root, baseline_tag = args[0], args[1]
    repo_root = package_root
    package_prefix = ""
    i = 2
    while i < len(args):
        if args[i] == "--repo-root":
            repo_root = args[i + 1]; i += 2
        elif args[i] == "--package-prefix":
            package_prefix = args[i + 1]; i += 2
        else:
            i += 1

    changed = changed_governed_files(repo_root, package_prefix, baseline_tag)
    print(f"baseline    : {baseline_tag}")
    print(f"governed files changed: {len(changed)}")
    if not changed:
        print("VERDICT     : PASS -- no governed file changed since baseline; nothing to account for")
        sys.exit(0)

    reg_path = register_path(repo_root, package_prefix)
    reg_rel_at_baseline = register_path_at_tag(repo_root, package_prefix, baseline_tag)
    rc, old_text, err = sh(["git", "show", f"{baseline_tag}:{reg_rel_at_baseline}"], repo_root)
    if rc != 0:
        print(f"GATE ABORT: could not read register at {baseline_tag}: {err.strip()}")
        sys.exit(3)
    with open(reg_path) as f:
        new_text = f.read()

    old_states = item_states(old_text)
    new_states = item_states(new_text)

    moved = []
    for subj, new_state in new_states.items():
        old_state = old_states.get(subj)
        if old_state is None:
            if new_state != "Proposed":
                moved.append((subj, "new", new_state))
        elif old_state != new_state:
            moved.append((subj, old_state, new_state))

    if moved:
        print(f"items moved : {len(moved)}")
        for subj, old_s, new_s in moved[:5]:
            print(f"  {subj}: {old_s} -> {new_s}")
        print("VERDICT     : PASS -- real item movement found in this span")
        sys.exit(0)

    print("items moved : 0")
    reason = declared_unplanned_reason(package_root, package_prefix, repo_root)
    if reason:
        print(f"declared    : unplanned work -- \"{reason}\"")
        print("VERDICT     : PASS -- release's own changelog declares unplanned work")
        sys.exit(0)

    print("declared    : no unplanned-work marker found in the changelog entry for this version")
    print("VERDICT     : FAIL -- governed files changed, no item moved, no unplanned-work declared")
    sys.exit(1)


if __name__ == "__main__":
    main()

