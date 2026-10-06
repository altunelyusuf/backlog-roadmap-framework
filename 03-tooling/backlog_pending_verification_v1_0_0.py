#!/usr/bin/env python3
"""backlog_pending_verification v1.0.0 -- lists every shape currently
carrying awaitingRealVerification, so a future session can find and
re-check them systematically rather than by searching prose.

Real gap this closes (G74): a shape whose positive case was proven only
by fixture, with the real condition it awaits stated only in a changelog
or a ruling's own prose, is easy to forget once the session that built it
ends. awaitingRealVerification makes the condition a real, queryable
fact; this script is the generic way to find every one that currently
exists, always reading the highest-versioned shipped shape file.

Usage: python3 backlog_pending_verification_v1_0_0.py
"""
import glob, os
import rdflib

B = rdflib.Namespace("http://example.org/backlog#")


def highest(pattern):
    import re
    matches = glob.glob(pattern)
    if not matches:
        return None

    def key(path):
        m = re.search(r"_v(\d+)_(\d+)_(\d+)", path)
        return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)

    return sorted(matches, key=key)[-1]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    shacl_path = highest(os.path.join(root, "02-shacl-safeguards", "backlog_shacl_v*.ttl"))
    if not shacl_path:
        print("FATAL: no shapes file found.")
        return
    g = rdflib.Graph()
    g.parse(shacl_path, format="turtle")
    pending = list(g.subject_objects(B.awaitingRealVerification))
    print("shapes file : %s" % os.path.basename(shacl_path))
    print("pending real-verification items: %d\n" % len(pending))
    for shape, condition in sorted(pending, key=lambda x: str(x[0])):
        name = str(shape).split("#")[-1]
        print("  %s" % name)
        print("    awaits: %s" % str(condition)[:220])
        print()
    if not pending:
        print("None currently -- every shape's own positive case is either proven against real")
        print("data already, or carries no such marker because none is genuinely awaited.")


if __name__ == "__main__":
    main()
