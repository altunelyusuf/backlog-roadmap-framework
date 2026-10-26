#!/usr/bin/env python3
"""backlog_work_guard_probe v1.5.0 -- proof that the work guard discriminates and cannot pass over nothing (L-95).

Builds a real throwaway git repository, installs the guard with backlog_guard_install, and drives REAL git commits and
the REAL Claude hook script against fixtures/fixture_execution_ready_negative (cite by stem, L-123), where the lineage
Lin_Ready is fully built with one groomed item and Lin_Waiting has no Backlog stage. Every case states the outcome it
must produce, both halves: what must pass AND what must be refused. Exit 0 when every expectation holds, 1 otherwise.
"""
import glob, json, os, re, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
fx = sorted(glob.glob(os.path.join(HERE, "fixtures", "fixture_execution_ready_negative_v*.ttl")), key=sv)[-1]
TOOLS = ["backlog_work_guard", "backlog_session_brief", "backlog_execution_ready", "backlog_guard_claude_hook", "backlog_guard_install"]
bad = []


def sh(cwd, *cmd, inp=None, env=None):
    e = dict(os.environ); e.update(env or {})
    return subprocess.run(list(cmd), cwd=cwd, capture_output=True, text=True, input=inp, env=e)


def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)


def fresh(lineage="Lin_Ready", work=("app/**",)):
    d = tempfile.mkdtemp(prefix="guardprobe_")
    sh(d, "git", "init", "-q"); sh(d, "git", "config", "user.email", "p@x"); sh(d, "git", "config", "user.name", "p")
    os.makedirs(os.path.join(d, "tools")); os.makedirs(os.path.join(d, "app")); os.makedirs(os.path.join(d, "docs"))
    for t in TOOLS:
        src = sorted(glob.glob(os.path.join(HERE, t + "_v*.py")), key=sv)[-1]
        shutil.copy(src, os.path.join(d, "tools"))
    shutil.copy(fx, os.path.join(d, "register.ttl"))
    open(os.path.join(d, "app", "main.py"), "w").write("print(1)\n"); open(os.path.join(d, "docs", "a.md"), "w").write("a\n")
    sh(d, "git", "add", "-A"); sh(d, "git", "commit", "-q", "-m", "baseline before the guard")
    args = [sys.executable, os.path.join(d, "tools", "backlog_guard_install_v1_1_0.py"), d, "--tooling-dir", "tools",
            "--register", "register.ttl", "--lineage", lineage]
    for w in work: args += ["--work-path", w]
    r = subprocess.run(args, capture_output=True, text=True)
    return d, r


def commit(d, msg, path="app/main.py", extra=(), noverify=False):
    open(os.path.join(d, path), "a").write("x\n")
    sh(d, "git", "add", "-A")
    return sh(d, "git", "commit", "-q", *(["--no-verify"] if noverify else []), "-m", msg, *extra)


if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(fx)
    for t in TOOLS:
        print(sorted(glob.glob(os.path.join(HERE, t + "_v*.py")), key=sv)[-1])
    sys.exit(0)


d, r = fresh()
expect("installer runs and reports the layers", r.returncode == 0 and "installed:" in r.stdout)
s = json.load(open(os.path.join(d, ".claude", "settings.json")))
expect("Claude hooks registered for SessionStart and PreToolUse",
       "SessionStart" in s["hooks"] and "PreToolUse" in s["hooks"])
expect("CI workflow written", os.path.isfile(os.path.join(d, ".github", "workflows", "backlog-work-guard.yml")))
r = commit(d, "work without any item")
expect("REFUSED: a work commit with no Work-Item trailer", r.returncode != 0 and "names no `Work-Item" in r.stdout + r.stderr)
r = commit(d, "work on a missing item\n\nWork-Item: S_Missing")
expect("REFUSED: a Work-Item that is not in the register", r.returncode != 0 and "not found in the register" in r.stdout + r.stderr)
r = commit(d, "work on an ungroomed item\n\nWork-Item: S_NoCriterion")
expect("REFUSED: a Work-Item with no acceptance criterion", r.returncode != 0 and "acceptance criterion" in r.stdout + r.stderr)
r = commit(d, "work on a proposed item\n\nWork-Item: S_Proposed")
expect("REFUSED: a Work-Item that is not Ready or InProgress", r.returncode != 0 and "Ready or InProgress" in r.stdout + r.stderr)
r = commit(d, "work on a groomed item\n\nWork-Item: S_Groomed")
expect("ACCEPTED: a work commit naming a groomed, planned item", r.returncode == 0)
r = commit(d, "docs only, no item needed", path="docs/a.md")
expect("ACCEPTED: a commit that touches no governed work needs no item", r.returncode == 0)
r = commit(d, "skipped the hook", noverify=True)
expect("a --no-verify commit gets in locally (the hook alone can be skipped)", r.returncode == 0)
g = os.path.join(d, "tools", "backlog_work_guard_v1_4_0.py")
r = sh(d, sys.executable, g, "range", "HEAD~2..HEAD")
expect("REFUSED by the CI layer: the range check names the skipped commit",
       r.returncode == 2 and "names no Work-Item" in r.stdout and "examined" in r.stdout)
r = sh(d, sys.executable, g, "range", "HEAD~2..HEAD~1")
expect("ACCEPTED by the CI layer: a range holding only compliant commits", r.returncode == 0 and "VERDICT: PASS" in r.stdout)
hook = os.path.join(d, "tools", "backlog_guard_claude_hook_v1_1_0.py")
ev = lambda **k: json.dumps(dict({"cwd": d, "hook_event_name": "PreToolUse"}, **k))
r = sh(d, sys.executable, hook, inp=ev(tool_name="Edit", tool_input={"file_path": os.path.join(d, "app", "main.py")}))
expect("ACCEPTED at edit time: lineage ready", r.returncode == 0)
r = sh(d, sys.executable, hook, inp=ev(tool_name="Bash", tool_input={"command": "echo hi"}))
expect("ACCEPTED: a Bash command that writes nothing governed", r.returncode == 0)

sh(d, "git", "add", "-A"); sh(d, "git", "commit", "-q", "--no-verify", "-m", "commit the installed guard files")
d5 = tempfile.mkdtemp(prefix="guardclone_"); shutil.rmtree(d5); sh(os.path.dirname(d), "git", "clone", "-q", d, d5)
sh(d5, "git", "config", "user.email", "p@x"); sh(d5, "git", "config", "user.name", "p")
r = commit(d5, "work in a fresh clone, hooks not armed yet")
expect("a fresh clone has no git hooks (they do not travel): the commit gets in", r.returncode == 0)
sh(d5, "git", "reset", "-q", "--hard", "HEAD~1")
r = sh(d5, sys.executable, os.path.join(d5, "tools", "backlog_guard_claude_hook_v1_1_0.py"), inp=json.dumps({"cwd": d5, "hook_event_name": "SessionStart"}))
expect("SessionStart re-arms the git hooks in the clone", r.returncode == 0 and "re-armed" in r.stdout)
r = commit(d5, "work in a fresh clone after the session start")
expect("REFUSED in the fresh clone once the session start has re-armed the hooks", r.returncode != 0 and "names no `Work-Item" in r.stdout + r.stderr)
shutil.rmtree(d5, ignore_errors=True)

bare = tempfile.mkdtemp(prefix="guardbare_"); sh(bare, "git", "init", "-q", "--bare")
sh(d, "git", "remote", "add", "origin", bare)
r = sh(d, "git", "push", "-q", "origin", "HEAD:refs/heads/work")
expect("REFUSED at push: the range holds the commit that skipped the commit hook", r.returncode != 0 and "names no Work-Item" in r.stdout + r.stderr)
d4, r = fresh()
bare4 = tempfile.mkdtemp(prefix="guardbare_"); sh(bare4, "git", "init", "-q", "--bare"); sh(d4, "git", "remote", "add", "origin", bare4)
commit(d4, "groomed work\n\nWork-Item: S_Groomed")
r = sh(d4, "git", "push", "-q", "origin", "HEAD:refs/heads/work")
expect("ACCEPTED at push: a range of compliant commits", r.returncode == 0)
shutil.rmtree(bare, ignore_errors=True); shutil.rmtree(bare4, ignore_errors=True); shutil.rmtree(d4, ignore_errors=True)

d2, r = fresh("Lin_Waiting")
hook2 = os.path.join(d2, "tools", "backlog_guard_claude_hook_v1_1_0.py")
ev2 = lambda **k: json.dumps(dict({"cwd": d2, "hook_event_name": "PreToolUse"}, **k))
r = sh(d2, sys.executable, hook2, inp=ev2(tool_name="Write", tool_input={"file_path": os.path.join(d2, "app", "new.py")}))
expect("REFUSED at edit time: lineage has no Backlog stage (the Lineage_2 state)",
       r.returncode == 2 and "Stage_Backlog" in r.stderr and "NEXT REQUIRED ACT" in r.stderr)
r = sh(d2, sys.executable, hook2, inp=ev2(tool_name="Bash", tool_input={"command": "sed -i s/1/2/ app/main.py"}))
expect("REFUSED at edit time: a Bash write to a governed path", r.returncode == 2)
r = sh(d2, sys.executable, hook2, inp=ev2(tool_name="Write", tool_input={"file_path": os.path.join(d2, "docs", "n.md")}))
expect("ACCEPTED at edit time: a non-governed path stays writable on the same lineage", r.returncode == 0)
r = sh(d2, sys.executable, hook2, inp=json.dumps({"cwd": d2, "hook_event_name": "SessionStart"}))
expect("SessionStart puts NOT READY and the next required act into the session",
       r.returncode == 0 and "NOT READY" in r.stdout and "build the Backlog stage" in r.stdout)
d3, r = fresh("Lin_Ready", work=("nowhere/**",))
r = commit(d3, "work", path="docs/a.md")
expect("REFUSED: a work path that matches no tracked file (a guard over nothing)",
       r.returncode != 0 and "matches no tracked file" in r.stdout + r.stderr)
r = subprocess.run([sys.executable, os.path.join(d, "tools", "backlog_guard_install_v1_1_0.py"), d, "--tooling-dir", "tools",
                    "--register", "register.ttl", "--lineage", "Lin_Ready", "--work-path", "app/**"], capture_output=True, text=True)
s2 = json.load(open(os.path.join(d, ".claude", "settings.json")))
expect("installer is idempotent: hooks are not duplicated", len(s2["hooks"]["PreToolUse"]) == 1 and r.returncode == 0)
for x in (d, d2, d3): shutil.rmtree(x, ignore_errors=True)

# ---- v1.2.0 (G119): the range is judged by the configuration and the register that were in force before it ----
def committed():
    """A fresh repository whose installed guard files are committed (the state a consumer is in once it adopted the guard)."""
    d, r = fresh()
    sh(d, "git", "add", "-A"); sh(d, "git", "commit", "-q", "--no-verify", "-m", "commit the installed guard files")
    return d
gv = lambda d: os.path.join(d, "tools", "backlog_work_guard_v1_4_0.py")
head = lambda d: sh(d, "git", "rev-parse", "HEAD").stdout.strip()

d6 = committed(); base = head(d6)
cfgp = os.path.join(d6, ".backlog-guard.json"); c = json.load(open(cfgp)); c["exempt_paths"] = ["app/**"]; json.dump(c, open(cfgp, "w"), indent=2)
sh(d6, "git", "add", "-A"); r = sh(d6, "git", "commit", "-q", "-m", "loosen the guard\n\nWork-Item: S_Groomed")
expect("a configuration change with a ready Work-Item gets in (the configuration is governed, not frozen)", r.returncode == 0)
r = commit(d6, "work after the loosening, no item", noverify=True)
r = sh(d6, sys.executable, gv(d6), "range", base + "..HEAD")
expect("REFUSED by the range check: a configuration loosened inside the range does not release the later commit",
       r.returncode == 2 and "names no Work-Item" in r.stdout and "read at" in r.stdout)
r = sh(d6, sys.executable, gv(d6), "range", "HEAD~1..HEAD")
expect("the same commit is exempt in the NEXT range (the loosening is in force at its base)", r.returncode == 0 and "VERDICT: PASS" in r.stdout)

d7 = committed()
c0 = json.load(open(os.path.join(d7, ".backlog-guard.json"))); c0["note"] = "edited"; json.dump(c0, open(os.path.join(d7, ".backlog-guard.json"), "w"), indent=2)
sh(d7, "git", "add", "-A"); r = sh(d7, "git", "commit", "-q", "-m", "edit the guard configuration, no item")
expect("REFUSED: the guard configuration is governed work (protected path)", r.returncode != 0 and "names no `Work-Item" in r.stdout + r.stderr)
c = json.load(open(os.path.join(d7, ".backlog-guard.json"))); sh(d7, "git", "checkout", "--", ".backlog-guard.json")
c["exempt_paths"] = [".githooks/**", ".backlog-guard.json", "tools/**"]; json.dump(c, open(os.path.join(d7, ".backlog-guard.json"), "w"), indent=2)
sh(d7, "git", "add", "-A"); sh(d7, "git", "commit", "-q", "--no-verify", "-m", "exempt the guard files")
r = commit(d7, "edit a hook, no item", path=".githooks/commit-msg")
expect("REFUSED: no exempt path releases the guard's own files", r.returncode != 0 and "names no `Work-Item" in r.stdout + r.stderr)
r = commit(d7, "edit the vendored guard, no item", path="tools/backlog_work_guard_v1_4_0.py")
expect("REFUSED: the vendored tooling directory is governed work", r.returncode != 0 and "names no `Work-Item" in r.stdout + r.stderr)

d8 = committed(); base8 = head(d8)
reg = os.path.join(d8, "register.ttl"); t = open(reg).read()
commit(d8, "work on a proposed item, hook skipped\n\nWork-Item: S_Proposed", noverify=True)
open(reg, "w").write(t.replace("ex:S_Proposed a backlog:Story ; backlog:hasIdentifier \"S_Proposed\" ; backlog:hasState backlog:Proposed", "ex:S_Proposed a backlog:Story ; backlog:hasIdentifier \"S_Proposed\" ; backlog:hasState backlog:Ready"))
sh(d8, "git", "add", "-A"); sh(d8, "git", "commit", "-q", "-m", "ready the item afterwards (register edit)")
r = sh(d8, sys.executable, gv(d8), "range", base8 + "..HEAD")
expect("REFUSED: work committed BEFORE its item was ready is not rescued by a later register edit (the register is read at the commit's parent)",
       r.returncode == 2 and "Ready or InProgress" in r.stdout)

d9 = committed(); base9 = head(d9)
reg = os.path.join(d9, "register.ttl"); t = open(reg).read()
open(reg, "w").write(t.replace("ex:S_Proposed a backlog:Story ; backlog:hasIdentifier \"S_Proposed\" ; backlog:hasState backlog:Proposed", "ex:S_Proposed a backlog:Story ; backlog:hasIdentifier \"S_Proposed\" ; backlog:hasState backlog:Ready"))
sh(d9, "git", "add", "-A"); sh(d9, "git", "commit", "-q", "-m", "ready the item (register edit)")
r = commit(d9, "work on the item readied one commit earlier\n\nWork-Item: S_Proposed")
expect("ACCEPTED locally: ready before the commit is what the commit hook asks", r.returncode == 0)
r = sh(d9, sys.executable, gv(d9), "range", base9 + "..HEAD")
expect("ACCEPTED by the range check, and the item readied inside the range is reported",
       r.returncode == 0 and "NOTE" in r.stdout and "became ready inside this range" in r.stdout)
r = sh(d9, sys.executable, gv(d9), "range", "--strict-base", base9 + "..HEAD")
expect("REFUSED under --strict-base: readiness must be established before the range began",
       r.returncode == 2 and "was not ready before the range began" in r.stdout)
r = sh(d9, sys.executable, gv(d9), "range", "HEAD~1..HEAD")
expect("ACCEPTED under the ordinary range once the item was ready at its base", r.returncode == 0 and "NOTE" not in r.stdout)
wf = open(os.path.join(d9, ".github", "workflows", "backlog-work-guard.yml")).read()
expect("the CI file runs the guard as it was BEFORE the range (git archive of the base), so a commit cannot edit the judge",
       "git archive" in wf and "--config .backlog-guard.json" in wf)
for x in (d6, d7, d8, d9): shutil.rmtree(x, ignore_errors=True)

# G122: the session-start status carries the brief, and does not stop speaking when the brief is absent
dB, _ = fresh()
r = sh(dB, sys.executable, os.path.join(dB, "tools", "backlog_work_guard_v1_4_0.py"), "--config", ".backlog-guard.json", "status")
expect("the status prints the brief (focus, items in progress, checkpoints due, what a close needs)",
       r.returncode == 0 and all(k in r.stdout for k in ("FOCUS", "IN PROGRESS", "DUE", "TO CLOSE")) and "NEXT REQUIRED ACT" in r.stdout)
os.remove(os.path.join(dB, "tools", "backlog_session_brief_v1_0_0.py"))
r = sh(dB, sys.executable, os.path.join(dB, "tools", "backlog_work_guard_v1_4_0.py"), "--config", ".backlog-guard.json", "status")
expect("without the brief tool the status still speaks and says what is missing",
       r.returncode == 0 and "NEXT REQUIRED ACT" in r.stdout and "BRIEF" in r.stdout and "not shown" in r.stdout)
shutil.rmtree(dB, ignore_errors=True)


# ---- v1.3.0 (G123): register by pattern, the guard-install commit, no rdflib needed to decide, the Bash write test ----
dP, _ = fresh("Lin_Waiting")
os.makedirs(os.path.join(dP, "registers"))
sh(dP, "git", "mv", "register.ttl", "registers/r_v1_0_0.ttl") if False else shutil.move(os.path.join(dP, "register.ttl"), os.path.join(dP, "registers", "r_v1_0_0.ttl"))
cp_ = os.path.join(dP, ".backlog-guard.json"); c = json.load(open(cp_)); c["register"] = ["registers/r_v*.ttl"]; json.dump(c, open(cp_, "w"), indent=2)
sh(dP, "git", "add", "-A"); sh(dP, "git", "commit", "-q", "--no-verify", "-m", "setup: the register cited by pattern and the guard committed")
gP = os.path.join(dP, "tools", "backlog_work_guard_v1_4_0.py")
r = sh(dP, sys.executable, gP, "status")
expect("a register cited by pattern is read (the lineage state is reported)", r.returncode == 0 and "NOT READY" in r.stdout)
shutil.move(os.path.join(dP, "registers", "r_v1_0_0.ttl"), os.path.join(dP, "registers", "r_v1_1_0.ttl"))
sh(dP, "git", "add", "-A"); r = sh(dP, "git", "commit", "-q", "-m", "BP-D7: the register gets a new version, the configuration is untouched")
expect("ACCEPTED while NOT READY: renaming a register cited by pattern touches only the register", r.returncode == 0)
r = sh(dP, sys.executable, gP, "status")
expect("the renamed register is the one read", r.returncode == 0 and "NOT READY" in r.stdout)
r = sh(dP, sys.executable, gP, "range", "HEAD~1..HEAD")
expect("the range check resolves the register at each revision", r.returncode == 0 and "VERDICT: PASS" in r.stdout)

# the guard-install commit
tf = os.path.join(dP, "tools", "backlog_work_guard_v1_4_0.py")
open(tf, "a").write("# re-vendored\n"); sh(dP, "git", "add", "-A")
r = sh(dP, "git", "commit", "-q", "-m", "re-vendor the guard, no marker")
expect("REFUSED while NOT READY: guard files changed with neither a Work-Item nor Guard-Install", r.returncode != 0 and "names no `Work-Item" in r.stdout + r.stderr)
r = sh(dP, "git", "commit", "-q", "-m", "re-vendor the guard\n\nGuard-Install: v1.3.0 vendored")
expect("ACCEPTED while NOT READY: a commit of only the guard's own files that states Guard-Install", r.returncode == 0)
open(tf, "a").write("# again\n"); open(os.path.join(dP, "app", "main.py"), "a").write("x\n"); sh(dP, "git", "add", "-A")
r = sh(dP, "git", "commit", "-q", "-m", "guard files with work mixed in\n\nGuard-Install: sneaked")
expect("REFUSED: Guard-Install does not release governed work committed beside the guard files", r.returncode != 0)
sh(dP, "git", "reset", "-q", "--hard", "HEAD")
open(os.path.join(dP, ".backlog-guard.json"), "a").write("\n"); sh(dP, "git", "add", "-A")
r = sh(dP, "git", "commit", "-q", "-m", "configuration under the install marker\n\nGuard-Install: sneaked")
expect("REFUSED: Guard-Install does not cover the configuration", r.returncode != 0)
sh(dP, "git", "reset", "-q", "--hard", "HEAD")
r = sh(dP, sys.executable, gP, "range", "HEAD~2..HEAD")
expect("the range check lists the guard-install commit without judging it by readiness", r.returncode == 0 and "guard-install commit" in r.stdout)

# no rdflib: python3 -S sees no site-packages
hP = os.path.join(dP, "tools", "backlog_guard_claude_hook_v1_1_0.py")
evP = lambda **k: json.dumps(dict({"cwd": dP, "hook_event_name": "PreToolUse"}, **k))
bash = lambda c: sh(dP, sys.executable, "-S", hP, inp=evP(tool_name="Bash", tool_input={"command": c}))
r = bash("python3 -m pip install rdflib pyshacl")
expect("ACCEPTED without rdflib: the command that installs rdflib", r.returncode == 0)
r = sh(dP, sys.executable, "-S", hP, inp=evP(tool_name="Write", tool_input={"file_path": os.path.join(dP, "app", "n.py")}))
expect("REFUSED without rdflib: a governed edit, and the reason names rdflib", r.returncode == 2 and "rdflib" in r.stderr)
r = sh(dP, sys.executable, "-S", hP, inp=json.dumps({"cwd": dP, "hook_event_name": "SessionStart"}))
expect("the session starts without rdflib and says the lineage state is not shown", r.returncode == 0 and "not shown" in r.stdout)

# the Bash write test
r = bash("grep -rn foo app > /tmp/guardprobe_out")
expect("ACCEPTED: a read of a governed directory whose redirect writes elsewhere", r.returncode == 0)
r = bash("echo x > app/new.py")
expect("REFUSED: a redirect into a governed path", r.returncode == 2)
r = bash("cp app/main.py /tmp/guardprobe_copy")
expect("ACCEPTED: copying a governed file OUT of the governed paths", r.returncode == 0)
r = bash("cp /tmp/guardprobe_copy app/main.py")
expect("REFUSED: copying INTO a governed path", r.returncode == 2)
r = bash("sed -i s/1/2/ app/main.py")
expect("REFUSED: sed -i on a governed file", r.returncode == 2)
shutil.rmtree(dP, ignore_errors=True)

# v1.4.0 (G161): a renamed register, and the configuration change that narrows an exact register path to its pattern
dV, r = fresh(lineage="Lin_Waiting")
shutil.move(os.path.join(dV, "register.ttl"), os.path.join(dV, "register_v1_0_0.ttl"))
cfgp = os.path.join(dV, ".backlog-guard.json"); cfg = json.load(open(cfgp)); cfg["register"] = ["register_v1_0_0.ttl"]; json.dump(cfg, open(cfgp, "w"))
sh(dV, "git", "add", "-A"); sh(dV, "git", "commit", "-q", "--no-verify", "-m", "version the register")
gV = os.path.join(dV, "tools", "backlog_work_guard_v1_4_0.py")
sh(dV, "git", "mv", "register_v1_0_0.ttl", "register_v1_1_0.ttl"); sh(dV, "git", "commit", "-q", "--no-verify", "-m", "rename the register")
r = sh(dV, sys.executable, gV, "status")
expect("a register renamed to a later version is still read through its exact path (G161)", "cannot read the register" not in r.stdout + r.stderr and r.returncode in (0, 2))
cfg = json.load(open(cfgp)); cfg["register"] = ["register_v*.ttl"]; json.dump(cfg, open(cfgp, "w"))
sh(dV, "git", "add", ".backlog-guard.json")
r = sh(dV, "git", "commit", "-q", "-m", "narrow the register path\n\nGuard-Install: pattern of the same stem")
expect("ACCEPTED while NOT READY: the configuration only replaces the exact register path by its pattern, Guard-Install stated (G161)", r.returncode == 0)
cfg["exempt_paths"] = ["app/**"]; json.dump(cfg, open(cfgp, "w"))
sh(dV, "git", "add", ".backlog-guard.json")
r = sh(dV, "git", "commit", "-q", "-m", "loosen\n\nGuard-Install: sneaked")
expect("REFUSED: a configuration change that does more than narrow the register path, even with Guard-Install", r.returncode != 0)
sh(dV, "git", "reset", "-q", "--hard", "HEAD")
shutil.rmtree(dV, ignore_errors=True)

print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
