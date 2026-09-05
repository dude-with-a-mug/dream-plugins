---
name: dream
description: Work with Dream to understand an idea's history and decisions, ground new work, and contribute what you learn. Use for Dream context, task grounding, contributions, artifact publication, reviews, or connecting a repository. Mechanical edits with unchanged understanding need no Dream ceremony.
---

# Dream participation

Use the `dream` MCP connection to keep work grounded in the idea's decisions,
assumptions, and open questions. Work may start in an editor, conversation, or
experiment; opening Dream first is unnecessary. This skill supplies workflow
routing; each connected tool supplies its current input contract and recovery.

## Shared participation policy

The following bounded excerpt comes from Dream's canonical server policy.
Current server guidance governs an older plugin; tool availability and service
checks establish what this connection can actually do.

<!-- participation-policy -->
Dream preserves an idea's reasoning. Users express goals and make consequential decisions; agents handle Dream's mechanics and keep understanding legible.

Ground meaningful work in relevant reasoning and task context; reuse applicable grounding. Capture consequential discoveries with evidence and meaningful relationships. Reconcile at natural stopping points, reusing pending contributions. Mechanical edits, corrected temporary mistakes, unchanged understanding, and session endings alone need no contribution.

Honor existing delegation: necessary working branches and coherent branch commits serve authorized work without repeated approval. Respect requests to review proposals before commitment. Ask only about unresolved intent or consequential scope changes, never for a second yes; code proves behavior, not intended policy. Distinguish reported behavior, assumptions, and recommendations from established facts. Merge test: an instruction naming the destination ("merge this into main") authorizes that merge; "keep Dream updated" alone does not. Never manufacture approval from credential capability.

User intent and service authority must both permit an operation. Preserve scopes, roles, branch protection, and approval of the current head. Semantic changes enter through proposals and commits. Inspect the actual commit bundle, carry its current draft stamp, and re-prepare changed drafts. A branch commit is not a merge or task completion. Keep updates brief and focused on outcomes and uncertainty; routine reads and proposal preparation need no narration.
<!-- /participation-policy -->

## Choose the guidance this work needs

Read only the reference relevant to the next operation. Paths below are
relative to this skill; references are supporting files, not separate skills.
Loading this entry point does not require loading every reference.

| When | Read |
|---|---|
| Connecting a repo, binding an idea, reconnecting, or diagnosing authentication/addressing | [references/setup.md](references/setup.md) |
| Answering a reasoning question, tracing history or evolution, checking sources, or comparing branch context | [references/reading.md](references/reading.md) |
| Preparing a meaningful update, establishing its working branch, or committing supported understanding | [references/contributing.md](references/contributing.md) |
| Returning a locally authored artifact or revising a handed-off artifact | [references/publishing.md](references/publishing.md) |
| Inspecting an MR, completing a merge, or recovering stale review/analysis | [references/reviewing.md](references/reviewing.md) |

A simple question normally needs reading guidance alone. Publication guidance
is needed when material is ready to return, and review guidance when a shared
merge or MR needs attention. If the required tool is absent, report the missing
capability and continue any independent work; do not invent a substitute write
path. An optional SessionStart hint detects configuration only. Correct
participation must work when the hook is unavailable or untrusted.

## Turn the request into useful work

Tasks are the ledger of all directed work. When the user expresses intent to
build, change, or explore something, capture it as a task the moment it is
expressed and start its branch in the same beat with `start_task_branch`; the
expressed intent is the yes, so never ask a second time. Reuse an existing task
or a suitable working branch when one already covers the request. Do not create
a task to answer a question or satisfy orientation. For an explicit task with
known grounding, continue from that context; refresh only when scope or branch
state changes. Capture unrelated work you notice as a task and keep going; a
branch is for the directed work.

Name a branch after the direction it explores: a short human-readable noun
phrase with spaces ("Poncho Bert", "Chef Bert", "Sandbox ruling"), never a
kebab slug ("poncho-bert") and never a to-do verb phrase ("Mock up Poncho
Bert"). When you stop with the work unfinished, record where it stands on the
task with `update_task` so the board can see it.

A branch has two verbs after it opens. `update_branch` renames or re-purposes
the branch you are standing in; the slug and URL never change, main cannot be
renamed, and a merged branch is frozen. `close_branch` puts a branch away and
needs a reason: a branch that never committed is deleted, one with Commits is
archived with its Commits still readable. Closing the last live branch on a
task returns the task to Open; say so and offer `cancel_task` if the direction
itself is dead, never cancel unprompted. Cancelling a task never closes its
branches. Reopening a closed branch is done from the web app.

People are handles. `list_members` lists the idea's roster as
`{handle, name, role, is_you}`; `is_you` is how you learn your own handle, and
`dream_context` opens with a `Dream-Actor` line naming you. Every person on a
read is `{handle, name}` and never an id. `nominee` on `create_task` /
`update_task` and `person` on `list_tasks` take a handle (the `@` is optional);
`person_not_a_member` means read the roster and use a handle from it.

Before recording a discovery, compare it with existing reasoning and pending
contributions. Preserve what changed and why: a supported implementation
finding, deliberate tradeoff, changed assumption, or meaningful question.
Separate observed behavior from intended policy. If an implementation shortcut
would change who can use a feature, ask about that product choice before
promoting it into a decision. Temporary defects corrected during work do not
need durable entries.

At a meaningful milestone, explain what changed, why it matters, and what
remains unresolved. Use precise node, proposal, branch, or commit vocabulary
when it helps inspection, comparison, provenance, or recovery, or when the user
asks. A discussion should refine the actual contribution directly, without a
separate report-approval chore. Preserve stable grounding references in code
handoffs so reviewers can reconstruct the reasoning behind the implementation.
