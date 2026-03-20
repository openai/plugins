#!/usr/bin/env python3
"""Minimal Box REST smoke-test helper using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import uuid
from pathlib import Path
from typing import Any
from urllib import error, parse, request


DEFAULT_API_BASE = "https://api.box.com/2.0"
DEFAULT_UPLOAD_BASE = "https://upload.box.com/api/2.0"


def build_headers(token: str, extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    if extra:
        headers.update(extra)
    return headers


def api_request(
    method: str,
    url: str,
    token: str,
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> Any:
    req = request.Request(
        url=url,
        method=method,
        data=body,
        headers=build_headers(token, headers),
    )
    try:
        with request.urlopen(req) as resp:
            raw = resp.read()
            content_type = resp.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return json.loads(raw.decode("utf-8"))
            return {"status": resp.status, "body": raw.decode("utf-8")}
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"message": raw}
        payload["_http_status"] = exc.code
        raise SystemExit(
            f"Box API error {exc.code}:\n{json.dumps(payload, indent=2, sort_keys=True)}"
        )


def dump_json(payload: Any) -> None:
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def encode_query(params: dict[str, Any]) -> str:
    filtered = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, list):
            filtered[key] = ",".join(str(item) for item in value)
        else:
            filtered[key] = value
    return parse.urlencode(filtered)


def get_token(cli_token: str | None) -> str:
    token = cli_token or os.environ.get("BOX_ACCESS_TOKEN")
    if not token:
        raise SystemExit(
            "Missing Box token. Set BOX_ACCESS_TOKEN or pass --token."
        )
    return token


def parse_bool(value: str) -> bool:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise argparse.ArgumentTypeError("Expected true or false.")


def handle_get_item(args: argparse.Namespace) -> None:
    query = encode_query({"fields": args.fields})
    url = f"{args.base_url}/{args.item_type}s/{args.item_id}"
    if query:
        url = f"{url}?{query}"
    dump_json(api_request("GET", url, args.token))


def handle_get_folder_items(args: argparse.Namespace) -> None:
    query = encode_query(
        {
            "limit": args.limit,
            "offset": args.offset,
            "fields": args.fields,
        }
    )
    url = f"{args.base_url}/folders/{args.folder_id}/items"
    if query:
        url = f"{url}?{query}"
    dump_json(api_request("GET", url, args.token))


def handle_search(args: argparse.Namespace) -> None:
    query = encode_query(
        {
            "query": args.query,
            "limit": args.limit,
            "offset": args.offset,
            "type": args.type,
            "fields": args.fields,
            "ancestor_folder_ids": args.ancestor_folder_ids,
            "content_types": args.content_types,
        }
    )
    url = f"{args.base_url}/search?{query}"
    dump_json(api_request("GET", url, args.token))


def json_body(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload).encode("utf-8")


def handle_create_folder(args: argparse.Namespace) -> None:
    payload = {
        "name": args.name,
        "parent": {"id": args.parent_folder_id},
    }
    query = encode_query({"fields": args.fields})
    url = f"{args.base_url}/folders"
    if query:
        url = f"{url}?{query}"
    dump_json(
        api_request(
            "POST",
            url,
            args.token,
            body=json_body(payload),
            headers={"Content-Type": "application/json"},
        )
    )


def _sanitize_filename(name: str) -> str:
    """Escape characters that would break a Content-Disposition header value."""
    return name.replace("\\", "\\\\").replace('"', '\\"').replace("\r", "").replace("\n", "")


def multipart_upload(file_path: Path, attributes: dict[str, Any]) -> tuple[bytes, str]:
    boundary = f"codex-box-{uuid.uuid4().hex}"
    mime_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    safe_name = _sanitize_filename(file_path.name)
    metadata_part = json.dumps(attributes).encode("utf-8")
    file_bytes = file_path.read_bytes()
    chunks = [
        f"--{boundary}\r\n".encode("utf-8"),
        b'Content-Disposition: form-data; name="attributes"\r\n',
        b"Content-Type: application/json\r\n\r\n",
        metadata_part,
        b"\r\n",
        f"--{boundary}\r\n".encode("utf-8"),
        f'Content-Disposition: form-data; name="file"; filename="{safe_name}"\r\n'.encode(
            "utf-8"
        ),
        f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8"),
        file_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode("utf-8"),
    ]
    return b"".join(chunks), boundary


def handle_upload_file(args: argparse.Namespace) -> None:
    file_path = Path(args.file).expanduser().resolve()
    if not file_path.exists():
        raise SystemExit(f"File not found: {file_path}")
    attributes = {
        "name": args.name or file_path.name,
        "parent": {"id": args.folder_id},
    }
    body, boundary = multipart_upload(file_path, attributes)
    query = encode_query({"fields": args.fields})
    url = f"{args.upload_base_url}/files/content"
    if query:
        url = f"{url}?{query}"
    dump_json(
        api_request(
            "POST",
            url,
            args.token,
            body=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
    )


def handle_move_item(args: argparse.Namespace) -> None:
    payload = {"parent": {"id": args.parent_folder_id}}
    query = encode_query({"fields": args.fields})
    url = f"{args.base_url}/{args.item_type}s/{args.item_id}"
    if query:
        url = f"{url}?{query}"
    dump_json(
        api_request(
            "PUT",
            url,
            args.token,
            body=json_body(payload),
            headers={"Content-Type": "application/json"},
        )
    )


def handle_create_shared_link(args: argparse.Namespace) -> None:
    shared_link: dict[str, Any] = {}
    if args.access:
        shared_link["access"] = args.access
    if args.allow_download is not None:
        shared_link["permissions"] = {"can_download": args.allow_download}
    if args.unshared_at:
        shared_link["unshared_at"] = args.unshared_at
    payload = {"shared_link": shared_link}
    dump_json(
        api_request(
            "PUT",
            f"{args.base_url}/{args.item_type}s/{args.item_id}",
            args.token,
            body=json_body(payload),
            headers={"Content-Type": "application/json"},
        )
    )


def add_common_auth_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--token",
        help="Box access token. Defaults to BOX_ACCESS_TOKEN.",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("BOX_API_BASE_URL", DEFAULT_API_BASE),
        help=f"Box API base URL. Defaults to {DEFAULT_API_BASE}.",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Minimal Box REST smoke-test helper."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    get_item = subparsers.add_parser(
        "get-item", help="Fetch a Box file or folder."
    )
    add_common_auth_args(get_item)
    get_item.add_argument("--item-type", required=True, choices=["file", "folder"])
    get_item.add_argument("--item-id", required=True)
    get_item.add_argument(
        "--fields",
        nargs="*",
        help="Optional list of Box fields to request.",
    )
    get_item.set_defaults(handler=handle_get_item)

    get_folder_items = subparsers.add_parser(
        "get-folder-items", help="List items in a Box folder."
    )
    add_common_auth_args(get_folder_items)
    get_folder_items.add_argument("--folder-id", required=True)
    get_folder_items.add_argument("--limit", type=int, default=20)
    get_folder_items.add_argument("--offset", type=int, default=0)
    get_folder_items.add_argument(
        "--fields",
        nargs="*",
        help="Optional list of Box fields to request.",
    )
    get_folder_items.set_defaults(handler=handle_get_folder_items)

    search = subparsers.add_parser("search", help="Search Box content.")
    add_common_auth_args(search)
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--offset", type=int, default=0)
    search.add_argument("--type", choices=["file", "folder", "web_link"])
    search.add_argument("--ancestor-folder-ids", nargs="*")
    search.add_argument("--content-types", nargs="*")
    search.add_argument("--fields", nargs="*")
    search.set_defaults(handler=handle_search)

    create_folder = subparsers.add_parser(
        "create-folder", help="Create a Box folder."
    )
    add_common_auth_args(create_folder)
    create_folder.add_argument("--parent-folder-id", required=True)
    create_folder.add_argument("--name", required=True)
    create_folder.add_argument("--fields", nargs="*")
    create_folder.set_defaults(handler=handle_create_folder)

    upload_file = subparsers.add_parser("upload-file", help="Upload a file to Box.")
    add_common_auth_args(upload_file)
    upload_file.add_argument(
        "--upload-base-url",
        default=os.environ.get("BOX_UPLOAD_BASE_URL", DEFAULT_UPLOAD_BASE),
        help=f"Box upload base URL. Defaults to {DEFAULT_UPLOAD_BASE}.",
    )
    upload_file.add_argument("--folder-id", required=True)
    upload_file.add_argument("--file", required=True)
    upload_file.add_argument("--name")
    upload_file.add_argument("--fields", nargs="*")
    upload_file.set_defaults(handler=handle_upload_file)

    move_item = subparsers.add_parser(
        "move-item", help="Move a file or folder to a different parent folder."
    )
    add_common_auth_args(move_item)
    move_item.add_argument("--item-type", required=True, choices=["file", "folder"])
    move_item.add_argument("--item-id", required=True)
    move_item.add_argument("--parent-folder-id", required=True)
    move_item.add_argument("--fields", nargs="*")
    move_item.set_defaults(handler=handle_move_item)

    create_shared_link = subparsers.add_parser(
        "create-shared-link", help="Create or update a shared link."
    )
    add_common_auth_args(create_shared_link)
    create_shared_link.add_argument(
        "--item-type", required=True, choices=["file", "folder"]
    )
    create_shared_link.add_argument("--item-id", required=True)
    create_shared_link.add_argument(
        "--access", choices=["open", "company", "collaborators"]
    )
    create_shared_link.add_argument(
        "--allow-download",
        type=parse_bool,
        default=None,
        metavar="{true,false}",
        help="Set to true or false.",
    )
    create_shared_link.add_argument(
        "--unshared-at",
        help="Optional ISO-8601 expiration timestamp.",
    )
    create_shared_link.set_defaults(handler=handle_create_shared_link)

    args = parser.parse_args()
    args.token = get_token(args.token)
    args.handler(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
