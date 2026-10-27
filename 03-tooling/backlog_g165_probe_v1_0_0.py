#!/usr/bin/env python3
"""backlog_g165_probe v1.0.0 -- re-runnable proof that the lessons are recorded as experience (G165).

  Every safeguard in the shapes is either the enforcer a governance ruling names or the subject of a lesson record that states, in the words of the experience, what went wrong in practice.
  Checks the shipped files, then plants a bare lesson and expects the validator to refuse it. Exit 0 when every expectation holds."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
TB, AB, SH, VAL = (latest("01-ontologies/backlog_tbox_v*.ttl"), latest("01-ontologies/backlog_abox_v*.ttl"), latest("02-shacl-safeguards/backlog_shacl_v*.ttl"), latest("03-tooling/backlog_validate_v*.py"))
if sys.argv[1:] == ["--deps"]:
    print("\n".join([TB, AB, SH, VAL, os.path.abspath(__file__)])); sys.exit(0)
from rdflib import Graph, Namespace, RDF
B = Namespace("http://example.org/backlog#"); SHN = Namespace("http://www.w3.org/ns/shacl#")
bad = []
def expect(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (" (%s)" % detail if detail else ""))
    if not ok: bad.append(name)
g = Graph(); g.parse(AB, format="turtle"); s = Graph(); s.parse(SH, format="turtle")
shapes = {x for x in s.subjects(RDF.type, SHN.NodeShape)} | {x for x in s.subjects(RDF.type, SHN.PropertyShape)}
enforced = {o for r in g.subjects(RDF.type, B.GovernanceRuling) for o in g.objects(r, B.enforcedByShape)}
lessons = list(g.subjects(RDF.type, B.ShapeLesson)); lesson_of = {g.value(l, B.lessonOfShape) for l in lessons}
expect("every safeguard is covered, by a ruling that names it or by a lesson record", not (shapes - enforced - lesson_of), "%d uncovered" % len(shapes - enforced - lesson_of))
expect("no safeguard is covered both ways, so the two routes stay distinct", not (enforced & lesson_of), "%d both" % len(enforced & lesson_of))
expect("every lesson names a safeguard that exists", lesson_of <= shapes, "%d unknown" % len(lesson_of - shapes))
expect("the nine families are all used", len({g.value(l, B.inLessonFamily) for l in lessons}) == 9)
expect("each lesson is complete: statement, family, segment, profile scope, confidence", all(all(g.value(l, p) is not None for p in (B.hasExperienceStatement, B.inLessonFamily, B.learnedInSegment, B.hasProfileScope, B.hasLessonConfidence)) for l in lessons), "%d lessons" % len(lessons))
expect("no lesson statement just repeats the safeguard's name", all(str(g.value(l, B.lessonOfShape)).split("#")[-1] not in str(g.value(l, B.hasExperienceStatement)) for l in lessons))
H = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/g165#> .\n"
with tempfile.TemporaryDirectory() as d:
    f = os.path.join(d, "s.ttl"); open(f, "w").write(H + "x:L a backlog:ShapeLesson .\n")
    out = subprocess.run([sys.executable, VAL, f], capture_output=True, text=True, timeout=900).stdout
    for m in ("name the one safeguard", "state the experience", "one lesson family", "where in the lineage", "which profiles", "how sure"):
        expect("a bare lesson is refused: " + m, any("[Violation]" in ln and m in ln for ln in out.splitlines()))
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
