#!/usr/bin/env python3
"""backlog_probe_inputs_probe v1.1.0 -- the measured inputs of a probe are measured, and a stamp built on them moves exactly when they do (G128).

Builds a throwaway package, runs small probes in it under backlog_probe_inputs, and shows: what is read is listed; a changed input changes the key and an unread
file does not; a file added to a listed directory, an absent file appearing, and a new version of a tool the probe read each change it; a run that read outside the
package, wrote inside it, changed directory, or was not traced is not usable; the exported file and the session record agree. Exit 0 when every expectation holds."""
import glob, importlib.util, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
TOOL = sorted(glob.glob(os.path.join(HERE, "backlog_probe_inputs_v*.py")), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(TOOL); print(os.path.abspath(__file__)); sys.exit(0)
spec = importlib.util.spec_from_file_location("pin", TOOL); pin = importlib.util.module_from_spec(spec); spec.loader.exec_module(pin)
bad = []; COUNT = [0]


def expect(name, ok):
    COUNT[0] += 1
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok:
        bad.append(name)


if not pin.strace_works():
    print("VERDICT: NOT RUN -- strace cannot trace in this environment, so no input can be measured here (the gate keeps the declared inputs)")
    sys.exit(0)

work = os.path.realpath(tempfile.mkdtemp(prefix="pin_probe_"))
pkg = os.path.join(work, "pkg"); memo = os.path.join(work, "memo")
os.makedirs(os.path.join(pkg, "03-tooling")); os.makedirs(os.path.join(pkg, "data")); os.makedirs(os.path.join(pkg, "lists"))
w = lambda rel, t: open(os.path.join(pkg, rel), "w").write(t)
for r, t in (("data/a.txt", "a1"), ("data/b.txt", "b1"), ("data/unread.txt", "u1"), ("lists/one.txt", "1"), ("03-tooling/tool_v1_0_0.py", "X = 1\n"), ("03-tooling/other_v1_0_0.py", "Y = 1\n")):
    w(r, t)


def probe(name, body):
    w("03-tooling/%s_v1_0_0.py" % name, "import os, sys, glob\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\nP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n" + body)
    return os.path.join(pkg, "03-tooling", "%s_v1_0_0.py" % name)


def run(name, body, env=None):
    s = probe(name, body)
    old = dict(os.environ)
    try:
        os.environ.update(env or {})
        rc = pin.cmd_run(s, pkg, memo, os.path.join(work, name + ".out"))
    finally:
        os.environ.clear(); os.environ.update(old)
    return rc, json.load(open(pin._recfile(memo, name)))


def key(name):
    return pin.key_of(json.load(open(pin._recfile(memo, name))), pkg)


rc, rec = run("reader", "import tool_v1_0_0\nopen(os.path.join(P,'data','a.txt')).read(); open(os.path.join(P,'data','b.txt')).read()\nglob.glob(os.path.join(P,'lists','*.txt'))\nos.path.exists(os.path.join(P,'data','later.txt'))\n")
expect("a clean run is usable and exits 0", rc == 0 and rec["usable"])
expect("the files read are listed (the probe itself, the tool it imports, two data files)", {"data/a.txt", "data/b.txt", "03-tooling/tool_v1_0_0.py", "03-tooling/reader_v1_0_0.py"} <= set(rec["files"]))
expect("a file that was not read is not listed", "data/unread.txt" not in rec["files"] and "03-tooling/other_v1_0_0.py" not in rec["files"])
expect("the directory the probe globbed is listed, and the path it looked for and did not find is recorded as absent", "lists" in rec["dirs"] and "data/later.txt" in rec["absent"])
k0 = key("reader")
expect("the key is stable while nothing changed", key("reader") == k0)
w("data/unread.txt", "u2")
expect("changing a file the probe did not read leaves the key alone", key("reader") == k0)
w("03-tooling/unrelated_v1_0_0.py", "Z = 1\n")
expect("an unrelated new tool in the script directory leaves the key alone", key("reader") == k0)
w("data/b.txt", "b2")
k1 = key("reader")
expect("changing a file the probe read changes the key", k1 != k0)
w("lists/two.txt", "2")
k2 = key("reader")
expect("a file added to a directory the probe listed changes the key", k2 != k1)
w("data/later.txt", "now")
k3 = key("reader")
expect("the absent file appearing changes the key", k3 != k2)
w("03-tooling/tool_v1_1_0.py", "X = 2\n")
expect("a new version of a tool the probe read changes the key", key("reader") != k3)

rc, rec = run("outsider", "import os\nf = os.path.expanduser('/home/claude/.pin_outside_test'); open(f, 'w').write('x'); open(f).read(); os.remove(f)\n") if os.access("/home/claude", os.W_OK) else (0, {"usable": False})
expect("a run that read a file outside the package is not usable", not rec["usable"])
rc, rec = run("writer", "open(os.path.join(P,'data','made.txt'),'w').write('x')\n")
expect("a run that wrote a file inside the package is not usable", not rec["usable"])
rc, rec = run("mover", "import subprocess\nsubprocess.run(['true'], cwd='/')\n")
expect("a run whose child changed directory is not usable", not rec["usable"])
rc, rec = run("quiet", "print('x')\n", env={"BACKLOG_NO_TRACE": "1"})
expect("an untraced run writes an unusable record and no key is offered", not rec["usable"] and subprocess.run([sys.executable, TOOL, "key", "quiet", pkg, memo], capture_output=True).returncode == 1)
rc, rec = run("failing", "sys.exit(3)\n")
expect("the exit code of the probe is the exit code of the run", rc == 3)

repo = os.path.join(work, "PROBE_INPUTS.json")
pin.cmd_export(memo, repo)
doc = json.load(open(repo))
expect("the export holds the record of every probe that exited 0, usable or not, and is sorted", "reader" in doc["probes"] and "failing" not in doc["probes"] and list(doc["probes"]) == sorted(doc["probes"]))
shutil.rmtree(memo)
out = subprocess.run([sys.executable, TOOL, "key", "reader", pkg, memo, repo], capture_output=True, text=True)
key_after = pin.key_of(doc["probes"]["reader"], pkg)
expect("a fresh session builds the same key from the exported record", out.returncode == 0 and out.stdout.strip() == key_after)
out = subprocess.run([sys.executable, TOOL, "key", "writer", pkg, memo, repo], capture_output=True, text=True)
expect("an exported record that is not usable offers no key", out.returncode == 1 and not out.stdout.strip())
w("03-tooling/reader_v1_0_0.py", "import tool_v1_0_0, os, sys\n")
expect("a changed probe changes its own key (the script is one of its inputs)", pin.key_of(doc["probes"]["reader"], pkg) != key_after)

has = lambda n, m, r=None: subprocess.run([sys.executable, TOOL, 'has', n, m] + ([r] if r else []), capture_output=True).returncode
nm = os.path.join(work, "memo2"); rf2 = os.path.join(work, "inputs2.json")
expect("has: a probe with no record in the session or the file has none", has("reader", nm, rf2) == 1)
rc, rec = run("quiet2", "print('x')\n", env={"BACKLOG_NO_TRACE": "1"})
doc2 = pin.cmd_export(memo, os.path.join(work, "inputs3.json"))
expect("has: the repo file holds a record after the export, and a probe that was only run untraced is not in it",
       has("reader", nm, repo) == 0 and "quiet2" not in json.load(open(os.path.join(work, "inputs3.json")))["probes"])

shutil.rmtree(work, ignore_errors=True)
print("VERDICT: %s" % ("PASS -- %d expectations hold" % COUNT[0] if not bad else "FAIL -- " + "; ".join(bad)))
sys.exit(1 if bad else 0)
