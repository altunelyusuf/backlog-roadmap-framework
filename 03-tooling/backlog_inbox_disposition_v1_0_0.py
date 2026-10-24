#!/usr/bin/env python3
"""backlog_inbox_disposition v1.0.0 -- disposition one inbox item in one command (G151).

The by-hand path had four steps per handover (move the file, write a response, write a log row, keep the three consistent); 134 are logged.
This does them together and refuses to half-do them.

  backlog_inbox_disposition.py FILE --decision "accepted (...)" --release 1.426.0 [--response BODYFILE] [--outcome "one-line log note"]
      FILE is a name in 07-handover-inbox/pending/. The decision's first word picks the folder: accepted, rejected or deferred.
      With --response the body becomes RESPONSE_<package>_to_<sender>_<slug>_v1_0_0.md in the same folder; without it no reply is written.
  backlog_inbox_disposition.py FILE --acknowledge --release 1.426.0
      For a note that asks for nothing (names starting CLOSURE_, NOTICE_ or NOTE_): accepted, logged "acknowledged, nothing asked", no reply.
Run from anywhere; --inbox DIR overrides the inbox (tests). Exit 0 done, 2 refused (nothing changed).
"""
import os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
PKGNAME = os.path.basename(PKG)


def main(argv):
    if not argv or argv[0].startswith("--"):
        print(__doc__); return 2
    name = argv[0]
    opt = lambda k: argv[argv.index(k) + 1] if k in argv else None
    inbox = opt("--inbox") or os.path.join(PKG, "07-handover-inbox")
    rel = opt("--release"); ack = "--acknowledge" in argv
    decision = "accepted (acknowledged, nothing asked)" if ack else opt("--decision")
    src = os.path.join(inbox, "pending", name)
    if not os.path.isfile(src):
        print("REFUSED: %s is not in pending/" % name); return 2
    if not rel or not re.fullmatch(r"\d+\.\d+\.\d+", rel) or not decision:
        print("REFUSED: --release X.Y.Z and --decision (or --acknowledge) are required"); return 2
    if ack and not re.match(r"(CLOSURE|NOTICE|NOTE)_", name):
        print("REFUSED: only a CLOSURE_, NOTICE_ or NOTE_ item is acknowledged without an answer; give a decision"); return 2
    folder = decision.split()[0].lower().rstrip(":")
    if folder not in ("accepted", "rejected", "deferred"):
        print("REFUSED: the decision starts with accepted, rejected or deferred"); return 2
    m = re.match(r"([A-Za-z]+)_(.+?)_to_(.+?)_(.+)_v\d+_\d+_\d+\.md$", name)
    sender = m.group(2) if m else "sender"; slug = m.group(4) if m else name
    body = opt("--response")
    if body and not os.path.isfile(body):
        print("REFUSED: response body %s not found" % body); return 2
    dst = os.path.join(inbox, folder, name); os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        print("REFUSED: %s already exists in %s/" % (name, folder)); return 2
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", src], cwd=os.path.dirname(src), capture_output=True).returncode == 0
    subprocess.run(["git", "mv", src, dst], cwd=os.path.dirname(src), check=True) if tracked else os.replace(src, dst)
    note = opt("--outcome") or ""
    if body:
        rn = "RESPONSE_%s_to_%s_%s_v1_0_0.md" % (PKGNAME, sender, slug)
        text = open(body, encoding="utf-8").read().rstrip("\n")
        open(os.path.join(inbox, folder, rn), "w", encoding="utf-8").write(
            "# Response: %s to %s\n\n**From:** %s (this package's own session) · **Release:** v%s\n\n%s\n" % (PKGNAME, sender, PKGNAME, rel, text))
        note = note or "See `%s`." % rn
    note = note or "No reply written."
    row = "| `%s` | %s | %s | v%s | %s |\n" % (name, sender, decision, rel, note)
    log = os.path.join(inbox, "HANDOVER_LOG.md")
    t = open(log, encoding="utf-8").read() if os.path.exists(log) else ""
    open(log, "w", encoding="utf-8").write(t + ("" if t.endswith("\n") or not t else "\n") + row)
    print("dispositioned %s -> %s/%s" % (name, folder, " (+response)" if body else "")); return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
