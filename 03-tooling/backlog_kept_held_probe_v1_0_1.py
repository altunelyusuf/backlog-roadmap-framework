#!/usr/bin/env python3
"""backlog_kept_held_probe v1.0.0 -- no rule set of another profile or of a lineage closed before Lineage 29 changed (Lineage 29, story KeptHeld).
What it shows: the register's statements about the three other profiles, the rule sets they include or the eight closed lineages adopted, and those lineages themselves are as at release 4.8.0, nothing is added about them, and none of the eight was reopened.
What it does not show: that the shapes enforcing those rule sets, the tools, the stage outputs, missions, findings or other files of those lineages are unchanged, or anything about lineages that closed after 4.8.0 (Lineages 29 to 31).
The baseline (kept_held_baseline_v1_0_0.nt) is the register of release 4.8.0 reduced to those subjects, without states, lineage status and version predicates.
Judged on the newest real register: (1) every baseline statement is still there; (2) nothing was added about those subjects except the exempt predicates, so no profile other than the agentic-adaptive one gained a rule set and no closed lineage adopted one later.
Mutants (copies in memory): a rule set dropped from a profile, a changed adoption of a closed lineage, a rule set added to another profile, a definition of a kept rule set edited; and a control: an exempt state change is still allowed.
Exit 0 when every expectation holds."""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
REG = latest("01-ontologies/backlog_abox_v*.ttl"); BASE = latest("03-tooling/kept_held_baseline_v*.nt")
if sys.argv[1:] == ["--deps"]:
    print(REG); print(latest("01-ontologies/archive/backlog_framework_archive_abox_v*.ttl")); print(BASE); print(os.path.abspath(__file__)); sys.exit(0)
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import OWL
B = "http://example.org/backlog#"; U = lambda n: URIRef(B + n)
EX = {U("hasState"), U("hasLineageStatus"), U("lineageArchived"), U("archivedAt"), U("archiveFile"), U("archivalTrigger"), U("hasArchivalConfirmationStatus"), OWL.versionInfo, OWL.versionIRI, OWL.priorVersion}
base = Graph(); base.parse(BASE, format="nt"); cur = Graph(); cur.parse(REG, format="turtle"); cur.parse(latest("01-ontologies/archive/backlog_framework_archive_abox_v*.ttl"), format="turtle")
subs = set(base.subjects())
CLOSED = [x for x in subs if (x, U("adoptsRuleSet"), None) in base]
def reopened(g): return [x for x in CLOSED if g.value(x, U("hasLineageStatus")) not in (U("LS_Achieved"), U("LS_Abandoned"), U("LS_Archived"))]
def judge(g):
    """(statements of the baseline that are gone or changed, statements added about the kept subjects)"""
    gone = [t for t in base if t not in g]
    added = [(s, p, o) for s in subs for p, o in g.predicate_objects(s) if p not in EX and (s, p, o) not in base]
    return gone + reopened(g), added
bad = []
def expect(n, ok):
    print(("PASS  " if ok else "FAIL  ") + n)
    if not ok: bad.append(n)
gone, added = judge(cur)
expect("the baseline holds %d statements about %d subjects" % (len(base), len(subs)), len(base) > 300 and len(subs) >= 20)
expect("every baseline statement is still in the register (gone: %d)" % len(gone), not gone)
expect("nothing was added about the kept profiles, rule sets or closed lineages (added: %d)" % len(added), not added)
def mut(f):
    m = Graph(); m += cur; f(m); g, a = judge(m); return bool(g or a)
prof = U("Profile_Agentic"); inc = U("profileIncludes"); closed = sorted(CLOSED)
expect("mutant: a rule set dropped from another profile is seen", mut(lambda m: m.remove((prof, inc, next(m.objects(prof, inc))))))
expect("mutant: an adoption of a closed lineage changed is seen", mut(lambda m: (m.remove((closed[0], U("adoptsRuleSet"), sorted(m.objects(closed[0], U("adoptsRuleSet")))[0])), m.add((closed[0], U("adoptsRuleSet"), U("RS_ScopeItemsAnswered"))))))
expect("mutant: a rule set added to another profile is seen", mut(lambda m: m.add((prof, inc, U("RS_ScopeItemsAnswered")))))
expect("mutant: a rule set added to a closed lineage is seen", mut(lambda m: m.add((closed[0], U("adoptsRuleSet"), U("RS_ScopeItemsAnswered")))))
rsd = next(((s, p, o) for s, p, o in sorted(base) if str(s).rsplit("#", 1)[-1].startswith("RS_") and isinstance(o, Literal)), None)
expect("a kept rule set with a text statement is in the baseline", rsd is not None)
expect("mutant: a kept rule set with a statement edited is seen", mut(lambda m: (m.remove(rsd), m.add((rsd[0], rsd[1], Literal("edited"))))))
rsv = next(((s, p, o) for s, p, o in sorted(base) if str(s).endswith("RS_IndependentVerification") and isinstance(o, Literal)), None)
expect("a rule set adopted only by closed lineages is in the baseline", rsv is not None)
expect("mutant: its statement edited is seen", mut(lambda m: (m.remove(rsv), m.add((rsv[0], rsv[1], Literal("edited"))))))
expect("mutant: a closed lineage reopened by its status alone is seen", mut(lambda m: m.set((closed[0], U("hasLineageStatus"), U("LS_InProgress")))))
expect("control: archiving a closed lineage is allowed", not mut(lambda m: (m.set((closed[0], U("hasLineageStatus"), U("LS_Archived"))), m.set((closed[0], U("lineageArchived"), Literal(True))))))
expect("control: a state change of a closed lineage is allowed", not mut(lambda m: m.add((closed[0], U("hasState"), U("Archived")))))
print("VERDICT   :", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
