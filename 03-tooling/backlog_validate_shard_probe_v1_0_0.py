#!/usr/bin/env python3
"""backlog_validate_shard_probe v1.0.0 -- the split validation reports exactly what the single-process validation reports (G99 release A).

The validator (v1.13.0 and later) splits one validation over the machine's cores. A split is a speed-up only if it changes no verdict, so this probe
runs the SAME register that VIOLATES (the adversarial fixture, 37 violations and many advisories) twice with no cache:
  - once with BACKLOG_VALIDATE_SHARDS=1 (the plain single-process run), once with the default split (forced to at least 2 shards);
  - and requires every line of the two reports to be equal (the shapes line, tooling line and everything printed: counts, each violation, each
    advisory group). A shape lost or counted twice would change a count or a line.
Its own self-proof, refused if it fails (exit 3):
  - a report with one line removed is NOT equal to the true report (the comparison can see a lost result);
  - the validator's own guard refuses a split whose shards do not judge all the shapes (BACKLOG_VALIDATE_SHARD_FAULT=drop plants that fault in the
    worker; the run must fail, never print CONFORMANT or the same counts).
A pass is stored once per set of bytes (R9): the key covers this probe, the validator, T-Box, data file, shapes and the fixture; a changed byte or
BACKLOG_VALIDATE_FRESH=1 runs everything. Only passes are stored. Exit 0 equal; 2 differs; 3 the probe cannot discriminate.
Usage: backlog_validate_shard_probe_v1_0_0.py [FIXTURE]
"""
import glob, hashlib, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)


def newest(pattern):
    def key(p):
        m = re.search(r"_v(\d+)_(\d+)_(\d+)\.", p)
        return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)
    return sorted(glob.glob(pattern), key=key)[-1]


VALIDATE = newest(os.path.join(HERE, "backlog_validate_v*.py"))
FIXTURE = sys.argv[1] if len(sys.argv) > 1 else newest(os.path.join(HERE, "fixtures", "fixture_adversarial_random_v*.ttl"))
KEYFILES = [os.path.abspath(__file__), VALIDATE, FIXTURE, newest(os.path.join(PKG, "01-ontologies", "backlog_abox_v*.ttl")),
            newest(os.path.join(PKG, "01-ontologies", "backlog_tbox_v*.ttl")), newest(os.path.join(PKG, "02-shacl-safeguards", "backlog_shacl_v*.ttl"))]


def run(shards, fault=None):
    env = {k: v for k, v in os.environ.items() if k not in ("BACKLOG_VALIDATE_MEMO_DIR", "BACKLOG_VALIDATE_SHARD_FAULT")}
    env["BACKLOG_VALIDATE_SHARDS"] = str(shards)
    if fault:
        env["BACKLOG_VALIDATE_SHARD_FAULT"] = fault
    p = subprocess.run([sys.executable, VALIDATE, FIXTURE], capture_output=True, text=True, env=env)
    return p.returncode, p.stdout


def main():
    h = hashlib.sha256()
    for f in KEYFILES:
        h.update(os.path.basename(f).encode()); h.update(open(f, "rb").read())
    memo = os.environ.get("BACKLOG_VALIDATE_MEMO_DIR")
    stamp = os.path.join(memo, "shardproof_" + h.hexdigest() + ".ok") if memo else None
    if stamp and os.path.exists(stamp) and not os.environ.get("BACKLOG_VALIDATE_FRESH"):
        print("shard probe : identical bytes to a passing run -- not run again (%s)" % os.path.basename(FIXTURE)); return 0
    rc1, single = run(1)
    rc2, split = run(max(2, min(os.cpu_count() or 2, 4)))
    if rc1 != 1 or "NON-CONFORMANT" not in single:
        print("PROBE UNUSABLE : the fixture must violate in the single run (rc=%d)" % rc1); return 3
    # self-proof 1: a lost line is seen
    lines = single.splitlines()
    cut = next(i for i, l in enumerate(lines) if l.startswith("  [Violation"))
    if "\n".join(lines[:cut] + lines[cut + 1:]) == single.rstrip("\n"):
        print("SELF-PROOF FAILED : a report missing a violation line compared equal"); return 3
    # self-proof 2: a split that loses a share is refused by the validator, never passed
    rc3, lost = run(2, fault="drop")
    if rc3 == 0 or "CONFORMANT" in lost.replace("NON-CONFORMANT", "") or lost.strip() == single.strip():
        print("SELF-PROOF FAILED : a split that dropped a share of the shapes was accepted"); return 3
    print("self-proof  : ok -- a report with a line missing differs; a split that drops shapes is refused (rc=%d)" % rc3)
    if split.strip() != single.strip():
        a, b = single.strip().splitlines(), split.strip().splitlines()
        diff = [x for x in a if x not in b][:3] + [x for x in b if x not in a][:3]
        print("DIFFERENT : the split report is not the single-process report; first differences:")
        for d in diff:
            print("   ", d[:160])
        return 2
    print("shard probe : equal -- %d report lines identical between 1 shard and the split (%s)" % (len(lines), os.path.basename(FIXTURE)))
    if stamp:
        open(stamp, "w").write("ok\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
