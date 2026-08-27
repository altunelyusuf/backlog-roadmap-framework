#!/usr/bin/env python3
"""backlog_script_decision_audit_v1_0_0.py — scripts that decide rather than execute.

BRF-EP24, story 1. The mission says what remains as code executes standard
engines and carries no meaning of its own: a script may run a validator, it may
not decide what is valid.

This audits for the shape of a decision, not for a list of known offenders. A
list would go stale the moment someone wrote a new one, and the point of the
story is that no script applies logic the ontology does not state.

Three patterns, each a place a script substitutes its own judgement:

  literal membership   `if x in ("a", "b")` — a classification the ontology
                       could hold, written as a tuple nobody can query.
  filename decision    `.endswith(...)` deciding behaviour — the fixture
                       polarity defect, generalised: a rename changes meaning.
  polarity by name     `"negative" in path` — the specific case It8 found.

Reports rather than fails by default. An audit that fails the build on its
first run gets suppressed, and a suppressed audit reports nothing at all;
--strict is available for a register that has already reached zero.

Exit 0 unless --strict and findings.
"""
import sys, os, re, glob

PATTERNS = [
    (r'if\s+\w+(?:\.\w+)*\s+in\s*\(\s*["\']', "literal membership"),
    (r'\.endswith\(["\']', "filename decision"),
    (r'["\']negative["\']\s*in\s+', "polarity by name"),
]

def audit(paths):
    """Scan real statements only.

    Docstrings and comments are skipped. Found on the first clean run: this
    audit flagged a docstring that QUOTED the code it had just caused to be
    removed. An audit that cannot tell an explanation from a decision reports
    its own success as a failure, and the honest fix is to parse rather than
    grep line by line.
    """
    import ast
    findings = []
    for f in sorted(paths):
        src = open(f, encoding="utf-8", errors="ignore").read()
        skip = set()
        try:
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
                        and isinstance(node.value.value, str):
                    for ln in range(node.lineno, (node.end_lineno or node.lineno) + 1):
                        skip.add(ln)
        except SyntaxError:
            pass
        for i, line in enumerate(src.split("\n"), 1):
            if i in skip or line.lstrip().startswith("#"):
                continue
            for pat, label in PATTERNS:
                if re.search(pat, line):
                    findings.append((os.path.basename(f), i, label, line.strip()[:60]))
    return findings

def main():
    strict = "--strict" in sys.argv
    here = os.path.dirname(os.path.abspath(__file__))
    me = os.path.basename(__file__)
    paths = [p for p in glob.glob(os.path.join(here, "*.py"))
             if os.path.basename(p) != me]
    findings = audit(paths)
    print("scripts audited     : %d" % len(paths))
    print("decisions in code   : %d" % len(findings))
    for name, ln, label, text in findings:
        print("   %-42s :%-4d %s" % (name[:42], ln, label))
        print("      %s" % text)
    print("VERDICT     : %s" % (
        "PASS - no script applies logic the ontology does not state"
        if not findings else
        "REPORTED - %d decision(s) remain in code; --strict fails on these"
        % len(findings)))
    sys.exit(1 if (findings and strict) else 0)

if __name__ == "__main__":
    main()
