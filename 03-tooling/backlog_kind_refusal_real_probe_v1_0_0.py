#!/usr/bin/env python3
# register-use: reads the newest register (a copy of it; the register itself is not changed)
"""backlog_kind_refusal_real_probe v1.0.0 -- the refusal of an obstacle with no kind fires on the REAL register (Lineage 29, story RuleFires).

The probe of the kinds (backlog_impediment_kind_probe) judges a scratch register. This one takes a copy of the newest real register, whose Lineage 29 adopts the rule set of known
obstacles (by its stage revision), adds one obstacle to that real lineage and judges the copy with the real validator and the real shapes:
  1  the real register itself raises no kind refusal                              (control)
  2  an obstacle of Lineage 29 with no kind is refused by name                     (the rule fires on real data)
  3  the same obstacle with a kind is not refused                                  (control)
  4  an obstacle with no kind in a lineage that did not adopt the rule set is not refused (the rule binds only adopters; the lineage tried is the one the register names first among those that do not)
The validation is restricted to the shapes that carry the refusal's text (validator 1.19.0), so each run takes seconds. Exit 0 when all hold, 1 otherwise."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
VAL, REG = latest("03-tooling/backlog_validate_v*.py"), latest("01-ontologies/backlog_abox_v*.ttl")
if sys.argv[1:] == ["--deps"]:
    for pat in ("03-tooling/backlog_validate_v*.py", "01-ontologies/backlog_abox_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl", "02-shacl-safeguards/backlog_shacl_v*.ttl"): print(latest(pat))
    print(os.path.abspath(__file__)); sys.exit(0)
KEY = "IK_NOKIND"
text = open(REG, encoding="utf-8").read()
def judge(extra):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, os.path.basename(REG)); open(f, "w", encoding="utf-8").write(text + "\n" + extra)
        env = dict(os.environ, BACKLOG_VALIDATE_ONLY_MESSAGE=KEY); env.pop("BACKLOG_VALIDATE_MEMO_DIR", None)
        out = subprocess.run([sys.executable, VAL, f], capture_output=True, text=True, timeout=900, env=env).stdout
    return [l for l in out.splitlines() if "[Violation]" in l and KEY in l]
IMP = lambda name, lin, kind: ("fw:%s a backlog:Impediment ; backlog:belongsToLineage fw:%s ; backlog:impedes fw:ST_IK_LiveProof ; backlog:hasImpedimentStatement \"A planted obstacle of the probe.\" ; "
                               "backlog:raisedAt \"2026-11-04T10:00:00Z\"^^xsd:dateTime ; backlog:hasImpedimentOwner backlog:Owner%s .\n" % (name, lin, (" ; backlog:hasImpedimentKind backlog:%s" % kind) if kind else ""))
bad = []
def expect(n, ok):
    print(("PASS  " if ok else "FAIL  ") + n)
    if not ok: bad.append(n)
expect("1 the real register raises no kind refusal", judge("") == [])
r2 = judge(IMP("PlantedNoKind", "L_ImpedimentsKnown", None))
expect("2 an obstacle of Lineage 29 with no kind is refused by name", len(r2) == 1 and "PlantedNoKind" in r2[0])
expect("3 the same obstacle with a kind is not refused", judge(IMP("PlantedKind", "L_ImpedimentsKnown", "Imp_ToolFault")) == [])
# a lineage of the register that did not adopt the rule set: the first lineage whose statement lacks RS_ImpedimentsKnown
lins = re.findall(r"^fw:(L_\w+) a backlog:Lineage", text, re.M)
non = []
for l in lins:
    m = re.search(r"^fw:%s a backlog:Lineage.*?(?=^fw:L_\w+ a backlog:Lineage|\Z)" % l, text, re.M | re.S)
    blk = m.group(0)[:6000] if m else ""
    if "RS_ImpedimentsKnown" not in blk and l != "L_ImpedimentsKnown": non.append(l)
    if non: break
if non:
    expect("4 an obstacle with no kind in a lineage that did not adopt the rule set (%s) is not refused" % non[0], judge(IMP("PlantedOutside", non[0], None)) == [])
else:
    expect("4 a lineage that did not adopt exists in the register", False)
print("register:", os.path.basename(REG)); print("VERDICT   :", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
