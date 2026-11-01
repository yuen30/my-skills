#!/usr/bin/env bash
#
# restore_personas.sh - Restore Codex and opencode persona configs from this repo.
#   Usage: restore_personas.sh [--force] [codex] [opencode]   (target args force targets, creating dirs)
#
# Targets are restored when the tool is on PATH or its config dir exists.
# Non-destructive by default: missing live files are created, identical ones left
# alone, and a live file that differs from the repo is SKIPPED (never overwritten).
# --force overwrites differing live files, saving the old one to <file>.bak first.
# Live files not in the repo are never deleted. Idempotent.

set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OVERWRITE=0
created=0 unchanged=0 skipped=0 overwritten=0

# sync_file <repo file> <live file>
sync_file() {
  local src="$1" dst="$2"
  if [ ! -f "$dst" ]; then
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
    created=$((created + 1))
  elif cmp -s "$src" "$dst"; then
    unchanged=$((unchanged + 1))
  elif [ "$OVERWRITE" = 1 ]; then
    cp "$dst" "$dst.bak"
    echo "  backed up $dst -> $dst.bak"
    cp "$src" "$dst"
    overwritten=$((overwritten + 1))
  else
    echo "  skip $dst: differs from repo (run with --force to overwrite; a .bak is kept)"
    skipped=$((skipped + 1))
  fi
}

summary() { # summary <name>
  echo "$1: $created created, $unchanged unchanged, $skipped skipped-differs, $overwritten overwritten"
  created=0 unchanged=0 skipped=0 overwritten=0
}

TARGETS=""
for a in "$@"; do
  case "$a" in
    --force) OVERWRITE=1 ;;
    codex|opencode) TARGETS="$TARGETS $a" ;;
    *) echo "usage: $0 [--force] [codex] [opencode]" >&2; exit 2 ;;
  esac
done

want() { # want <name> <dir>
  case "$TARGETS " in *" $1 "*) return 0 ;; esac
  command -v "$1" >/dev/null 2>&1 || [ -d "$2" ]
}

if want codex "$HOME/.codex"; then
  sync_file "$SRC/codex/AGENTS.md" "$HOME/.codex/AGENTS.md"
  sync_file "$SRC/codex/AGENTS.md" "$HOME/.agents/agents/AGENTS.md"
  summary codex
else
  echo "skip codex (not installed)"
fi

if want opencode "$HOME/.config/opencode"; then
  sync_file "$SRC/opencode/AGENTS.md" "$HOME/.config/opencode/AGENTS.md"
  for f in "$SRC"/opencode/agents/*.md; do
    [ -e "$f" ] || continue
    sync_file "$f" "$HOME/.config/opencode/agents/$(basename "$f")"
  done
  summary opencode
else
  echo "skip opencode (not installed)"
fi
