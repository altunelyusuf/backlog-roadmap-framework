#!/usr/bin/env python3
"""backlog_new_shape_proof v1.2.0 -- every NEWLY authored shape declares its
proof, checked against a REAL, distinct baseline, with the run's own claim
written back as real, checkable data -- not only printed to a terminal.

Real gaps this closes over v1.1.0 (G75, per the owner's own direct request
to make preventive mechanisms ontology-based rather than code-only):

1. Configuration as data. v1.1.0 still required a human to type --baseline
   correctly every run. This version first looks for a real
   backlog:BaselineReference naming this tool in the current register; a
   CLI --baseline, if given, overrides it. The comparison target becomes a
   fact this suite's own rules can see and check, not a private argument a
   session has to remember.

2. Self-check as data, not only as a printed claim. Every run now emits a
   real backlog:ToolRunRecord (Turtle, to stdout or --record-out) naming
   the tool, both real content hashes, and what the run itself concluded
   about whether its baseline was genuinely distinct. SelfComparisonClaimShape
   then independently re-checks that claim against the two real hashes --
   the exact bug this session found (a run claiming a real comparison while
   its own two hashes were identical) is now something the register's own
   rules catch on the next validation pass, not only something a human
   would have to notice in scrollback.

This does NOT verify the tool's own internal comparison logic is correct.
No ontology reaches inside arbitrary code and proves its algorithm sound;
claiming so would overstate what any of this closes. What it closes is
narrower and real: the tool's own recorded claim cannot silently
contradict its own recorded inputs.

Usage:
  python3 backlog_new_shape_proof_v1_2_0.py [--baseline PATH] [--strict]
                                             [--register REGISTER.ttl]
                                             [--record-out FILE.ttl]
"""
import sys, os, glob, hashlib
import rdflib

B = rdflib.Namespace("http://example.org/backlog#")


def shape_names(path):
    from rdflib import URIRef, RDF
    SH = "http://www.w3.org/ns/shacl#"
    g = rdflib.Graph()
    g.parse(path, format="turtle")
    return {str(s) for s in g.subjects(RDF.type, URIRef(SH + "NodeShape"))}, g


def proven(name, g):
    return any(True for _ in g.triples((rdflib.URIRef(name), B.provenByFixture, None)))


def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def find_baseline_reference(register_path, script_filename):
    """Query the register for a real backlog:BaselineReference naming this
    tool, per the owner's own instruction that configuration should be a
    fact this suite can check, not a hardcoded or hand-typed assumption.
    Matches by the tool's own real scriptFileName fact, not by a hardcoded
    IRI local name -- the tool identifies itself by what it verifiably is
    (its own __file__ basename), not by a string literal this script would
    otherwise have to keep in sync with its own name by hand."""
    if not register_path or not os.path.isfile(register_path):
        return None
    g = rdflib.Graph()
    try:
        g.parse(register_path, format="turtle")
    except Exception:
        return None
    tool = None
    for t in g.subjects(rdflib.RDF.type, B.ToolScript):
        if str(g.value(t, B.scriptFileName)) == script_filename:
            tool = t
            break
    if tool is None:
        return None
    for ref in g.subjects(B.baselineForTool, tool):
        loc = g.value(ref, B.hasBaselineLocation)
        if loc:
            return str(loc)
    return None


def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    baseline_dir = None
    register_path = None
    record_out = None
    if "--baseline" in args:
        i = args.index("--baseline")
        if i + 1 < len(args):
            baseline_dir = args[i + 1]
    if "--register" in args:
        i = args.index("--register")
        if i + 1 < len(args):
            register_path = args[i + 1]
    if "--record-out" in args:
        i = args.index("--record-out")
        if i + 1 < len(args):
            record_out = args[i + 1]

    here = os.path.dirname(os.path.abspath(__file__))
    pkg = os.path.dirname(here)
    current = sorted(glob.glob(os.path.join(pkg, "02-shacl-safeguards", "backlog_shacl_v*.ttl")))
    if not current:
        raise SystemExit("FATAL: no shapes file found. Refusing to report on nothing.")
    current_path = current[-1]

    tool_local_name = os.path.basename(__file__)
    cloned_tmp = None
    if not baseline_dir:
        default_register = register_path or highest_register(pkg)
        queried = find_baseline_reference(default_register, tool_local_name)
        if queried:
            url_part = queried.split(" ")[0]
            if url_part.startswith("http") and "#" in url_part:
                repo_url, subpath = url_part.split("#", 1)
                cloned_tmp = clone_shallow(repo_url)
                if cloned_tmp:
                    baseline_dir = os.path.join(cloned_tmp, subpath)
                    print("baseline    : queried from a real backlog:BaselineReference, resolved by cloning %s -> %s" % (repo_url, baseline_dir))
                else:
                    print("baseline    : queried a real backlog:BaselineReference (%s) but could not clone it" % repo_url)
            elif os.path.isdir(url_part):
                baseline_dir = url_part
                print("baseline    : queried from a real backlog:BaselineReference in the register -> %s" % baseline_dir)

    def emit_record(used_hash, compared_hash, concluded_distinct):
        record = (
            "@prefix backlog: <http://example.org/backlog#> .\n"
            "@prefix ex: <http://example.org/toolrun#> .\n\n"
            "ex:Run_%s a backlog:ToolRunRecord ;\n"
            "    backlog:ranTool backlog:TS_backlog_new_shape_proof_v1_2_0 ;\n"
            "    backlog:usedBaselineHash \"%s\" ;\n"
            "    backlog:comparedAgainstHash \"%s\" ;\n"
            "    backlog:runConcludedDistinctBaseline %s .\n"
        ) % (file_hash(current_path)[:12], used_hash, compared_hash, str(concluded_distinct).lower())
        if record_out:
            with open(record_out, "w") as f:
                f.write(record)
            print("\ntool run record written to: %s" % record_out)
        else:
            print("\n--- real, checkable claim of this run (backlog:ToolRunRecord) ---")
            print(record)

    if not baseline_dir or not os.path.isdir(baseline_dir):
        print("baseline    : NOT PROVIDED, not queryable, or not a real directory")
        print("VERDICT     : NOT-VERIFIED — no real, distinct baseline given; this run proves nothing about what is new")
        cur_hash = file_hash(current_path)
        emit_record(cur_hash, cur_hash, False)
        sys.exit(1 if strict else 0)

    published = sorted(glob.glob(os.path.join(baseline_dir, "backlog_shacl_v*.ttl")))
    if not published:
        print("baseline    : %s (no backlog_shacl_v*.ttl found there)" % baseline_dir)
        print("VERDICT     : NOT-VERIFIED — baseline directory has no shapes file to compare against")
        cur_hash = file_hash(current_path)
        emit_record(cur_hash, cur_hash, False)
        sys.exit(1 if strict else 0)

    base_hash = file_hash(published[-1])
    cur_hash = file_hash(current_path)
    if base_hash == cur_hash:
        print("baseline    : %s -- IDENTICAL BYTES to the current shapes file" % published[-1])
        print("VERDICT     : NOT-VERIFIED — baseline is the same file as current; nothing to compare, this is not a real check")
        emit_record(base_hash, cur_hash, False)
        sys.exit(1 if strict else 0)

    cur_names, cur_g = shape_names(current_path)
    pub_names, _ = shape_names(published[-1])
    new_shapes = sorted(cur_names - pub_names)
    unproven = [n for n in new_shapes if not proven(n, cur_g)]
    print("current  : %s" % os.path.basename(current_path))
    print("baseline : %s (a real, distinct file, hash-verified different from current)" % os.path.basename(published[-1]))
    print("shapes in current file   : %d" % len(cur_names))
    print("shapes already published : %d" % len(pub_names & cur_names))
    print("NEW since baseline       : %d" % len(new_shapes))
    for n in unproven:
        print("   UNPROVEN NEW SHAPE  %s" % n.split("#")[-1])
    verdict_pass = not unproven
    print("VERDICT     : %s" % (
        "PASS - every newly authored shape declares its proof, verified against a real, distinct baseline"
        if verdict_pass else
        "REPORTED - %d new shape(s) ship without provenByFixture" % len(unproven)))
    emit_record(base_hash, cur_hash, True)
    sys.exit(1 if (unproven and strict) else 0)


def clone_shallow(repo_url):
    import subprocess, tempfile
    tmp = tempfile.mkdtemp(prefix="shapeproof_baseline_")
    try:
        subprocess.run(["git", "clone", "-q", "--depth", "1", repo_url, tmp],
                        check=True, timeout=60, capture_output=True)
        return tmp
    except Exception:
        return None


def highest_register(pkg):
    matches = glob.glob(os.path.join(pkg, "01-ontologies", "backlog_framework_register_abox_v*.ttl"))
    if not matches:
        return None
    import re

    def key(path):
        m = re.search(r"_v(\d+)_(\d+)(?:_(\d+))?\.ttl$", path)
        return tuple(int(x) if x else 0 for x in (m.groups() if m else (0, 0, 0)))

    return sorted(matches, key=key)[-1]


if __name__ == "__main__":
    main()
