#!/usr/bin/env python3
"""backlog_stamp_key_probe v1.0.0 -- a stamp that says "unchanged" must change when anything it stands on changes (G99 release B; OE rule R9).

The gate skips the fixture suite, and the clause proof skips its run, when a stamp equals a key over their inputs. A key that leaves out an input says
"unchanged" over a changed checker. This probe builds a throwaway package layout and shows, for BOTH keys (the gate's FIXKEY, taken from the gate's own text
and run in bash, and the clause proof's _key):
  1 the same bytes give the same key;
  2 a changed shapes file, T-Box, fixture or VALIDATOR changes it;
  3 (clause proof) a changed copy of the clause proof itself changes it.
Exit 0 all hold; 2 a case failed; 3 the gate's key text could not be found.
"""
import glob, importlib.util, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def newest(pattern):
    def key(p):
        m = re.search(r"_v(\d+)_(\d+)_(\d+)\.", p)
        return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)
    return sorted(glob.glob(pattern), key=key)[-1]


GATE = sys.argv[1] if len(sys.argv) > 1 else newest(os.path.join(HERE, "backlog_gate_v*.sh")); CP = newest(os.path.join(HERE, "backlog_clause_proof_v*.py"))
m = re.search(r'^(FIXKEY="\$\(.*?\| cut -d\' \' -f1\)")', open(GATE).read(), re.M | re.S)
if not m:
    print("GATE KEY TEXT NOT FOUND"); sys.exit(3)
SNIPPET = m.group(1)
bad = []


def check(name, cond):
    print("  %-4s %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        bad.append(name)


def layout(d):
    for sub in ("01-ontologies", "02-shacl-safeguards", "03-tooling/fixtures"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    for rel, txt in (("01-ontologies/backlog_tbox_v1_0_0.ttl", "tbox"), ("02-shacl-safeguards/backlog_shacl_v1_0_0.ttl", "shapes"),
                     ("03-tooling/fixtures/f1.ttl", "fixture"), ("03-tooling/backlog_validate_v1_0_0.py", "validator")):
        open(os.path.join(d, rel), "w").write(txt)
    shutil.copy(CP, os.path.join(d, "03-tooling", os.path.basename(CP)))


def gate_key(d):
    r = subprocess.run(["bash", "-c", 'HERE="%s"; %s; printf %%s "$FIXKEY"' % (os.path.join(d, "03-tooling"), SNIPPET)], capture_output=True, text=True)
    return r.stdout.strip()


def clause_key(d):
    spec = importlib.util.spec_from_file_location("cp_probe", os.path.join(d, "03-tooling", os.path.basename(CP)))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod._key(d)


with tempfile.TemporaryDirectory() as d:
    layout(d)
    for label, keyf in (("gate fixture-suite key", gate_key), ("clause-proof key", clause_key)):
        base = keyf(d)
        check("%s: the same bytes give the same key" % label, bool(base) and keyf(d) == base)
        for rel, what in (("02-shacl-safeguards/backlog_shacl_v1_0_0.ttl", "shapes"), ("01-ontologies/backlog_tbox_v1_0_0.ttl", "T-Box"),
                          ("03-tooling/fixtures/f1.ttl", "a fixture"), ("03-tooling/backlog_validate_v1_0_0.py", "the VALIDATOR")):
            p = os.path.join(d, rel); old = open(p).read()
            if label.startswith("gate") and what == "T-Box":
                pass
            open(p, "w").write(old + " changed")
            check("%s: changing %s changes the key" % (label, what), keyf(d) != base)
            open(p, "w").write(old)
        check("%s: restored bytes give the original key" % label, keyf(d) == base)
    p = os.path.join(d, "03-tooling", os.path.basename(CP)); old = open(p).read()
    base = clause_key(d); open(p, "w").write(old + "\n# changed\n")
    check("clause-proof key: changing the clause proof itself changes it", clause_key(d) != base)
print("VERDICT : " + ("ALL HOLD" if not bad else "FAILED -- " + "; ".join(bad)))
sys.exit(0 if not bad else 2)
