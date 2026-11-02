#!/usr/bin/env python3
"""backlog_impediment_probe v1.0.0 -- proof of backlog_impediment (G191): the tool run on a scratch register that holds the real kinds and ways, then the real validator on what it wrote."""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", p)[0]]
if sys.argv[1:] == ["--deps"]:
    print(os.path.join(HERE, "backlog_impediment_v1_0_0.py")); print(os.path.abspath(__file__)); sys.exit(0)
TOOL = os.path.join(HERE, "backlog_impediment_v1_0_0.py")
VAL = sorted(glob.glob(HERE + "/backlog_validate_v*.py"), key=sv)[-1]
REGF = sorted(glob.glob(PKG + "/01-ontologies/backlog_abox_v*.ttl"), key=sv)[-1]
fails = 0
def expect(label, ok):
    global fails
    print(("PASS  " if ok else "FAIL  ") + label); fails += (not ok)
from rdflib import Graph, RDF, Namespace
B = Namespace("http://example.org/backlog#")
src = Graph(); src.parse(REGF, format="turtle")
sub = Graph(); sub.bind("backlog", B)
for k in src.subjects(RDF.type, B.ImpedimentKind):
    for t in src.triples((k, None, None)): sub.add(t)
    for m in src.objects(k, B.clearableBy):
        for t in src.triples((m, None, None)): sub.add(t)
base = sub.serialize(format="turtle") + """
@prefix ex: <http://example.org/imp-probe#> . @prefix backlog: <http://example.org/backlog#> .
ex:Lin a backlog:Lineage ; backlog:adoptsRuleSet backlog:RS_ImpedimentsKnown ; backlog:humanApprovalLevel 3 .
ex:Work a backlog:Story .
ex:Builder a backlog:Role .
"""
def run(reg, *a):
    r = subprocess.run([sys.executable, "-I", TOOL, reg] + list(a), capture_output=True, text=True); return r.returncode, r.stdout + r.stderr
with tempfile.TemporaryDirectory() as d:
    reg = os.path.join(d, "r.ttl"); open(reg, "w").write(base)
    RA = ["--lineage", "Lin", "--prefix", "T", "--blocks", "Work", "--kind", "ToolFault", "--statement", "The tool crashes on a checkpoint with no date; nothing can be dated.", "--owner", "Builder"]
    c, o = run(reg, "advise", "--kind", "ToolFault")
    expect("advise prints the ways of a kind with their steps", c == 0 and "Reproduce the fault" in o and "Gone when" in o)
    c, o = run(reg, "advise", "--kind", "NoSuch"); expect("advise refuses a kind that is not one of the seven", c == 1 and "REFUSED" in o and "RuleRefusal" in o)
    c, o = run(reg, "raise", *RA, "--now", "2026-11-02T10:00:00Z")
    expect("raise appends an impediment and prints the ways that fit its kind", c == 0 and "raised Imp_T_1" in o and "Reproduce the fault" in o)
    c, o = run(reg, "raise", *RA[:RA.index("--statement")], "--statement", "  ", "--owner", "Builder"); expect("raise refuses an empty statement", c == 1 and "empty" in o)
    c, o = run(reg, "raise", *[x if x != "Work" else "Nothing" for x in RA]); expect("raise refuses a blocked item that is not in the register", c == 1 and "nothing named" in o)
    c, o = run(reg, "raise", *[x if x != "Builder" else "Work" for x in RA]); expect("raise refuses an owner that is not a role", c == 1 and "not a role" in o)
    c, o = run(reg, "raise", *[x if x != "ToolFault" else "Mood" for x in RA]); expect("raise refuses a kind that is not one of the seven", c == 1 and "not one of" in o)
    c, o = run(reg, "raise", *RA, "--now", "2026-11-02T10:05:00Z"); expect("a second impediment takes the next number", c == 0 and "raised Imp_T_2" in o)
    c, o = run(reg, "list", ); expect("list shows both as open with their kind", o.count("open") == 2 and "ToolFault" in o.replace("Imp_ToolFault", "ToolFault"))
    c, o = run(reg, "clear", "Imp_T_1", "--method", "BoundedRetry", "--now", "2026-11-02T11:00:00Z"); expect("clear refuses a way the kind does not list and names the ways it does", c == 1 and "does not list" in o and "Mth_ReproduceAndRepairTool" in o)
    c, o = run(reg, "clear", "Imp_T_1", "--method", "ReproduceAndRepairTool", "--now", "2026-11-02T09:00:00Z"); expect("clear refuses a time before it was raised", c == 1 and "before it was raised" in o)
    c, o = run(reg, "clear", "Imp_T_1", "--now", "2026-11-02T11:00:00Z"); expect("clear refuses a clearance that says no way", c == 1 and "--method" in o)
    c, o = run(reg, "clear", "Imp_T_1", "--method", "ReproduceAndRepairTool", "--now", "2026-11-02T11:00:00Z"); expect("clear appends the time and the way", c == 0 and "cleared Imp_T_1" in o)
    c, o = run(reg, "clear", "Imp_T_1", "--method", "ReproduceAndRepairTool", "--now", "2026-11-02T11:30:00Z"); expect("clear refuses an impediment already resolved", c == 1 and "already resolved" in o)
    before = open(reg).read()
    c, o = run(reg, "clear", "Imp_Nope", "--method", "ReproduceAndRepairTool"); expect("clear refuses an impediment that does not exist and changes nothing", c == 1 and open(reg).read() == before)
    NL = ["--lineage", "Lin", "--prefix", "T", "--blocks", "Work", "--kind", "ToolFault", "--owner", "Builder"]
    c, o = run(reg, "raise", *NL, "--statement", 'line one\nline "two" \\ back\ttab; it blocks the dating.', "--now", "2026-11-02T10:10:00Z")
    expect("a statement with a newline, quotes, a backslash and a tab is written so that the register still parses", c == 0 and run(reg, "list")[0] == 0 and 'line one' in open(reg).read().replace("\\n", " "))
    snap = open(reg).read()
    c, o = run(reg, "raise", "--lineage", "Lin", "--prefix", "I K>", "--blocks", "Work", "--kind", "ToolFault", "--owner", "Builder", "--statement", "x y z"); expect("a prefix that is not letters and digits is refused and the register is unchanged", c == 1 and "prefix" in o and open(reg).read() == snap)
    c, o = run(reg, "raise", *RA, "--now", "2999-01-01T00:00:00Z"); expect("a time in the future is refused", c == 1 and "future" in o and open(reg).read() == snap)
    c, o = run(reg, "raise", *RA, "--now", "yesterday"); expect("a time that is not a time is refused with a message, not a traceback", c == 1 and "REFUSED" in o and "Traceback" not in o)
    c, o = run(reg, "raise", *[x if x != "Work" else "Builder" for x in RA]); expect("a role cannot be the thing an impediment blocks", c == 1 and "nothing named" in o)
    c, o = run(reg, "raise", *[x if x != "Work" else "Imp_ToolFault" for x in RA]); expect("a kind cannot be the thing an impediment blocks", c == 1 and "nothing named" in o)
    # an item with many triples, as every real item has, can be blocked; a year before 2000 and text that is not UTF-8 are refused and leave the register as it was
    with open(reg, "a") as f: f.write("ex:Many a backlog:Story ; backlog:hasState backlog:Ready ; backlog:hasEffort 2 ; backlog:belongsToLineage ex:Lin .\n")
    snap2 = open(reg, "rb").read()
    c, o = run(reg, "raise", *[x if x != "Work" else "Many" for x in RA], "--now", "2026-11-02T10:20:00Z"); expect("an item with several triples can be blocked", c == 0 and "blocks Many" in o)
    snap2 = open(reg, "rb").read()
    c, o = run(reg, "raise", *RA, "--now", "0001-01-01T00:00:00Z"); expect("a time before the year 2000 is refused and the register is unchanged", c == 1 and open(reg, "rb").read() == snap2)
    r = subprocess.run([sys.executable, "-I", TOOL, reg, "raise", "--lineage", "Lin", "--prefix", "T", "--blocks", "Work", "--kind", "ToolFault", "--owner", "Builder", "--statement", "bad \udcff byte"], capture_output=True, text=True, env={"PATH": os.environ.get("PATH", "")})
    expect("text that is not valid UTF-8 is refused and the register keeps its size", r.returncode != 0 and open(reg, "rb").read() == snap2)
    import threading
    res = []
    def go(i): res.append(subprocess.run([sys.executable, "-I", TOOL, reg, "raise", *NL, "--statement", "parallel %d" % i, "--now", "2026-11-02T10:30:00Z"], capture_output=True, text=True).returncode)
    ths = [threading.Thread(target=go, args=(i,)) for i in range(4)]; [t.start() for t in ths]; [t.join() for t in ths]
    ok = res.count(0); lst = run(reg, "list")[1]
    expect("four raises started together: each success is in the register once and none is lost (%d succeeded)" % ok, ok >= 1 and len(re.findall(r"^Imp_T_\d+ ", lst, re.M)) == len(set(re.findall(r"^(Imp_T_\d+) ", lst, re.M))) and len(re.findall(r"^Imp_T_\d+ ", lst, re.M)) == 4 + ok)
    out = subprocess.run([sys.executable, VAL, reg], capture_output=True, text=True).stdout
    mine = re.findall(r"\[Violation\]\s+(Imp_T_\d+)", out)
    expect("the validator, which still reports its own 9 violations for the bare scratch, reports none against an impediment the tool wrote", mine == [] and "Violation" in out)
    open(reg + ".bad", "w").write(open(reg).read() + "\n<http://example.org/backlog-framework-register#Imp_T_99> a <http://example.org/backlog#Impediment> .\n")
    out2 = subprocess.run([sys.executable, VAL, reg + ".bad"], capture_output=True, text=True).stdout
    expect("control: the same validator does flag an impediment with no statement, owner or time, so the check above can fail", "Imp_T_99" in " ".join(re.findall(r"\[Violation\]\s+(\S+)", out2)))
    # two clears started together: exactly one is written
    ids = re.findall(r"^(Imp_T_\d+) ", run(reg, "list")[1], re.M); tgt = [i for i in ids if "cleared" not in [l for l in run(reg, "list")[1].splitlines() if l.startswith(i + " ")][0]][0]
    res2 = []
    def goc(i): res2.append(subprocess.run([sys.executable, "-I", TOOL, reg, "clear", tgt, "--method", "ReproduceAndRepairTool", "--now", "2026-11-02T10:40:0%dZ" % i], capture_output=True, text=True).returncode)
    ths = [threading.Thread(target=goc, args=(i,)) for i in range(4)]; [t.start() for t in ths]; [t.join() for t in ths]
    expect("four clears of one impediment started together: one is written and three are refused (%d written)" % res2.count(0), res2.count(0) == 1 and open(reg).read().count(tgt + "> <http://example.org/backlog#resolvedAt>") == 1)
    # a write that fails partway leaves the register as it was
    import resource
    before = open(reg, "rb").read(); size = len(before)
    def lim(): resource.setrlimit(resource.RLIMIT_FSIZE, (size + 40, size + 40))
    rf = subprocess.run([sys.executable, "-I", TOOL, reg, "raise", *NL, "--statement", "x" * 400, "--now", "2026-11-02T10:50:00Z"], capture_output=True, text=True, preexec_fn=lim)
    expect("a write cut short by a file-size limit is refused and the register is byte-for-byte as it was and still parses", rf.returncode != 0 and open(reg, "rb").read() == before and run(reg, "list")[0] == 0)
    # a statement that quotes the full address of a later impediment does not block that number
    nxt = max(int(x.split("_")[-1]) for x in re.findall(r"^(Imp_T_\d+) ", run(reg, "list")[1], re.M)) + 1
    c, o = run(reg, "raise", *NL, "--statement", "quotes <http://example.org/backlog-framework-register#Imp_T_%d> in its text" % nxt, "--now", "2026-11-02T10:55:00Z")
    c2, o2 = run(reg, "raise", *NL, "--statement", "the next one", "--now", "2026-11-02T10:56:00Z")
    expect("a statement quoting the address of a later number does not block it", c == 0 and c2 == 0 and ("raised Imp_T_%d" % (nxt + 1)) in o2)
    import shutil
    real = os.path.join(d, "real.ttl"); shutil.copy(REGF, real)
    c, o = run(real, "raise", "--lineage", "L_ImpedimentsKnown", "--prefix", "ZZ", "--blocks", "ST_IK_RaiseAdviseClear", "--kind", "ToolFault", "--owner", "Builder", "--statement", "Probe entry on a copy of the real register.", "--now", "2026-11-02T10:00:00Z")
    expect("on a copy of the real register an item of the lineage can be blocked, the way a real story is", c == 0 and "raised Imp_ZZ_1" in o)
    c, o = run(reg, "list"); expect("list shows the cleared one with its way and the other still open", "cleared by Mth_ReproduceAndRepairTool" in o and "open" in o)
print("VERDICT   :", "PASS" if not fails else "FAIL"); sys.exit(1 if fails else 0)
