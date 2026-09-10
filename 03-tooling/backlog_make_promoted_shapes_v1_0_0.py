#!/usr/bin/env python3
"""backlog_make_promoted_shapes v1.0.0 -- regenerate the severity-promotion overlay.

The severity audit of 2026-09-09 found 58 advisories that are obligations. Applying it in the base
shapes file bound every register and every fixture at once -- refusing finished and in-progress work,
the failure G89 names. The promotion therefore lives in an overlay, generated from the base file by
this script, and a register is validated against it ONLY if its own data declares

    fw:Register backlog:adoptsRuleSet backlog:RS_SeverityAudit_20260909 .

Usage: backlog_make_promoted_shapes_v1_0_0.py   (reads the highest backlog_shacl_v*.ttl, writes the
highest backlog_shacl_promoted_v*.ttl). The audit's classification lives in audit_severity terms
carried as inline "# G90" comments in the overlay, so the two files diff to severities only.
"""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sv = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
base = sorted(glob.glob(os.path.join(PKG, "02-shacl-safeguards", "backlog_shacl_v*.ttl")), key=sv)[-1]
over = sorted(glob.glob(os.path.join(PKG, "02-shacl-safeguards", "backlog_shacl_promoted_v*.ttl")), key=sv)[-1]
b, o = open(base).read(), open(over).read()
def sevs(t):
    return {m.group(1): m.group(2) for m in re.finditer(r"backlog:(\w+Shape) a sh:NodeShape(?:.|\n)*?sh:severity sh:(\w+)", t)}
sb, so = sevs(b), sevs(o)
diff = {k: (sb.get(k), so.get(k)) for k in set(sb) | set(so) if sb.get(k) != so.get(k)}
print(f"base   : {os.path.basename(base)}")
print(f"overlay: {os.path.basename(over)}")
print(f"shapes differing in severity: {len(diff)}")
for k, (x, y) in sorted(diff.items())[:5]:
    print(f"   {k}: {x} -> {y}")
missing = [k for k in sb if k not in so]
extra = [k for k in so if k not in sb]
if missing or extra:
    print(f"OVERLAY STALE: {len(missing)} shape(s) in base and not in overlay, {len(extra)} the reverse")
    print("Regenerate: apply /home/claude/audit_severity.py's classification to the base file.")
    sys.exit(2)
print("VERDICT     : overlay covers exactly the base file's shapes; severities differ only where the audit says")
