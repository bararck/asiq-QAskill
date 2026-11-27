"""Negative controls for evidence binding; all sessions here are synthetic fixtures."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import evaluate_behavior as evaluator


class EvidenceBindingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.pack = {"version": 1, "cases": [{"id": "BE-X", "prompt": "Synthetic case",
                     "expected": "Preserve failed attempt", "small_task": True}]}
        self.pack_bytes = json.dumps(self.pack).encode()
        skill_hash = self.write("skill.md", b"Synthetic skill snapshot")
        artifact_hash = self.write("events/case.jsonl", b'{"type":"synthetic.fixture"}\n')
        self.events = {"version": 1, "events": [{"id": "event-x", "case_id": "BE-X",
                       "session_id": "synthetic-session-x", "model": "fixture-model",
                       "skill_sha256": skill_hash,
                       "artifact": {"path": "events/case.jsonl", "sha256": artifact_hash}}]}
        events_hash = self.write("events.json", json.dumps(self.events).encode())
        self.review = {"version": 2, "session_id": "synthetic-run", "model": "fixture-model",
                       "skill_revision": "fixture-revision", "reviewer": "fixture-reviewer",
                       "pack_sha256": hashlib.sha256(self.pack_bytes).hexdigest(),
                       "skill_file": "skill.md", "skill_sha256": skill_hash,
                       "events_file": "events.json", "events_sha256": events_hash,
                       "records": [{"case_id": "BE-X", "session_id": "synthetic-session-x",
                                    "event_ids": ["event-x"], "verdict_correct": True,
                                    "evidence_complete": True, "scope_respected": True,
                                    "independent_work_continued": True,
                                    "redundant_questions": 0, "duration_seconds": 1}]}

    def write(self, relative, content):
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return hashlib.sha256(content).hexdigest()

    def summarize(self):
        return evaluator.summarize(self.pack, self.review, evidence_root=self.root, pack_bytes=self.pack_bytes)

    def save_events(self):
        self.review["events_sha256"] = self.write("events.json", json.dumps(self.events).encode())

    def test_valid_binding_is_explicit_without_certifying_reviewer_truth(self):
        result = self.summarize()
        self.assertTrue(result["evidence_binding_verified"])
        self.assertFalse(result["reviewer_judgment_verified"])

    def test_v2_cannot_score_without_evidence_root(self):
        with self.assertRaises(ValueError):
            evaluator.summarize(self.pack, self.review)

    def test_changed_artifact_and_missing_file_are_rejected(self):
        self.write("events/case.jsonl", b"changed")
        with self.assertRaises(ValueError):
            self.summarize()
        (self.root / "events/case.jsonl").unlink()
        with self.assertRaises(ValueError):
            self.summarize()

    def test_pack_snapshot_and_manifest_tamper_are_rejected(self):
        for field in ("pack_sha256", "skill_sha256", "events_sha256"):
            original = self.review[field]
            self.review[field] = "0" * 64
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.summarize()
            self.review[field] = original

    def test_fabricated_and_repeated_event_references_are_rejected(self):
        for ids in (["made-up-event"], ["event-x", "event-x"]):
            self.review["records"][0]["event_ids"] = ids
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                self.summarize()

    def test_event_context_cannot_be_reused_from_another_case_model_or_session(self):
        for field in ("case_id", "session_id", "model", "skill_sha256"):
            original = self.events["events"][0][field]
            self.events["events"][0][field] = "other-context"
            self.save_events()
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.summarize()
            self.events["events"][0][field] = original

    def test_traversal_and_platform_specific_absolute_paths_are_rejected(self):
        for path in ("../escape", "/outside", "C:/outside", "events\\case.jsonl"):
            self.events["events"][0]["artifact"]["path"] = path
            self.save_events()
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.summarize()

    def test_duplicate_manifest_event_ids_are_rejected(self):
        self.events["events"].append(copy.deepcopy(self.events["events"][0]))
        self.save_events()
        with self.assertRaises(ValueError):
            self.summarize()

    def test_empty_artifact_is_not_execution_evidence(self):
        self.events["events"][0]["artifact"]["sha256"] = self.write("events/case.jsonl", b"")
        self.save_events()
        with self.assertRaises(ValueError):
            self.summarize()


if __name__ == "__main__":
    unittest.main()
