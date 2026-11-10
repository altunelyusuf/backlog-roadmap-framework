#!/usr/bin/env python3
"""Proof for C7 of the IPage box-tool-for-an-adopting-register handover, against backlog_box_step_v2_0_0.py:
the validator is found via a declared BRSF_ROOT (env var or --brsf-root), not only when it happens to sit beside the tool."""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "backlog_box_step_v2_0_0.py")
bad, COUNT = [], [0]


def expect(name, ok):
    COUNT[0] += 1
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok:
        bad.append(name)


def git(pk, *a):
    return subprocess.run(["git", "-C", pk] + list(a), capture_output=True, text=True)


work = tempfile.mkdtemp()
pk = os.path.join(work, "pkg")                 # the adopting package: NO validator beside its own tooling
os.makedirs(os.path.join(pk, "01-ontologies"))
os.makedirs(os.path.join(pk, "03-tooling"))
shutil.copy(TOOL, os.path.join(pk, "03-tooling", os.path.basename(TOOL)))
reg = os.path.join(pk, "01-ontologies", "ipage_abox_v0_1_0.ttl")
open(reg, "w").write("""@prefix pcl: <http://example.org/ipage-register#> .
@prefix backlog: <http://example.org/backlog#> .
pcl:D1 a backlog:Lineage ; backlog:hasLineageStatus backlog:LS_InProgress .
""")
git(pk, "init", "-q")
open(os.path.join(pk, "03-tooling", "other.py"), "w").write("x = 1\n")
git(pk, "add", "-A")
git(pk, "-c", "user.email=p@p", "-c", "user.name=p", "commit", "-qm", "p")
git(pk, "update-ref", "refs/remotes/origin/main", "HEAD")

frw = os.path.join(work, "framework")           # a separate checkout of the framework, with its own 03-tooling/validator
os.makedirs(os.path.join(frw, "03-tooling"))
open(os.path.join(frw, "03-tooling", "backlog_validate_v1_0_0.py"), "w").write(
    "import sys\nprint('VERDICT : CONFORMANT')\nsys.exit(0)\n")


def run(*extra):
    r = subprocess.run([sys.executable, os.path.join(pk, "03-tooling", os.path.basename(TOOL)), reg, "--lineage", "pcl:D1"] + list(extra),
                        capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


env_before = os.environ.pop("BRSF_ROOT", None)
rc, out = run("owes", "LS_InProgress")
expect("with no validator beside the tool and no BRSF_ROOT, nothing is checked (unchanged default)", "NOT CHECKED" in out)

rc, out = run("--brsf-root", frw, "owes", "LS_InProgress")
expect("--brsf-root points the tool at a validator in a separately checked-out framework (C7), so it IS checked this time", "NOT CHECKED" not in out and rc == 0)

if env_before is not None:
    os.environ["BRSF_ROOT"] = env_before
shutil.rmtree(work, ignore_errors=True)

print("VERDICT: %s" % ("PASS -- %d expectations hold" % COUNT[0] if not bad else "FAIL -- " + "; ".join(bad)))
sys.exit(1 if bad else 0)
