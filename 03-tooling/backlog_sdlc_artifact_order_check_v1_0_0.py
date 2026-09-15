#!/usr/bin/env python3
"""backlog_sdlc_artifact_order_check v1.0.0 -- SDLC-S06.

Exists because backlog_lineage_order_check measures STAGE OUTPUT order and WORK ITEM order (does the
chain come before the work) but never asked the one level finer question this obligation set is
actually about: does the OWED ARTIFACT a stage output claims -- the DomainEntity, the Blueprint, the
Specification, whatever StageOutputOwesShape's owesClass names -- first appear in git strictly BEFORE
the output that claims it, or after? An output can be perfectly ordered relative to other outputs and
still claim an artifact that was written to fit it afterward. That gap is what this measures.

Reuses the same git-anchoring method as backlog_lineage_order_check (first-appearance commit under
the register path, via `git log -S`), not a new one -- one honest measurement, not two competing
ones. Runs against a lineage's real StageOutput/StageObligation data or a --witness fixture map, the
same dual-mode pattern.

Usage: backlog_sdlc_artifact_order_check_v1_0_0.py <register.ttl> --lineage <local_name>
       [--repo-root <path>] [--register-path <rel_path_under_repo>] [--witness <json>]

Exit 0 and PASS, or exit 1 and names every artifact that appears after the output claiming it.
"""
import json
import subprocess
import sys

import rdflib

BL = rdflib.Namespace("http://example.org/backlog#")


def local(x):
    return str(x).split("#")[-1]


class GitWitness:
    def __init__(self, repo_root, rel_path):
        self.root, self.rel = repo_root, rel_path
        self.cache = {}

    def first(self, local_name, prefix):
        key = prefix + local_name
        if key in self.cache:
            return self.cache[key]
        r = subprocess.run(
            ["git", "log", "--reverse", "--format=%h", "-S", key + " ", "--", self.rel],
            cwd=self.root, capture_output=True, text=True,
        )
        line = r.stdout.strip().split("\n")[0] if r.stdout.strip() else ""
        val = None
        if line:
            h = line.split()[0]
            c = subprocess.run(["git", "rev-list", "--count", h], cwd=self.root, capture_output=True, text=True)
            val = (h, int(c.stdout.strip() or 0))
        self.cache[key] = val
        return val


class MapWitness:
    def __init__(self, path):
        self.m = json.load(open(path))

    def first(self, local_name, prefix):
        v = self.m.get(local_name)
        return (v[0], int(v[1])) if v else None


def prefix_for(g, L):
    ns_of = str(L).rsplit("#", 1)[0] + "#" if "#" in str(L) else None
    return next((p + ":" for p, ns in g.namespaces() if ns_of and str(ns) == ns_of), "fw:")


def artifact_order_check(g, L, witness, prefix):
    """For every StageOutput of L whose stage owes a required artifact class, check that at
    least one real artifact of that class in L first-appears at or before the output does.
    Returns a list of (output_local_name, class_local_name, output_ord, artifact_ord) for every
    violation -- an owed class where every matching artifact appears strictly after the output."""
    violations = []
    q = """
    SELECT ?output ?stage ?cls WHERE {
        ?output a backlog:StageOutput ; backlog:outputOfStage ?stage ; backlog:belongsToLineage ?l .
        FILTER NOT EXISTS { ?output backlog:outputRetracted true }
        ?ob a backlog:StageObligation ; backlog:obligationOfStage ?stage ; backlog:owesClass ?cls ;
            backlog:obligationSeverity backlog:Oblig_Required ; backlog:inObligationSet ?set .
        ?l backlog:adoptsObligationSet ?set .
        FILTER NOT EXISTS { ?output backlog:obligationWaivedBy ?ob }
    }
    """
    for row in g.query(q, initBindings={"l": L}, initNs={"backlog": BL}):
        out_first = witness.first(local(row.output), prefix)
        if out_first is None:
            continue  # output itself unwitnessed; backlog_lineage_order_check's own job
        out_ord = out_first[1]

        artifacts = list(g.subjects(rdflib.RDF.type, row.cls))
        artifacts = [a for a in artifacts if (L, BL.belongsToLineage, a) in g or (a, BL.belongsToLineage, L) in g]
        best_ord = None
        for a in artifacts:
            f = witness.first(local(a), prefix)
            if f is not None and (best_ord is None or f[1] < best_ord):
                best_ord = f[1]
        if best_ord is None:
            continue  # no witnessed artifact at all -- StageOutputOwesShape's own job, not this one
        if best_ord > out_ord:
            violations.append((local(row.output), local(row.cls), out_ord, best_ord))
    return violations


def main():
    argv = sys.argv[1:]
    if not argv:
        print("usage: backlog_sdlc_artifact_order_check_v1_0_0.py <register.ttl> --lineage <local_name> "
              "[--repo-root <path>] [--register-path <rel_path>] [--witness <json>]")
        return 2

    reg_path = argv[0]
    lineage_name = argv[argv.index("--lineage") + 1] if "--lineage" in argv else None
    repo_root = argv[argv.index("--repo-root") + 1] if "--repo-root" in argv else "."
    register_path = argv[argv.index("--register-path") + 1] if "--register-path" in argv else reg_path
    witness_path = argv[argv.index("--witness") + 1] if "--witness" in argv else None
    if not lineage_name:
        print("error: --lineage <local_name> is required")
        return 2

    g = rdflib.Graph()
    g.parse(reg_path, format="turtle")
    prefix = prefix_for(g, rdflib.URIRef(""))  # placeholder, refined below once L is known

    L = None
    for s in g.subjects(rdflib.RDF.type, BL.Lineage):
        if local(s) == lineage_name:
            L = s
            break
    if L is None:
        print(f"error: no backlog:Lineage named {lineage_name} in {reg_path}")
        return 2
    prefix = prefix_for(g, L)

    witness = MapWitness(witness_path) if witness_path else GitWitness(repo_root, register_path)

    violations = artifact_order_check(g, L, witness, prefix)
    if violations:
        print("FAIL: artifact first appears AFTER the output that claims it:")
        for out_name, cls_name, out_ord, art_ord in violations:
            print(f"  - {out_name} claims {cls_name}, but {cls_name} first appears at ordinal "
                  f"{art_ord} (output first appears at {out_ord})")
        return 1

    print(f"PASS: every witnessed owed artifact for {lineage_name} first appears at or before "
          f"the output claiming it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
