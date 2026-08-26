#!/usr/bin/env python3
"""Minimal Box CLI smoke-test helper."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def ensure_box_cli() -> str:
    box = shutil.which("box")
    if not box:
        raise SystemExit(
            "Box CLI is not installed. Install it or fall back to scripts/box_rest.py."
        )
    return box


def common_box_args(args: argparse.Namespace) -> list[str]:
    command = ["--json", "--no-color"]
    if args.token:
        command.extend(["-t", args.token])
    if args.as_user:
        command.extend(["--as-user", args.as_user])
    return command


def run_box(subcommand: list[str]) -> int:
    box = ensure_box_cli()
    process = subprocess.run([box, *subcommand], text=True)
    return process.returncode


def handle_check_auth(args: argparse.Namespace) -> int:
    return run_box(["users:get", "me", *common_box_args(args)])


def handle_get_folder(args: argparse.Namespace) -> int:
    command = ["folders:get", args.folder_id, *common_box_args(args)]
    if args.fields:
        command.extend(["--fields", ",".join(args.fields)])
    return run_box(command)


def handle_list_folder_items(args: argparse.Namespace) -> int:
    command = [
        "folders:items",
        args.folder_id,
        *common_box_args(args),
        "--max-items",
        str(args.max_items),
    ]
    if args.fields:
        command.extend(["--fields", ",".join(args.fields)])
    return run_box(command)


def handle_search(args: argparse.Namespace) -> int:
    command = ["search", args.query, *common_box_args(args), "--limit", str(args.limit)]
    if args.item_type:
        command.extend(["--type", args.item_type])
    if args.fields:
        command.extend(["--fields", ",".join(args.fields)])
    if args.ancestor_folder_ids:
        command.extend(["--ancestor-folder-ids", ",".join(args.ancestor_folder_ids)])
    if args.content_types:
        command.extend(["--content-types", ",".join(args.content_types)])
    return run_box(command)


def handle_create_folder(args: argparse.Namespace) -> int:
    command = ["folders:create", args.parent_id, args.name, *common_box_args(args)]
    if args.fields:
        command.extend(["--fields", ",".join(args.fields)])
    return run_box(command)


def handle_upload_file(args: argparse.Namespace) -> int:
    file_path = Path(args.path).expanduser().resolve()
    if not file_path.exists():
        raise SystemExit(f"File not found: {file_path}")
    command = [
        "files:upload",
        str(file_path),
        *common_box_args(args),
        "--parent-id",
        args.parent_id,
    ]
    if args.name:
        command.extend(["--name", args.name])
    if args.overwrite:
        command.append("--overwrite")
    if args.fields:
        command.extend(["--fields", ",".join(args.fields)])
    return run_box(command)


def handle_move_item(args: argparse.Namespace) -> int:
    command = [
        f"{args.item_type}s:move",
        args.item_id,
        args.parent_id,
        *common_box_args(args),
    ]
    if args.fields:
        command.extend(["--fields", ",".join(args.fields)])
    return run_box(command)


def handle_create_shared_link(args: argparse.Namespace) -> int:
    command = [
        "shared-links:create",
        args.item_id,
        args.item_type,
        *common_box_args(args),
    ]
    if args.access:
        command.extend(["--access", args.access])
    if args.can_download is not None:
        command.append("--can-download" if args.can_download else "--no-can-download")
    if args.unshared_at:
        command.extend(["--unshared-at", args.unshared_at])
    if args.fields:
        command.extend(["--fields", ",".join(args.fields)])
    return run_box(command)


def parse_bool(value: str) -> bool:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise argparse.ArgumentTypeError("Expected true or false.")


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--token",
        help="Optional Box token to pass directly to the CLI.",
    )
    parser.add_argument(
        "--as-user",
        help="Optional user ID for Box CLI --as-user impersonation.",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal Box CLI smoke-test helper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_auth = subparsers.add_parser(
        "check-auth",
        help="Verify that Box CLI is installed and can access the current actor.",
    )
    add_common_args(check_auth)
    check_auth.set_defaults(handler=handle_check_auth)

    get_folder = subparsers.add_parser("get-folder", help="Fetch a Box folder.")
    add_common_args(get_folder)
    get_folder.add_argument("folder_id")
    get_folder.add_argument("--fields", nargs="*")
    get_folder.set_defaults(handler=handle_get_folder)

    list_folder_items = subparsers.add_parser(
        "list-folder-items", help="List items in a Box folder."
    )
    add_common_args(list_folder_items)
    list_folder_items.add_argument("folder_id")
    list_folder_items.add_argument("--max-items", type=int, default=20)
    list_folder_items.add_argument("--fields", nargs="*")
    list_folder_items.set_defaults(handler=handle_list_folder_items)

    search = subparsers.add_parser("search", help="Search Box content.")
    add_common_args(search)
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--type", dest="item_type", choices=["file", "folder", "web_link"])
    search.add_argument("--ancestor-folder-ids", nargs="*")
    search.add_argument("--content-types", nargs="*")
    search.add_argument("--fields", nargs="*")
    search.set_defaults(handler=handle_search)

    create_folder = subparsers.add_parser("create-folder", help="Create a Box folder.")
    add_common_args(create_folder)
    create_folder.add_argument("parent_id")
    create_folder.add_argument("name")
    create_folder.add_argument("--fields", nargs="*")
    create_folder.set_defaults(handler=handle_create_folder)

    upload_file = subparsers.add_parser("upload-file", help="Upload a file to Box.")
    add_common_args(upload_file)
    upload_file.add_argument("path")
    upload_file.add_argument("--parent-id", default="0")
    upload_file.add_argument("--name")
    upload_file.add_argument("--overwrite", action="store_true")
    upload_file.add_argument("--fields", nargs="*")
    upload_file.set_defaults(handler=handle_upload_file)

    move_item = subparsers.add_parser(
        "move-item", help="Move a file or folder to a different parent folder."
    )
    add_common_args(move_item)
    move_item.add_argument("item_id")
    move_item.add_argument("item_type", choices=["file", "folder"])
    move_item.add_argument("--parent-id", required=True)
    move_item.add_argument("--fields", nargs="*")
    move_item.set_defaults(handler=handle_move_item)

    create_shared_link = subparsers.add_parser(
        "create-shared-link", help="Create or update a shared link with Box CLI."
    )
    add_common_args(create_shared_link)
    create_shared_link.add_argument("item_id")
    create_shared_link.add_argument("item_type", choices=["file", "folder"])
    create_shared_link.add_argument("--access")
    create_shared_link.add_argument("--can-download", type=parse_bool)
    create_shared_link.add_argument("--unshared-at")
    create_shared_link.add_argument("--fields", nargs="*")
    create_shared_link.set_defaults(handler=handle_create_shared_link)

    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
