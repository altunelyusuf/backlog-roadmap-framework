#!/usr/bin/env python3
"""backlog_guard_claude_hook v1.1.0 -- Claude Code hook dispatcher for the work guard (ruling G101).

Registered by backlog_guard_install in .claude/settings.json for:
  SessionStart  re-arms the git hooks in this clone (they do not travel with a clone), then prints the lineage's start-gate state and the NEXT REQUIRED ACT into the session's context, so the rule
                is in front of the session at every start and after every compaction, not remembered
  PreToolUse    Edit | Write | MultiEdit | NotebookEdit on a governed work path: exit 2 (block) unless the active
                lineage is READY. Bash: a command that writes a governed work path (redirect, sed -i, tee, cp, mv, rm,
                patch, git apply) is blocked the same way. The Bash test is a heuristic, a best effort; the
                commit-msg hook and the CI range check are the backstop that cannot be argued with.

v1.1.0 (G123): the hook decides whether a call touches a governed path from the configuration alone; rdflib is needed only
when a governed path is touched or the session starts, so the command that installs rdflib is never blocked by its absence.
The Bash test judges the targets of redirects and the operands of the write commands, not every word of a command that
happens to contain a redirect: `grep -rn x app > /tmp/o` writes /tmp/o, not app.

Fails CLOSED: any error inside the guard blocks (exit 2) with the reason; a hook that fails open is the drift itself.
Claude Code protocol: JSON on stdin; exit 2 blocks and stderr is returned to the model; stdout of SessionStart is added
to the context.
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def load_guard():
    import importlib.util, glob
    sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
    c = sorted(g for g in glob.glob(os.path.join(HERE, "backlog_work_guard_v*.py")) if "probe" not in os.path.basename(g))
    spec = importlib.util.spec_from_file_location("backlog_work_guard", sorted(c, key=sv)[-1])
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


WRITE = re.compile(r"(>>?\s*\S+|\bsed\s+-i|\btee\b|\bcp\b|\bmv\b|\brm\b|\bpatch\b|\bgit\s+apply\b|\btouch\b)")
REDIR = re.compile(r"(?<![0-9&<])\d?>>?(?!&)\s*([^\s;&|<>]+)")
WCMD = {"tee", "mv", "rm", "patch", "touch", "cp", "sed", "install", "ln", "truncate", "dd"}


def written_tokens(cmd):
    """The words of CMD that are written: redirect targets, and the operands of the write commands (cp: its last operand;
    sed only with -i; git apply: its operands). Read-only words that name a governed path are not written."""
    out = [m.group(1).strip("\"'") for m in REDIR.finditer(cmd)]
    for seg in re.split(r"&&|\|\||[;|\n]", cmd):
        seg = re.sub(r"\d?>>?\s*[^\s;&|<>]+|<\s*[^\s;&|<>]+", " ", seg)
        w = seg.split()
        while w and (w[0] in ("sudo", "env", "command", "time", "nohup") or "=" in w[0].split("/")[0]):
            w = w[1:]
        if not w:
            continue
        c = os.path.basename(w[0])
        args = [a.strip("\"'") for a in w[1:]]
        if c == "git" and args[:1] == ["apply"]:
            out += [a for a in args[1:] if not a.startswith("-")]
        elif c == "sed":
            if any(a == "-i" or a.startswith("-i") or a == "--in-place" for a in args):
                out += [a for a in args if not a.startswith("-")][1:]
        elif c in WCMD:
            ops = [a for a in args if not a.startswith("-")]
            out += ops[-1:] if c == "cp" else ops
    return out


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        ev = {}
    cwd = ev.get("cwd") or os.getcwd()
    top = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or cwd
    cfg = os.path.join(top, ".backlog-guard.json")
    out = []
    try:
        m = load_guard()
        gd = m.Guard(cfg, root=top)
        name = ev.get("hook_event_name", "")
        if name == "SessionStart":
            # git hooks do not travel with a clone (core.hooksPath is local config); the session start re-arms them
            if os.path.isdir(os.path.join(top, ".githooks")):
                cur = subprocess.run(["git", "-C", top, "config", "core.hooksPath"], capture_output=True, text=True).stdout.strip()
                if cur != ".githooks":
                    subprocess.run(["git", "-C", top, "config", "core.hooksPath", ".githooks"])
                    print("BACKLOG GUARD: git hooks re-armed in this clone (core.hooksPath = .githooks).")
            try:
                m.cmd_status(gd, out=lambda s: print(s))
            except SystemExit as e:     # the session must be able to start and install what the guard needs
                print(f"BACKLOG GUARD: the lineage state is not shown: {e}")
            return 0
        tool, ti = ev.get("tool_name", ""), ev.get("tool_input", {}) or {}
        paths = []
        if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
            paths = [ti.get("file_path") or ti.get("notebook_path") or ""]
        elif tool == "Bash":
            cmd = ti.get("command", "")
            if WRITE.search(cmd):
                for tok in written_tokens(cmd):
                    rel = os.path.relpath(os.path.join(cwd, tok), top)
                    if not rel.startswith("..") and gd.is_work(rel):
                        paths.append(tok)
        rc = 0
        for p in [p for p in paths if p]:
            rc = max(rc, m.cmd_edit(gd, os.path.relpath(os.path.join(cwd, p), top), out=out.append))
            if rc:
                break
        if rc:
            print("\n".join(out), file=sys.stderr)
            return 2
        return 0
    except SystemExit as e:
        print(f"GUARD BLOCKS (cannot examine): {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"GUARD BLOCKS (guard error, failing closed): {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
