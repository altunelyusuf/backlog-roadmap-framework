#!/usr/bin/env python3
"""backlog_merkle_cache v1.2.0 -- a stamp that skips a step only when every file it reads is still the bytes of its last pass (G99 release E; OE R9; the owner's
Merkle-root idea, mixed with the over-processing findings of release D).

Flat whole-input hashing (the fixture-suite stamp before this release concatenated the TBox, every shapes file and ALL fixtures into one sha256) ties every leaf
into one key: touching ONE fixture forced every sibling fixture that shared the key to be re-validated too, even though nothing about them had changed. This
module keeps inputs as separate, named leaves and composes them: leaf(path) hashes one file; a step's key is the hash of its own sorted (name, leaf) pairs, never
of files it does not declare. Two steps that share no leaf never invalidate each other. A root over many steps' keys gives one receipt for "nothing anywhere
changed" while a single change still points at exactly the step it touches -- the generalisation the old flat stamps lacked, and the reason a cold-looking run
that in truth changed one file was paying for every file.

v1.2.0 (G126, the owner's proof-and-SHA idea made portable): (1) a key names each file by its path RELATIVE to the package (the directory above this module's own), not by
its absolute path, so the same bytes give the same key in any clone or container; BACKLOG_MERKLE_ROOT overrides the root. Before, the key held `abspath`, so a stamp
could never be honoured from a different directory. (2) A stamp file records its NAME beside its key. (3) RECORDED STAMPS: `export` writes every stamp of a
directory to one JSON file kept in the package (06-package-provenance/PROOF_STAMPS.json), and `check` also honours that file: a step whose key equals the recorded
one is skipped, as it would be by a stamp made earlier in the same session. A recorded stamp is only ever written from a gate run that passed whole. BACKLOG_COLD=1
makes `check` answer "not stamped" for everything, so a full run can always be forced. `check` prints which source answered ("memo" or "repo").

API:
  leaf(path) -> hex sha256 of one file's bytes (the file must exist -- a step names what it really reads, not a hope)
  key(*paths) -> hex sha256 over "abspath:leaf" for every path, SORTED so order never matters; a path holding a wildcard (*?[) is glob-expanded first, and a glob
                 matching nothing is refused (a step whose named input has vanished is not silently judging less than it claims)
  root(keys) -> hex sha256 over the sorted keys -- a receipt composed from many steps' keys
  Stamp(dir): one stamp per NAME, independent of every other name's stamp
    .check(name, key) -> True only if a prior .record call stored exactly this key for this name
    .record(name, key)
    .clear(name)
Command line (for the bash gate, which has no Stamp object of its own):
  key PATH...             print the composite key
  leaf PATH               print one file's leaf
  check NAME KEY DIR [REPOFILE]   exit 0 if DIR (or REPOFILE) holds a stamp recorded for NAME equal to KEY, 1 otherwise; prints memo or repo when it answers
  export DIR REPOFILE [k=v ...]   write DIR's stamps to REPOFILE
  record NAME KEY DIR     record KEY as NAME's stamp in DIR
A probe prints its own declared inputs (its own file plus whatever tool or fixture it resolves) via its own `--deps`; the caller composes the key from exactly
that list and uses check/record under one NAME per probe or fixture -- the probe is the only one who truly knows what it reads.
"""
import glob, hashlib, json, os, sys


def _root():
    return os.environ.get("BACKLOG_MERKLE_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _rel(n):
    """The path as a step names it: relative to the package when it lies inside it, otherwise absolute (a file outside the package is outside the claim)."""
    a, r = os.path.abspath(n), os.path.abspath(_root())
    return os.path.relpath(a, r) if a == r or a.startswith(r + os.sep) else a


def leaf(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _expand(paths):
    out = []
    for p in paths:
        if any(c in p for c in "*?["):
            hits = sorted(glob.glob(p))
            if not hits:
                raise SystemExit("merkle leaf: a glob matched nothing -- a step cannot name a file it does not read: %s" % p)
            out += hits
        else:
            out.append(p)
    return out


def key(*paths):
    names = _expand(list(paths))
    lines = sorted("%s:%s" % (_rel(n), leaf(n)) for n in names)
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def root(keys):
    return hashlib.sha256("\n".join(sorted(keys)).encode()).hexdigest()


class Stamp:
    def __init__(self, directory):
        self.dir = directory
        os.makedirs(directory, exist_ok=True)

    def _path(self, name):
        safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in name)
        return os.path.join(self.dir, "stamp_" + safe + ".key")

    def check(self, name, k):
        p = self._path(name)
        return os.path.exists(p) and open(p).read().split("\n")[0].strip() == k

    def record(self, name, k):
        open(self._path(name), "w").write(k + "\n" + name + "\n")

    def entries(self):
        out = {}
        for f in sorted(os.listdir(self.dir)):
            if f.startswith("stamp_") and f.endswith(".key"):
                lines = open(os.path.join(self.dir, f)).read().split("\n")
                if len(lines) >= 2 and lines[0].strip() and lines[1].strip():
                    out[lines[1].strip()] = lines[0].strip()
        return out

    def clear(self, name):
        p = self._path(name)
        if os.path.exists(p):
            os.remove(p)


def repo_has(repo_file, name, k):
    try:
        return json.load(open(repo_file))["entries"].get(name) == k
    except Exception:
        return False


def export(directory, repo_file, meta=None):
    """Write every stamp of DIRECTORY, by name, to REPO_FILE (sorted, so the file only changes when a stamp does)."""
    doc = {"format": 1, "note": "Keys of steps that passed in a whole passing gate run; honoured by backlog_merkle_cache check unless BACKLOG_COLD=1.",
           "meta": meta or {}, "entries": dict(sorted(Stamp(directory).entries().items()))}
    os.makedirs(os.path.dirname(os.path.abspath(repo_file)), exist_ok=True)
    json.dump(doc, open(repo_file, "w"), indent=1, sort_keys=True); open(repo_file, "a").write("\n")
    return len(doc["entries"])


def main(argv):
    if not argv:
        print("usage: key PATH... | leaf PATH | check NAME KEY DIR | record NAME KEY DIR")
        return 2
    if argv[0] == "key":
        print(key(*argv[1:]))
        return 0
    if argv[0] == "leaf":
        print(leaf(argv[1]))
        return 0
    if argv[0] == "check":
        name, k, d = argv[1], argv[2], argv[3]
        if os.environ.get("BACKLOG_COLD") == "1":
            return 1
        if Stamp(d).check(name, k):
            print("memo"); return 0
        if len(argv) > 4 and repo_has(argv[4], name, k):
            print("repo"); return 0
        return 1
    if argv[0] == "record":
        _, name, k, d = argv
        Stamp(d).record(name, k)
        return 0
    if argv[0] == "export":
        meta = dict(a.split("=", 1) for a in argv[3:] if "=" in a)
        print("exported %d stamp(s)" % export(argv[1], argv[2], meta))
        return 0
    print("unknown command: %s" % argv[0])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
