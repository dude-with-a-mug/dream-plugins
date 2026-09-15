# Reviewing and merging

Load to inspect or complete an MR, incorporate work into shared
understanding, or recover stale review state. The entry point's shared policy
says when a merge is authorized; the service enforces target protection.

## Address and inspect the review

Use `list_merge_requests` / `get_merge_request` for an existing review; each
row names its `author` and `approved_by` as `{handle, name}` people, never
ids. `open_merge_request` creates or reuses the source/target pair and returns
an analysis receipt; a closed source or target is refused with
`branch_closed`, and so is a commit on a closed branch. Poll `get_merge_request` according to
`analysis_status.poll_after_ms`; reads do not generate analysis. Review state
remains readable while analysis is pending, refreshing, stale, or failed.

Pass `merge_request_id` to the supported proposal search, summary, ledger,
curation/edit, prepare, and commit tools to address that review. The MR supplies
its source branch; a repo binding to Main must not redirect it. Ordinary graph
reads remain branch-scoped and need the intended branch explicitly when its
default differs.

Review actual changes, warnings, and source evidence. For an ambiguous cluster,
use `apply_proposal_action(action="resolve_cluster", merge_request_id=...,
filter={"proposal_ids": [one_id]}, resolution=...)`. Select a supported
`MERGE_CLUSTERS` or `PROMOTE_CLUSTER` resolution only after inspecting its
meaning; preview is available. Preserve uncertainty where evidence does not
settle the choice.

When the staged review bundle is ready, `prepare_commit` supplies its
`commit_draft_id`, `review_stamp`, and actual `bundle`. Inspect every
member's actual payload, including cluster reconciliation. Read known draft
IDs in narrow batches using `search_proposals` with this shape, replacing the
example proposal and MR IDs:

```json
{"merge_request_id":"merge-request-id","filter":{"state":["staged"],"change_kind":"any","proposal_ids":["proposal-id"]},"detail":"full"}
```

Default `members` filtering excludes reconciliation and `brief` omits payloads.
When the bundle is truncated, discover remaining staged IDs in this MR with
the same all-kind state filter, omitting `proposal_ids` only for discovery.
Narrow capped results by visible cluster, verb, or reconstruction checkpoint,
then inspect known IDs in smaller full-detail batches. Reconcile unique
inspected IDs with the draft total and every returned draft ID; incomplete
coverage is not permission to commit. Curate unrelated or unsupported entries
and prepare again after any changes. `commit_changes` must carry the returned
`commit_draft_id`, mapping returned `review_stamp` to
`expected_review_stamp`. A conflict requires a fresh read and prepare; never
reuse an old stamp or claim another session's commit.

## Incorporate and explain the result

Commit meaningful source work before merging. Uncommitted proposals on a
merged source expire and are hard-deleted; the receipt's
`expired_proposal_count` reports them. Do not merge while meaningful intended
work remains uncommitted or unsupported staged work has escaped review.

- An unprotected target permits `merge_branch` to open an MR and merge in one
  operation, producing a review-after record.
- A protected target requires `open_merge_request`, genuine owner approval
  through `approve_merge_request`, then `merge_branch`. The source author,
  editor, or owner can merge once the service's checks admit them.

`merge_requires_approved_mr` means required approval is missing.
`merge_source_moved_since_approval` means the source changed: review and obtain
valid approval of the new current head before merging.

Read the receipt and `get_merge_digest`. Explain what was incorporated, what
it means, and any outstanding contradictions or incomplete coverage. A merge
does not change task status: if the merged work achieved a task's intended
outcome, mark it Done with `set_task_status`; otherwise leave its status as it
is. Reading the digest does not mark it read—the user controls that
acknowledgment.

## Analysis recovery

Open questions are visible uncertainty, not automatic blockers. If overview
generation fails, otherwise valid work can merge when actual checks and user
intent permit it. Explain incomplete coverage; do not claim missing overview
contributions were incorporated. Invalid references are reported, never guessed
or silently replaced.

To deliberately retry or refresh analysis before merge, call
`open_merge_request` for the same pair with `refresh_analysis=true` and a new
stable `request_key`; reuse that key only for transport retries. Failed or
interrupted attempts do not automatically repeat paid generation. Closed or
merged reviews cannot refresh. Missed overview contributions remain recorded
for a later merge analysis.
