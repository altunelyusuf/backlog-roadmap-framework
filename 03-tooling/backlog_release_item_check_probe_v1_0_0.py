#!/usr/bin/env python3
"""backlog_release_item_check_probe v1.0.0 -- GOV-S01/GOV-S02 shown to fire on real known-bad trees and stay silent on known-good
ones, on a real throwaway git repository (this tool had no self-proof before v1.5.0 -- G100/G101's own lesson: "a gate shown
only on good input proves nothing" applied to this gate itself, found while writing the G99 root-cause analysis).

Builds a tiny real git repo with a baseline tag, then for each case commits (or leaves uncommitted, to prove the untracked-file
fix) a change and checks the verdict:
  1 no governed file touched                              -> PASS, 0 changed
  2 a governed file is MODIFIED and left uncommitted       -> FAIL (the v1.4.0-and-before bug: this alone used to read as 0)
  3 a brand-new governed file is created, never git-added  -> FAIL (the untracked-file bug this release also fixes)
  4 same as 3, but a real item moved Proposed -> InProgress -> PASS
  5 same as 3, but the changelog carries a real "**Unplanned work:**" marker for the current version -> PASS
  6 same as 3, but the changelog mentions "unplanned" in prose with no marker                          -> still FAIL
Exit 0 all hold; 1 a case did not.
"""
import glob, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = sorted(glob.glob(os.path.join(HERE, "backlog_release_item_check_v*.py")),
              key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]])[-1]

bad = []


def check(name, cond):
    print("  %-4s %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        bad.append(name)


def git(args, cwd):
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def run_check(pkg, baseline, repo):
    r = subprocess.run([sys.executable, TOOL, pkg, baseline, "--repo-root", repo, "--package-prefix", "pkg/"],
                        capture_output=True, text=True)
    return r.returncode, r.stdout


def build_repo(d):
    repo = os.path.join(d, "repo")
    pkg = os.path.join(repo, "pkg")
    for sub in ("01-ontologies", "02-shacl-safeguards", "03-tooling", "04-documentation"):
        os.makedirs(os.path.join(pkg, sub))
    open(os.path.join(pkg, "01-ontologies", "backlog_abox_v1_0_0.ttl"), "w").write(
        "fw:S_One a backlog:Story ; backlog:hasState backlog:Proposed .\n")
    open(os.path.join(pkg, "03-tooling", "existing.py"), "w").write("# existing tool\n")
    open(os.path.join(pkg, "04-documentation", "CHANGELOG_v1_0_0.md"), "w").write(
        "## v1.0.0\nbaseline\n")
    open(os.path.join(pkg, "VERSION.txt"), "w").write("1.0.0\n")
    for cmd in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        git(cmd, repo)
    git(["add", "-A"], repo)
    git(["commit", "-q", "-m", "baseline"], repo)
    git(["tag", "pkg-v1.0.0"], repo)
    return repo, pkg


with tempfile.TemporaryDirectory() as d:
    repo, pkg = build_repo(d)

    # 1: doc-only change, committed
    open(os.path.join(pkg, "04-documentation", "CHANGELOG_v1_0_0.md"), "a").write("doc tweak\n")
    git(["add", "-A"], repo); git(["commit", "-q", "-m", "doc"], repo)
    code, out = run_check(pkg, "pkg-v1.0.0", repo)
    check("1 doc-only change: PASS, 0 governed files", code == 0 and "governed files changed: 0" in out)

    # 2: a governed file MODIFIED, left uncommitted (the pre-v1.5.0 bug)
    open(os.path.join(pkg, "03-tooling", "existing.py"), "a").write("# modified\n")
    code, out = run_check(pkg, "pkg-v1.0.0", repo)
    check("2 a modified governed file, uncommitted, is counted (not silently 0)", code == 1 and "governed files changed: 1" in out)
    git(["checkout", "--", "pkg/03-tooling/existing.py"], repo)  # revert for next case

    # 3: a brand-new governed file, never git-added
    open(os.path.join(pkg, "03-tooling", "brand_new.py"), "w").write("# new, untracked\n")
    code, out = run_check(pkg, "pkg-v1.0.0", repo)
    check("3 a new, never-git-added governed file is still caught", code == 1 and "governed files changed: 1" in out)

    # 4: same tree, but a real item moved
    open(os.path.join(pkg, "01-ontologies", "backlog_abox_v1_0_0.ttl"), "w").write(
        "fw:S_One a backlog:Story ; backlog:hasState backlog:InProgress .\n")
    code, out = run_check(pkg, "pkg-v1.0.0", repo)
    check("4 a real item movement overrides the FAIL", code == 0 and "VERDICT     : PASS -- real item movement" in out)
    open(os.path.join(pkg, "01-ontologies", "backlog_abox_v1_0_0.ttl"), "w").write(
        "fw:S_One a backlog:Story ; backlog:hasState backlog:Proposed .\n")  # revert

    # 5: no item movement, but a real "**Unplanned work:**" marker for the CURRENT version
    open(os.path.join(pkg, "VERSION.txt"), "w").write("1.1.0\n")
    open(os.path.join(pkg, "04-documentation", "CHANGELOG_v1_0_0.md"), "a").write(
        "\n## v1.1.0\n**Unplanned work:** a real, deliberate reason.\n")
    code, out = run_check(pkg, "pkg-v1.0.0", repo)
    check("5 a real unplanned-work marker for this version overrides the FAIL", code == 0 and "declares unplanned work" in out)

    # 6: prose MENTIONING "unplanned" with no real marker still FAILs
    open(os.path.join(pkg, "04-documentation", "CHANGELOG_v1_0_0.md"), "w").write(
        "## v1.0.0\nbaseline\ndoc tweak\n\n## v1.1.0\nSome unplanned-sounding prose, no real marker.\n")
    code, out = run_check(pkg, "pkg-v1.0.0", repo)
    check("6 prose mentioning 'unplanned' without the real marker still FAILs", code == 1 and "no unplanned-work marker found" in out)

print("VERDICT : " + ("ALL HOLD" if not bad else "FAILED -- " + "; ".join(bad)))
sys.exit(0 if not bad else 1)
