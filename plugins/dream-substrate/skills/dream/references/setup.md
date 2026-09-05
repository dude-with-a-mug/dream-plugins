# Setup and connection recovery

Load for connection, binding, authentication, or scope-default work. Ordinary
reads and contributions need no repeated setup ritual.

Installing the connection is once per machine/account: the plugin names the
hosted MCP server, and the client handles OAuth sign-in. Binding is per repo:
commit only the non-secret `X-Dream-Idea` and optional `X-Dream-Branch` defaults.
Claude Code uses the `dream` server's `headers` in `.mcp.json`; Codex uses
`http_headers` in `.codex/config.toml` (trusted projects only). Preserve unrelated
configuration and existing server settings.

Before the first contribution, resolve the intended idea, working branch, and
connection identity. Reuse verified information already present:

1. If the repo has a binding or the user's paste-block identifies the idea,
   use it. At setup or reconnect call `dream_context` **without `idea`** and
   compare the resolved idea with that declaration; its `Dream-Actor` line
   confirms who you are acting as and through which connection. A hook hint
   does not verify effective binding. Diagnose client configuration and
   global/plugin overrides when they disagree; do not mask a broken default
   with explicit arguments.
2. Otherwise call `dream_ideas` for visible ideas and roles. Ask which idea the
   repo belongs to only when the user's intent does not already identify it.
3. For authorized setup, write the binding, reconnect as needed, verify, and
   briefly confirm the resolved idea and work destination. Directed work runs
   on a task branch: reuse a suitable one, or capture the task and start its
   branch with `start_task_branch`, which returns the branch and grounding.
   Main may be used for reading; obtain a permitted working branch before
   contributing where branch protection requires it.

When binding a repo, add or update a short breadcrumb in its existing
`AGENTS.md` or `CLAUDE.md`, preserving unrelated instructions:

```markdown
## Dream

This repo belongs to Dream idea **<title>** (`<idea-id>`), reached through the
`dream` MCP server at `<host>/v1/mcp`. Ground meaningful work, preserve
consequential discoveries, and reconcile at natural stopping points. Load
the `dream` skill when relevant. At setup/reconnect,
verify the effective idea through the active connection.
```

This is durable non-secret context, not an automated write trigger. Include
configuration changes in the authorized repository work; a breadcrumb alone
is not grounds for an extra commit ceremony.

## Credentials and addressing

The harness owns OAuth tokens. Never print, log, write, or pass them as CLI
arguments, and never ask the user to paste credentials into the conversation.
A headless caller uses a PAT from Settings → Tokens via `DREAM_PAT`, referenced
by the client without reading its value back.

- On 401, direct the user to the installed client's Dream MCP sign-in flow or
  Settings → Connections. Use the client's current supported login UI/command;
  credentials remain in the harness.
- On 403 `insufficient_scope`, report the missing authority. Wider consent is
  the user's decision; rewording or retrying a call cannot grant it.
- Local disconnect forgets this machine's credentials. Revoking in Settings →
  Connections ends the connection everywhere.
- To repoint a repo, change only the non-secret binding headers and reconnect.
  For a one-off read, explicit `idea` / `branch` arguments override defaults;
  changing configuration is unnecessary. MR-scoped tools derive their source
  branch from `merge_request_id`; an unrelated repo default must not redirect
  the review.
