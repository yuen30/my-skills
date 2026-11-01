#!/usr/bin/env python3
"""Run each case on Haiku with and without its SKILL.md; grade by regex.

Isolation (claude -p): cwd = empty tempdir (no project CLAUDE.md), --tools "" (no tools),
--strict-mcp-config (no MCP), --setting-sources "" (no user/project/local settings, hooks),
--disable-slash-commands (no skills), --no-session-persistence, --system-prompt replaces the
default prompt. NOT isolated: OAuth auth/account, model-side defaults. Verified no CLAUDE.md leak.
Skill injection = SKILL.md body (frontmatter stripped) in the system prompt; references/ are
NOT provided (no tools), so abe-framework/project-structure are tested on SKILL.md rules only.
"""
import argparse, json, re, subprocess, tempfile, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
BASE = "Answer tersely and exactly as asked."

def skill_body(name):
    t = (ROOT / name / "SKILL.md").read_text()
    return re.sub(r"\A---\n.*?\n---\n", "", t, flags=re.S).strip()

def call(case, with_skill, run, cwd, effort=None):
    sp = BASE + ("\n\n# Skill\n" + skill_body(case["skill"]) if with_skill else "")
    cmd = ["claude", "-p", "--model", "haiku", "--tools", "", "--strict-mcp-config",
           "--setting-sources", "", "--disable-slash-commands", "--no-session-persistence",
           "--system-prompt", sp] + (["--effort", effort] if effort else []) + [case["prompt"]]
    try:
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120).stdout.strip()
    except subprocess.TimeoutExpired:
        out = "<TIMEOUT>"
    ok = (out != "<TIMEOUT>"
          and all(re.search(p, out, re.I | re.S | re.M) for p in case["must"])
          and not any(re.search(p, out, re.I | re.S | re.M) for p in case["must_not"]))
    return dict(id=case["id"], skill=case["skill"], with_skill=with_skill, run=run, output=out, pass_=ok)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--case")
    ap.add_argument("--file", default="cases.json")
    ap.add_argument("--effort")
    ap.add_argument("--without-only", action="store_true")
    a = ap.parse_args()
    cases = [c for c in json.loads((HERE / a.file).read_text()) if not a.case or c["id"] == a.case]
    with tempfile.TemporaryDirectory() as cwd, ThreadPoolExecutor(4) as ex:
        futs = [ex.submit(call, c, w, r, cwd, a.effort) for c in cases for r in range(a.runs) for w in ((False,) if a.without_only else (True, False))]
        res = [f.result() for f in futs]
    print(f"{'case':26} {'with':>6} {'without':>8}")
    tot = {True: [0, 0], False: [0, 0]}
    for c in cases:
        row = []
        for w in (True, False):
            rs = [x for x in res if x["id"] == c["id"] and x["with_skill"] == w]
            p = sum(x["pass_"] for x in rs); tot[w][0] += p; tot[w][1] += len(rs)
            row.append(f"{p}/{len(rs)}")
        print(f"{c['id']:26} {row[0]:>6} {row[1]:>8}")
    print(f"{'TOTAL':26} {tot[True][0]}/{tot[True][1]:>3} {tot[False][0]}/{tot[False][1]:>5}")
    out = HERE / "results" / (time.strftime("%Y%m%d-%H%M%S") + ".json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print("saved", out)

if __name__ == "__main__":
    main()
