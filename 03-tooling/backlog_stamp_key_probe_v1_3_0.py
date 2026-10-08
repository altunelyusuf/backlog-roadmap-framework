#!/usr/bin/env python3
"""backlog_stamp_key_probe v1.3.0 -- a stamp that says "unchanged" must change when anything it stands on changes, and must NOT change over a leaf it never
named (G99 release B, generalised in release E for the per-fixture Merkle key; OE rule R9).

The gate skips a fixture's own validation, and the clause proof skips its run, when a stamp equals a key over their inputs. A key that leaves out an input says
"unchanged" over a changed checker -- that half is unchanged from release B. Release E's fixture key also claims something release B's single flat FIXKEY could
not: that fixture A's key is deaf to fixture B's bytes. This probe builds a throwaway package layout with TWO fixtures and shows, for all three keys (the gate's
per-fixture key, taken from the gate's own text and run in bash; and the clause proof's _key):
  1 the same bytes give the same key;
  2 a changed shapes file, T-Box, VALIDATOR or MEMO changes every fixture's key (a leaf they all share);
  3 (gate only) changing fixture A's OWN bytes changes A's key but not fixture B's -- the property this release is built on;
  4 (clause proof) a changed copy of the clause proof itself changes its key.
Exit 0 all hold; 2 a case failed; 3 the gate's key text could not be found.
"""
import glob, importlib.util, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def newest(pattern):
    def key(p):
        m = re.search(r"_v(\d+)_(\d+)_(\d+)\.", p)
        return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)
    return sorted(glob.glob(pattern), key=key)[-1]


_ARGS = [a for a in sys.argv[1:] if a != "--deps"]
GATE = _ARGS[0] if _ARGS else newest(os.path.join(HERE, "backlog_gate_v*.sh"))
CP = newest(os.path.join(HERE, "backlog_clause_proof_v*.py"))
MERKLE = newest(os.path.join(HERE, "backlog_merkle_cache_v*.py"))
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(GATE); print(CP); print(MERKLE)
    sys.exit(0)

GATE_TEXT = open(GATE).read()


def extract(pattern, what):
    m = re.search(pattern, GATE_TEXT, re.M)
    if not m:
        print("GATE TEXT NOT FOUND: %s" % what); sys.exit(3)
    return m.group(1)


MERKLE_LINE = extract(r'^(MERKLE="\$\(ls.*?\|\| true\)")', "the MERKLE discovery line")
BASE_LEAVES_LINE = extract(r'^(BASE_LEAVES=\(.*?\))', "the BASE_LEAVES array")
KEY_LINE = extract(r'^(\s*K="\$\(python3 "\$MERKLE" key "\$\{BASE_LEAVES\[@\]\}" "\$FX"\)")', "the per-fixture key line")

bad = []


def check(name, cond):
    print("  %-4s %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        bad.append(name)


def layout(d):
    for sub in ("01-ontologies", "02-shacl-safeguards", "03-tooling/fixtures"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    for rel, txt in (("01-ontologies/backlog_tbox_v1_0_0.ttl", "tbox"), ("02-shacl-safeguards/backlog_shacl_v1_0_0.ttl", "shapes"),
                     ("03-tooling/fixtures/f1.ttl", "fixture one"), ("03-tooling/fixtures/f2.ttl", "fixture two"),
                     ("03-tooling/backlog_validate_v1_0_0.py", "validator"), ("03-tooling/backlog_sparql_memo_v1_0_0.py", "memo")):
        open(os.path.join(d, rel), "w").write(txt)
    shutil.copy(CP, os.path.join(d, "03-tooling", os.path.basename(CP)))
    shutil.copy(MERKLE, os.path.join(d, "03-tooling", os.path.basename(MERKLE)))


def gate_key(d, fixture_rel="03-tooling/fixtures/f1.ttl"):
    here = os.path.join(d, "03-tooling")
    fx = os.path.join(d, fixture_rel)
    script = 'HERE="%s"; %s\n%s\nFX="%s"\n%s\nprintf %%s "$K"' % (here, MERKLE_LINE, BASE_LEAVES_LINE, fx, KEY_LINE)
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    return r.stdout.strip()


def clause_key(d):
    spec = importlib.util.spec_from_file_location("cp_probe", os.path.join(d, "03-tooling", os.path.basename(CP)))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod._key(d)


with tempfile.TemporaryDirectory() as d:
    layout(d)
    for label, keyf in (("gate fixture key (f1)", gate_key), ("clause-proof key", clause_key)):
        base = keyf(d)
        check("%s: the same bytes give the same key" % label, bool(base) and keyf(d) == base)
        shared = [("02-shacl-safeguards/backlog_shacl_v1_0_0.ttl", "shapes"), ("01-ontologies/backlog_tbox_v1_0_0.ttl", "T-Box"),
                  ("03-tooling/backlog_validate_v1_0_0.py", "the VALIDATOR"), ("03-tooling/backlog_sparql_memo_v1_0_0.py", "the QUERY MEMO")]
        if label.startswith("clause"):
            shared.append(("03-tooling/fixtures/f1.ttl", "a fixture"))
        for rel, what in shared:
            p = os.path.join(d, rel); old = open(p).read()
            open(p, "w").write(old + " changed")
            check("%s: changing %s changes the key" % (label, what), keyf(d) != base)
            open(p, "w").write(old)
        check("%s: restored bytes give the original key" % label, keyf(d) == base)
    # the property release E is built on: fixture A's key is deaf to fixture B's bytes
    base_f1 = gate_key(d, "03-tooling/fixtures/f1.ttl")
    base_f2 = gate_key(d, "03-tooling/fixtures/f2.ttl")
    p2 = os.path.join(d, "03-tooling/fixtures/f2.ttl"); old2 = open(p2).read()
    open(p2, "w").write(old2 + " changed")
    check("gate fixture key (f1): unaffected by fixture f2 changing", gate_key(d, "03-tooling/fixtures/f1.ttl") == base_f1)
    check("gate fixture key (f2): DOES change when f2 itself changes", gate_key(d, "03-tooling/fixtures/f2.ttl") != base_f2)
    open(p2, "w").write(old2)
    p = os.path.join(d, "03-tooling", os.path.basename(CP)); old = open(p).read()
    base = clause_key(d); open(p, "w").write(old + "\n# changed\n")
    check("clause-proof key: changing the clause proof itself changes it", clause_key(d) != base)
print("VERDICT : " + ("ALL HOLD" if not bad else "FAILED -- " + "; ".join(bad)))
sys.exit(0 if not bad else 2)
