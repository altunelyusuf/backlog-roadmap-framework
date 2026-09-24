#!/usr/bin/env python3
"""backlog_make_promoted_shapes v1.1.0 -- regenerate, or check, the severity-promotion overlay.

A register that declares
    fw:Register backlog:adoptsRuleSet backlog:RS_SeverityAudit_20260909 .
is validated against the overlay INSTEAD of the base shapes (backlog_validate's promoted_overlay).
The overlay must therefore be the current base file with the audit's severities applied and
nothing else -- otherwise an adopting register silently loses every shape added since the overlay
was last generated.

v1.1.0 (an adopting project handover, promoted-overlay-stale-drops-succession-shapes): v1.0.0 only CHECKED,
named a regeneration script that existed only on one machine, and was not in the gate; the shipped
overlay had fallen 20 base versions and 21 shapes behind, including the succession shapes an
adopting successor needs most. This version regenerates in-package and its check is gated.

The classification source is the applied audit as recorded per shape in the current overlay: the
severity line of each audited shape carries an inline "# G90 ..." comment (the design v1.0.0
states). Those lines are carried forward verbatim. A base shape with no G90 line keeps its base
severity and is reported as UNAUDITED -- promoting it would be a classification decision, not a
regeneration. A G90 line whose shape no longer exists in the base is reported as DROPPED.

Usage:
  backlog_make_promoted_shapes_v1_1_0.py            check; exit 2 if the overlay is not an exact
                                                    regeneration of the current base
  backlog_make_promoted_shapes_v1_1_0.py --write X.Y.Z
                                                    write backlog_shacl_promoted_vX_Y_Z.ttl from the
                                                    current base and the highest overlay's G90 lines
"""
import glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
SAFE = os.path.join(PKG, "02-shacl-safeguards")
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
BASE = sorted(glob.glob(os.path.join(SAFE, "backlog_shacl_v*.ttl")), key=sv)[-1]
OVER = sorted(glob.glob(os.path.join(SAFE, "backlog_shacl_promoted_v*.ttl")), key=sv)[-1]
START = re.compile(r"^backlog:(\w+Shape) a sh:NodeShape", re.M)
SEV = re.compile(r"^    sh:severity sh:\w+ ;.*$", re.M)
ONT = re.compile(r"^<http://example\.org/backlog-shapes(?:-promoted)?> a owl:Ontology ;.*?\n\n", re.M | re.S)


def blocks(text):
    """(name, start, end) for each top-level NodeShape block."""
    ms = list(START.finditer(text))
    return [(m.group(1), m.start(), ms[i + 1].start() if i + 1 < len(ms) else len(text)) for i, m in enumerate(ms)]


def g90_lines(text):
    out = {}
    for name, a, b in blocks(text):
        m = SEV.search(text, a, b)
        if m and "# G90" in m.group(0):
            out[name] = m.group(0)
    return out


def body(text):
    """Everything after the ontology header block -- the shapes themselves."""
    m = ONT.search(text)
    return text[m.end():] if m else text


def apply(base_text, g90):
    out, pos = [], 0
    for name, a, b in blocks(base_text):
        if name in g90:
            m = SEV.search(base_text, a, b)
            if m:
                out.append(base_text[pos:m.start()]); out.append(g90[name]); pos = m.end()
    out.append(base_text[pos:])
    return "".join(out)


def main():
    base_text, over_text = open(BASE, encoding="utf-8").read(), open(OVER, encoding="utf-8").read()
    g90 = g90_lines(over_text)
    base_names = {n for n, _, _ in blocks(base_text)}
    unaudited = sorted(base_names - set(g90))
    dropped = sorted(set(g90) - base_names)
    regen = apply(base_text, g90)
    print(f"base      : {os.path.basename(BASE)} ({len(base_names)} shapes)")
    print(f"overlay   : {os.path.basename(OVER)} ({len(blocks(over_text))} shapes, {len(g90)} audited)")
    print(f"unaudited : {len(unaudited)} base shape(s) with no G90 classification -- kept at base severity")
    if dropped:
        print(f"DROPPED   : {len(dropped)} audited shape(s) no longer in the base: {', '.join(dropped)}")

    if "--write" in sys.argv:
        ver = sys.argv[sys.argv.index("--write") + 1]
        prev = re.search(r"owl:versionInfo \"([\d.]+)\"", over_text).group(1)
        m = ONT.search(regen)
        head = m.group(0)
        head = head.replace("<http://example.org/backlog-shapes> a owl:Ontology", "<http://example.org/backlog-shapes-promoted> a owl:Ontology", 1)
        head = re.sub(r"owl:versionIRI <[^>]+> ;", f"owl:versionIRI <http://example.org/backlog-shapes-promoted/{ver}> ;", head, 1)
        head = re.sub(r"owl:versionInfo \"[\d.]+\" ;", f"owl:versionInfo \"{ver}\" ;\n    owl:priorVersion <http://example.org/backlog-shapes-promoted/{prev}> ;", head, 1)
        comment = (
            f"# backlog_shacl_promoted v{ver} -- GENERATED from {os.path.basename(BASE)} by\n"
            f"# 03-tooling/backlog_make_promoted_shapes_v1_1_0.py, carrying forward the applied severity audit of\n"
            f"# 2026-09-09 as recorded on each audited shape's own severity line (\"# G90 ...\"). Shapes with no\n"
            f"# such line keep their base severity. Identical to the base file in every other byte. Loaded INSTEAD\n"
            f"# of the base file only for a register whose own data declares\n"
            f"#   fw:Register backlog:adoptsRuleSet backlog:RS_SeverityAudit_20260909 .\n"
            f"# Do not edit: regenerate with the tool above; the release gate refuses a stale overlay.\n")
        pre = regen[:m.start()]
        out = comment + pre + head + regen[m.end():]
        path = os.path.join(SAFE, "backlog_shacl_promoted_v%s.ttl" % ver.replace(".", "_"))
        open(path, "w", encoding="utf-8").write(out)
        print(f"written   : {os.path.basename(path)}")
        return 0

    if body(regen) != body(over_text):
        missing = sorted(base_names - {n for n, _, _ in blocks(over_text)})
        print(f"VERDICT   : STALE -- the overlay is not an exact regeneration of {os.path.basename(BASE)}"
              + (f"; {len(missing)} base shape(s) absent from it" if missing else "; shape bodies or severities differ"))
        print("            regenerate: backlog_make_promoted_shapes_v1_1_0.py --write <next overlay version>")
        return 2
    print("VERDICT   : CURRENT -- the overlay is the base file with the recorded audit severities, nothing else")
    return 0


if __name__ == "__main__":
    sys.exit(main())
