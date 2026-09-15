# Preparing and committing understanding

Load for meaningful proposals, working-branch setup, or a branch commit. The
entry point's shared policy governs delegation; tool descriptions supply the
current call contract.

## Prepare a coherent contribution

Capture directed work as a task and set its status explicitly under the
user's intent. Reuse suitable tasks and branches. Read `get_task` before
starting a branch and preserve its authoritative starting point. Status changes
require the current `status_version`; refresh after a conflict rather than
overwriting newer work.

`update_branch(name?, purpose?)` renames or re-purposes the branch the call is
standing in. Author or idea owner only; main cannot be renamed; a merged
branch is frozen; a closed branch may still be edited so a closing note can
land in its purpose. The slug and URL never change on rename, and a duplicate
name fails with `branch_name_duplicate`. The receipt says what changed.

Use `propose_nodes` for thoughts, decisions, and questions, with
`propose_edges` for meaningful contradictions, dependencies, resolutions, or
evolution. Node proposal responses reserve a stable `node_id` before graph
materialization; use returned identities as the tool permits, rather than
assuming creation already committed a graph row. Evidence from observed
material should carry the repository, path, commit SHA, excerpt, and a code
line range or document heading. Connection/tool/time attribution alone does
not establish grounding.

Distinguish a deliberate policy change from code drift and a temporary
compromise. Preserve consequential discrepancies as questions or corrections,
with truthful relationships to the existing assumption. Four verbs change a node already in the record: `edit_node` for the same claim
in better words, `replace_node` when a new belief takes over (it records what
took over, which a retirement cannot), `retire_node` when nothing does, and
`restore_node` to bring a retired or replaced node back. Retire and restore require a
reason that explains what changed; a restatement of the action is refused.
An artifact's new version is a publication, not `replace_node`; reserve
`replace_node` for a genuinely different artifact taking over. Do not invent a
settled rationale merely because implementation is easy. Discussion refines
these same proposals; it creates no separate report-approval step.

Proposals remain editable before commitment: `update_proposed_node` and
`update_proposed_edge` refine them; `apply_proposal_action` stages, unstages, or
discards selected work. Honor staging warnings, including degraded duplicate
review: successful staging does not imply every duplicate check succeeded.
A stage receipt's `inferred_edge_proposal_ids` identifies lineage added by the
pipeline; inspect and unstage incorrect lineage by ID.

Tasks are the ledger of directed work, and they express useful next work.
Capture freely: an unrelated discovery becomes a task and you keep going. Check
the board first so a second task does not restate the first. When you stop
with a task's work unfinished, update its summary with `update_task` so where
it stands is recorded rather than lost. Reorganize existing tasks,
dependencies, cancellations, or reopened work only when directed; cancellations
need a reason so a deferred direction remains legible. Publish useful local
artifacts through the publishing guidance when ready; the resulting proposals
belong with the reasoning that supports them.

## Put a branch away

`close_branch(reason)` is the branch's own cancellation, and the reason is
required for the same reason a task's is. It does one of two things and says
which: a branch that never committed is deleted outright; a branch that owns
Commits is archived with `closed_at` and `close_reason`, and every Commit
stays readable. Guards: author or idea owner, not main, not merged, no open or
approved merge request (close it first). Closing an already-closed branch
changes nothing.

Tasks and branches stay decoupled both ways. Cancelling a task leaves its
branches open, because one of them may be someone else's; closing a branch
never cancels its task. Closing the last live branch leaves task status
unchanged. Offer `cancel_task` only if the direction itself is dead. Reopening
a closed branch is done from the web app.

## Read the staged outcome

Staging returns one structured graph-change preview. Read the before/after
facts, inspect omitted material with `read_review_preview`, and explain their
significance in the user's context. Retirement does not revive an older
belief and preview does not create follow-up proposals. Restore only when the
user's intent authorizes it; no second confirmation is needed for intent
already stated. For a merge, read `read_review_preview(mode="merge")` so the
stamp covers the destination outcome, and pass that stamp to approval and merge.

## Commit the reviewed bundle

A natural stopping point can justify preserving supported understanding on the
working branch. Follow the actual bundle and stamp mechanics; conversational
permission does not replace them.

A Dream Commit is not a git commit. Its `title` is the moment of clarity
stated as one claim in the founder's words, at most 80 characters: "Chef Bert
is Workshop Bert in an apron", not "Update Bert artwork". Its `message` is
three to five plain sentences, at most 600 characters: what was settled and why
it beat the alternative, what it changes for what comes next, and what remains
open. Neither carries node, proposal, or Dream-Commit ids, bundle listings, or
`Dream-Commit:` trailers; the bundle already records what the Commit lands, and
the Dream-Commit id belongs in your git commits and PR text.

1. Call `prepare_commit`. Read the returned `bundle` and retain
   `commit_draft_id` and `review_stamp`. The bundle covers staged
   proposals in draft order and is capped at 50. Inspect the full proposal
   payloads needed to judge every current draft member; labels alone do not
   establish that its actual content is supported. Use the focused reads below
   to recover missing content or a truncated bundle.
2. If it includes unrelated or unsupported work, curate it with
   `apply_proposal_action` and prepare again. Never commit other contributors'
   pending work merely because it happened to be staged.
3. Call `commit_changes` with that exact `commit_draft_id`, mapping the
   returned `review_stamp` to its `expected_review_stamp` argument.
   No session tracks or refreshes the stamp for an external caller.

For each known draft proposal ID, use `search_proposals` in the same branch
or MR scope with this argument shape (replace the example ID):

```json
{"filter":{"state":["staged"],"change_kind":"any","proposal_ids":["proposal-id"]},"detail":"full"}
```

`change_kind="any"` includes cluster reconciliation; the default `members`
filter would omit it. `detail="full"` supplies actual payloads that the default
brief output omits. Batch known IDs narrowly and reduce the batch if capped.
For a truncated bundle, discover the remaining staged IDs using that same
state/all-kind filter, omitting `proposal_ids` only for discovery; narrow by
visible cluster, verb, or reconstruction checkpoint if capped. Reconcile unique
inspected IDs with the prepared bundle's total and every returned draft ID.
Do not commit while any draft member or its material remains uninspected, or
when capped reads prevent establishing complete coverage. If membership or
content changed during inspection, prepare again and inspect the updated draft.

On `review_changed`, reread and prepare the changed draft;
never retry an old stamp. `committed_since_prepare` means the branch already
committed, not that another session's receipt belongs to this caller. Inspect
current state before taking the next action. Editing or curation after
preparation always requires another prepare.

A commit preserves branch understanding. Shared incorporation uses the review
and merge workflow when authorized, and a branch commit alone does not make a
task Done. If understanding did not change, there is nothing new to commit.
