#!/usr/bin/env python3
"""backlog_archive_forms_probe v1.0.0 -- the archive tool moves a statement whatever the form of its subject (Lineage 22, D2).

A register holds the same subject written as a prefixed name or as a full IRI. v2.9.0 of the tool moved the first form only and left 59 statements of Lineage 20 in the
live register. Cases: a prefixed and a full-IRI statement of the lineage both move, with their continuation lines; a statement of another lineage in either form stays;
comments stay; with the full IRIs not given (the v2.9.0 reading) the full-IRI statement stays, so the case discriminates."""
import glob, importlib.util, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
tool = sorted(glob.glob(os.path.join(HERE, "backlog_lineage_archive_v*.py")), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(tool); sys.exit(0)
spec = importlib.util.spec_from_file_location("lar", tool); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
bad = []
def expect(n, ok):
    print(("PASS  " if ok else "FAIL  ") + n)
    if not ok: bad.append(n)
NS = "http://example.org/r#"
lines = ["@prefix fw: <%s> ." % NS, "# a comment that stays", "fw:Mine a fw:Thing ;", "    fw:p 1 .",
         "<%sMineFull> a fw:Thing ;" % NS, "    fw:p 2 .", "fw:Other a fw:Thing .", "<%sOtherFull> a fw:Thing ." % NS, "# closing comment"]
pre = {"fw": NS}
live, arch, moved = m.split_statements(lines, {"Mine", "MineFull"}, pre, {NS + "Mine", NS + "MineFull"})
expect("both forms of the lineage's subjects move, with their continuation lines", moved == 2 and "fw:Mine a fw:Thing ;" in arch and "    fw:p 1 ." in arch and ("<%sMineFull> a fw:Thing ;" % NS) in arch and "    fw:p 2 ." in arch)
expect("statements of another lineage stay, in either form", "fw:Other a fw:Thing ." in live and ("<%sOtherFull> a fw:Thing ." % NS) in live)
expect("comments and the prefix line stay", "# a comment that stays" in live and "# closing comment" in live and lines[0] in live)
expect("nothing is lost: the live and archive lines together are the input", sorted(live + arch) == sorted(lines))
live2, arch2, moved2 = m.split_statements(lines, {"Mine", "MineFull"}, pre, set())
expect("without the full IRIs (the v2.9.0 reading) the full-IRI statement stays in the live part, so the case discriminates", moved2 == 1 and ("<%sMineFull> a fw:Thing ;" % NS) in live2)
expect("a full IRI of a namespace outside the partition is never taken by its local name", m.split_statements(["<http://other.org/x#Mine> a fw:T ."], {"Mine"}, pre, {NS + "Mine"})[2] == 0)
print("VERDICT   :", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
