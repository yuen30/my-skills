#!/usr/bin/env python3
"""Check that every skill named in installed personas is available locally.
CLAUDE_HOME overrides ~/.claude."""
import glob, json, os, re, sys

home = os.environ.get("CLAUDE_HOME") or os.path.expanduser("~/.claude")


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        sys.exit(f"error: cannot read {path}: {e}")


personas = sorted(glob.glob(os.path.join(home, "agents", "*.md")))
if not personas:
    sys.exit(f"error: no personas found in {home}/agents")

avail = {os.path.basename(os.path.dirname(p))
         for p in glob.glob(os.path.join(home, "skills", "*", "SKILL.md"))}
local = set(avail)

enabled = load(os.path.join(home, "settings.json")).get("enabledPlugins", {})
installed = load(os.path.join(home, "plugins", "installed_plugins.json")).get("plugins", {})
for key, on in enabled.items():
    if on is not True:
        continue
    for entry in installed.get(key, []):
        for p in glob.glob(os.path.join(entry["installPath"], "skills", "*", "SKILL.md")):
            avail.add(f"{key.split('@')[0]}:{os.path.basename(os.path.dirname(p))}")

missing, n = [], 0
for path in personas:
    for line in open(path, encoding="utf-8"):
        if "skill" not in line.lower():
            continue
        for tok in re.findall(r"`([a-z0-9][a-z0-9:-]*[a-z0-9])`", line):
            if "-" in tok or ":" in tok or tok in local:
                n += 1
                if tok not in avail:
                    missing.append(f"{os.path.basename(path)}: `{tok}` not available")

if missing:
    print("\n".join(missing))
    sys.exit(1)
print(f"ok: {n} persona skill refs available")
