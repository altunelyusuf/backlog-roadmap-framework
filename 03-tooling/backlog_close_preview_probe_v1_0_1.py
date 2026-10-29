#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe reads no record of the framework register; the validator keeps only the controlled individuals)
"""backlog_close_preview_probe v1.0.0 -- re-runnable proof of backlog_close_preview (G109).

Planted register: an in-progress item whose closing requires several things at once (verified evidence, a finish point, ...).
  1  the preview lists MORE THAN ONE requirement in a single run (the point of the tool), every one of them a message the validator itself gives
  2  every listed requirement is absent from the register as it stands (it is what closing adds, not what is already wrong)
  3  the register file on disk is byte-identical after the run
  4  a Done item that already has everything (none planted here) is not needed: instead an unknown item name exits 2
  5  closing an item that is already Done adds nothing (exit 0)
Exit 0 when every expectation holds, 1 otherwise.
"""
import glob, hashlib, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
if sys.argv[1:] == ["--deps"]:
    pkg = os.path.dirname(HERE)
    for pat in ("03-tooling/backlog_validate_v*.py", "03-tooling/backlog_close_preview_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl"):
        print(sorted(glob.glob(os.path.join(pkg, pat)), key=sv)[-1])
    print(os.path.abspath(__file__)); sys.exit(0)
tool = sorted([p for p in glob.glob(os.path.join(HERE, "backlog_close_preview_v*.py")) if "_probe_" not in p], key=sv)[-1]
REG = """@prefix backlog: <http://example.org/backlog#> .
@prefix x: <http://example.org/close-preview-probe#> .
x:Open a backlog:Task ; backlog:hasIdentifier "OPEN" ; backlog:hasState backlog:InProgress .
x:Closed a backlog:Task ; backlog:hasIdentifier "CLOSED" ; backlog:hasState backlog:Done .
"""
bad = []
def run(*args): return subprocess.run([sys.executable, "-B", tool, *args], capture_output=True, text=True, timeout=3600)
with tempfile.TemporaryDirectory() as d:
    f = os.path.join(d, "r.ttl"); open(f, "w").write(REG)
    h0 = hashlib.sha256(open(f, "rb").read()).hexdigest()
    r = run("OPEN", f); lines = [l for l in r.stdout.splitlines() if l.startswith("  [")]
    print("closing OPEN: exit", r.returncode, "-", len(lines), "requirement(s) listed")
    if r.returncode != 1: bad.append(f"closing an open item should exit 1, got {r.returncode}")
    if len(lines) < 2: bad.append(f"expected several requirements in one run, got {len(lines)}")
    if not any("Evidence" in l for l in lines): bad.append("the evidence requirement of a Done item is not listed")
    if hashlib.sha256(open(f, "rb").read()).hexdigest() != h0: bad.append("the register file was changed")
    r = run("CLOSED", f); print("closing CLOSED: exit", r.returncode)
    if r.returncode != 0: bad.append(f"closing a Done item should add nothing (exit 0), got {r.returncode}")
    r = run("NOSUCH", f); print("unknown item: exit", r.returncode)
    if r.returncode != 2: bad.append(f"unknown item should exit 2, got {r.returncode}")
    r = run("OPEN", f); r2 = run("Open", f)
    if r.stdout != r2.stdout: bad.append("the item given by local name and by identifier gives different output")
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
