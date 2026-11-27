"""Kontrak grader lokal; fixture sintetis bukan hasil evaluasi agen."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BehaviorEvaluationTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("behavior_eval", ROOT / "scripts/evaluate_behavior.py")
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.pack = json.loads((ROOT / "benchmarks/behavior-cases.json").read_text(encoding="utf-8"))
        self.review = {"version": 1, "session_id": "synthetic-unit-fixture", "model": "fixture",
                       "skill_revision": "fixture", "reviewer": "fixture-reviewer",
                       "records": [{"case_id": case["id"], "event_ids": ["event-1"],
                                    "verdict_correct": True, "evidence_complete": True,
                                    "scope_respected": True, "independent_work_continued": True,
                                    "redundant_questions": 0, "duration_seconds": 12}
                                   for case in self.pack["cases"]]}

    def test_complete_review_reports_dimensions_and_small_task_time(self):
        summary = self.module.summarize(self.pack, self.review)
        self.assertEqual(10, summary["cases"])
        self.assertEqual(10, summary["verdict_correct"])
        self.assertEqual(12, summary["small_task_seconds"])

    def test_wrong_verdict_is_retained_not_retried_away(self):
        self.review["records"][0]["verdict_correct"] = False
        self.assertEqual(9, self.module.summarize(self.pack, self.review)["verdict_correct"])

    def test_missing_and_duplicate_case_cannot_improve_denominator(self):
        for records in (self.review["records"][:-1], self.review["records"] + self.review["records"][:1]):
            with self.subTest(records=len(records)), self.assertRaises(ValueError):
                self.module.summarize(self.pack, dict(self.review, records=records))

    def test_unknown_case_and_zero_cases_are_rejected(self):
        for pack in (dict(self.pack, cases=[]), dict(self.pack, cases=self.pack["cases"][:-1])):
            with self.subTest(pack=pack), self.assertRaises(ValueError):
                self.module.summarize(pack, self.review)

    def test_missing_event_citation_is_rejected(self):
        self.review["records"][0]["event_ids"] = []
        with self.assertRaises(ValueError):
            self.module.summarize(self.pack, self.review)

    def test_boolean_scores_are_not_coerced(self):
        for value in (1, "true", None):
            review = copy.deepcopy(self.review)
            review["records"][0]["evidence_complete"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.module.summarize(self.pack, review)

    def test_invalid_metrics_are_rejected(self):
        for field, value in (("duration_seconds", -1), ("duration_seconds", float("nan")),
                             ("duration_seconds", float("inf")), ("duration_seconds", True),
                             ("redundant_questions", -1), ("redundant_questions", 0.5)):
            review = copy.deepcopy(self.review)
            review["records"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.module.summarize(self.pack, review)

    def test_scope_violation_is_visible_even_when_verdict_correct(self):
        self.review["records"][0]["scope_respected"] = False
        result = self.module.summarize(self.pack, self.review)
        self.assertEqual(1, result["scope_violations"])
        self.assertEqual(10, result["verdict_correct"])

    def test_pack_requires_prompt_rubric_and_unique_ids(self):
        for key in ("prompt", "expected"):
            pack = copy.deepcopy(self.pack)
            pack["cases"][0][key] = ""
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.module.summarize(pack, self.review)
        pack = copy.deepcopy(self.pack)
        pack["cases"].append(pack["cases"][0])
        with self.assertRaises(ValueError):
            self.module.summarize(pack, self.review)

    def test_cli_rejects_duplicate_keys_without_echoing_data(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "review.json"
            source.write_text('{"version": 1, "version": "sensitive-value"}', encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/evaluate_behavior.py"),
                                     "--review", str(source)], capture_output=True, text=True)
            self.assertEqual(1, result.returncode)
            self.assertNotIn("sensitive-value", result.stdout + result.stderr)

    def test_cli_outputs_metrics_for_reviewed_fixture(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "review.json"
            source.write_text(json.dumps(self.review), encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/evaluate_behavior.py"),
                                     "--review", str(source)], capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(10, json.loads(result.stdout)["cases"])


if __name__ == "__main__":
    unittest.main()
