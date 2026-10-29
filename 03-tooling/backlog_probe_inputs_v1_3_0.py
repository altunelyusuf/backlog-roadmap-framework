#!/usr/bin/env python3
"""backlog_probe_inputs v1.3.0 -- what a probe really reads, measured, and a stamp key built on that (G128).

A proof stamp (G126) skips a step when the SHA of the files the step DECLARES equals the one recorded at its last pass. A probe declares its inputs by hand through
its own `--deps`, and the declaration is a hope: it can name more than the probe reads (the probe then reruns for a change it never sees) or fewer (it is then skipped
for a change it would have judged). This module measures instead. It runs the probe under `strace`, lists every file the probe and the programs it started opened,
looked at or listed inside the package, and keys the stamp on exactly that.

What a record holds, per probe (kept in the session's stamp directory and exported to 06-package-provenance/PROBE_INPUTS.json):
  files   package files the run opened or looked at (their bytes are the key)
  dirs    package directories the run listed (their entry names are the key, so a file added to a directory a probe globbed is noticed)
  absent  package paths the run looked for and did not find (the path must still be absent)
  family  the script directory is listed by Python for every import and by every glob, so its listing is keyed only on the names of the same family as a file the
          probe read (`name_vX_Y_Z.ext`): a new version of a tool the probe reads is noticed, an unrelated new tool is not
A record is USABLE only when the run was clean: strace worked; nothing outside the package was read except the interpreter, libraries, temporary files and the
user's home; no file inside the package was written; no working-directory change; fewer than 25 files read from the script directory (a probe that sweeps the tooling
directory is not derivable). Otherwise the caller keeps the declared inputs, as before.

The key is the SHA over the sorted lines `F:path:sha256`, `D:path:sha256(names)`, `A:path:absent|PRESENT`, `Y:family:sha256(names)`. A record whose probe now reads
something else is not trusted: the key is built from the OLD list, so a changed input changes the key, the probe reruns, and the rerun writes a new record.

v1.3.0: a record names the register file of the release it was measured in, and the file is renamed with every release; the reference key now reads the NEWEST register file, not the recorded path (the recorded path was missing one release later, so every audited probe re-ran: measured in release 1.456.0).

v1.2.0 (gate cost): a probe that carries the line `# register-use: reference-only` reads the register file only through the validator, which keeps the controlled individuals and drops every record of the framework's own register; its key therefore uses the digest of that reference part (and not the file's bytes or its versioned name), so a release that only adds records no longer reruns it. Each such probe was audited: it reads no record of the register.

v1.1.0 (G128): `has` tells the gate whether any record exists, so a probe with none is measured even when its declared stamp holds (otherwise a probe is only ever measured when its declared inputs happen
to change, and an under-declared one stays unsound); an untraced run's record is never exported.

Commands:
  run SCRIPT PKG MEMODIR OUT      run SCRIPT (python) under strace from PKG's script directory, stdout+stderr to OUT, exit with its code; writes the record
  key NAME PKG MEMODIR [REPOFILE] print the key built on the record of NAME (memo first, then REPOFILE); exit 1 and print nothing when there is no usable record
  has NAME MEMODIR [REPOFILE]     exit 0 when a record exists (usable or not) in the session or in REPOFILE, 1 when there is none
  export MEMODIR REPOFILE         write the usable records of MEMODIR to REPOFILE (sorted)
  audit NAME PKG MEMODIR          print the measured files and, for a probe with --deps, the declared ones that were not read and the read ones that were not declared
"""
import hashlib, json, os, re, subprocess, sys, tempfile

SYS_PREFIXES = ("/usr/", "/lib/", "/lib64/", "/bin/", "/sbin/", "/etc/", "/opt/", "/proc/", "/sys/", "/dev/", "/run/", "/var/", "/tmp/", "/root/")
VER = re.compile(r"^(.*)_v\d+_\d+_\d+(\.[^.]+)$")
TRACE = "openat,open,openat2,stat,lstat,newfstatat,statx,access,faccessat,faccessat2,readlink,readlinkat,execve,chdir,fchdir,getdents64,getdents,unlink,unlinkat,rename,renameat,renameat2,mkdir,mkdirat,rmdir,symlink,symlinkat,link,linkat,truncate,chmod,fchmodat,utimensat"
WRITEFLAGS = ("O_WRONLY", "O_RDWR", "O_CREAT", "O_TRUNC", "O_APPEND")
MUTATORS = {"unlink", "unlinkat", "rename", "renameat", "renameat2", "mkdir", "mkdirat", "rmdir", "symlink", "symlinkat", "link", "linkat", "truncate", "chmod", "fchmodat", "utimensat"}
NOFD = {"open", "stat", "lstat", "access", "readlink", "execve", "unlink", "rename", "mkdir", "rmdir", "symlink", "link", "truncate", "chmod"}
LINE = re.compile(r'^(?:\d+\s+)?(\w+)\((.*)\)\s+=\s+(-?\d+)(?:\s+(\w+))?')
STR = re.compile(r'"((?:[^"\\]|\\.)*)"')
FDP = re.compile(r'^(?:AT_FDCWD|\d+)<([^>]*)>')


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _ignored_name(n):
    return n == "__pycache__" or n.endswith(".pyc")


def _tmpdirs():
    t = {"/tmp", "/var/tmp"}
    t.add(os.path.realpath(tempfile.gettempdir()))
    if os.environ.get("TMPDIR"):
        t.add(os.path.realpath(os.environ["TMPDIR"]))
    return tuple(sorted(t))


def _parse(tracefiles, pkg, cwd0):
    """Read the per-process strace files. Returns the record fields and the reasons the run is not clean."""
    pkg = os.path.realpath(pkg)
    files, dirs, absent, written, outside, notes = set(), set(), set(), set(), set(), []
    tmp = _tmpdirs()
    home = os.path.realpath(os.environ.get("HOME", "/root"))
    pathdirs = tuple(sorted({x for d in os.environ.get("PATH", "").split(os.pathsep) if d for x in (os.path.normpath(d), os.path.realpath(d))}))

    def rel_of(p):
        p = os.path.normpath(p)
        if p == pkg:
            return "."
        if p.startswith(pkg + os.sep):
            return os.path.relpath(p, pkg)
        return None

    def classify(p):
        r = rel_of(p)
        if r is not None:
            return r
        if p.startswith(tmp) or p.startswith(home + os.sep) or p == home or p.startswith(SYS_PREFIXES) or os.path.dirname(p) in pathdirs or pkg.startswith(p.rstrip(os.sep) + os.sep):
            return None
        outside.add(p)
        return None

    for tf in tracefiles:
        for line in open(tf, errors="replace"):
            m = LINE.match(line)
            if not m:
                continue
            sc, args, res, err = m.group(1), m.group(2), int(m.group(3)), m.group(4)
            if sc in ("chdir", "fchdir"):
                if res >= 0:
                    notes.append("chdir")
                continue
            if sc in ("getdents64", "getdents"):
                d = FDP.match(args)
                if d and d.group(1).startswith("/"):
                    r = classify(os.path.normpath(d.group(1)))
                    if r is not None and not any(_ignored_name(x) for x in r.split(os.sep)):
                        dirs.add(r)
                continue
            s = STR.search(args)
            if not s:
                continue
            raw = s.group(1).encode().decode("unicode_escape", "ignore") if "\\" in s.group(1) else s.group(1)
            if not raw.startswith("/"):
                fd = FDP.match(args)
                base = fd.group(1) if fd else (cwd0 if sc in NOFD else None)
                if not base or not base.startswith("/"):
                    notes.append("unresolved path " + raw)
                    continue
                raw = os.path.join(base, raw)
            p = os.path.normpath(raw)
            if sc == "execve" and rel_of(p) is None:
                continue
            r = classify(p)
            if r is None:
                continue
            if any(_ignored_name(x) for x in r.split(os.sep)):
                continue
            if sc in MUTATORS:
                if res >= 0:
                    written.add(r)
                continue
            if sc in ("open", "openat", "openat2"):
                if res >= 0 and any(f in args for f in WRITEFLAGS):
                    written.add(r)
                    continue
            if res < 0:
                if err in ("ENOENT", "ENOTDIR"):
                    absent.add(r)
                continue
            files.add(r)
    files -= written
    return files, dirs, absent, written, outside, notes


def _is_dir(pkg, r):
    return os.path.isdir(os.path.join(pkg, r))


def build_record(name, script, pkg, tracefiles, rc, cwd0):
    pkg = os.path.realpath(pkg)
    files, dirs, absent, written, outside, notes = _parse(tracefiles, pkg, cwd0)
    sdir = os.path.relpath(os.path.dirname(os.path.realpath(script)), pkg)
    fam = set()
    in_sdir = [f for f in files if os.path.dirname(f) == sdir]
    for f in in_sdir:
        m = VER.match(os.path.basename(f))
        if m:
            fam.add((m.group(1), m.group(2)))
    dirs.discard(sdir)
    # a package directory that was only looked at is "present", not its content
    plain = sorted(f for f in files if not _is_dir(pkg, f))
    present_dirs = sorted(f for f in files if _is_dir(pkg, f) and f not in dirs)
    why = []
    if outside:
        why.append("read outside the package: " + ", ".join(sorted(outside)[:3]))
    if written:
        why.append("wrote inside the package: " + ", ".join(sorted(written)[:3]))
    if notes:
        why.append(notes[0])
    if len(in_sdir) >= 25:
        why.append("reads %d files of its own directory" % len(in_sdir))
    if not plain:
        why.append("no file read was seen")
    return {"probe": name, "script_dir": sdir, "files": plain, "present_dirs": present_dirs, "dirs": sorted(dirs),
            "absent": sorted(a for a in absent if a not in dirs), "family": sorted("%s|%s" % f for f in fam),
            "usable": not why, "unusable_because": why, "rc": rc}


def _names(pkg, r, fam=None):
    try:
        ns = sorted(n for n in os.listdir(os.path.join(pkg, r)) if not _ignored_name(n))
    except OSError:
        return None
    if fam is not None:
        ns = [n for n in ns if any((lambda m: m and (m.group(1), m.group(2)) == f)(VER.match(n)) for f in fam)]
    return ns


FW_NS = "http://example.org/backlog-framework-register#"
ABOX_RE = re.compile(r"^01-ontologies/backlog_abox_v\d+_\d+_\d+\.ttl$")
REF_MARK = re.compile(r"^# register-use: reference-only\s*$", re.M)


def _reference_only(rec, pkg):
    """True when the probe's own source carries the audited marker (see v1.2.0)."""
    try:
        d = os.path.join(pkg, rec.get("script_dir", "03-tooling"))
        cands = sorted(f for f in os.listdir(d) if re.match(re.escape(rec["probe"]) + r"_v\d+_\d+_\d+\.py$", f))
        key = lambda f: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", f)[0]]
        return bool(cands) and bool(REF_MARK.search(open(os.path.join(d, sorted(cands, key=key)[-1]), encoding="utf-8").read()))
    except Exception:
        return False


def _reference_digest(path):
    """sha256 over the triples of the register file whose subject is not in the framework's own register namespace: exactly what the validator keeps as reference."""
    import rdflib
    g = rdflib.Graph().parse(path, format="turtle")
    lines = sorted(" ".join(t.n3() for t in tr) for tr in g if not (isinstance(tr[0], rdflib.URIRef) and str(tr[0]).startswith(FW_NS)))
    return _sha("\n".join(lines).encode())


def key_of(rec, pkg):
    pkg = os.path.realpath(pkg)
    out = []
    ref = _reference_only(rec, pkg)
    for f in rec["files"]:
        p = os.path.join(pkg, f)
        if ref and ABOX_RE.match(f):
            try:
                d0 = os.path.join(pkg, "01-ontologies")
                cur = sorted((x for x in os.listdir(d0) if re.match(r"^backlog_abox_v\d+_\d+_\d+\.ttl$", x)), key=lambda x: [int(n) for n in re.findall(r"_v(\d+)_(\d+)_(\d+)", x)[0]])[-1]
                out.append("F:01-ontologies/backlog_abox:REFERENCE:%s" % _reference_digest(os.path.join(d0, cur)))
                continue
            except Exception:
                pass
        try:
            out.append("F:%s:%s" % (f, _sha(open(p, "rb").read())))
        except OSError:
            out.append("F:%s:MISSING" % f)
    for d in rec.get("present_dirs", []):
        out.append("P:%s:%s" % (d, "dir" if os.path.isdir(os.path.join(pkg, d)) else "MISSING"))
    for d in rec["dirs"]:
        ns = _names(pkg, d)
        if ref and ns is not None:
            ns = [n for n in ns if not re.match(r"^backlog_abox_v\d+_\d+_\d+\.ttl$", n)]   # the versioned name changes every release
        out.append("D:%s:%s" % (d, "MISSING" if ns is None else _sha("\n".join(ns).encode())))
    for a in rec["absent"]:
        out.append("A:%s:%s" % (a, "PRESENT" if os.path.lexists(os.path.join(pkg, a)) else "absent"))
    fam = [tuple(x.split("|", 1)) for x in rec.get("family", [])]
    if fam:
        ns = _names(pkg, rec["script_dir"], fam)
        out.append("Y:%s:%s" % (rec["script_dir"], "MISSING" if ns is None else _sha("\n".join(ns).encode())))
    return _sha("\n".join(sorted(out)).encode())


def _recfile(memo, name):
    return os.path.join(memo, "inputs_%s.json" % "".join(c if c.isalnum() or c in "-_." else "_" for c in name))


def load(name, memo, repofile=None):
    try:
        return json.load(open(_recfile(memo, name)))
    except Exception:
        pass
    if repofile:
        try:
            return json.load(open(repofile))["probes"].get(name)
        except Exception:
            return None
    return None


def strace_works():
    try:
        return subprocess.run(["strace", "-f", "-qq", "-o", os.devnull, "true"], capture_output=True, timeout=20).returncode == 0
    except Exception:
        return False


def cmd_run(script, pkg, memo, out):
    name = os.path.basename(script)
    name = re.sub(r"_v\d+_\d+_\d+\.py$", "", name)
    os.makedirs(memo, exist_ok=True)
    cwd = os.path.dirname(os.path.realpath(script))
    if os.environ.get("BACKLOG_NO_TRACE") == "1" or not strace_works():
        with open(out, "w") as fh:
            rc = subprocess.call([sys.executable, script], stdout=fh, stderr=subprocess.STDOUT, cwd=cwd)
        # an untraced run says nothing about what was read: the old record must not outlive the run that made it stale
        json.dump({"probe": name, "usable": False, "unusable_because": ["not traced"], "rc": rc, "files": [], "dirs": [], "absent": [], "family": [], "script_dir": "."},
                  open(_recfile(memo, name), "w"), indent=1, sort_keys=True)
        return rc
    td = tempfile.mkdtemp(prefix="trace_")
    base = os.path.join(td, "t")
    with open(out, "w") as fh:
        rc = subprocess.call(["strace", "-f", "-ff", "-qq", "-y", "--seccomp-bpf", "-e", "trace=" + TRACE, "-s", "400", "-o", base, sys.executable, script],
                             stdout=fh, stderr=subprocess.STDOUT, cwd=cwd)
    tfs = sorted(os.path.join(td, f) for f in os.listdir(td))
    rec = build_record(name, script, pkg, tfs, rc, cwd)
    for f in tfs:
        os.remove(f)
    os.rmdir(td)
    json.dump(rec, open(_recfile(memo, name), "w"), indent=1, sort_keys=True)
    return rc


def cmd_key(name, pkg, memo, repofile=None):
    if os.environ.get("BACKLOG_NO_TRACE") == "1":
        return 1
    rec = load(name, memo, repofile)
    if not rec or not rec.get("usable"):
        return 1
    print(key_of(rec, pkg))
    return 0


def cmd_has(name, memo, repofile=None):
    if os.environ.get("BACKLOG_NO_TRACE") == "1":
        return 0
    return 0 if load(name, memo, repofile) is not None else 1


def cmd_export(memo, repofile):
    recs = {}
    try:
        recs = dict(json.load(open(repofile))["probes"])
    except Exception:
        recs = {}
    if os.path.isdir(memo):
        for f in sorted(os.listdir(memo)):
            if f.startswith("inputs_") and f.endswith(".json"):
                try:
                    r = json.load(open(os.path.join(memo, f)))
                except Exception:
                    continue
                if r.get("rc") == 0 and r.get("unusable_because") != ["not traced"]:
                    recs[r["probe"]] = r
    doc = {"format": 1, "note": "What each probe read when it last passed, measured by backlog_probe_inputs; keys of proof stamps are built on these lists. A record that is not usable is kept so that an older usable one is not revived.",
           "probes": dict(sorted(recs.items()))}
    os.makedirs(os.path.dirname(os.path.abspath(repofile)), exist_ok=True)
    json.dump(doc, open(repofile, "w"), indent=1, sort_keys=True)
    open(repofile, "a").write("\n")
    print("exported %d probe record(s), %d usable" % (len(recs), sum(1 for r in recs.values() if r.get("usable"))))
    return 0


def cmd_audit(name, pkg, memo):
    rec = load(name, memo)
    if not rec:
        print("no record for %s" % name)
        return 1
    print("%s: usable=%s files=%d dirs=%d absent=%d" % (name, rec["usable"], len(rec["files"]), len(rec["dirs"]), len(rec["absent"])))
    for w in rec.get("unusable_because", []):
        print("  not usable: " + w)
    for f in rec["files"]:
        print("  read " + f)
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    c = argv[0]
    if c == "run":
        return cmd_run(*argv[1:5])
    if c == "key":
        return cmd_key(*argv[1:5])
    if c == "has":
        return cmd_has(*argv[1:4])
    if c == "export":
        return cmd_export(argv[1], argv[2])
    if c == "audit":
        return cmd_audit(*argv[1:4])
    print("unknown command: " + c)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
