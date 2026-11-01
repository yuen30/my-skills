#!/usr/bin/env bash
#
# install.sh - Restore Claude Code skills + persona agents from this repo backup
#              onto a fresh machine (or after an OS reset).
#
# Scope: Claude Code skills + personas, then (via my-agent/scripts/restore_personas.sh)
#   Codex (~/.codex, ~/.agents/agents) and opencode (~/.config/opencode) personas,
#   each only if that tool is installed. A differing live file is skipped, not overwritten (see --force).
#
# Skills layout: canonical copy in ~/.agents/skills/<name> (also read by Codex /
#   `npx skills`); ~/.claude/skills/<name> is a relative symlink to it.
#   Only names this repo owns (or owned, per manifest) are touched.
#
# Idempotent: safe to re-run any time; always converges to the same state.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SKILLS_DEST="$HOME/.claude/skills"
CANON_DEST="$HOME/.agents/skills"
AGENTS_DEST="$HOME/.claude/agents"
AGENTS_SRC="$SCRIPT_DIR/my-agent/agents"

mkdir -p "$SKILLS_DEST" "$CANON_DEST" "$AGENTS_DEST"

# --- 1. Restore skills (repo -> ~/.agents/skills/<name>/, symlinked from ~/.claude/skills/<name>) ---
skill_count=0
current_skills=" "
for skill_md in "$SCRIPT_DIR"/*/SKILL.md; do
  [ -e "$skill_md" ] || continue
  skill_dir="$(dirname "$skill_md")"
  name="$(basename "$skill_dir")"

  # Exclude non-skill top-level dirs even if they somehow contain a SKILL.md
  case "$name" in
    docs) continue ;;
  esac

  # Replace, not overlay, so files deleted from the repo disappear too
  rm -rf "${CANON_DEST:?}/$name"
  mkdir -p "$CANON_DEST/$name"
  cp -R "$skill_dir/." "$CANON_DEST/$name/"
  # A real dir (older install) must go first, else ln -sfn would link inside it
  [ -L "$SKILLS_DEST/$name" ] || rm -rf "${SKILLS_DEST:?}/$name"
  ln -sfn "../../.agents/skills/$name" "$SKILLS_DEST/$name"
  current_skills="$current_skills$name "
  skill_count=$((skill_count + 1))
done

# --- 1b. Prune skills this repo installed before but no longer ships ---
# Candidates come from the manifest of the previous run, so plugin, app-managed
# (synced/) or skills installed later by find-skills are never touched.
# First run without a manifest: fall back to names that ever had a top-level
# SKILL.md in this repo's git history.
MANIFEST="$SKILLS_DEST/.my-skills-installed"
pruned=0
if [ -f "$MANIFEST" ]; then
  candidates="$(cat "$MANIFEST")"
elif git -C "$SCRIPT_DIR" rev-parse --git-dir >/dev/null 2>&1; then
  candidates="$(git -C "$SCRIPT_DIR" log --all --format= --name-only -- '*/SKILL.md' \
               | awk -F/ 'NF==2 && $2=="SKILL.md" {print $1}' | sort -u)"
else
  candidates=""
fi
for old in $candidates; do
  case "$current_skills" in *" $old "*) continue ;; esac
  case "$old" in docs|""|.*) continue ;; esac
  if [ -e "$SKILLS_DEST/$old" ] || [ -L "$SKILLS_DEST/$old" ] || [ -d "$CANON_DEST/$old" ]; then
    rm -rf "${SKILLS_DEST:?}/$old" "${CANON_DEST:?}/$old"
    pruned=$((pruned + 1))
  fi
done
printf '%s\n' $current_skills > "$MANIFEST"

# Repo checks run before every commit (scripts/check.py)
if git -C "$SCRIPT_DIR" rev-parse --git-dir >/dev/null 2>&1; then
  git -C "$SCRIPT_DIR" config core.hooksPath .githooks
fi

# --- 2. Restore Claude persona agent configs (repo backup -> live ~/.claude/agents/) ---
agent_count=0
if [ -d "$AGENTS_SRC" ]; then
  for agent_md in "$AGENTS_SRC"/*.md; do
    [ -e "$agent_md" ] || continue
    # Respect personas the user parked in ~/.claude/agents-disabled/
    [ -e "$HOME/.claude/agents-disabled/$(basename "$agent_md")" ] && continue
    cp "$agent_md" "$AGENTS_DEST/"
    agent_count=$((agent_count + 1))
  done
fi

# --- 3. Parked personas (repo my-agent/agents-disabled -> ~/.claude/agents-disabled/) ---
# Kept installable but inactive; activate with: mv ~/.claude/agents-disabled/<name>.md ~/.claude/agents/
parked_count=0
if [ -d "$SCRIPT_DIR/my-agent/agents-disabled" ]; then
  mkdir -p "$HOME/.claude/agents-disabled"
  for agent_md in "$SCRIPT_DIR"/my-agent/agents-disabled/*.md; do
    [ -e "$agent_md" ] || continue
    name="$(basename "$agent_md")"
    # Skip if the user already activated it; never activate it ourselves
    [ -e "$AGENTS_DEST/$name" ] && continue
    cp "$agent_md" "$HOME/.claude/agents-disabled/"
    parked_count=$((parked_count + 1))
  done
fi

echo "Restore complete:"
echo "  - Skills copied to $CANON_DEST and symlinked from $SKILLS_DEST: $skill_count"
echo "  - Old skills pruned from both locations: $pruned"
echo "  - Agent files copied to $AGENTS_DEST: $agent_count"
echo "  - Parked personas copied to ~/.claude/agents-disabled: $parked_count"

bash "$SCRIPT_DIR/my-agent/scripts/restore_personas.sh"

# Warn-only: report persona skill refs that are not installed (never fails the install)
if command -v python3 >/dev/null 2>&1; then
  python3 "$SCRIPT_DIR/my-agent/scripts/check_installed.py" || echo "warning: some persona skills are not installed (see above)"
else
  echo "note: python3 not found, skipping persona skill check"
fi
