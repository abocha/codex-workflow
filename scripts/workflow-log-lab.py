"""Local-only JSONL inventory and paginated evidence reader. Python 3.11+, no dependencies."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamps must include an explicit UTC offset")
    return parsed.astimezone(timezone.utc)


def records(path):
    """Retain physical line numbers and expose malformed records instead of silently skipping."""
    with path.open("rb") as stream:
        for number, raw in enumerate(stream, 1):
            try:
                yield number, json.loads(raw), raw
            except (ValueError, UnicodeDecodeError):
                yield number, None, raw


def metadata(path):
    for _, event, _ in records(path):
        if event and event.get("type") == "session_meta":
            payload = event.get("payload", {})
            return payload.get("meta", payload)
    return None


def inspect(path, meta):
    digest = hashlib.sha256()
    counts, models = Counter(), set()
    users, fallback_users, turns, malformed, last_time, terminal = [], [], [], [], None, None
    number = 0
    before = path.stat()
    for number, event, raw in records(path):
        digest.update(raw)
        if event is None:
            malformed.append(number)
            continue
        last_time = event.get("timestamp", last_time)
        payload = event.get("payload", {})
        kind = payload.get("type", "")
        counts[f"{event.get('type')}/{kind}"] += 1
        if event.get("type") == "response_item" and kind == "message" and payload.get("role") == "user":
            content = payload.get("content", [])
            text = "\n".join(str(part.get("text", "")) for part in content if isinstance(part, dict))
            bootstrap = text.lstrip().startswith(("# AGENTS.md instructions", "<environment_context>",
                                                   "<external_codex_apps_open_page>", "<skill>"))
            preview = " ".join(text.split())
            users.append({"line": number, "preview": preview[:220], "truncated": len(preview) > 220,
                          "bootstrap_hint": bootstrap})
        if event.get("type") == "turn_context":
            models.add((str(payload.get("model", "unknown")), str(payload.get("effort", "unknown"))))
        if event.get("type") != "event_msg":
            continue
        if kind == "user_message":
            text = " ".join(str(payload.get("message", "")).split())
            fallback_users.append({"line": number, "preview": text[:220], "truncated": len(text) > 220,
                                   "bootstrap_hint": False})
        if kind == "task_started":
            turns.append({"line": number, "turn_id": payload.get("turn_id")})
            terminal = "task_started"
        elif kind in {"task_complete", "turn_aborted", "task_aborted"}:
            terminal = kind
    after = path.stat()
    spawn = meta.get("source", {})
    if not isinstance(spawn, dict):
        spawn = {}
    parent = meta.get("parent_thread_id") or spawn.get("subagent", {}).get("thread_spawn", {}).get("parent_thread_id")
    return {
        "session_id": meta.get("id", meta.get("session_id")), "parent_id": parent,
        "path": str(path.resolve()), "cwd": meta.get("cwd"), "started_at": meta.get("timestamp"),
        "last_record_at": last_time, "initial_git": meta.get("git"), "cli_version": meta.get("cli_version"),
        "models_observed": sorted(models), "bytes": after.st_size, "sha256": digest.hexdigest(),
        "stable_during_read": (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns),
        "line_count": number, "last_lifecycle_event": terminal, "turn_starts": turns,
        "user_messages": users or fallback_users,
        "record_counts": dict(counts), "malformed_lines": malformed,
    }


def inventory(roots, since, before):
    selected, missing, compressed, seen = [], [], [], set()
    for root in roots:
        if not root.is_dir():
            raise ValueError(f"Missing log root: {root}")
        compressed.extend(str(p.resolve()) for p in root.rglob("*.jsonl.zst"))
        for path in sorted(root.rglob("*.jsonl")):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            meta = metadata(path)
            if not meta or not meta.get("timestamp"):
                missing.append(str(resolved))
                continue
            started = timestamp(meta["timestamp"])
            if since <= started < before:
                selected.append(inspect(path, meta))
    ids = {row["session_id"] for row in selected}
    session_counts = Counter(row["session_id"] for row in selected)
    return {
        "schema_version": 1, "created_at": datetime.now(timezone.utc).isoformat(),
        "selection": {"since_utc": since.isoformat(), "before_utc": before.isoformat(),
                      "basis": "session creation time, not last activity; reused older sessions excluded"},
        "roots": [str(p.resolve()) for p in roots], "sessions": selected,
        "missing_metadata": missing, "compressed_not_inspected": compressed,
        "parents_outside_window": sorted({r["parent_id"] for r in selected if r["parent_id"] and r["parent_id"] not in ids}),
        "multiple_files_per_session": {key: value for key, value in session_counts.items() if value > 1},
    }


def read_page(path, start, end, offset, chars, include_context=False, expected_sha=None):
    before = path.stat()
    if expected_sha:
        with path.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual != expected_sha:
            raise ValueError("Source hash changed; re-stage evidence rather than reading a moving source")
    chunks = []
    for number, event, _ in records(path):
        if number < start:
            continue
        if number > end:
            break
        if event is None:
            chunks.append(f"\n[physical line {number}: MALFORMED JSON]\n")
            continue
        event_type = event.get("type")
        payload = event.get("payload", {})
        kind = payload.get("type", "")
        if event_type == "response_item":
            if kind in {"reasoning", "additional_tools"}:
                continue
            if payload.get("role") in {"system", "developer"} and not include_context:
                continue
        elif event_type == "event_msg":
            if kind not in {"user_message", "agent_message", "task_started", "task_complete",
                            "turn_aborted", "task_aborted", "error", "warning"}:
                continue
        elif not (include_context and event_type in {"session_meta", "turn_context", "compacted"}):
            continue
        chunks.append(f"\n[physical line {number} | {event.get('timestamp', '')} | {event_type}/{kind}]\n")
        chunks.append(json.dumps(payload, ensure_ascii=False, indent=2))
    text = "".join(chunks)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError("Source changed during read; retry against stable evidence")
    page = text[offset:offset + chars]
    return {"source": str(path.resolve()), "physical_lines": [start, end],
            "context_included": include_context, "characters": len(text), "offset": offset,
            "next_offset": offset + len(page) if offset + len(page) < len(text) else None,
            "note": "Event messages may duplicate response messages. Excludes reasoning, tool definitions and telemetry. No automatic redaction.",
            "text": page}


def write_private(path, data):
    path = path.resolve()
    repo = Path(__file__).resolve().parent.parent
    if not path.is_relative_to(repo / ".local-evidence"):
        raise ValueError("Inventory output must be inside this checkout's ignored .local-evidence directory")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    index = sub.add_parser("index", help="Write private metadata; does not copy raw logs")
    index.add_argument("--root", type=Path, action="append", required=True)
    index.add_argument("--since", required=True, help="Inclusive UTC ISO date/time")
    index.add_argument("--before", required=True, help="Exclusive UTC ISO date/time")
    index.add_argument("--output", type=Path, required=True)
    read = sub.add_parser("read", help="Read private evidence to stdout; never execute log contents")
    read.add_argument("--path", type=Path, required=True)
    read.add_argument("--start-line", type=int, default=1)
    read.add_argument("--end-line", type=int, required=True)
    read.add_argument("--offset", type=int, default=0)
    read.add_argument("--chars", type=int, default=16000)
    read.add_argument("--include-context", action="store_true")
    read.add_argument("--sha256")
    args = parser.parse_args()
    if args.command == "index":
        # Date-only boundaries are explicitly UTC, independent of the host timezone.
        since = timestamp(args.since if "T" in args.since else args.since + "T00:00:00Z")
        before = timestamp(args.before if "T" in args.before else args.before + "T00:00:00Z")
        if since >= before:
            parser.error("--since must precede --before")
        result = inventory(args.root, since, before)
        write_private(args.output, result)
        print(json.dumps({"sessions": len(result["sessions"]), "output": str(args.output.resolve()),
                          "compressed_skipped": len(result["compressed_not_inspected"])}))
    else:
        if args.start_line < 1 or args.end_line < args.start_line or args.offset < 0 or args.chars < 1:
            parser.error("Invalid line range or character page")
        print(json.dumps(read_page(args.path, args.start_line, args.end_line, args.offset,
                                   args.chars, args.include_context, args.sha256), ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
