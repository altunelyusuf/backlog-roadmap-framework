#!/usr/bin/env python3
"""backlog_inbox_disposition_probe v1.0.0 -- proof that the disposition tool does all four steps together and refuses half of one (G151)."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
tool = sorted(glob.glob(os.path.join(HERE, "backlog_inbox_disposition_v*.py")), key=sv)[-1]
if sys.argv[1:] == ["--deps"]:
    print(os.path.abspath(__file__)); print(tool); sys.exit(0)
bad = []
def expect(n, ok):
    print(("PASS  " if ok else "FAIL  ") + n)
    if not ok: bad.append(n)
def run(inbox, *a):
    r = subprocess.run([sys.executable, tool, *a, "--inbox", inbox], capture_output=True, text=True); return r.returncode, r.stdout
def fresh():
    d = tempfile.mkdtemp(); os.makedirs(d + "/pending")
    for n in ("HANDOVER_acme_to_backlog-roadmap-framework_a-defect_v1_0_0.md", "CLOSURE_acme_to_backlog-roadmap-framework_thanks_v1_0_0.md", "HANDOVER_acme_to_backlog-roadmap-framework_a-question_v1_0_0.md"):
        open(f"{d}/pending/{n}", "w").write("x\n")
    open(d + "/HANDOVER_LOG.md", "w").write("# Log\n\n| file | from | decision | release | note |\n")
    open(d + "/body.md", "w").write("Fixed.\n"); return d
d = fresh(); H = "HANDOVER_acme_to_backlog-roadmap-framework_a-defect_v1_0_0.md"
rc, _ = run(d, H, "--decision", "accepted (ruled; built)", "--release", "1.426.0", "--response", d + "/body.md")
log = open(d + "/HANDOVER_LOG.md").read()
expect("a decision with a reply moves the file, writes the response and logs one row", rc == 0 and os.path.exists(f"{d}/accepted/{H}") and not os.path.exists(f"{d}/pending/{H}")
       and os.path.exists(f"{d}/accepted/RESPONSE_backlog-roadmap-framework_to_acme_a-defect_v1_0_0.md") and log.count(H) == 1 and "v1.426.0" in log)
C = "CLOSURE_acme_to_backlog-roadmap-framework_thanks_v1_0_0.md"
rc, _ = run(d, C, "--acknowledge", "--release", "1.426.0")
expect("a closure note is acknowledged with a log row and no reply", rc == 0 and os.path.exists(f"{d}/accepted/{C}") and "nothing asked" in open(d + "/HANDOVER_LOG.md").read()
       and not [f for f in os.listdir(d + "/accepted") if f.startswith("RESPONSE_") and "thanks" in f])
Q = "HANDOVER_acme_to_backlog-roadmap-framework_a-question_v1_0_0.md"
before = open(d + "/HANDOVER_LOG.md").read()
rc, _ = run(d, Q, "--acknowledge", "--release", "1.426.0")
expect("a handover that asks something is not acknowledged away (refused, nothing changed)", rc == 2 and os.path.exists(f"{d}/pending/{Q}") and open(d + "/HANDOVER_LOG.md").read() == before)
rc, _ = run(d, Q, "--decision", "maybe", "--release", "1.426.0")
expect("a decision outside accepted/rejected/deferred is refused", rc == 2 and os.path.exists(f"{d}/pending/{Q}"))
rc, _ = run(d, "HANDOVER_nobody.md", "--acknowledge", "--release", "1.426.0")
expect("a file not in pending/ is refused", rc == 2)
rc, _ = run(d, Q, "--decision", "deferred (needs the Owner)", "--release", "1.426.0")
expect("a deferral is filed under deferred/ with a log row", rc == 0 and os.path.exists(f"{d}/deferred/{Q}"))
print("VERDICT   :", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
