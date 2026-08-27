#!/usr/bin/env python3
"""backlog_standard_row_check_v1_0_0.py — standard rows checked against the TBox.

BRF-EP25. The doc-coverage gate checks every class is NAMED in the standard and
never that a row AGREES with the ontology, so a row could contradict the TBox
indefinitely and nothing would notice.

Two stories, one tool:

  story 1  each row names the term it describes — resolved from the row's own
           first cell rather than annotated by hand, because 186 hand-written
           annotations would themselves be prose nobody checks.
  story 2  a row whose named term is absent from the TBox is reported.

What this does NOT do: judge whether a row's PROSE is a fair description. That
needs a reader.

And it cannot fully separate a TERM row from a CLAIM row. Measured on the
shipped standard: 187 rows, 124 naming a TBox term, 21 whose first cell is a
sentence rather than an identifier — "Order needs an external witness", "Every
epic decomposes", "L4 requires". Those are claims about the framework, not
descriptions of a class, and no amount of pattern tuning turns one into the
other.

The honest limit is stated rather than tuned away: --strict would fail on all
21 today, so the tool REPORTS by default and the 21 are recorded as a known
population. Suppressing them with a longer exclusion list would make the
checker agree with the document by construction, which is the defect it exists
to catch one level up.

Exit 0 unless --strict and unresolved rows.
"""
import sys, os, re, glob

def _header_words(tbox_path, reg_path):
    """First-cell values that name a column rather than a term.

    EXPORTED at v1.118.0, after the script-decision audit caught this file.
    The audit shipped in the same iteration and reported zero; it now reports
    the checker written beside it. An audit that passes once is a measurement;
    one that keeps passing is a constraint.

    Fails loudly rather than falling back.
    """
    from rdflib import Graph, Namespace, RDF
    B = Namespace("http://example.org/backlog#")
    g = Graph()
    g.parse(tbox_path, format="turtle")
    g.parse(reg_path, format="turtle")
    words = {str(g.value(w, B.headerWord)) for w in g.subjects(RDF.type, B.TableHeaderWord)
             if g.value(w, B.headerWord) is not None}
    if not words:
        raise SystemExit(
            "FATAL: the ontology declares no TableHeaderWord. Exported at "
            "v1.118.0 and read here; refusing to fall back to a literal."
        )
    return words


def rows_of(md):
    out = []
    for i, line in enumerate(open(md, encoding="utf-8", errors="ignore"), 1):
        s = line.strip()
        if not s.startswith("|") or set(s) <= set("|-: "):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if cells:
            out.append((i, cells[0]))
    return out

def tbox_terms(tbox, reg=None):
    """Terms the TBox defines, plus the abbreviations the docs use for them.

    A checker resolving identifiers literally reads "L2" as an absent term
    because the class is L2_EvidenceBound. The honest fix is to teach the
    checker the abbreviation, not to rewrite the document or exclude the row —
    both of which would make the checker agree with the document by
    construction.
    """
    from rdflib import Graph, Namespace, RDF
    B = Namespace("http://example.org/backlog#")
    g = Graph()
    g.parse(tbox, format="turtle")
    terms = {str(s).split("#")[-1] for s in set(g.subjects())
             if str(s).startswith(str(B))}
    if reg:
        gr = Graph()
        gr.parse(tbox, format="turtle")
        gr.parse(reg, format="turtle")
        for a in gr.subjects(RDF.type, B.TermAbbreviation):
            txt = gr.value(a, B.abbreviationText)
            if txt is not None:
                terms.add(str(txt))
    return terms

def main():
    strict = "--strict" in sys.argv
    here = os.path.dirname(os.path.abspath(__file__))
    pkg = os.path.dirname(here)
    std = sorted(glob.glob(os.path.join(
        pkg, "04-documentation", "BACKLOG_ROADMAP_FRAMEWORK_STANDARD_v*.md")))[-1]
    tbox = sorted(glob.glob(os.path.join(
        pkg, "01-ontologies", "backlog_tbox_v*.ttl")))[-1]
    reg = sorted(glob.glob(os.path.join(
        pkg, "01-ontologies", "backlog_framework_register_abox_v*.ttl")))[-1]
    headers = _header_words(tbox, reg)
    terms = tbox_terms(tbox, reg)
    rows = rows_of(std)
    named, unnamed, absent = [], [], []
    for ln, first in rows:
        # A row names a term when its first cell contains a backtick-quoted or
        # bare identifier the TBox knows. Resolved, not annotated: 186 hand
        # annotations would be prose nobody checks, which is the defect.
        # Header rows and emphasis rows name no term by design. Found on the
        # first run: 50 "absent" rows were mostly the word "Term" repeated —
        # a checker that cannot tell a header from a claim reports the
        # document's structure as a defect.
        bare = first.strip("*` ")
        if bare in headers:
            continue
        # Presentation, not classification: emphasis marks how a row READS and
        # states nothing about the ontology, so this stays in the script. The
        # audit flags the pattern and the exemption is stated rather than hidden.
        if first[:2] == "**" and first[-2:] == "**":  # audit-exempt: presentation
            continue
        # An abbreviation may contain characters an identifier cannot —
        # "Scope-facing" is Facing_Scope written for a reader. Matching only
        # identifier-shaped substrings never reaches it. Found when three of
        # the seventeen "uncheckable claim rows" turned out to be display
        # forms of real terms: the abbreviation mechanism existed and the
        # matcher could not use it.
        if bare in terms:
            named.append((ln, bare))
            continue
        cands = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", first)
        hit = [c for c in cands if c in terms]
        if hit:
            named.append((ln, hit[0]))
        elif any(c[:1].isupper() for c in cands):
            absent.append((ln, first[:44]))
        else:
            unnamed.append((ln, first[:44]))
    print("standard            : %s" % os.path.basename(std))
    print("table rows          : %d" % len(rows))
    print("rows naming a term  : %d" % len(named))
    print("rows naming nothing : %d (prose rows: headings, levels, examples)" % len(unnamed))
    print("rows naming an ABSENT term : %d" % len(absent))
    for ln, txt in absent[:20]:
        print("   line %-5d %s" % (ln, txt))
    print("VERDICT     : %s" % (
        "PASS - no row describes a term the TBox does not define"
        if not absent else
        "REPORTED - %d row(s) name a term absent from the TBox" % len(absent)))
    sys.exit(1 if (absent and strict) else 0)

if __name__ == "__main__":
    main()
