# dream-substrate

The plugin is the box the connection ships in. One directory carrying the
**skill** (doctrine), the **MCP server reference** (capability), and a
**SessionStart hook** (ambient orientation) — installed once, instead of a
two-step "add the server, then copy the skill" ritual.

A repo holds the code. Dream holds the idea behind it — what it is, what's
decided, what's still open, and why. This plugin is the door between them.

## Install

The package is published to the public marketplace repo
`dude-with-a-mug/dream-plugins`, for both harnesses. Inside Claude Code:

```
/plugin marketplace add dude-with-a-mug/dream-plugins
/plugin install dream-substrate@dream
```

Or from a terminal:

```bash
claude plugin marketplace add dude-with-a-mug/dream-plugins
claude plugin install dream-substrate@dream
```

In Codex, the same package from the same repo:

```bash
codex plugin marketplace add dude-with-a-mug/dream-plugins
codex plugin add dream-substrate@dream
```

(or `/plugin marketplace add dude-with-a-mug/dream-plugins` inside Codex, then pick
**Dream** from `/plugins`.)

`dream` is the marketplace name — `.claude-plugin/marketplace.json` at the
marketplace root for Claude Code, `.agents/plugins/marketplace.json` beside it
for Codex, both listing the same entry; `dream-substrate` is the plugin. The
marketplace repo is a published artifact, not a source: a release workflow in
Dream's private source repo copies `plugins/dream-substrate/` and the two
marketplace manifests into it on every `plugin-v*` tag, so marketplace-installed
plugins pick up updates when a release lands. Inside a checkout of the source
repo, `/plugin marketplace add ./` works against the working tree in either
harness.

## The connection

The plugin ships **no credential**. The manifests name the door and nothing
else; the agent signs in the way it signs in to any OAuth-protected MCP
server. On its first call the door answers 401 with a
`WWW-Authenticate: Bearer resource_metadata=…` challenge, and the harness
follows it to Dream's own authorization server at the same origin. In Claude
Code that is:

```
claude mcp login dream
```

and in Codex:

```
codex mcp login dream
```

Both identify themselves by client-id metadata document, so the consent page
shows them as **Verified**. A browser opens on dreamluci.com. If you are signed out, sign in first
(password or Google — either returns you to the request). The consent page
names the agent asking, whether Dream recognises it, where the authorization
will be delivered ("this computer" for a CLI), and the scopes it wants —
`read` always, `contribute` pre-ticked when requested, `merge` never
pre-ticked. Give the connection a label (it is the attribution on every
proposal the agent makes), click **Allow**, and the terminal reports the
server connected.

What you have afterwards is a **connection**: a named, scoped, revocable
grant that lives in **Settings → Connections**. Rename it there; revoke it
there. Signing out in the terminal only disconnects that machine — revoking
in Settings is what ends the connection, on every machine, immediately.
Tokens rotate on their own; a connection that goes unused for a month
retires itself.

The idea and branch bindings (`X-Dream-Idea`, `X-Dream-Branch`) are
non-secret and are meant to be committed to the repo they bind — in
`.mcp.json` for Claude Code, in `.codex/config.toml` (`http_headers` on the
`dream` server, read in trusted projects only) for Codex. Nothing in this
package is secret, and nothing here should ever print a token.

### Headless (PAT)

A process with no browser — CI, cron — uses a personal access token from
**Settings → Tokens** instead, presented from an environment variable: as
`Authorization: Bearer ${DREAM_PAT}` in Claude Code, or by name
(`--bearer-token-env-var DREAM_PAT`) in Codex, which reads the variable
itself. That is the *only* place a PAT belongs: never in a plugin manifest,
never committed. The SessionStart hook refuses to echo anything that looks
like a token or an unexpanded placeholder.

## What gets loaded

| Component | File | What it does |
|---|---|---|
| Skill | `skills/dream-substrate/SKILL.md` | Latent in every session; loads at Dream-relevant moments (binding a repo, starting a task, hitting a decision the idea may own, discovering the spec was wrong). Carries the participation doctrine. |
| MCP server | `.mcp.json` (Claude Code) / `mcp.json` (Agent Plugins, which is what Codex reads) | Registers `dream` as a remote HTTP MCP server at `https://dream-30pu.onrender.com/v1/mcp`. No credential: the door's 401 challenge starts the OAuth sign-in (`claude mcp login dream` / `codex mcp login dream`). |
| Hook | `hooks/hooks.json` → `hooks/session-start.sh` | On SessionStart, prints one line naming the bound idea and door — and prints nothing at all in a repo that is not bound to a Dream idea. Same hooks file and event schema in both harnesses. |

All three are discovered from their default locations, so the Claude Code
manifest declares metadata only — no `skills` / `hooks` / `mcpServers` path
fields. Adding them would be redundant, and the `commands`/`agents` variants of
those fields *replace* the defaults rather than adding to them. The Codex
overlay (below) is the one manifest that names the hooks file, because it is
where Codex looks for hooks on an Agent Plugins package.

**Where doctrine actually lives.** The MCP server's own `instructions`, sent at
every connection, are the authoritative participation doctrine. The skill is a
delivery vehicle and can be months stale; where the two disagree, the server
wins. That is deliberate — an agent running an outdated plugin still
participates under current doctrine.

### The hook, precisely

It runs at the start of **every** session in **every** repo, because the plugin
installs globally. So it is deliberately boring:

1. Resolve the working directory from `CLAUDE_PROJECT_DIR` (falling back to
   `PWD`).
2. If `.mcp.json` there carries an `X-Dream-Idea` header, take that id and the
   `…/v1/mcp` door URL from it.
3. Otherwise, if `.codex/config.toml` there carries the same header (inline
   `http_headers = { … }` or its own `[mcp_servers.dream.http_headers]`
   table), take the id and the `url = "…/v1/mcp"` from that.
4. Otherwise, if `CLAUDE.md`, `AGENTS.md`, or `.claude/CLAUDE.md` carries the
   Dream binding breadcrumb, take the id (and door) from that.
5. Validate both against a character set that cannot contain a token, an
   unexpanded `${VAR}`, or whitespace; refuse to print a line containing
   `Bearer`, `dream_pat_`, or `${`.
6. Print one line, or nothing.

No network calls, no writes, no secrets, and it always exits `0` — a session
never fails because of this hook. Silence is the normal case: an unbound repo
produces no output. Claude Code adds a SessionStart hook's stdout to the model's
context on exit 0, which is the only reason it prints at all. Codex runs plugin
hooks from the same `hooks/hooks.json` with the same event schema and provides
`CLAUDE_PLUGIN_ROOT` for compatibility; it does not set `CLAUDE_PROJECT_DIR`,
so there the hook reads the directory it is run in.

## Three manifests, two marketplaces

The package carries three manifests on purpose, so the same directory installs
in Claude Code, in Codex, and in other Agent-Plugins-compatible harnesses:

- `.claude-plugin/plugin.json` — the Claude Code manifest.
- `plugin.json` — the vendor-neutral [Agent Plugins
  1.0](https://agent-plugins.org/specification) manifest. **This is the one
  Codex reads**: a root `plugin.json` carrying the Agent Plugins `$schema`
  makes Codex treat the directory as an Agent Plugins package — skills from
  `skills/`, servers from `mcp.json`.
- `.codex-plugin/plugin.json` — Codex's overlay on the Agent Plugins manifest.
  Codex takes only `hooks`, `apps`, and `interface` (display name, category)
  from it; `skills` and `mcpServers` come from the Agent Plugins layout and
  are deliberately absent here.

The Claude Code manifest and the Agent Plugins manifest each have their own
MCP config file, because the two standards disagree on the filename: Claude
Code auto-discovers `.mcp.json`, Agent Plugins 1.0 specifies `mcp.json` at
the plugin root. They point at the same door and must stay in sync
(`backend/tests/plugin/test_plugin_manifests.py` asserts they do, and asserts
the overlay's name and version match).

The repo root carries two marketplace manifests for the same reason:
`.claude-plugin/marketplace.json` for Claude Code and
`.agents/plugins/marketplace.json` for Codex. Codex would fall back to the
Claude Code file if its own were missing, but its documented location is the
`.agents` one, and it is where the Codex-only `policy` block lives
(`installation: AVAILABLE`, `authentication: ON_USE` — there is no install-time
credential; the door's 401 on first use starts the sign-in). Both name the
marketplace `dream` and list `dream-substrate` at `./plugin`; the manifest test
holds them to that.

### Verified against live docs

Every field in every manifest here was checked against the current published
schema or reference, not written from memory:

| File | Source |
|---|---|
| `.claude-plugin/plugin.json` | [Plugins reference](https://code.claude.com/docs/en/plugins-reference) · [`claude-code-plugin-manifest.json`](https://json.schemastore.org/claude-code-plugin-manifest.json) |
| `../.claude-plugin/marketplace.json` | [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) · [`claude-code-marketplace.json`](https://json.schemastore.org/claude-code-marketplace.json) |
| `.mcp.json` | [MCP configuration](https://code.claude.com/docs/en/mcp) — `type` is required alongside `url`; a remote server declared without `headers` authenticates through the OAuth discovery flow on its first 401 |
| `hooks/hooks.json` | [Hooks reference](https://code.claude.com/docs/en/hooks) — `SessionStart`, `type: "command"`, stdout-as-context on exit 0 |
| `plugin.json` | [Agent Plugins 1.0 manifest](https://agent-plugins.org/plugin-authors/manifest) |
| `mcp.json` | [Agent Plugins 1.0 MCP schema](https://agent-plugins.org/schemas/1.0.0/mcp.schema.json) — `streamable-http`, not `http` |
| `.codex-plugin/plugin.json` | [Codex plugin packaging](https://developers.openai.com/codex/plugins/build) · [`codex-rs/core-plugins/src/agent_plugin_manifest.rs`](https://github.com/openai/codex/blob/main/codex-rs/core-plugins/src/agent_plugin_manifest.rs) — the overlay applied to an Agent Plugins root manifest supplies `hooks`, `apps`, `interface` only |
| `../.agents/plugins/marketplace.json` | [Codex plugins](https://learn.chatgpt.com/docs/plugins) · [`codex-rs/core-plugins/src/marketplace.rs`](https://github.com/openai/codex/blob/main/codex-rs/core-plugins/src/marketplace.rs) — discovery order `.agents/plugins/marketplace.json` → `.claude-plugin/marketplace.json`; the bare `"./plugin"` source form is accepted; `policy.installation` ∈ `AVAILABLE` / `INSTALLED_BY_DEFAULT` / `NOT_AVAILABLE`, `policy.authentication` ∈ `ON_INSTALL` / `ON_USE` |
| Codex's reading of `mcp.json` | [`codex-rs/codex-mcp/src/plugin_config.rs`](https://github.com/openai/codex/blob/main/codex-rs/codex-mcp/src/plugin_config.rs) — accepts a `mcpServers` wrapper or a bare server map, a `url` server as streamable HTTP, and `type` ∈ `http` / `streamable_http` / `streamable-http` / `stdio` |

### Two things to know

- **The manifests are portable by construction.** Neither MCP config carries
  a header, a bearer, or an environment placeholder, so there is nothing for
  a client to expand and nothing for a strict Agent-Plugins client to send
  literally. Any harness that implements the MCP authorization flow (Claude
  Code, Codex, Cursor, MCP Inspector) discovers Dream's authorization server
  from the door's 401 and signs in; `test_plugin_manifests.py` asserts the
  configs stay credential-free.
- **The `$schema` values are `json.schemastore.org`-hosted**, matching what
  Anthropic's own bundled marketplace manifest uses. The docs describe the field
  as being for editor autocomplete and validation (and explicitly ignored at
  load time for `marketplace.json`), so it is advisory — but both documents
  validate against their published schema, and `claude plugin validate` passes
  on the plugin directory and on the repo root.

## Runbook: the door origin

`https://dream-30pu.onrender.com/v1/mcp` is the Render service host, taken
verbatim from `backend/config.prod.yaml` → `api.api_public_origin`. It is the
API host, **not** the `www.dreamluci.com` frontend: Vercel rewrites `/api/*`
only, so `/v1` and `/v1/mcp` are served from Render directly. The same value is
published as the canonical resource identifier in the RFC 9728
protected-resource metadata document.

Moving the API behind a custom domain means changing three things in the same
deploy — `api_public_origin` in `config.prod.yaml`, `.mcp.json`, and `mcp.json`
— or every connected agent's resource identifier goes stale.
