#!/usr/bin/env python3
import json, os, subprocess, sys, tempfile

script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "check_installed.py")


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)


def run(home):
    return subprocess.run([sys.executable, script], capture_output=True, text=True,
                          env={**os.environ, "CLAUDE_HOME": home})


with tempfile.TemporaryDirectory() as h:
    plug = os.path.join(h, "plugins", "cache", "p")
    w(os.path.join(h, "skills", "my-local", "SKILL.md"), "x")
    w(os.path.join(plug, "skills", "alpha", "SKILL.md"), "x")
    w(os.path.join(h, "settings.json"), json.dumps({"enabledPlugins": {"pl@mk": True}}))
    w(os.path.join(h, "plugins", "installed_plugins.json"),
      json.dumps({"plugins": {"pl@mk": [{"installPath": plug}]}}))
    w(os.path.join(h, "agents", "bob.md"), "Skills: `my-local`, `pl:alpha`\n")
    r = run(h)
    assert r.returncode == 0 and "ok: 2" in r.stdout, r
    w(os.path.join(h, "agents", "bob.md"), "Skills: `my-local`, `pl:alpha`, `pl:gone`\n")
    r = run(h)
    assert r.returncode == 1 and "bob.md: `pl:gone` not available" in r.stdout, r
    w(os.path.join(h, "settings.json"), json.dumps({"enabledPlugins": {"pl@mk": False}}))
    r = run(h)
    assert r.returncode == 1 and "`pl:alpha` not available" in r.stdout, r
    os.remove(os.path.join(h, "settings.json"))
    assert run(h).returncode == 1
print("ok")
