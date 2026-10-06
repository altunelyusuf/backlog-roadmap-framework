#!/usr/bin/env python3
"""backlog_guard_install v1.0.0 -- put the work guard in the path of the act, in one command (ruling G101).

  backlog_guard_install_v1_0_0.py REPO --tooling-dir DIR --register FILE --lineage NAME --work-path GLOB [...]
                                       [--exempt-path GLOB ...]

  REPO         the consumer repository (a git work tree)
  --tooling-dir  where the framework's tools are vendored INSIDE the repo (relative), e.g.
               packages/backlog-roadmap-framework-v1_331_0/03-tooling
  Writes (idempotent; existing content is merged, never replaced):
    .backlog-guard.json                      the configuration, with governed_from = the current commit
    .githooks/commit-msg, .githooks/pre-push git hooks (+ git config core.hooksPath .githooks)
    .claude/settings.json                    SessionStart and PreToolUse hooks added beside whatever is there
    .github/workflows/backlog-work-guard.yml the CI range check: the layer `--no-verify` cannot skip
  Four layers, because each one alone has been argued past: the session sees the rule at start (SessionStart), edits
  to governed paths stop before they happen (PreToolUse), a commit without a ready Work-Item stops (commit-msg, pre-push),
  and a pull request or push that contains one fails (CI). Mark the CI job as a required status check in the host.
"""
import json, os, stat, subprocess, sys

COMMIT_MSG = """#!/bin/sh
# installed by backlog_guard_install: a commit that changes governed work must name a ready Work-Item.
exec python3 "$(git rev-parse --show-toplevel)/{tools}/backlog_work_guard_v1_0_0.py" commit-msg "$1"
"""
PRE_PUSH = """#!/bin/sh
# installed by backlog_guard_install: no push of a range containing work outside the register.
TOP="$(git rev-parse --show-toplevel)"
ZERO=0000000000000000000000000000000000000000
while read lref lsha rref rsha; do
  [ "$lsha" = "$ZERO" ] && continue
  if [ "$rsha" = "$ZERO" ]; then base="$(git merge-base "$lsha" origin/main 2>/dev/null || git merge-base "$lsha" origin/master 2>/dev/null || echo)"; else base="$rsha"; fi
  if [ -z "$base" ]; then rng="$lsha"; else rng="$base..$lsha"; fi
  python3 "$TOP/{tools}/backlog_work_guard_v1_0_0.py" range "$rng" || exit 1
done
exit 0
"""
WORKFLOW = """name: Backlog work guard
# Every commit that changes governed work must name a ready Work-Item. Mark this job as a required status check.
on:
  pull_request:
  push:
jobs:
  guard:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout with full history
        run: |
          git clone --no-checkout "https://x-access-token:${{{{ github.token }}}}@github.com/${{{{ github.repository }}}}.git" repo
          cd repo && git fetch origin "${{{{ github.sha }}}}" && git checkout --detach "${{{{ github.sha }}}}" && git fetch --unshallow origin 2>/dev/null || true
      - name: Install rdflib
        run: pip install rdflib
      - name: Work guard over the commits this event brings
        working-directory: repo
        run: |
          if [ "${{{{ github.event_name }}}}" = "pull_request" ]; then RANGE="${{{{ github.event.pull_request.base.sha }}}}..${{{{ github.sha }}}}"
          else RANGE="${{{{ github.event.before }}}}..${{{{ github.sha }}}}"; fi
          case "$RANGE" in 000000*) RANGE="${{{{ github.sha }}}}";; esac
          python3 {tools}/backlog_work_guard_v1_0_0.py range "$RANGE"
"""


def merge_hooks(path, tools):
    cur = json.load(open(path)) if os.path.exists(path) else {}
    hooks = cur.setdefault("hooks", {})
    cmd = f'python3 "$CLAUDE_PROJECT_DIR/{tools}/backlog_guard_claude_hook_v1_0_0.py"'
    want = {"SessionStart": {"matcher": "", "hooks": [{"type": "command", "command": cmd}]},
            "PreToolUse": {"matcher": "Edit|Write|MultiEdit|NotebookEdit|Bash", "hooks": [{"type": "command", "command": cmd}]}}
    for ev, entry in want.items():
        lst = hooks.setdefault(ev, [])
        if not any("backlog_guard_claude_hook" in h.get("command", "") for e in lst for h in e.get("hooks", [])):
            lst.append(entry)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(cur, open(path, "w"), indent=2)


def main(a):
    def opt(n, multi=False):
        v = [a[i + 1] for i, x in enumerate(a) if x == n]
        return v if multi else (v[0] if v else None)
    if not a or a[0].startswith("--"):
        print(__doc__); return 1
    repo = os.path.abspath(a[0])
    tools = (opt("--tooling-dir") or "").strip("/")
    reg, lin, work, ex = opt("--register", True), opt("--lineage"), opt("--work-path", True), opt("--exempt-path", True)
    if not (tools and reg and lin and work):
        print(__doc__); return 1
    if not os.path.isfile(os.path.join(repo, tools, "backlog_work_guard_v1_0_0.py")):
        print(f"the tools are not vendored at {tools}: backlog_work_guard_v1_0_0.py is not there"); return 1
    for r in reg:
        if not os.path.isfile(os.path.join(repo, r)):
            print(f"register not found: {r}"); return 1
    head = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    cfgp = os.path.join(repo, ".backlog-guard.json")
    cfg = json.load(open(cfgp)) if os.path.exists(cfgp) else {}
    cfg.update({"register": reg, "active_lineage": lin, "work_paths": work, "exempt_paths": ex or cfg.get("exempt_paths", [])})
    cfg.setdefault("governed_from", head)
    json.dump(cfg, open(cfgp, "w"), indent=2)
    for name, body in (("commit-msg", COMMIT_MSG), ("pre-push", PRE_PUSH)):
        p = os.path.join(repo, ".githooks", name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(body.format(tools=tools))
        os.chmod(p, os.stat(p).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    subprocess.run(["git", "-C", repo, "config", "core.hooksPath", ".githooks"], check=True)
    merge_hooks(os.path.join(repo, ".claude", "settings.json"), tools)
    wf = os.path.join(repo, ".github", "workflows", "backlog-work-guard.yml")
    os.makedirs(os.path.dirname(wf), exist_ok=True)
    open(wf, "w").write(WORKFLOW.format(tools=tools))
    print(f"installed: .backlog-guard.json (governed_from {cfg['governed_from'][:9]}), .githooks/, .claude/settings.json hooks, CI workflow")
    print("still owed by a person: mark the CI job 'Backlog work guard' as a required status check, and commit these files.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
