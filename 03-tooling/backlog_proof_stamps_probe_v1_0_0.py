#!/usr/bin/env python3
"""backlog_proof_stamps_probe v1.0.0 -- proof that a recorded stamp is honoured exactly when its inputs are unchanged, and that the validation cache stays small (G126).

  1  the gate's own STAMPED function (read out of the gate text) honours a stamp recorded in the package file, counts it, and says where it came from
  2  it refuses a stamp whose key differs (an input changed), a stamp for another name, and every stamp when BACKLOG_COLD=1
  3  a stamp made in the session is honoured and counted apart from a recorded one
  4  one validation writes ONE shape bundle and no per-shape file, and a second run replays every shape from it
  5  the release tool's prune removes the old one-file-per-shape cache only with --legacy, and keeps recent bundles
Exit 0 all hold; 2 a case failed. `--deps` prints what the probe reads (the stamp key of the gate stamps THIS probe on exactly that).
"""
import glob, os, re, subprocess, sys, tempfile, json

HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
newest = lambda pat: sorted(glob.glob(os.path.join(HERE, pat)), key=sv)[-1]
GATE, MERKLE, VALIDATE, RELTOOL = (newest(x) for x in ("backlog_gate_v*.sh", "backlog_merkle_cache_v*.py", "backlog_validate_v*.py", "backlog_release_tool_v*.py"))
POS = sorted(glob.glob(os.path.join(HERE, "fixtures", "fixture_positive_v*.ttl")), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    for x in (os.path.abspath(__file__), GATE, MERKLE, VALIDATE, RELTOOL, POS):
        print(x)
    sys.exit(0)
bad = []


def check(name, ok):
    print("  %-4s %s" % ("ok" if ok else "FAIL", name))
    if not ok: bad.append(name)


text = open(GATE).read()
m = re.search(r"^(STAMPS_MEMO=0.*?^\}\n)", text[text.index("PROOF_STAMPS="):], re.M | re.S)
block = m.group(1) if m else ""
check("0 the gate text holds the STAMPED function", "STAMPED()" in block)

with tempfile.TemporaryDirectory() as d:
    memo, repo = os.path.join(d, "memo"), os.path.join(d, "PROOF_STAMPS.json")
    json.dump({"format": 1, "entries": {"probe:a": "k1"}}, open(repo, "w"))
    def run(calls, env=None):
        script = 'MERKLE="%s"; BACKLOG_VALIDATE_MEMO_DIR="%s"; PROOF_STAMPS="%s"\n%s\n%s\necho "R=$STAMPS_REPO M=$STAMPS_MEMO N=$STEPS_RUN"' % (MERKLE, memo, repo, block, calls)
        return subprocess.run(["bash", "-c", script], capture_output=True, text=True, env=dict(os.environ, **(env or {}))).stdout.strip()
    check("1 a recorded stamp with the right key is honoured and counted as repo", run('STAMPED probe:a k1 && echo yes') == "yes\nR=1 M=0 N=0")
    check("2 a recorded stamp with another key is not honoured", run('STAMPED probe:a k2 || echo no') == "no\nR=0 M=0 N=1")
    check("2 a recorded stamp does not answer for another name", run('STAMPED probe:b k1 || echo no') == "no\nR=0 M=0 N=1")
    check("2 BACKLOG_COLD=1 refuses a recorded stamp", run('STAMPED probe:a k1 || echo no', {"BACKLOG_COLD": "1"}) == "no\nR=0 M=0 N=1")
    subprocess.run([sys.executable, MERKLE, "record", "probe:c", "k3", memo])
    check("3 a session stamp is honoured and counted as memo", run('STAMPED probe:c k3 && echo yes') == "yes\nR=0 M=1 N=0")
    check("3 BACKLOG_COLD=1 refuses a session stamp too", run('STAMPED probe:c k3 || echo no', {"BACKLOG_COLD": "1"}) == "no\nR=0 M=0 N=1")

    cache = os.path.join(d, "cache"); os.makedirs(cache)
    env = dict(os.environ, BACKLOG_VALIDATE_MEMO_DIR=cache)
    v = lambda: subprocess.run([sys.executable, VALIDATE, POS], capture_output=True, text=True, env=env)
    r1 = v(); names = os.listdir(cache)
    check("4 one validation leaves exactly one shape bundle and no per-shape file",
          sum(n.startswith("shapes_") for n in names) == 1 and not any(re.fullmatch(r"shape_[0-9a-f]+\.ttl", n) for n in names))
    for n in names:
        if re.fullmatch(r"[0-9a-f]{64}\.json", n): os.remove(os.path.join(cache, n))
    r2 = v(); mm = re.search(r"SHAPECACHE hits=(\d+) ran=(\d+) of (\d+)", r2.stderr + r2.stdout)
    check("4 the second run replays every shape from the bundle", bool(mm) and mm.group(2) == "0" and mm.group(1) == mm.group(3) and int(mm.group(3)) > 0)
    check("4 both runs say the same thing about the fixture", re.findall(r"VERDICT.*", r1.stdout) == re.findall(r"VERDICT.*", r2.stdout))

    pc = os.path.join(d, "prune"); os.makedirs(pc)
    old = os.path.join(pc, "shape_" + "a" * 64 + ".ttl"); new = os.path.join(pc, "shapes_" + "b" * 64 + ".json")
    open(old, "w").write("x"); open(new, "w").write("{}")
    subprocess.run([sys.executable, RELTOOL, "prune-cache", pc, "--days", "14"], capture_output=True)
    check("5 prune without --legacy keeps a recent per-shape file and a recent bundle", os.path.exists(old) and os.path.exists(new))
    subprocess.run([sys.executable, RELTOOL, "prune-cache", pc, "--days", "14", "--legacy"], capture_output=True)
    check("5 prune --legacy removes the per-shape file and keeps the recent bundle", not os.path.exists(old) and os.path.exists(new))

print("VERDICT : " + ("ALL HOLD" if not bad else "FAILED -- " + "; ".join(bad)))
sys.exit(0 if not bad else 2)
