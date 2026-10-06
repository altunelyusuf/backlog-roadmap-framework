#!/usr/bin/env python3
"""backlog_subject_split v1.0.0 -- the one-time move of this package's live subject into one vocabulary, one data and one rules file.

WHY THIS EXISTS (Lineage 17, story OESC-S01). The OE method (BP-D53) allows one T-Box, one A-Box and one SHACL file per
subject, sharing one ontology IRI, with no file mixing roles and no side-by-side variant. This package shipped nine ontology
files: a vocabulary file that also held 284 controlled individuals, a rules file that mixed an individual with shapes, an
A-Box, a register, an archive, an exercise register, an alignment file, a second SHACL file (the severity-promotion overlay) and
the shapes. This tool performs the move, and `backlog_split_proof` proves it lost and changed nothing.

WHAT IT DOES, at the level of TEXT, so the dated comment blocks in every file (the history, L-112) travel with their statements:
  1. the 284 individuals in the vocabulary file and the 2 in the rules file move to the data file;
  2. the rules file's shapes move to the shapes file; the rules file goes;
  3. the register and the reference data file merge into one data file under the identity `backlog`;
  4. the severity-promotion overlay, a full second copy of the shapes differing in 59 severities, is replaced by the audit's
     own record: one SeverityPromotion individual per audited shape (63), carrying the shape, the severity and the rationale
     that sat in the overlay's "# G90" comment, plus the five vocabulary terms that describe it. The overlay is then DERIVED
     from the shapes and these individuals whenever a register adopting the audit is validated (backlog_make_promoted_shapes);
  5. the strategy exercise register is test input, so it moves to 03-tooling/exercises/; the alignment file names one adopting
     project's private deposit, so it moves to 06-package-provenance/ (the public distribution already drops that directory).
Ontology headers are rewritten (identity `backlog`, a role-specific versionIRI, the previous identity kept as priorVersion).
No statement other than a header is changed. Idempotent only on a pre-split tree; refuses if the tree is already split.

Usage: backlog_subject_split_v1_0_0.py [--apply]     (default: a dry run that reports what would move and writes nothing)
"""
import glob, os, re, subprocess, sys
from rdflib import Graph, RDF, RDFS, OWL, URIRef, Namespace

HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
ONT, SAFE = os.path.join(PKG, "01-ontologies"), os.path.join(PKG, "02-shacl-safeguards")
SH = Namespace("http://www.w3.org/ns/shacl#")
LIVE = "http://example.org/backlog"
T_TYPES = {OWL.Class, RDFS.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty, OWL.TransitiveProperty,
           OWL.SymmetricProperty, OWL.FunctionalProperty, OWL.InverseFunctionalProperty, RDF.Property}
S_TYPES = {SH.NodeShape, SH.PropertyShape}
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]


def latest(d, stem):
    c = sorted(glob.glob(os.path.join(d, stem + "_v*.ttl")), key=sv)
    if not c:
        raise SystemExit(f"no {stem} in {d}")
    return c[-1]


def ver(p):
    return ".".join(map(str, sv(p)))


def prefixes(text):
    return {m.group(1): m.group(2) for m in re.finditer(r"^@prefix\s+([\w-]*):\s+<([^>]*)>\s*\.", text, re.M)}


def subject_iri(tok, pfx):
    if tok.startswith("<") and ">" in tok:
        return tok[1:tok.index(">")]
    m = re.match(r"([\w-]*):([^\s;,.]+)", tok)
    return pfx[m.group(1)] + m.group(2) if m and m.group(1) in pfx else None


def segments(text):
    """Split into ('stmt', subject_token, [lines]) and ('other', None, [lines]). A statement starts at a column-0 line that is not a
    comment, directive or blank, and ends at the first line whose last non-space token is ' .' outside a triple-quoted string."""
    lines = text.split("\n"); out = []; i = 0; inq = False
    while i < len(lines):
        ln = lines[i]
        if ln and ln[0] not in " \t#@":
            j = i; inq = False
            while True:
                inq ^= (lines[j].count('"""') % 2 == 1)
                if not inq and lines[j].rstrip().endswith(" ."):
                    break
                j += 1
                if j >= len(lines):
                    raise SystemExit(f"unterminated statement at line {i + 1}")
            out.append(("stmt", ln.split()[0], lines[i:j + 1])); i = j + 1
        else:
            out.append(("other", None, [ln])); i += 1
    return out


def extract(text, wanted_iris):
    """Return (remaining text, moved text). A statement whose subject is in wanted_iris moves, with the comment lines directly above it."""
    pfx = prefixes(text); segs = segments(text); keep, moved = [], []
    for kind, tok, ls in segs:
        if kind == "stmt" and subject_iri(tok, pfx) in wanted_iris:
            cm = []
            while keep and keep[-1][0] == "other" and keep[-1][2][0].startswith("#") and keep[-1][2][0].strip():
                cm.insert(0, keep.pop()[2][0])
            moved.append("\n".join(cm + ls))
        else:
            keep.append((kind, tok, ls))
    return "\n".join(l for _, _, ls in keep for l in ls), "\n\n".join(moved)


def drop_statement(text, subject):
    """Remove the statement (the ontology header) whose subject token is subject."""
    segs = segments(text); out = [s for s in segs if not (s[0] == "stmt" and s[1] == subject)]
    if len(out) == len(segs):
        raise SystemExit(f"header {subject} not found")
    return "\n".join(l for _, _, ls in out for l in ls)


def header_of(text, subject):
    for kind, tok, ls in segments(text):
        if kind == "stmt" and tok == subject:
            return "\n".join(ls)
    raise SystemExit(f"header {subject} not found")


def body_without_prefixes(text):
    return "\n".join(l for l in text.split("\n") if not l.startswith("@prefix"))


def merged_prefixes(*texts):
    out = {}
    for t in texts:
        for k, v in prefixes(t).items():
            if k in out and out[k] != v:
                raise SystemExit(f"prefix {k}: bound to two namespaces ({out[k]}, {v}); resolve before merging")
            out[k] = v
    return "\n".join(f"@prefix {k}: <{v}> ." for k, v in sorted(out.items()))


def new_header(old, old_iri, new_iri, version_iri, version, label=None, prior=None, drop_imports=True):
    h = old.replace(f"<{old_iri}>", f"<{new_iri}>", 1)
    h = re.sub(r"owl:versionIRI <[^>]+> ;", f"owl:versionIRI <{version_iri}> ;", h, 1)
    h = re.sub(r'owl:versionInfo "[^"]+" ;', f'owl:versionInfo "{version}" ;', h, 1)
    if prior:
        h = re.sub(r"(owl:versionInfo \"[^\"]+\" ;\n)", r"\1    owl:priorVersion <" + prior + "> ;\n", h, 1) if "owl:priorVersion" not in h else \
            re.sub(r"owl:priorVersion ", f"owl:priorVersion <{prior}> , ", h, 1)
    if drop_imports:
        h = re.sub(r"\n    owl:imports <" + re.escape(LIVE) + r"> ;", "", h)
    h = re.sub(r'dcterms:identifier "[^"]+"', 'dcterms:identifier "backlog"', h, 1)
    if label:
        h = re.sub(r'rdfs:label "[^"]*"@en', f'rdfs:label "{label}"@en', h, 1)
    return h


PROMO_VOCAB = '''
#################################################################
#  v1.119.0 (Lineage 17, OESC-S01) -- the severity audit's own record
#  The overlay that used to ship as a second SHACL file was a full copy of the shapes differing in the severity of the audited
#  ones. What it carried that the shapes did not is, per audited shape, a severity and a reason. That is data about a RuleSet, so
#  it is individuals now, and the overlay is derived from the shapes and these individuals when a register adopting the audit is
#  validated (backlog_make_promoted_shapes). Nothing a register is judged by changes.
#################################################################
backlog:SeverityPromotion a owl:Class ; rdfs:subClassOf backlog:BacklogConcept ;
    rdfs:isDefinedBy <http://example.org/backlog> ; rdfs:label "severity promotion"@en ;
    skos:definition "One audited shape's severity under one rule set, with the reason. A register that adopts the rule set is validated against the shapes with each promoted shape's severity replaced by this one; every other shape keeps its own."@en .
backlog:promotionInRuleSet a owl:ObjectProperty ; rdfs:domain backlog:SeverityPromotion ; rdfs:range backlog:RuleSet ;
    rdfs:isDefinedBy <http://example.org/backlog> ; rdfs:label "promotion in rule set"@en ;
    skos:definition "The rule set under which this promotion applies."@en .
backlog:promotesShape a owl:ObjectProperty ; rdfs:domain backlog:SeverityPromotion ;
    rdfs:isDefinedBy <http://example.org/backlog> ; rdfs:label "promotes shape"@en ;
    skos:definition "The shape whose severity this promotion sets, a node shape in the package's shapes file."@en .
backlog:promotedSeverity a owl:ObjectProperty ; rdfs:domain backlog:SeverityPromotion ;
    rdfs:isDefinedBy <http://example.org/backlog> ; rdfs:label "promoted severity"@en ;
    skos:definition "The SHACL severity (sh:Violation, sh:Warning or sh:Info) the promoted shape has under the rule set."@en .
backlog:promotionRationale a owl:DatatypeProperty ; rdfs:domain backlog:SeverityPromotion ; rdfs:range xsd:string ;
    rdfs:isDefinedBy <http://example.org/backlog> ; rdfs:label "promotion rationale"@en ;
    skos:definition "Why the audit gave the shape this severity, as recorded on the shape's severity line when the audit was applied."@en .
'''


def promotions_from_overlay(over_text):
    """(shape name, severity token, rationale) for each shape whose severity line carries a '# G90' comment."""
    out = []
    ms = list(re.finditer(r"^backlog:(\w+Shape) a sh:NodeShape", over_text, re.M))
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(over_text)
        s = re.search(r"^    sh:severity (sh:\w+) ;\s*# (G90 .*)$", over_text[m.start():end], re.M)
        if s:
            out.append((m.group(1), s.group(1), s.group(2).strip()))
    return out


def main(argv):
    apply = "--apply" in argv
    tbox, rules = latest(ONT, "backlog_tbox"), latest(SAFE, "backlog_rules")
    abox, reg = latest(ONT, "backlog_abox"), latest(ONT, "backlog_framework_register_abox")
    shapes, over = latest(SAFE, "backlog_shacl"), latest(SAFE, "backlog_shacl_promoted")
    for p in (rules, over):
        if not os.path.exists(p):
            raise SystemExit("this tree is already split (no rules file or overlay); nothing to do")
    T, R = open(tbox).read(), open(rules).read()
    A, G = open(abox).read(), open(reg).read()
    S, O = open(shapes).read(), open(over).read()
    tg, rg = Graph().parse(tbox, format="turtle"), Graph().parse(rules, format="turtle")
    hdr = lambda g: set(g.subjects(RDF.type, OWL.Ontology))
    def individuals(g):
        return {s for s in set(g.subjects()) if isinstance(s, URIRef) and s not in hdr(g) and not (set(g.objects(s, RDF.type)) & (T_TYPES | S_TYPES))}
    ti, ri = individuals(tg), individuals(rg)
    T2, T_moved = extract(T, {str(x) for x in ti})
    R2, R_moved = extract(R, {str(x) for x in ri})
    promos = promotions_from_overlay(O)
    print(f"vocabulary file : {len(ti)} individuals move to the data file")
    print(f"rules file      : {len(ri)} individual(s) move to the data file; its shapes join the shapes file")
    print(f"overlay         : {len(promos)} audited shapes become SeverityPromotion individuals")
    if not apply:
        print("DRY RUN: nothing written. Re-run with --apply."); return 0

    tv, av, sv_ = ver(tbox), ver(abox), ver(shapes)
    ntv = ".".join(map(str, [1, int(tv.split('.')[1]) + 1, 0])); nav = ".".join(map(str, [1, int(av.split('.')[1]) + 1, 0]))
    nsv = ".".join(map(str, [1, int(sv_.split('.')[1]) + 1, 0]))
    # --- vocabulary
    th = header_of(T2, "<http://example.org/backlog>")
    T3 = T2.replace(th, new_header(th, LIVE, LIVE, f"{LIVE}/{ntv}", ntv, prior=f"{LIVE}/{tv}", drop_imports=False), 1)
    T3 = T3.rstrip("\n") + "\n" + PROMO_VOCAB
    # --- data: controlled individuals, the rules file's individuals, the old reference data, the register
    ah = header_of(A, "<http://example.org/backlog-abox>")
    A_body = drop_statement(A, "<http://example.org/backlog-abox>")
    G_body = drop_statement(G, "<http://example.org/backlog-framework-register>")
    promo_txt = "\n".join(
        f'backlog:SeverityPromotion_{n} a backlog:SeverityPromotion ; rdfs:label "Severity promotion: {n}"@en ;\n'
        f'    backlog:promotionInRuleSet backlog:RS_SeverityAudit_20260909 ; backlog:promotesShape backlog:{n} ;\n'
        f'    backlog:promotedSeverity {sev} ; backlog:promotionRationale "{why.replace(chr(92), chr(92) * 2).replace(chr(34), chr(92) + chr(34))}" .'
        for n, sev, why in promos)
    new_ah = new_header(ah, "http://example.org/backlog-abox", LIVE, f"{LIVE}/abox/{nav}", nav,
                        label="Backlog & Roadmap Semantic Framework (ABox: controlled individuals, reference data and the live register)",
                        prior="http://example.org/backlog-abox/" + av)
    pref = merged_prefixes(T, R, A, G, S, '@prefix sh: <http://www.w3.org/ns/shacl#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .')
    A_new = "\n".join([
        pref, "", new_ah, "",
        "#################################################################",
        f"#  v{nav} (Lineage 17, OESC-S01): this file now holds, in this order, the controlled individuals that lived in the vocabulary",
        "#  file, the two the rules file held, the reference individuals, the severity audit's record, and the live register (which was",
        f"#  backlog_framework_register_abox_v{ver(reg)}). Statements and their dated comments are moved as they were.",
        "#################################################################", "",
        "# ---- controlled individuals (from the vocabulary file)", T_moved, "",
        "# ---- individuals from the rules file", R_moved, "",
        "# ---- reference individuals (from backlog_abox)", body_without_prefixes(A_body), "",
        "# ---- the severity audit of 2026-09-09, one record per audited shape (from the severity-promotion overlay's G90 lines)", promo_txt, "",
        "# ---- the live register (from backlog_framework_register_abox)", body_without_prefixes(G_body), ""])
    # --- shapes: the base shapes plus the rules file's shapes, one file, identity backlog
    sh_h = header_of(S, "<http://example.org/backlog-shapes>")
    S_body = drop_statement(S, "<http://example.org/backlog-shapes>")
    R_body = drop_statement(R2, "<http://example.org/backlog-rules>")
    S_new = "\n".join([
        merged_prefixes(S, R2), "",
        new_header(sh_h, "http://example.org/backlog-shapes", LIVE, f"{LIVE}/shacl/{nsv}", nsv, prior="http://example.org/backlog-shapes/" + sv_), "",
        body_without_prefixes(S_body), "",
        "# ---- the rules (from backlog_rules, merged here at v%s under OESC-S01: one shapes file per subject)" % nsv,
        body_without_prefixes(R_body), ""])
    out = {os.path.join(ONT, f"backlog_tbox_v{ntv.replace('.', '_')}.ttl"): T3,
           os.path.join(ONT, f"backlog_abox_v{nav.replace('.', '_')}.ttl"): A_new,
           os.path.join(SAFE, f"backlog_shacl_v{nsv.replace('.', '_')}.ttl"): S_new}
    for p, t in out.items():
        open(p, "w").write(t); print("written:", os.path.relpath(p, PKG))
    gone = [tbox, abox, reg, shapes, rules, over]
    for p in gone:
        subprocess.run(["git", "-C", PKG, "rm", "-q", "-f", os.path.relpath(p, PKG)], check=True)
        print("retired:", os.path.relpath(p, PKG))
    for src, dst in ((latest(ONT, "backlog_strategy_exercise_abox"), os.path.join(PKG, "03-tooling", "exercises")),
                     (latest(ONT, "backlog_alignment_productbacklog"), os.path.join(PKG, "06-package-provenance"))):
        os.makedirs(dst, exist_ok=True)
        subprocess.run(["git", "-C", PKG, "mv", os.path.relpath(src, PKG), os.path.relpath(os.path.join(dst, os.path.basename(src)), PKG)], check=True)
        print("moved  :", os.path.relpath(src, PKG), "->", os.path.relpath(dst, PKG))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
