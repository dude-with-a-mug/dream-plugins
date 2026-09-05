#!/usr/bin/env python3
"""Inspect or transfer a selected file; authentication stays in the MCP client."""

import argparse
import hashlib
import http.client
import ipaddress
import json
import os
import socket
import ssl
import stat
import sys
from urllib.parse import urlsplit

TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".html": "text/html",
    ".htm": "text/html",
}
CHUNK = 64 * 1024
MAX_RECEIPT = 64 * 1024


class UploadError(Exception):
    """A safe error: messages never contain a URL, response body, or credential."""

    def __init__(self, code, message, uncertain=False):
        super().__init__(message)
        self.code = code
        self.uncertain = uncertain


def inspect_file(path):
    """Return metadata and a digest for an explicit regular file."""
    suffix = os.path.splitext(path)[1].lower()
    if suffix not in TYPES:
        raise UploadError("unsupported_type", "Use a PNG, JPEG, WebP, Markdown, or HTML file.")
    digest = hashlib.sha256()
    with os.fdopen(os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0)), "rb") as source:
        before = os.fstat(source.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size <= 0:
            raise UploadError("invalid_file", "Select a nonempty regular file.")
        while True:
            chunk = source.read(CHUNK)
            if not chunk:
                break
            digest.update(chunk)
        after = os.fstat(source.fileno())
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise UploadError("file_changed", "The file changed during inspection; inspect it again.")
    return {"content_type": TYPES[suffix], "declared_bytes": before.st_size, "sha256": digest.hexdigest()}


def read_reservation(path=None):
    """Read a bounded reservation from stdin or an owner-only regular file."""
    if path is None:
        raw = sys.stdin.read(MAX_RECEIPT + 1)
    else:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        with os.fdopen(fd, "r", encoding="utf-8") as source:
            info = os.fstat(source.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077:
                raise UploadError(
                    "insecure_reservation_file", "Reservation files must be regular and owner-only (0600)."
                )
            if hasattr(os, "getuid") and info.st_uid != os.getuid():
                raise UploadError("insecure_reservation_file", "Reservation file must belong to this user.")
            raw = source.read(MAX_RECEIPT + 1)
    if len(raw) > MAX_RECEIPT:
        raise UploadError("invalid_reservation", "Reservation JSON exceeds the size limit.")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise UploadError("invalid_reservation", "Expected a reservation JSON object.")
    return value


def transfer(path, reservation, expected_sha256=None, timeout=30):
    """Stream a file once to the reserved URL without redirects or credential access."""
    metadata = inspect_file(path)
    if expected_sha256 and metadata["sha256"] != expected_sha256:
        raise UploadError("file_changed", "The file no longer matches its inspected digest.")
    if reservation.get("upload_method") != "PUT":
        raise UploadError("invalid_reservation", "Expected a PUT reservation.")
    if metadata["declared_bytes"] != reservation.get("declared_bytes"):
        raise UploadError("file_changed", "The file size differs from the reservation; inspect it again.")
    headers = reservation.get("required_headers")
    if (
        headers != {"Content-Type": metadata["content_type"]}
        or reservation.get("content_type") != metadata["content_type"]
    ):
        raise UploadError("type_mismatch", "The file type differs from the reservation.")
    upload_id = reservation.get("upload_id")
    if (
        not isinstance(upload_id, str)
        or not upload_id
        or len(upload_id) > 80
        or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in upload_id)
    ):
        raise UploadError("invalid_reservation", "Missing or invalid upload ID.")
    raw_url = reservation.get("upload_url")
    if not isinstance(raw_url, str):
        raise UploadError("invalid_upload_url", "Expected an absolute upload URL.")
    address = urlsplit(raw_url)
    if not address.hostname or address.username or address.password or address.fragment:
        raise UploadError("invalid_upload_url", "Expected an absolute upload URL without user information.")
    if address.scheme == "https":
        connection = http.client.HTTPSConnection(
            address.hostname, address.port, timeout=timeout, context=ssl.create_default_context()
        )
    elif address.scheme == "http":
        try:
            loopback = ipaddress.ip_address(address.hostname).is_loopback
        except ValueError:
            loopback = False
        if not loopback:
            raise UploadError(
                "insecure_upload_url", "HTTP is allowed only for a literal loopback address in local development."
            )
        connection = http.client.HTTPConnection(address.hostname, address.port, timeout=timeout)
    else:
        raise UploadError("insecure_upload_url", "Uploads require HTTPS (loopback HTTP is allowed for development).")
    # Connect explicitly: http.client otherwise opens the socket lazily inside
    # endheaders(), which would make "no network at all" look like an uncertain
    # transfer. Nothing has left this machine until the connection exists.
    try:
        connection.connect()
    except OSError as exc:
        connection.close()
        raise UploadError(
            "no_connection",
            "Could not reach storage; nothing was sent. A sandboxed client may be blocking outbound "
            "traffic: rerun the same upload with network access granted for this command, against the "
            "same reservation.",
        ) from exc
    sent = False
    try:
        with os.fdopen(os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0)), "rb") as source:
            before = os.fstat(source.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size != metadata["declared_bytes"]:
                raise UploadError("file_changed", "The file changed before transfer.")
            target = address.path + ("?" + address.query if address.query else "")
            connection.putrequest("PUT", target)
            connection.putheader("Content-Type", metadata["content_type"])
            connection.putheader("Content-Length", str(before.st_size))
            connection.endheaders()
            sent = True
            digest = hashlib.sha256()
            remaining = before.st_size
            while remaining:
                chunk = source.read(min(CHUNK, remaining))
                if not chunk:
                    raise UploadError(
                        "file_changed", "The file changed during transfer. Do not publish this reservation.", True
                    )
                digest.update(chunk)
                connection.send(chunk)
                remaining -= len(chunk)
            if source.read(1) or digest.hexdigest() != metadata["sha256"]:
                raise UploadError(
                    "file_changed", "The file changed during transfer. Do not publish this reservation.", True
                )
            response = connection.getresponse()
            if 300 <= response.status < 400:
                raise UploadError("redirect_refused", "Storage returned a redirect; it was not followed.")
            if not 200 <= response.status < 300:
                raise UploadError(
                    "upload_rejected",
                    "Storage rejected the upload (HTTP %d)." % response.status,
                    response.status >= 500 or response.status == 409,
                )
    except (OSError, http.client.HTTPException) as exc:
        raise UploadError(
            "transfer_uncertain" if sent else "transfer_failed",
            "Transfer did not return a confirmed result. Try publishing with the same upload ID; if that "
            "reports artifact_upload_missing, rerun the same upload against the same reservation "
            "(with network access granted) rather than reserving again."
            if sent
            else "The connection dropped before the request was sent; the file was not uploaded. Rerun the "
            "same upload with network access granted for this command, against the same reservation.",
            sent,
        ) from exc
    finally:
        connection.close()
    return {"status": "uploaded", "upload_id": upload_id, **metadata}


class SafeArgumentParser(argparse.ArgumentParser):
    """Keep invalid command lines machine-readable without echoing arguments."""

    def error(self, message):
        print(json.dumps({"error": True, "code": "invalid_arguments", "message": "Invalid arguments; see --help."}))
        raise SystemExit(2)


def main():
    """Expose inspection and transfer as small JSON-in/JSON-out commands."""
    parser = SafeArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("file")
    upload = commands.add_parser("upload")
    upload.add_argument("file")
    upload.add_argument("--reservation-file")
    upload.add_argument("--sha256", required=True, help="Digest returned by inspect; never a credential.")
    upload.add_argument("--timeout", type=float, default=30)
    args = parser.parse_args()
    try:
        if args.command == "inspect":
            result = inspect_file(args.file)
        else:
            if not 0 < args.timeout <= 300:
                raise UploadError("invalid_timeout", "Timeout must be between 0 and 300 seconds.")
            result = transfer(args.file, read_reservation(args.reservation_file), args.sha256, args.timeout)
        print(json.dumps(result))
        return 0
    except UploadError as exc:
        result = {"error": True, "code": exc.code, "message": str(exc), "uncertain": exc.uncertain}
    except (OSError, ValueError, TypeError, KeyError, socket.timeout):
        result = {"error": True, "code": "invalid_input", "message": "Could not read the selected file or reservation."}
    print(json.dumps(result))
    return 1


if __name__ == "__main__":
    sys.exit(main())
