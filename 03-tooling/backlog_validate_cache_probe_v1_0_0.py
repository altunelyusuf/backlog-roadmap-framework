#!/usr/bin/env python3
"""backlog_validate_cache_probe v1.0.0 -- the per-shape result cache and the split validation change no verdict (G99 release A2).

The probe builds its own small shapes file and register (a named shape with a property rule, a query constraint, a shape pointing to another, and a RULE
whose derived fact another shape depends on, so a result that flows between nodes is exercised) and runs the validator on them in separate processes:
  1 reference     : the plain single-process pyshacl run, no cache, no split (BACKLOG_VALIDATE_NOSHAPECACHE=single)
  2 cold cache    : empty cache, two shards          -> same report as 1, every shape judged (hits 0)
  3 warm cache    : same inputs again                -> same report as 1, every shape replayed (ran 0)
  4 planted SHAPE : one message changed              -> same report as the reference run on the planted shapes; only the changed shape(s) judged again
  5 planted DATA  : one triple added                 -> same report as the reference on the planted data; EVERY shape judged again; report differs from 1
  6 planted RULE  : the rule's query changed         -> same report as the reference on the planted shapes; EVERY shape judged again; report differs from 1
  7 lost share    : a shard that drops shapes (BACKLOG_VALIDATE_SHARD_FAULT=drop) is refused, never reported as a pass
A comparison that cannot see a difference is refused (cases 4 to 6 must differ from case 1 where the plant changes the verdict).
A pass is stored once per set of bytes (R9): key = this probe, the validator, the T-Box and the data file; only passes are stored.
Exit 0 all hold; 2 a case failed; 3 the probe cannot discriminate. Usage: backlog_validate_cache_probe_v1_0_0.py
"""
import glob, hashlib, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)


def newest(pattern):
    def key(p):
        m = re.search(r"_v(\d+)_(\d+)_(\d+)\.", p)
        return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)
    return sorted(glob.glob(pattern), key=key)[-1]


VALIDATE = newest(os.path.join(HERE, "backlog_validate_v*.py"))
SHAPES = '''@prefix sh: <http://www.w3.org/ns/shacl#> . @prefix ex: <http://t/> . @prefix owl: <http://www.w3.org/2002/07/owl#> .
<http://t/shapes> a owl:Ontology ; owl:versionInfo "1.0.0" .
ex:RuleShape a sh:NodeShape ; sh:targetClass ex:Thing ;
  sh:rule [ a sh:SPARQLRule ; sh:construct "CONSTRUCT { $this <http://t/derived> \\"yes\\" } WHERE { $this <http://t/child> ?c }" ] .
ex:NameShape a sh:NodeShape ; sh:targetClass ex:Thing ;
  sh:property [ sh:path ex:name ; sh:minCount 1 ; sh:message "a thing needs a name" ] .
ex:DerivedShape a sh:NodeShape ; sh:targetClass ex:Thing ;
  sh:sparql [ a sh:SPARQLConstraint ; sh:message "needs the derived fact" ;
    sh:select "SELECT $this WHERE { $this <http://t/needsDerived> true . FILTER NOT EXISTS { $this <http://t/derived> ?d } }" ] .
ex:HolderShape a sh:NodeShape ; sh:targetClass ex:Holder ; sh:node ex:NameShape .
ex:OtherShape a sh:NodeShape ; sh:targetClass ex:Other ;
  sh:property [ sh:path ex:size ; sh:datatype <http://www.w3.org/2001/XMLSchema#integer> ; sh:message "size must be an integer" ] .
'''
DATA = '''@prefix ex: <http://t/> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
ex:t1 a ex:Thing .
ex:t2 a ex:Thing ; ex:name "two" ; ex:child ex:c ; ex:needsDerived true .
ex:t3 a ex:Thing ; ex:name "three" ; ex:needsDerived true .
ex:h1 a ex:Holder ; ex:name "h" .
ex:o1 a ex:Other ; ex:size "x" .
'''


def run(tag, shapes, data, shape_dir, env_extra=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("BACKLOG_VALIDATE")}
    env.update({"BACKLOG_VALIDATE_SHAPES": shapes, "BACKLOG_VALIDATE_SHAPE_DIR": shape_dir, "BACKLOG_VALIDATE_SHARDS": "2"})
    env.update(env_extra or {})
    p = subprocess.run([sys.executable, VALIDATE, data], capture_output=True, text=True, env=env)
    out = "\n".join(l for l in p.stdout.splitlines() if not re.match(r"(shapes|tooling|data)\s*:", l))
    m = re.search(r"SHAPECACHE hits=(\d+) ran=(\d+) of (\d+)", p.stderr)
    return p.returncode, out, tuple(int(x) for x in m.groups()) if m else None, p.stderr


def main():
    h = hashlib.sha256()
    for f in (os.path.abspath(__file__), VALIDATE, newest(os.path.join(PKG, "01-ontologies", "backlog_tbox_v*.ttl")), newest(os.path.join(PKG, "01-ontologies", "backlog_abox_v*.ttl"))):
        h.update(os.path.basename(f).encode()); h.update(open(f, "rb").read())
    memo = os.environ.get("BACKLOG_VALIDATE_MEMO_DIR")
    stamp = os.path.join(memo, "cacheproof_" + h.hexdigest() + ".ok") if memo else None
    if stamp and os.path.exists(stamp) and not os.environ.get("BACKLOG_VALIDATE_FRESH"):
        print("cache probe : identical bytes to a passing run -- not run again"); return 0
    bad = []

    def check(name, cond):
        print("  %-4s %s" % ("ok" if cond else "FAIL", name))
        if not cond:
            bad.append(name)
    with tempfile.TemporaryDirectory() as d:
        w = lambda n, t: (open(os.path.join(d, n), "w").write(t), os.path.join(d, n))[1]
        sh, da = w("s.ttl", SHAPES), w("d.ttl", DATA)
        sh_pl = w("s_pl.ttl", SHAPES.replace("a thing needs a name", "a thing needs a name PLANTED"))
        da_pl = w("d_pl.ttl", DATA + "ex:t4 a ex:Thing .\n")
        sh_rule = w("s_rule.ttl", SHAPES.replace("<http://t/child>", "<http://t/kid>"))
        cache = os.path.join(d, "cache"); os.makedirs(cache)
        rc, ref, _, e = run("ref", sh, da, cache, {"BACKLOG_VALIDATE_NOSHAPECACHE": "single"})
        if "NON-CONFORMANT" not in ref:
            print("PROBE UNUSABLE : the reference register must violate\n" + e[-300:]); return 3
        rc, o, st, _ = run("cold", sh, da, cache); total = st[2] if st else -1
        check("2 cold cache equals the reference, every shape judged", o == ref and st and st[0] == 0 and st[1] == total > 0)
        rc, o, st, _ = run("warm", sh, da, cache)
        check("3 warm cache equals the reference, every shape replayed", o == ref and st and st[1] == 0 and st[0] == total)
        rc, refp, _, _ = run("refp", sh_pl, da, cache, {"BACKLOG_VALIDATE_NOSHAPECACHE": "single"})
        rc, o, st, _ = run("shape", sh_pl, da, cache)
        check("4 a planted shape change equals its reference and is judged again alone", o == refp and o != ref and st and 0 < st[1] < total)
        rc, refd, _, _ = run("refd", sh, da_pl, cache, {"BACKLOG_VALIDATE_NOSHAPECACHE": "single"})
        rc, o, st, _ = run("data", sh, da_pl, cache)
        check("5 a planted data change equals its reference and every shape is judged again", o == refd and o != ref and st and st[1] == total and st[0] == 0)
        rc, refr, _, _ = run("refr", sh_rule, da, cache, {"BACKLOG_VALIDATE_NOSHAPECACHE": "single"})
        rc, o, st, _ = run("rule", sh_rule, da, cache)
        check("6 a planted rule change equals its reference and every shape is judged again", o == refr and o != ref and st and st[1] == st[2] and st[0] == 0)
        rc, o, st, e = run("lost", sh_pl, da_pl, cache, {"BACKLOG_VALIDATE_SHARD_FAULT": "drop"})
        check("7 a shard that drops shapes is refused, not passed", rc != 0 and "SHARD REFUSED" in e and "CONFORMANT" not in o.replace("NON-CONFORMANT", ""))
    print("VERDICT : " + ("ALL HOLD" if not bad else "FAILED -- " + "; ".join(bad)))
    if not bad and stamp:
        open(stamp, "w").write("ok\n")
    return 0 if not bad else 2


if __name__ == "__main__":
    sys.exit(main())
