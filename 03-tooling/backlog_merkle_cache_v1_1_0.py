#!/usr/bin/env python3
"""backlog_merkle_cache v1.1.0 -- a stamp that skips a step only when every file it reads is still the bytes of its last pass (G99 release E; OE R9; the owner's
Merkle-root idea, mixed with the over-processing findings of release D).

Flat whole-input hashing (the fixture-suite stamp before this release concatenated the TBox, every shapes file and ALL fixtures into one sha256) ties every leaf
into one key: touching ONE fixture forced every sibling fixture that shared the key to be re-validated too, even though nothing about them had changed. This
module keeps inputs as separate, named leaves and composes them: leaf(path) hashes one file; a step's key is the hash of its own sorted (name, leaf) pairs, never
of files it does not declare. Two steps that share no leaf never invalidate each other. A root over many steps' keys gives one receipt for "nothing anywhere
changed" while a single change still points at exactly the step it touches -- the generalisation the old flat stamps lacked, and the reason a cold-looking run
that in truth changed one file was paying for every file.

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
  check NAME KEY DIR      exit 0 if DIR holds a stamp recorded for NAME equal to KEY, 1 otherwise -- nothing is printed either way
  record NAME KEY DIR     record KEY as NAME's stamp in DIR
A probe prints its own declared inputs (its own file plus whatever tool or fixture it resolves) via its own `--deps`; the caller composes the key from exactly
that list and uses check/record under one NAME per probe or fixture -- the probe is the only one who truly knows what it reads.
"""
import glob, hashlib, os, sys


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
    lines = sorted("%s:%s" % (os.path.abspath(n), leaf(n)) for n in names)
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
        return os.path.exists(p) and open(p).read().strip() == k

    def record(self, name, k):
        open(self._path(name), "w").write(k + "\n")

    def clear(self, name):
        p = self._path(name)
        if os.path.exists(p):
            os.remove(p)


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
        _, name, k, d = argv
        return 0 if Stamp(d).check(name, k) else 1
    if argv[0] == "record":
        _, name, k, d = argv
        Stamp(d).record(name, k)
        return 0
    print("unknown command: %s" % argv[0])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
