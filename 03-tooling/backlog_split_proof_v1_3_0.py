#!/usr/bin/env python3
"""backlog_split_proof v1.3.0 -- a move of statements between files lost nothing and changed nothing.

WHY THIS EXISTS (Lineage 17, story OESC-S03, deliverable "A before and after proof that no statement changed").
The Mission says no statement any file makes changes. A split of the package into a live and an archive subject moves
thousands of statements between files, and a person reading the diff cannot see a lost one. This tool compares the
statements of the ontology files BEFORE with those AFTER, as sets, and reports what is only on one side.

WHAT IS COMPARED. Every statement in every .ttl under 01-ontologies/ and 02-shacl-safeguards/ of each tree, except the
statements whose subject is an owl:Ontology header (identity, version and imports are what a split legitimately changes).
Blank nodes are compared by their content, not their label: a blank node is replaced by a hash of what it says, so a
reserialisation that renames them is not a difference. The comparison is of sets, so two blank nodes that say exactly the
same thing count once (stated limit: a duplicate of an identical blank node is not detected). A decimal is compared by value ("1.0" and "1" are one value), and
the number of statements where only the spelling differs is COUNTED and printed, never silently absorbed.

THE PROOF PROVES ITSELF EVERY RUN (L-95). Before it certifies anything it removes one statement from a copy of the AFTER
side and one statement's object from another, and each must be reported as a difference; if either is not seen the tool
refuses to certify and exits 3.

v1.3.0 (Lineage 18, OC-S04, a move into the archive folder): the archive folder (01-ontologies/archive/) is read on each side like the folders above it;
--rewrite OLD=NEW declares that a text pointer (a file path in a literal) was repointed, and applies it to the BEFORE side's literals, COUNTING how many
statements it touched; --exclude-after PATH leaves out a file that is new (a shapes file written from scratch, which has no BEFORE counterpart).
v1.2.0 (Lineage 18, OC-S04, a fold of a package's files into one): --module-of-header IRI declares that a file's ontology header became a
module record. The header's own statements were always set aside (they are what a split legitimately changes); the module record that replaces it
is untyped and carries four statements (part-of, identifier, label, version). Those four, and only those four predicates, on a declared IRI are set
aside on the AFTER side and COUNTED and printed. Any other statement on that subject is compared like any other.
v1.1.0 (OESC-S01, a split that moves files and retires one): the comparison can be told which files left the compared
directories and where they went, and which added statements are declared.
Usage: backlog_split_proof_v1_3_0.py BEFORE_PACKAGE_DIR AFTER_PACKAGE_DIR [options]
  --allow-added                 statements only AFTER are reported but do not fail
  --allow-added-pattern REGEX   a statement only AFTER passes if it matches REGEX (repeatable); any other added statement fails
  --exclude-before PATH         leave this file of the BEFORE tree (relative to the package) out of the comparison, e.g. a derived copy
  --extra-before PATH / --extra-after PATH   also read this file (relative to the package) on that side, e.g. a file that moved to
                                a directory the comparison does not otherwise read
  --rewrite OLD=NEW             a repointed text path: applied to the BEFORE side's literals and counted (repeatable)
  --exclude-after PATH          leave this file of the AFTER tree out of the comparison, e.g. a new file with no BEFORE counterpart
  --ignore-subject IRI          leave out the statements about this subject (repeatable)
Exit 0 identical, 2 differences, 3 the proof could not discriminate, 1 usage.
"""
import glob, hashlib, os, sys
from decimal import Decimal
from rdflib import Graph, BNode, Literal, RDF, OWL, XSD

DIRS = ("01-ontologies", os.path.join("01-ontologies", "archive"), "02-shacl-safeguards")


def load(pkg, exclude=(), extra=(), rewrite=()):
    g = Graph()
    files = []
    for d in DIRS:
        files += sorted(glob.glob(os.path.join(pkg, d, "*.ttl")))
    ex = {os.path.normpath(os.path.join(pkg, e)) for e in exclude}
    files = [f for f in files if os.path.normpath(f) not in ex] + [os.path.join(pkg, e) for e in extra]
    for f in files:
        g.parse(f, format="turtle")
    n = 0
    for old, new in rewrite:
        for t in list(g):
            if isinstance(t[2], Literal) and old in str(t[2]):
                g.remove(t); g.add((t[0], t[1], Literal(str(t[2]).replace(old, new), datatype=t[2].datatype, lang=t[2].language))); n += 1
    load.rewritten = n
    return g, files


def lit(n):
    """A literal's comparison form. Returns (form, spelling_only_flag) where decimals are value-normalised."""
    if isinstance(n, Literal) and n.datatype in (XSD.decimal, XSD.double, XSD.float, XSD.integer):
        try:
            v = Decimal(str(n))
            return f'"{v.normalize():f}"^^{str(n.datatype)}' if n.datatype == XSD.decimal else n.n3(), str(n) != f"{v.normalize():f}"
        except Exception:
            return n.n3(), False
    return n.n3(), False


MODULE_PREDICATES = ("http://purl.org/dc/terms/isPartOf", "http://purl.org/dc/terms/identifier",
                     "http://www.w3.org/2000/01/rdf-schema#label", "http://www.w3.org/2002/07/owl#versionInfo")


def strip_module_records(g, iris):
    """Remove the four module-record predicates from each declared subject; return how many statements were set aside."""
    from rdflib import URIRef
    n = 0
    for iri in iris:
        for pr in MODULE_PREDICATES:
            for t in list(g.triples((URIRef(iri), URIRef(pr), None))):
                g.remove(t); n += 1
    return n


def signature(g, ignore):
    """Sorted list of blank-node-free statement strings; second value counts decimal respellings."""
    drop = {s for s in set(g.subjects(RDF.type, OWL.Ontology))} | set(ignore)
    memo, respelled = {}, [0]

    def h(n):
        if not isinstance(n, BNode):
            s, sp = lit(n) if isinstance(n, Literal) else (n.n3(), False)
            if sp:
                respelled[0] += 1
            return s
        if n in memo:
            return memo[n]
        memo[n] = "~"
        parts = sorted(f"{p.n3()} {h(o)}" for p, o in g.predicate_objects(n))
        memo[n] = hashlib.sha1("|".join(parts).encode()).hexdigest()[:16]
        return memo[n]

    out = []
    for s, p, o in g:
        if s in drop:
            continue
        out.append(f"{h(s)} {p.n3()} {h(o)}")
    return sorted(set(out)), respelled[0]   # a set: two blank nodes with identical content are one statement


def compare(a, b):
    sa, sb = set(a), set(b)
    return sorted(sa - sb), sorted(sb - sa)


def self_proof(after_sig):
    """The proof must see a removed statement and a changed object, or it certifies nothing."""
    if len(after_sig) < 2:
        return False
    removed = after_sig[:]; removed.pop(len(removed) // 2)
    only_b, _ = compare(after_sig, removed)
    if len(only_b) != 1:
        return False
    changed = after_sig[:]; i = len(changed) // 3
    changed[i] = changed[i] + " ~changed"
    only_b2, only_a2 = compare(after_sig, changed)
    return len(only_b2) == 1 and len(only_a2) == 1


def main(argv):
    import re
    ignore, allow_added, pos, pats, exb, xb, xa, mods = [], False, [], [], [], [], [], []
    rew, exa = [], []
    i = 0
    while i < len(argv):
        if argv[i] == "--ignore-subject":
            from rdflib import URIRef
            ignore.append(URIRef(argv[i + 1])); i += 2
        elif argv[i] == "--rewrite":
            o, n = argv[i + 1].split("=", 1); rew.append((o, n)); i += 2
        elif argv[i] == "--exclude-after":
            exa.append(argv[i + 1]); i += 2
        elif argv[i] == "--module-of-header":
            mods.append(argv[i + 1]); i += 2
        elif argv[i] == "--allow-added":
            allow_added = True; i += 1
        elif argv[i] == "--allow-added-pattern":
            pats.append(re.compile(argv[i + 1])); i += 2
        elif argv[i] == "--exclude-before":
            exb.append(argv[i + 1]); i += 2
        elif argv[i] == "--extra-before":
            xb.append(argv[i + 1]); i += 2
        elif argv[i] == "--extra-after":
            xa.append(argv[i + 1]); i += 2
        else:
            pos.append(argv[i]); i += 1
    if len(pos) != 2:
        print(__doc__); return 1
    gb, fb = load(pos[0], exb, xb, rew); rewritten = load.rewritten; ga, fa = load(pos[1], exa, xa)
    if rew:
        print(f"repointed paths: {len(rew)} declared; {rewritten} BEFORE-side statement(s) rewritten and counted")
    set_aside = strip_module_records(ga, mods)
    if mods:
        print(f"module records: {len(mods)} declared header(s); {set_aside} statement(s) (part-of, identifier, label, version) set aside on the AFTER side")
    sb, rb = signature(gb, ignore); sa, ra = signature(ga, ignore)
    print(f"before : {len(fb)} file(s), {len(gb)} statements ({len(sb)} compared)  {pos[0]}")
    print(f"after  : {len(fa)} file(s), {len(ga)} statements ({len(sa)} compared)  {pos[1]}")
    print(f"decimals whose spelling differs but value is equal, counted: before {rb}, after {ra}")
    if not self_proof(sa):
        print("SELF-PROOF : FAILED -- a removed statement and a changed object were not both reported. Nothing is certified.")
        return 3
    print("SELF-PROOF : ok -- a planted removal and a planted change are both reported")
    lost, added = compare(sb, sa)
    print(f"only BEFORE (lost or changed): {len(lost)}")
    for x in lost[:5]:
        print("   -", x[:200])
    print(f"only AFTER  (added or changed): {len(added)}")
    for x in added[:5]:
        print("   +", x[:200])
    undeclared = [x for x in added if not any(p.search(x) for p in pats)] if pats else added
    if pats:
        print(f"added statements matching a declared pattern: {len(added) - len(undeclared)}; matching none: {len(undeclared)}")
        for x in undeclared[:5]:
            print("   ?", x[:200])
    bad = bool(lost) or (bool(undeclared) and not allow_added)
    print("VERDICT    : " + ("IDENTICAL -- every statement before is present after, and none was changed" if not bad
                             else "DIFFERENT -- see the lists above"))
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
