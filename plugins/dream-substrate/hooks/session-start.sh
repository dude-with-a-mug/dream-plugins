#!/bin/sh
# Offline hint only. The active MCP connection, not a file, verifies binding.
dream_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
for dream_file in "$dream_dir/.mcp.json" "$dream_dir/.codex/config.toml"; do
    [ -r "$dream_file" ] || continue
    if grep -q 'X-Dream-Idea' "$dream_file" 2>/dev/null; then
        printf '%s\n' 'Dream: a binding declaration was detected. Load the dream skill; verify the intended idea through the active MCP connection at setup or reconnect. This offline hint does not verify effective binding.'
        exit 0
    fi
done
for dream_file in "$dream_dir/CLAUDE.md" "$dream_dir/AGENTS.md" "$dream_dir/.claude/CLAUDE.md"; do
    [ -r "$dream_file" ] || continue
    if grep -q 'Dream idea' "$dream_file" 2>/dev/null; then
        printf '%s\n' 'Dream: an idea breadcrumb was detected. Load the dream skill to inspect the intended binding; the active MCP connection must verify it.'
        exit 0
    fi
done
exit 0
