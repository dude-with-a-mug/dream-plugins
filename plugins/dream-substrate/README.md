# dream-substrate

The plugin is the box the connection ships in. One directory carrying the
**skill** (doctrine), the **MCP server reference** (capability), and a
**optional SessionStart hook** (ambient orientation) — installed once, instead of a
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
marketplace manifests into it on every merge that changes the package, so
marketplace-installed plugins pick up updates when a release lands. Inside a checkout of the source
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
`read` always and `contribute` pre-ticked when requested. Contribution
includes owner approval and merges when Dream's branch rules permit them.
Give the connection a label (it is the attribution on every
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
| Skill metadata | `skills/dream/SKILL.md` frontmatter | Available for discovery; describes when Dream participation helps. |
| Skill body | `skills/dream/SKILL.md` | Loaded on activation: shared participation policy and conditional workflow routing. |
| References | `skills/dream/references/*.md` | Setup, reading, contributing, publishing, and reviewing are loaded only when the current task needs them. |
| MCP server | `.mcp.json` (read by both Claude Code and Codex) | Registers `dream` as a remote HTTP MCP server at `https://dream-30pu.onrender.com/v1/mcp`. No credential: the door's 401 challenge starts the OAuth sign-in (`claude mcp login dream` / `codex mcp login dream`). |
| Hook | `hooks/hooks.json` → `hooks/session-start.sh` | On SessionStart, prints a non-secret declaration hint, without claiming that the active connection is bound — and prints nothing at all in a repo that is not bound to a Dream idea. Uses the shared optional hook file where the client supports and trusts it. |

All three are discovered from their default locations, so the Claude Code
manifest declares metadata only — no `skills` / `hooks` / `mcpServers` path
fields. Adding them would be redundant, and the `commands`/`agents` variants of
those fields *replace* the defaults rather than adding to them. Codex also discovers the standard `hooks/hooks.json` location; the overlay
only carries display metadata. This keeps the package compatible with both
runtime discovery and the stricter local manifest validator.

**Policy ownership.** `backend/dream/core/doctrine/participation.md` in the
source repo owns the shared participation policy. The skill carries a bounded
verbatim excerpt checked against the runtime loader; the server and Luci use
that same policy. Current server guidance governs an older plugin. Individual
tools describe immediate effects, prerequisites, handles, and recovery, so
correct use does not require installing the skill.

Initialization instructions arrive at connection setup. Tool descriptions and
schemas load according to the host's eager/deferred discovery behavior. The
complete catalogue size is not a claim about startup or task context. Reports
should count metadata, activated body, selected references, actual rendered
tool schemas (including wrappers), and responses separately.

### The optional hook

The hook reads from `CLAUDE_PROJECT_DIR`, falling back to the process working
directory. It checks `.mcp.json` and `.codex/config.toml` for an `X-Dream-Idea`
declaration, then `CLAUDE.md`, `AGENTS.md`, and `.claude/CLAUDE.md` for an idea
breadcrumb. It prints one constant hint when a declaration is present and
nothing otherwise. It does not parse or echo IDs, URLs, credentials, or file
contents, and does not verify authentication or the effective connection.

There are no network calls or writes, and the hook exits successfully. Hook
trust and execution depend on the client; installation alone does not make a
hook trusted. The same skill and tools remain usable if the hook is unavailable,
untrusted, or disabled. Its hint is never an ingestion or synchronization
trigger. Validate the active binding at setup/reconnect through `dream_context`,
not from the hint.

Package layout tests and manifest validation establish portable packaging;
they do not prove identical hooks, deferred loading, or runtime task behavior
across clients. Record the tested client/version and observed loading separately.

## Two manifests, two marketplaces

The package carries two plugin manifests on purpose, so the same directory
installs in Claude Code and in Codex:

- `.claude-plugin/plugin.json` — the Claude Code manifest.
- `.codex-plugin/plugin.json` — the Codex manifest. It supplies `interface`
  (display name, category) and nothing else: Codex discovers `skills/`,
  `hooks/hooks.json`, and `.mcp.json` from their default locations, so the
  `skills` and `mcpServers` fields are deliberately absent.

**Deliberately not an Agent Plugins 1.0 package.** A root `plugin.json`
carrying the Agent Plugins `$schema` makes Codex 0.147+ treat the directory as
an Agent Plugin and enforce runtime boundaries on its MCP tools: every tool
description is cut at 1,000 bytes, and the plugin's tool specs must fit 64,000
bytes in aggregate, after which Codex silently hides the rest, sorted by name.
The door's 41 tools total roughly 143 KB under those rules, so a 0.1.3 install
saw only the first 20 tools alphabetically and lost `list_idea_branches`
onward. OpenAI's own curated plugins ship the legacy manifest for the same
reason. Reintroduce the portable manifest (`plugin.json` + `mcp.json`) only
once the door's exposed surface fits that budget;
`backend/tests/plugin/test_plugin_manifests.py` asserts both files are absent.

Both harnesses read the one MCP config file, `.mcp.json` (Claude Code
auto-discovers it; Codex's legacy loader defaults to the same file), so there
is nothing to keep in sync.

The repo root carries two marketplace manifests for the same reason:
`.claude-plugin/marketplace.json` for Claude Code and
`.agents/plugins/marketplace.json` for Codex. Codex would fall back to the
Claude Code file if its own were missing, but its documented location is the
`.agents` one, and it is where the Codex-only `policy` block lives
(`installation: AVAILABLE`, `authentication: ON_USE` — there is no install-time
credential; the door's 401 on first use starts the sign-in). Both name the
marketplace `dream` and list `dream-substrate` at `./plugin`; the manifest test
holds them to that.

### Packaging references

These sources document the package layout and client-specific fields. They are
reference links, not a claim that every client runtime was exercised on this
checkout:

| File | Source |
|---|---|
| `.claude-plugin/plugin.json` | [Plugins reference](https://code.claude.com/docs/en/plugins-reference) · [`claude-code-plugin-manifest.json`](https://json.schemastore.org/claude-code-plugin-manifest.json) |
| `../.claude-plugin/marketplace.json` | [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) · [`claude-code-marketplace.json`](https://json.schemastore.org/claude-code-marketplace.json) |
| `.mcp.json` | [MCP configuration](https://code.claude.com/docs/en/mcp) — `type` is required alongside `url`; a remote server declared without `headers` authenticates through the OAuth discovery flow on its first 401 |
| `hooks/hooks.json` | [Hooks reference](https://code.claude.com/docs/en/hooks) — `SessionStart`, `type: "command"`, stdout-as-context on exit 0 |
| `.codex-plugin/plugin.json` | [Codex plugin packaging](https://developers.openai.com/codex/plugins/build) · [`codex-rs/core-plugins/src/loader.rs`](https://github.com/openai/codex/blob/main/codex-rs/core-plugins/src/loader.rs) — the legacy manifest; skills, `hooks/hooks.json`, and `.mcp.json` come from their default locations. The Agent Plugins budget lives in [`codex-rs/core/src/mcp_tool_exposure.rs`](https://github.com/openai/codex/blob/main/codex-rs/core/src/mcp_tool_exposure.rs) |
| `../.agents/plugins/marketplace.json` | [Codex plugins](https://learn.chatgpt.com/docs/plugins) · [`codex-rs/core-plugins/src/marketplace.rs`](https://github.com/openai/codex/blob/main/codex-rs/core-plugins/src/marketplace.rs) — discovery order `.agents/plugins/marketplace.json` → `.claude-plugin/marketplace.json`; the bare `"./plugin"` source form is accepted; `policy.installation` ∈ `AVAILABLE` / `INSTALLED_BY_DEFAULT` / `NOT_AVAILABLE`, `policy.authentication` ∈ `ON_INSTALL` / `ON_USE` |
| Codex's reading of `.mcp.json` | [`codex-rs/codex-mcp/src/plugin_config.rs`](https://github.com/openai/codex/blob/main/codex-rs/codex-mcp/src/plugin_config.rs) — accepts a `mcpServers` wrapper or a bare server map, a `url` server as streamable HTTP, and `type` ∈ `http` / `streamable_http` / `streamable-http` / `stdio` |

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
  are covered by package checks. Claude Code 2.1.260 `plugin validate` passes
  on the plugin directory and on a temporary copied installation. Codex
  0.153.2 has no offline plugin-validation command; filesystem/manifest tests
  cover its declared layout, not authenticated clean-install behavior.

## Runbook: the door origin

`https://dream-30pu.onrender.com/v1/mcp` is the Render service host, taken
verbatim from `backend/config.prod.yaml` → `api.api_public_origin`. It is the
API host, **not** the `www.dreamluci.com` frontend: Vercel rewrites `/api/*`
only, so `/v1` and `/v1/mcp` are served from Render directly. The same value is
published as the canonical resource identifier in the RFC 9728
protected-resource metadata document.

Moving the API behind a custom domain means changing two things in the same
deploy — `api_public_origin` in `config.prod.yaml` and `.mcp.json` — or every
connected agent's resource identifier goes stale.


## Artifact files (Python 3)

The package includes `scripts/artifact_upload.py`; it uses Python 3's standard
library and installs no dependencies. The existing MCP login supplies all
Dream authorization. Inspect a selected file, reserve through
`reserve_artifact_upload`, transfer with the helper, then `publish_artifact`.
The helper never reads OAuth credentials or a PAT. See [publishing guidance](skills/dream/references/publishing.md) for
the exact stdin/0600-file recipe and installed-package-relative helper path. Signed upload URLs are credentials; do not print them.
Images, Markdown specs, and portable HTML share this flow. Supply a local
screenshot for an HTML preview; external HTML is not rendered by Dream's server.

At installation or reconnect, call `dream_context` without `idea` and verify
its resolved idea. Use `.mcp.json` for Claude Code and `.codex/config.toml`
`http_headers` for Codex. Check pre-existing server overrides when declarations
and the active connection disagree. A SessionStart hint only detects a
configuration declaration; it does not verify authentication or routing.

Artifact publication prevents duplicate absorption across artifact formats. Same-format
semantic deduplication is unchanged and is not proof of byte equivalence.
