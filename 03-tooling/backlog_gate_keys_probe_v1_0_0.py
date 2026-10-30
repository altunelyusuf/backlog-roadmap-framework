#!/usr/bin/env python3
"""backlog_gate_keys_probe v1.0.0 -- re-runnable proof that the gate's register-independent checks are keyed on what they read (Lineage 22, box 2, D6).

  The gate (v1.76.0) skips the validation cache proof, the self-proof of Gate R and the self-proof of the lineage-order gate while TOOLKEY, one key over every tool, fixture, gate script,
  shape file and the vocabulary, is the one under which they last held. This probe takes the gate's own TOOLKEY function and shows, on a throwaway package, that the key
  (1) does not move when only the register changes, (2) moves when a tool, a fixture, the shapes, the vocabulary or the gate script changes, (3) is the same on two runs;
  and that the gate keys the three sections, records only after a pass, runs the archived-lineages check once, and parses. Exit 0 when every expectation holds."""
import glob, os, re, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
GATE, MERKLE = latest("03-tooling/backlog_gate_v*.sh"), latest("03-tooling/backlog_merkle_cache_v*.py")
if sys.argv[1:] == ["--deps"]:
    print("\n".join([GATE, MERKLE, latest("03-tooling/backlog_flow_point_git_trace_v*.py"), os.path.abspath(__file__)])); sys.exit(0)
bad = []
def expect(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (" (%s)" % detail if detail else ""))
    if not ok: bad.append(name)
text = open(GATE, encoding="utf-8").read()
m = re.search(r"^TOOLKEY\(\) \{.*\}$", text, re.M)
expect("the gate defines TOOLKEY", bool(m))
with tempfile.TemporaryDirectory() as d:
    pk = os.path.join(d, "pkg")
    for sub in ("03-tooling/fixtures", "02-shacl-safeguards", "01-ontologies"): os.makedirs(os.path.join(pk, sub))
    W = lambda rel, t: open(os.path.join(pk, rel), "w").write(t)
    W("03-tooling/backlog_a_v1_0_0.py", "a = 1\n"); W("03-tooling/fixtures/fixture_positive_v1_0_0.ttl", "# f\n"); W("03-tooling/backlog_gate_v1_0_0.sh", "echo 1\n")
    W("02-shacl-safeguards/backlog_shacl_v1_0_0.ttl", "# s\n"); W("01-ontologies/backlog_tbox_v1_0_0.ttl", "# t\n"); W("01-ontologies/backlog_abox_v1_0_0.ttl", "# register\n")
    def key():
        sh = 'HERE="%s"; PKG="%s"; MERKLE="%s"; %s; TOOLKEY' % (os.path.join(pk, "03-tooling"), pk, MERKLE, m.group(0) if m else "")
        return subprocess.run(["bash", "-c", sh], capture_output=True, text=True).stdout.strip()
    k0 = key()
    expect("the key is a digest and is the same on a second run", bool(k0) and k0 == key(), k0[:16])
    W("01-ontologies/backlog_abox_v1_0_0.ttl", "# register changed\n")
    expect("a change of the register alone does not move the key", key() == k0)
    for label, rel in (("a tool", "03-tooling/backlog_a_v1_0_0.py"), ("a fixture", "03-tooling/fixtures/fixture_positive_v1_0_0.ttl"), ("the gate script", "03-tooling/backlog_gate_v1_0_0.sh"), ("the shapes", "02-shacl-safeguards/backlog_shacl_v1_0_0.ttl"), ("the vocabulary", "01-ontologies/backlog_tbox_v1_0_0.ttl")):
        before = key(); W(rel, open(os.path.join(pk, rel)).read() + "# changed\n")
        expect("a change of %s moves the key" % label, key() != before)
    W("03-tooling/backlog_new_v1_0_0.py", "b = 2\n"); k1 = key(); os.remove(os.path.join(pk, "03-tooling/backlog_new_v1_0_0.py"))
    expect("a new tool moves the key", k1 != key())
for sec in ("cache_proof", "gate_r_selfproof", "register_path", "lineage_order_selfproof"):
    expect("the gate keys the section %s and records it after its checks" % sec, ("KEYED_SKIP %s;" % sec) in text and ("KEYED_RECORD %s" % sec) in text)
    i, j = text.find("KEYED_SKIP %s;" % sec), text.find("KEYED_RECORD %s" % sec)
    body = text[i:j]
    expect("the section %s records only after its aborting checks (an abort leaves nothing recorded)" % sec, j > i and "exit 3" in body)
expect("BACKLOG_COLD=1 refuses the keyed skips", 'BACKLOG_COLD:-}" != 1' in text.split("KEYED_SKIP()")[1].split("\n")[0])
expect("the archived-lineages check runs once", text.count('python3 -B "$ADC"') == 1)
# the flow-point trace keeps what it read of each commit by the blob's hash and gives the same answer from the disk (Lineage 22, box 2, D6)
TRACE = latest("03-tooling/backlog_flow_point_git_trace_v*.py")
with tempfile.TemporaryDirectory() as d:
    repo, memo = os.path.join(d, "r"), os.path.join(d, "memo"); os.makedirs(repo); os.makedirs(memo)
    g = lambda *a: subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True)
    g("init", "-q", "-b", "main"); g("config", "user.email", "t@t"); g("config", "user.name", "t")
    PRE = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/t#> .\n"
    open(os.path.join(repo, "reg.ttl"), "w").write(PRE + "x:A backlog:hasState backlog:Proposed .\n"); g("add", "."); g("commit", "-q", "-m", "one")
    open(os.path.join(repo, "reg.ttl"), "w").write(PRE + "x:A backlog:hasState backlog:Done ; backlog:startedAt \"2020-01-01T10:00:00Z\"^^<http://www.w3.org/2001/XMLSchema#dateTime> ; backlog:finishedAt \"2020-01-01T11:00:00Z\"^^<http://www.w3.org/2001/XMLSchema#dateTime> .\n"); g("add", "."); g("commit", "-q", "-m", "two")
    run = lambda m: subprocess.run([sys.executable, TRACE, repo, "reg.ttl"], capture_output=True, text=True, env=dict(os.environ, **({"BACKLOG_VALIDATE_MEMO_DIR": m} if m else {})))
    cold, plain = run(memo), run(None)
    kept = [f for f in os.listdir(memo) if f.startswith("flowstates_")]
    warm = run(memo)
    expect("the trace keeps one file per commit it read and nothing else", len(kept) == 2, "%d file(s)" % len(kept))
    expect("a run from the kept files gives the output of a run with no cache and of the first run", cold.stdout == warm.stdout == plain.stdout and "state paths seen" in warm.stdout and cold.returncode == warm.returncode)
    expect("the trace still sees the path Proposed to Done", "Proposed -> Done" in warm.stdout)
expect("the gate parses", subprocess.run(["bash", "-n", GATE]).returncode == 0)
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
