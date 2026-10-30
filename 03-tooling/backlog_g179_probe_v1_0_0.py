#!/usr/bin/env python3
"""backlog_g179_probe v1.0.0 -- re-runnable proof of the adaptive profile's revision 9 (G179, Lineage 22, box 2).

  Checks the shipped file (revision 9 adds RS_StateReflectsEvidence to the adaptive profile and nothing else; the standard and agentic profiles are as they were; the ruling decides the
  revision and every rule set outside the profile and names an enforcing shape), then opens a lineage with the opening tool under the adaptive profile and shows the block adopts
  the rule set, and shows the validator refusing a work item that is still Proposed and carries verified evidence in a lineage opened with the revised block, and not refusing it in
  a lineage opened with the block of revision 8. Exit 0 when every expectation holds."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
AB, VAL, OPEN = latest("01-ontologies/backlog_abox_v*.ttl"), latest("03-tooling/backlog_validate_v*.py"), latest("03-tooling/backlog_open_lineage_v*.py")
if sys.argv[1:] == ["--deps"]:
    print("\n".join([AB, VAL, OPEN, latest("02-shacl-safeguards/backlog_shacl_v*.ttl"), latest("01-ontologies/backlog_tbox_v*.ttl"), os.path.abspath(__file__)])); sys.exit(0)
from rdflib import Graph, Namespace
B = Namespace("http://example.org/backlog#")
bad = []
def expect(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (" (%s)" % detail if detail else ""))
    if not ok: bad.append(name)
g = Graph(); g.parse(AB, format="turtle")
inc = lambda p: set(g.objects(p, B.profileIncludes))
expect("the standard and agentic profiles are as they were (nine and ten)", len(inc(B.Profile_Standard)) == 9 and len(inc(B.Profile_Agentic)) == 10 and B.RS_StateReflectsEvidence not in inc(B.Profile_Standard) | inc(B.Profile_Agentic))
expect("the adaptive profile includes the rule set, introduced in profile revision 9", B.RS_StateReflectsEvidence in inc(B.Profile_Adaptive) and g.value(B.RS_StateReflectsEvidence, B.introducedInRevision) == B.Pr_9 and int(g.value(B.Pr_9, B.revisionNumber)) == 9)
rs = {s for s in g.subjects(__import__("rdflib").RDF.type, B.RuleSet) if "DigestTable" not in str(s)}
allin = inc(B.Profile_Standard) | inc(B.Profile_Agentic) | inc(B.Profile_Adaptive)
rul = [r for r in g.subjects(B.hasRulingIdentifier, None) if str(g.value(r, B.hasRulingIdentifier)) == "G179"]
dec = set(g.objects(rul[0], B.rulingDecides)) if rul else set()
expect("ruling G179 exists, decides revision 9 and names an enforcing shape", len(rul) == 1 and B.Pr_9 in dec and len(set(g.objects(rul[0], B.enforcedByShape))) >= 1)
expect("every rule set no profile included before revision 9 has a recorded decision in the ruling", {x for x in rs if x not in allin - {B.RS_StateReflectsEvidence}} <= dec | {B.RS_StateReflectsEvidence} , "%d rule sets, %d decided" % (len(rs), len(dec)))
run = lambda *a: subprocess.run([sys.executable, OPEN, *a], capture_output=True, text=True)
blk = run("--profile", "Profile_Adaptive", "--lineage", "L", "--prefix", "x").stdout
expect("the opening block of the adaptive profile adopts the rule set and records revision 9", "RS_StateReflectsEvidence" in blk and "Pr_9" in blk)
old = re.sub(r"\s*,?\s*backlog:RS_StateReflectsEvidence\s*,?", lambda m: " , " if m.group(0).strip().startswith(",") and m.group(0).strip().endswith(",") else " ", blk)
HEAD = "@prefix backlog: <http://example.org/backlog#> .\n@prefix x: <http://example.org/g179#> .\nx:L a backlog:Lineage .\n"
PLANT = "x:S a backlog:Task ; backlog:belongsToLineage x:L ; backlog:hasState backlog:Proposed ; backlog:hasEvidence x:E .\nx:E a backlog:ArtifactEvidence ; backlog:evidenceVerified true .\n"
def refused(block, body):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "s.ttl"); open(f, "w").write(HEAD + block + body)
        out = subprocess.run([sys.executable, VAL, f], capture_output=True, text=True, timeout=900).stdout
    return any("[Violation]" in ln and "carries evidence the bridge verified" in ln for ln in out.splitlines())
expect("a Proposed item with verified evidence is refused in a lineage opened with the revised block", refused(blk, PLANT))
expect("the same item is not refused in a lineage opened with the block of revision 8", "RS_StateReflectsEvidence" not in old and not refused(old, PLANT))
expect("a started item with verified evidence is not refused in the revised block", not refused(blk, PLANT.replace("Proposed", "InProgress")))
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
