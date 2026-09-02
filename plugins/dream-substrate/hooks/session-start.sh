#!/bin/sh
# Dream SessionStart hook — print one ambient line of binding fact, or nothing.
#
# This plugin installs globally, so this script runs at the start of EVERY
# session in EVERY repo, most of which have nothing to do with Dream. It is
# therefore defensive by construction:
#
#   * read-only: it opens two or three files and never writes;
#   * offline: no network calls, ever;
#   * secret-free: it reads only the non-secret `X-Dream-Idea` binding and the
#     door URL, and validates both against a character set that cannot contain
#     a token or a `${VAR}` reference before echoing them;
#   * harness-neutral: the binding may sit in Claude Code's `.mcp.json` or in
#     Codex's `.codex/config.toml`; the same gates apply to both;
#   * silent by default: no binding found means no output at all;
#   * always `exit 0`, so a session never fails because of this hook.
#
# On exit 0, Claude Code adds a SessionStart hook's plain-text stdout to the
# model's context (Claude Code hooks reference, "Exit code 0"); Codex runs the
# same hooks file with the same event schema. That is the only reason this
# prints anything: it makes orientation ambient rather than a judgment call,
# per the activation decision in the external-agent-connection spec. There is
# deliberately no `set -e`: partial failure must degrade to silence, never to
# a broken session.

# Claude Code names the project directory; Codex runs the hook in it.
dream_dir="${CLAUDE_PROJECT_DIR:-$PWD}"

# A Dream idea id is non-secret, but only echo one that looks like an id.
# The character set excludes whitespace, quotes, `$`, `{` and `}`, so an
# unexpanded `${DREAM_PAT}` or a real token can never survive this gate.
_dream_safe_id() {
    case "$1" in
        '' | *[!A-Za-z0-9._-]*) return 1 ;;
    esac
    [ "${#1}" -le 80 ]
}

# A door is a URL (or bare host) ending at the `/v1/mcp` mount. Same character
# discipline as above, plus a shape check. One trailing slash is tolerated —
# the server answers `/v1/mcp/` too, and a founder who typed it that way in
# `.mcp.json` must not lose the ambient line over it. The normalized,
# slash-less form is what gets echoed, via `dream_door_normalized`.
_dream_safe_door() {
    dream_door_normalized="${1%/}"
    case "$dream_door_normalized" in
        */v1/mcp) ;;
        *) return 1 ;;
    esac
    case "$dream_door_normalized" in
        *[!A-Za-z0-9./:_-]*) return 1 ;;
    esac
    [ "${#dream_door_normalized}" -ge 8 ] && [ "${#dream_door_normalized}" -le 200 ]
}

# Flatten JSON into one token per line so a single key can be read with sed.
# This is not a JSON parser and does not pretend to be one: it strips
# whitespace and breaks on structural punctuation, which is enough to find a
# top-of-object `"key":"value"` pair and nothing more.
_dream_flatten() {
    tr -d ' \t\r\n' < "$1" 2>/dev/null | tr ',{}' '\n\n\n' 2>/dev/null
}

dream_idea=''
dream_door=''

# Source 1: the repo's committed `.mcp.json` — the durable "this repo is a
# checkout of this idea" binding.
dream_mcp="$dream_dir/.mcp.json"
if [ -f "$dream_mcp" ] && [ -r "$dream_mcp" ]; then
    dream_flat=$(_dream_flatten "$dream_mcp")
    dream_idea=$(
        printf '%s\n' "$dream_flat" |
            sed -n 's/^"X-Dream-Idea":"\([^"]*\)".*/\1/p' |
            head -n 1
    )
    dream_door=$(
        printf '%s\n' "$dream_flat" |
            sed -n 's|^"url":"\([^"]*/v1/mcp/\{0,1\}\)".*|\1|p' |
            head -n 1
    )
fi

# Source 1b: Codex's project config — the same binding, spelled in TOML. Only
# consulted when `.mcp.json` did not answer. The header may sit inline
# (`http_headers = { "X-Dream-Idea" = "…" }`) or under its own table header;
# either way it is one `"X-Dream-Idea" = "…"` pair, and the door is the
# `url = "…/v1/mcp"` line of the same file. The key's quotes are optional in
# TOML, so both spellings are read.
dream_toml="$dream_dir/.codex/config.toml"
if [ -z "$dream_idea" ] && [ -f "$dream_toml" ] && [ -r "$dream_toml" ]; then
    dream_idea=$(
        sed -n 's/.*"\{0,1\}X-Dream-Idea"\{0,1\}[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' "$dream_toml" 2>/dev/null |
            head -n 1
    )
    if [ -n "$dream_idea" ]; then
        dream_door=$(
            sed -n 's|^[[:space:]]*url[[:space:]]*=[[:space:]]*"\([^"]*/v1/mcp/\{0,1\}\)".*|\1|p' "$dream_toml" 2>/dev/null |
                head -n 1
        )
    fi
fi

# Source 2: the activation breadcrumb the binding step appends to the repo's
# agent instructions. Only consulted when neither config file answered. The
# breadcrumb is prose and wraps: `Door:` and the backticked URL routinely land
# on different lines, so the door is any backticked `/v1/mcp` token in the
# document rather than one on the `Door:` line.
if [ -z "$dream_idea" ]; then
    for dream_doc in "$dream_dir/CLAUDE.md" "$dream_dir/AGENTS.md" "$dream_dir/.claude/CLAUDE.md"; do
        [ -f "$dream_doc" ] && [ -r "$dream_doc" ] || continue
        grep -q 'Dream idea' "$dream_doc" 2>/dev/null || continue
        dream_idea=$(
            sed -n 's/.*Dream idea[^(]*(`\([A-Za-z0-9._-]\{1,80\}\)`).*/\1/p' "$dream_doc" 2>/dev/null |
                head -n 1
        )
        if [ -n "$dream_idea" ]; then
            dream_door=$(
                sed -n 's|.*`\([^`]*/v1/mcp/\{0,1\}\)`.*|\1|p' "$dream_doc" 2>/dev/null |
                    head -n 1
            )
            break
        fi
    done
fi

_dream_safe_id "$dream_idea" || exit 0
if _dream_safe_door "$dream_door"; then
    dream_door="$dream_door_normalized"
else
    dream_door=''
fi

if [ -n "$dream_door" ]; then
    dream_line="Dream: this repo is bound to idea $dream_idea · door $dream_door · load the dream-substrate skill to orient from the task board and contribute back."
else
    dream_line="Dream: this repo is bound to idea $dream_idea · load the dream-substrate skill to orient from the task board and contribute back."
fi

# Last-resort guard: never emit a line carrying anything token-shaped, even if
# a future edit widens one of the gates above.
case "$dream_line" in
    *Bearer* | *dream_pat_* | *'${'*) exit 0 ;;
esac

printf '%s\n' "$dream_line"
exit 0
