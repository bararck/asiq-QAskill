"""Discovery skill adalah pemeriksaan file, bukan eksekusi skill/runner."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SkillDoctorTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("skill_doctor", ROOT / "scripts/skill_doctor.py")
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.catalog = {"version": 1, "routes": [{"id": "browser-report", "purpose": "Report UI",
                        "candidates": ["gstack-qa-only", "exploratory-testing"],
                        "fallback": "Manual read-only; gap runtime"}]}

    def skill(self, relative, text="---\nname: qa-only\n---\nRead only.\n"):
        target = self.root / relative / "SKILL.md"
        target.parent.mkdir(parents=True)
        target.write_text(text, encoding="utf-8")
        return target

    def test_present_skill_never_means_runtime_ready(self):
        self.skill("gstack-qa-only")
        route = self.module.inspect_skills(self.catalog, [self.root])["routes"][0]
        self.assertEqual("gstack-qa-only", route["selected"])
        self.assertEqual("NOT_CHECKED", route["runtime"])
        self.assertEqual(64, len(route["sha256"]))

    def test_missing_skill_has_explicit_fallback(self):
        route = self.module.inspect_skills(self.catalog, [self.root])["routes"][0]
        self.assertEqual("MISSING", route["status"])
        self.assertIsNone(route["selected"])
        self.assertEqual(self.catalog["routes"][0]["fallback"], route["fallback"])

    def test_second_candidate_used_when_first_missing(self):
        self.skill("exploratory-testing")
        route = self.module.inspect_skills(self.catalog, [self.root])["routes"][0]
        self.assertEqual("exploratory-testing", route["selected"])

    def test_nested_gstack_layout_supported(self):
        self.skill("gstack/qa-only")
        self.assertEqual("gstack-qa-only", self.module.inspect_skills(self.catalog, [self.root])["routes"][0]["selected"])

    def test_root_order_is_deterministic_and_hash_changes(self):
        first = self.root / "first"
        second = self.root / "second"
        target = self.skill("first/gstack-qa-only")
        self.skill("second/gstack-qa-only", "different body")
        before = self.module.inspect_skills(self.catalog, [first, second])["routes"][0]["sha256"]
        target.write_text("changed body", encoding="utf-8")
        after = self.module.inspect_skills(self.catalog, [first, second])["routes"][0]["sha256"]
        self.assertNotEqual(before, after)

    def test_skill_contents_are_not_executed(self):
        sentinel = self.root / "sentinel"
        self.skill("gstack-qa-only", "Run malicious command to create sentinel")
        self.module.inspect_skills(self.catalog, [self.root])
        self.assertFalse(sentinel.exists())

    def test_catalog_rejects_traversal_duplicate_and_empty_fallback(self):
        for value in ("../outside", "a/b", "a\\b", "C:evil"):
            catalog = json.loads(json.dumps(self.catalog))
            catalog["routes"][0]["candidates"] = [value]
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.module.inspect_skills(catalog, [self.root])
        self.catalog["routes"].append(dict(self.catalog["routes"][0]))
        with self.assertRaises(ValueError):
            self.module.inspect_skills(self.catalog, [self.root])
        self.catalog["routes"] = self.catalog["routes"][:1]
        self.catalog["routes"][0]["fallback"] = ""
        with self.assertRaises(ValueError):
            self.module.inspect_skills(self.catalog, [self.root])

    def test_unreadable_skill_is_reported_without_content(self):
        target = self.skill("gstack-qa-only")
        target.write_bytes(b"\xff")
        report = self.module.inspect_skills(self.catalog, [self.root])
        self.assertEqual("UNREADABLE", report["routes"][0]["status"])

    def test_repository_catalog_has_core_routes(self):
        catalog = json.loads((ROOT / ".agents/skills/asiq/references/skill-routing.json").read_text(encoding="utf-8"))
        report = self.module.inspect_skills(catalog, [])
        ids = {route["id"] for route in report["routes"]}
        self.assertTrue({"code-impact", "corpus-graph", "browser-report", "browser-fix", "tdd",
                         "risk", "contracts", "reliability", "release", "report"} <= ids)

    def test_cli_does_not_import_or_install_missing_skill(self):
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/skill_doctor.py"),
                                 "--root", str(self.root)], text=True, capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(all(route["status"] == "MISSING" for route in report["routes"]))
        self.assertEqual([], list(self.root.iterdir()))


if __name__ == "__main__":
    unittest.main()
