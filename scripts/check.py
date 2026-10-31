#!/usr/bin/env python3
"""Repo checks for my-skills. Usage: python3 scripts/check.py [--write-index]

Fails (exit 1) on: name != folder, bad/long description, broken references/ links,
index.json out of sync, personas naming unknown skills, untracked files in skill folders.
--write-index regenerates index.json from the folders first.
"""
import glob, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
NOT_SKILLS = {"docs"}
MAX_DESC = 500  # umbrella skills (abe-*) list many stacks; keep the rest short
errors = []


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    try:
        import yaml
        return yaml.safe_load(m.group(1))
    except ImportError:  # shortcut: naive parser if PyYAML is missing, install PyYAML for exact checks
        return dict(re.findall(r"^(\w[\w-]*):\s*\"?(.*?)\"?\s*$", m.group(1), re.M))


skills = sorted(p.split("/")[0] for p in glob.glob("*/SKILL.md") if p.split("/")[0] not in NOT_SKILLS)

for name in skills:
    text = open(f"{name}/SKILL.md", encoding="utf-8").read()
    fm = frontmatter(text)
    if not fm:
        errors.append(f"{name}: missing frontmatter")
        continue
    if fm.get("name") != name:
        errors.append(f"{name}: name '{fm.get('name')}' != folder")
    desc = str(fm.get("description", ""))
    if not desc or "\n" in desc.strip():
        errors.append(f"{name}: description missing or multi-line")
    elif len(desc) > MAX_DESC:
        errors.append(f"{name}: description {len(desc)} chars > {MAX_DESC}")
    body = re.sub(r"```.*?```", "", text, flags=re.S)
    for link in re.findall(r"\]\(((?:references|templates|scripts)/[^)#\s]+)\)", body):
        if not os.path.exists(os.path.join(name, link)):
            errors.append(f"{name}: broken link {link}")


def skill_files(name):
    if name == "my-agent":
        return [f"{name}/SKILL.md"]
    files = [f"{name}/SKILL.md"] + sorted(glob.glob(f"{name}/references/*"))
    return files


def render_index():
    data = {"skills": [{"name": n, "files": skill_files(n)} for n in skills]}
    out = json.dumps(data, indent=2, ensure_ascii=False)
    out = re.sub(r'"files": \[\s*([^\]]*?)\s*\]',
                 lambda m: '"files": [' + re.sub(r",\s*\n\s*", ", ", m.group(1)) + "]", out)
    return out + "\n"


if "--write-index" in sys.argv:
    open("index.json", "w", encoding="utf-8").write(render_index())
try:
    current = json.load(open("index.json", encoding="utf-8"))
    names = {s["name"] for s in current["skills"]}
    if names != set(skills):
        errors.append(f"index.json out of sync: missing {sorted(set(skills) - names)}, extra {sorted(names - set(skills))} (run with --write-index)")
    for s in current["skills"]:
        for f in s["files"]:
            if not os.path.exists(f):
                errors.append(f"index.json: {f} does not exist (run with --write-index)")
except (OSError, ValueError, KeyError) as e:
    errors.append(f"index.json unreadable: {e}")

known = set(skills) | {l.strip() for l in open("scripts/external-skills.txt") if l.strip() and not l.startswith("#")}
for path in sorted(glob.glob("my-agent/agents/*.md")):
    for line in open(path, encoding="utf-8"):
        if "skill" not in line.lower():
            continue
        for tok in re.findall(r"`([a-z0-9][a-z0-9:-]*[a-z0-9])`", line):
            if "-" in tok or ":" in tok or tok in skills:
                if tok not in known:
                    errors.append(f"{path}: unknown skill `{tok}`")

try:
    untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "--", *skills],
                               capture_output=True, text=True, check=True).stdout.split()
    if untracked:
        errors.append(f"untracked files in skill folders (git add them): {untracked}")
except (OSError, subprocess.CalledProcessError):
    pass

if errors:
    print("check failed:\n  " + "\n  ".join(errors))
    sys.exit(1)
print(f"ok: {len(skills)} skills, index.json in sync, personas reference known skills")
