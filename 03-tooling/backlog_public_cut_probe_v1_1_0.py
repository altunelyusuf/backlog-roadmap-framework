#!/usr/bin/env python3
"""backlog_public_cut_probe v1.1.0 -- the public copy is cut by each module's declared audience, and stops when it cannot be sure (Lineage 19, DC-S04).

Runs the deriver's cut over small planted texts and requires:
  1. a module declared private is cut, banner to END line, and the text around it is kept;
  2. a module declared public is kept whole;
  3. a module record with no audience stops the derivation with an error naming the module;
  4. a module record with no END MODULE line stops it, naming the module (the old deriver skipped a listed module it could not find);
  5. a private module whose banner is missing stops it;
  6. the real package's own data files cut exactly the modules they declare private, and no data file errors.
Exit 0 when all hold, 3 otherwise.
"""
import glob, importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
BAR = "#" * 65


def deriver():
    p = sorted(glob.glob(os.path.join(HERE, "make_public_distribution_v*.py")), key=lambda x: [int(n) for n in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", x)[0]])[-1]
    spec = importlib.util.spec_from_file_location("mpd", p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m, os.path.basename(p)


def module(iri, audience, body="x:a x:b x:c .\n", end=True, banner=True):
    t = ""
    if banner:
        t += BAR + "\n#  MODULE probe %s\n" % iri.rsplit("/", 1)[-1] + BAR + "\n"
    t += "<%s> dcterms:isPartOf <http://example.org/probe> ;\n" % iri
    if audience:
        t += "    backlog:moduleAudience backlog:%s ;\n" % audience
    t += '    rdfs:label "probe" .\n' + body
    if end:
        t += "#  END MODULE <%s>\n" % iri
    return t


def raises(fn):
    try:
        fn()
    except SystemExit as e:
        return str(e.code) if e.code else "exit"
    return None


if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__))
    print(sorted(glob.glob(os.path.join(HERE, "make_public_distribution_v*.py")), key=lambda x: [int(n) for n in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", x)[0]])[-1])
    for f in sorted(glob.glob(os.path.join(PKG, "01-ontologies", "**", "*.ttl"), recursive=True)):
        print(f)
    sys.exit(0)


def main():
    m, name = deriver()
    out = []
    keep = "x:keep x:this x:line .\n"
    t, cut = m.cut_modules(keep + module("http://example.org/p1", "Aud_Private") + keep)
    out.append(("private module is cut, surroundings kept", cut == ["http://example.org/p1"] and "p1" not in t and t.count(keep) == 2))
    t, cut = m.cut_modules(keep + module("http://example.org/p2", "Aud_Public") + keep)
    out.append(("public module is kept whole", cut == [] and "p2" in t))
    e = raises(lambda: m.cut_modules(module("http://example.org/p3", None)))
    out.append(("no audience stops, naming the module", e is not None and "p3" in e))
    e = raises(lambda: m.cut_modules(module("http://example.org/p4", "Aud_Private", end=False)))
    out.append(("no END line stops, naming the module", e is not None and "p4" in e))
    e = raises(lambda: m.cut_modules(module("http://example.org/p5", "Aud_Private", banner=False)))
    out.append(("private module with no banner stops", e is not None and "p5" in e))
    # the real files
    real_ok, cuts = True, 0
    for f in sorted(glob.glob(os.path.join(PKG, "01-ontologies", "**", "*.ttl"), recursive=True)):
        txt = open(f, encoding="utf-8").read()
        declared = len(re.findall(r"backlog:moduleAudience\s+backlog:Aud_Private", txt))
        if "dcterms:isPartOf <" in txt or "#  END MODULE <" in txt:
            try:
                _, cut = m.cut_modules(txt, os.path.basename(f))
            except SystemExit as e:
                real_ok = False; print("   real file error:", e)
                continue
            real_ok &= len(cut) == declared; cuts += len(cut)
    out.append(("the package's own data files cut exactly the modules declared private (%d)" % cuts, real_ok and cuts > 0))
    bad = 0
    for label, ok in out:
        bad += not ok
        print("  %-78s %s" % (label, "ok" if ok else "FAILED"))
    print("deriver : %s" % name)
    print("VERDICT : " + ("PASS" if not bad else "FAIL -- %d probe(s) failed" % bad))
    return 0 if not bad else 3


if __name__ == "__main__":
    sys.exit(main())
