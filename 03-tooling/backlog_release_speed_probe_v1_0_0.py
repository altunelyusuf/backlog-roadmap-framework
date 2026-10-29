#!/usr/bin/env python3
"""backlog_release_speed_probe v1.0.0 -- the release tool 1.6.0 does what it says (Lineage 22).

Cases: preflight stops on a register that does not validate and on a failed archive integrity check and lets a valid one through; `roll` moves the register and the
change-log to their next versions, inserts the entry above the newest one and makes PROBE_INPUTS.json follow, and refuses without an account of unplanned work; the gate
receipt is written when the head of the target repository can be read, is valid for the same bytes and head, is invalid after a changed byte or a moved head, and is not
written when the head cannot be read."""
import glob, importlib.util, json, os, re, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
tool = sorted(glob.glob(os.path.join(HERE, "backlog_release_tool_v*.py")), key=sv)[-1]
rcp = sorted(glob.glob(os.path.join(REPO, "repo-tooling", "oe_gate_receipt_v*.py")), key=sv)[-1:]
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(tool)
    print(sorted(glob.glob(os.path.join(HERE, "backlog_gate_v*.sh")), key=sv)[-1])
    for r in rcp: print(r)
    sys.exit(0)
bad = []
def expect(n, ok):
    print(("PASS  " if ok else "FAIL  ") + n)
    if not ok: bad.append(n)
def git(d, *a): return subprocess.run(["git", "-c", "user.email=p@p", "-c", "user.name=p", *a], cwd=d, capture_output=True, text=True, check=True).stdout
HDR = 'owl:versionInfo "1.5.0" ;\n owl:versionIRI <http://example.org/backlog/abox/1.5.0> ;\n owl:priorVersion <http://example.org/backlog/abox/1.4.0> .\n'

with tempfile.TemporaryDirectory() as t:
    git(t, "init", "-q", "--bare", "-b", "main", "origin.git"); git(t, "clone", "-q", "origin.git", "a")
    a = os.path.join(t, "a"); pkg = os.path.join(a, "backlog-roadmap-framework")
    for d in ("03-tooling", "01-ontologies", "04-documentation", "06-package-provenance"): os.makedirs(os.path.join(pkg, d))
    shutil.copy(tool, pkg + "/03-tooling/" + os.path.basename(tool))
    open(pkg + "/VERSION.txt", "w").write("1.0.0\n")
    open(pkg + "/04-documentation/CHANGELOG_v1_9_0.md", "w", encoding="utf-8").write("## v1.0.1 — 2026-01-01 (x)\n\nbody\n\n**Unplanned work:** none\n\n## v1.0.0 — 2026-01-01 (y)\n\nold\n")
    open(pkg + "/01-ontologies/backlog_abox_v1_5_0.ttl", "w").write("<http://example.org/backlog/abox> a owl:Ontology ;\n " + HDR)
    open(pkg + "/06-package-provenance/PROBE_INPUTS.json", "w").write(json.dumps({"p": ["01-ontologies/backlog_abox_v1_5_0.ttl", "04-documentation/CHANGELOG_v1_9_0.md"]}))
    val = pkg + "/03-tooling/backlog_validate_v1_0_0.py"
    open(val, "w").write("import sys\nprint('  [Violation] Mission_X   L3: it does not say where it stands') if open(sys.argv[1]).read().count('BAD') else None\nsys.exit(1 if open(sys.argv[1]).read().count('BAD') else 0)\n")
    ai = pkg + "/03-tooling/backlog_archive_integrity_v1_0_0.py"
    open(ai, "w").write("import os,sys\nprint('VERDICT : BROKEN')\nsys.exit(1 if os.path.exists('BROKEN') else 0)\n")
    git(a, "add", "-A"); git(a, "commit", "-q", "-m", "base"); git(a, "push", "-q", "origin", "HEAD:main")
    T = pkg + "/03-tooling/" + os.path.basename(tool)
    pre = lambda: subprocess.run([sys.executable, "-B", T, "preflight", "1.0.1"], capture_output=True, text=True, cwd=pkg).stdout
    out = pre()
    expect("a register that validates is not stopped by preflight", "does not validate" not in out)
    open(pkg + "/01-ontologies/backlog_abox_v1_5_0.ttl", "a").write("# BAD\n")
    out = pre()
    expect("a register that does not validate stops preflight and the violation is named", "the register does not validate" in out and "Mission_X" in out and "STOP" in out)
    open(pkg + "/01-ontologies/backlog_abox_v1_5_0.ttl", "w").write("<http://example.org/backlog/abox> a owl:Ontology ;\n " + HDR)
    open(pkg + "/BROKEN", "w").write("x")
    expect("a failed archive integrity check stops preflight", "archive integrity" in pre())
    os.remove(pkg + "/BROKEN")

    # roll
    r = subprocess.run([sys.executable, "-B", T, "roll", "1.0.1", "--title", "MINOR: t", "--body", "the body", "--unplanned", "none beyond the stage"], capture_output=True, text=True, cwd=pkg)
    expect("roll renames the register to its next version and moves its header", os.path.exists(pkg + "/01-ontologies/backlog_abox_v1_6_0.ttl") and not os.path.exists(pkg + "/01-ontologies/backlog_abox_v1_5_0.ttl") and 'owl:versionInfo "1.6.0"' in open(pkg + "/01-ontologies/backlog_abox_v1_6_0.ttl").read())
    cl = pkg + "/04-documentation/CHANGELOG_v1_10_0.md"
    txt = open(cl, encoding="utf-8").read() if os.path.exists(cl) else ""
    new_at, old_at = txt.find("(MINOR: t)"), txt.find("(x)")
    expect("roll renames the change-log and inserts the entry above the newest one with the unplanned-work line", new_at != -1 and 0 <= new_at < old_at and "**Unplanned work:** none beyond the stage" in txt[new_at:old_at] and not os.path.exists(pkg + "/04-documentation/CHANGELOG_v1_9_0.md"))
    pi = open(pkg + "/06-package-provenance/PROBE_INPUTS.json").read()
    expect("PROBE_INPUTS.json follows the new names", "backlog_abox_v1_6_0.ttl" in pi and "CHANGELOG_v1_10_0.md" in pi and "backlog_abox_v1_5_0" not in pi and "CHANGELOG_v1_9_0" not in pi)
    r = subprocess.run([sys.executable, "-B", T, "roll", "1.0.2", "--title", "t", "--body", "b"], capture_output=True, text=True, cwd=pkg)
    expect("roll without an account of unplanned work is refused", r.returncode != 0 and "REFUSED" in r.stdout)

    # receipt
    if rcp:
        spec = importlib.util.spec_from_file_location("rt", pkg + "/03-tooling/" + os.path.basename(tool)); rt = importlib.util.module_from_spec(spec); spec.loader.exec_module(rt)
        pubdir = os.path.join(t, "pubtools"); os.makedirs(pubdir); shutil.copy(rcp[0], pubdir)
        os.environ["OE_TARGET_URL"] = os.path.join(t, "origin.git")
        head = rt.origin_head()
        expect("the head of the target repository is read the way the publisher reads it", len(head) == 40)
        expect("the receipt is written when the head can be read", rt.write_receipt(pkg, pubdir, 7) and os.path.exists(rt.receipt_path(pkg)))
        chk = lambda h: subprocess.run([sys.executable, "-B", rcp[0], "check", pkg, "--origin", h], capture_output=True, text=True).returncode
        expect("the receipt is valid for the same bytes and the same head", chk(head) == 0)
        expect("the receipt is invalid when the head of the target has moved", chk("0" * 40) == 1)
        open(pkg + "/VERSION.txt", "w").write("1.0.9\n")
        expect("the receipt is invalid after one changed byte of the package", chk(head) == 1)
        os.remove(rt.receipt_path(pkg))
        os.environ["OE_TARGET_URL"] = os.path.join(t, "nowhere.git")
        expect("no receipt is written when the head cannot be read", rt.write_receipt(pkg, pubdir, 7) is False and not os.path.exists(rt.receipt_path(pkg)))
    else:
        expect("the receipt tool is present next to the publisher", False)
gate = sorted(glob.glob(os.path.join(HERE, "backlog_gate_v*.sh")), key=sv)[-1]
gt = open(gate, encoding="utf-8").read()
expect("the gate takes the newest register when it is run without an argument, before its register section", 'set -- "$_DEFREG"' in gt and 0 <= gt.index('set -- "$_DEFREG"') < gt.index("== Register under test =="))
print("VERDICT   :", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
