#!/usr/bin/env python3
"""backlog_close_preview v1.0.0 -- everything that closing an item would require, in ONE run (G109, reported by the agentic-sdlc session, 2026-10-13).

Closing an epic took five gate runs because each run reported only what was visible in the state it was run on: the Done rules fire when an item reads Done, so the
requirement that belongs to the next layer (a dated measurement of the objective, a recorded test harness, evidence attesting the criterion, a baseline measurement
before the work) did not show until the first was met. This tool asks the question once: it validates the register as it is, then validates a copy in which the named
item reads Done, and prints every violation the second run has that the first did not -- the complete list of what closing the item requires, with the same messages the
gate gives. The register on disk is never changed; the copy lives in a temporary folder.

  python3 backlog_close_preview_v1_0_0.py ITEM DATA.ttl [DATA2.ttl ...] [--state Done]
ITEM is the item's IRI, its local name, or its backlog:hasIdentifier. Exit 0 when closing adds no violation, 1 when it does, 2 on a usage error.
Requirements that rest on a fact only the future can supply (a measurement taken after the work) are listed like the rest: the tool states what is owed, it does not supply it.
"""
import argparse, glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
BL = "http://example.org/backlog#"

def violations(val, files):
    out = subprocess.run([sys.executable, "-B", val] + files, capture_output=True, text=True, timeout=3600).stdout
    got = []
    for ln in out.splitlines():
        m = re.match(r"\s*\[Violation\]\s+(\S+)\s+(.*)$", ln)
        if m: got.append((m.group(1), m.group(2).strip()))
    return got

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("item"); ap.add_argument("data", nargs="+"); ap.add_argument("--state", default="Done")
    a = ap.parse_args()
    import rdflib
    from rdflib import URIRef, Literal
    val = sorted(glob.glob(os.path.join(HERE, "backlog_validate_v*.py")), key=sv)[-1]
    has_state, has_id = URIRef(BL + "hasState"), URIRef(BL + "hasIdentifier")
    graphs = []
    for f in a.data:
        g = rdflib.Graph(); g.parse(f, format="turtle"); graphs.append((f, g))
    target = None
    for f, g in graphs:
        for s in set(g.subjects(has_state, None)):
            if str(s) == a.item or str(s).split("#")[-1].split("/")[-1] == a.item or (s, has_id, Literal(a.item)) in g:
                target = s
    if target is None:
        print(f"no item '{a.item}' with a state in the given files"); return 2
    base = violations(val, a.data)
    with tempfile.TemporaryDirectory() as d:
        mod = []
        for f, g in graphs:
            if (target, has_state, None) in g:
                g.remove((target, has_state, None)); g.add((target, has_state, URIRef(BL + a.state)))
            p = os.path.join(d, os.path.basename(f)); g.serialize(p, format="turtle"); mod.append(p)
        after = violations(val, mod)
    seen = {}
    for x in base: seen[x] = seen.get(x, 0) + 1
    new = []
    for x in after:
        if seen.get(x, 0) > 0: seen[x] -= 1
        else: new.append(x)
    print(f"item     : {target}\nstate    : {a.state}\nbefore   : {len(base)} violation(s)\nafter    : {len(after)} violation(s)")
    if not new:
        print(f"closing as {a.state} adds no violation."); return 0
    print(f"closing as {a.state} adds {len(new)} violation(s) -- everything owed, in one list:")
    for f, m in sorted(new): print(f"  [{f}] {m}")
    return 1

if __name__ == "__main__":
    if sys.argv[1:] == ["--deps"]:
        pkg = os.path.dirname(HERE)
        for pat in ("03-tooling/backlog_validate_v*.py", "02-shacl-safeguards/backlog_shacl_v*.ttl", "01-ontologies/backlog_tbox_v*.ttl"):
            print(sorted(glob.glob(os.path.join(pkg, pat)), key=sv)[-1])
        print(os.path.abspath(__file__)); sys.exit(0)
    sys.exit(main())
