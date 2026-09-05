#!/usr/bin/env bash
#
# install.sh - Restore Claude Code skills + persona agents from this repo backup
#              onto a fresh machine (or after an OS reset).
#
# Scope: Claude Code only.
#   - my-agent/codex/    -> NOT touched by this script. Codex CLI has its own
#                            config location/format; restore manually if needed.
#   - my-agent/opencode/ -> NOT touched by this script. OpenCode CLI has its own
#                            config location/format; restore manually if needed.
#
# Idempotent: safe to re-run any time; always converges to the same state.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SKILLS_DEST="$HOME/.claude/skills"
AGENTS_DEST="$HOME/.claude/agents"
AGENTS_SRC="$SCRIPT_DIR/my-agent/agents"

mkdir -p "$SKILLS_DEST" "$AGENTS_DEST"

# --- 1. Restore skill folders (repo -> ~/.claude/skills/<name>/) ---
skill_count=0
for skill_md in "$SCRIPT_DIR"/*/SKILL.md; do
  [ -e "$skill_md" ] || continue
  skill_dir="$(dirname "$skill_md")"
  name="$(basename "$skill_dir")"

  # Exclude non-skill top-level dirs even if they somehow contain a SKILL.md
  case "$name" in
    my-agent|docs) continue ;;
  esac

  mkdir -p "$SKILLS_DEST/$name"
  cp -R "$skill_dir/." "$SKILLS_DEST/$name/"
  skill_count=$((skill_count + 1))
done

# --- 2. Restore Claude persona agent configs (repo backup -> live ~/.claude/agents/) ---
agent_count=0
if [ -d "$AGENTS_SRC" ]; then
  for agent_md in "$AGENTS_SRC"/*.md; do
    [ -e "$agent_md" ] || continue
    cp "$agent_md" "$AGENTS_DEST/"
    agent_count=$((agent_count + 1))
  done
fi

echo "Restore complete:"
echo "  - Skill folders copied to $SKILLS_DEST: $skill_count"
echo "  - Agent files copied to $AGENTS_DEST: $agent_count"
