#!/usr/bin/env python3
"""backlog_archive_conformance v1.3.0 -- progressive archive conformance.

THE OWNER'S DESIGN, test-driven before adoption (G46). The settled archive is never re-validated:
its conformance is a RECORDED VALUE, confirmed by comparing a canonical digest. Only lineages that
have ARRIVED since the value was recorded are validated, and they are validated in the FULL archive
context -- pyshacl's focus_nodes scopes the report without shrinking the graph -- so nothing is
judged out of the context its statements resolve against. On success the value advances.

Measured on this package's archive (13 lineages, 11,763 triples), 2026-09-10:

    value check (canonical digest)                   0.09 s
    focused validation of one arriving lineage       3.9  s
    ----------------------------------------------------------
    progressive total                              ~ 4    s
    whole-archive re-validation                    162.3  s
    per-lineage SLICING (a wrong first test drive) 247.7  s, 994 artefact violations

The slicing figure is kept here deliberately: cutting a lineage out of the archive loses the mission
it superseded, the register root it belonged to and the deliverables its epics satisfied, so every
fragment reports violations that are artefacts of the cut. A refuted design should be refuted with
its numbers, not merely dropped.

  backlog_archive_conformance_v1_0_0.py            confirm the recorded value, validate arrivals
  backlog_archive_conformance_v1_0_0.py --emit     print the ArchiveConformanceRecord to record

Exit 0 conformant (value confirmed, arrivals clean); 2 a violation or a changed archive; 1 on error.
"""
import glob, hashlib, os, re, sys, time
from rdflib import Graph, Namespace, RDF, URIRef
import pyshacl

B = Namespace("http://example.org/backlog#")
SH = Namespace("http://www.w3.org/ns/shacl#")
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
def loc(x): return str(x).split("#")[-1]
def sv(p): return [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
def latest(sub, pat): return sorted(glob.glob(os.path.join(PKG, sub, pat)), key=sv)[-1]


def canonical_digest(g):
    """SHA-256 over canonical N-Triples: re-serialization, comments and statement order cannot move
    it; only a change in what the archive SAYS can."""
    return hashlib.sha256("\n".join(sorted(g.serialize(format="nt").splitlines())).encode()).hexdigest()


def main():
    emit = "--emit" in sys.argv
    seed = "--seed" in sys.argv
    reg_f = latest("01-ontologies", "backlog_framework_register_abox_v*.ttl")
    arc_f = latest("01-ontologies", "backlog_framework_archive_abox_v*.ttl")
    sh_f = latest("02-shacl-safeguards", "backlog_shacl_v*.ttl")
    ru_f = latest("02-shacl-safeguards", "backlog_rules_v*.ttl")
    tb_f = latest("01-ontologies", "backlog_tbox_v*.ttl")
    ab_f = latest("01-ontologies", "backlog_abox_v*.ttl")
    g, a = Graph().parse(reg_f), Graph().parse(arc_f)
    print(f"archive     : {os.path.basename(arc_f)} ({len(a)} triples)")

    rel = os.path.relpath(arc_f, PKG)
    rec = next((r for r in g.subjects(RDF.type, B.ArchiveConformanceRecord)
                if str(g.value(r, B.recordForArchiveFile)) == rel), None)
    t0 = time.time(); dig = canonical_digest(a); t_dig = time.time() - t0
    cleared = set()
    if rec is None:
        print(f"  value       : no ArchiveConformanceRecord for {rel} -- every lineage in it is an arrival")
    else:
        old = str(g.value(rec, B.hasArchiveDigest) or "")
        cleared = {str(x) for x in g.objects(rec, B.includesRetiredLineage)}
        if old == dig:
            print(f"  value       : CONFIRMED in {t_dig:.2f}s -- digest {dig[:16]} unchanged since "
                  f"{g.value(rec, B.clearedAt)} under {g.value(rec, B.clearedUnderShapes)}; "
                  f"{len(cleared)} lineage(s) already cleared, not re-validated")
        else:
            print(f"  value       : CHANGED -- recorded {old[:16]}, computed {dig[:16]}. The settled archive "
                  f"is not supposed to change; either a retirement rewrote it (then re-record) or "
                  f"something edited history (then investigate).")
            cleared = set()   # trust nothing: validate every lineage as an arrival

    if seed:
        # SEEDING, once. Lineages retired before this mechanism existed cannot honestly be validated
        # now: measured 2026-09-10, doing so reports 193 violations, and they come from shapes shipped
        # AFTER those lineages closed -- GoalTriangleShape arrived from SCAMPS on 2026-09-10 and fires
        # on chains gated clean days earlier. Judging them under today's rules is exactly the
        # retroactive enforcement this framework refuses (G89, G91). Their conformance is established
        # by the RELEASE RECORD: each was gated clean, under the shapes of its own day, in the release
        # that closed it. --seed records that value and names its ground; every lineage that arrives
        # afterwards is validated for real, under the shapes in force when it retires.
        cleared = {str(L) for L in a.subjects(RDF.type, B.Lineage)}
        print(f"  seeding     : {len(cleared)} lineage(s) cleared by the release record, not by re-validation "
              f"(each was gated clean in the release that closed it; judging them under today's shapes "
              f"would be retroactive -- G91)")
    # Per-lineage confirmation, wired in for real, 2026-09-18 (G98 follow-up): a lineage already
    # AC_Confirmed was checked, once, against the shapes current at that moment, and found to
    # hold its own era's standards -- re-validating it here on every later digest change is the
    # exact retroactive-enforcement mistake this whole mechanism exists to prevent. Excluded from
    # arrivals regardless of the whole-file digest, which was always the coarser, wrong unit.
    confirmed = {str(L) for L in a.subjects(RDF.type, B.Lineage)
                 if a.value(L, B.hasArchivalConfirmationStatus) == B.AC_Confirmed}
    arrivals = [L for L in a.subjects(RDF.type, B.Lineage) if str(L) not in cleared and str(L) not in confirmed]
    print(f"  arrivals    : {len(arrivals)} lineage(s) to validate " +
          (f"({', '.join(sorted(loc(L) for L in arrivals)[:6])}{'...' if len(arrivals) > 6 else ''})" if arrivals else "-- none"))
    bad = 0
    if arrivals:
        tb, ab = Graph().parse(tb_f), Graph().parse(ab_f)
        # Real root cause, found 2026-09-18: harnessComplete and every other SHACL-AF-derived
        # property live in a SEPARATE rules file (backlog_rules), never loaded here before --
        # backlog_validate correctly combines shapes+rules as the one graph passed to pyshacl;
        # this tool only ever loaded the shapes half, so every derived property silently never
        # computed, and every check depending on one fired as if it were simply absent. Confirmed
        # directly: content that validates clean through backlog_validate was failing here on
        # exactly this class of check (G98's own finding, now root-caused rather than left as
        # "unresolved, downgraded to advisory").
        shg = Graph().parse(sh_f); shg.parse(ru_f)
        focus = set()
        for L in arrivals:
            items = {s for s in a.subjects(B.belongsToLineage, L)}
            focus |= items | {L}
            m = a.value(L, B.lineageForMission)
            if m is not None: focus.add(m)
            # Real root cause, found 2026-09-18: focus_nodes was believed (per this tool's own
            # earlier docstring claim) to scope only the REPORT, not rule execution -- verified
            # false by direct test: a Done item's own harnessComplete rule never fired when its
            # TestHarness (which never carries belongsToLineage) sat outside focus, even though
            # the harness was present in the full data graph passed to pyshacl. Widened one real
            # hop to the harness and its own evidence, the actual rule-dependency chain a Done
            # item's derived properties depend on -- not a blanket widening, which would lose the
            # real performance benefit this scoping exists for.
            for item in items:
                for h in a.subjects(B.harnessFor, item):
                    focus.add(h)
                    for ev in a.objects(h, B.hasHarnessEvidence):
                        focus.add(ev)
                for ev in a.objects(item, B.hasEvidence):
                    focus.add(ev)
        t0 = time.time()
        # FULL context means the live register too: retired items still reference the register ROOT,
        # which never leaves the live file (G92). Validating archive+TBox alone reported 397
        # violations that were all "not a member of a Backlog register" -- artefacts of the missing
        # root, the same class of error as the slicing test drive, one level up.
        _, rg, _ = pyshacl.validate(a + g + tb + ab, shacl_graph=shg, advanced=True, inference="none",
                                    focus_nodes=[str(f) for f in focus])
        t_val = time.time() - t0
        viol = [r for r in rg.subjects(RDF.type, SH.ValidationResult) if rg.value(r, SH.resultSeverity) == SH.Violation]
        print(f"  validated   : {len(focus)} focus node(s) in the FULL archive context in {t_val:.1f}s -- "
              f"{len(viol)} violation(s)")
        for r in viol[:8]:
            print(f"     {loc(rg.value(r, SH.focusNode))}: {str(rg.value(r, SH.resultMessage))[:90]}")
        bad = len(viol)

    if emit:
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        allo = sorted(str(L) for L in a.subjects(RDF.type, B.Lineage))
        print("\n# --- record this in the register (the value now covers every lineage in the archive) ---")
        print(f'''fw:ArchiveConformance_{re.sub(r"[^0-9]", "", os.path.basename(arc_f))} a backlog:ArchiveConformanceRecord ;
    backlog:recordForArchiveFile "{rel}" ;
    backlog:hasArchiveDigest "{dig}" ;
    backlog:clearedUnderShapes "{os.path.basename(sh_f) if not seed else 'seeded from the release record; each lineage was gated under the shapes of its own day'}" ;
    backlog:clearedAt "{now}"^^xsd:dateTime ;''')
        print("    backlog:includesRetiredLineage " + " ,\n        ".join(f'"{x}"' for x in allo) + " .")

    print("VERDICT     : " + ("CONFORMANT — the settled archive is unchanged and every arrival validates"
                              if bad == 0 else f"VIOLATION — {bad} on arriving lineage(s); they do not join the value"))
    return 0 if bad == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
