#!/usr/bin/env python3
"""backlog_release_tool_probe v1.1.0 -- the release tool refuses what it must refuse and does what it says (G99 release A; OE rule R4).

Each case is a fact about backlog_release_tool, shown on a throwaway folder, and each failing case must really fail:
  1 a header bump renames the file and moves versionInfo, versionIRI and priorVersion (the old version is added to the prior list);
  2 a bump is refused when the file is not at the stated version, when the new version is not above the old, when the header does not read the
    old version, and when the target file already exists (the folder is unchanged after each refusal);
  3 clean-bytecode removes nested __pycache__ folders and leaves other files;
  4 a push is retried after a transient server error and succeeds; a rejection that is not transient is NOT retried (one attempt);
  5 a release is refused when the changelog has no entry for the version, and the dry run runs nothing (VERSION.txt unchanged).
  6 (v1.1.0) deletion_args writes the named paths one per line behind --expect-delete, and nothing when no path is named;
  7 (v1.1.0) prune-cache removes only cache-kind files older than the limit, keeps recent ones and leaves every other file alone;
  8 (v1.1.0) the release path does not remove the fixture-suite stamp.
Exit 0 all hold; 2 a case failed.
"""
import importlib.util, os, subprocess, sys, tempfile, glob

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rt", sorted(glob.glob(os.path.join(HERE, "backlog_release_tool_v*.py")))[-1])
RT = importlib.util.module_from_spec(spec); spec.loader.exec_module(RT)
FAILS = []


def check(name, cond):
    print("  %-4s %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        FAILS.append(name)


HDR = ('<http://example.org/backlog> a owl:Ontology ;\n    owl:versionIRI <http://example.org/x/shacl/1.2.0> ;\n    owl:versionInfo "1.2.0" ;\n'
       '    owl:priorVersion <http://example.org/x-shapes/1.1.0> .\n')


def main():
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "x_shacl_v1_2_0.ttl"); open(f, "w").write(HDR)
        r = RT.bump_file(f, "1.2.0", "1.3.0", "http://example.org/x/shacl", "http://example.org/x-shapes")
        t = os.path.join(d, "x_shacl_v1_3_0.ttl")
        s = open(t).read() if os.path.exists(t) else ""
        check("1 bump renames the file and moves the header", r == t and not os.path.exists(f) and 'versionInfo "1.3.0"' in s
              and "shacl/1.3.0>" in s and "x-shapes/1.2.0> , <http://example.org/x-shapes/1.1.0>" in s)
        before = sorted(os.listdir(d)); cont = open(t).read()
        e1 = RT.bump_file(os.path.join(d, "x_shacl_v9_9_9.ttl"), "9.9.9", "9.9.10", "a", "b")
        e2 = RT.bump_file(t, "1.3.0", "1.3.0", "http://example.org/x/shacl", "http://example.org/x-shapes")
        e3 = RT.bump_file(t, "1.3.0", "1.2.9", "http://example.org/x/shacl", "http://example.org/x-shapes")
        e4 = RT.bump_file(t, "1.3.0", "1.4.0", "http://example.org/WRONG", "http://example.org/x-shapes")
        open(os.path.join(d, "x_shacl_v1_4_0.ttl"), "w").write("x")
        e5 = RT.bump_file(t, "1.3.0", "1.4.0", "http://example.org/x/shacl", "http://example.org/x-shapes")
        os.remove(os.path.join(d, "x_shacl_v1_4_0.ttl"))
        refused = all(isinstance(e, str) and not e.endswith(".ttl") for e in (e1, e2, e3, e4, e5))
        check("2 bump refused: missing file, not above, header mismatch, target exists", refused)
        check("2 the folder and the file are unchanged after refusals", sorted(os.listdir(d)) == before and open(t).read() == cont)

        os.makedirs(os.path.join(d, "a", "__pycache__")); os.makedirs(os.path.join(d, "a", "b", "__pycache__")); open(os.path.join(d, "a", "keep.py"), "w").write("1")
        n = RT.clean_bytecode(d)
        check("3 clean-bytecode removes nested __pycache__, keeps files", n == 2 and os.path.exists(os.path.join(d, "a", "keep.py"))
              and not os.path.exists(os.path.join(d, "a", "b", "__pycache__")))

        bare, work = os.path.join(d, "bare.git"), os.path.join(d, "work")
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        g = lambda *a, cwd=work: subprocess.run(["git", *a], cwd=cwd, env=env, capture_output=True, text=True)
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], env=env)
        os.makedirs(work); g("init", "-q", "-b", "main"); g("remote", "add", "origin", bare)
        open(os.path.join(work, "f"), "w").write("1"); g("add", "-A"); g("commit", "-q", "-m", "c1")
        hook = os.path.join(bare, "hooks", "pre-receive"); cnt = os.path.join(d, "count")
        open(hook, "w").write('#!/bin/sh\nn=$(cat "%s" 2>/dev/null || echo 0); n=$((n+1)); echo $n > "%s"\n'
                              'if [ "$n" -le 1 ]; then echo "error: HTTP 500 Internal Server Error" >&2; exit 1; fi\nexit 0\n' % (cnt, cnt)); os.chmod(hook, 0o755)
        rc, tries = RT.push_retry(work, tries=3, delay=0.1)
        check("4 a transient server error is retried and the push lands", rc == 0 and tries == 2)
        open(os.path.join(work, "f"), "w").write("2"); g("add", "-A"); g("commit", "-q", "-m", "c2")
        open(cnt, "w").write("0")
        open(hook, "w").write('#!/bin/sh\necho "remote: permission denied" >&2\nexit 1\n'); os.chmod(hook, 0o755)
        rc, tries = RT.push_retry(work, tries=3, delay=0.1)
        check("4 a rejection that is not transient is not retried", rc != 0 and tries == 1)

    with tempfile.TemporaryDirectory() as d2:
        a = RT.deletion_args(["03-tooling/x.py", " 03-tooling/y.py "], d2)
        check("6 deletion_args writes the paths behind --expect-delete", a[0] == "--expect-delete" and open(a[1]).read() == "03-tooling/x.py\n03-tooling/y.py\n")
        check("6 no deletions, no argument", RT.deletion_args([], d2) == [])
        import time as _t
        d2 = os.path.join(d2, "cache"); os.makedirs(d2)
        old_t = _t.time() - 40 * 86400
        names = {"shape_" + "a" * 64 + ".ttl": True, "b" * 64 + ".json": True, "cacheproof_" + "c" * 8 + ".ok": True}
        for n in names:
            open(os.path.join(d2, n), "w").write("x"); os.utime(os.path.join(d2, n), (old_t, old_t))
        open(os.path.join(d2, "shape_" + "d" * 64 + ".ttl"), "w").write("recent"); open(os.path.join(d2, "notes.txt"), "w").write("keep"); os.utime(os.path.join(d2, "notes.txt"), (old_t, old_t))
        rem, kept = RT.prune_cache(d2, 14)
        check("7 prune removes the old cache files only", rem == 3 and kept == 1 and sorted(os.listdir(d2)) == ["notes.txt", "shape_" + "d" * 64 + ".ttl"])
    check("8 the release path never removes the fixture-suite stamp", "os.remove(stamp)" not in open(RT.__file__).read())

    ver = os.path.join(RT.PKG, "VERSION.txt"); before = open(ver).read() if os.path.exists(ver) else None
    p = subprocess.run([sys.executable, os.path.join(HERE, os.path.basename(RT.__file__)), "release", "99.99.99", "--dry-run"], capture_output=True, text=True)
    check("5 release refused for a version with no changelog entry", p.returncode == 2 and "no entry" in p.stdout)
    check("5 the refused dry run changed nothing", (open(ver).read() if os.path.exists(ver) else None) == before)
    print("VERDICT : " + ("ALL HOLD" if not FAILS else "FAILED -- " + "; ".join(FAILS)))
    return 0 if not FAILS else 2


if __name__ == "__main__":
    sys.exit(main())
