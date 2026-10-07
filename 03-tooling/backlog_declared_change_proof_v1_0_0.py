#!/usr/bin/env python3
"""backlog_declared_change_proof v1.0.0 -- a release changed exactly what it declared, and nothing else (Lineage 19, DC-S07).

WHY THIS EXISTS. backlog_split_proof answers "is every statement still there?" and can only say "identical" or "different". A lineage that repairs rules,
marks records and adds its own records legitimately differs; "different" then proves nothing. This tool reads the same statements (it imports the split
proof's own loader and signature, so a statement means the same thing in both) and sorts every difference into a DECLARED category. A difference that
fits none is printed and fails the proof. Nothing is hidden: every category prints how many statements it accounts for.

WHAT IS DECLARED (the table below is the whole list; to declare more, change this file and its version):
  LOST (present before, absent after):
    - the two shapes this lineage reworded (MissionClosureRequiresReportShape, ArchivedLineageMarkedShape) and what hangs from them;
    - an archived lineage's "not archived" marker and its "pending" status, which the repaired confirmation step set to archived / confirmed.
    - (text pointers to the archive data file and to the archive shapes check are repointed on the BEFORE side with --rewrite and COUNTED, as in the split proof.)
  ADDED (absent before, present after):
    - the records of this lineage and of its finding and reports (subject names below);
    - the new vocabulary and the new shapes (subject names below) and what hangs from them;
    - the three statements this lineage made new: reportsDeliveredItem, reportsCancelledItem, moduleAudience, wherever they occur;
    - the marker and the confirmation status on an archived lineage record, and its Aud_ individuals.
  A statement hanging from a declared subject through blank nodes (a SPARQL constraint, a list) is declared with it.

Exit 0 every difference is declared; 2 some difference is not; 3 the proof could not discriminate (a planted undeclared change was not reported).
Usage: backlog_declared_change_proof_v1_0_0.py BEFORE_PACKAGE_DIR AFTER_PACKAGE_DIR [--rewrite OLD=NEW ...] [--show-all]
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("split_proof", os.path.join(HERE, "backlog_split_proof_v1_4_0.py"))
SP = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(SP)

B = "<http://example.org/backlog#"
LOST_SUBJECTS = [B + "MissionClosureRequiresReportShape>", B + "ArchivedLineageMarkedShape>"]
ADDED_SUBJECT_PATTERNS = [
    r"^<[^>]*#[A-Za-z_]*_DC_\w+>", r"^<[^>]*#(DCC\d+|DoD_DC)>", r"^<[^>]*#\w*_?RecordsTellTruth>", r"^<[^>]*#Find_ObjectiveOnExternalRegister>",
    r"^<[^>]*#CR_(OEStructureCleanup|BuildSoftware)>",
    r"^<[^>]*#(Aud_Public|Aud_Private|ModuleAudience)>",
    r"^<[^>]*backlog#(ClosureReportNamesCancelledShape|ModuleAudienceDeclaredShape|ArchivedMissionReportedShape|ArchivedCancellationReportedShape|ArchivedModuleAudienceShape|ArchivedLineageMarkedShape|MissionClosureRequiresReportShape)>",
    r"^<[^>]*backlog#(reportsDeliveredItem|reportsCancelledItem|moduleAudience)>",
]
ADDED_PREDICATES = [B + "reportsDeliveredItem>", B + "reportsCancelledItem>", B + "moduleAudience>"]
MARKER_PREDICATES = [B + "lineageArchived>", B + "hasArchivalConfirmationStatus>"]
LOST_MARKER_VALUES = ("\"false\"^^<http://www.w3.org/2001/XMLSchema#boolean>", B + "AC_PendingConfirmation>")
HEX = re.compile(r"^[0-9a-f]{16}$")


def parts(line):
    s, p, o = line.split(" ", 2)
    return s, p, o


def closure(lines, roots):
    """Lines declared by hanging from a root: the root's own lines, then blank-node subjects reached from declared lines."""
    declared, frontier = set(), set()
    for ln in lines:
        s, p, o = parts(ln)
        if roots(s, p, o):
            declared.add(ln)
            if HEX.match(o):
                frontier.add(o)
    while frontier:
        nxt = set()
        for ln in lines:
            s, p, o = parts(ln)
            if s in frontier and ln not in declared:
                declared.add(ln)
                if HEX.match(o):
                    nxt.add(o)
        frontier = nxt
    return declared


def classify(lost, added):
    lost_dec = closure(lost, lambda s, p, o: s in LOST_SUBJECTS or o.rstrip() in LOST_SUBJECTS or
                       (p in MARKER_PREDICATES and o in LOST_MARKER_VALUES))
    lost_cat = {"reworded or hardened shapes": 0, "archive marker / confirmation status": 0}
    for ln in lost_dec:
        s, p, o = parts(ln)
        lost_cat["archive marker / confirmation status" if p in MARKER_PREDICATES and o in LOST_MARKER_VALUES else "reworded or hardened shapes"] += 1

    def root(s, p, o):
        return (any(re.search(r, s) for r in ADDED_SUBJECT_PATTERNS) or p in ADDED_PREDICATES or p in MARKER_PREDICATES
                or (o.startswith("<") and any(re.search(r, o) for r in (ADDED_SUBJECT_PATTERNS[5], ADDED_SUBJECT_PATTERNS[6]))))
    added_dec = closure(added, root)
    cats = {"records of the lineage, its finding and its reports": 0, "new vocabulary and shapes": 0,
            "reportsDeliveredItem / reportsCancelledItem / moduleAudience": 0, "archive marker / confirmation status": 0,
            "hanging from a declared shape or list": 0}
    for ln in added_dec:
        s, p, o = parts(ln)
        if p in ADDED_PREDICATES:
            cats["reportsDeliveredItem / reportsCancelledItem / moduleAudience"] += 1
        elif p in MARKER_PREDICATES:
            cats["archive marker / confirmation status"] += 1
        elif any(re.search(r, s) for r in ADDED_SUBJECT_PATTERNS[:5]):
            cats["records of the lineage, its finding and its reports"] += 1
        elif any(re.search(r, s) for r in ADDED_SUBJECT_PATTERNS[5:]):
            cats["new vocabulary and shapes"] += 1
        else:
            cats["hanging from a declared shape or list"] += 1
    return lost_dec, lost_cat, added_dec, cats


def main(argv):
    show_all = "--show-all" in argv
    rew, pos, i = [], [], 0
    while i < len(argv):
        if argv[i] == "--rewrite":
            o, n = argv[i + 1].split("=", 1); rew.append((o, n)); i += 2
        elif argv[i] == "--show-all":
            i += 1
        else:
            pos.append(argv[i]); i += 1
    if len(pos) != 2:
        print(__doc__); return 1
    gb, fb = SP.load(pos[0], (), (), rew); rewritten = SP.load.rewritten
    ga, fa = SP.load(pos[1])
    sb, _ = SP.signature(gb, []); sa, _ = SP.signature(ga, [])
    print(f"before : {len(fb)} file(s), {len(sb)} statements compared  {pos[0]}")
    print(f"after  : {len(fa)} file(s), {len(sa)} statements compared  {pos[1]}")
    if rew:
        print(f"repointed paths: {len(rew)} declared; {rewritten} BEFORE-side statement(s) rewritten and counted")
    lost, added = SP.compare(sb, sa)
    # self-proof: a planted undeclared statement on each side must come out undeclared
    pl = "<http://example.org/x#Planted> <http://example.org/x#p> \"undeclared\""
    ld, _, ad, _ = classify(lost + [pl], added + [pl])
    if pl in ld or pl in ad:
        print("SELF-PROOF : FAILED -- a planted undeclared statement was accepted. Nothing is certified."); return 3
    print("SELF-PROOF : ok -- a planted undeclared statement is refused on each side")
    lost_dec, lost_cat, added_dec, cats = classify(lost, added)
    lost_un = [x for x in lost if x not in lost_dec]; added_un = [x for x in added if x not in added_dec]
    print(f"only BEFORE: {len(lost)}  declared {len(lost_dec)}  undeclared {len(lost_un)}")
    for k, v in lost_cat.items():
        print(f"   declared: {k}: {v}")
    print(f"only AFTER : {len(added)}  declared {len(added_dec)}  undeclared {len(added_un)}")
    for k, v in cats.items():
        print(f"   declared: {k}: {v}")
    for x in (lost_un if show_all else lost_un[:8]):
        print("   - UNDECLARED", x[:200])
    for x in (added_un if show_all else added_un[:8]):
        print("   + UNDECLARED", x[:200])
    ok = not lost_un and not added_un
    print("VERDICT : " + ("DECLARED -- every difference is one this lineage declared, and none other" if ok
                          else "UNDECLARED DIFFERENCES -- see above"))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
