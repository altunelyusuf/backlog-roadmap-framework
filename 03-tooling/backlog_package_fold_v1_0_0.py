#!/usr/bin/env python3
"""backlog_package_fold v1.0.0 -- fold data files into the package's data files as modules, and move test inputs to the fixtures folder.

WHY THIS EXISTS (Lineage 18). The OE method (BP-D54) lets a package ship ONE vocabulary file, ONE data file and ONE shapes file, each with one
ontology header; what used to be a file of its own becomes a MODULE inside one of them. This tool does that move at the text level, so every
statement, its comments and its dated notes are carried as written (the same approach as the one-time split of Lineage 17).

WHAT IT CHANGES, AND NOTHING ELSE. A folded file's ontology header cannot stay (one header per file). It becomes an untyped module record at the
same IRI carrying dcterms:isPartOf (the target's ontology IRI), dcterms:identifier, rdfs:label and owl:versionInfo, and the former header is kept
above it as a comment, as written. Every other statement is appended unchanged. A file moved to the fixtures folder gains one statement, its
declared polarity, because that folder requires it. The before and after proof (backlog_split_proof) names exactly these two kinds of edit.

Usage: backlog_package_fold_v1_0_0.py --target TARGET.ttl --fold SRC.ttl [--fold SRC2.ttl ...] [--module-iri SRCNAME=IRI] [--apply]
       backlog_package_fold_v1_0_0.py --fixture SRC.ttl --polarity positive|negative [--apply]
Dry run unless --apply. With --apply the folded sources are deleted (they live on in git history and the release tags).
"""
import argparse, os, re, sys
from rdflib import Graph, RDF, RDFS, OWL, URIRef, Literal
from rdflib.namespace import DCTERMS

HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)


def prefixes(text):
    return {m.group(1): m.group(2) for m in re.finditer(r"^@prefix\s+([\w-]*):\s+<([^>]*)>\s*\.", text, re.M)}


def subject_iri(tok, pfx):
    if tok.startswith("<") and ">" in tok:
        return tok[1:tok.index(">")]
    m = re.match(r"([\w-]*):([^\s;,.]+)", tok)
    return pfx[m.group(1)] + m.group(2) if m and m.group(1) in pfx else None


def segments(text):
    """('stmt', subject_token, [lines]) and ('other', None, [line]). A statement starts at a column-0 line that is not a comment, directive
    or blank, and ends at the first line ending in ' .' outside a triple-quoted string."""
    lines = text.split("\n"); out = []; i = 0
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
                    raise SystemExit("unterminated statement at line %d" % (i + 1))
            out.append(("stmt", ln.split()[0], lines[i:j + 1])); i = j + 1
        else:
            out.append(("other", None, [ln])); i += 1
    return out


def version_of(path):
    m = re.search(r"_v(\d+)_(\d+)_(\d+)\.ttl$", path)
    return ".".join(m.groups()) if m else None


def split_header(text, iri):
    """(text without the header statement, the header statement's lines)."""
    pfx = prefixes(text); out = []; hdr = None
    for kind, tok, ls in segments(text):
        if kind == "stmt" and subject_iri(tok, pfx) == iri and hdr is None:
            hdr = ls
        else:
            out.append(ls)
    return "\n".join(l for ls in out for l in ls), hdr


def merged_prefixes(*texts):
    out = {}
    for t in texts:
        for k, v in prefixes(t).items():
            if k in out and out[k] != v:
                raise SystemExit("prefix %s is bound to two namespaces (%s, %s); resolve before folding" % (k, out[k], v))
            out[k] = v
    for k, v in (("dcterms", "http://purl.org/dc/terms/"), ("owl", "http://www.w3.org/2002/07/owl#"), ("rdfs", "http://www.w3.org/2000/01/rdf-schema#")):
        out.setdefault(k, v)
    return "\n".join("@prefix %s: <%s> ." % (k, v) for k, v in sorted(out.items()))


def without_prefixes(text):
    return "\n".join(l for l in text.split("\n") if not l.startswith("@prefix"))


def ontology_iri(path):
    g = Graph().parse(path, format="turtle")
    return [str(s) for s in g.subjects(RDF.type, OWL.Ontology)], g


def module_block(src_path, src_text, package_iri, forced_iri):
    iris, g = ontology_iri(src_path)
    name = os.path.basename(src_path)
    stem = re.sub(r"_v\d+_\d+_\d+\.ttl$", "", name)
    if len(iris) > 1:
        raise SystemExit("%s declares more than one ontology header" % name)
    if iris:
        iri = iris[0]; body, hdr = split_header(src_text, iri)
        label = g.value(URIRef(iri), RDFS.label); ident = g.value(URIRef(iri), DCTERMS.identifier); vi = g.value(URIRef(iri), OWL.versionInfo)
    else:
        iri = forced_iri
        if not iri:
            raise SystemExit("%s has no ontology header; give its module IRI with --module-iri %s=IRI" % (name, name))
        body, hdr, label, ident, vi = src_text, None, None, None, None
    label = str(label) if label else stem.replace("_", " ")
    ident = str(ident) if ident else stem
    vi = str(vi) if vi else (version_of(src_path) or "1.0.0")
    cm = ["#  MODULE %s -- folded in from %s (Lineage 18)." % (label, name)]
    if hdr:
        cm += ["#  Its former ontology header, kept as it was written:"] + ["#    " + l for l in hdr]
    else:
        cm += ["#  The file carried no ontology header; the module IRI below was chosen when it was folded in."]
    rec = ('<%s> dcterms:isPartOf <%s> ;\n    dcterms:identifier "%s" ;\n    rdfs:label "%s"@en ;\n    owl:versionInfo "%s" .'
           % (iri, package_iri, ident.replace('"', "'"), label.replace('"', "'"), vi))
    bar = "#" * 65
    return iri, bar + "\n" + "\n".join(cm) + "\n" + bar + "\n" + rec + "\n\n" + without_prefixes(body).strip("\n") + "\n"


def fold(target, srcs, forced):
    ttext = open(target, encoding="utf-8").read()
    tiris, _ = ontology_iri(target)
    if len(tiris) != 1:
        raise SystemExit("the target must declare exactly one ontology header")
    texts = [open(s, encoding="utf-8").read() for s in srcs]
    pfx = merged_prefixes(ttext, *texts)
    blocks = []
    for s, t in zip(srcs, texts):
        iri, blk = module_block(s, t, tiris[0], forced.get(os.path.basename(s)))
        blocks.append((s, iri, blk))
    head = "\n".join(l for l in ttext.split("\n") if not l.startswith("@prefix")).strip("\n")
    return pfx + "\n\n" + head + "\n\n" + "\n".join(b for _, _, b in blocks), blocks


def to_fixture(src, polarity):
    text = open(src, encoding="utf-8").read()
    iris, _ = ontology_iri(src)
    if len(iris) != 1:
        raise SystemExit("a fixture needs exactly one ontology header to carry its polarity")
    pfx = prefixes(text)
    if "backlog" not in pfx:
        text = '@prefix backlog: <http://example.org/backlog#> .\n' + text
    line = "\n# Lineage 18: this file moved to the fixtures folder, which requires a declared polarity (the one statement added by the move).\n<%s> backlog:hasExpectedPolarity backlog:Polarity_%s .\n" % (iris[0], polarity.capitalize())
    return text.rstrip("\n") + "\n" + line


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target"); ap.add_argument("--fold", action="append", default=[]); ap.add_argument("--module-iri", action="append", default=[])
    ap.add_argument("--fixture"); ap.add_argument("--polarity", choices=["positive", "negative"]); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if a.target:
        forced = dict(x.split("=", 1) for x in a.module_iri)
        new, blocks = fold(a.target, a.fold, forced)
        for s, iri, blk in blocks:
            print("fold %-60s -> module %s" % (os.path.relpath(s, PKG), iri))
        if a.apply:
            open(a.target, "w", encoding="utf-8").write(new)
            for s in a.fold:
                os.remove(s)
            print("applied: %d file(s) folded into %s" % (len(a.fold), os.path.relpath(a.target, PKG)))
        else:
            print("dry run (%d bytes would be written); --apply to do it" % len(new))
    elif a.fixture:
        if not a.polarity:
            raise SystemExit("--polarity is required with --fixture")
        new = to_fixture(a.fixture, a.polarity)
        dst = os.path.join(PKG, "03-tooling", "fixtures", os.path.basename(a.fixture))
        print("fixture %s -> %s (polarity %s)" % (os.path.relpath(a.fixture, PKG), os.path.relpath(dst, PKG), a.polarity))
        if a.apply:
            open(dst, "w", encoding="utf-8").write(new); os.remove(a.fixture); print("applied")
    else:
        ap.error("give --target with --fold, or --fixture")


if __name__ == "__main__":
    main()
