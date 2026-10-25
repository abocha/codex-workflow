"""Focused synthetic contract checks for the local research reader; no live logs or services."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
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

    def test_navigation_retains_authority_and_tools_with_exact_line_links(self):
        path = self.log()
        page = lab.navigate(path, 1, 5, 20)
        rows = {row["line"]: row for row in page["records"]}
        self.assertIn(1, rows)  # Session instructions are discoverable, even when very large.
        self.assertEqual(rows[5]["call_id"], "c1")
        self.assertEqual(rows[5]["characters"], 300)
        self.assertTrue(rows[5]["preview_truncated"])
        self.assertEqual(page["next_line"], 6)
        later = lab.navigate(path, 6, 9, 20)
        self.assertNotIn(6, {row["line"] for row in later["records"]})
        self.assertEqual(later["records"][0]["role"], "developer")
        with self.assertRaisesRegex(ValueError, "hash changed"):
            lab.navigate(path, 1, 5, 20, "0" * 64)

    def test_cli_unicode_survives_legacy_redirected_encoding(self):
        path = self.root / "unicode.jsonl"
        text = "Привет 🧭"
        path.write_text(json.dumps({"type": "response_item", "payload": {"type": "message", "role": "user",
                        "content": [{"type": "input_text", "text": text}]}}, ensure_ascii=False), encoding="utf-8")
        env = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONUTF8="0")
        for command, flags in [("navigate", []), ("read", ["--end-line", "1"])]:
            result = subprocess.run([sys.executable, str(Path(lab.__file__)), command, "--path", str(path), *flags],
                                    env=env, capture_output=True, check=True)
            output = result.stdout.decode("utf-8")
            self.assertIn(text, output)

    def evidence(self):
        path = self.log()
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        packet = {"files": [{"path": str(path), "sha256": sha, "line_count": 9}]}
        report = {"totals": {"files": 1, "physical_lines": 9}, "coverage": [
            {"file": str(path), "scan_ranges": [[1, 9]], "read_ranges": [[4, 5]], "gaps": "Other payloads scanned only"}],
            "claims": [{"id": "C1", "basis": "observed_sequence", "limits": "Synthetic example", "references": [
                {"file": str(path), "sha256": sha, "lines": [4, 5]}]}]}
        return path, packet, report

    def test_report_rejects_wrong_file_range_total_and_scanned_only_support(self):
        _, packet, report = self.evidence()
        self.assertTrue(lab.check_report(packet, report)["ok"])
        report["totals"]["physical_lines"] = 10
        report["claims"][0]["references"][0]["lines"] = [8, 12]
        errors = lab.check_report(packet, report)["errors"]
        self.assertTrue(any("totals" in err for err in errors))
        self.assertTrue(any("invalid physical" in err for err in errors))
        packet_path, report_path = self.root / "packet.json", self.root / "report.json"
        packet_path.write_text(json.dumps(packet), encoding="utf-8")
        report_path.write_text(json.dumps(report), encoding="utf-8")
        cli = subprocess.run([sys.executable, str(Path(lab.__file__)), "check-report", "--packet", str(packet_path),
                              "--report", str(report_path)], capture_output=True)
        self.assertEqual(cli.returncode, 1)
        self.assertFalse(json.loads(cli.stdout.decode("utf-8"))["ok"])
        report["claims"][0]["references"][0]["lines"] = [6, 7]
        self.assertTrue(any("scanned only" in err for err in lab.check_report(packet, report)["errors"]))
        report["claims"][0]["references"][0]["file"] = str(self.root / "different.jsonl")
        self.assertTrue(any("Unknown packet file" in err for err in lab.check_report(packet, report)["errors"]))

    def test_report_rejects_changed_source_wrong_hash_and_missing_coverage(self):
        path, packet, report = self.evidence()
        report["claims"][0]["references"][0]["sha256"] = "0" * 64
        report["coverage"] = []
        with path.open("a", encoding="utf-8") as stream:
            stream.write("\n{}")
        errors = lab.check_report(packet, report)["errors"]
        for expected in ["source changed", "Missing coverage", "wrong or missing source hash"]:
            self.assertTrue(any(expected in err for err in errors), errors)


if __name__ == "__main__":
    unittest.main()
