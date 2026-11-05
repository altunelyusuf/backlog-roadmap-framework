#!/usr/bin/env python3
# register-use: reference-only
# (audited: the probe builds its own throwaway repositories and registers; it reads no record of the framework register)
"""backlog_witness_branch_probe v1.4.0 -- a lineage witnessed on a work branch (ruling G203, order check v1.20.0).

v1.4.0 (after the independent review of the batch): cases 13 and 14, a release tag followed by extra text and a malformed release tag, read broken; the repair of 1.20.0 that refuses them had no case.

v1.3.0 (repair after the third independent review): cases 11 and 12, a blank recorded value and a hash followed by extra text, read broken; the counts in this text are corrected.

v1.2.0 (repair after the second independent review): case 9, a branch whose name ends like the real one (a/refs/heads/wip/x) must not block it; case 10, a recorded value that is neither a commit nor a release reads broken.

v1.1.0 (repair after the independent review of 1.0.0, which found three of its five faults not real): every case checks the
reason printed as well as the verdict; case 2 has a main line that is itself in order, so reading a missing branch on the main
line would pass and is caught; new cases for a branch deleted on origin after it was fetched, an unreachable origin and a
recorded commit that does not hold its output; and the probe runs its cases on two mutants of the checker and requires each
mutant to be caught.

Each case builds a throwaway origin and clone. On a work branch the five stages of a lineage close in five commits, each
recording the commit of the stage before, and its one story comes after the backlog stage; the main line then receives the
finished register in ONE commit, as a batch release does. The order check runs on the main line:

  0 the lineage names its branch                                      -> ORDERED, "witnessed on"
  1 the lineage names no branch                                       -> not ORDERED (the main line holds one commit)
  2 it names a branch never pushed; the main line itself is in order  -> WITNESS_BROKEN, "not held by origin"
  3 on the branch the story comes before the backlog stage            -> BYPASS
  4 a stage output records a commit origin does not hold              -> WITNESS_BROKEN, "does not hold"
  5 a stage output records a real commit of another branch            -> WITNESS_BROKEN, "not an ancestor"
  6 the branch was fetched, then deleted on origin                    -> WITNESS_BROKEN, "not held by origin"
  7 origin cannot be reached                                          -> WITNESS_BROKEN, "cannot be reached"
  8 a stage output records an earlier commit that does not hold it    -> WITNESS_BROKEN, "does not hold it"
  9 origin also holds a branch a/refs/heads/wip/x                     -> ORDERED, "witnessed on"
 10 a stage output records "release 4.8.0"                            -> WITNESS_BROKEN, "not a commit hash or a release tag"
 11 a stage output records a blank value                              -> WITNESS_BROKEN, "not a commit hash or a release tag"
 12 a stage output records a hash followed by extra text              -> WITNESS_BROKEN, "not a commit hash or a release tag"
 13 a stage output records a release tag followed by extra text       -> WITNESS_BROKEN, "not a commit hash or a release tag"
 14 a stage output records a malformed release tag                    -> WITNESS_BROKEN, "not a commit hash or a release tag"
Mutants (each must make at least one case fail): A, the per-lineage branch witness switched off; B, the rule that a recorded
commit holds its output switched off; C, the first line of origin's answer read instead of the exact ref; D, a recorded value of
any form accepted.
Exit 0 when every case reads as expected and every mutant is caught, 1 otherwise."""
import glob, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(latest("03-tooling/backlog_lineage_order_check_v*.py")); print(os.path.abspath(__file__)); sys.exit(0)
CHK = latest("03-tooling/backlog_lineage_order_check_v*.py")

HEAD = """@prefix backlog: <http://example.org/backlog#> .
@prefix ex: <http://example.org/witness-branch#> .
ex:L a backlog:Lineage ; backlog:lineageOrdinal 1 ; backlog:lineageArchived false ; backlog:hasLineageStatus backlog:LS_InProgress ; backlog:lineageForMission ex:M .
ex:M a backlog:Mission ; backlog:belongsToLineage ex:L .
"""
STAGES = [("Mission", None), ("Scope", "Mission"), ("Goal", "Scope"), ("Objective", "Goal"), ("Backlog", "Objective")]
STORY = "ex:S1 a backlog:Story ; backlog:hasIdentifier \"S1\" ; backlog:hasState backlog:Ready ; backlog:belongsToLineage ex:L .\n"
ENV = {**os.environ, "GIT_AUTHOR_NAME": "probe", "GIT_AUTHOR_EMAIL": "probe@example.org",
       "GIT_COMMITTER_NAME": "probe", "GIT_COMMITTER_EMAIL": "probe@example.org"}

def git(cwd, *a):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, env=ENV)
    if r.returncode != 0:
        raise SystemExit(f"probe setup failed: git {' '.join(a)}: {r.stderr.strip()}")
    return r.stdout.strip()

def out(st, prev):
    s = f"ex:O_{st} a backlog:StageOutput ; backlog:outputOfStage backlog:Stage_{st} ; backlog:belongsToLineage ex:L ; backlog:hasStateDigest \"d{st}\""
    return s + (f" ; backlog:consumesOutput ex:O_{prev}" if prev else "") + " .\n"

def chain(work, reg, text, case, base, side):
    """Commits the five stages and the story in work's current branch; each stage records the commit of the stage before."""
    pieces, hashes = [], {}
    for st, prev in STAGES:
        if case == 3 and st == "Backlog":
            pieces.append(STORY)
            open(reg, "w").write(text + "".join(pieces)); git(work, "add", "-A"); git(work, "commit", "-q", "-m", "story first")
        pieces.append(out(st, prev))
        if prev is not None:
            rec = hashes[prev]
            if case == 4 and st == "Goal": rec = "0123456789ab"            # a commit origin does not hold
            if case == 5 and st == "Goal": rec = side                      # a real commit of another branch
            if case == 8 and st == "Goal": rec = base                      # an earlier commit: an ancestor that does not hold O_Scope
            if case == 10 and st == "Goal": rec = "release 4.8.0"          # a value that is not a commit or a release tag
            if case == 11 and st == "Goal": rec = "   "                    # a blank value
            if case == 12 and st == "Goal": rec = hashes[prev] + " oops"   # the right hash followed by extra text
            if case == 13 and st == "Goal": rec = "backlog-roadmap-framework-v4.8.0 junk"   # a release tag followed by extra text
            if case == 14 and st == "Goal": rec = "backlog-roadmap-framework-vX"            # a malformed release tag
            pieces.append(f"ex:O_{prev} backlog:closedAtCommit \"{rec}\" .\n")
        open(reg, "w").write(text + "".join(pieces)); git(work, "add", "-A"); git(work, "commit", "-q", "-m", f"stage {st}")
        hashes[st] = git(work, "rev-parse", "--short=12", "HEAD")
    if case != 3:
        pieces.append(STORY)
    pieces.append(f"ex:O_Backlog backlog:closedAtCommit \"{hashes['Backlog']}\" .\n")
    open(reg, "w").write(text + "".join(pieces)); git(work, "add", "-A"); git(work, "commit", "-q", "-m", "story and last commit")
    return text + "".join(pieces)

def build(case):
    t = tempfile.mkdtemp(prefix="witness_branch_")
    origin = os.path.join(t, "origin.git"); work = os.path.join(t, "work")
    git(t, "init", "-q", "--bare", origin); git(t, "clone", "-q", origin, work)
    d = os.path.join(work, "pkg", "01-ontologies"); os.makedirs(d); reg = os.path.join(d, "reg_v1_0_0.ttl")
    open(os.path.join(work, "README"), "w").write("main\n")
    git(work, "add", "-A"); git(work, "commit", "-q", "-m", "base"); git(work, "branch", "-M", "main"); git(work, "push", "-q", "origin", "main")
    base = git(work, "rev-parse", "--short=12", "HEAD")
    git(work, "checkout", "-q", "-b", "side"); open(os.path.join(work, "SIDE"), "w").write("side\n")
    git(work, "add", "-A"); git(work, "commit", "-q", "-m", "side"); git(work, "push", "-q", "origin", "side")
    side = git(work, "rev-parse", "--short=12", "HEAD"); git(work, "checkout", "-q", "main")
    branch_line = "" if case == 1 else "ex:L backlog:witnessedOnBranch \"%s\" .\n" % ("wip/missing" if case == 2 else "wip/x")
    text = HEAD + branch_line
    if case == 2:
        # the main line itself holds the chain in order, one stage per commit; the named branch was never pushed
        chain(work, reg, text, case, base, side); git(work, "push", "-q", "origin", "main")
        return t, reg, work
    git(work, "checkout", "-q", "-b", "wip/x")
    final = chain(work, reg, text, case, base, side)
    git(work, "push", "-q", "origin", "wip/x")
    if case == 9:
        git(work, "push", "-q", "origin", "side:refs/heads/a/refs/heads/wip/x")   # a branch whose name ends like the real one
    # the batch release: a fresh clone of origin's main line receives the finished register in one commit
    rel = os.path.join(t, "release"); git(t, "clone", "-q", "-b", "main", origin, rel)
    rd = os.path.join(rel, "pkg", "01-ontologies"); os.makedirs(rd)
    open(os.path.join(rd, "reg_v1_0_0.ttl"), "w").write(final)
    git(rel, "add", "-A"); git(rel, "commit", "-q", "-m", "batch release"); git(rel, "push", "-q", "origin", "main")
    git(rel, "fetch", "-q", "origin", "+refs/heads/wip/x:refs/remotes/origin/wip/x")   # the clone that is checked holds the branch
    if case == 6:
        git(t, "--git-dir", origin, "update-ref", "-d", "refs/heads/wip/x")            # deleted on origin after it was fetched
    if case == 7:
        git(rel, "remote", "set-url", "origin", os.path.join(t, "gone.git"))             # origin cannot be reached
    return t, os.path.join(rd, "reg_v1_0_0.ttl"), rel

def verdict(chk, reg):
    r = subprocess.run([sys.executable, "-I", chk, reg], capture_output=True, text=True, timeout=600)
    m = re.search(r"^\s+L\s+([A-Z_]+)", r.stdout, re.M)
    return (m.group(1) if m else "NONE"), r.returncode, r.stdout + r.stderr

CASES = [(0, "ORDERED", "witnessed on", "names its branch"),
         (1, "!ORDERED", None, "names no branch: the main line holds one commit"),
         (2, "WITNESS_BROKEN", "not held by origin", "names a branch never pushed, main line in order"),
         (3, "BYPASS", None, "story before the backlog stage on the branch"),
         (4, "WITNESS_BROKEN", "does not hold", "records a commit origin does not hold"),
         (5, "WITNESS_BROKEN", "not an ancestor", "records a real commit of another branch"),
         (6, "WITNESS_BROKEN", "not held by origin", "branch fetched, then deleted on origin"),
         (7, "WITNESS_BROKEN", "cannot be reached", "origin cannot be reached"),
         (8, "WITNESS_BROKEN", "does not hold it", "records an earlier commit that does not hold the output"),
         (9, "ORDERED", "witnessed on", "origin also holds a branch whose name ends like the real one"),
         (10, "WITNESS_BROKEN", "not a commit hash or a release tag", "records a value that is not a commit or a release"),
         (11, "WITNESS_BROKEN", "not a commit hash or a release tag", "records a blank value"),
         (12, "WITNESS_BROKEN", "not a commit hash or a release tag", "records a hash followed by extra text"),
         (13, "WITNESS_BROKEN", "not a commit hash or a release tag", "records a release tag followed by extra text"),
         (14, "WITNESS_BROKEN", "not a commit hash or a release tag", "records a malformed release tag")]

def run_cases(chk, quiet=False):
    fails = 0
    for case, want, reason, label in CASES:
        t, reg, _ = build(case)
        try:
            v, rc, so = verdict(chk, reg)
            good = (v != "ORDERED" and v != "NONE") if want == "!ORDERED" else v == want
            if reason is not None and reason not in so:
                good = False
            if not quiet:
                print(f"  case {case} {'PASS' if good else 'FAIL'}: {label} -> {want}{' / ' + repr(reason) if reason else ''}; read {v} (exit {rc})")
                if not good:
                    print("    " + "\n    ".join(so.splitlines()[-8:]))
            fails += 0 if good else 1
        finally:
            shutil.rmtree(t, ignore_errors=True)
    return fails

MUTANTS = [("A: the per-lineage branch witness switched off", "        if wb is not None and isinstance(witness, GitWitness):", "        if False:"),
           ("B: a recorded commit need not hold its output", "                        if r_.returncode == 1:", "                        if False:"),
           ("C: the first line of origin's answer is read", "    line = next((l for l in ls.stdout.splitlines() if len(l.split()) == 2 and l.split()[1] == want), \"\")", "    line = ls.stdout.strip().split(\"\\n\")[0] if ls.stdout.strip() else \"\""),
           ("D: a recorded value of any form is accepted", "            if raw is not None and isinstance(witness, GitWitness) and not well_formed:", "            if False:")]

fails = run_cases(CHK)
caught = 0
src = open(CHK, encoding="utf-8").read()
for label, a, b in MUTANTS:
    if src.count(a) != 1:
        print(f"  mutant {label}: FAIL, the line to mutate is not found once in the checker"); continue
    md = tempfile.mkdtemp(prefix="witness_mutant_")
    try:
        mp = os.path.join(md, os.path.basename(CHK)); open(mp, "w").write(src.replace(a, b))
        mf = run_cases(mp, quiet=True)
        ok = mf > 0; caught += ok
        print(f"  mutant {label}: {'caught' if ok else 'NOT CAUGHT'} ({mf} case(s) fail)")
    finally:
        shutil.rmtree(md, ignore_errors=True)
good = fails == 0 and caught == len(MUTANTS)
print(f"VERDICT     : {'PASS' if good else 'FAIL'} -- {len(CASES) - fails} of {len(CASES)} cases as expected, {caught} of {len(MUTANTS)} mutants caught")
sys.exit(0 if good else 1)
