---
name: dream-substrate
description: Use in any repo connected to Dream — the `dream` MCP server is registered, or an idea binding sits in `.mcp.json` (Claude Code) or `.codex/config.toml` (Codex) — and to connect one that is not yet bound. Covers binding a repo to a Dream idea, orienting from the task board, reading the idea's substrate (graph, history, branch diff, clusters) before you build, and contributing back through proposals, tasks, branches, and the commit ceremony. Triggers on "check Dream", "what's on the board", "pick up a task", "log this to the idea", "connect this repo to Dream", starting or finishing a task, hitting a decision the idea might already own, discovering the spec was wrong, and opening a what-if.
---

# Dream Substrate — participation, operationally

This repo is a checkout of an idea. The code lives here; the idea's reasoning —
what it is, what's decided, what's still open, and why — lives in Dream, and you
reach it through the `dream` MCP server. You are a contribution surface to that
substrate, the same as Luci is. Same tools, same grammar, same lattice.

This file carries the **choreography**: how to bind a repo, how to orient, what
to do at each moment, and what the ceremony looks like end to end.

## Authority

The MCP server's own `instructions` — delivered at every connection — carry the
canonical participation doctrine and the current state of the surface. **Where
this file and the server disagree, the server wins.** A plugin can be months
stale; the connection never is. In particular, do not assume a tool exists
because it is named here: the surface is v0/unstable and grows in waves. If a
tool is absent from the connection, it has not landed yet — say so and stop,
never improvise a substitute path.

## First use in a repo: bind, then echo, then write

Two acts, at two levels. **Installing the connection** is once per machine —
plugin plus sign-in, no idea involved. **Binding a repo to an idea** is once per
repo: an `X-Dream-Idea` header in the repo's committed binding file — the
`dream` server's `headers` in `.mcp.json` for Claude Code, its `http_headers`
in `.codex/config.toml` for Codex — saying "this repo is a checkout of that
idea." Non-secret, inherited by every clone.

Resolve three things before your first write: **which idea**, **which branch
posture**, **which connection identity**.

1. **Repo already bound?** The binding file carries `X-Dream-Idea` — a
   teammate committed it. Setup is done; inherit it and move on.
2. **A paste-block carried an idea id?** (copied from an idea's page on
   dreamluci.com, which bakes it in) — write the binding, then confirm aloud.
   The echo catches a stale or mispasted id in the first ten seconds.
3. **Neither?** Call `dream_ideas`. It answers the idea question and the
   identity question at once: it lists only what this connection can see, with
   your role on each. Ask the user which idea this repo is for, bind, confirm.

**Branch posture** — pick one, name it in the echo, and hold it for the session
(one conversation, one branch):

- **A task's branch** — the normal case. `start_task_branch` on the activated
  task brings its branch, grounding, spec artifact, and pinned commit with it.
- **A what-if branch** — `create_branch`, **only when the user directs it**
  (see What-if etiquette below).
- **Mainline, read-only** — orientation and grounding only. Do not propose onto
  a protected branch; get a branch first.

**Confirm-echo template.** Print this compact block before the first write of
the session, filled from `dream_ideas` / `dream_context` / `list_tasks`:

```
Dream   <Idea title> (<idea-id>)
Branch  <branch name> — <task branch | what-if | mainline, read-only>
As      <connection name> · <your role on this idea>
Board   <n> ready, <n> open · context pinned at <Dream-Commit id>
```

**Then write the breadcrumb.** Whichever path bound the repo (2 or 3), append
~5 lines to the repo's `CLAUDE.md` / `AGENTS.md` so every future session in this
checkout engages Dream without being told:

```markdown
## Dream

This repo is a checkout of Dream idea **<title>** (`<idea-id>`) — the reasoning
behind the code lives there, not here. Door: `<host>/v1/mcp`, reached through
the `dream` MCP server; sign in with `claude mcp login dream` /
`codex mcp login dream` if a call returns 401. Default branch posture: work on the task's
branch; never propose onto `main`. At task start, orient with `list_tasks` and
`dream_context`; record what you learn as proposals. Load the `dream-substrate`
skill for the full doctrine.
```

Commit it once. It is inherited by every clone and always in context.

## The connection

- You reach Dream through a **connection** the user approved in their browser:
  `claude mcp login dream` / `codex mcp login dream` follows the door's
  401 challenge to Dream's sign-in and consent page, and the tokens it mints
  are held by the harness. Nothing about it belongs in a file you write.
- **Never** echo, print, log, or write any token, and never pass one as a
  CLI argument. Idea and branch ids are non-secret and safe to commit; the
  connection's tokens are the only secret, and they are not yours to handle.
- A headless process (CI, cron) uses a personal access token from Settings →
  Tokens, presented from the `DREAM_PAT` environment variable. Same rule: the
  variable is referenced, never read back.
- **On 401:** the connection is gone — signed out, expired from a month's
  disuse, or revoked in Settings → Connections. Tell the user to run their
  harness's `mcp login dream` again, or to check Settings → Connections. Do not
  ask them to paste anything into the conversation.
- **On 403 `insufficient_scope`:** the connection was not granted that
  authority. Stop and report what you needed; a wider grant is the user's
  decision, made on the consent page or in Settings → Connections, never by
  rewording the call.
- Disconnecting in the terminal only forgets this machine's tokens; revoking
  in Settings → Connections is what ends the connection everywhere.
- To repoint a repo, edit the non-secret `X-Dream-Idea` / `X-Dream-Branch`
  headers only — they take effect on reconnect. For a one-off read outside the
  pinned scope, pass the `idea` / `branch` tool arguments instead of editing
  config.

## Read doctrine: ground before you speak

**At task start.** `list_tasks` → `get_task` for the mission, its grounding, and
its branch plan; then `dream_context` for the compiled idea and `get_branch_diff`
for the delta and the crossings — contradictions and resolutions against shared
truth. Do not start implementing from the task prompt alone when a compiled
context is one call away.

**Before an architectural choice.** `search_graph` with `node_type=decision`
plus a query for the topic. The decision may already exist. If it does, build to
it — do not relitigate it in code, comments, or a PR. If it contradicts what you
were about to do, that is signal: surface it as a proposal, not a shrug.

**When a node id appears anywhere** — compiled context, a diff lane, a commit
message, a PR body — `explore_graph` it rather than guessing from the label. The
payload and its relationship lanes (contradicts, depends_on, resolves, evolves,
addresses) are ground truth; your inference is not. An artifact node's
material is withheld even at `detail=full` — a document's body is stubbed to
`content.body_omitted` / `content.body_chars`, a mockup's or image's storage
paths are bare — so pass `include_content=true` for the one artifact you
actually need. For a document that inlines the body. For a mockup it inlines
the primary HTML as `content.primary.html` (capped; `html_truncated` says
when), adds a signed `*_url` beside every stored path, and returns the
screenshot as an image block after the JSON so you can look at the page —
or says `screenshot_available: false` when none was ever rendered. An image
artifact returns its picture the same way. Neighbors never carry material.
When the question is what
changed, what came before, why a node was retired, or what replaced it, use
`read_history` with that node id — retired ids are valid there even when
`explore_graph` cannot see them.

**Before you review or commit.** `review_ledger` for what's left,
`search_proposals` / `summarize_proposals` to see it grouped and counted,
`get_review_story` for the narrative, `list_clusters` for the idea's table of
contents. `list_idea_branches` and `get_analysis_report` when scope or a prior
analysis is the question.

Cite stable node ids in everything you say about the idea.

## Contribution doctrine (digest — the server's instructions are canonical)

**Capture-first.** A discovery that stays in the conversation is lost. When you
learn something the idea does not know, propose it: `propose_nodes` for the
thought, decision, or question; `propose_edges` for what it contradicts,
depends on, resolves, or evolves. Ground it — when the contribution comes from
observed material, carry typed evidence (repository, path, blob SHA, excerpt,
captured-at); without it Dream records only your connection, the tool, and the
time, which is attribution rather than grounding. "Spec assumed X;
`auth/jwt.py:373` says Y — which wins?" is a question proposal with a
contradicts edge, not a paragraph in a PR description.

**Drift gets flagged, never silently fixed.** When code reality and the idea's
belief have diverged, the fix in the repo is not the fix in Dream. Propose the
correction — `propose_status_change` on reasoning that no longer holds, a
contradicts edge against the assumption you broke — and let the founder ratify
it. Editing the code and saying nothing leaves the idea wrong forever.

**Capture freely; reorganize only when directed.** Noticing out-of-scope work is
a `create_task`, ten seconds, and you keep going — it does not derail the
session and it does not need permission. Restructuring the board —
`update_task`, `connect_tasks`, `cancel_task`, `reopen_task` — happens when the
user asks for it. Check for duplicates before creating. Never reorganize
silently.

**Cancellations carry reasons.** `cancel_task` without a recorded reason is a
silent vanish; a losing or deferred direction must die legibly.

**What-if etiquette: humans fork freely, agents ask first.** A what-if branch is
warranted only when the alternative needs *development* to be judged — when
armchair comparison fails. Surface alternative directions as question proposals
or captured tasks; open a `create_branch` what-if **only when directed**. A
closed what-if still leaves a decision node recording the comparison.

**One conversation, one branch.** Drift stays put — sorting happens at the exit,
in review, not mid-flow. A genuine pivot means activating a different task, and
its branch arrives with it.

**Editing before ratification.** Proposals are live until committed:
`edit_proposed_node` / `edit_proposed_edge` to correct one,
`apply_proposal_action` to stage or unstage it for the commit.

**Artifacts enter once.** A spec, mockup, or document authored locally comes
home through `publish_artifact` — with `suggested_edges` to the reasoning that
shaped it and its repo provenance. If the file carries a `dream-provenance`
comment naming an existing artifact node, publishing proposes a *revision* of
that node, not a duplicate.

**A file on disk never goes through `content`.** Inline `content` is for short
text you composed in this turn, under 16,000 characters; past that the door
refuses with `inline_content_too_large`. Anything that exists as a file — a
spec, an HTML mockup, an image — takes the upload path, which moves the bytes
without them ever passing through you:

1. Mint: `POST /v1/ideas/{idea}/artifact-uploads` with your bearer token and
   `{"content_type": "text/html", "declared_bytes": <size>, "kind": "artifact_content"}`.
   The response carries `upload_id` and a signed `upload_url`.
2. PUT the file to `upload_url` (`curl -X PUT --data-binary @file`).
3. `publish_artifact` with `upload_id` (plus `target_title`, `suggested_edges`,
   and `evidence`). For a mockup, mint a second reservation with
   `kind: "preview_image"`, PUT the screenshot, and pass it as
   `preview_upload_id`.

`docs/substrate-api.md` ("reserve an upload") has the curl form. Publishing is not a ceremony of its own: it creates
proposals, and the Commit that carries them alongside their reasoning is the
exit. Never invent a second way into the graph. Each direct publish is a fresh
contribution — republishing the same content proposes it again, so check
`search_proposals` before re-sending something that may already be pending.

## The commit ceremony

Proposals accumulate on the branch; a commit is the branch reaching a moment of
clarity. Three steps, and the stamp is not optional:

1. `prepare_commit` — opens or refreshes the draft. It returns
   `commit_draft_id`, `commit_draft_version`, and `bundle`: one line per staged
   proposal the draft holds (id, verb, label), in draft order, capped at 50
   (`truncated` says when; `search_proposals(state='staged')` reads the rest).
   **Carry the stamp, and read the bundle** — it is what the Commit will land.
2. If the bundle is not right, curate with `apply_proposal_action`
   (stage/unstage/discard) and call `prepare_commit` again so the draft and
   its stamp cover the change. A stage receipt's `inferred_edge_proposal_ids`
   names lineage edges the pipeline staged that you did not propose; unstage
   them by id if the lineage is wrong.
3. `commit_changes` with `commit_draft_id` and `expected_draft_version` set to
   exactly what step 1 returned. The stamp proves you read *this* draft.

You are a stateless caller: nothing tracks the draft for you. If the version
mismatches (`commit_draft_version_conflict`), another session changed the draft
— re-read and re-prepare; do not retry with the old stamp. If the branch already
committed (`committed_since_prepare`), that is an honest refusal, not your
receipt. Branch law authorizes the commit; there is no approval click anywhere.

Then open the MR. Merging completes the task and unblocks whatever depended on
it; review happens before the merge when others are affected, after it when the
founder works alone.

## Downstream: what you write in git

Every commit message and PR description that came out of substrate-grounded work
cites the **node ids** you built against and the **`Dream-Commit` id** your reads
resolved at (the `Dream-Commit:` line in the compiled context;
`resolved_at_commit_id` on every branch-scoped response). That is what lets a
reviewer replay exactly what you knew when you wrote the code.

## The surface

Converged names — one contract, both surfaces. Use these; nothing else.

- **Graph reads:** `explore_graph` · `search_graph` · `read_history` ·
  `get_branch_diff` · `list_clusters` · `list_idea_branches` ·
  `get_analysis_report`
- **Review reads:** `search_proposals` · `summarize_proposals` ·
  `review_ledger` · `get_review_story`
- **Proposal spine:** `propose_nodes` · `propose_edges` ·
  `propose_status_change` · `edit_proposed_node` · `edit_proposed_edge` ·
  `apply_proposal_action`
- **Ceremony:** `prepare_commit` · `commit_changes`
- **Publication:** `publish_artifact`
- **Board:** `list_tasks` · `get_task` · `create_task` · `update_task` ·
  `connect_tasks` · `cancel_task` · `reopen_task`
- **Door orientation (MCP only):** `dream_ideas` · `dream_context` ·
  `create_branch` · `start_task_branch`

Workspace drafts, agenda, navigation, and Bert delegation are Luci's chat-surface
chrome and do not travel — your scratchpad is this filesystem, and your consent
surface is this conversation.
