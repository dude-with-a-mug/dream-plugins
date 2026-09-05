# Returning an artifact

Load when a local spec, document, portable HTML mockup, or image is ready to
return to Dream, or when revising an existing artifact. `publish_artifact`
creates proposals; the commit carrying the artifact and its supporting
reasoning is the exit. Publication is not a separate approval ceremony.

Inspect the actual material against the reasoning it claims to follow. Correct
temporary defects while refining it; preserve deliberate exceptions, changed
rules, and reusable discoveries alongside it. Do not manufacture criticism or
repeat an unchanged review. A retained alternate is a new artifact with honest
relationships; an explicit revision preserves the existing artifact identity.

## Identity, provenance, and pending work

Files handed off by Dream have a `dream-provenance` comment. Check `idea=`
against the intended idea before publishing. If it differs, report the
mismatch and resolve the destination instead of silently importing it. Read
`artifact=` and pass `revises_artifact_id` when improving that artifact. An
explicit revision preserves history. Do not alter titles to evade deduplication.

Include repo provenance and `suggested_edges` to the reasoning that shaped the
material. Direct publication is a fresh contribution, not an idempotent resend;
check `search_proposals` before repeating an uncertain publication. Semantic
deduplication does not prove byte equality.

## File transport

Inline `content` is only for short text composed in the current turn, under
16,000 characters; the server rejects excess with `inline_content_too_large`.
Anything already on disk uses the upload flow, including small files. Choose
one content source according to the tool schema; a file's bytes should not be
read into conversation merely to publish it.

The helper is [../../../scripts/artifact_upload.py](../../../scripts/artifact_upload.py),
resolved **relative to this reference file's directory in the installed
package**, not the shell's current directory or a development checkout. It
uses Python 3's standard library, with no PAT, `.env`, packages, or extra login.
It needs outbound network access from the machine running it. A sandboxed
client may block traffic even after the connection opens; the helper reports
`no_connection` or `transfer_failed` and nothing has been sent. If the client
can grant network access for a single command, request it for the `upload`
step and rerun the same command against the same reservation. Replace
`<helper>` below with that resolved absolute path.

1. Inspect: `python3 <helper> inspect <file>`. Retain `content_type`,
   `declared_bytes`, and `sha256`.
2. Call `reserve_artifact_upload` using those type/size values and
   `kind="artifact_content"`; the active MCP connection authorizes reservation.
3. Feed the reservation JSON to the helper by stdin or an owner-only (0600)
   temporary file outside the repo:
   `python3 <helper> upload <file> --sha256 <digest> --reservation-file <temporary-file>`.
   Never put a signed URL into command-line arguments, logs, commits, or user
   summaries. Remove the reservation file after transfer. The helper does not
   follow redirects, read credentials, or create another reservation.
4. Call `publish_artifact(upload_id=..., target_title=..., suggested_edges=...)`,
   adding revision/provenance fields as applicable. Inspect the receipt for
   actual artifact format and preview availability.

For HTML, provide portable material that needs no local dev server. Optionally
inspect/reserve/upload a screenshot with `kind="preview_image"`, and pass its
`preview_upload_id` in the same publication. HTML plus screenshot is one
artifact. Dream does not execute external HTML to generate screenshots; without
an uploaded screenshot the artifact has no screenshot preview. A screenshot-only
mockup is an image. Specs use Markdown.

On `no_connection` or `transfer_failed`, nothing was sent: do not attempt
publication (it fails with `artifact_upload_missing`) and do not reserve
again. Request network access for the upload command if the client offers it,
then rerun the same upload against the same reservation; stop and report the
missing network path only when no such escalation exists. On
`transfer_uncertain`, attempt publication with the existing reservation before
minting another; if publication fails with `artifact_upload_missing`, re-upload
the same reservation rather than reserving again. On `file_changed`, do not
publish uncertain bytes: inspect the now-stable file and reserve again. A signed URL is a temporary write
credential; revoking the Dream connection prevents publication but may not
invalidate an already-issued storage URL. Keep it private throughout recovery.
