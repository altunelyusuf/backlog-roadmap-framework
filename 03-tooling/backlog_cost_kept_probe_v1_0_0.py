#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe reads no record of the framework register; it reads git and builds throw-away repositories)
"""backlog_cost_kept_probe v1.0.0 -- the full gate, the release tool and the two disciplines are shown unchanged by Lineage 30 (cost-saving tools).

The baseline is the published tree at the start of the lineage (tag backlog-roadmap-framework-v4.6.0). The newest gate script may differ from the baseline's only in its
version-note comment lines and in its PROBE_LIST, and the list may only GAIN the probes named in ALLOWED (the proof probes of this lineage); nothing may be taken out. The
newest release tool, the files the release path calls (RELEASE_PATH), the newest lineage discipline and the newest OE discipline are byte-identical to the baseline's. The PROBE_LIST must be one plain assignment that keeps the baseline's probes first, in order and once each. A line that begins like a version note is taken to be a comment and ignored wherever it stands (the gate holds no heredoc; one added would change what the rule means). Files the release path reaches by other means (the publisher repository) are not compared. This probe is not a check of the gate: it shows only what
this lineage did not change; the gate's own steps are held by backlog_checks_kept_probe.
  The check is first shown on throw-away repositories: unchanged passes; a gate step changed, a probe taken out of the list, a probe added that is not named, the release tool
  changed, either discipline changed -- each fails; no baseline tag is NOT RUN (stated, and exit 0 only because nothing could be compared). Then a set of mutants of the check
  itself is run, each of which must fail one of those cases. Then the real repository is checked.
Exit 0 when every case holds and the real repository shows nothing changed (or the baseline is absent: NOT RUN), 1 otherwise."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); sys.exit(0)
TAG = "backlog-roadmap-framework-v4.6.0"
RELEASE_PATH = ("build_manifest", "make_public_distribution", "backlog_release_item_check", "backlog_probe_inputs", "backlog_merkle_cache", "backlog_distribution_drift_check", "backlog_archive_integrity", "backlog_pipeline_verify")
ALLOWED = {"backlog_cost_tools_probe", "backlog_cost_kept_probe"}
CHECK_SRC = r'''
def newest(names, stem):
    best = None
    for n in names:
        m = re.fullmatch(re.escape(stem) + r"_v(\d+)_(\d+)_(\d+)\.[a-z]+", os.path.basename(n))
        if m and (best is None or tuple(map(int, m.groups())) > best[0]):
            best = (tuple(map(int, m.groups())), n)
    return best[1] if best else None
def sh(root, *a):
    r = subprocess.run(["git", "-C", root, *a], capture_output=True)
    return r.returncode, r.stdout
def tree(root, ref, folder):
    rc, out = sh(root, "ls-tree", "--name-only", ref, folder.rstrip("/") + "/") if ref else (0, b"")
    return out.decode().split() if rc == 0 else []
def read_at(root, ref, path):
    rc, out = sh(root, "show", "%s:%s" % (ref, path))
    return out if rc == 0 else None
def gate_parts(text):
    lines = text.split("\n")
    plist = [l for l in lines if l.startswith("PROBE_LIST=")]
    rest = [("@PROBE_LIST@" if l.startswith("PROBE_LIST=") else l) for l in lines if not re.match(r"# v\d+\.\d+\.\d+ \(", l)]
    ok = len(plist) == 1 and re.fullmatch(r'PROBE_LIST="[A-Za-z0-9_ ]*"', plist[0]) is not None
    members = plist[0].split('"')[1].split() if ok else None
    return rest, members
def check(root, pkg, tag, oe_folder):
    """None when the baseline tag is absent (not run); else the list of problems (empty when nothing changed)."""
    if sh(root, "rev-parse", "--verify", "-q", tag + "^{commit}")[0] != 0:
        return None
    problems = []
    cur_dir = os.path.join(root, pkg, "03-tooling")
    for stem, ext in (("backlog_gate", "sh"), ("backlog_release_tool", "py")):
        base_files = tree(root, tag, pkg + "/03-tooling")
        bn = newest(base_files, stem); cn = newest(glob.glob(os.path.join(cur_dir, stem + "_v*." + ext)), stem)
        if not bn or not cn:
            problems.append("%s: no file in the baseline or now" % stem); continue
        bt = read_at(root, tag, bn); ct = open(cn, "rb").read()
        if stem == "backlog_release_tool":
            if bt != ct:
                problems.append("the release tool differs from the baseline (%s now, %s then)" % (os.path.basename(cn), os.path.basename(bn)))
        else:
            b_rest, b_members = gate_parts(bt.decode()); c_rest, c_members = gate_parts(ct.decode())
            if b_members is None or c_members is None:
                problems.append("the probe list is not a single plain assignment of names"); continue
            if b_rest != c_rest:
                problems.append("the gate differs from the baseline outside its version notes and its probe list")
            if len(set(c_members)) != len(c_members) or c_members[:len(b_members)] != b_members:
                problems.append("the probe list does not keep the baseline's probes, in their order, first and once each")
            if [m for m in b_members if m not in c_members]:
                problems.append("the gate no longer lists: " + ", ".join(m for m in b_members if m not in c_members))
            extra = [m for m in c_members if m not in b_members and m not in ALLOWED]
            if extra:
                problems.append("the gate lists probes this lineage did not name: " + ", ".join(extra))
    for stem in RELEASE_PATH:
        bn = newest(tree(root, tag, pkg + "/03-tooling"), stem); cn = newest(glob.glob(os.path.join(cur_dir, stem + "_v*.py")), stem)
        if bn and (not cn or read_at(root, tag, bn) != open(cn, "rb").read()):
            problems.append("the release path file %s differs from the baseline" % stem)
    for label, folder, stem, where in (("lineage discipline", pkg + "/04-documentation", "LINEAGE_OPERATING_DISCIPLINE", os.path.join(root, pkg, "04-documentation")),
                                       ("OE discipline", oe_folder, "OE_Operating_Discipline", os.path.join(root, oe_folder))):
        bn = newest(tree(root, tag, folder), stem); cn = newest(glob.glob(os.path.join(where, stem + "_v*.md")), stem)
        if not bn and not cn:
            continue          # a clone that does not hold this folder (the public copy holds no OE method): nothing to compare
        if not bn or not cn:
            problems.append("%s: present in only one of the baseline and now" % label); continue
        if read_at(root, tag, bn) != open(cn, "rb").read():
            problems.append("the %s differs from the baseline (%s now, %s then)" % (label, os.path.basename(cn), os.path.basename(bn)))
    return problems
'''
def load(src):
    ns = {"os": os, "re": re, "subprocess": subprocess, "glob": glob, "ALLOWED": ALLOWED, "RELEASE_PATH": RELEASE_PATH}
    exec(src, ns); return ns["check"]
def build(d, gate_extra="", plist="a_probe", rt="x\n", ld="lineage\n", oe="oe\n", tag=True):
    def w(p, t):
        os.makedirs(os.path.dirname(os.path.join(d, p)), exist_ok=True); open(os.path.join(d, p), "w").write(t)
    subprocess.run(["git", "init", "-q", d], check=True)
    def git(*a): subprocess.run(["git", "-c", "user.email=p@p", "-c", "user.name=p", "-C", d, *a], capture_output=True, text=True, check=True)
    w("pkg/03-tooling/backlog_gate_v1_82_0.sh", '# v1.82.0 (note)\necho step one\nPROBE_LIST="a_probe b_probe"\necho step two\n')
    w("pkg/03-tooling/backlog_release_tool_v1_12_0.py", "x\n")
    w("pkg/03-tooling/build_manifest_v1_7_0.py", "m\n")
    w("pkg/04-documentation/LINEAGE_OPERATING_DISCIPLINE_v158_0_0.md", "lineage\n")
    w("oe-method/04-documentation/OE_Operating_Discipline_v2_37_0.md", "oe\n")
    git("add", "-A"); git("commit", "-q", "-m", "base")
    if tag: git("tag", TAG)
    return git, w
def scenarios(check):
    res = []
    def run(name, mutate, expect_sub):
        with tempfile.TemporaryDirectory() as d:
            git, w = build(d)
            mutate(w, d)
            r = check(d, "pkg", TAG, "oe-method/04-documentation")
            ok = (r == []) if expect_sub is None else (bool(r) and any(expect_sub in x for x in r))
            res.append((name, ok))
    GATE = lambda extra_step="", plist="a_probe b_probe": '# v1.83.0 (other note)\necho step one\n%sPROBE_LIST="%s"\necho step two\n' % (extra_step, plist)
    run("unchanged but for a new version note and the two named probes: passes", lambda w, d: w("pkg/03-tooling/backlog_gate_v1_83_0.sh", GATE(plist="a_probe b_probe backlog_cost_tools_probe backlog_cost_kept_probe")), None)
    run("a gate step changed: fails", lambda w, d: w("pkg/03-tooling/backlog_gate_v1_83_0.sh", GATE(extra_step="echo a new step\n").replace("step two", "step 2")), "outside its version notes")
    run("a probe taken out of the list: fails", lambda w, d: w("pkg/03-tooling/backlog_gate_v1_83_0.sh", GATE(plist="a_probe")), "no longer lists")
    run("a probe added that is not named: fails", lambda w, d: w("pkg/03-tooling/backlog_gate_v1_83_0.sh", GATE(plist="a_probe b_probe sneaky_probe")), "did not name")
    run("a step added: fails", lambda w, d: w("pkg/03-tooling/backlog_gate_v1_83_0.sh", GATE(extra_step="echo added\n")), "outside its version notes")
    run("the release tool changed: fails", lambda w, d: w("pkg/03-tooling/backlog_release_tool_v1_13_0.py", "changed\n"), "release tool differs")
    run("the lineage discipline changed: fails", lambda w, d: w("pkg/04-documentation/LINEAGE_OPERATING_DISCIPLINE_v159_0_0.md", "changed\n"), "lineage discipline differs")
    run("the OE discipline changed: fails", lambda w, d: w("oe-method/04-documentation/OE_Operating_Discipline_v2_38_0.md", "changed\n"), "OE discipline differs")
    run("a command appended inside the probe list line: fails", lambda w, d: w("pkg/03-tooling/backlog_gate_v1_83_0.sh", GATE().replace('b_probe"', 'b_probe"; rm -rf x #')), "probe list is not")
    run("a second probe list assignment: fails", lambda w, d: w("pkg/03-tooling/backlog_gate_v1_83_0.sh", GATE() + 'PROBE_LIST="a_probe b_probe"\n'), "probe list is not")
    run("the baseline probes reordered: fails", lambda w, d: w("pkg/03-tooling/backlog_gate_v1_83_0.sh", GATE(plist="b_probe a_probe")), "in their order")
    run("a probe listed twice: fails", lambda w, d: w("pkg/03-tooling/backlog_gate_v1_83_0.sh", GATE(plist="a_probe b_probe b_probe")), "once each")
    run("a step moved across the probe list: fails", lambda w, d: w("pkg/03-tooling/backlog_gate_v1_83_0.sh", '# v1.83.0 (n)\nPROBE_LIST="a_probe b_probe"\necho step one\necho step two\n'), "outside its version notes")
    run("a release path file changed: fails", lambda w, d: w("pkg/03-tooling/build_manifest_v1_8_0.py", "changed\n"), "release path file")
    run("a discipline present in the baseline and gone now: fails", lambda w, d: os.remove(os.path.join(d, "oe-method/04-documentation/OE_Operating_Discipline_v2_37_0.md")), "present in only one")
    run("nothing changed at all: passes", lambda w, d: None, None)
    with tempfile.TemporaryDirectory() as d:
        build(d, tag=False)
        res.append(("no baseline tag: not run (None), never a pass of its own", check(d, "pkg", TAG, "oe-method/04-documentation") is None))
    return res
MUTANTS = [
    ("the gate's steps are not compared", "if b_rest != c_rest:", "if False:"),
    ("a probe taken out is not seen", "if [m for m in b_members if m not in c_members]:", "if False:"),
    ("any added probe is allowed", "m not in b_members and m not in ALLOWED]", "m not in b_members and False]"),
    ("the release tool is not compared", "if bt != ct:", "if False:"),
    ("the disciplines are not compared", "if read_at(root, tag, bn) != open(cn, \"rb\").read():", "if False:"),
    ("the OE discipline is read from the lineage folder", "(\"OE discipline\", oe_folder, \"OE_Operating_Discipline\", os.path.join(root, oe_folder))", "(\"OE discipline\", pkg + \"/04-documentation\", \"OE_Operating_Discipline\", os.path.join(root, pkg, \"04-documentation\"))"),
    ("a doubled or reordered probe list is accepted", 'if len(set(c_members)) != len(c_members) or c_members[:len(b_members)] != b_members:', "if False:"),
    ("a probe list with a command in it is accepted", "ok = len(plist) == 1 and re.fullmatch(r'PROBE_LIST=\"[A-Za-z0-9_ ]*\"', plist[0]) is not None", "ok = len(plist) >= 1"),
    ("the other release path files are not compared", 'if bn and (not cn or read_at(root, tag, bn) != open(cn, "rb").read()):', "if False:"),
    ("a discipline present on one side only is passed over", 'if not bn or not cn:\n            problems.append("%s: present in only one', 'if False:\n            problems.append("%s: present in only one'),
    ("version notes are not ignored", 'not re.match(r"# v\\d+\\.\\d+\\.\\d+ \\(", l)', "True"),
]
bad = []
for name, ok in scenarios(load(CHECK_SRC)):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: bad.append(name)
for what, old, new in MUTANTS:
    if old not in CHECK_SRC:
        print("FAIL  mutant text not found: " + what); bad.append("stale mutant: " + what); continue
    try:
        got = scenarios(load(CHECK_SRC.replace(old, new, 1)))
    except Exception as e:
        got = [("crash", False)]
    failed = [n for n, ok in got if not ok]
    print(("PASS  " if failed else "FAIL  ") + "mutant caught: %s -> %d case(s) failed" % (what, len(failed)))
    if not failed: bad.append("mutant survived: " + what)
root = subprocess.run(["git", "-C", HERE, "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
if not root:
    print("NOT RUN  the package is not in a git work tree; nothing could be compared")
else:
    pkg = os.path.relpath(os.path.dirname(HERE), root)
    r = load(CHECK_SRC)(root, pkg, TAG, "oe-method/04-documentation")
    if r is None:
        print("NOT RUN  the baseline tag %s is not in this clone; nothing was compared (never read as a pass)" % TAG)
    elif r:
        print("FAIL  the real repository differs from the baseline: " + "; ".join(r)); bad.append("real: " + "; ".join(r))
    else:
        print("PASS  the gate (but for version notes and the two named probes), the release tool and the two disciplines are those of %s" % TAG)
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
