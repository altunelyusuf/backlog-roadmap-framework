#!/usr/bin/env python3
"""backlog_vocabulary_probe v1.0.0 -- the vocabulary check passes on the real file and refuses a drifted or incomplete one (G106).
  1. the newest vocabulary file against the newest T-Box and A-box: passes
  2. the same file with one member's label changed: refused (differs)
  3. a T-Box copy whose enumeration lists a member the A-box does not define: refused (not defined)
Exit 0 when all three behave, 3 otherwise.   --deps prints the tool it runs."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE); ONT = os.path.join(PKG, "01-ontologies")
def newest(pat, d=ONT): return sorted(glob.glob(os.path.join(d, pat)), key=lambda x: [int(n) for n in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", x)[0]])[-1]
T = sorted(glob.glob(os.path.join(HERE, "backlog_vocabulary_derive_v*.py")), key=lambda x: [int(n) for n in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", x)[0]])[-1]
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(T)
    for pat in ("backlog_tbox_v*.ttl", "backlog_abox_v*.ttl", "backlog_vocabulary_v*.ttl"): print(newest(pat))
    sys.exit(0)
def run(*a): return subprocess.run([sys.executable, "-B", T, *a], capture_output=True, text=True).returncode
bad = []
if run("--check") != 0: bad.append("1: the real vocabulary file does not pass")
with tempfile.TemporaryDirectory() as d:
    v = open(newest("backlog_vocabulary_v*.ttl")).read(); lab = re.search(r'rdfs:label "([^"]+)"@en', v[v.index("backlog:AC_Confirmed"):]).group(1)
    p = os.path.join(d, "backlog_vocabulary_v9_9_9.ttl"); open(p, "w").write(v.replace(f'rdfs:label "{lab}"@en', 'rdfs:label "DRIFT"@en', 1))
    if run("--check", "--vocab", p) == 0: bad.append("2: a drifted vocabulary file was accepted")
    t = open(newest("backlog_tbox_v*.ttl")).read(); m = re.search(r"owl:oneOf \(\s*backlog:(\w+)", t)
    q = os.path.join(d, "backlog_tbox_v9_9_9.ttl"); open(q, "w").write(t.replace(m.group(0), m.group(0) + " backlog:Ghost_Member_Probe", 1))
    if run("--check", "--tbox", q) == 0: bad.append("3: an enumeration member missing from the A-box was accepted")
for b in bad: print("FAIL", b)
print("vocabulary probe:", "PASS" if not bad else f"{len(bad)} failure(s)"); sys.exit(3 if bad else 0)
