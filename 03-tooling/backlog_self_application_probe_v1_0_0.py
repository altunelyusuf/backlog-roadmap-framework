#!/usr/bin/env python3
"""backlog_self_application_probe v1.0.0 -- the self-application check reads its two declaration files once, and its verdict is the one it had (Lineage 22, box 2, D6).

  v1.1.0 of the check parsed the vocabulary and the register again for every script of the folder (about 200 times, 100 s of the gate). This probe runs the current check with the parser
  counted: it must parse the two files once each, still list the five graph-accepting checkers as refusing to run blind, and still say PASS; and the declaration lookup must give
  None for a script nobody declared and the declared value for one that is. Exit 0 when every expectation holds."""
import glob, importlib.util, io, os, re, sys, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
latest = lambda pat: sorted(glob.glob(os.path.join(PKG, pat)), key=sv)[-1]
SA, TB, AB = latest("03-tooling/backlog_self_application_v*.py"), latest("01-ontologies/backlog_tbox_v*.ttl"), latest("01-ontologies/backlog_abox_v*.ttl")
if sys.argv[1:] == ["--deps"]:
    print("\n".join([SA, TB, AB, os.path.abspath(__file__)])); sys.exit(0)
bad = []
def expect(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (" (%s)" % detail if detail else ""))
    if not ok: bad.append(name)
import rdflib
calls = []
orig = rdflib.Graph.parse
def counted(self, *a, **k):
    src = a[0] if a else k.get("source") or k.get("location") or ""
    calls.append(str(src)); return orig(self, *a, **k)
rdflib.Graph.parse = counted
sp = importlib.util.spec_from_file_location("sa", SA); mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod)
buf = io.StringIO(); code = 0
sys.argv = [SA, "--strict"]
with contextlib.redirect_stdout(buf):
    try: mod.main()
    except SystemExit as e: code = e.code or 0
out = buf.getvalue()
rdflib.Graph.parse = orig
ours = [c for c in calls if c.endswith(".ttl")]
expect("the two declaration files are parsed once each in a whole run", len([c for c in ours if os.path.basename(c).startswith("backlog_tbox")]) == 1 and len([c for c in ours if os.path.basename(c).startswith("backlog_abox")]) == 1, "%d parse(s) of .ttl" % len(ours))
expect("the check still finds the graph-accepting checkers and none runs blind", "refuse to run blind    : 5" in out and "PASS on no input       : 0" in out)
expect("the check still says PASS and exits 0 under --strict", "VERDICT     : PASS" in out and code == 0)
d = mod._declared_scripts(TB, AB)
expect("the lookup gives None for an undeclared script and the declared value for a declared one", mod._accepts_graph_path("no_such_script_v9_9_9.py", TB, AB) is None and any(mod._accepts_graph_path(n, TB, AB) is True for n in d))
print("VERDICT   :", "PASS" if not bad else "FAIL"); [print("  ", b) for b in bad]
sys.exit(1 if bad else 0)
