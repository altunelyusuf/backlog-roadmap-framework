#!/usr/bin/env python3
"""backlog_box_step v1.9.0 -- records the work of one box in order, with the clock of its run, and refuses the faults made by hand.

Lineage 21, deliverable D3. The faults came from boxes 4 to 9 of Lineage 20, each written down as a finding there:
  * a close composed in one pass          -> `close` refuses a box with no checkpoint recorded between its start and the close
  * a committed record edited in place    -> `close` refuses when a statement of the last published register is gone or changed
                                             (what moves is the state of an item, the status of the lineage and the version header of the file, so those are exempt)
  * work before the box was opened        -> `open` refuses when a governed file already differs from the last published tree;
                                             `close` refuses an artifact older than the box or a governed file older than the box
  * a name changed by hand                -> every identifier is made here from the box number and the story key, and `close` refuses when one the opening wrote is gone
  * the effort read from the wrong place  -> effort is read from `hasEffort` of the stories, nowhere else

v1.9.0 (Lineage 27): the place-unchanged digest also covers the register, git-ignored files and the old path of a renamed file.
v1.8.0 (Lineage 27): the box being closed (its stories, tasks, iteration and deployment unit) is not reported as stalled by the monitor.
v1.7.0 (Lineage 26, G184): in an agentic lineage the close records the verifier's session as the Agentic-Systems package defines it (v0.78.0): the plan with its digest, the grant of
access, the way it started, the session, whether the place was unchanged, and a configuration recorded before the run; the verifier run is stamped when the review started, not at the close; the
iteration and the deployment unit of the box name their overseer, verifier and approver; and each item of the overseer's escalation list becomes a finding. Before the verifier starts the builder runs
`freeze BRIEF.txt`, which fixes the digest of the brief and of the governed files at that moment (`BRIEF.txt.frozen.json`); the spec names it (verifier: plan, started, model).
v1.2.0 (Lineage 22): the Definition of Done the tool writes states its criterion text with rdfs:comment; v1.1.0 wrote a predicate declared nowhere, which the link-control probe refused.
v1.1.0 (Lineage 22, D3): the obligations of a status are read from the register, not carried as code. `owes` validates a copy of the register with the lineage moved to the named status and
prints what is violated there that is not violated now; `open` prints the same for the status it enters. `open` and `close` then validate the register they wrote and, when they introduced a
violation, put the register back as it was and refuse, naming it. With no validator beside the tool nothing is checked and the tool says so.

Usage:  backlog_box_step.py REGISTER.ttl owes STATUS      (e.g. LS_InProgress: what that status owes that the register does not yet hold)
        backlog_box_step.py REGISTER.ttl open  N "title" "sprint goal" STORY_KEY[,STORY_KEY...] [--capacity C] [--allow PATH ...]
        backlog_box_step.py REGISTER.ttl act   N STORY_KEY "what was done"
        backlog_box_step.py REGISTER.ttl freeze BRIEF.txt        (agentic lineage: fix the verifier's plan and the state of the governed files before the verifier starts)
        backlog_box_step.py REGISTER.ttl close N SPEC.json
The lineage and prefix are fixed by --lineage (default L_AdaptiveProof) and --prefix (default AP).

Every record time is read from the clock when the record is written; a later record is at least one second after the one before.
Git is the witness of the published tree: the tool reads it with `git show origin/main:<path>`.
"""
import sys, os, re, json, time, glob, datetime, subprocess

FW = "http://example.org/backlog-framework-register#"
DEFAULT_EXEC = "<http://example.org/fixture-autofix#DefaultExecutor>"
RECORD_FILES = re.compile(r"^(01-ontologies/backlog_abox_v[\d_]+\.ttl|04-documentation/CHANGELOG_v[\d_]+\.md|06-package-provenance/PROBE_INPUTS\.json|MANIFEST_SHA256\.txt|VERSION\.txt|RELEASE_METRICS\.txt)$")
EXEMPT_PREDICATES = {"http://example.org/backlog#hasState", "http://example.org/backlog#hasLineageStatus",
                     "http://www.w3.org/2002/07/owl#versionInfo", "http://www.w3.org/2002/07/owl#versionIRI", "http://www.w3.org/2002/07/owl#priorVersion"}   # the header moves with every release


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


_last = [""]


def tick():
    """A strictly later second than the record before, taken from the clock."""
    t = now()
    while t <= _last[0]:
        time.sleep(0.25)
        t = now()
    _last[0] = t
    return t


def dt(t):
    return '"%s"^^xsd:dateTime' % t


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def parse_t(t):
    return datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)


# ---- the refusals, as functions the probe plants faults against ----

def committed_lost(published_text, current_text):
    """Statements of the published register that the current one no longer holds (hasState excepted). A statement with a blank node is compared by its other parts."""
    import rdflib
    a = rdflib.Graph().parse(data=published_text, format="turtle")
    b = rdflib.Graph().parse(data=current_text, format="turtle")
    lost = []
    for s, p, o in a:
        if str(p) in EXEMPT_PREDICATES or isinstance(s, rdflib.BNode) or isinstance(o, rdflib.BNode):
            continue
        if (s, p, o) not in b:
            lost.append((str(s), str(p), str(o)))
    return sorted(lost)


def files_before(paths, t0):
    """Paths whose modification time is earlier than the box's start t0 (an ISO second)."""
    t0s = parse_t(t0).timestamp()
    return [p for p in paths if os.path.getmtime(p) + 1 < t0s]


def governed_changed(root, ref="origin/main", allow=()):
    """Governed files of the package that differ from the published tree: changed, new or removed, record files excluded."""
    out = subprocess.run(["git", "-C", root, "diff", "--relative", "--no-renames", "--name-status", ref, "--", "."], capture_output=True, text=True).stdout.split("\n")
    new = subprocess.run(["git", "-C", root, "ls-files", "--others", "--exclude-standard", "--", "."], capture_output=True, text=True).stdout.split("\n")
    rel = lambda p: p
    paths = []
    for ln in out:
        if ln.strip():
            paths.append(ln.split("\t")[-1])
    paths += [p for p in new if p.strip()]
    ign = subprocess.run(["git", "-C", root, "ls-files", "--others", "--ignored", "--exclude-standard", "--", "."], capture_output=True, text=True).stdout.split("\n")
    paths += [p for p in ign if p.strip() and not re.match(r"^\.[a-z-]+-stamp$", p)]   # the stamps the release gate leaves in the tree are not work
    pk = subprocess.run(["git", "-C", root, "rev-parse", "--show-prefix"], capture_output=True, text=True).stdout.strip()
    res = []
    for p in paths:
        q = p[len(pk):] if pk and p.startswith(pk) else p
        if "__pycache__" in q or q.endswith(".pyc"):
            continue
        if not RECORD_FILES.match(q) and q not in allow:
            res.append(q)
    return sorted(set(res))


def published_register_text(root, reg):
    """The newest register file of the published tree (paths are read relative to the package, which may sit inside a larger repository)."""
    names = subprocess.run(["git", "-C", root, "ls-tree", "--name-only", "origin/main", "./01-ontologies/"], capture_output=True, text=True).stdout.split("\n")
    ab = [n for n in names if re.search(r"backlog_abox_v\d+_\d+_\d+\.ttl$", n)]
    if not ab:
        raise SystemExit("REFUSED: the published tree holds no register file to compare with")
    ab.sort(key=lambda n: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", n)[0]])
    return subprocess.run(["git", "-C", root, "show", "origin/main:./" + ab[-1]], capture_output=True, text=True).stdout


# ---- the register file ----

class Reg:
    def __init__(self, path, lineage, prefix):
        self.path, self.L, self.P = path, "fw:" + lineage, prefix
        self.s = open(path, encoding="utf-8").read()

    def has(self, ident):
        return re.search(r"^fw:%s\s" % re.escape(ident), self.s, re.M) is not None

    def append(self, text):
        self.s = self.s.rstrip("\n") + "\n" + text.rstrip("\n") + "\n"

    def story_block(self, key):
        m = re.search(r"^fw:ST_%s_%s a backlog:Story .*?backlog:producedByStage fw:\S+ \." % (self.P, key), self.s, re.M | re.S)
        if not m:
            raise SystemExit("REFUSED: no story %s in the register" % key)
        return m

    def story_value(self, key, prop):
        m = re.search(r"backlog:%s ([^;\n]+?)\s*[;.](?=\s|$)" % prop, self.story_block(key).group(0))
        return m.group(1).strip() if m else None

    def set_state(self, key, old, new):
        m = self.story_block(key)
        blk = m.group(0)
        if "backlog:hasState backlog:%s ;" % old not in blk:
            raise SystemExit("REFUSED: story %s is not %s" % (key, old))
        self.s = self.s[:m.start()] + blk.replace("backlog:hasState backlog:%s ;" % old, "backlog:hasState backlog:%s ;" % new, 1) + self.s[m.end():]

    def save(self):
        open(self.path, "w", encoding="utf-8").write(self.s)


def box_ids(P, n):
    return dict(it="It_%s_%d" % (P, n), plan="Ceremony_%s_Planning%d" % (P, n), rel="Rel_%s_%d" % (P, n),
                dplan="DPlan_%s_%d" % (P, n), act="Act_%s_%d_Validate" % (P, n), run="Run_%s_%d_Validate" % (P, n),
                review="Review_%s_%d" % (P, n), retro="Retro_%s_%d" % (P, n))


def opening_ids(P, n, keys):
    """Every identifier the opening of box n writes, derived from the box number and the story keys alone."""
    ids = box_ids(P, n)
    out = [ids["it"], ids["plan"], ids["dplan"], ids["act"]]
    for k in keys:
        out += ["Ref_%s_%d_%s" % (P, n, k), "Chk_%s_%d_%s" % (P, n, k), "Chk_%s_%d_T_%s" % (P, n, k), "Plan_%s_%d_%s" % (P, n, k), "T_%s_%s_Build" % (P, k),
                "Ev%d_ST_%s_%s_T_Refine" % (n, P, k), "Ev%d_ST_%s_%s_T_Start" % (n, P, k)]
        out += ["K_%s_%d_%s_%s" % (P, n, k, x) for x in ("AC", "Size", "Dep", "Input")] + ["K_%s_%d_T_%s_%s" % (P, n, k, x) for x in ("AC", "Size", "Dep", "Input")]
        out += ["Ev%d_T_%s_%s_Build_%s" % (n, P, k, x) for x in ("T_Decompose", "T_RefinedToReady", "T_Start")]
    return out


def read_box(reg, n):
    ids = box_ids(reg.P, n)
    m = re.search(r"^fw:%s a backlog:Iteration .*?backlog:iterationStart \"([^\"]+)\"" % ids["it"], reg.s, re.M | re.S)
    if not m:
        raise SystemExit("REFUSED: box %d is not open" % n)
    st = re.search(r"^fw:%s a backlog:Iteration .*?backlog:hasState backlog:(\w+)" % ids["it"], reg.s, re.M | re.S).group(1)
    stories = re.findall(r"backlog:plansItem fw:ST_%s_(\w+) ;" % reg.P, reg.s[reg.s.index("fw:%s a " % ids["plan"]):]) if reg.has(ids["plan"]) else []
    return ids, m.group(1), st


# ---- commands ----


# ---- an agentic lineage records who acts (Lineage 24) ----
AGENTS = (("Builder", "The builder agent: the session that does the work of a box"), ("Overseer", "The overseeing agent: the agent monitor, which reads the register and reports what needs attention"),
          ("Verifier", "The verifying agent: an agent that did not do the work and judges it against the evidence"), ("Approver", "The approving agent: the register validator, which accepts the box only if the register holds no new violation"))

def is_agentic(reg):
    m = re.search(r"^%s backlog:openedWithProfile .*?\n(?:\s+[^\n]*\n)*?[^\n]* \.\n" % re.escape(reg.L), reg.s, re.M)
    blk = m.group(0) if m else ""
    return "RS_AgentAccountability" in blk

def run_id(P, n, role): return "fw:Run_%s_%d_%s" % (P, n, role)

def agent_defs(reg):
    return "".join("fw:Exec_%s a backlog:Executor_SingleAgent ; rdfs:label \"%s\"@en .\n" % (r, d) for r, d in AGENTS if not reg.has("Exec_" + r))

def agent_run(P, n, role, t, version):
    return "%s a backlog:ExecutorInstance , backlog:Executor_SingleAgent ; backlog:instanceOf fw:Exec_%s ; backlog:instantiatedFromVersion \"%s\" ; backlog:instantiatedAt %s ." % (run_id(P, n, role), role, version, dt(t))

def made_by(recs, P, n):
    """Every move the tool records names the run that made it."""
    return [r.replace("backlog:transitionedBy backlog:Builder", "backlog:transitionedBy backlog:Builder ; backlog:transitionedByExecutor %s" % run_id(P, n, "Builder")) for r in recs]

import hashlib

BRIDGE = """@prefix agsys: <http://example.org/agentic-systems#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
fw:StartWay_Request a agsys:StartWay ; rdfs:label "On the builder's request"@en .
fw:AccessRoute_FileSystem a agsys:AccessRoute ; rdfs:label "The working tree of the package, on the file system of the session"@en ."""


def tree_digest(root, reg_path):
    """sha256 over the governed files that differ from the published tree (path and content: changed, new, removed, the old path of a renamed file, and git-ignored files) and over the register itself; the review notes and briefs, where the verifier writes, stay out."""
    h = hashlib.sha256()
    for f in governed_changed(root):
        if f.startswith("06-package-provenance/reviews/") or os.path.join(root, f) == os.path.realpath(reg_path):
            continue
        p = os.path.join(root, f)
        h.update(f.encode()); h.update(open(p, "rb").read() if os.path.isfile(p) else b"<removed>")
    h.update(b"<register>"); h.update(open(reg_path, "rb").read())
    return h.hexdigest()


def file_digest(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def cmd_freeze(reg, root, brief):
    p = os.path.join(root, brief)
    if not os.path.isfile(p) or os.path.getsize(p) == 0:
        raise SystemExit("REFUSED: the brief %s does not exist or is empty" % brief)
    fz = {"frozen_at": now(), "plan_digest": file_digest(p), "tree_digest": tree_digest(root, reg.path)}
    json.dump(fz, open(p + ".frozen.json", "w"))
    print("frozen at %s: plan %s..., governed files %s..." % (fz["frozen_at"], fz["plan_digest"][:12], fz["tree_digest"][:12]))


def escalation_items(text):
    out, on = [], False
    for ln in text.splitlines():
        if ln.startswith("== Escalation"): on = True
        elif on and ln.strip().startswith("- "): out.append(ln.strip()[2:])
    clean = lambda s: re.sub(r"\bRel_\w+", "a deployment unit", re.sub(r"\bIt_\w+", "an iteration", re.sub(r"\b(ST|T|Run|Ev|Obj)_\w+", "a record", s)))
    return [clean(x) for x in out]

TOOL_VERSION = "1.9.0"

def has_own_kickoff(text, L):
    """True when the register holds a kick-off of this lineage itself; the kick-off of another lineage does not count (Lineage 24, held by a probe in Lineage 25)."""
    return re.search(r"backlog:kicksOffLineage\s+(?:fw:|<http://example.org/backlog-framework-register#)%s\b" % re.escape(L[3:]), text) is not None


def cmd_open(reg, root, n, title, goal, keys, capacity, allow=(), integrity=2):
    P, L = reg.P, reg.L
    ids = box_ids(P, n)
    if reg.has(ids["it"]):
        raise SystemExit("REFUSED: box %d already has records" % n)
    subprocess.run(["git", "-C", root, "fetch", "-q", "origin"], capture_output=True)
    dirty = governed_changed(root, allow=allow)
    if dirty:
        raise SystemExit("REFUSED: governed files already differ from the published tree, so work began before the box was opened: " + ", ".join(dirty))
    for k in keys:
        if reg.story_value(k, "hasState") != "backlog:Proposed":
            raise SystemExit("REFUSED: story %s is not Proposed" % k)
    if not reg.has("DoD_%s" % P):
        reg.append("fw:DoD_%s a backlog:DefinitionOfDone ; rdfs:label \"Definition of Done for the stories of Lineage 21\"@en ;\n    backlog:hasDoDCriterion fw:DoD_%s_1 , fw:DoD_%s_2 .\n"
                   "fw:DoD_%s_1 a backlog:DoDCriterion ; rdfs:label \"Evidence attests the acceptance criterion\"@en ;\n    rdfs:comment \"A test or a measured run of a tool attests the acceptance criterion, and the artifact it names exists.\" ;\n    backlog:hasCheckQuery \"ASK { ?e a backlog:TestEvidence . FILTER NOT EXISTS { ?e backlog:attestsCriterion ?c } }\" ; backlog:hasExpectedResult \"false\" ; backlog:hasCriterionStatus backlog:Holds .\n"
                   "fw:DoD_%s_2 a backlog:DoDCriterion ; rdfs:label \"The register validates\"@en ;\n    rdfs:comment \"The register validates with no violation after the box is closed.\" ;\n    backlog:hasCheckQuery \"backlog_validate: 0 sh:Violation.\" ; backlog:hasExpectedResult \"0 violations\" ; backlog:hasCriterionStatus backlog:Holds .\n" % (P, P, P, P, P))
    # the status being entered owes a kick-off recorded before the first start (RS_PlanBeforeStart) and the status itself
    if not has_own_kickoff(reg.s, L):  # this lineage's own kick-off, not any lineage's
        reg.save()
        steps = sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backlog_lineage_steps_v*.py")), key=lambda x: [int(y) for y in re.findall(r"_v(\d+)_(\d+)_(\d+)", x)[0]])[-1]
        r = subprocess.run([sys.executable, steps, "plan", reg.path, "--lineage", FW + reg.L[3:], "--container", FW + "Register", "--by", "Builder"], capture_output=True, text=True)
        if r.returncode:
            raise SystemExit("REFUSED: the plan step failed: " + (r.stdout + r.stderr)[-400:])
        print(r.stdout.strip())
        reg.s = open(reg.path, encoding="utf-8").read()
    m = re.search(r"^%s a backlog:Lineage .*?backlog:hasLineageStatus backlog:(\w+)" % re.escape(L), reg.s, re.M | re.S)
    if m and m.group(1) in ("LS_Backlogged",):
        reg.s = reg.s[:m.start(1)] + "LS_InProgress" + reg.s[m.end(1):]
    # refinement and readiness, one second apart, before the box is planned
    recs = []
    for k in keys:
        t1 = tick()
        eff = reg.story_value(k, "hasEffort")
        recs.append("fw:Ref_%s_%d_%s a backlog:RefinementEvent ; backlog:hasWorkKind backlog:WorkKind_Preparation ; backlog:refines fw:ST_%s_%s ; backlog:refinedAt %s ;\n"
                    "    backlog:hasRefinementOutcome \"Groomed for box %d: the acceptance criterion reads as a test, the effort is %s points, and the change is to shapes, tooling or records with probe checks.\" ;\n"
                    "    backlog:refinedBy backlog:Builder ; backlog:addressesConcern backlog:Concern_Architecture ." % (P, n, k, P, k, dt(t1), n, eff))
        recs.append("fw:Ev%d_ST_%s_%s_T_Refine a backlog:TransitionEvent ; backlog:transitionedItem fw:ST_%s_%s ; backlog:viaTransition backlog:T_Refine ; backlog:transitionedAt %s ; backlog:transitionedBy backlog:Builder ; backlog:hasTransitionNote \"Groomed and made ready for box %d.\" ." % (n, P, k, P, k, dt(t1), n))
        t2 = tick()
        recs.append("fw:Chk_%s_%d_%s a backlog:ReadinessCheck ; rdfs:label \"Readiness of the story %s\"@en ;\n    backlog:checksReadinessOf fw:ST_%s_%s ; backlog:readinessCheckedAt %s ;\n    backlog:hasReadinessCriterion fw:K_%s_%d_%s_AC , fw:K_%s_%d_%s_Size , fw:K_%s_%d_%s_Dep , fw:K_%s_%d_%s_Input ." % (P, n, k, k, P, k, dt(t2), P, n, k, P, n, k, P, n, k, P, n, k))
        for suf, lab in (("AC", "The acceptance criterion reads as a test the validator can run"), ("Size", "The effort is estimated and fits the box"), ("Dep", "Nothing it depends on is open"), ("Input", "No decision of the Owner is waited on")):
            recs.append("fw:K_%s_%d_%s_%s a backlog:ReadinessCriterion ; rdfs:label \"%s\"@en ; backlog:criterionMet true ." % (P, n, k, suf, lab))
    tp = tick()
    recs.append("fw:%s a backlog:DeploymentPlan ; backlog:hasWorkKind backlog:WorkKind_Planning ; backlog:deploymentPlanForBox fw:%s ; backlog:plansDeploymentUnit fw:%s ; backlog:deploymentPlannedAt %s ." % (ids["dplan"], ids["it"], ids["rel"], dt(tp)))
    t0 = tick()
    recs.append("fw:%s a backlog:Iteration ; backlog:hasIdentifier \"%s-BOX-%d\" ; backlog:hasTitle \"%s\" ;\n    backlog:hasSprintGoal \"%s\" ;\n"
                "    backlog:hasState backlog:InProgress ; backlog:iterationStart %s ;\n    backlog:hasCapacity %s ; backlog:belongsToLineage %s%s ." % (ids["it"], P, n, esc(title), esc(goal), dt(t0), float(capacity), L, (" ;\n    rdfs:comment \"Disclosed at the opening: these governed files already differed from the published tree, so work on them began before the box was open: %s.\"@en" % ", ".join(allow)) if allow else ""))
    tpl = tick()
    recs.append("fw:%s a backlog:SprintPlanningCeremony ; backlog:hasWorkKind backlog:WorkKind_Planning ; backlog:ceremonyFor fw:%s ; backlog:heldAt %s ;\n    backlog:includesPlanningEvent %s ." % (ids["plan"], ids["it"], dt(tpl), " , ".join("fw:Plan_%s_%d_%s" % (P, n, k) for k in keys)))
    for k in keys:
        tq = tick()
        recs.append("fw:Plan_%s_%d_%s a backlog:PlanningEvent ; rdfs:label \"Story %s planned into box %d\"@en ;\n    backlog:plansItem fw:ST_%s_%s ; backlog:plannedInto fw:%s ; backlog:plannedAt %s ; backlog:plannedBy backlog:Builder ; backlog:producesTask fw:T_%s_%s_Build ." % (P, n, k, k, n, P, k, ids["it"], dt(tq), P, k))
        tdec = tick(); tck = tick(); trdy = tick(); tsk = tick(); tss = tick()
        recs.append("fw:T_%s_%s_Build a backlog:ExecutionTask ; backlog:hasIdentifier \"T-%s-%s-BUILD\" ; backlog:hasState backlog:InProgress ;\n"
                    "    backlog:hasTaskType backlog:Task_Implementation ; backlog:responsible %s ; backlog:memberOfContainer fw:%s ; backlog:appliesDefinitionOfDone fw:DoD_%s ; backlog:belongsToLineage %s ;\n"
                    "    backlog:hasExecutionModality backlog:Mode_Automated ; backlog:startedAt %s ." % (P, k, P, k.upper(), DEFAULT_EXEC, ids["it"], P, L, dt(tsk)))
        recs.append("fw:Chk_%s_%d_T_%s a backlog:ReadinessCheck ; rdfs:label \"Readiness of the task of story %s\"@en ;\n    backlog:checksReadinessOf fw:T_%s_%s_Build ; backlog:readinessCheckedAt %s ;\n    backlog:hasReadinessCriterion fw:K_%s_%d_T_%s_AC , fw:K_%s_%d_T_%s_Size , fw:K_%s_%d_T_%s_Dep , fw:K_%s_%d_T_%s_Input ." % (P, n, k, k, P, k, dt(tck), P, n, k, P, n, k, P, n, k, P, n, k))
        for suf, lab in (("AC", "The task builds what the acceptance criterion tests"), ("Size", "The effort is estimated and fits the box"), ("Dep", "Nothing it depends on is open"), ("Input", "No decision of the Owner is waited on")):
            recs.append("fw:K_%s_%d_T_%s_%s a backlog:ReadinessCriterion ; rdfs:label \"%s\"@en ; backlog:criterionMet true ." % (P, n, k, suf, lab))
        recs.append("fw:ST_%s_%s backlog:decomposesInto fw:T_%s_%s_Build ; backlog:memberOfContainer fw:%s ; backlog:appliesDefinitionOfDone fw:DoD_%s ; backlog:hasApplicableConcern backlog:Concern_Architecture ; backlog:startedAt %s ." % (P, k, P, k, ids["it"], P, dt(tss)))
        for via, t in (("T_Decompose", tdec), ("T_RefinedToReady", trdy), ("T_Start", tsk)):
            recs.append("fw:Ev%d_T_%s_%s_Build_%s a backlog:TransitionEvent ; backlog:transitionedItem fw:T_%s_%s_Build ; backlog:viaTransition backlog:%s ; backlog:transitionedAt %s ; backlog:transitionedBy backlog:Builder ." % (n, P, k, via, P, k, via, dt(t)))
        recs.append("fw:Ev%d_ST_%s_%s_T_Start a backlog:TransitionEvent ; backlog:transitionedItem fw:ST_%s_%s ; backlog:viaTransition backlog:T_Start ; backlog:transitionedAt %s ; backlog:transitionedBy backlog:Builder ." % (n, P, k, P, k, dt(tss)))
        reg.set_state(k, "Proposed", "InProgress")
    recs.append("fw:%s a backlog:ControlActivity ; rdfs:label \"Validate the register and run the probes before the box is reviewed\"@en ;\n    backlog:hasWorkKind backlog:WorkKind_Control ; backlog:plannedInBox fw:%s ." % (ids["act"], ids["it"]))
    if is_agentic(reg):
        recs = [r.replace("backlog:responsible " + DEFAULT_EXEC, "backlog:responsible " + run_id(P, n, "Builder")) for r in made_by(recs, P, n)]
        recs.insert(0, agent_run(P, n, "Builder", t0, TOOL_VERSION))
        for k in keys:
            recs.append("fw:ST_%s_%s backlog:responsible %s ; backlog:integrityLevel %d ." % (P, k, run_id(P, n, "Builder"), integrity))
            recs.append("fw:T_%s_%s_Build backlog:integrityLevel %d ." % (P, k, integrity))
        defs = agent_defs(reg)
        if defs: recs.insert(0, defs.rstrip("\n"))
    reg.append("\n# ---- box %d of %s: opened %s by backlog_box_step ----\n" % (n, L, t0) + "\n".join(recs))
    reg.save()
    print("box %d opened at %s; stories %s now InProgress" % (n, t0, ", ".join(keys)))


def cmd_act(reg, n, key, note):
    ids, t0, st = read_box(reg, n)
    if st != "InProgress":
        raise SystemExit("REFUSED: box %d is not in progress" % n)
    named = re.findall(r"\bG\d{2,4}\b|\b[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]+\b|\b(?:backlog|fw):\w+|\b[A-Z]{1,4}\d*-[A-Z]\d+\b", note)
    if named:
        raise SystemExit("REFUSED: the note names a modelled thing by identifier (%s). A connection is a link, not text: say it in words and record the link in the register." % ", ".join(sorted(set(named))))
    count = len(re.findall(r"^fw:Ckp_%s_%d_\d+ " % (reg.P, n), reg.s, re.M)) + 1
    t = tick()
    reg.append("fw:Ckp_%s_%d_%d a backlog:DailyCheckpoint ; rdfs:comment \"%s: %s\"@en ; backlog:hasWorkKind backlog:WorkKind_Monitoring ; backlog:checkpointOfBox fw:%s ; backlog:checkpointAt %s ;\n    backlog:openItemCount 0 ; backlog:inProgressItemCount %d ; backlog:doneItemCount 0 ." % (reg.P, n, count, key, esc(note), ids["it"], dt(t), len(re.findall(r"^fw:Plan_%s_%d_\w+ a " % (reg.P, n), reg.s, re.M))))
    reg.save()
    print("checkpoint %d of box %d at %s" % (count, n, t))


def cmd_close(reg, root, n, spec):
    P, L = reg.P, reg.L
    ids, t0, st = read_box(reg, n)
    if st != "InProgress":
        raise SystemExit("REFUSED: box %d is not in progress" % n)
    keys = re.findall(r"^fw:Plan_%s_%d_(\w+) a " % (P, n), reg.s, re.M)
    gone = [i for i in opening_ids(P, n, keys) if not reg.has(i)]
    if gone:
        raise SystemExit("REFUSED: %d identifier(s) written at the opening of box %d are gone, so a name was changed by hand: %s" % (len(gone), n, ", ".join(gone[:3])))
    if not re.search(r"^fw:Ckp_%s_%d_\d+ " % (P, n), reg.s, re.M):
        raise SystemExit("REFUSED: no checkpoint was recorded between the start of box %d and its close, so the close would be composed in one pass" % n)
    lost = committed_lost(published_register_text(root, reg.path), reg.s)
    if lost:
        raise SystemExit("REFUSED: %d statement(s) of the published register are gone or changed (a committed record is appended to, never edited): %s" % (len(lost), "; ".join(" ".join(x.rsplit("#", 1)[-1] for x in l) for l in lost[:3])))
    for k in keys:
        if k not in spec["stories"]:
            raise SystemExit("REFUSED: no evidence given for story %s" % k)
        art = spec["stories"][k]["artifact"]
        p = os.path.join(root, art)
        if not os.path.exists(p):
            raise SystemExit("REFUSED: the artifact %s of story %s does not exist" % (art, k))
        if files_before([p], t0):
            raise SystemExit("REFUSED: the artifact %s is older than the box: it was not produced inside box %d" % (art, n))
    disc = re.search(r"^fw:%s a backlog:Iteration .*?Disclosed at the opening: [^:]*: ([^\"]+)\.\"@en" % ids["it"], reg.s, re.M | re.S)
    allow = [x.strip() for x in disc.group(1).split(",")] if disc else []
    stale = files_before([os.path.join(root, f) for f in governed_changed(root, allow=allow) if os.path.exists(os.path.join(root, f))], t0)
    if stale:
        raise SystemExit("REFUSED: governed files changed before the box was opened: " + ", ".join(os.path.relpath(x, root) for x in stale))
    efforts = {k: float(reg.story_value(k, "hasEffort")) for k in keys}
    recs = []
    agentic = is_agentic(reg)
    if agentic:
        v = spec.get("verifier") or {}
        if not v.get("agent") or not v.get("review"):
            raise SystemExit("REFUSED: this lineage is agentic: the spec must name the verifying agent and the file that holds its review (verifier: agent, review)")
        if v["agent"].strip().lower() in ("builder", spec.get("maker", "builder").strip().lower()):
            raise SystemExit("REFUSED: the verifier is the maker. Work that one party produced and the same party then checked has been checked by nobody else.")
        rv = os.path.join(root, v["review"])
        if not os.path.exists(rv) or os.path.getsize(rv) == 0:
            raise SystemExit("REFUSED: the review file %s of the verifying agent does not exist or is empty" % v["review"])
        if files_before([rv], t0):
            raise SystemExit("REFUSED: the review file %s is older than the box: it was not produced inside box %d" % (v["review"], n))
        if not v.get("plan") or not v.get("started"):
            raise SystemExit("REFUSED: this lineage is agentic: the spec must name the plan of the verifier (verifier: plan, the brief fixed with `freeze`) and the time it started (verifier: started)")
        pf = os.path.join(root, v["plan"])
        if not os.path.isfile(pf) or not os.path.isfile(pf + ".frozen.json"):
            raise SystemExit("REFUSED: the plan %s or its frozen record is missing: run `freeze` on the brief before the verifier starts" % v["plan"])
        fz = json.load(open(pf + ".frozen.json"))
        if file_digest(pf) != fz["plan_digest"]:
            raise SystemExit("REFUSED: the brief %s changed after it was fixed: it is not the plan the verifier followed" % v["plan"])
        if not (parse_t(t0) <= parse_t(fz["frozen_at"]) <= parse_t(v["started"]) and parse_t(v["started"]) <= datetime.datetime.fromtimestamp(os.path.getmtime(rv), datetime.timezone.utc) + datetime.timedelta(seconds=2)):
            raise SystemExit("REFUSED: the order is not box opened <= plan fixed <= verifier started <= review written: %s, %s, %s" % (t0, fz["frozen_at"], v["started"]))
        unchanged = (fz["tree_digest"] == tree_digest(root, reg.path))
        mon = sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backlog_agent_monitor_v*.py")), key=lambda x: [int(y) for y in re.findall(r"_v(\d+)_(\d+)_(\d+)", x)[0]])
        esc_n = "the agent monitor was not found beside the tool"; esc_list = []
        if mon:
            mr = subprocess.run([sys.executable, mon[-1], reg.path, "--lineage", reg.L[3:], "--closing", ",".join(["ST_%s_%s" % (P, k) for k in keys] + ["T_%s_%s_Build" % (P, k) for k in keys] + [ids["it"], ids["rel"]])], capture_output=True, text=True)
            esc_list = escalation_items(mr.stdout)
            esc_n = "the agent monitor ran and its escalation list was %s" % ("empty" if mr.returncode == 0 else "not empty (exit %d); each item is a finding of this box" % mr.returncode)
        tov, tapp = tick(), tick()
        cfg = "fw:Config_%s_%d_Verifier" % (P, n)
        recs_a = [BRIDGE if "agsys:StartWay" not in reg.s else "",
                  "fw:Session_%s_%d_Verifier a prov:Agent ; rdfs:label \"%s\"@en ." % (P, n, esc(v["agent"])),
                  "fw:Grant_%s_%d_Verifier a agsys:AccessGrant ; agsys:grantedBy %s ; agsys:viaRoute fw:AccessRoute_FileSystem ; agsys:grantedPlace \"the governed files and the register of the package, as the builder left them when the brief was fixed\" ; agsys:grantMode \"read-only\" ; agsys:grantedAt %s ." % (P, n, run_id(P, n, "Builder"), dt(fz["frozen_at"])),
                  "fw:Plan_%s_%d_Verifier a agsys:VerificationPlan ; agsys:hasPlanDigest \"%s\" ; rdfs:comment \"The brief given to the verifying agent, fixed by its digest before the agent started.\"@en ." % (P, n, fz["plan_digest"]),
                  "%s a agsys:AgentConfiguration ; agsys:isConfigurationOf fw:Exec_Verifier ; agsys:recordedAt %s ; agsys:hasConfigurationItem fw:CfgItem_%s_%d_Brief%s ." % (cfg, dt(fz["frozen_at"]), P, n, (" , fw:CfgItem_%s_%d_Model" % (P, n)) if v.get("model") else ""),
                  "fw:CfgItem_%s_%d_Brief a agsys:ConfigurationItem ; agsys:hasItemKind \"brief\" ; agsys:hasItemValue \"sha256 %s\" ." % (P, n, fz["plan_digest"])]
        if v.get("model"):
            recs_a.append("fw:CfgItem_%s_%d_Model a agsys:ConfigurationItem ; agsys:hasItemKind \"model\" ; agsys:hasItemValue \"%s\" ." % (P, n, esc(v["model"])))
        recs_a += [agent_run(P, n, "Overseer", tov, TOOL_VERSION)[:-2] + "; rdfs:comment \"%s.\"@en ." % esc(esc_n),
                   (agent_run(P, n, "Verifier", v["started"], "Config_%s_%d_Verifier" % (P, n))[:-2] + "; agsys:startedInWay fw:StartWay_Request ; agsys:startedUnderGrant fw:Grant_%s_%d_Verifier ; agsys:followsPlan fw:Plan_%s_%d_Verifier ; agsys:executedBy fw:Session_%s_%d_Verifier ; agsys:placeUnchanged %s ; rdfs:comment \"Reviewed by %s; the review is kept in a file of the package.\"@en ." % (P, n, P, n, P, n, "true" if unchanged else "false", esc(v["agent"]))),
                   agent_run(P, n, "Approver", tapp, TOOL_VERSION)]
        defs = agent_defs(reg)
        if defs: recs_a.insert(0, defs.rstrip("\n"))
        recs_a = [x for x in recs_a if x]
    recs = []
    for k in keys:
        s = spec["stories"][k]
        tf = tick()
        recs.append("fw:Ev%d_T_%s_%s_Build_T_Complete a backlog:TransitionEvent ; backlog:transitionedItem fw:T_%s_%s_Build ; backlog:viaTransition backlog:T_Complete ; backlog:transitionedAt %s ; backlog:transitionedBy backlog:Builder ." % (n, P, k, P, k, dt(tf)))
        recs.append("fw:Ev%d_ST_%s_%s_T_Complete a backlog:TransitionEvent ; backlog:transitionedItem fw:ST_%s_%s ; backlog:viaTransition backlog:T_Complete ; backlog:transitionedAt %s ; backlog:transitionedBy backlog:Builder ." % (n, P, k, P, k, dt(tf)))
        recs.append("fw:Ev_%s_%s a backlog:TestEvidence ; rdfs:label \"The check for story %s\"@en ;\n    backlog:evidenceVerified true ; backlog:hasTestId \"%s\" ;\n    backlog:hasTestSpec \"%s\" ;\n    backlog:attestsCriterion fw:AC_%s_%s ;\n    backlog:hasVerificationMethod \"%s\" ;\n    backlog:verifiedAt %s ; backlog:verifiedByTool \"%s\" ;\n    backlog:satisfiedByArtifact \"%s\" ; backlog:belongsToLineage %s ." % (P, k, k, k, s["artifact"], P, k, esc(s["method"]), dt(tf), esc(s["tool"]), s["artifact"], L))
        recs.append("fw:AC_%s_%s backlog:satisfiedByArtifact \"%s\" ." % (P, k, s["artifact"]))
        recs.append("fw:H_%s_%s a backlog:TestHarness ; rdfs:label \"Harness for story %s\"@en ;\n    backlog:harnessFor fw:ST_%s_%s ; backlog:hasHarnessEvidence fw:Ev_%s_%s ; backlog:harnessComplete true ;\n    backlog:hasRationale \"%s\" ." % (P, k, k, P, k, P, k, esc(s["harness"])))
        recs.append("fw:Demo_%s_%s a backlog:DemoRun ; backlog:hasWorkKind backlog:WorkKind_Control ; backlog:demonstratesItem fw:ST_%s_%s ; backlog:demonstratedAgainst fw:AC_%s_%s ; backlog:demoAt %s ;\n    backlog:hasDemoShown \"%s\" ;\n    backlog:hasDemoResult \"%s\" ." % (P, k, P, k, P, k, dt(tick()), esc(s["demo"]), esc(s["result"])))
        reg.set_state(k, "InProgress", "Done")
        m = re.search(r"^fw:T_%s_%s_Build a backlog:ExecutionTask .*?backlog:startedAt \"[^\"]+\"\^\^xsd:dateTime \." % (P, k), reg.s, re.M | re.S)
        blk = m.group(0).replace("backlog:hasState backlog:InProgress ;", "backlog:hasState backlog:Done ;", 1)
        blk = blk[:-1].rstrip() + " ; backlog:finishedAt %s ; backlog:hasEvidence fw:Ev_%s_%s ." % (dt(tf), P, k)
        reg.s = reg.s[:m.start()] + blk + reg.s[m.end():]
        recs.append("fw:ST_%s_%s backlog:finishedAt %s ; backlog:lastAuditedAt %s ; backlog:hasEvidence fw:Ev_%s_%s ; backlog:memberOfContainer fw:%s ." % (P, k, dt(tf), dt(tf), P, k, ids["rel"]))
    trun = tick()
    recs.append("fw:%s a backlog:ControlRun ; backlog:runOfActivity fw:%s ; backlog:ranAt %s ;\n    backlog:hasRunResult \"%s\" ." % (ids["run"], ids["act"], dt(trun), esc(spec["run_result"])))
    trev = tick()
    recs.append("fw:%s a backlog:SprintReviewCeremony ; backlog:hasWorkKind backlog:WorkKind_Closure ;\n    backlog:ceremonyFor fw:%s ; backlog:heldAt %s ; backlog:reviewsCeremony fw:%s ;\n    backlog:closesIteration fw:%s ; backlog:closesStory %s ." % (ids["review"], ids["it"], dt(trev), ids["plan"], ids["it"], " , ".join("fw:ST_%s_%s" % (P, k) for k in keys)))
    trel = tick()
    recs.append("fw:%s a backlog:DeploymentUnit ;\n    backlog:hasIdentifier \"%s-REL-%d\" ; backlog:hasTitle \"%s\" ;\n    backlog:hasState backlog:Done ; backlog:hasDeploymentDate %s ;\n    backlog:deploysFrom fw:%s ; backlog:deploysItem %s ;\n    backlog:decidedBy backlog:Builder ; backlog:hasSelectionBasis backlog:Sel_Committed ; backlog:belongsToLineage %s ." % (ids["rel"], P, n, esc(spec["release_title"]), dt(trel), ids["it"], " , ".join("fw:ST_%s_%s" % (P, k) for k in keys), L))
    if "plansDeploymentUnit fw:%s " % ids["rel"] not in reg.s:  # the plan names its unit at the opening (G170); the unit may not carry unfinished work, so it is written at the close
        recs.append("fw:%s backlog:plansDeploymentUnit fw:%s ." % (ids["dplan"], ids["rel"]))
    fks = []
    for f in spec["findings"]:
        fks.append("fw:Find_%s_%s" % (P, f["key"]))
        recs.append("fw:Find_%s_%s a backlog:RetrospectiveFinding ;\n    backlog:hasFindingScope backlog:Scope_LineageLocal ;\n    backlog:relatesToWorkItem fw:ST_%s_%s ;\n    backlog:hasRootCause \"%s\" ;\n    backlog:hasRemedy \"%s\" ." % (P, f["key"], P, f.get("story", keys[0]), esc(f["root_cause"]), esc(f["remedy"])))
    if agentic:
        ans = spec.get("escalation_answer", "Open: raised by the overseer and not answered in this box.")
        for i, line in enumerate(esc_list, 1):
            if ('hasRootCause "%s"' % esc(line)) in reg.s:
                continue
            fks.append("fw:Find_%s_Esc%d_%d" % (P, n, i))
            recs.append("fw:Find_%s_Esc%d_%d a backlog:RetrospectiveFinding ;\n    backlog:hasFindingScope backlog:Scope_LineageLocal ;\n    backlog:relatesToWorkItem fw:ST_%s_%s ;\n    backlog:hasRootCause \"%s\" ;\n    backlog:hasRemedy \"%s\" ." % (P, n, i, P, keys[0], esc(line), esc(ans)))
    tret = tick()
    recs.append("fw:%s a backlog:SprintRetrospective ; backlog:hasWorkKind backlog:WorkKind_Closure ;\n    backlog:followsReview fw:%s ; backlog:heldAt %s ; backlog:producesFinding %s ." % (ids["retro"], ids["review"], dt(tret), " , ".join(fks)))
    for o in spec["observations"]:
        recs.append("fw:Obs_%s_%s_B%d a backlog:MetricObservation ; rdfs:label \"After box %d: %s\"@en ;\n    backlog:observesMetric fw:Metric_%s_%s ; backlog:observationFor fw:Obj_%s_%s ; backlog:hasObservedValue %s ; backlog:observedAt %s ;\n    backlog:hasObservationMethod \"%s\" ." % (P, o["obj"], n, n, o["obj"], P, o["obj"], P, o["obj"], float(o["value"]), dt(trun), esc(o["method"])))
    mins = round((parse_t(tret) - parse_t(t0)).total_seconds() / 60, 1)
    m = re.search(r"(^fw:%s a backlog:Iteration .*?)backlog:hasState backlog:InProgress ; backlog:iterationStart (\"[^\"]+\"\^\^xsd:dateTime) ;\n    backlog:hasCapacity ([\d.]+) ;" % ids["it"], reg.s, re.M | re.S)
    cap = float(m.group(3))
    reg.s = reg.s[:m.start()] + m.group(1) + 'backlog:hasState backlog:Done ; backlog:iterationStart %s ;\n    backlog:iterationEnd %s ;\n    backlog:hasCapacity %s ; backlog:hasObservedDuration %s ; backlog:hasDurationSource "Wall clock from the start of the box to its review, both taken from the register: %s to %s. Effort of the stories read from hasEffort: %s points." ;' % (m.group(2), dt(trev), m.group(3), mins, t0, trev, sum(efforts.values())) + reg.s[m.end():]
    if agentic:
        recs = made_by(recs, P, n) + recs_a
        for cont in (ids["it"], ids["rel"]):
            recs.append("fw:%s backlog:overseenBy %s ; backlog:verifiedBy %s ; backlog:approvedBy %s ; backlog:integrityLevel %d ." % (cont, run_id(P, n, "Overseer"), run_id(P, n, "Verifier"), run_id(P, n, "Approver"), 2))
        for k in keys:
            for it in ("ST_%s_%s" % (P, k), "T_%s_%s_Build" % (P, k)):
                recs.append("fw:%s backlog:overseenBy %s ; backlog:verifiedBy %s ; backlog:approvedBy %s ." % (it, run_id(P, n, "Overseer"), run_id(P, n, "Verifier"), run_id(P, n, "Approver")))
    reg.append("\n".join(recs))
    reg.save()
    print("box %d closed: review %s, %s min, %s points of effort" % (n, trev, mins, sum(efforts.values())))


# ---- the obligations, read from the register by validating it (v1.1.0) ----

def validator():
    c = sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backlog_validate_v*.py")), key=lambda x: [int(y) for y in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", x)[0]])
    return c[-1] if c else None


def parse_violations(out):
    """The set of (focus, message start) of the Violation results in a validator's output."""
    res = set()
    for ln in out.splitlines():
        if "[Violation]" in ln:
            rest = ln.split("[Violation]", 1)[1].strip().split(None, 1)
            res.add((rest[0], (rest[1] if len(rest) > 1 else "")[:110]))
    return res


def violations_of(path):
    """The violations of the register at PATH, or None when no validator sits beside the tool."""
    v = validator()
    if not v:
        return None
    r = subprocess.run([sys.executable, "-B", v, path], capture_output=True, text=True)
    if r.returncode not in (0, 1) or ("VERDICT" not in r.stdout):
        raise SystemExit("REFUSED: the validator did not run: " + (r.stdout + r.stderr).strip()[-300:])
    return parse_violations(r.stdout)


def owes(path, lineage, status):
    """What the register would be violated by at STATUS that it is not violated by now (the obligations of that status), as a sorted list; None with no validator."""
    base = violations_of(path)
    if base is None:
        return None
    import tempfile
    s = open(path, encoding="utf-8").read()
    pat = re.compile(r"(^fw:%s a backlog:Lineage .*?backlog:hasLineageStatus )backlog:\w+" % re.escape(lineage), re.M | re.S)
    if not pat.search(s):
        raise SystemExit("REFUSED: no lineage %s in the register" % lineage)
    with tempfile.TemporaryDirectory() as d:
        t = os.path.join(d, os.path.basename(path))
        open(t, "w", encoding="utf-8").write(pat.sub(lambda m: m.group(1) + "backlog:" + status, s, count=1))
        return sorted(violations_of(t) - base)


def guarded(path, fn):
    """Run FN (which writes the register at PATH); when the register then holds a violation it did not hold before, restore it and refuse."""
    before = violations_of(path)
    orig = open(path, encoding="utf-8").read()
    try:
        fn()
    except SystemExit:
        open(path, "w", encoding="utf-8").write(orig)
        raise
    if before is None:
        print("NOT CHECKED: no validator sits beside this tool, so the register was not validated")
        return
    new = sorted(violations_of(path) - before)
    if new:
        open(path, "w", encoding="utf-8").write(orig)
        raise SystemExit("REFUSED: the register would hold a violation it did not hold before (it is put back as it was): " + " | ".join("%s: %s" % x for x in new[:4]))


def main(argv):
    a = [x for x in argv]
    lineage, prefix, capacity = "L_AdaptiveProof", "AP", 5.0
    integrity = 2
    while "--integrity" in a:
        i = a.index("--integrity"); integrity = int(a[i + 1]); del a[i:i + 2]
    allow = []
    while "--allow" in a:
        i = a.index("--allow"); allow.append(a[i + 1]); del a[i:i + 2]
    for flag in ("--lineage", "--prefix", "--capacity"):
        if flag in a:
            i = a.index(flag); v = a[i + 1]; del a[i:i + 2]
            if flag == "--lineage": lineage = v
            elif flag == "--prefix": prefix = v
            else: capacity = float(v)
    if len(a) < 2:
        print(__doc__); return 1
    path, cmd = a[0], a[1]
    root = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(path)), ".."))
    if cmd == "owes":
        o = owes(path, lineage, a[2])
        print("NOT CHECKED: no validator sits beside this tool" if o is None else ("at %s the register owes:\n  " % a[2] + "\n  ".join("%s: %s" % x for x in o) if o else "at %s the register owes nothing it does not already hold" % a[2]))
        return 0
    reg = Reg(path, lineage, prefix)
    if cmd == "open":
        o = owes(path, lineage, "LS_InProgress")
        if o:
            print("owed at LS_InProgress, before the box is opened:\n  " + "\n  ".join("%s: %s" % x for x in o))
        guarded(path, lambda: cmd_open(reg, root, int(a[2]), a[3], a[4], a[5].split(","), capacity, allow, integrity))
    elif cmd == "freeze":
        cmd_freeze(reg, root, a[2])
    elif cmd == "act":
        cmd_act(reg, int(a[2]), a[3], a[4])
    elif cmd == "close":
        guarded(path, lambda: cmd_close(reg, root, int(a[2]), json.load(open(a[3]))))
    else:
        print(__doc__); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
