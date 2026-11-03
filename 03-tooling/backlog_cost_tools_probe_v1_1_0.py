#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe reads no record of the framework register; it builds throw-away repositories and logs)
"""backlog_cost_tools_probe v1.1.0 -- proof that the three cost-saving tools discriminate (G195; Lineage 30).

The scenarios are run against the real tools (every expectation must hold) and then against MUTANTS: copies of the tools with one key behaviour made wrong, each of which
must fail at least one scenario ("when its key behaviour is made wrong, the probe fails"). A mutant whose text is not found is itself a failure (a stale mutant proves nothing).
  (a ceremony that prints NOT anywhere is also refused; a pass of the digest needs the gate's own closing line)
  session_start   integers not text order; NEVER READ / UNCHANGED / CHANGED with the changed line; the record is written only by --ack (a second run still says CHANGED);
                  not READY until read; origin's bytes, not the working copy; the fetch; behind origin; the ceremony counts only with exit 0, a last PROCEED and no REFUSE
  gate_digest     the failing section with its lines; clean log silent; a zero-count line is no failure; FAILURE / REFUSE / ABORT / ERROR / Traceback / NEW FAILURE are seen
                  under a passing last verdict; a failing closing line is never a pass
  probe_changed   only changed probes; --own; declared and measured inputs; committed-but-unpublished work counts; a change outside the package counts; a failing probe exits 1
Exit 0 when every expectation holds and every mutant is caught, 1 otherwise."""
import glob, json, os, re, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda n: sorted(glob.glob(os.path.join(HERE, n + "_v*.py")), key=sv)[-1]
SS, GD, PC = latest("backlog_session_start"), latest("backlog_gate_digest"), latest("backlog_probe_changed")
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(SS); print(GD); print(PC); sys.exit(0)
def git(d, *a):
    for attempt in (1, 2):
        r = subprocess.run(["git", "-c", "user.email=p@p", "-c", "user.name=p", *a], cwd=d, capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout
    raise RuntimeError("git %s failed twice: %s" % (" ".join(a), r.stderr.strip()[:300]))
def run(*a): r = subprocess.run([sys.executable, "-I", *a], capture_output=True, text=True, timeout=300); return r.returncode, r.stdout + r.stderr
def make_origin(root, folder, files):
    bare = os.path.join(root, "origin.git"); subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True)
    work = os.path.join(root, "work"); subprocess.run(["git", "clone", "-q", bare, work], capture_output=True, check=True)
    os.makedirs(os.path.join(work, folder), exist_ok=True)
    for n, t in files.items(): open(os.path.join(work, folder, n), "w").write(t)
    git(work, "add", "-A"); git(work, "commit", "-q", "-m", "one"); git(work, "branch", "-M", "main"); git(work, "push", "-q", "origin", "main")
    return work

def scenarios(ss, gd, pc, which=("ss", "gd", "pc")):
    """[(name, held)] for the three tools at the given paths."""
    res = []
    def expect(name, ok): res.append((name, bool(ok)))
    with tempfile.TemporaryDirectory() as t:
        if "ss" in which:
            LD = "LINEAGE_OPERATING_DISCIPLINE_v%d_0_0.md"; OD = "OE_Operating_Discipline_v%s.md"
            pub = make_origin(os.path.join(t, "p"), "04-documentation", {LD % 9: "nine\n", LD % 71: "seventy-one\n", LD % 110: "one-ten\nline two\n"})
            mono = make_origin(os.path.join(t, "m"), "oe-method/04-documentation", {OD % "2_9_0": "old oe\n", OD % "2_37_0": "oe thirty-seven\n"})
            state = os.path.join(t, "state")
            base = ["--public", pub, "--mono", mono, "--state", state, "--no-ceremony"]
            rc, out = run(ss, *base)
            expect("ss: v110 over v71 and v9 (integers, not text)", "LINEAGE_OPERATING_DISCIPLINE_v110_0_0.md" in out and "_v71_" not in out and "_v9_" not in out)
            expect("ss: OE v2_37_0 over v2_9_0", "OE_Operating_Discipline_v2_37_0.md" in out)
            expect("ss: never read: NEVER READ and not READY until acknowledged", out.count("NEVER READ") == 2 and rc == 1 and "NOT READY" in out)
            rc, out = run(ss, *base, "--ack")
            expect("ss: --ack records and is READY", rc == 0 and "SESSION START: READY" in out)
            rc, out = run(ss, *base)
            expect("ss: UNCHANGED the next time, READY", out.count("UNCHANGED") == 2 and "NEVER READ" not in out and rc == 0)
            # origin's bytes, not the working copy: the working copy is edited and not committed
            open(os.path.join(pub, "04-documentation", LD % 110), "w").write("working copy only\n")
            rc, out = run(ss, *base)
            expect("ss: the working copy does not count: origin's bytes are compared", out.count("UNCHANGED") == 2 and rc == 0)
            git(pub, "checkout", "--", ".")
            # origin changes in another clone, this one has not fetched: the tool must fetch
            other = os.path.join(t, "other"); subprocess.run(["git", "clone", "-q", os.path.join(t, "p", "origin.git"), other], capture_output=True, check=True)
            open(os.path.join(other, "04-documentation", LD % 110), "w").write("one-ten\nline TWO changed\n")
            git(other, "add", "-A"); git(other, "commit", "-q", "-m", "change"); git(other, "push", "-q", "origin", "main")
            rc, out = run(ss, *base)
            expect("ss: CHANGED with the changed line, fetched from origin", "CHANGED" in out and "+line TWO changed" in out and "-line two" in out)
            expect("ss: a changed discipline is not READY until acknowledged, and BEHIND is reported", rc == 1 and "NOT READY" in out and "BEHIND" in out)
            rc, out = run(ss, *base)
            ll = [l for l in out.splitlines() if l.startswith("lineage discipline")]
            expect("ss: the record is not overwritten by a run without --ack: still CHANGED", bool(ll) and " CHANGED " in ll[0] and "UNCHANGED" not in ll[0])
            git(pub, "pull", "-q", "origin", "main")
            rc, out = run(ss, *base, "--ack")
            rc, out = run(ss, *base)
            expect("ss: after --ack and an update the next run is UNCHANGED and READY", out.count("UNCHANGED") == 2 and rc == 0 and "BEHIND" not in out)
            # the ceremony
            def ceremony(body, code):
                p = os.path.join(t, "cer.sh"); open(p, "w").write("#!/bin/bash\n" + body + "\nexit %d\n" % code)
                return run(ss, "--public", pub, "--mono", mono, "--state", state, "--ceremony", p)
            rc, out = ceremony('if [ "$1" = "backlog-roadmap-framework" ]; then echo "VERDICT: PROCEED"; else echo "VERDICT: HOLD"; fi', 0)
            expect("ss: the ceremony is run with the package name", rc == 0 and "SESSION START: READY" in out)
            rc, out = ceremony('echo "VERDICT: PROCEED   all well"', 0)
            expect("ss: a ceremony that says PROCEED and exits 0 is READY", rc == 0 and "SESSION START: READY" in out)
            rc, out = ceremony('echo "VERDICT: PROCEED"\necho "REFUSE something later"', 0)
            expect("ss: a REFUSE line beside PROCEED is NOT READY", rc == 1 and "NOT READY" in out)
            rc, out = ceremony('echo "VERDICT: PROCEED"', 1)
            expect("ss: a ceremony that exits 1 is NOT READY even with a PROCEED line", rc == 1 and "NOT READY" in out)
            rc, out = ceremony('echo "VERDICT: PROCEED"\necho "VERDICT: HOLD   stop"', 0)
            expect("ss: the LAST verdict counts: PROCEED then HOLD is NOT READY", rc == 1 and "NOT READY" in out)
            rc, out = ceremony('echo "nothing"', 0)
            expect("ss: no verdict line is NOT READY", rc == 1 and "NOT READY" in out)
            # behind origin, after everything else holds
            open(os.path.join(other, "04-documentation", "x.md"), "w").write("x\n"); git(other, "add", "-A"); git(other, "commit", "-q", "-m", "x"); git(other, "push", "-q", "origin", "main")
            rc, out = run(ss, *base)
            expect("ss: a repository behind origin is reported and NOT READY", "BEHIND" in out and rc == 1 and "NOT READY" in out)
            # ack order, fetch failure, no ceremony script, empty bytes, loose ceremony words
            git(pub, "pull", "-q", "origin", "main")      # up to date again, so a READY below is possible and a refusal is the tool's own
            run(ss, *base, "--ack")
            st2 = os.path.join(t, "state2")
            rc, out = run(ss, "--public", pub, "--mono", mono, "--state", st2, "--no-ceremony", "--ack")
            expect("ss: --ack on a version never shown is refused and NOT READY", "--ack refused" in out and rc == 1 and "NOT READY" in out)
            run(ss, "--public", pub, "--mono", mono, "--state", st2, "--no-ceremony")
            rc, out = run(ss, "--public", pub, "--mono", mono, "--state", st2, "--no-ceremony", "--ack")
            expect("ss: shown first, then --ack, is READY", "acknowledged" in out and "NOT READY" not in out and rc == 0 or "BEHIND" in out)
            broken = os.path.join(t, "broken"); subprocess.run(["git", "clone", "-q", os.path.join(t, "p", "origin.git"), broken], capture_output=True, check=True)
            git(broken, "remote", "set-url", "origin", os.path.join(t, "nowhere.git"))
            rc, out = run(ss, "--public", broken, "--mono", mono, "--state", st2, "--no-ceremony")
            expect("ss: a fetch that fails is NOT READY", "cannot fetch" in out and rc == 1 and "NOT READY" in out)
            bare_mono = os.path.join(t, "bm"); os.makedirs(bare_mono); subprocess.run(["git", "clone", "-q", os.path.join(t, "m", "origin.git"), os.path.join(bare_mono, "c")], capture_output=True, check=True)
            rc, out = run(ss, "--public", pub, "--mono", os.path.join(bare_mono, "c"), "--state", st2)
            expect("ss: no ceremony script is NOT READY", "no oe_ceremony" in out and rc == 1 and "NOT READY" in out)
            pe = make_origin(os.path.join(t, "pe"), "04-documentation", {LD % 1: ""}); me = make_origin(os.path.join(t, "me"), "oe-method/04-documentation", {OD % "2_1_0": "x\n"})
            rc, out = run(ss, "--public", pe, "--mono", me, "--state", os.path.join(t, "st3"), "--no-ceremony")
            expect("ss: a discipline file with no bytes on origin is NOT READY and not acknowledged", "cannot read" in out and rc == 1)
            rc, out = ceremony('echo "VERDICT: PROCEED"\necho "REFUSED: x"', 0)
            expect("ss: REFUSED beside PROCEED is NOT READY", rc == 1 and "NOT READY" in out)
            rc, out = ceremony('echo "VERDICT: PROCEEDS"', 0)
            expect("ss: a verdict that only starts with PROCEED is NOT READY", rc == 1 and "NOT READY" in out)
        if "gd" in which:
            # gate digest
            def digest(text):
                p = os.path.join(t, "g.log"); open(p, "w").write(text); return run(gd, p)
            rc, out = digest("== Section A ==\n  ok\n== Section B ==\n  declaration FAILED : 0\n  X check FAILED — the cause\n== Section C ==\nRELEASE GATE: FAIL — see above\n")
            expect("gd: the failing section is printed and exit is 1", rc == 1 and "FAIL in: Section B" in out and "the cause" in out and "FAIL in: Section A" not in out)
            rc, out = digest("== Section A ==\n  ok\n  declaration FAILED : 0\nRELEASE GATE: PASS\n")
            expect("gd: a clean log shows no failure; a zero-count line is none; exit 0", rc == 0 and "FAIL in" not in out and "last verdict: RELEASE GATE: PASS" in out)
            for word in ("VIOLATION found", "NEW FAILURE x", "REFUSE the thing", "ABORT: stop", "ERROR reading", "Traceback (most recent call last):", "check FAILURE here"):
                rc, out = digest("== Section A ==\n  ok\n== Section B ==\n  %s\n== Section C ==\n  ok\nRELEASE GATE: PASS\n" % word)
                expect("gd: '%s' under a passing last verdict is seen and exit 1" % word[:14], rc == 1 and "FAIL in: Section B" in out)
            rc, out = digest("== Section A ==\n  ok\nRELEASE GATE: FAIL — one gate failed\nVERDICT : PASS\n")
            expect("gd: a failing closing line is the authority even when a passing verdict line follows it", rc == 1)
            rc, out = digest("== Distribution-drift gate — is the public copy current? ==\n  Distribution-drift gate FAILED\nRELEASE GATE: FAIL — see the failing gate above; release blocked.\n")
            expect("gd: the drift-only failure of an unpublished version is shown with a note and the exit stays 1", rc == 1 and "only the drift check failed" in out and "FAIL in: Distribution-drift" in out)
            rc, out = digest("== Distribution-drift gate — x ==\n  Distribution-drift gate FAILED\n== Other ==\n  X check FAILED — real\nRELEASE GATE: FAIL\n")
            expect("gd: the drift check plus another failure is a failure", rc == 1)
            rc, out = digest("== Section A ==\n  VERDICT : FAIL — a check says so\nRELEASE GATE: PASS\n")
            expect("gd: a failing VERDICT line alone is seen even under a passing closing line", rc == 1 and "FAIL in: Section A" in out)
            rc, out = digest("== Section A ==\n  ok\n")
            expect("gd: no verdict line is exit 1", rc == 1)
            rc, out = digest("== Section A ==\n  ok\nVERDICT : PASS\n")
            expect("gd: a truncated log with a passing sub-verdict and no closing line is exit 1", rc == 1)
            rc, out = digest("== Section A ==\n  ok\nRELEASE GATE (LIGHT, stage release): PASS — the chain clears\n")
            expect("gd: the light gate's passing closing line is a pass", rc == 0)
            DR = "== Distribution-drift gate — is the public copy current? ==\n  Distribution-drift gate FAILED\n"
            rc, out = digest("== Section A ==\n  VERDICT : FAIL — the package contains files coverage cannot account for\n" + DR + "RELEASE GATE: FAIL\n")
            expect("gd: a failing verdict line of another check beside the drift check is a failure", rc == 1)
            rc, out = digest("== Distribution-drift gate — is the public copy current? ==\n  Distribution-drift gate FAILED\n  Traceback (most recent call last):\nRELEASE GATE: FAIL\n")
            expect("gd: a Traceback inside the drift section is a failure", rc == 1)
            rc, out = digest("== Distribution-drift gate — something else ==\n  Distribution-drift gate FAILED\nRELEASE GATE: FAIL\n")
            expect("gd: a section whose name only starts like the drift check is a failure", rc == 1)
            rc, out = digest(DR)
            expect("gd: the drift failure with no closing line is a failure", rc == 1)
        if "pc" in which:
            # probe changed: a package inside a repository with an origin
            root = os.path.join(t, "repo"); bare = os.path.join(t, "repo.git"); subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True)
            subprocess.run(["git", "clone", "-q", bare, root], capture_output=True, check=True)
            pk = os.path.join(root, "pkg"); os.makedirs(os.path.join(pk, "03-tooling")); os.makedirs(os.path.join(pk, "01-ontologies")); os.makedirs(os.path.join(pk, "06-package-provenance"))
            open(os.path.join(root, "outside.txt"), "w").write("o\n")
            open(os.path.join(pk, "03-tooling", "backlog_gate_v1_0_0.sh"), "w").write('PROBE_LIST="a_probe b_probe c_probe e_probe"\n')
            for n, dep in (("a_probe", "data_a.ttl"), ("b_probe", "data_b.ttl"), ("c_probe", None), ("e_probe", "data_e.ttl")):
                if dep and n != "e_probe": open(os.path.join(pk, "01-ontologies", dep), "w").write("x\n")
                deps = ("os.path.abspath(os.path.join(H,'..','01-ontologies','%s'))" % dep) if dep else "os.path.abspath(os.path.join(H,'..','..','outside.txt'))"
                open(os.path.join(pk, "03-tooling", n + "_v1_0_0.py"), "w").write("import sys,os\nH=os.path.dirname(os.path.abspath(__file__))\nif sys.argv[1:]==['--deps']:\n    print(%s); sys.exit(0)\nsys.exit(0)\n" % deps)
            json.dump({"format": 1, "probes": {"b_probe": {"files": ["01-ontologies/measured_b.ttl"]}}}, open(os.path.join(pk, "06-package-provenance", "PROBE_INPUTS.json"), "w"))
            open(os.path.join(pk, "01-ontologies", "measured_b.ttl"), "w").write("m\n")
            git(root, "add", "-A"); git(root, "commit", "-q", "-m", "base"); git(root, "branch", "-M", "main"); git(root, "push", "-q", "origin", "main")
            rc, out = run(pc, pk, "--list")
            expect("pc: nothing changed lists nothing", rc == 0 and "to run first: 0" in out)
            open(os.path.join(pk, "01-ontologies", "data_a.ttl"), "w").write("changed\n")
            rc, out = run(pc, pk, "--list")
            expect("pc: only the probe whose declared input changed", "a_probe_v1_0_0.py" in out and "b_probe" not in out and "c_probe" not in out and "to run first: 1" in out)
            rc, out = run(pc, pk, "--own", "--list")
            expect("pc: --own lists none when only an input changed", "to run first: 0" in out)
            git(root, "add", "-A"); git(root, "commit", "-q", "-m", "local, not pushed")
            rc, out = run(pc, pk, "--list")
            expect("pc: committed but unpublished work still counts", "a_probe_v1_0_0.py" in out and "to run first: 1" in out)
            rc, out = run(pc, pk, "--list", "--since", "HEAD")
            expect("pc: --since HEAD reads changes against HEAD, where that unpublished commit is already included", "to run first: 0" in out)
            git(root, "push", "-q", "origin", "main")
            open(os.path.join(pk, "01-ontologies", "measured_b.ttl"), "w").write("changed\n")
            rc, out = run(pc, pk, "--list")
            expect("pc: a file the gate measured for a probe counts (not only its declared inputs)", "b_probe_v1_0_0.py" in out and "to run first: 1" in out)
            git(root, "checkout", "--", ".")
            open(os.path.join(root, "outside.txt"), "w").write("changed\n")
            rc, out = run(pc, pk, "--list")
            expect("pc: a change outside the package folder counts for a probe that reads it", "c_probe_v1_0_0.py" in out and "to run first: 1" in out)
            git(root, "checkout", "--", ".")
            open(os.path.join(pk, "01-ontologies", "data_e.ttl"), "w").write("new, untracked\n")
            rc, out = run(pc, pk, "--list")
            expect("pc: a new untracked file a probe reads counts", "e_probe_v1_0_0.py" in out and "to run first: 1" in out)
            os.remove(os.path.join(pk, "01-ontologies", "data_e.ttl"))
            open(os.path.join(pk, "03-tooling", "b_probe_v1_0_0.py"), "a").write("# edit\n")
            rc, out = run(pc, pk, "--own", "--list")
            expect("pc: --own lists the probe whose own file changed", "b_probe_v1_0_0.py" in out and "a_probe" not in out)
            open(os.path.join(pk, "03-tooling", "a_probe_v1_0_0.py"), "w").write("import sys\nif sys.argv[1:]==['--deps']:\n    print('%s'); sys.exit(0)\nprint('boom'); sys.exit(1)\n" % os.path.join(pk, "01-ontologies", "data_a.ttl"))
            rc, out = run(pc, pk)
            expect("pc: a failing probe makes it exit 1 and shows its tail", rc == 1 and "FAIL" in out and "boom" in out)
    return res

MUTANTS = [
    ("ss", "the record is written without --ack", 'if "--ack" in argv:', "if True:"),
    ("ss", "a changed or unread discipline no longer blocks", 'read it, then run again with --ack" % label)\n                ok = False', 'read it, then run again with --ack" % label)\n                ok = ok'),
    ("ss", "the ceremony is always good", "good = rc == 0 and bool(verd) and", "good = True or"),
    ("ss", "a REFUSE line beside PROCEED is ignored", ' and not any(re.search(r"\\bREFUSE\\w*\\b|\\bNOT\\b", l) for l in keep)', ""),
    ("ss", "REFUSED is not read as a refusal", "REFUSE\\w*\\b|\\bNOT", "REFUSE\\b|\\bNOT"),
    ("ss", "a verdict that only starts with PROCEED is accepted", 're.match(r"VERDICT:\\s+PROCEED(\\s|$)", verd[-1].strip()) is not None', '"PROCEED" in verd[-1]'),
    ("ss", "a failed fetch is not an obstacle", 'cannot fetch origin (%s)" % (label, err.strip()[:100])); ok = False; continue', 'cannot fetch origin (%s)" % (label, err.strip()[:100])); continue'),
    ("ss", "a missing ceremony script is not an obstacle", 'no oe_ceremony script found"); ok = False', 'no oe_ceremony script found")'),
    ("ss", "--ack acknowledges what was never shown", 'if "--ack" in argv and shown == sha:', 'if "--ack" in argv:'),
    ("ss", "empty bytes from origin are accepted", "if r.returncode != 0 or not r.stdout:", "if False:"),
    ("ss", "the ceremony exit code is ignored", "good = rc == 0 and bool(verd) and", "good = bool(verd) and"),
    ("ss", "the first verdict counts, not the last", "verd[-1].strip()", "verd[0].strip()"),
    ("ss", "the bytes come from HEAD, not origin", '"origin/main:" + name', '"HEAD:" + name'),
    ("ss", "origin is not fetched", '["git", "fetch", "-q", "origin", "main"]', '["git", "status", "-q"]'),
    ("ss", "versions compared as text", "key = tuple(int(x) for x in m.groups())", "key = m.groups()"),
    ("ss", "behind origin is not an obstacle", "ok = ok and behind == 0", "ok = ok"),
    ("gd", "Traceback is not a failure word", "|Traceback", ""),
    ("gd", "ABORT is not a failure word", "|ABORT|ABORTED", ""),
    ("gd", "the closing line is not the authority", 'closing = [v for v in verdicts if v.startswith("RELEASE GATE")]', "closing = []"),
    ("gd", "a shown failure no longer fails the exit", "return 0 if passing and not shown else 1", "return 0 if passing else 1"),
    ("gd", "a zero-count line is read as a failure", r"(FAILED|declaration FAILED)\s*:\s*0\b|", ""),
    ("gd", "the drift note is not printed", 'print("note: only the drift check failed', 'print("" and "note: only the drift check failed'),
    ("gd", "VIOLATION is not a failure word", "|VIOLATION|", "|"),
    ("gd", "a log with no closing line can pass", "passing = bool(closing) and", "passing = bool(verdicts) and"),
    ("gd", "a failing verdict line is not a failure", "shown.setdefault(section, []).append(l.strip()[:220])      # a failing", "pass      # a failing"),
    ("gd", "the light closing line is not recognised", 'v.startswith("RELEASE GATE")', 'v.startswith("RELEASE GATE:")'),
    ("gd", "REFUSE is not a failure word", "|REFUSE|REFUSED", "|REFUSED"),
    ("pc", "declared inputs are ignored", "(d | measured(pkg, name)) & ch", "measured(pkg, name) & ch"),
    ("pc", "measured inputs are ignored", "(d | measured(pkg, name)) & ch", "d & ch"),
    ("pc", "--since is ignored", 'ref = since or (', 'ref = ('),
    ("ss", "the ceremony is run without the package argument", '["bash", scripts[-1], package]', '["bash", scripts[-1]]'),
    ("pc", "untracked files are not counted", '["ls-files", "--others", "--exclude-standard"]', '["diff", "--name-only", "-M", ref]'),
    ("pc", "a probe's own change is ignored", "os.path.realpath(p) in ch or", "False or"),
    ("pc", "changed is read against HEAD, not origin", '"origin/main" if subprocess', '"HEAD" if subprocess'),
    ("pc", "a failing probe does not fail the run", "return 1 if bad else 0", "return 0"),
    ("pc", "--own is not honoured", '"--own" not in argv)', "True)"),
]
bad = []
real = scenarios(SS, GD, PC)
for name, ok in real:
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
paths = {"ss": SS, "gd": GD, "pc": PC}
for tool, what, old, new in MUTANTS:
    src = open(paths[tool], encoding="utf-8").read()
    if old not in src:
        print("FAIL  mutant text not found: " + what); bad.append("stale mutant: " + what); continue
    with tempfile.TemporaryDirectory() as md:
        m = {k: os.path.join(md, os.path.basename(v)) for k, v in paths.items()}
        for k, v in paths.items(): shutil.copy(v, m[k])
        open(m[tool], "w", encoding="utf-8").write(src.replace(old, new, 1))
        got = scenarios(m["ss"], m["gd"], m["pc"], (tool,))
    failed = [n for n, ok in got if not ok]
    print(("PASS  " if failed else "FAIL  ") + "mutant caught (%s): %s -> %d scenario(s) failed" % (tool, what, len(failed)))
    if not failed: bad.append("mutant survived: " + what)
print("tools: %s %s %s" % tuple(os.path.basename(x) for x in (SS, GD, PC))); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
