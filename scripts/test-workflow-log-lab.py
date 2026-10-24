"""Focused synthetic contract checks for the local research reader; no live logs or services."""

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("lab", Path(__file__).with_name("workflow-log-lab.py"))
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class LogLabTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def log(self, name="sample.jsonl", session="root", parent=None):
        path = self.root / name
        meta = {"id": session, "timestamp": "2026-10-21T00:00:00Z", "cwd": "synthetic"}
        if parent:
            meta["source"] = {"subagent": {"thread_spawn": {"parent_thread_id": parent}}}
        rows = [
            {"type": "session_meta", "payload": meta},
            {"type": "event_msg", "payload": {"type": "task_started", "turn_id": "t1"}},
            {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [
                {"type": "input_text", "text": "# AGENTS.md instructions for synthetic"}]}},
            {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [
                {"type": "input_text", "text": "Please inspect the tool error."}]}},
            {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "c1", "output": "x" * 300}},
            {"type": "response_item", "payload": {"type": "reasoning", "text": "not-observable-evidence"}},
            {"type": "response_item", "payload": {"type": "message", "role": "developer", "content": [
                {"type": "input_text", "text": "synthetic-context-rule"}]}},
            {"type": "event_msg", "payload": {"type": "turn_aborted"}},
        ]
        path.write_text("\n".join(json.dumps(row) for row in rows) + "\n{broken", encoding="utf-8")
        return path

    def test_modern_requests_lineage_and_malformed_evidence(self):
        path = self.log(parent="parent")
        row = lab.inspect(path, lab.metadata(path))
        self.assertEqual(row["parent_id"], "parent")
        self.assertEqual(row["malformed_lines"], [9])
        self.assertEqual(row["line_count"], 9)
        self.assertTrue(row["user_messages"][0]["bootstrap_hint"])
        self.assertEqual(row["user_messages"][1]["line"], 4)
        self.assertEqual(row["last_lifecycle_event"], "turn_aborted")
        self.assertEqual(row["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_pages_reassemble_and_context_is_explicit(self):
        path = self.log()
        whole = lab.read_page(path, 1, 9, 0, 100000)
        offset, parts = 0, []
        while True:
            page = lab.read_page(path, 1, 9, offset, 71)
            parts.append(page["text"])
            if page["next_offset"] is None:
                break
            offset = page["next_offset"]
        self.assertEqual("".join(parts), whole["text"])
        self.assertIn("physical line 5", whole["text"])
        self.assertIn("MALFORMED JSON", whole["text"])
        self.assertNotIn("not-observable-evidence", whole["text"])
        self.assertNotIn("synthetic-context-rule", whole["text"])
        contextual = lab.read_page(path, 1, 9, 0, 100000, include_context=True)
        self.assertIn("synthetic-context-rule", contextual["text"])

    def test_duplicate_session_files_and_outside_parents_are_visible(self):
        self.log("one.jsonl")
        self.log("two.jsonl")
        self.log("child.jsonl", "child", "outside")
        (self.root / "old.jsonl.zst").write_bytes(b"synthetic-not-decoded")
        result = lab.inventory([self.root, self.root], lab.timestamp("2026-10-20T00:00:00Z"),
                               lab.timestamp("2026-10-22T00:00:00Z"))
        self.assertEqual(len(result["sessions"]), 3)
        self.assertEqual(result["multiple_files_per_session"], {"root": 2})
        self.assertEqual(result["parents_outside_window"], ["outside"])

    def test_legacy_message_fallback_and_changed_hash(self):
        path = self.root / "legacy.jsonl"
        path.write_text(json.dumps({"type": "session_meta", "payload": {"meta": {"id": "legacy"}}}) + "\n" +
                        json.dumps({"type": "event_msg", "payload": {"type": "user_message", "message": "legacy request"}}),
                        encoding="utf-8")
        row = lab.inspect(path, lab.metadata(path))
        self.assertEqual(row["user_messages"][0]["preview"], "legacy request")
        with self.assertRaisesRegex(ValueError, "hash changed"):
            lab.read_page(path, 1, 2, 0, 100, expected_sha="0" * 64)

    def test_output_boundary_and_timezone(self):
        with self.assertRaisesRegex(ValueError, "ignored"):
            lab.write_private(self.root / "public.json", {})
        with self.assertRaisesRegex(ValueError, "explicit UTC offset"):
            lab.timestamp("2026-10-20T00:00:00")


if __name__ == "__main__":
    unittest.main()
