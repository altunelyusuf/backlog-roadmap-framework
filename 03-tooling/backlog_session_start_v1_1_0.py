#!/usr/bin/env python3
"""backlog_session_start v1.1.0 -- the session-start ceremony in one command that prints a few lines (G195).

For the governing disciplines it does what the Owner asks at every session start, from the repositories and never from memory: fetches origin, lists the discipline
files of the folder as origin holds them, picks the highest version comparing the three numbers as integers, takes the bytes of that file from origin, and says whether
they are identical to the copy last read in full (then nothing needs reading again), changed (it prints the difference, which is all that needs reading), or never read
(read the whole file). It also runs the OE session ceremony and prints its verdict and any failing line. It reads git; it does not reach the GitHub pages.

v1.1.0 (Lineage 30, review of box 1): (1) the record of the copy last read is written only by `--ack`, after the difference has been read, so a second run cannot say UNCHANGED for a discipline that changed; a CHANGED or NEVER READ discipline makes the start NOT READY until it is acknowledged. (2) The ceremony counts only when its exit code is 0, its last verdict line is PROCEED (the word alone) and no line of its output says REFUSE (also REFUSED) or NOT; (3) `--ack` is accepted only for a version an earlier run without it showed; origin is the last fetched state of origin/main; `--ceremony SCRIPT` names a script (tests). 

Usage: backlog_session_start.py [--public DIR] [--mono DIR] [--package SLUG] [--state DIR] [--no-ceremony] [--ceremony SCRIPT] [--ack]
Exit 0 when both disciplines are resolved and read (unchanged, or acknowledged with --ack after reading), nothing is behind origin and the ceremony says PROCEED; 1 otherwise."""
import difflib, glob, hashlib, json, os, re, subprocess, sys, time

def sh(args, cwd, timeout=300):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr

def highest(names, pattern):
    best = None
    for n in names:
        m = re.fullmatch(pattern, os.path.basename(n))
        if m:
            key = tuple(int(x) for x in m.groups())
            if best is None or key > best[0]:
                best = (key, n)
    return best[1] if best else None

def resolve(repo, folder, pattern):
    """The highest-versioned file of the folder on origin/main, its bytes and their digest."""
    rc, out, err = sh(["git", "ls-tree", "--name-only", "origin/main", folder.rstrip("/") + "/"], repo)
    if rc != 0:
        return None, None, "cannot list %s on origin: %s" % (folder, err.strip()[:120])
    name = highest(out.split(), pattern)
    if not name:
        return None, None, "no file of the pattern in %s" % folder
    r = subprocess.run(["git", "show", "origin/main:" + name], cwd=repo, capture_output=True)
    if r.returncode != 0 or not r.stdout:
        return None, None, "cannot read %s from origin" % name
    return name, r.stdout, None

def judge(kind, name, data, state):
    """READ / UNCHANGED / CHANGED against the copy last read in full."""
    sha = hashlib.sha256(data).hexdigest()
    os.makedirs(state, exist_ok=True)
    meta_p = os.path.join(state, kind + ".json")
    copy_p = os.path.join(state, kind + ".md")
    old = json.load(open(meta_p)) if os.path.exists(meta_p) and os.path.exists(copy_p) else None     # a record without its copy is no record
    lines = []
    if old and old["sha"] == sha:
        lines.append("%s: %s  sha %s  UNCHANGED since %s (bytes identical to the copy read in full)" % (kind, os.path.basename(name), sha[:12], old["at"]))
    elif old:
        lines.append("%s: %s  sha %s  CHANGED (was %s, sha %s) -- read the difference:" % (kind, os.path.basename(name), sha[:12], old["name"], old["sha"][:12]))
        a = open(copy_p, encoding="utf-8", errors="replace").read().splitlines()
        b = data.decode("utf-8", "replace").splitlines()
        d = [l for l in difflib.unified_diff(a, b, "last read", "now", lineterm="", n=0)]
        lines += ["    " + l[:200] for l in d[:80]] + (["    ... %d more lines of difference" % (len(d) - 80)] if len(d) > 80 else [])
    else:
        lines.append("%s: %s  sha %s  NEVER READ here -- read it in full (%d lines)" % (kind, os.path.basename(name), sha[:12], data.count(b"\n")))
    return sha, lines, meta_p, copy_p, old

def main(argv):
    o = lambda k, d: argv[argv.index(k) + 1] if k in argv else d
    public = o("--public", "/home/claude/backlog-roadmap-framework")
    mono = o("--mono", "/home/claude/ontologies")
    package = o("--package", "backlog-roadmap-framework")
    state = o("--state", "/home/claude/.session_state")
    ok = True
    for label, repo in (("public", public), ("monorepo", mono)):
        rc, _, err = sh(["git", "fetch", "-q", "origin", "main"], repo, 300)
        if rc != 0:
            print("%s: cannot fetch origin (%s)" % (label, err.strip()[:100])); ok = False; continue
        rc, out, _ = sh(["git", "rev-list", "--count", "HEAD..origin/main"], repo)
        behind = int(out.strip() or 0)
        print("%s: %d behind origin/main%s" % (label, behind, "" if behind == 0 else "  (BEHIND -- update before acting)"))
        ok = ok and behind == 0
    todo = (("lineage discipline", public, "04-documentation", r"LINEAGE_OPERATING_DISCIPLINE_v(\d+)_(\d+)_(\d+)\.md", "lineage"),
            ("OE discipline", mono, "oe-method/04-documentation", r"OE_Operating_Discipline_v(\d+)_(\d+)_(\d+)\.md", "oe"))
    for label, repo, folder, pat, kind in todo:
        name, data, err = resolve(repo, folder, pat)
        if err:
            print("%s: %s" % (label, err)); ok = False; continue
        sha, lines, meta_p, copy_p, old = judge(label, name, data, state)
        print("\n".join(lines))
        if old is None or old["sha"] != sha:
            pend_p = os.path.join(state, kind + ".shown")
            shown = open(pend_p).read().strip() if os.path.exists(pend_p) else ""
            if "--ack" in argv and shown == sha:
                open(copy_p, "wb").write(data)
                json.dump({"name": os.path.basename(name), "sha": sha, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, open(meta_p, "w"))
                print("%s: acknowledged as read in full" % label)
            else:
                if "--ack" in argv:
                    print("%s: --ack refused: this version was not shown by an earlier run; run without --ack, read it, then acknowledge" % label)
                else:
                    open(pend_p, "w").write(sha)
                    print("%s: read it, then run again with --ack" % label)
                ok = False
    if "--no-ceremony" not in argv:
        scripts = [o("--ceremony", None)] if "--ceremony" in argv else sorted(glob.glob(os.path.join(mono, "repo-tooling", "oe_ceremony_v*.sh")), key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]] if re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p) else [0])
        if not scripts:
            print("ceremony: no oe_ceremony script found"); ok = False
        else:
            rc, out, err = sh(["bash", scripts[-1], package], mono, 900)
            keep = [l for l in (out + err).splitlines() if "VERDICT" in l or re.search(r"\b(FAIL\w*|REFUSE\w*|NEW|BEHIND|differs)\b", l)]
            print("ceremony (%s): %s" % (os.path.basename(scripts[-1]), "\n    ".join(keep[-6:]) or "no verdict line"))
            verd = [l for l in keep if l.strip().startswith("VERDICT")]
            good = rc == 0 and bool(verd) and re.match(r"VERDICT:\s+PROCEED(\s|$)", verd[-1].strip()) is not None and not any(re.search(r"\bREFUSE\w*\b|\bNOT\b", l) for l in keep)
            if not good:
                print("ceremony: does not say PROCEED cleanly (exit %d)" % rc)
            ok = ok and good
    print("SESSION START: %s" % ("READY" if ok else "NOT READY"))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
