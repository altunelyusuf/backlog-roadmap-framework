#!/usr/bin/env python3
"""backlog_package_activation_drift_classifier_probe v1.1.0 -- shown on six throwaway cases:
  1 no drift at all                                                           -> "no drift found"
  2 real basis, claimed direction, dependency starts no earlier (the owner's first-named case) -> PackageScopePlanning, dissolve-and-repack
  3 NO real dependsOn edge in either direction                               -> MistakenDependency, remove the edge
  4 real basis, but the dependency already started earlier -- not case 2     -> UNCLASSIFIED
  5 real basis running the OTHER way only (the direction is backwards)       -> WrongDirection, flip the edge
Exit 0 all hold; 1 a case did not.
"""
import glob, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = sorted(glob.glob(os.path.join(HERE, "backlog_package_activation_drift_classifier_v*.py")),
              key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]])[-1]
PREFIX = "@prefix backlog: <http://example.org/backlog#> .\n@prefix ex: <http://example.org/t#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"

if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(TOOL)
    sys.exit(0)

bad = []


def check(name, cond):
    print("  %-4s %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        bad.append(name)


def run(ttl):
    with tempfile.NamedTemporaryFile(suffix=".ttl", mode="w", delete=False) as f:
        f.write(PREFIX + ttl)
        p = f.name
    try:
        r = subprocess.run([sys.executable, TOOL, p], capture_output=True, text=True)
        return r.returncode, r.stdout
    finally:
        os.remove(p)


# 1: no drift -- B depends on A, A already Done
code, out = run("""
ex:A a backlog:Package . ex:tA a backlog:Task ; backlog:hasState backlog:Done ; backlog:memberOfContainer ex:A .
ex:B a backlog:Package ; backlog:containerDependsOn ex:A . ex:tB a backlog:Task ; backlog:hasState backlog:InProgress ; backlog:memberOfContainer ex:B .
""")
check("1 no drift when the dependency is already Done", code == 0 and "no drift found" in out)

# 2: the named case -- real basis, dependency package starts no earlier than the drifted one
code, out = run("""
ex:IterEarly a backlog:Iteration ; backlog:iterationStart "2026-01-01T00:00:00"^^xsd:dateTime .
ex:IterLate a backlog:Iteration ; backlog:iterationStart "2026-03-01T00:00:00"^^xsd:dateTime .
ex:A2 a backlog:Package ; backlog:targetsIteration ex:IterLate .
ex:tA2 a backlog:Task ; backlog:hasState backlog:Proposed ; backlog:memberOfContainer ex:A2 .
ex:B2 a backlog:Package ; backlog:containerDependsOn ex:A2 ; backlog:targetsIteration ex:IterEarly .
ex:tB2 a backlog:Task ; backlog:hasState backlog:InProgress ; backlog:memberOfContainer ex:B2 ; backlog:dependsOn ex:tA2 .
""")
check("2 the named case classifies as PackageScopePlanning", code == 0 and "classification: PackageScopePlanning" in out and "dissolve and repack" in out)

# 3: a drift with no real dependsOn basis in either direction -- mistaken link
code, out = run("""
ex:A3 a backlog:Package . ex:tA3 a backlog:Task ; backlog:hasState backlog:Proposed ; backlog:memberOfContainer ex:A3 .
ex:B3 a backlog:Package ; backlog:containerDependsOn ex:A3 . ex:tB3 a backlog:Task ; backlog:hasState backlog:InProgress ; backlog:memberOfContainer ex:B3 .
""")
check("3 no real basis in either direction is MistakenDependency, remedy names removing the edge", code == 0 and "classification: MistakenDependency" in out and "remove the containerDependsOn" in out)

# 4: a real basis in the claimed direction, but the dependency package started EARLIER than the drifted one -- not case 2
code, out = run("""
ex:IterEarly4 a backlog:Iteration ; backlog:iterationStart "2026-01-01T00:00:00"^^xsd:dateTime .
ex:IterLate4 a backlog:Iteration ; backlog:iterationStart "2026-03-01T00:00:00"^^xsd:dateTime .
ex:A4 a backlog:Package ; backlog:targetsIteration ex:IterEarly4 .
ex:tA4 a backlog:Task ; backlog:hasState backlog:Proposed ; backlog:memberOfContainer ex:A4 .
ex:B4 a backlog:Package ; backlog:containerDependsOn ex:A4 ; backlog:targetsIteration ex:IterLate4 .
ex:tB4 a backlog:Task ; backlog:hasState backlog:InProgress ; backlog:memberOfContainer ex:B4 ; backlog:dependsOn ex:tA4 .
""")
check("4 a real basis with the dependency already started earlier is UNCLASSIFIED, not case 2", code == 0 and "classification: UNCLASSIFIED" in out and "does not fit" in out)

# 5: a real basis running the OTHER way only -- the containerDependsOn direction is backwards
code, out = run("""
ex:A5 a backlog:Package ; backlog:containerDependsOn ex:B5 .
ex:tA5 a backlog:Task ; backlog:hasState backlog:InProgress ; backlog:memberOfContainer ex:A5 .
ex:B5 a backlog:Package . ex:tB5 a backlog:Task ; backlog:hasState backlog:Proposed ; backlog:memberOfContainer ex:B5 ; backlog:dependsOn ex:tA5 .
""")
check("5 a real basis running only the other way is WrongDirection, remedy names flipping the edge", code == 0 and "classification: WrongDirection" in out and "flip the containerDependsOn" in out)

print("VERDICT : " + ("ALL HOLD" if not bad else "FAILED -- " + "; ".join(bad)))
sys.exit(0 if not bad else 1)
