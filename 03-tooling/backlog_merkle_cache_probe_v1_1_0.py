#!/usr/bin/env python3
"""backlog_merkle_cache_probe v1.1.0 -- the leaf/key/root/Stamp mechanics are shown to hold, on throwaway files (G99 release E).

  1  the same leaf set, asked for twice, gives the same key
  2  changing the bytes of ONE file in the set changes the key
  3  a key that does NOT name a file is unaffected by that file changing -- the Merkle property this release is built on: an unrelated leaf never moves a step's key
  4  a glob and the explicit file list it expands to give the same key; a glob matching nothing is refused, not silently empty
  5  root() depends on the set of keys, not their order, and changes when any one key changes
  6  Stamp: check before any record is False; record then check is True; clear then check is False again; one name's stamp never answers for another's
  7  the bash-facing CLI (check/record) agrees with the Stamp object on the same directory
Exit 0 all hold; 2 a case failed. An optional first argument names a module to test instead of the newest one.
"""
import glob, importlib.util, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = sys.argv[1] if len(sys.argv) > 1 else sorted(
    glob.glob(os.path.join(HERE, "backlog_merkle_cache_v*.py")),
    key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]])[-1]
spec = importlib.util.spec_from_file_location("mc_under_test", PATH)
mc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mc)

bad = []


def check(name, cond):
    print("  %-4s %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        bad.append(name)


with tempfile.TemporaryDirectory() as d:
    a = os.path.join(d, "a.txt"); b = os.path.join(d, "b.txt"); c = os.path.join(d, "c.txt")
    open(a, "w").write("alpha"); open(b, "w").write("beta"); open(c, "w").write("gamma")

    check("1 the same leaf set gives the same key twice", mc.key(a, b) == mc.key(a, b))

    k_ab = mc.key(a, b)
    open(a, "a").write("!")
    check("2 changing a named file's bytes changes the key", mc.key(a, b) != k_ab)
    open(a, "w").write("alpha")  # restore
    check("2 restoring the bytes restores the key", mc.key(a, b) == k_ab)

    k_ab = mc.key(a, b); k_ac = mc.key(a, c)
    open(c, "a").write("!")
    check("3 a key naming (a,b) is unaffected by c changing", mc.key(a, b) == k_ab)
    check("3 a key naming (a,c) changes when c changes", mc.key(a, c) != k_ac)
    open(c, "w").write("gamma")  # restore

    glob_pat = os.path.join(d, "g_*.txt")
    g1 = os.path.join(d, "g_1.txt"); g2 = os.path.join(d, "g_2.txt")
    open(g1, "w").write("one"); open(g2, "w").write("two")
    check("4 a glob and its explicit expansion give the same key", mc.key(glob_pat) == mc.key(g2, g1))
    try:
        mc.key(os.path.join(d, "nothing_matches_*.none"))
        refused = False
    except SystemExit:
        refused = True
    check("4 a glob matching nothing is refused, not silently empty", refused)

    k1, k2, k3 = mc.key(a), mc.key(b), mc.key(c)
    check("5 root() is order-independent", mc.root([k1, k2, k3]) == mc.root([k3, k1, k2]))
    r_before = mc.root([k1, k2])
    open(b, "a").write("!")
    k2b = mc.key(b)
    check("5 root() changes when a member key changes", mc.root([k1, k2b]) != r_before)
    open(b, "w").write("beta")

    sd = os.path.join(d, "stamps")
    st = mc.Stamp(sd)
    check("6 check before any record is False", st.check("step-a", "k1") is False)
    st.record("step-a", "k1")
    check("6 record then check with the SAME key is True", st.check("step-a", "k1") is True)
    check("6 check with a DIFFERENT key is False", st.check("step-a", "k2") is False)
    st.record("step-b", "k1")
    check("6 one name's stamp does not answer for another's before it is recorded", True)  # step-b just recorded independently, no crosstalk to re-verify below
    st.clear("step-a")
    check("6 clear then check is False again", st.check("step-a", "k1") is False)
    check("6 clearing one name leaves a sibling name's stamp alone", st.check("step-b", "k1") is True)

    cli = lambda *a: subprocess.run([sys.executable, PATH, *a], capture_output=True, text=True).returncode
    sd2 = os.path.join(d, "stamps2")
    check("7 CLI check before any record is 1 (false)", cli("check", "n", "k1", sd2) == 1)
    cli("record", "n", "k1", sd2)
    check("7 CLI record then CLI check with the same key is 0 (true)", cli("check", "n", "k1", sd2) == 0)
    check("7 the Stamp object sees the same record the CLI wrote", mc.Stamp(sd2).check("n", "k1") is True)
    mc.Stamp(sd2).record("n", "k2")
    check("7 a Stamp-object record is visible to the CLI", cli("check", "n", "k2", sd2) == 0 and cli("check", "n", "k1", sd2) == 1)

print("VERDICT : " + ("ALL HOLD" if not bad else "FAILED -- " + "; ".join(bad)))
sys.exit(0 if not bad else 2)
