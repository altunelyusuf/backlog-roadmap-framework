#!/usr/bin/env python3
"""backlog_probe_changed v1.1.0 -- run first only the gate's probes that read a changed file (G195).

The full release gate runs its probes after twenty minutes of other work, so a faulty probe or tool shows late. Every probe lists its inputs with --deps. This takes the
probe list of the newest gate script, asks each probe for its inputs, and runs the probes whose inputs (or the probe itself) changed in the git working tree, two at a time,
printing one line each and the last lines of any failure. It does not replace the gate: the gate still runs everything, and a probe skipped here is skipped only for speed.

With --own only the probes whose own file changed run (new or edited probes are the likeliest to be faulty, and this is the shortest first look).

v1.1.0 (Lineage 30, review of box 1): "changed" is read against the last published tree (the last fetched origin/main, else HEAD; `--since REF` names another) so committed but unpublished work counts, not only the working tree; a probe's inputs are its declared --deps together with the files the gate measured for it (06-package-provenance/PROBE_INPUTS.json), the gate's own source of keys; changes anywhere in the repository count, not only inside the package folder. A probe it cannot read inputs for is listed as left to the gate. Of PROBE_INPUTS.json only the `files` of a probe are read, not its `dirs` or `family`, so a probe whose measured input is a new file in a measured directory is found by the gate and not by this first look.

Usage: backlog_probe_changed.py [PACKAGE_DIR] [--jobs N] [--list] [--own] [--since REF]
Exit 0 when every probe run passes (or none needs to run), 1 when one fails."""
import concurrent.futures as cf, glob, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
def changed(pkg, since=None):
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=pkg, capture_output=True, text=True).stdout.strip()
    ref = since or ("origin/main" if subprocess.run(["git", "rev-parse", "--verify", "-q", "origin/main"], cwd=pkg, capture_output=True).returncode == 0 else "HEAD")
    files = set()
    for args in (["diff", "--name-only", "-M", ref], ["ls-files", "--others", "--exclude-standard"]):
        out = subprocess.run(["git", *args], cwd=top, capture_output=True, text=True).stdout
        for l in out.splitlines():
            if l.strip():
                files.add(os.path.realpath(os.path.join(top, l.strip())))
    return files
def measured(pkg, name):
    try:
        import json
        d = json.load(open(os.path.join(pkg, "06-package-provenance", "PROBE_INPUTS.json")))["probes"].get(name)
        return {os.path.realpath(os.path.join(pkg, f)) for f in (d or {}).get("files", [])}
    except Exception:
        return set()
def probe_list(pkg):
    gates = sorted(glob.glob(os.path.join(pkg, "03-tooling", "backlog_gate_v*.sh")), key=sv)
    m = re.search(r'PROBE_LIST="([^"]+)"', open(gates[-1]).read())
    return m.group(1).split() if m else []
def newest(pkg, name):
    c = sorted(glob.glob(os.path.join(pkg, "03-tooling", name + "_v*.py")), key=sv)
    return c[-1] if c else None
def deps(path):
    r = subprocess.run([sys.executable, "-I", path, "--deps"], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        return None
    return {os.path.realpath(l.strip()) for l in r.stdout.splitlines() if l.strip().startswith("/")}
def run(path):
    t = time.time()
    r = subprocess.run([sys.executable, "-I", path], capture_output=True, text=True, timeout=1500)
    return os.path.basename(path), r.returncode, time.time() - t, (r.stdout + r.stderr).strip().splitlines()[-5:]
def main(argv):
    pkg = os.path.dirname(HERE)
    rest = [a for i, a in enumerate(argv) if not a.startswith("--") and not re.fullmatch(r"\d+", a) and not (i and argv[i - 1] == "--since")]
    if rest: pkg = os.path.abspath(rest[0])
    jobs = int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 2
    ch = changed(pkg, argv[argv.index("--since") + 1] if "--since" in argv else None)
    todo, unknown = [], []
    for name in probe_list(pkg):
        p = newest(pkg, name)
        if not p: continue
        try: d = deps(p)
        except Exception: d = None
        if d is None: unknown.append(name); continue
        if os.path.realpath(p) in ch or (((d | measured(pkg, name)) & ch) and "--own" not in argv): todo.append(p)
    print("changed files: %d; probes in the gate list: %d; to run first: %d; without --deps (left to the gate): %d" % (len(ch), len(probe_list(pkg)), len(todo), len(unknown)))
    if "--list" in argv:
        print("\n".join("  " + os.path.basename(p) for p in todo)); return 0
    bad = 0
    with cf.ThreadPoolExecutor(max_workers=jobs) as ex:
        for name, rc, s, tail in ex.map(run, todo):
            print("  %-4s %-58s %5.0fs" % ("ok" if rc == 0 else "FAIL", name, s))
            if rc != 0:
                bad += 1; print("\n".join("      " + l[:200] for l in tail))
    print("PROBES RUN FIRST: %s" % ("PASS" if not bad else "FAIL (%d)" % bad))
    return 1 if bad else 0
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
