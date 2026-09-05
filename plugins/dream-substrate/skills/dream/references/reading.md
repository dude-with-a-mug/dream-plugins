# Reading reasoning and evidence

Load to answer a reasoning question, trace history or evolution, ground
meaningful work, inspect sources, or compare branch context. Reuse applicable
grounding and refresh only the relevant portion when the task or branch changes.

Use `list_tasks` / `get_task` when existing task context is needed;
`dream_context` supplies the compiled idea and resolved commit, and its
`Dream-Actor` line (the `actor` object in JSON) names you — handle, name,
role, and connection. `list_tasks` narrows with `query` (free text over title,
summary, and every name and handle on the card), `person` (a handle; tasks
they created, were nominated for, or explore on a branch), and `on_branch`
(id, name, or slug; tasks it explores or that were captured from it); the
lane counts keep reporting the whole board. `list_members` is the roster —
`{handle, name, role, is_you}` — and the only place to learn a handle before
naming someone. `get_branch_diff` compares the branch with shared
understanding. Task context is useful, but reading does not require creating
a task. Before an
architectural choice, search relevant decisions with
`search_graph(node_type="decision", query=...)` so settled reasoning informs
implementation. If current behavior conflicts with intent, preserve that
uncertainty rather than treating code as the policy decision.

For a referenced node ID, use `explore_graph` to inspect its content and
relationships. Find relevant nodes with semantic search, then inspect their
relationships using `search_graph(relation_type=..., node_ids=[...])`.
Do not combine a semantic query with a relationship filter. Counts cover the
selected graph scope only; absence of recorded contradictions is not proof
that a design satisfies every requirement.

## Evidence and history

`search_graph`, `get_branch_diff`, `read_history`, and `search_proposals` return
compact `provenance`: a source locator or `null` if none was recorded for the
inspected revision. `total` and `omitted` disclose additional sources. Use a
narrow `detail="full"` read for recorded excerpts and additional evidence.
Connection attribution is not source evidence. Read evidence behind both
positions before recommending a resolution; do not infer a linked document's
contents or authority from its filename.

Use `read_history` for what changed, what came before, why a node was retired,
or what replaced it. Retired IDs remain valid there even when `explore_graph`
cannot see them. Cite stable node IDs where they support a claim or handoff.
Git commit messages and PR descriptions for grounded work should retain the
relevant node IDs and resolved `Dream-Commit` ID (`resolved_at_commit_id` on
branch responses), allowing reviewers to reconstruct what informed the work.

## Tracing an idea's evolution

When asked how an idea or character began or evolved, investigate before
telling its story. Recent commits and top semantic matches do not establish
historical coverage. Look for the earliest recorded form, major changes of
direction, and the reasons behind them. Use `search_graph(include_past=true)`
to find earlier thinking, then `read_history` for relevant revisions and
`explore_graph(include_content=true)` to read the underlying documents.
If results cluster around recent work, broaden or vary the search toward
earlier periods rather than treating those results as the whole history.

Read the evidence behind turning points and follow relevant relationships
to understand what prompted a change. Distinguish imagined directions,
accepted decisions, and demonstrated implementation; a design document alone
does not prove something shipped. Describe an origin as the earliest record
found when coverage is uncertain, and mark inferred connections as your reading.

Keep the investigation proportional to the requested scope and the answer
as simple as requested. A short answer can rest on substantial reading;
ordinary status questions do not require reconstructing the full history.

## Artifact material and focused review reads

Artifact material is withheld even at `detail="full"`. Use
`explore_graph(include_content=true)` for the specific artifact you need:

- Documents inline their body instead of `body_omitted` / `body_chars` stubs.
- Mockups inline `content.primary.html` up to the reported cap, expose signed
  URLs beside stored paths, and return an available screenshot as an image
  block. Honor `html_truncated` and `screenshot_available`.
- Image artifacts return their image. Neighbor nodes never inline material.

Before evaluating pending contributions, use `review_ledger` for unresolved
work, `search_proposals` / `summarize_proposals` for focused groups and counts,
and `get_review_story` for the narrative. `list_clusters` gives the idea's
topics; `list_idea_branches` and `get_analysis_report` address branch scope or a
prior analysis. Closed branches are hidden from `list_idea_branches` unless
`include_closed=true`; a closed row carries `closed_at` and `close_reason`,
and its Commits stay readable through `read_history` and `get_branch_diff`.
Load review guidance only when completing an MR or merge.
Honor partial coverage and warnings; an incomplete read cannot support a
claim that every relevant contribution was checked.
