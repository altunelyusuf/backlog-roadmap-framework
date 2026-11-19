#!/usr/bin/env python3
"""backlog_governance_mitigations_probe v1.2.0 -- the mechanisms of Lineage 16's last stories, each shown firing on a planted fault and silent on its twin.

  GOVMIT-S02  an item that records a start while its state is still Proposed or Ready, with no batch counter  -> ItemStartedStateStaleShape fires;
              with the state moved, with no start, or batch-tracked (the older rule owns it)                   -> silent
  GOVMIT-S03  a criterion's artefact path that leads outside the package ('..', an absolute path, a link out)    -> backlog_criterion_resolve reports it
              OUTSIDE ITS PACKAGE and does not resolve it; a path inside the package, and a named symbol in it   -> resolves
  IK-S86      backlog_criterion_resolve on a package's own register and root (--register, --root): reports each criterion of that register against that root only;
              without options it reads the framework as before
  IK-S89      the lineage practice guide: its five sections, every tool it names exists, the discipline points to it, the ruling it cites is in the register
Exit 0 when every case behaves; 3 otherwise.
Usage: backlog_governance_mitigations_probe_v1_0_0.py
"""
import glob, importlib.util, os, re, sys, tempfile
from rdflib import Graph, Namespace, Literal, RDF
from rdflib.namespace import XSD

HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
B = Namespace("http://example.org/backlog#"); P = Namespace("http://example.org/probe#"); SH = Namespace("http://www.w3.org/ns/shacl#")


def latest(sub, pat):
    hits = glob.glob(os.path.join(PKG, sub, pat))
    return sorted(hits, key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]])[-1]


def fired(shapes, data, marker, focus):
    import pyshacl
    _, rg, _ = pyshacl.validate(data, shacl_graph=shapes, inference="none", advanced=True, allow_warnings=True)
    return any(rg.value(r, SH.focusNode) == focus and marker in str(rg.value(r, SH.resultMessage)) for r in rg.subjects(RDF.type, SH.ValidationResult))


def item(state, started=True, batch=False):
    g = Graph(); g.add((P.Item, RDF.type, B.Story)); g.add((P.Item, RDF.type, B.WorkItem)); g.add((P.Item, B.hasState, state))  # typed WorkItem too: the probe runs without inference
    if started:
        g.add((P.Item, B.startedAt, Literal("2026-10-07T09:00:00Z", datatype=XSD.dateTime)))
    if batch:
        g.add((P.Item, B.hasBatchSize, Literal(10))); g.add((P.Item, B.hasBatchCompleted, Literal(2)))
    return g


if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(latest("02-shacl-safeguards", "backlog_shacl_v*.ttl")); print(latest("03-tooling", "backlog_criterion_resolve_v*.py"))
    print(latest("04-documentation", "LINEAGE_PRACTICE_GUIDE_v*.md")); print(latest("04-documentation", "LINEAGE_OPERATING_DISCIPLINE_v*.md")); print(latest("01-ontologies", "backlog_abox_v*.ttl"))
    sys.exit(0)


def own_register_cases():
    import subprocess
    tool = latest("03-tooling", "backlog_criterion_resolve_v*.py")
    def run(*a):
        r = subprocess.run([sys.executable, "-I", tool] + list(a), capture_output=True, text=True); return r.returncode, r.stdout + r.stderr
    out = []
    with tempfile.TemporaryDirectory() as t:
        root = os.path.join(t, "adopter"); os.makedirs(os.path.join(root, "files"))
        open(os.path.join(root, "files", "exists.md"), "w").write("here\n")
        reg = os.path.join(t, "adopter_register.ttl")
        open(reg, "w").write("""@prefix backlog: <http://example.org/backlog#> . @prefix pcl: <http://example.org/adopter#> .
pcl:AC1 a backlog:AcceptanceCriterion ; backlog:satisfiedByArtifact "files/exists.md" .
pcl:AC2 a backlog:AcceptanceCriterion ; backlog:satisfiedByArtifact "files/missing.md" .
pcl:AC3 a backlog:AcceptanceCriterion ; backlog:satisfiedByArtifact "../elsewhere.md" .
""")
        c, o = run("--register", reg, "--root", root)
        out.append(("package register and root: only that register's three criteria are read", "criteria naming an artefact : 3" in o and c == 0, True))
        out.append(("package register and root: the missing file is named unresolved", "UNRESOLVED  AC2" in o and "unresolved                  : 2" in o, True))
        out.append(("package register and root: the file that exists is not reported", "AC1" not in o, True))
        out.append(("package register and root: a path leading out of the root is named outside", "OUTSIDE ITS PACKAGE  AC3" in o, True))
        c, o = run("--register", reg, "--root", root, "--strict")
        out.append(("package register and root: --strict exits 1 on an unresolved criterion", c == 1, True))
        open(os.path.join(root, "files", "missing.md"), "w").write("now\n"); os.remove(os.path.join(t, "adopter_register.ttl"))
        open(reg, "w").write(open(reg).read() if os.path.exists(reg) else "")
        open(reg, "w").write("""@prefix backlog: <http://example.org/backlog#> . @prefix pcl: <http://example.org/adopter#> .
pcl:AC1 a backlog:AcceptanceCriterion ; backlog:satisfiedByArtifact "files/exists.md" .
pcl:AC2 a backlog:AcceptanceCriterion ; backlog:satisfiedByArtifact "files/missing.md" .
""")
        c, o = run("--register", reg, "--root", root, "--strict")
        out.append(("package register and root: with every file present it passes under --strict", c == 0 and "PASS" in o and "criteria naming an artefact : 2" in o, True))
        c, o = run("--register", os.path.join(t, "none.ttl"), "--root", root)
        out.append(("a register that does not exist is refused with exit 2", c == 2 and "register not found" in o, True))
        c, o = run("--register", reg, "--root", os.path.join(t, "none"))
        out.append(("a root that does not exist is refused with exit 2", c == 2 and "root not found" in o, True))
        c, o = run("--register")
        out.append(("an option with no value is refused with exit 2", c == 2 and "needs a value" in o, True))
    c, o = run()
    out.append(("without options the framework's own register and root are read, as before", c == 0 and "VERDICT     : PASS" in o and "criteria naming an artefact : 0" not in o, True))
    return out


def practice_guide_cases():
    out = []
    try:
        gpath = latest("04-documentation", "LINEAGE_PRACTICE_GUIDE_v*.md")
    except IndexError:
        return [("the lineage practice guide exists", False, True)]
    guide = open(gpath, encoding="utf-8").read(); disc_path = latest("04-documentation", "LINEAGE_OPERATING_DISCIPLINE_v*.md")
    disc = open(disc_path, encoding="utf-8").read(); register = open(latest("01-ontologies", "backlog_abox_v*.ttl"), encoding="utf-8").read()
    for h in ("Who may decide what", "Before a box", "When a tool refuses", "During and after a box", "Do not"):
        out.append(("the guide has the section '%s'" % h, bool(re.search(r"^## %s\s*$" % re.escape(h), guide, re.M)), True))
    names = sorted(set(re.findall(r"`(backlog_[a-z_]+)(?:\s[^`]*)?`", guide)))
    missing = [n for n in names if not glob.glob(os.path.join(PKG, "03-tooling", n + "_v*.py"))]
    out.append(("every tool the guide names exists in the tooling (%d named)" % len(names), len(names) >= 5 and not missing, True))
    out.append(("the discipline names the guide by its file name", os.path.basename(gpath) in disc, True))
    out.append(("the guide carries the Owner's instruction of 2026-11-18 as a ruling the register records", "G245" in guide and re.search(r'hasRulingIdentifier\s+"G245"', register) is not None, True))
    out.append(("the guide names the discipline file it is read beside, and it exists", os.path.basename(disc_path) in guide, True))
    out.append(("the guide states no way to ask BRSF other than the handover inbox and the Owner", "07-handover-inbox" in guide and "The Owner" in guide, True))
    return out


def main():
    shapes = Graph().parse(latest("02-shacl-safeguards", "backlog_shacl_v*.ttl"))
    M = "records a start (startedAt) but its hasState is still"
    spec = importlib.util.spec_from_file_location("cr", latest("03-tooling", "backlog_criterion_resolve_v*.py"))
    cr = importlib.util.module_from_spec(spec); spec.loader.exec_module(cr)
    results = [
        ("started, still Proposed, not batch-tracked: rule fires", fired(shapes, item(B.Proposed), M, P.Item), True),
        ("started, still Ready, not batch-tracked: rule fires", fired(shapes, item(B.Ready), M, P.Item), True),
        ("started and InProgress: rule silent", fired(shapes, item(B.InProgress), M, P.Item), False),
        ("Proposed, never started: rule silent", fired(shapes, item(B.Proposed, started=False), M, P.Item), False),
        ("started, Ready, batch-tracked (older rule owns it): silent", fired(shapes, item(B.Ready, batch=True), M, P.Item), False),
    ]
    with tempfile.TemporaryDirectory() as t:
        pkg = os.path.join(t, "pkg"); other = os.path.join(t, "other")
        os.makedirs(os.path.join(pkg, "03-tooling")); os.makedirs(other)
        open(os.path.join(pkg, "03-tooling", "tool.py"), "w").write("def Symbol():\n    pass\n")
        open(os.path.join(other, "tool.py"), "w").write("def Symbol():\n    pass\n")
        os.symlink(other, os.path.join(pkg, "link"))
        inside = "03-tooling/tool.py -- Symbol"
        results += [
            ("path inside the package: resolves", cr.resolve(inside, set(), pkg), True),
            ("path inside the package: not outside", cr.outside_package(inside, pkg), False),
            ("'..' path into a sibling package: named as outside", cr.outside_package("../other/tool.py -- Symbol", pkg), True),
            ("'..' path into a sibling package: does not resolve", cr.resolve("../other/tool.py -- Symbol", set(), pkg), False),
            ("absolute path outside: named as outside", cr.outside_package(os.path.join(other, "tool.py") + " -- Symbol", pkg), True),
            ("a link inside the package that leaves it: named as outside", cr.outside_package("link/tool.py -- Symbol", pkg), True),
            ("an IRI target is never outside", cr.outside_package("backlog:Story", pkg), False),
        ]
    results += own_register_cases() + practice_guide_cases()
    bad = 0
    for label, got, want in results:
        ok = got == want; bad += not ok
        print("  %-62s %s" % (label, "ok" if ok else "FAILED (got %s)" % got))
    print("VERDICT : " + ("PASS -- every mechanism fires on its fault and is silent on its twin" if not bad else "FAIL -- %d case(s) did not discriminate" % bad))
    return 0 if not bad else 3


if __name__ == "__main__":
    sys.exit(main())
