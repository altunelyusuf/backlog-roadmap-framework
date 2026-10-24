#!/usr/bin/env python3
"""backlog_release_tool v1.4.0 -- the release steps a session used to do by hand, as one tested tool (G99 release A; OE rule R4).

Subcommands (each prints what it did and exits non-zero on any refusal):
  bump-data NEWVER                      rename the package data file to the new version and move its header (versionInfo, versionIRI, priorVersion)
  bump DIR PREFIX OLD NEW PRIORBASE VERSIONBASE
                                        the same for any versioned Turtle file, e.g. 02-shacl-safeguards backlog_shacl 1.151.0 1.152.0
                                        http://example.org/backlog-shapes http://example.org/backlog/shacl
  clean-bytecode [DIR]                  remove every __pycache__ (a stowaway the publisher's manifest check refuses)
  push-retry REPO_DIR [--tries N] [--delay S]
                                        git push origin HEAD:main, retried when the remote answers with a server error (a transient HTTP 5xx); a
                                        rejection that is not transient (non-fast-forward, permission) is NOT retried
  release VERSION [--dry-run] [--step-timeout S] [--delete PATH ...]
                                        the whole path for a version whose changelog entry is already written: backup, VERSION.txt, manifest,
                                        gate, public copy and its push, the publisher, then the tag check. Every step is time-limited and prints its
                                        duration; --dry-run prints the plan and the refusals it already knows (missing changelog entry) and runs nothing
  prune-cache [DIR] [--days N] [--legacy]          remove cache files (shape_*.ttl, memo *.json, stamps) older than N days (default 14) from the validation cache; they are rebuilt on demand
  republish VERSION                     only the publisher and the tag check (after a transient failure of the public push)
v1.4.0 (G151): `preflight VERSION` and the start of `release` run, in seconds, the refusals that used to come after a 25-minute gate: the changelog entry, an inbox item that arrived on origin and is not in the working tree, the release-item accounting (an item moved, or a changelog "Unplanned work:" line), and Gate K. The inbox is looked at again just before the publisher; on an arrival the release stops there, names the files and says to disposition them and run `republish`, which now rebuilds the manifest first, so the gate is not run again for a change that touches only the inbox.
v1.3.5 (G138): the release path creates both stamp files (`ensure_stamps`: .fixture-suite-stamp and .clause-proof-stamp) when absent, so a release no longer needs them touched by hand beforehand.
v1.3.4 (G128): after the proof stamps the measured probe inputs are exported to 06-package-provenance/PROBE_INPUTS.json; `public_keep` (the files the public copy keeps) is a function of its own and has a test.
v1.3.3 (G126): `release --cold` runs every gate step (BACKLOG_COLD=1); after a passing gate the proof stamps are exported to 06-package-provenance/PROOF_STAMPS.json and the manifest is rebuilt; prune-cache --legacy removes the one-file-per-shape cache and prunes the shape bundles.
v1.3.2 (G124): the public copy keeps its own README.md, DISTRIBUTION.md and LICENSE, but 04-documentation/README.md is taken from the derivation whenever the derivation has one, so a changed README no longer needs a hand fix in the public copy.
v1.3.1 (G115): a gate line that only REPORTS a zero count of failures ("declaration FAILED : 0", printed by the clause proof whenever it runs rather than being skipped) is no longer read as a failure; before, the first release that changed a shape stopped at that line. Real failures (a non-zero count, a VERDICT: FAIL, an ABORT) still stop it. The public copy step keeps README.md, DISTRIBUTION.md, LICENSE and 04-documentation/README.md only when the public copy has them (it stopped with FileNotFoundError on a public copy that holds none).
v1.3.0: prune-cache also removes the Merkle-cache per-fixture and per-probe stamp files (stamp_*.key, G99 release E -- they live in the same off-package memo directory, so retiring a removed fixture or probe's stamp needs no gitignore or manifest change).
v1.2.0: prune-cache also removes the archived-digest result files (archdigest_*.json); the gate now runs it by itself at its start (entries unused for 14 days go; every entry is rebuilt on demand).
v1.1.0: the fixture-suite stamp is KEPT (v1.0.0 deleted it, so the publisher's own gate re-run redid the whole fixture suite cold, about 9 minutes; the stamp is git-ignored and
manifest-exempt, and the gate keys it on every input including the validator); bytecode is cleaned before AND after the publisher; --delete PATH (repeatable) names a
file the release removes, passed to the publisher as --expect-delete; prune-cache removes validation cache files older than N days.
Nothing here loosens a check: the gate and the publisher run unchanged; the tool only removes the hand-work around them.
Environment: BRSF_PUBCOPY (the public copy's clone), BRSF_PUBLISHER_DIR (where oe_publish_v*.sh lives), BRSF_WORK (scratch), GH_TOKEN, OE_SESSION,
RELEASE_COMMIT_TRAILER (text appended to the public-copy commit message).
"""
import glob, os, re, shutil, subprocess, sys, tarfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
REPO = os.path.dirname(PKG)
PKGNAME = os.path.basename(PKG)


def semver_key(p):
    m = re.search(r"_v(\d+)_(\d+)_(\d+)\.[a-z]+$", p)
    return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)


def newest(pattern):
    c = sorted(glob.glob(pattern), key=semver_key)
    return c[-1] if c else None


def die(msg, code=2):
    print("REFUSED: " + msg); sys.exit(code)


# ---------------------------------------------------------------- header bumps
def bump_file(path, old, new, version_base, prior_base):
    """Rename PATH from version OLD to NEW and move its header. Refuses (returns an error text) when the file is not at OLD."""
    base = os.path.basename(path)
    otok, ntok = old.replace(".", "_"), new.replace(".", "_")
    if "_v" + otok + "." not in base:
        return "the file name %s does not carry version %s" % (base, old)
    if not re.fullmatch(r"\d+\.\d+\.\d+", new) or semver_key("x_v%s.ttl" % ntok) <= semver_key("x_v%s.ttl" % otok):
        return "the new version %s is not above %s" % (new, old)
    if not os.path.isfile(path):
        return "%s does not exist" % base
    s = open(path, encoding="utf-8").read()
    if 'owl:versionInfo "%s"' % old not in s or "owl:versionIRI <%s/%s>" % (version_base, old) not in s:
        return "the header of %s does not read version %s with versionIRI %s/%s" % (base, old, version_base, old)
    s = s.replace("owl:versionIRI <%s/%s>" % (version_base, old), "owl:versionIRI <%s/%s>" % (version_base, new), 1)
    s = s.replace('owl:versionInfo "%s"' % old, 'owl:versionInfo "%s"' % new, 1)
    if "owl:priorVersion <" not in s:
        return "the header has no owl:priorVersion to extend"
    s = s.replace("owl:priorVersion <", "owl:priorVersion <%s/%s> , <" % (prior_base, old), 1)
    target = os.path.join(os.path.dirname(path), base.replace("_v" + otok + ".", "_v" + ntok + ".", 1))
    if os.path.exists(target):
        return "%s already exists" % os.path.basename(target)
    open(path, "w", encoding="utf-8").write(s)
    os.rename(path, target)
    return target


def cmd_bump_data(args):
    if len(args) != 1:
        die("usage: bump-data NEWVER")
    cur = newest(os.path.join(PKG, "01-ontologies", "backlog_abox_v*.ttl"))
    old = ".".join(re.search(r"_v(\d+)_(\d+)_(\d+)\.ttl$", cur).groups())
    r = bump_file(cur, old, args[0], "http://example.org/backlog/abox", "http://example.org/backlog/abox")
    if not r.endswith(".ttl"):
        die(r)
    print("bumped %s -> %s" % (os.path.basename(cur), os.path.basename(r)))


def cmd_bump(args):
    if len(args) != 6:
        die("usage: bump DIR PREFIX OLD NEW PRIORBASE VERSIONBASE")
    d, prefix, old, new, prior, vbase = args
    d = d if os.path.isabs(d) else os.path.join(PKG, d)
    r = bump_file(os.path.join(d, "%s_v%s.ttl" % (prefix, old.replace(".", "_"))), old, new, vbase, prior)
    if not r.endswith(".ttl"):
        die(r)
    print("bumped ->", os.path.basename(r))


# ---------------------------------------------------------------- bytecode, push
def public_keep(pd, pubcopy):
    """The files the public copy keeps from its own previous state when the derived distribution is copied over it (v1.3.4 gives this its own test).
    v1.3.2 (G124): 04-documentation/README.md is DERIVED, so the derived one wins when the derivation produced it; the public copy's older one was kept and then
    failed the drift check. The root README, DISTRIBUTION and LICENSE are the public copy's own and are always kept."""
    keep = {}
    derived = os.path.join("04-documentation", "README.md")
    for f in ("README.md", "DISTRIBUTION.md", "LICENSE", derived):
        if f == derived and os.path.exists(os.path.join(pd, f)):
            continue
        if os.path.exists(os.path.join(pubcopy, f)):
            keep[f] = open(os.path.join(pubcopy, f), "rb").read()
    return keep


def ensure_stamps(pkg):
    """v1.3.5 (G138): both stamp files exist (empty when new); an existing one is left as it is. -> the names created."""
    made = []
    for n in (".fixture-suite-stamp", ".clause-proof-stamp"):
        f = os.path.join(pkg, n)
        if not os.path.exists(f):
            open(f, "w").close(); made.append(n)
    return made


def clean_bytecode(root):
    n = 0
    for dp, dn, _ in os.walk(root):
        for d in list(dn):
            if d == "__pycache__":
                shutil.rmtree(os.path.join(dp, d), ignore_errors=True); dn.remove(d); n += 1
    return n


TRANSIENT = re.compile(r"HTTP (5\d\d)|returned error: 5\d\d|Internal Server Error|Bad Gateway|Service Unavailable|Gateway Time-?out|"
                       r"unexpected disconnect|connection reset|early EOF|RPC failed", re.I)


def push_retry(repo, tries=4, delay=15.0):
    last = ""
    for i in range(1, tries + 1):
        p = subprocess.run(["git", "push", "-q", "origin", "HEAD:main"], cwd=repo, capture_output=True, text=True)
        if p.returncode == 0:
            return 0, i
        last = p.stderr + p.stdout
        if not TRANSIENT.search(last):
            print("push refused, not transient:\n" + last[-400:]); return p.returncode, i
        print("push failed with a transient server error (attempt %d of %d); retrying" % (i, tries))
        time.sleep(delay)
    print("push still failing after %d attempts:\n%s" % (tries, last[-400:])); return 1, tries


def cmd_push_retry(args):
    tries, delay, pos, i = 4, 15.0, [], 0
    while i < len(args):
        if args[i] == "--tries":
            tries = int(args[i + 1]); i += 2
        elif args[i] == "--delay":
            delay = float(args[i + 1]); i += 2
        else:
            pos.append(args[i]); i += 1
    if len(pos) != 1:
        die("usage: push-retry REPO_DIR [--tries N] [--delay S]")
    rc, n = push_retry(pos[0], tries, delay)
    print("pushed on attempt %d" % n if rc == 0 else "NOT PUSHED")
    sys.exit(rc)


# ---------------------------------------------------------------- release path
def changelog_entry_ok(version):
    cl = newest(os.path.join(PKG, "04-documentation", "CHANGELOG_v*.md"))
    if not cl:
        return None, "no CHANGELOG found"
    head = open(cl, encoding="utf-8").read()
    if not re.search(r"^#+\s*v?%s\b" % re.escape(version), head, re.M):
        return cl, "the changelog %s has no entry headed v%s" % (os.path.basename(cl), version)
    return cl, None


def inbox_arrivals():
    """Pending inbox files that are on origin/main and not in the working tree (G151). A handover that lands during a release makes the publisher refuse it whole."""
    rel = os.path.relpath(PKG, REPO) + "/07-handover-inbox/pending/"
    subprocess.run(["git", "fetch", "-q", "origin"], cwd=REPO, capture_output=True)
    r = subprocess.run(["git", "ls-tree", "-r", "--name-only", "origin/main", rel], cwd=REPO, capture_output=True, text=True)
    def known(f):  # already here, in pending or dispositioned into accepted/rejected/deferred
        base = os.path.dirname(os.path.dirname(os.path.join(REPO, f)))
        return any(os.path.exists(os.path.join(base, d, os.path.basename(f))) for d in ("pending", "accepted", "rejected", "deferred"))
    return sorted(f for f in r.stdout.split() if not f.endswith("README.md") and not known(f))


def preflight(v):
    """Returns the list of refusals found in seconds (empty = go). Nothing here replaces the gate; it only asks the cheap questions first."""
    bad = []
    cl, err = changelog_entry_ok(v)
    if err:
        bad.append(err)
    arr = inbox_arrivals()
    if arr:
        bad.append("handover(s) on origin not in the working tree, disposition them first: " + ", ".join(os.path.basename(a) for a in arr))
    ric = newest(os.path.join(HERE, "backlog_release_item_check_v*.py"))
    tag = subprocess.run(["git", "tag", "--list", PKGNAME + "-v*"], cwd=REPO, capture_output=True, text=True).stdout.split()
    tag = sorted(tag, key=lambda t: [int(x) for x in re.findall(r"\d+", t.split("-v")[-1])])[-1:] 
    if ric and tag:
        vpath = os.path.join(PKG, "VERSION.txt"); old = open(vpath).read() if os.path.exists(vpath) else None
        open(vpath, "w").write(v + "\n")
        try:
            r = subprocess.run([sys.executable, ric, PKG, tag[0], "--repo-root", REPO, "--package-prefix", os.path.relpath(PKG, REPO) + "/"], capture_output=True, text=True)
        finally:
            if old is not None: open(vpath, "w").write(old)
        if r.returncode != 0:
            bad.append("release-item accounting: " + (r.stdout.strip().splitlines() or ["failed"])[-1])
    # the publisher's name guard (BP-D7), asked first: a published file that keeps its versioned name with changed bytes
    d = subprocess.run(["git", "diff", "--name-status", "--no-renames", "origin/main", "--", PKG], cwd=REPO, capture_output=True, text=True).stdout.splitlines()
    kept = [l.split("\t")[1] for l in d if l.startswith("M\t") and re.search(r"_v\d+_\d+_\d+\.", l)]
    if kept:
        bad.append("a changed file keeps its versioned name (BP-D7), rename it to its next version: " + ", ".join(os.path.basename(k) for k in kept))
    val = newest(os.path.join(HERE, "backlog_validate_v*.py"))
    if val:
        r = subprocess.run([sys.executable, val, "--gate-k"], capture_output=True, text=True)
        if r.returncode != 0:
            bad.append("Gate K: " + (r.stdout.strip().splitlines() or ["failed"])[-1])
    return bad


def cmd_preflight(args):
    if len(args) != 1 or not re.fullmatch(r"\d+\.\d+\.\d+", args[0]):
        die("usage: preflight VERSION")
    bad = preflight(args[0])
    for b in bad:
        print("  REFUSED: " + b)
    print("preflight %s: %s" % (args[0], "GO" if not bad else "STOP (%d)" % len(bad)))
    sys.exit(1 if bad else 0)


class Steps:
    def __init__(self, limit):
        self.limit, self.total = limit, time.time()

    def run(self, name, cmd, limit=None, **kw):
        print("step: %s" % name, flush=True)
        t = time.time()
        try:
            p = subprocess.run(cmd, timeout=limit or self.limit, **kw)
        except subprocess.TimeoutExpired:
            die("step '%s' exceeded its %d s limit (a finding to explain, not a command to run again unchanged)" % (name, limit or self.limit), 4)
        print("  %s: %.0f s" % (name, time.time() - t), flush=True)
        return p


def deletion_args(paths, work):
    """['--expect-delete', FILE] with the package-relative PATHS one per line, or [] when nothing is deleted."""
    if not paths:
        return []
    f = os.path.join(work, "deletions.txt")
    open(f, "w").write("".join(p.strip() + "\n" for p in paths))
    return ["--expect-delete", f]


def prune_cache(cache_dir, days=14.0, now=None, legacy=False):
    """Remove validation cache files not written for DAYS days; returns (removed, kept). Only the cache's own file kinds are touched."""
    now = now or time.time(); removed = kept = 0
    for f in os.listdir(cache_dir):
        if not re.fullmatch(r"(shape_[0-9a-f]+\.ttl|shapes_[0-9a-f]+\.json|[0-9a-f]{64}\.json|(shardproof|cacheproof)_[0-9a-f]+\.ok|archdigest_[0-9a-f]+\.json|stamp_[A-Za-z0-9_.-]+\.key)", f):
            continue
        p = os.path.join(cache_dir, f)
        if (legacy and f.startswith("shape_") and f.endswith(".ttl")) or now - os.path.getmtime(p) > days * 86400:
            os.remove(p); removed += 1
        else:
            kept += 1
    return removed, kept


def cmd_prune(args):
    days, pos, i, legacy = 14.0, [], 0, False
    while i < len(args):
        if args[i] == "--days":
            days = float(args[i + 1]); i += 2
        elif args[i] == "--legacy":
            legacy = True; i += 1
        else:
            pos.append(args[i]); i += 1
    d = pos[0] if pos else os.environ.get("BACKLOG_VALIDATE_MEMO_DIR") or os.path.join(os.environ.get("HOME", "/tmp"), ".backlog_validate_memo")
    if not os.path.isdir(d):
        die("no cache folder at %s" % d)
    r, k = prune_cache(d, days, legacy=legacy)
    print("pruned %s: %d removed, %d kept (older than %g days)" % (d, r, k, days))



def gate_failures(text):
    """The lines of a gate log that mean the gate failed. The drift section is dropped (a pending version always fails it); a line that only reports
    a count of zero failures is not a failure."""
    text = re.sub(r"(?ms)^== Distribution-drift gate.*?(?=^== |\Z)", "", text)
    return [l for l in text.splitlines() if re.search(r"FAILED|VERDICT *: *FAIL|ABORT", l) and not re.search(r"FAILED\s*:\s*0\s*$", l)]


def cmd_release(args, only_publish=False):
    dry, limit, pos, i, deletes = False, None, [], 0, []
    while i < len(args):
        if args[i] == "--delete":
            deletes.append(args[i + 1]); i += 2
        elif args[i] == "--dry-run":
            dry = True; i += 1
        elif args[i] == "--cold":
            os.environ["BACKLOG_COLD"] = "1"; i += 1
        elif args[i] == "--step-timeout":
            limit = int(args[i + 1]); i += 2
        else:
            pos.append(args[i]); i += 1
    if len(pos) != 1 or not re.fullmatch(r"\d+\.\d+\.\d+", pos[0]):
        die("usage: release VERSION [--dry-run] [--cold] [--step-timeout S]")
    v = pos[0]
    work = os.environ.get("BRSF_WORK", "/tmp/brsf_release")
    pubcopy = os.environ.get("BRSF_PUBCOPY", "/home/claude/pubcopy")
    pubdir = os.environ.get("BRSF_PUBLISHER_DIR", os.path.join(REPO, "repo-tooling"))
    publisher = newest(os.path.join(pubdir, "oe_publish_v*.sh"))
    cl, err = (None, None) if only_publish else changelog_entry_ok(v)
    if err:
        die(err)
    gate = newest(os.path.join(HERE, "backlog_gate_v*.sh"))
    plan = ["backup", "VERSION.txt", "manifest", "gate", "public copy", "public push", "publisher", "tag check"]
    if only_publish:
        plan = ["publisher", "tag check"]
    print("release %s of %s: %s" % (v, PKGNAME, " -> ".join(plan)))
    if dry:
        print("dry run: gate=%s publisher=%s pubcopy=%s; nothing run" % (os.path.basename(gate or "MISSING"), os.path.basename(publisher or "MISSING"), pubcopy))
        sys.exit(0 if gate and publisher else 2)
    if not publisher:
        die("no oe_publish_v*.sh in %s (set BRSF_PUBLISHER_DIR)" % pubdir)
    os.makedirs(work, exist_ok=True)
    st = Steps(limit or 600)
    if not only_publish:
        bad = preflight(v)
        if bad:
            die("preflight refuses before the gate: " + " | ".join(bad)[:400], 6)
        print("  preflight: GO")
    P = PKG
    if not only_publish:
        with tarfile.open(os.path.join(work, "pkg_%s.tgz" % v), "w:gz") as tf:
            tf.add(P, arcname=PKGNAME)
        open(os.path.join(P, "VERSION.txt"), "w").write(v + "\n")
        clean_bytecode(P)
        ensure_stamps(P)
        mf = newest(os.path.join(HERE, "build_manifest_v*.py"))
        p = st.run("manifest", [sys.executable, mf], cwd=P, capture_output=True, text=True)
        print("  " + (p.stdout.strip().splitlines() or [""])[-1])
        glog = os.path.join(work, "gate_%s.log" % v)
        with open(glog, "w") as fh:
            st.run("gate (the long step)", ["bash", gate], limit=limit or 3600, cwd=P, stdout=fh, stderr=subprocess.STDOUT)
        text = open(glog, encoding="utf-8", errors="replace").read()
        bad = gate_failures(text)
        if bad:
            die("the gate fails (other than the drift check a pending version always shows): " + bad[0][:160] + "  (log %s)" % glog)
        # v1.3.3 (G126): the gate passed whole, so the keys of the steps it ran or replayed are written into the package, where a later session or a fresh container
        # honours them (backlog_merkle_cache check). The manifest is rebuilt because the package now holds the file.
        merkle = newest(os.path.join(HERE, "backlog_merkle_cache_v*.py"))
        memo = os.environ.get("BACKLOG_VALIDATE_MEMO_DIR") or os.path.join(os.environ.get("HOME", "/tmp"), ".backlog_validate_memo")
        ps = os.path.join(P, "06-package-provenance", "PROOF_STAMPS.json")
        if True:
            p = st.run("proof stamps", [sys.executable, merkle, "export", memo, ps, "package=" + v, "gate=" + os.path.basename(gate)], capture_output=True, text=True)
            print("  " + (p.stdout.strip().splitlines() or [""])[-1])
            pinp = newest(os.path.join(HERE, "backlog_probe_inputs_v*.py"))
            pi = os.path.join(P, "06-package-provenance", "PROBE_INPUTS.json")
            p = st.run("probe inputs", [sys.executable, pinp, "export", memo, pi], capture_output=True, text=True)
            print("  " + (p.stdout.strip().splitlines() or [""])[-1])
            p = st.run("manifest (with the stamps)", [sys.executable, mf], cwd=P, capture_output=True, text=True)
            print("  " + (p.stdout.strip().splitlines() or [""])[-1])
        clean_bytecode(P)
        derive = newest(os.path.join(HERE, "make_public_distribution_v*.py"))
        pd = os.path.join(work, "pd"); shutil.rmtree(pd, ignore_errors=True)
        st.run("public derivation", [sys.executable, derive, P, pd], capture_output=True)
        if not os.path.exists(os.path.join(pd, "VERSION.txt")):
            die("the public derivation produced nothing", 5)
        subprocess.run(["git", "fetch", "-q"], cwd=pubcopy); subprocess.run(["git", "reset", "-q", "--hard", "origin/main"], cwd=pubcopy)
        keep = public_keep(pd, pubcopy)
        for e in os.listdir(pubcopy):
            if e != ".git":
                q = os.path.join(pubcopy, e); shutil.rmtree(q) if os.path.isdir(q) else os.remove(q)
        shutil.copytree(pd, pubcopy, dirs_exist_ok=True)
        for f, b in keep.items():
            open(os.path.join(pubcopy, f), "wb").write(b)
        drift = newest(os.path.join(HERE, "backlog_distribution_drift_check_v*.py"))
        p = st.run("drift check against the new public copy", [sys.executable, drift, P, pubcopy], capture_output=True, text=True)
        print("  " + (p.stdout.strip().splitlines() or [""])[-1])
        msg = "%s v%s public distribution (derived by make_public_distribution)" % (PKGNAME, v)
        if os.environ.get("RELEASE_COMMIT_TRAILER"):
            msg += "\n\n" + os.environ["RELEASE_COMMIT_TRAILER"]
        subprocess.run(["git", "add", "-A"], cwd=pubcopy)
        subprocess.run(["git", "commit", "-q", "-m", msg], cwd=pubcopy)
        rc, n = push_retry(pubcopy)
        if rc:
            die("the public copy could not be pushed (see above); fix the cause, then run: republish %s" % v, 5)
        clean_bytecode(P)
    arr = inbox_arrivals()
    if arr:
        die("handover(s) arrived on origin during the release: %s. Disposition them, then run: republish %s (the gate is not run again for an inbox-only change)" % (", ".join(os.path.basename(a) for a in arr), v), 6)
    if only_publish:
        mf = newest(os.path.join(HERE, "build_manifest_v*.py"))
        st.run("manifest", [sys.executable, mf], cwd=P, capture_output=True, text=True)
    pw = os.path.join(work, "pub"); os.makedirs(pw, exist_ok=True)
    plog = os.path.join(work, "pub_%s.log" % v)
    env = dict(os.environ, OE_SESSION=os.environ.get("OE_SESSION", "brsf-session"))
    clean_bytecode(P)
    cmd = ["bash", publisher, os.environ.get("GH_TOKEN", ""), P, PKGNAME] + deletion_args(deletes, work)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        with open(plog, "w") as fh:
            st.run("publisher", cmd, limit=limit or 3600, cwd=pw, env=env, stdout=fh, stderr=subprocess.STDOUT)
    finally:
        clean_bytecode(P)
    ptext = open(plog, encoding="utf-8", errors="replace").read()
    print("  " + " | ".join(ptext.strip().splitlines()[-3:])[:300])
    if not re.search(r"^published:", ptext, re.M):
        die("NOT PUBLISHED (the working tree is left untouched; log %s)" % plog, 4)
    subprocess.run(["git", "fetch", "-q", "origin"], cwd=REPO); subprocess.run(["git", "reset", "-q", "--hard", "origin/main"], cwd=REPO)
    tag = "refs/tags/%s-v%s" % (PKGNAME, v); seen = ""
    for _ in range(6):
        seen = subprocess.run(["git", "ls-remote", "--tags", "origin", tag], cwd=REPO, capture_output=True, text=True).stdout.strip()
        if seen:
            break
        time.sleep(10)
    print("release %s: published; tag %s; total %.0f s" % (v, "present" if seen else "NOT YET on the remote (the workflow makes it)", time.time() - st.total))


def main(argv):
    if not argv:
        print(__doc__); return 1
    c, a = argv[0], argv[1:]
    if c == "bump-data": cmd_bump_data(a)
    elif c == "bump": cmd_bump(a)
    elif c == "clean-bytecode": print("removed %d __pycache__ folder(s)" % clean_bytecode(a[0] if a else PKG))
    elif c == "push-retry": cmd_push_retry(a)
    elif c == "prune-cache": cmd_prune(a)
    elif c == "preflight": cmd_preflight(a)
    elif c == "release": cmd_release(a)
    elif c == "republish": cmd_release(a, only_publish=True)
    else: print(__doc__); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
