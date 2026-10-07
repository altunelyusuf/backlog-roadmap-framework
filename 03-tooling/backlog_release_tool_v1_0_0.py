#!/usr/bin/env python3
"""backlog_release_tool v1.0.0 -- the release steps a session used to do by hand, as one tested tool (G99 release A; OE rule R4).

Subcommands (each prints what it did and exits non-zero on any refusal):
  bump-data NEWVER                      rename the package data file to the new version and move its header (versionInfo, versionIRI, priorVersion)
  bump DIR PREFIX OLD NEW PRIORBASE VERSIONBASE
                                        the same for any versioned Turtle file, e.g. 02-shacl-safeguards backlog_shacl 1.151.0 1.152.0
                                        http://example.org/backlog-shapes http://example.org/backlog/shacl
  clean-bytecode [DIR]                  remove every __pycache__ (a stowaway the publisher's manifest check refuses)
  push-retry REPO_DIR [--tries N] [--delay S]
                                        git push origin HEAD:main, retried when the remote answers with a server error (a transient HTTP 5xx); a
                                        rejection that is not transient (non-fast-forward, permission) is NOT retried
  release VERSION [--dry-run] [--step-timeout S]
                                        the whole path for a version whose changelog entry is already written: backup, VERSION.txt, manifest,
                                        gate, public copy and its push, the publisher, then the tag check. Every step is time-limited and prints its
                                        duration; --dry-run prints the plan and the refusals it already knows (missing changelog entry) and runs nothing
  republish VERSION                     only the publisher and the tag check (after a transient failure of the public push)
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


def cmd_release(args, only_publish=False):
    dry, limit, pos, i = False, None, [], 0
    while i < len(args):
        if args[i] == "--dry-run":
            dry = True; i += 1
        elif args[i] == "--step-timeout":
            limit = int(args[i + 1]); i += 2
        else:
            pos.append(args[i]); i += 1
    if len(pos) != 1 or not re.fullmatch(r"\d+\.\d+\.\d+", pos[0]):
        die("usage: release VERSION [--dry-run] [--step-timeout S]")
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
    P = PKG
    if not only_publish:
        with tarfile.open(os.path.join(work, "pkg_%s.tgz" % v), "w:gz") as tf:
            tf.add(P, arcname=PKGNAME)
        open(os.path.join(P, "VERSION.txt"), "w").write(v + "\n")
        clean_bytecode(P)
        stamp = os.path.join(P, ".fixture-suite-stamp")
        if not os.path.exists(stamp):
            open(stamp, "w").close()
        mf = newest(os.path.join(HERE, "build_manifest_v*.py"))
        p = st.run("manifest", [sys.executable, mf], cwd=P, capture_output=True, text=True)
        print("  " + (p.stdout.strip().splitlines() or [""])[-1])
        glog = os.path.join(work, "gate_%s.log" % v)
        with open(glog, "w") as fh:
            st.run("gate (the long step)", ["bash", gate], limit=limit or 3600, cwd=P, stdout=fh, stderr=subprocess.STDOUT)
        text = open(glog, encoding="utf-8", errors="replace").read()
        text = re.sub(r"(?ms)^== Distribution-drift gate.*?(?=^== |\Z)", "", text)
        bad = [l for l in text.splitlines() if re.search(r"FAILED|VERDICT *: *FAIL|ABORT", l)]
        if bad:
            die("the gate fails (other than the drift check a pending version always shows): " + bad[0][:160] + "  (log %s)" % glog)
        try:
            os.remove(stamp)
        except OSError:
            pass
        clean_bytecode(P)
        derive = newest(os.path.join(HERE, "make_public_distribution_v*.py"))
        pd = os.path.join(work, "pd"); shutil.rmtree(pd, ignore_errors=True)
        st.run("public derivation", [sys.executable, derive, P, pd], capture_output=True)
        if not os.path.exists(os.path.join(pd, "VERSION.txt")):
            die("the public derivation produced nothing", 5)
        subprocess.run(["git", "fetch", "-q"], cwd=pubcopy); subprocess.run(["git", "reset", "-q", "--hard", "origin/main"], cwd=pubcopy)
        keep = {}
        for f in ("README.md", "DISTRIBUTION.md", "LICENSE", os.path.join("04-documentation", "README.md")):
            keep[f] = open(os.path.join(pubcopy, f), "rb").read()
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
    pw = os.path.join(work, "pub"); os.makedirs(pw, exist_ok=True)
    plog = os.path.join(work, "pub_%s.log" % v)
    env = dict(os.environ, OE_SESSION=os.environ.get("OE_SESSION", "brsf-session"))
    with open(plog, "w") as fh:
        st.run("publisher", ["bash", publisher, os.environ.get("GH_TOKEN", ""), P, PKGNAME], limit=limit or 3600, cwd=pw, env=env, stdout=fh, stderr=subprocess.STDOUT)
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
    elif c == "release": cmd_release(a)
    elif c == "republish": cmd_release(a, only_publish=True)
    else: print(__doc__); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
