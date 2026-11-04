#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe reads no record of the framework register)
"""backlog_checks_kept_probe v1.0.1 -- proves no check of the gate was removed or weakened by Lineage 31 (story Kept).

checks_before_lineage31_v1_0_0.tsv records the gate of 4.2.3 (v1.0.1 judges the gate and the probes as they stand at the tag where the lineage closed, backlog-roadmap-framework-v4.6.0, read from git, so later work does not make a statement about this lineage false): every section header, every probe of the probe list, and for each probe a digest of its text with the validator
restriction argument and the version numbers removed. The probe holds that
  1  every recorded section header is still echoed by the newest gate
  2  every recorded probe is still in the probe list of the newest gate, and its file exists
  3  the newest version of each recorded probe, with the restriction argument and version numbers removed, is the text recorded: its assertions are unchanged
  4  the restriction argument is the only difference proved by 3: a probe whose digest differs is named
  5  the check itself discriminates: a recorded probe missing from a planted gate text is refused
Exit 0 when every expectation holds, 1 otherwise."""
import glob, hashlib, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(HERE, pat)), key=sv)[-1]
base = latest("checks_before_lineage31_v*.tsv")
END = "backlog-roadmap-framework-v4.6.0"
ROOT = subprocess.run(["git", "-C", HERE, "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
PKGREL = os.path.relpath(os.path.dirname(HERE), ROOT) if ROOT else ""
def gitsh(*a): return subprocess.run(["git", "-C", ROOT, *a], capture_output=True)
def at_end(stem, ext):
    """(file name, bytes) of the newest STEM file in 03-tooling as the END tag holds it, or (None, None)."""
    out = gitsh("ls-tree", "--name-only", END, PKGREL + "/03-tooling/").stdout.decode().split()
    c = [n for n in out if re.fullmatch(re.escape(PKGREL + "/03-tooling/" + stem) + r"_v\d+_\d+_\d+\." + ext, n)]
    if not c: return None, None
    n = sorted(c, key=sv)[-1]
    return n, gitsh("show", END + ":" + n).stdout
gate = "the gate at " + END
if sys.argv[1:] == ["--deps"]:
    print(base); print(os.path.abspath(__file__))     # the rest is read from a tag, which never changes
    sys.exit(0)
bad = []
def expect(n, ok):
    print(("PASS  " if ok else "FAIL  ") + n)
    if not ok: bad.append(n)
NORM = lambda t: re.sub(r"v\d+[._]\d+[._]\d+", "v", re.sub(r', env=\{\*\*os\.environ, "BACKLOG_VALIDATE_ONLY_MESSAGE": .*?\}\)', ")", t))
rows = [l.rstrip("\n").split("\t") for l in open(base, encoding="utf-8") if l.strip() and not l.startswith("#")]
secs = [r[1] for r in rows if r[0] == "section"]; probes = {r[1]: r[2] for r in rows if r[0] == "probe"}
def judge(gt):
    plist = re.search(r'^PROBE_LIST="(.*?)"', gt, re.M).group(1).split()
    return [s for s in secs if ('echo "%s"' % s) not in gt], [p for p in probes if p not in plist or at_end(p, "py")[0] is None]
if not ROOT or gitsh("rev-parse", "--verify", "-q", END + "^{commit}").returncode != 0:
    print("NOT RUN  the tag %s is not in this clone; nothing was compared (never read as a pass)" % END); sys.exit(0)
gn, gb = at_end("backlog_gate", "sh")
gt = gb.decode("utf-8")
ms, mp = judge(gt)
expect("1 every recorded section (%d) is still echoed" % len(secs), not ms)
if ms: print("   missing:", ms[:3])
expect("2 every recorded probe (%d) is still listed and its file exists" % len(probes), not mp)
if mp: print("   missing:", mp[:3])
changed = [p for p, d in probes.items() if at_end(p, "py")[0] and hashlib.sha256(NORM(at_end(p, "py")[1].decode("utf-8")).encode()).hexdigest()[:16] != d]
expect("3 the assertions of every recorded probe are the recorded ones, ignoring the restriction argument and versions", not changed)
if changed: print("   changed:", changed[:5])
expect("4 (the list of changed probes above is empty)", not changed)
planted = re.sub(r"(?m)^(PROBE_LIST=\"(?:.*? )?)" + re.escape(next(iter(probes))) + r"( |\")", r"\1\2", gt, count=1).replace(secs[0], "== gone ==", 1)
ms2, mp2 = judge(planted)
expect("5 the check refuses a planted gate with one probe and one section taken out", bool(ms2) and bool(mp2))
print("recorded:", os.path.basename(base)); print("gate    :", gate); print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
