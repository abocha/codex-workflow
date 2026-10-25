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


def navigate(path, start, end, preview_chars, expected_sha=None):
    """Bounded record index, including authority and tool records, never hidden reasoning."""
    before = path.stat()
    digest, rows, total = hashlib.sha256(), [], 0
    for number, event, raw in records(path):
        digest.update(raw)
        total = number
        if not start <= number <= end:
            continue
        if event is None:
            rows.append({"line": number, "type": "malformed"})
            continue
        payload = event.get("payload", {})
        event_type, kind = event.get("type"), payload.get("type", "")
        if kind == "reasoning" or (event_type == "event_msg" and kind.startswith("agent_reasoning")):
            continue
        if event_type == "response_item":
            if kind == "message":
                text = "\n".join(str(part.get("text", "")) for part in payload.get("content", [])
                                 if isinstance(part, dict))
            elif kind == "additional_tools":
                text = "[tool definitions; available in raw source]"
            else:
                text = str(payload.get("arguments", payload.get("input", payload.get("output", ""))))
        elif event_type == "event_msg":
            if kind not in {"user_message", "agent_message", "task_started", "task_complete",
                            "turn_aborted", "task_aborted", "error", "warning"}:
                continue
            text = str(payload.get("message", ""))
        elif event_type == "session_meta":
            text = str(payload.get("base_instructions", "[session metadata]"))
        elif event_type in {"turn_context", "compacted"}:
            text = json.dumps(payload, ensure_ascii=False)
        else:
            continue
        compact = " ".join(text.split())
        rows.append({"line": number, "timestamp": event.get("timestamp"), "type": event_type,
                     "kind": kind, "role": payload.get("role"), "name": payload.get("name"),
                     "call_id": payload.get("call_id"), "turn_id": payload.get("turn_id"),
                     "characters": len(text), "preview": compact[:preview_chars],
                     "preview_truncated": len(compact) > preview_chars})
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError("Source changed during navigation")
    if expected_sha and digest.hexdigest() != expected_sha:
        raise ValueError("Source hash changed; re-stage evidence")
    return {"source": str(path.resolve()), "sha256": digest.hexdigest(), "line_count": total,
            "physical_lines": [start, end], "next_line": end + 1 if end < total else None,
            "note": "Navigation only; previews are not detailed reading. Authority, tools and compactions remain indexed. Read exact lines with --include-context for evidence. No automatic redaction.",
            "records": rows}


def check_report(packet, report):
    """Check references and declared reading coverage, not semantic support for conclusions."""
    files = packet["files"]
    by_path = {str(Path(row["path"]).resolve()): row for row in files}
    errors, coverage, claim_ids = [], {}, set()

    def resolve(ref):
        key = str(Path(ref.get("file", "")).resolve())
        if key not in by_path:
            errors.append(f"Unknown packet file: {ref.get('file')}")
            return None
        return key

    def ranges(value, key, label):
        valid = []
        if not isinstance(value, list):
            errors.append(f"{label}: expected a list of ranges")
            return valid
        for pair in value:
            if (not isinstance(pair, list) or len(pair) != 2 or
                    any(type(n) is not int for n in pair) or
                    not 1 <= pair[0] <= pair[1] <= by_path[key]["line_count"]):
                errors.append(f"{label}: invalid physical line range {pair}")
            else:
                valid.append(pair)
        return valid

    actual_totals = {"files": len(files), "physical_lines": sum(row["line_count"] for row in files)}
    if report.get("totals") != actual_totals:
        errors.append(f"Incorrect packet totals; expected {actual_totals}")
    # Pin both file identity and actual physical bounds, not only the report's assertions.
    for key, row in by_path.items():
        try:
            digest, count = hashlib.sha256(), 0
            with Path(key).open("rb") as stream:
                for raw in stream:
                    digest.update(raw)
                    count += 1
            if digest.hexdigest() != row["sha256"] or count != row["line_count"]:
                errors.append(f"Packet source changed: {key}")
        except OSError:
            errors.append(f"Packet source unavailable: {key}")
    for item in report.get("coverage", []):
        key = resolve(item)
        if key is None:
            continue
        if key in coverage:
            errors.append(f"Duplicate coverage entry: {key}")
        coverage[key] = ranges(item.get("read_ranges"), key, "read_ranges")
        ranges(item.get("scan_ranges"), key, "scan_ranges")
        if not isinstance(item.get("gaps"), str) or not item["gaps"].strip():
            errors.append(f"Coverage must state gaps or explicitly 'none': {key}")
    for key in by_path.keys() - coverage.keys():
        errors.append(f"Missing coverage entry: {key}")

    def was_read(key, pair):
        cursor = pair[0]
        for low, high in sorted(coverage.get(key, [])):
            if low > cursor:
                break
            cursor = max(cursor, high + 1)
        return cursor > pair[1]

    for claim in report.get("claims", []):
        ident = claim.get("id")
        if not isinstance(ident, str) or not ident.strip() or ident in claim_ids:
            errors.append("Each claim needs a unique nonempty id")
        claim_ids.add(str(ident))
        if claim.get("basis") not in {"observed_sequence", "historical_report", "inference"}:
            errors.append(f"{ident}: unknown evidence basis")
        if not isinstance(claim.get("limits"), str) or not claim["limits"].strip():
            errors.append(f"{ident}: state evidence limits or explicitly 'none'")
        refs = claim.get("references", [])
        if not refs:
            errors.append(f"{ident}: missing evidence references")
        for ref in refs:
            key = resolve(ref)
            if key is None:
                continue
            if ref.get("sha256") != by_path[key]["sha256"]:
                errors.append(f"{ident}: wrong or missing source hash for {key}")
            for pair in ranges([ref.get("lines")], key, str(ident)):
                if not was_read(key, pair):
                    errors.append(f"{ident}: cited range was scanned only or not declared read: {pair}")
    return {"ok": not errors, "totals": actual_totals, "errors": errors,
            "note": "Structural checks only. Declared reading is self-reported; a human/primary reviewer must check that the cited sequence supports the claim, including tool results for observed outcomes."}


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
    # Redirected Windows stdout may otherwise use a legacy encoding and fail on real transcripts.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
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
    nav = sub.add_parser("navigate", help="Compact record index; includes authority and tool references")
    nav.add_argument("--path", type=Path, required=True)
    nav.add_argument("--start-line", type=int, default=1)
    nav.add_argument("--end-line", type=int, default=100)
    nav.add_argument("--preview-chars", type=int, default=180)
    nav.add_argument("--sha256")
    check = sub.add_parser("check-report", help="Check packet totals, citation bounds/hashes and declared coverage")
    check.add_argument("--packet", type=Path, required=True)
    check.add_argument("--report", type=Path, required=True)
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
    elif args.command == "navigate":
        if args.start_line < 1 or args.end_line < args.start_line or args.preview_chars < 1:
            parser.error("Invalid navigation range or preview length")
        print(json.dumps(navigate(args.path, args.start_line, args.end_line,
                                  args.preview_chars, args.sha256), ensure_ascii=False))
    elif args.command == "check-report":
        result = check_report(json.loads(args.packet.read_text(encoding="utf-8")),
                              json.loads(args.report.read_text(encoding="utf-8")))
        print(json.dumps(result, ensure_ascii=False))
        if not result["ok"]:
            sys.exit(1)
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
