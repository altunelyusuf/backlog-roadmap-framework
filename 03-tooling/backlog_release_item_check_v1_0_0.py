#!/usr/bin/env python3
"""backlog_release_item_check v1.0.0 -- GOV-S01.

The real, agreed gap: a package can publish a release whose governed files genuinely changed, while
not one real backlog item moved -- checked and confirmed on automate-python-book-3e (fourteen real
releases, zero item movement) and on this framework's own earlier, less formal infra fixes. This
tool closes it for the one direction GOV-S01 owns: detecting whether a real WorkItem left Proposed
in the same commit span a release's governed files changed in.

Scope, precisely: this checks item MOVEMENT, not the unplanned-work declaration escape hatch --
that mechanism belongs to GOV-S02, not yet built. --unplanned-reason exists here only as a minimal,
honest stub so this check can be exercised end to end; GOV-S02 will give it a real, checkable shape.

Method: compares the register's own WorkItem hasState values at the baseline tag against the
current working tree. A real movement is either an existing item whose hasState differs, or a new
item introduced already past Proposed. Governed files are 01-ontologies/, 02-shacl-safeguards/,
03-tooling/ under the package root -- documentation-only changes (CHANGELOG, README, standard prose)
never trigger this check, since they carry no claim about backlog-relevant work.

Usage: backlog_release_item_check_v1_0_0.py <package_root> <baseline_tag>
       [--repo-root <path>] [--package-prefix <rel_path>] [--unplanned-reason <text>]

Exit 0 and PASS if nothing governed changed, an unplanned-work reason was given, or a real item
moved. Exit 1 and FAIL, naming the span checked, if governed files changed and nothing moved.
"""
import subprocess
import sys
import re

GOVERNED_DIRS = ("01-ontologies/", "02-shacl-safeguards/", "03-tooling/")


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


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        sys.exit(2)
    package_root, baseline_tag = args[0], args[1]
    repo_root = package_root
    package_prefix = ""
    unplanned_reason = None
    i = 2
    while i < len(args):
        if args[i] == "--repo-root":
            repo_root = args[i + 1]; i += 2
        elif args[i] == "--package-prefix":
            package_prefix = args[i + 1]; i += 2
        elif args[i] == "--unplanned-reason":
            unplanned_reason = args[i + 1]; i += 2
        else:
            i += 1

    changed = changed_governed_files(repo_root, package_prefix, baseline_tag)
    print(f"baseline    : {baseline_tag}")
    print(f"governed files changed: {len(changed)}")
    if not changed:
        print("VERDICT     : PASS -- no governed file changed since baseline; nothing to account for")
        sys.exit(0)

    if unplanned_reason:
        print(f"declared    : unplanned work -- \"{unplanned_reason}\"")
        print("VERDICT     : PASS -- release declared as unplanned work")
        sys.exit(0)

    reg_path = register_path(repo_root, package_prefix)
    reg_rel = reg_path[len(repo_root) + 1:] if reg_path.startswith(repo_root) else reg_path
    rc, old_text, err = sh(["git", "show", f"{baseline_tag}:{reg_rel}"], repo_root)
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
    print("VERDICT     : FAIL -- governed files changed, no item moved, no unplanned-work reason given")
    sys.exit(1)


if __name__ == "__main__":
    main()
