#!/usr/bin/env python3
"""backlog_box_step v3.0.0 -- records the work of one box in order, with the clock of its run, and refuses the faults made by hand.

v3.0.0 (IPage handover box-tool-for-an-adopting-register, tried and refused on IPage's own register at commit 6832e82 before this fix, and re-run clean to the end after it):
IPage ran v2.0.0 on its real register (`05-lineage/interactive_page_lineage_abox_v0_70_0.ttl`, a Turtle writer's own layout, alphabetical properties, ending each story in
`satisfiesDeliverable` with no `producedByStage` anywhere) and it refused every story it holds, because `story_block` matched only a block ending in the literal text
`backlog:producedByStage fw:<x> .` -- a pattern this framework's own writer happens to produce and no other Turtle writer is bound to. `story_block` is now serialization-order-tolerant:
it takes the subject's whole statement, from its own line to the line before the next top-level subject (the same stop rule `cmd_open` already used for a planned box's own block),
whatever order its properties were written in and whichever one is last. This is still a text scan, not a literal rdflib graph parse; it is tolerant of property order and multi-line
values within one subject's own statement, which is what actually blocked IPage, not of a serializer that interleaves subjects. A full graph-native read is left as further hardening,
named honestly rather than claimed again without the proof to back it, since the same overclaim is what broke trust last time. The published-register lookup and the
governed-files check no longer assume `01-ontologies/`: `published_register_text` lists the register's own directory, and the register's own relative path is always exempt from
`governed_changed`, alongside `RECORD_FILES`, whatever directory it lives in.

Fixing `story_block` let `open` run far enough to expose three further bugs IPage's own test never reached, each the same mistake in a different place -- a BRSF-own naming habit
assumed instead of read from the register: (1) `is_agentic` looked only at the lineage's own block nearest `openedWithProfile`, missing a rule set recorded in a separate statement
for the same subject (which is how IPage records it, and -- found only once this was fixed and checked against this framework's own register too -- how part of this framework's own
Lineage 29 records it as well: `is_agentic` was wrongly False for it before this fix, not only for IPage's register). It now reads every one of the subject's own top-level statements
(`whole_subject_text`), wherever Turtle writes them. (2) The box's own Iteration was assumed to be named "It_<prefix>_<n>"; IPage's own planner had already named box 1's Iteration
"It4_1", no underscore, so `open` never recognised the pre-planned box and built a conflicting duplicate instead of opening the real one in place -- the exact fault C5 was supposed to
rule out, not actually proven before now. `resolve_it_id` now finds it by its own hasIdentifier suffix ("-BOX-<n>", the one every planner already writes) and its own
`belongsToLineage`, across every one of its statements, falling back to this tool's own naming only for a box not yet planned. (3) The register's own root individual, which the
kick-off step needs to name what it activates, was assumed to be named "Register"; `register_root_iri` now finds it by its own marker, `backlog:isRegisterRoot true`, wherever that
statement sits. C3 (stories found by their own link, not a name pattern), C5 (a planned box opens in place) and the agentic-ceremony detection are now proven directly against
IPage's own register below -- `open 1 "Box 1" ... Story4_D3,Story4_D4,Story4_D1,Story4_D2,Story4_D5 --lineage pcl:Lineage04 --prefix 4` runs to completion (exit 0; the only thing it
still reports is the unrelated, already-known "no pace to predict the end of box 1 from", which is the first-lineage forecast gap filed separately and left for that work) -- not a
fixture built by this session. C4, C6, C7, C8 were not disputed by IPage's report and are re-checked, not rebuilt. C9 (this framework's own register: re-checked read-only above,
including the `is_agentic` correction) and C10 (the proof ships with the tool) still stand as open work.

Lineage 21, deliverable D3. The faults came from boxes 4 to 9 of Lineage 20, each written down as a finding there:
  * a close composed in one pass          -> `close` refuses a box with no checkpoint recorded between its start and the close
  * a committed record edited in place    -> `close` refuses when a statement of the last published register is gone or changed
                                             (what moves is the state of an item, the status of the lineage and the version header of the file, so those are exempt)
  * work before the box was opened        -> `open` refuses when a governed file already differs from the last published tree;
                                             `close` refuses an artifact older than the box or a governed file older than the box
  * a name changed by hand                -> every identifier is made here from the box number and the story key, and `close` refuses when one the opening wrote is gone
  * the effort read from the wrong place  -> effort is read from `hasEffort` of the stories, or `hasCostEstimate`/`hasEffortEstimate` when that is absent (book-ontology handover, 2026-11-10), nowhere else

v1.12.0 (Lineage 29, story OpenPlanned, box 41): `open` opens a time-box that was planned in advance. A time-box recorded in the state Proposed (with its stories and its base plan) is moved to In progress and given its start; no second record of the time-box and no second base plan is written; its stories must already be members of it. A time-box that is already open or closed, is planned in another lineage, or whose stories are not members of it is refused; membership may be in the story's block or in a line appended after it; a planned time-box with no base plan is given one ("already has records"). Before, the tool could only create a time-box, so every time-box planned in advance was refused.
v1.11.0 (Lineage 29, story Grantor): the builder run that grants the verifier its access is recorded as acting for a person (prov:actedOnBehalfOf the owner), as the Owner ruled on 2026-11-04 (option 2: an agent may be the giver when it acts for a named person). The record states it; nothing verifies it.
v1.10.0 (Lineage 28, G187): `open` records a base plan for the box (a PlanBaseline: the box's start, and an end predicted from the effort of its stories and the pace delivered in earlier boxes, with the buffer written beside it) and checks the objectives the box moves against it; `baseline N` records one for a box opened without. A finished box is measured against its baseline, not refused for differing from it.
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
        backlog_box_step.py REGISTER.ttl baseline N               (record the base plan of an open box that has none)
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
RECORD_FILES = re.compile(r"^(04-documentation/CHANGELOG_v[\d_]+\.md|06-package-provenance/PROBE_INPUTS\.json|MANIFEST_SHA256\.txt|VERSION\.txt|RELEASE_METRICS\.txt)$")
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


def governed_changed(root, ref="origin/main", allow=(), reg=None):
    """Governed files of the package that differ from the published tree: changed, new or removed, record files excluded.
    REG, when given, is the register object (or a path) actually in use: its own relative path is exempt wherever it lives
    (C1/C4/C6 — RECORD_FILES no longer hardcodes "01-ontologies/backlog_abox...", since an adopting register may sit anywhere)."""
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
    reg_path = reg.path if hasattr(reg, "path") else reg
    reg_rel = os.path.relpath(os.path.abspath(reg_path), os.path.abspath(root)) if reg_path else None
    res = []
    for p in paths:
        q = p[len(pk):] if pk and p.startswith(pk) else p
        if "__pycache__" in q or q.endswith(".pyc"):
            continue
        if not RECORD_FILES.match(q) and q != reg_rel and q not in allow:
            res.append(q)
    return sorted(set(res))


def published_register_text(root, reg):
    """The newest register file of the published tree (paths are read relative to the package, which may sit inside a larger repository).
    The file-name stem (everything before _vN_N_N.ttl) is read from REG itself, not assumed to be the framework's own "backlog_abox" (C1/C2),
    and the directory searched is the register's own directory, not assumed to be "01-ontologies/" (C1/C4/C6: an adopting register may sit
    anywhere its own package lays its lineage files out, e.g. IPage's "05-lineage/")."""
    stem_m = re.match(r"(.+)_v\d+_\d+_\d+\.ttl$", os.path.basename(reg))
    stem = stem_m.group(1) if stem_m else "backlog_abox"
    reg_dir = os.path.relpath(os.path.dirname(os.path.abspath(reg)), root)
    names = subprocess.run(["git", "-C", root, "ls-tree", "--name-only", "origin/main", "./" + reg_dir + "/"], capture_output=True, text=True).stdout.split("\n")
    ab = [n for n in names if re.search(r"%s_v\d+_\d+_\d+\.ttl$" % re.escape(stem), n)]
    if not ab:
        raise SystemExit("REFUSED: the published tree holds no register file to compare with")
    ab.sort(key=lambda n: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", n)[0]])
    return subprocess.run(["git", "-C", root, "show", "origin/main:./" + ab[-1]], capture_output=True, text=True).stdout


# ---- the register's own namespace (C1/C2: never a hardcoded constant) ----

def resolve_lineage_ns(path, lineage_arg):
    """What (namespace IRI, short prefix token, local name) the register itself uses for LINEAGE_ARG.
    LINEAGE_ARG may be a bare local name (legacy: assumed to live in fw:, the framework's own namespace -- unchanged for the framework's own invocations),
    "PREFIX:Local" (PREFIX's IRI is read from the register's own @prefix line, never assumed), or a full "<http://...#Local>" IRI given on the command line."""
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^<([^>]+)#([^>#]+)>$", lineage_arg)
    if m:
        return m.group(1) + "#", "fw", m.group(2)
    if ":" in lineage_arg:
        pfx, local = lineage_arg.split(":", 1)
        mm = re.search(r"@prefix\s+%s:\s*<([^>]+)>\s*\." % re.escape(pfx), text)
        if not mm:
            raise SystemExit("REFUSED: the register declares no @prefix %s: -- its namespace cannot be read from a constant" % pfx)
        return mm.group(1), pfx, local
    return FW, "fw", lineage_arg


def _alias_in(text, ns, pfx):
    """Working copy: the register's own namespace, however it spells it, read as fw: (so the framework's own refusal logic, unchanged below, operates on it)."""
    if pfx != "fw":
        text = re.sub(r"(?<![A-Za-z0-9_])%s:" % re.escape(pfx), "fw:", text)
    if ns != FW:
        text = text.replace("<" + ns, "<" + FW)
    return text


def _alias_out(text, ns, pfx):
    """The reverse of _alias_in, applied just before anything is written back to disk."""
    if ns != FW:
        text = text.replace("<" + FW, "<" + ns)
    if pfx != "fw":
        text = re.sub(r"(?<![A-Za-z0-9_])fw:", pfx + ":", text)
    return text


# ---- the register file ----

STD_PREFIXES = {"rdfs": "http://www.w3.org/2000/01/rdf-schema#", "xsd": "http://www.w3.org/2001/XMLSchema#"}   # standard vocabularies the tool's own records use; an adopting register that never used one of them yet (or a serializer that drops an unused @prefix line) still needs it declared


def _ensure_prefixes(text):
    missing = [p for p, iri in STD_PREFIXES.items() if not re.search(r"@prefix\s+%s:\s*<" % re.escape(p), text)]
    if not missing:
        return text
    return "".join("@prefix %s: <%s> .\n" % (p, STD_PREFIXES[p]) for p in missing) + text


class Reg:
    def __init__(self, path, lineage, prefix):
        self.ns, self.pfx, local = resolve_lineage_ns(path, lineage)
        self.adopting = (self.ns != FW or self.pfx != "fw")
        self.path, self.L, self.P = path, "fw:" + local, prefix
        raw = open(path, encoding="utf-8").read()
        self.s = _ensure_prefixes(_alias_in(raw, self.ns, self.pfx) if self.adopting else raw)

    def has(self, ident):
        return re.search(r"^fw:%s\s" % re.escape(ident), self.s, re.M) is not None

    def append(self, text):
        self.s = self.s.rstrip("\n") + "\n" + text.rstrip("\n") + "\n"

    def story_ident(self, key):
        """The local name KEY actually refers to (C3): the legacy ST_<P>_<key> pattern this framework mints its own stories with, if a story of that
        name exists; otherwise KEY itself when a backlog:Story of that exact name already exists in the register -- so a story authored under the
        adopting register's own naming convention is found by its own identity, never forced into this framework's name pattern."""
        legacy = "ST_%s_%s" % (self.P, key)
        if re.search(r"^fw:%s\s+a\s+backlog:Story\b" % re.escape(legacy), self.s, re.M):
            return legacy
        if re.search(r"^fw:%s\s+a\s+backlog:Story\b" % re.escape(key), self.s, re.M):
            return key
        raise SystemExit("REFUSED: no story %s in the register" % key)

    def story_block(self, key):
        """The story's own statement, however its properties were ordered or which one its writer put last (C3/C5): from its own
        line to the line before the next top-level subject, the same stop rule used for a planned box's own block below."""
        sid = self.story_ident(key)
        m = re.search(r"^fw:%s a backlog:Story\b(?:(?!\nfw:|\n#).)*" % re.escape(sid), self.s, re.M | re.S)
        if not m:
            raise SystemExit("REFUSED: no story %s in the register" % key)
        return m

    def story_value(self, key, prop):
        m = re.search(r"backlog:%s ([^;\n]+?)\s*[;.](?=\s|$)" % prop, self.story_block(key).group(0))
        return m.group(1).strip() if m else None

    def effort_of_story(self, key):
        """A story's effort (book-ontology handover, 2026-11-10): hasEffort when present on the story itself, otherwise
        hasEffortEstimate of the backlog:CostEstimate it hasCostEstimate -- never zero or refused merely because a
        register built on the validator's own cost-estimate vocabulary carries effort that way instead. Read across
        every one of the story's own top-level statements, and then every one of that cost estimate's own, not only
        the block that first declares each one's type."""
        sid = self.story_ident(key)
        blk = whole_subject_text(self, sid)
        m = re.search(r"backlog:hasEffort\s+([^;\n]+?)\s*[;.](?=\s|$)", blk)
        if m:
            return float(m.group(1))
        m = re.search(r"backlog:hasCostEstimate\s+fw:([^;,.\s]+)", blk)
        if m:
            m2 = re.search(r"backlog:hasEffortEstimate\s+([^;\n]+?)\s*[;.](?=\s|$)", whole_subject_text(self, m.group(1)))
            if m2:
                return float(m2.group(1))
        raise SystemExit("REFUSED: story %s has no effort: neither hasEffort nor hasCostEstimate/hasEffortEstimate" % key)

    def set_state(self, key, old, new):
        m = self.story_block(key)
        blk = m.group(0)
        if "backlog:hasState backlog:%s ;" % old not in blk:
            raise SystemExit("REFUSED: story %s is not %s" % (key, old))
        self.s = self.s[:m.start()] + blk.replace("backlog:hasState backlog:%s ;" % old, "backlog:hasState backlog:%s ;" % new, 1) + self.s[m.end():]

    def to_disk(self, text):
        """TEXT, in this object's working (fw:) space, translated back to the register's own real spelling."""
        return _alias_out(text, self.ns, self.pfx) if self.adopting else text

    def save(self):
        open(self.path, "w", encoding="utf-8").write(self.to_disk(self.s))


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


def whole_subject_text(reg, subj):
    """Every top-level statement SUBJ (a bare local name, no "fw:" prefix) appears as, concatenated: an adopting register
    may write one subject's properties as a single block, or (as this framework's own register does, growing by appends
    over time) as several separate statements scattered through the file. A check that only reads the first such block
    misses whatever a later, separate statement adds -- the mistake this exists to avoid."""
    return "\n".join(m.group(0) for m in re.finditer(r"^fw:%s\b(?:(?!\nfw:|\n#).)*" % re.escape(subj), reg.s, re.M | re.S))


def effort_of_rdflib(g, B, subject):
    """A story's (or other work item's) effort read through rdflib (book-ontology handover, 2026-11-10): hasEffort
    when present, otherwise hasEffortEstimate of the backlog:CostEstimate it hasCostEstimate -- the same fallback as
    Reg.effort_of_story, for the rdflib-graph callers (cmd_baseline here, and backlog_date_plan) that read the register
    as a graph rather than as text."""
    from rdflib import URIRef
    v = g.value(subject, URIRef(B + "hasEffort"))
    if v is not None:
        return float(v)
    ce = g.value(subject, URIRef(B + "hasCostEstimate"))
    if ce is not None:
        v2 = g.value(ce, URIRef(B + "hasEffortEstimate"))
        if v2 is not None:
            return float(v2)
    return 0.0


def register_root_iri(reg):
    """The register's own root individual, as the full IRI the external lineage-steps tool (which reads the file
    directly, outside this tool's internal "fw:" alias) is given: found by its own marker, backlog:isRegisterRoot true,
    not assumed to be named "Register" (an adopting register may root itself under another name, e.g. IPage's own
    "pcl:Backlog"). The marker's own statement always carries its subject, whether that statement stands alone (this
    framework's own register writes it as a lone "fw:Register backlog:isRegisterRoot true .") or sits inside a longer
    block, so one pass over every top-level statement is enough -- no need to gather a subject's other statements too."""
    for m in re.finditer(r"^fw:(\S+)\b(?:(?!\nfw:|\n#).)*", reg.s, re.M | re.S):
        if re.search(r"backlog:isRegisterRoot\s+true\b", m.group(0)):
            return reg.ns + m.group(1)
    return reg.ns + "Register"


def resolve_it_id(reg, P, n, L):
    """The real identifier of box n's own Iteration (C5): a pre-planned box may already carry one in the register under its
    own naming convention, not this tool's assumed "It_P_n" (IPage's own planner, for instance, writes "It4_1", no underscore).
    Found by belonging to this lineage and an hasIdentifier ending "-BOX-<n>", the one suffix every planner of a box, this
    tool included, already writes -- never by guessing the local name from the box number. The two properties may sit in
    separate statements for the same subject (whole_subject_text), not only in the block that first declares the type.
    Falls back to this tool's own "It_P_n" pattern when no such Iteration is found (a box not yet planned, about to be
    created fresh by this run)."""
    for subj in sorted(set(re.findall(r"^fw:(\S+) a backlog:Iteration\b", reg.s, re.M))):
        blk = whole_subject_text(reg, subj)
        if ("backlog:belongsToLineage %s" % L) in blk and re.search(r'backlog:hasIdentifier\s+"[^"]*-BOX-%d"' % n, blk):
            return subj
    return "It_%s_%d" % (P, n)


def read_box(reg, n):
    ids = box_ids(reg.P, n)
    ids["it"] = resolve_it_id(reg, reg.P, n, reg.L)
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
    """True when the lineage's own statement adopts RS_AgentAccountability, wherever that rule sits among its properties (C9/C10):
    read over every one of the lineage's own top-level statements (whole_subject_text), not just its first block or the
    neighbourhood of backlog:openedWithProfile — an adopting register may carry the rule set on a separate property
    (e.g. backlog:adoptsRuleSet, listed earlier in an alphabetically-ordered serialization) rather than beside that one,
    and this framework's own register, which grows by separate appended statements for the same subject, may carry it in
    a later statement than the lineage's own type declaration."""
    return "RS_AgentAccountability" in whole_subject_text(reg, reg.L[3:] if reg.L.startswith("fw:") else reg.L)

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
    for f in governed_changed(root, reg=reg_path):
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

TOOL_VERSION = "3.0.0"

def has_own_kickoff(text, L):
    """True when the register holds a kick-off of this lineage itself; the kick-off of another lineage does not count (Lineage 24, held by a probe in Lineage 25)."""
    return re.search(r"backlog:kicksOffLineage\s+(?:fw:|<http://example.org/backlog-framework-register#)%s\b" % re.escape(L[3:]), text) is not None


def _date_plan():
    import importlib.util
    f = sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backlog_date_plan_v*.py")), key=lambda x: [int(y) for y in re.findall(r"_v(\d+)_(\d+)_(\d+)", x)[0]])
    if not f: return None
    sp = importlib.util.spec_from_file_location("backlog_date_plan_mod", f[-1]); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def cmd_baseline(reg, n, buffer=1.5):
    """The base plan of box n: its start, and an end predicted from the effort of its stories and the pace delivered in earlier boxes. Refused when the register holds no pace to predict from."""
    P = reg.P
    ids = box_ids(P, n)
    ids["it"] = resolve_it_id(reg, P, n, reg.L)
    bid = "PB_%s_%d" % (P, n)
    if not reg.has(ids["it"]):
        raise SystemExit("REFUSED: box %d is not open" % n)
    if reg.has(bid):
        raise SystemExit("REFUSED: box %d already has a base plan; moving it is a Rebaseline decided by the Owner" % n)
    dp = _date_plan()
    if dp is None:
        raise SystemExit("REFUSED: no backlog_date_plan beside this tool, so no pace to predict from")
    from rdflib import Graph, URIRef
    reg.save()
    g = Graph(); g.parse(reg.path, format="turtle")
    B = dp.B
    it = URIRef(reg.ns + ids["it"])
    vel_s = dp.samples(g)
    if not vel_s:
        raise SystemExit("REFUSED: the register holds no pair of consecutive boxes with delivered effort: there is no pace to predict the end of box %d from" % n)
    import statistics
    vel = statistics.median(vel_s)
    stories = [g.value(ev, URIRef(B + "plansItem")) for ev in g.subjects(URIRef(B + "plannedInto"), it)]
    pts = sum(effort_of_rdflib(g, B, st) for st in stories if st is not None)
    start = g.value(it, URIRef(B + "iterationStart"))
    t0 = dp.dt(start)
    end = t0 + datetime.timedelta(hours=(pts / vel) * buffer)
    tb = tick()
    reg.append("fw:%s a backlog:PlanBaseline ; rdfs:label \"Base plan of box %d\"@en ;\n    backlog:baselineFor fw:%s ; backlog:baselinedAt %s ; backlog:isCurrentBaseline true ;\n"
               "    backlog:hasBaselineStart %s ; backlog:hasBaselineEnd %s ;\n"
               "    rdfs:comment \"Predicted end of the box: %s points of its stories at the median delivered pace of %.2f points per elapsed hour (%d pair(s) of earlier boxes), times a buffer of %s.\"@en ."
               % (bid, n, ids["it"], dt(tb), dt(t0.strftime("%Y-%m-%dT%H:%M:%SZ")), dt(end.strftime("%Y-%m-%dT%H:%M:%SZ")), pts, vel, len(vel_s), buffer))
    reg.save()
    print("base plan of box %d: ends %s (%s points at %.2f points per hour, buffer %s)" % (n, end.strftime("%Y-%m-%d %H:%MZ"), pts, vel, buffer))
    # the objectives these stories move, against the end of the box
    for st in stories:
        for obj in g.subjects(URIRef(B + "metricMovableBy"), st):
            for cp in g.objects(obj, URIRef(B + "hasCheckpoint")):
                d = dp.dt(g.value(cp, URIRef(B + "checkpointDate")))
                if d and d < end:
                    print("WARNING: the checkpoint %s of %s is dated %s, before this box is planned to end (%s)" % (str(cp).rsplit("#", 1)[-1], str(obj).rsplit("#", 1)[-1], d.strftime("%Y-%m-%d %H:%MZ"), end.strftime("%Y-%m-%d %H:%MZ")))


def cmd_open(reg, root, n, title, goal, keys, capacity, allow=(), integrity=2):
    P, L = reg.P, reg.L
    ids = box_ids(P, n)
    ids["it"] = resolve_it_id(reg, P, n, L)   # C5: a planned box's real identifier, not this tool's assumed "It_P_n"
    planned = None
    if reg.has(ids["it"]):
        stmt = re.search(r"^fw:%s a backlog:Iteration ;(?:(?!\nfw:|\n#).)*" % ids["it"], reg.s, re.M | re.S).group(0)
        if "backlog:hasState backlog:Proposed" not in stmt or "backlog:iterationStart" in stmt:
            raise SystemExit("REFUSED: box %d already has records" % n)
        if ("backlog:belongsToLineage %s" % L) not in stmt:
            raise SystemExit("REFUSED: box %d is planned in another lineage" % n)
        if not (re.search(r"backlog:hasState\s+backlog:Proposed\s*;", stmt) and re.search(r"backlog:hasCapacity\s+[\d.]+\s*;", stmt)):
            raise SystemExit("REFUSED: box %d is planned with its state and capacity laid out in a way this tool cannot open in place" % n)
        planned = True
        for k in keys:   # a story is a member of a planned box in its own block or in a line appended after it (C3: found by its own identity, never forced into ST_<P>_<key>)
            sidk = reg.story_ident(k)
            if not (re.search(r"backlog:memberOfContainer[^;]*\bfw:%s\b" % ids["it"], reg.story_block(k).group(0))
                    or re.search(r"^fw:%s backlog:memberOfContainer[^.\n]*\bfw:%s\b" % (re.escape(sidk), ids["it"]), reg.s, re.M)):
                raise SystemExit("REFUSED: story %s is not a member of the planned box %d" % (k, n))
    subprocess.run(["git", "-C", root, "fetch", "-q", "origin"], capture_output=True)
    dirty = governed_changed(root, allow=allow, reg=reg)
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
        r = subprocess.run([sys.executable, steps, "plan", reg.path, "--lineage", reg.ns + reg.L[3:], "--container", register_root_iri(reg), "--by", "Builder"], capture_output=True, text=True)
        if r.returncode:
            raise SystemExit("REFUSED: the plan step failed: " + (r.stdout + r.stderr)[-400:])
        print(r.stdout.strip())
        raw = open(reg.path, encoding="utf-8").read()
        reg.s = _ensure_prefixes(_alias_in(raw, reg.ns, reg.pfx) if reg.adopting else raw)
    m = re.search(r"^%s a backlog:Lineage .*?backlog:hasLineageStatus backlog:(\w+)" % re.escape(L), reg.s, re.M | re.S)
    if m and m.group(1) in ("LS_Backlogged",):
        reg.s = reg.s[:m.start(1)] + "LS_InProgress" + reg.s[m.end(1):]
    # refinement and readiness, one second apart, before the box is planned
    sid = {k: reg.story_ident(k) for k in keys}   # C3: the local name each key actually refers to, resolved once
    recs = []
    for k in keys:
        t1 = tick()
        eff = reg.effort_of_story(k)
        recs.append("fw:Ref_%s_%d_%s a backlog:RefinementEvent ; backlog:hasWorkKind backlog:WorkKind_Preparation ; backlog:refines fw:%s ; backlog:refinedAt %s ;\n"
                    "    backlog:hasRefinementOutcome \"Groomed for box %d: the acceptance criterion reads as a test, the effort is %s points, and the change is to shapes, tooling or records with probe checks.\" ;\n"
                    "    backlog:refinedBy backlog:Builder ; backlog:addressesConcern backlog:Concern_Architecture ." % (P, n, k, sid[k], dt(t1), n, eff))
        recs.append("fw:Ev%d_ST_%s_%s_T_Refine a backlog:TransitionEvent ; backlog:transitionedItem fw:%s ; backlog:viaTransition backlog:T_Refine ; backlog:transitionedAt %s ; backlog:transitionedBy backlog:Builder ; backlog:hasTransitionNote \"Groomed and made ready for box %d.\" ." % (n, P, k, sid[k], dt(t1), n))
        t2 = tick()
        recs.append("fw:Chk_%s_%d_%s a backlog:ReadinessCheck ; rdfs:label \"Readiness of the story %s\"@en ;\n    backlog:checksReadinessOf fw:%s ; backlog:readinessCheckedAt %s ;\n    backlog:hasReadinessCriterion fw:K_%s_%d_%s_AC , fw:K_%s_%d_%s_Size , fw:K_%s_%d_%s_Dep , fw:K_%s_%d_%s_Input ." % (P, n, k, k, sid[k], dt(t2), P, n, k, P, n, k, P, n, k, P, n, k))
        for suf, lab in (("AC", "The acceptance criterion reads as a test the validator can run"), ("Size", "The effort is estimated and fits the box"), ("Dep", "Nothing it depends on is open"), ("Input", "No decision of the Owner is waited on")):
            recs.append("fw:K_%s_%d_%s_%s a backlog:ReadinessCriterion ; rdfs:label \"%s\"@en ; backlog:criterionMet true ." % (P, n, k, suf, lab))
    tp = tick()
    recs.append("fw:%s a backlog:DeploymentPlan ; backlog:hasWorkKind backlog:WorkKind_Planning ; backlog:deploymentPlanForBox fw:%s ; backlog:plansDeploymentUnit fw:%s ; backlog:deploymentPlannedAt %s ." % (ids["dplan"], ids["it"], ids["rel"], dt(tp)))
    t0 = tick()
    if planned is None:
        recs.append("fw:%s a backlog:Iteration ; backlog:hasIdentifier \"%s-BOX-%d\" ; backlog:hasTitle \"%s\" ;\n    backlog:hasSprintGoal \"%s\" ;\n"
                    "    backlog:hasState backlog:InProgress ; backlog:iterationStart %s ;\n    backlog:hasCapacity %s ; backlog:belongsToLineage %s%s ." % (ids["it"], P, n, esc(title), esc(goal), dt(t0), float(capacity), L, (" ;\n    rdfs:comment \"Disclosed at the opening: these governed files already differed from the published tree, so work on them began before the box was open: %s.\"@en" % ", ".join(allow)) if allow else ""))
    else:  # the planned time-box is opened in place: its state and its start, nothing else
        pm = re.search(r"^fw:%s a backlog:Iteration ;(?:(?!\nfw:|\n#).)*?backlog:hasState\s+backlog:Proposed\s*;" % ids["it"], reg.s, re.M | re.S)
        blk = re.sub(r"backlog:hasState\s+backlog:Proposed\s*;", "backlog:hasState backlog:InProgress ; backlog:iterationStart %s ;" % dt(t0), pm.group(0), count=1)
        reg.s = reg.s[:pm.start()] + blk + reg.s[pm.end():]
    tpl = tick()
    recs.append("fw:%s a backlog:SprintPlanningCeremony ; backlog:hasWorkKind backlog:WorkKind_Planning ; backlog:ceremonyFor fw:%s ; backlog:heldAt %s ;\n    backlog:includesPlanningEvent %s ." % (ids["plan"], ids["it"], dt(tpl), " , ".join("fw:Plan_%s_%d_%s" % (P, n, k) for k in keys)))
    for k in keys:
        tq = tick()
        recs.append("fw:Plan_%s_%d_%s a backlog:PlanningEvent ; rdfs:label \"Story %s planned into box %d\"@en ;\n    backlog:plansItem fw:%s ; backlog:plannedInto fw:%s ; backlog:plannedAt %s ; backlog:plannedBy backlog:Builder ; backlog:producesTask fw:T_%s_%s_Build ." % (P, n, k, k, n, sid[k], ids["it"], dt(tq), P, k))
        tdec = tick(); tck = tick(); trdy = tick(); tsk = tick(); tss = tick()
        recs.append("fw:T_%s_%s_Build a backlog:ExecutionTask ; backlog:hasIdentifier \"T-%s-%s-BUILD\" ; backlog:hasState backlog:InProgress ;\n"
                    "    backlog:hasTaskType backlog:Task_Implementation ; backlog:responsible %s ; backlog:memberOfContainer fw:%s ; backlog:appliesDefinitionOfDone fw:DoD_%s ; backlog:belongsToLineage %s ;\n"
                    "    backlog:hasExecutionModality backlog:Mode_Automated ; backlog:startedAt %s ." % (P, k, P, k.upper(), DEFAULT_EXEC, ids["it"], P, L, dt(tsk)))
        recs.append("fw:Chk_%s_%d_T_%s a backlog:ReadinessCheck ; rdfs:label \"Readiness of the task of story %s\"@en ;\n    backlog:checksReadinessOf fw:T_%s_%s_Build ; backlog:readinessCheckedAt %s ;\n    backlog:hasReadinessCriterion fw:K_%s_%d_T_%s_AC , fw:K_%s_%d_T_%s_Size , fw:K_%s_%d_T_%s_Dep , fw:K_%s_%d_T_%s_Input ." % (P, n, k, k, P, k, dt(tck), P, n, k, P, n, k, P, n, k, P, n, k))
        for suf, lab in (("AC", "The task builds what the acceptance criterion tests"), ("Size", "The effort is estimated and fits the box"), ("Dep", "Nothing it depends on is open"), ("Input", "No decision of the Owner is waited on")):
            recs.append("fw:K_%s_%d_T_%s_%s a backlog:ReadinessCriterion ; rdfs:label \"%s\"@en ; backlog:criterionMet true ." % (P, n, k, suf, lab))
        recs.append("fw:%s backlog:decomposesInto fw:T_%s_%s_Build ; backlog:memberOfContainer fw:%s ; backlog:appliesDefinitionOfDone fw:DoD_%s ; backlog:hasApplicableConcern backlog:Concern_Architecture ; backlog:startedAt %s ." % (sid[k], P, k, ids["it"], P, dt(tss)))
        for via, t in (("T_Decompose", tdec), ("T_RefinedToReady", trdy), ("T_Start", tsk)):
            recs.append("fw:Ev%d_T_%s_%s_Build_%s a backlog:TransitionEvent ; backlog:transitionedItem fw:T_%s_%s_Build ; backlog:viaTransition backlog:%s ; backlog:transitionedAt %s ; backlog:transitionedBy backlog:Builder ." % (n, P, k, via, P, k, via, dt(t)))
        recs.append("fw:Ev%d_ST_%s_%s_T_Start a backlog:TransitionEvent ; backlog:transitionedItem fw:%s ; backlog:viaTransition backlog:T_Start ; backlog:transitionedAt %s ; backlog:transitionedBy backlog:Builder ." % (n, P, k, sid[k], dt(tss)))
        reg.set_state(k, "Proposed", "InProgress")
    recs.append("fw:%s a backlog:ControlActivity ; rdfs:label \"Validate the register and run the probes before the box is reviewed\"@en ;\n    backlog:hasWorkKind backlog:WorkKind_Control ; backlog:plannedInBox fw:%s ." % (ids["act"], ids["it"]))
    if is_agentic(reg):
        recs = [r.replace("backlog:responsible " + DEFAULT_EXEC, "backlog:responsible " + run_id(P, n, "Builder")) for r in made_by(recs, P, n)]
        recs.insert(0, agent_run(P, n, "Builder", t0, TOOL_VERSION))
        for k in keys:
            recs.append("fw:%s backlog:responsible %s ; backlog:integrityLevel %d ." % (sid[k], run_id(P, n, "Builder"), integrity))
            recs.append("fw:T_%s_%s_Build backlog:integrityLevel %d ." % (P, k, integrity))
        defs = agent_defs(reg)
        if defs: recs.insert(0, defs.rstrip("\n"))
    reg.append("\n# ---- box %d of %s: opened %s by backlog_box_step ----\n" % (n, L, t0) + "\n".join(recs))
    reg.save()
    print("box %d opened at %s; stories %s now InProgress" % (n, t0, ", ".join(keys)))
    if planned is not None:
        if reg.has("PB_%s_%d" % (P, n)):
            print("box %d was planned in advance: its base plan stands" % n)
            return
        print("box %d was planned in advance with no base plan: one is recorded now" % n)
    try:
        cmd_baseline(reg, n)
    except SystemExit as e:
        print("NO BASE PLAN: " + str(e))


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
    # C4: the box's planning events are found by the planning ceremony's own link (includesPlanningEvent), not by scanning for whatever Plan_ records
    # still happen to exist -- so a planning event deleted outright, not merely renamed, is refused too, and "no records found" is never read as "nothing to close".
    plan_blk = re.search(r"^fw:%s a backlog:SprintPlanningCeremony .*?backlog:includesPlanningEvent ([^.\n]+) \." % re.escape(ids["plan"]), reg.s, re.M | re.S)
    if not plan_blk:
        raise SystemExit("REFUSED: box %d has no planning ceremony linking its planning events" % n)
    expected_plans = [x.strip() for x in plan_blk.group(1).split(",")]
    missing_plans = [p for p in expected_plans if not reg.has(p.split(":", 1)[-1])]
    if missing_plans:
        raise SystemExit("REFUSED: %d planning event(s) linked from the planning ceremony of box %d are gone: %s" % (len(missing_plans), n, ", ".join(missing_plans)))
    keys = []
    for p in expected_plans:
        pid = p.split(":", 1)[-1]
        pm = re.search(r"^fw:%s a backlog:PlanningEvent .*?backlog:plansItem fw:(\S+) ;" % re.escape(pid), reg.s, re.M | re.S)
        if not pm:
            raise SystemExit("REFUSED: the planning event %s does not link to a story (plansItem)" % pid)
        km = re.match(r"Plan_%s_%d_(.+)$" % (re.escape(P), n), pid)
        keys.append(km.group(1) if km else pm.group(1))
    gone = [i for i in opening_ids(P, n, keys) if not reg.has(i)]
    if gone:
        raise SystemExit("REFUSED: %d identifier(s) written at the opening of box %d are gone, so a name was changed by hand: %s" % (len(gone), n, ", ".join(gone[:3])))
    if not re.search(r"^fw:Ckp_%s_%d_\d+ " % (P, n), reg.s, re.M):
        raise SystemExit("REFUSED: no checkpoint was recorded between the start of box %d and its close, so the close would be composed in one pass" % n)
    pub = published_register_text(root, reg.path)
    pub = _ensure_prefixes(_alias_in(pub, reg.ns, reg.pfx) if reg.adopting else pub)
    lost = committed_lost(pub, reg.s)
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
    stale = files_before([os.path.join(root, f) for f in governed_changed(root, allow=allow, reg=reg) if os.path.exists(os.path.join(root, f))], t0)
    if stale:
        raise SystemExit("REFUSED: governed files changed before the box was opened: " + ", ".join(os.path.relpath(x, root) for x in stale))
    efforts = {k: reg.effort_of_story(k) for k in keys}
    sid = {k: reg.story_ident(k) for k in keys}   # C3: the local name each key actually refers to, resolved once
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
            # C8: the monitor is called with full IRIs, not bare local names that would be ambiguous as to which register's namespace they belong to.
            closing_iris = ",".join("<%s%s>" % (reg.ns, x) for x in ([sid[k] for k in keys] + ["T_%s_%s_Build" % (P, k) for k in keys] + [ids["it"], ids["rel"]]))
            mr = subprocess.run([sys.executable, mon[-1], reg.path, "--lineage", "<%s%s>" % (reg.ns, reg.L[3:]), "--closing", closing_iris], capture_output=True, text=True)
            esc_list = escalation_items(mr.stdout)
            esc_n = "the agent monitor ran and its escalation list was %s" % ("empty" if mr.returncode == 0 else "not empty (exit %d); each item is a finding of this box" % mr.returncode)
        tov, tapp = tick(), tick()
        cfg = "fw:Config_%s_%d_Verifier" % (P, n)
        recs_a = [BRIDGE if "agsys:StartWay" not in reg.s else "",
                  "fw:Session_%s_%d_Verifier a prov:Agent ; rdfs:label \"%s\"@en ." % (P, n, esc(v["agent"])),
                  "fw:Grant_%s_%d_Verifier a agsys:AccessGrant ; agsys:grantedBy %s ; agsys:viaRoute fw:AccessRoute_FileSystem ; agsys:grantedPlace \"the governed files and the register of the package, as the builder left them when the brief was fixed\" ; agsys:grantMode \"read-only\" ; agsys:grantedAt %s ." % (P, n, run_id(P, n, "Builder"), dt(fz["frozen_at"])),
                  "%s prov:actedOnBehalfOf backlog:%s ." % (run_id(P, n, "Builder"), "Executor_YusufAltunel"),
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
        recs.append("fw:Ev%d_ST_%s_%s_T_Complete a backlog:TransitionEvent ; backlog:transitionedItem fw:%s ; backlog:viaTransition backlog:T_Complete ; backlog:transitionedAt %s ; backlog:transitionedBy backlog:Builder ." % (n, P, k, sid[k], dt(tf)))
        recs.append("fw:Ev_%s_%s a backlog:TestEvidence ; rdfs:label \"The check for story %s\"@en ;\n    backlog:evidenceVerified true ; backlog:hasTestId \"%s\" ;\n    backlog:hasTestSpec \"%s\" ;\n    backlog:attestsCriterion fw:AC_%s_%s ;\n    backlog:hasVerificationMethod \"%s\" ;\n    backlog:verifiedAt %s ; backlog:verifiedByTool \"%s\" ;\n    backlog:satisfiedByArtifact \"%s\" ; backlog:belongsToLineage %s ." % (P, k, k, k, s["artifact"], P, k, esc(s["method"]), dt(tf), esc(s["tool"]), s["artifact"], L))
        recs.append("fw:AC_%s_%s backlog:satisfiedByArtifact \"%s\" ." % (P, k, s["artifact"]))
        recs.append("fw:H_%s_%s a backlog:TestHarness ; rdfs:label \"Harness for story %s\"@en ;\n    backlog:harnessFor fw:%s ; backlog:hasHarnessEvidence fw:Ev_%s_%s ; backlog:harnessComplete true ;\n    backlog:hasRationale \"%s\" ." % (P, k, k, sid[k], P, k, esc(s["harness"])))
        recs.append("fw:Demo_%s_%s a backlog:DemoRun ; backlog:hasWorkKind backlog:WorkKind_Control ; backlog:demonstratesItem fw:%s ; backlog:demonstratedAgainst fw:AC_%s_%s ; backlog:demoAt %s ;\n    backlog:hasDemoShown \"%s\" ;\n    backlog:hasDemoResult \"%s\" ." % (P, k, sid[k], P, k, dt(tick()), esc(s["demo"]), esc(s["result"])))
        reg.set_state(k, "InProgress", "Done")
        m = re.search(r"^fw:T_%s_%s_Build a backlog:ExecutionTask .*?backlog:startedAt \"[^\"]+\"\^\^xsd:dateTime \." % (P, k), reg.s, re.M | re.S)
        blk = m.group(0).replace("backlog:hasState backlog:InProgress ;", "backlog:hasState backlog:Done ;", 1)
        blk = blk[:-1].rstrip() + " ; backlog:finishedAt %s ; backlog:hasEvidence fw:Ev_%s_%s ." % (dt(tf), P, k)
        reg.s = reg.s[:m.start()] + blk + reg.s[m.end():]
        recs.append("fw:%s backlog:finishedAt %s ; backlog:lastAuditedAt %s ; backlog:hasEvidence fw:Ev_%s_%s ; backlog:memberOfContainer fw:%s ." % (sid[k], dt(tf), dt(tf), P, k, ids["rel"]))
    trun = tick()
    recs.append("fw:%s a backlog:ControlRun ; backlog:runOfActivity fw:%s ; backlog:ranAt %s ;\n    backlog:hasRunResult \"%s\" ." % (ids["run"], ids["act"], dt(trun), esc(spec["run_result"])))
    trev = tick()
    recs.append("fw:%s a backlog:SprintReviewCeremony ; backlog:hasWorkKind backlog:WorkKind_Closure ;\n    backlog:ceremonyFor fw:%s ; backlog:heldAt %s ; backlog:reviewsCeremony fw:%s ;\n    backlog:closesIteration fw:%s ; backlog:closesStory %s ." % (ids["review"], ids["it"], dt(trev), ids["plan"], ids["it"], " , ".join("fw:%s" % sid[k] for k in keys)))
    trel = tick()
    recs.append("fw:%s a backlog:DeploymentUnit ;\n    backlog:hasIdentifier \"%s-REL-%d\" ; backlog:hasTitle \"%s\" ;\n    backlog:hasState backlog:Done ; backlog:hasDeploymentDate %s ;\n    backlog:deploysFrom fw:%s ; backlog:deploysItem %s ;\n    backlog:decidedBy backlog:Builder ; backlog:hasSelectionBasis backlog:Sel_Committed ; backlog:belongsToLineage %s ." % (ids["rel"], P, n, esc(spec["release_title"]), dt(trel), ids["it"], " , ".join("fw:%s" % sid[k] for k in keys), L))
    if "plansDeploymentUnit fw:%s " % ids["rel"] not in reg.s:  # the plan names its unit at the opening (G170); the unit may not carry unfinished work, so it is written at the close
        recs.append("fw:%s backlog:plansDeploymentUnit fw:%s ." % (ids["dplan"], ids["rel"]))
    fks = []
    for f in spec["findings"]:
        fks.append("fw:Find_%s_%s" % (P, f["key"]))
        recs.append("fw:Find_%s_%s a backlog:RetrospectiveFinding ;\n    backlog:hasFindingScope backlog:Scope_LineageLocal ;\n    backlog:relatesToWorkItem fw:%s ;\n    backlog:hasRootCause \"%s\" ;\n    backlog:hasRemedy \"%s\" ." % (P, f["key"], sid[f.get("story", keys[0])], esc(f["root_cause"]), esc(f["remedy"])))
    if agentic:
        ans = spec.get("escalation_answer", "Open: raised by the overseer and not answered in this box.")
        for i, line in enumerate(esc_list, 1):
            if ('hasRootCause "%s"' % esc(line)) in reg.s:
                continue
            fks.append("fw:Find_%s_Esc%d_%d" % (P, n, i))
            recs.append("fw:Find_%s_Esc%d_%d a backlog:RetrospectiveFinding ;\n    backlog:hasFindingScope backlog:Scope_LineageLocal ;\n    backlog:relatesToWorkItem fw:%s ;\n    backlog:hasRootCause \"%s\" ;\n    backlog:hasRemedy \"%s\" ." % (P, n, i, sid[keys[0]], esc(line), esc(ans)))
    tret = tick()
    # pre-existing defect, fixed here (not in v1.12.0, kept as the historical baseline): with no findings at all, fks is empty and
    # " , ".join(fks) is "", which used to write "backlog:producesFinding  ." -- a predicate with no object, invalid Turtle that a
    # real RDF parser (rdflib, a SHACL validator, the agent monitor) refuses to read. The clause is now simply omitted when there
    # is nothing to name, exactly as every other optional clause in this tool already does.
    recs.append("fw:%s a backlog:SprintRetrospective ; backlog:hasWorkKind backlog:WorkKind_Closure ;\n    backlog:followsReview fw:%s ; backlog:heldAt %s%s ." % (ids["retro"], ids["review"], dt(tret), " ; backlog:producesFinding " + " , ".join(fks) if fks else ""))
    for o in spec["observations"]:
        recs.append("fw:Obs_%s_%s_B%d a backlog:MetricObservation ; rdfs:label \"After box %d: %s\"@en ;\n    backlog:observesMetric fw:Metric_%s_%s ; backlog:observationFor fw:Obj_%s_%s ; backlog:hasObservedValue %s ; backlog:observedAt %s ;\n    backlog:hasObservationMethod \"%s\" ." % (P, o["obj"], n, n, o["obj"], P, o["obj"], P, o["obj"], float(o["value"]), dt(trun), esc(o["method"])))
    mins = round((parse_t(tret) - parse_t(t0)).total_seconds() / 60, 1)
    # the InProgress/start and the capacity are read and rewritten independently of their order in the file (C1/C5): capacity's own value is never moved, so its position never matters
    m = re.search(r"^fw:%s a backlog:Iteration .*?backlog:hasState\s+backlog:InProgress\s*;\s*backlog:iterationStart\s+(\"[^\"]+\"\^\^xsd:dateTime)\s*;" % ids["it"], reg.s, re.M | re.S)
    if not m:
        raise SystemExit("REFUSED: box %d has no InProgress iteration with a start to close" % n)
    new_state = ('backlog:hasState backlog:Done ; backlog:iterationStart %s ;\n    backlog:iterationEnd %s ;\n    backlog:hasObservedDuration %s ; backlog:hasDurationSource "Wall clock from the start of the box to its review, both taken from the register: %s to %s. Effort of the stories read from hasEffort, or hasCostEstimate/hasEffortEstimate when that is absent: %s points." ;'
                 % (m.group(1), dt(trev), mins, t0, trev, sum(efforts.values())))
    blk = re.sub(r"backlog:hasState\s+backlog:InProgress\s*;\s*backlog:iterationStart\s+\"[^\"]+\"\^\^xsd:dateTime\s*;", new_state, m.group(0), count=1)
    reg.s = reg.s[:m.start()] + blk + reg.s[m.end():]
    if agentic:
        recs = made_by(recs, P, n) + recs_a
        for cont in (ids["it"], ids["rel"]):
            recs.append("fw:%s backlog:overseenBy %s ; backlog:verifiedBy %s ; backlog:approvedBy %s ; backlog:integrityLevel %d ." % (cont, run_id(P, n, "Overseer"), run_id(P, n, "Verifier"), run_id(P, n, "Approver"), 2))
        for k in keys:
            for it in (sid[k], "T_%s_%s_Build" % (P, k)):
                recs.append("fw:%s backlog:overseenBy %s ; backlog:verifiedBy %s ; backlog:approvedBy %s ." % (it, run_id(P, n, "Overseer"), run_id(P, n, "Verifier"), run_id(P, n, "Approver")))
    reg.append("\n".join(recs))
    reg.save()
    print("box %d closed: review %s, %s min, %s points of effort" % (n, trev, mins, sum(efforts.values())))


# ---- the obligations, read from the register by validating it (v1.1.0) ----

def validator():
    """The newest backlog_validate_v*.py. Looked up first in BRSF_ROOT's own 03-tooling (an env var or --brsf-root, C7: a declared path, never
    assumed), then, for the framework's own invocations, beside this tool itself (unchanged default)."""
    roots = []
    env_root = os.environ.get("BRSF_ROOT")
    if env_root:
        roots.append(os.path.join(env_root, "03-tooling"))
    roots.append(os.path.dirname(os.path.abspath(__file__)))
    for r in roots:
        c = sorted(glob.glob(os.path.join(r, "backlog_validate_v*.py")), key=lambda x: [int(y) for y in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", x)[0]])
        if c:
            return c[-1]
    return None


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
    ns, pfx, local = resolve_lineage_ns(path, lineage)
    pat = re.compile(r"(^%s:%s a backlog:Lineage .*?backlog:hasLineageStatus )backlog:\w+" % (re.escape(pfx), re.escape(local)), re.M | re.S)
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
    for flag in ("--lineage", "--prefix", "--capacity", "--brsf-root"):
        if flag in a:
            i = a.index(flag); v = a[i + 1]; del a[i:i + 2]
            if flag == "--lineage": lineage = v
            elif flag == "--prefix": prefix = v
            elif flag == "--brsf-root": os.environ["BRSF_ROOT"] = v   # C7: a declared path to the framework checkout, read by validator()
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
    elif cmd == "baseline":
        guarded(path, lambda: cmd_baseline(reg, int(a[2])))
    elif cmd == "act":
        cmd_act(reg, int(a[2]), a[3], a[4])
    elif cmd == "close":
        guarded(path, lambda: cmd_close(reg, root, int(a[2]), json.load(open(a[3]))))
    else:
        print(__doc__); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
