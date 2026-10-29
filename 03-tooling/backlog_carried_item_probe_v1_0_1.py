#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe reads no record of the framework register; the validator keeps only the controlled individuals)
"""backlog_carried_item_probe v1.0.0 -- a carried item through a revision, and through a chain of successors (shapes v1.172.0, G129).

Built from the shipped succession fixture, one planted register per case, a carried story set InProgress:
  1 the admitting output is active: the story owes no planning event and no concern declaration (the pre-lineage exemption);
  2 the admitting output is retracted and the lineage holds no active Backlog output yet (a revision under way): the exemption still holds (G129);
  3 the lineage now holds an active Backlog output that does not re-admit the story: the exemption lapses and both are owed again;
  4 the active output re-admits it: silent again;
  5 a later successor in the chain takes the story in: neither the admission rule nor the carried-item rule refuses it (G129);
  6 an output of a lineage that is not in the chain refuses it on both.
Exit 0 when every expectation holds, 1 otherwise."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    for pat in ("03-tooling/backlog_validate_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl", "01-ontologies/backlog_abox_v*.ttl", "03-tooling/fixtures/fixture_lineage_succession_v*.ttl"):
        print(latest(pat))
    print(os.path.abspath(__file__)); sys.exit(0)
VAL = latest("03-tooling/backlog_validate_v*.py"); FIX = latest("03-tooling/fixtures/fixture_lineage_succession_v*.ttl")
base = open(FIX, encoding="utf-8").read()
CARRIED = "backlog:preLineageItem true ; backlog:admittedByOutput ex:Out_Backlog ."
assert CARRIED in base and "backlog:hasIdentifier \"S-CARRIED\" ; backlog:hasState backlog:Proposed" in base
inprog = base.replace('backlog:hasIdentifier "S-CARRIED" ; backlog:hasState backlog:Proposed', 'backlog:hasIdentifier "S-CARRIED" ; backlog:hasState backlog:InProgress')
OUT = lambda n, lin: ('\nex:%s a backlog:StageOutput ; backlog:outputOfStage backlog:Stage_Backlog ; backlog:belongsToLineage ex:%s ;\n'
                      '    backlog:hasStateDigest "00" ; backlog:consumesOutput ex:Out_Objective ; backlog:closedAtCommit "fixture-only-%s" .\n' % (n, lin, n))
LIN = lambda n, k: '\nex:%s a backlog:Lineage ; backlog:lineageArchived false ; backlog:lineageForMission ex:M ; backlog:lineageOrdinal %d .\n' % (n, k)
SUCC = ('\nex:Gap_PL a backlog:PartialScopeDeclaration ; backlog:declaresGapFor ex:Lin_PL ; backlog:decidedBy backlog:Owner ; backlog:describesUncoveredScope "Remainder." .\n'
        'ex:Succ_2 a backlog:LineageSuccession ; backlog:succeedsLineage ex:Lin_PL ; backlog:successorLineage ex:Lin_Third ; backlog:resolvesGap ex:Gap_PL ;\n'
        '    backlog:successionRationale "The second lineage closed; the third continues." ; backlog:decidedBy backlog:Owner .\n')
RET = "\nex:Out_Backlog backlog:outputRetracted true .\n"
MSG = {"planning": "no PlanningEvent ever took it", "concern": "declares neither an applicable design concern", "admission": "claims admission by an output",
       "carried": "succession wound down, is still open"}


def verdicts(text):
    with tempfile.NamedTemporaryFile("w", suffix=".ttl", delete=False) as f:
        f.write(text)
    out = subprocess.run([sys.executable, VAL, f.name], capture_output=True, text=True).stdout
    os.unlink(f.name)
    lines = [l for l in out.splitlines() if "S_Carried" in l]
    return {k: any(m in l for l in lines) for k, m in MSG.items()}


bad = []
def expect(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok:
        bad.append(name)


c1 = verdicts(inprog)
expect("1 active admission: no planning event and no concern declaration owed", not c1["planning"] and not c1["concern"])
c2 = verdicts(inprog + RET)
expect("2 admitting output retracted, no active Backlog output yet (revision under way): still not owed", not c2["planning"] and not c2["concern"])
c3 = verdicts(inprog + RET + OUT("Out_Backlog_R", "Lin_PL"))
expect("3 an active Backlog output that does not re-admit the story: both owed again", c3["planning"] and c3["concern"])
c4 = verdicts(inprog.replace(CARRIED, "backlog:preLineageItem true ; backlog:admittedByOutput ex:Out_Backlog_R .") + RET + OUT("Out_Backlog_R", "Lin_PL"))
expect("4 the active output re-admits it: not owed", not c4["planning"] and not c4["concern"])
chain = inprog.replace(CARRIED, "backlog:preLineageItem true ; backlog:admittedByOutput ex:Out_Backlog3 .") + LIN("Lin_Third", 3) + OUT("Out_Backlog3", "Lin_Third") + SUCC
c5 = verdicts(chain)
expect("5 taken in by the next successor's output down the chain: neither rule refuses it", not c5["admission"] and not c5["carried"])
other = inprog.replace(CARRIED, "backlog:preLineageItem true ; backlog:admittedByOutput ex:Out_BacklogO .") + LIN("Lin_Other", 3) + OUT("Out_BacklogO", "Lin_Other")
c6 = verdicts(other)
expect("6 an output of a lineage outside the chain is refused by the admission rule", c6["admission"])
nochain = inprog.replace(CARRIED, "backlog:preLineageItem true ; backlog:admittedByOutput ex:Out_Backlog3 .") + LIN("Lin_Third", 3) + OUT("Out_Backlog3", "Lin_Third")
c7 = verdicts(nochain)
expect("7 the same third lineage without a succession from the second is refused: the chain is what allows it", c7["admission"])
print("VERDICT: %s" % ("PASS -- %d expectations hold" % 7 if not bad else "FAIL -- " + "; ".join(bad)))
sys.exit(1 if bad else 0)
