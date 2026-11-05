"""Fixture sintetis untuk gate bukti aplikasi; bukan hasil QA produk."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
try:
    import qa_gate
except ModuleNotFoundError:
    qa_gate = None


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="asiq-gate-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.evidence = self.root / "evidence"
        self.evidence.mkdir()
        self.artifact = self.evidence / "result.txt"
        self.artifact.write_bytes(b"observed: allowed\n")
        self.context = {"source_revision": "a" * 40, "build_id": "build-1",
                        "environment": "isolated-test", "config_sha256": "b" * 64}
        self.baseline = {"version": 1, "context": self.context,
                         "requirements": ["REQ-1"], "risks": ["RISK-1"],
                         "scenarios": [{"id": "SC-1", "requirement_ids": ["REQ-1"],
                                        "risk_ids": ["RISK-1"]}]}
        self.ledger = {"version": 1, "baseline_sha256": "", "context": self.context,
                       "scenarios": [{"id": "SC-1", "selected": True, "gap": "",
                                      "attempts": [self.attempt()]}],
                       "counts": {"total": 1, "selected": 1, "passed": 1,
                                  "failed": 0, "not_run": 0}}
        self.baseline_path = self.root / "baseline.json"
        self.ledger_path = self.root / "ledger.json"

    def attempt(self):
        return {"id": "A-1", "context": dict(self.context), "status": "PASS",
                "command": {"argv": ["runner", "--offline"], "exit_code": 0,
                            "status": "completed"},
                "oracle": {"expected": "allowed", "observed": "allowed", "verified": True},
                "artifacts": [{"path": "result.txt", "sha256": hashlib.sha256(
                    self.artifact.read_bytes()).hexdigest()}], "resolves": [], "fix": ""}

    def save(self):
        self.baseline_path.write_text(json.dumps(self.baseline), encoding="utf-8")
        self.ledger["baseline_sha256"] = hashlib.sha256(self.baseline_path.read_bytes()).hexdigest()
        self.ledger_path.write_text(json.dumps(self.ledger), encoding="utf-8")

    def errors(self):
        self.assertIsNotNone(qa_gate, "qa_gate feature missing")
        self.save()
        return qa_gate.validate_files(self.ledger_path, self.baseline_path, self.evidence)

    def test_valid_bound_evidence(self):
        self.assertEqual([], self.errors())

    def test_schema_inventory_traceability(self):
        import copy
        changes = [
            lambda: self.ledger.update(version=True),
            lambda: self.ledger.update(secret="do-not-echo"),
            lambda: self.ledger["scenarios"].clear(),
            lambda: self.ledger["scenarios"].append(copy.deepcopy(self.ledger["scenarios"][0])),
            lambda: self.ledger["scenarios"][0].update(id="UNKNOWN"),
            lambda: self.baseline["scenarios"][0].update(requirement_ids=["UNKNOWN"]),
            lambda: self.baseline["requirements"].append("REQ-ORPHAN"),
            lambda: self.baseline["risks"].append("RISK-ORPHAN"),
            lambda: self.baseline["scenarios"][0].update(risk_ids=[]),
            lambda: self.ledger["counts"].update(total=True),
            lambda: self.ledger["counts"].update(passed=9),
            lambda: self.ledger["scenarios"][0].update(selected=False),
        ]
        original = copy.deepcopy((self.baseline, self.ledger))
        for change in changes:
            self.baseline, self.ledger = copy.deepcopy(original)
            change()
            with self.subTest(change=changes.index(change)):
                self.assertTrue(self.errors())

    def test_explicit_not_run_and_unselected_gaps_block_gate(self):
        scenario = self.ledger["scenarios"][0]
        for selected in (False, True):
            scenario.update(selected=selected, gap="Blocked by unavailable fixture", attempts=[])
            self.ledger["counts"].update(selected=int(selected), passed=0, not_run=1)
            self.assertTrue(self.errors())

    def test_duplicate_keys_and_malformed_json_are_redacted(self):
        self.save()
        for text in ('{"version":1,"version":1}', '{"secret":"do-not-echo",'):
            self.ledger_path.write_text(text, encoding="utf-8")
            errors = qa_gate.validate_files(self.ledger_path, self.baseline_path, self.evidence)
            self.assertTrue(errors)
            self.assertNotIn("do-not-echo", str(errors))

    def test_attempt_contract_oracle_and_context(self):
        import copy
        original = copy.deepcopy(self.ledger)
        changes = [
            lambda a: a.update(context={**a["context"], "build_id": "other"}),
            lambda a: a["oracle"].update(verified=False),
            lambda a: a["oracle"].update(expected=""),
            lambda a: a.update(artifacts=[]),
            lambda a: a["artifacts"][0].update(sha256="0" * 64),
            lambda a: a["command"].update(exit_code=True),
            lambda a: a["command"].update(exit_code=1),
            lambda a: a["command"].update(status="timeout"),
            lambda a: a["command"].update(argv=[]),
            lambda a: a.update(status="SKIP"),
            lambda a: a.update(extra="secret"),
            lambda a: a.update(resolves=["UNKNOWN"], fix="fixed"),
        ]
        for index, change in enumerate(changes):
            self.ledger = copy.deepcopy(original)
            change(self.ledger["scenarios"][0]["attempts"][0])
            with self.subTest(change=index):
                self.assertTrue(self.errors())

    def test_fail_retry_requires_explicit_fix_and_retest_link(self):
        import copy
        failed = self.ledger["scenarios"][0]["attempts"][0]
        failed.update(status="FAIL")
        failed["command"]["exit_code"] = 1
        failed["oracle"].update(observed="denied", verified=False)
        passed = self.attempt()
        passed["id"] = "A-2"
        attempts = self.ledger["scenarios"][0]["attempts"]
        attempts.append(passed)
        self.assertTrue(self.errors(), "retry must not hide first FAIL")
        passed.update(resolves=["A-1"], fix="FIX-1: corrected authorization policy")
        self.assertEqual([], self.errors())
        for resolves, fix in (([], "FIX-1"), (["A-1"], ""), (["A-2"], "FIX-1"),
                              (["UNKNOWN"], "FIX-1"), (["A-1", "A-1"], "FIX-1")):
            passed.update(resolves=resolves, fix=fix)
            self.assertTrue(self.errors())
        passed.update(resolves=["A-1"], fix="FIX-1")
        attempts.append(copy.deepcopy(passed))
        self.assertTrue(self.errors(), "duplicate attempt ID")

    def test_latest_fail_and_unresolved_earlier_fail_block(self):
        first = self.ledger["scenarios"][0]["attempts"][0]
        first["status"] = "FAIL"
        self.ledger["counts"].update(passed=0, failed=1)
        self.assertTrue(self.errors())
        second = self.attempt()
        second.update(id="A-2", status="FAIL")
        third = self.attempt()
        third.update(id="A-3", resolves=["A-2"], fix="FIX-2")
        self.ledger["scenarios"][0]["attempts"].extend([second, third])
        self.ledger["counts"].update(passed=1, failed=0)
        self.assertTrue(self.errors())
        third["resolves"] = ["A-1", "A-2"]
        self.assertEqual([], self.errors())

    def test_unsafe_artifact_paths_are_rejected_even_with_matching_bytes(self):
        outside = self.root / "outside.txt"
        outside.write_bytes(self.artifact.read_bytes())
        paths = ["../outside.txt", str(outside), "C:/outside.txt", "C:outside.txt",
                 "\\\\server\\share\\file", "sub/../result.txt", "./result.txt",
                 "result.txt:stream", "result.txt/", "sub//result.txt", "result.txt."]
        for path in paths:
            self.ledger["scenarios"][0]["attempts"][0]["artifacts"][0]["path"] = path
            with self.subTest(path=path):
                self.assertTrue(self.errors())

    def make_directory_link(self, target, link):
        import os
        if os.name == "nt":
            import _winapi
            _winapi.CreateJunction(str(target), str(link))
            self.addCleanup(lambda: link.rmdir())
        else:
            link.symlink_to(target, target_is_directory=True)
            self.addCleanup(lambda: link.unlink())

    def test_evidence_root_link_and_link_ancestor_are_rejected(self):
        alias = self.root / "alias"
        self.make_directory_link(self.evidence, alias)
        self.save()
        self.assertTrue(qa_gate.validate_files(self.ledger_path, self.baseline_path, alias))
        nested = self.evidence / "nested"
        nested.mkdir()
        (nested / "result.txt").write_bytes(self.artifact.read_bytes())
        self.assertTrue(qa_gate.validate_files(self.ledger_path, self.baseline_path, alias / "nested"))

    def test_artifact_directory_link_is_rejected(self):
        target = self.root / "external"
        target.mkdir()
        (target / "result.txt").write_bytes(self.artifact.read_bytes())
        self.make_directory_link(target, self.evidence / "linked")
        self.ledger["scenarios"][0]["attempts"][0]["artifacts"][0]["path"] = "linked/result.txt"
        self.assertTrue(self.errors())

    def test_missing_evidence_and_directory_not_artifact(self):
        for path in ("absent.txt", "directory"):
            (self.evidence / "directory").mkdir(exist_ok=True)
            self.ledger["scenarios"][0]["attempts"][0]["artifacts"][0]["path"] = path
            self.assertTrue(self.errors())

    def test_cli_usage_errors_redact_supplied_values(self):
        command = [sys.executable, "-B", str(Path(__file__).resolve().parents[1] / "scripts" / "qa_gate.py")]
        self.save()
        command.extend(["--ledger", str(self.ledger_path), "--baseline", str(self.baseline_path),
                        "--evidence-root", str(self.evidence), "--unknown=secret-do-not-echo"])
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(2, result.returncode)
        self.assertNotIn("secret-do-not-echo", result.stderr)

    def test_context_and_json_type_matrix(self):
        import copy
        original = copy.deepcopy((self.baseline, self.ledger))
        for value in (None, True, 1, [], {}, "1"):
            self.baseline, self.ledger = copy.deepcopy(original)
            self.ledger["scenarios"] = value
            self.assertTrue(self.errors())
        self.baseline, self.ledger = copy.deepcopy(original)
        self.ledger["context"] = {**self.context, "build_id": "other"}
        self.assertTrue(self.errors())
        self.save()
        self.baseline_path.write_text('{"version":1,"version":1}')
        self.assertTrue(qa_gate.validate_files(self.ledger_path, self.baseline_path, self.evidence))
        self.ledger_path.write_text('{"version":NaN}')
        self.assertTrue(qa_gate.validate_files(self.ledger_path, self.baseline_path, self.evidence))

    def test_baseline_digest_binding(self):
        self.save()
        self.baseline_path.write_text(self.baseline_path.read_text() + " ")
        self.assertTrue(qa_gate.validate_files(self.ledger_path, self.baseline_path, self.evidence))

    def test_cli_success_failure_and_no_command_execution(self):
        self.ledger["scenarios"][0]["attempts"][0]["command"]["argv"] = ["NEVER-EXECUTE-THIS"]
        self.save()
        command = [sys.executable, "-B", str(Path(__file__).resolve().parents[1] / "scripts" / "qa_gate.py"),
                   "--ledger", str(self.ledger_path), "--baseline", str(self.baseline_path),
                   "--evidence-root", str(self.evidence)]
        passed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(0, passed.returncode, passed.stderr)
        self.assertIn("PASS", passed.stdout)
        self.ledger_path.write_text('{"secret":"do-not-echo",')
        failed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(1, failed.returncode)
        self.assertNotIn("do-not-echo", failed.stderr)
        self.assertIn("ERROR", failed.stderr)
        missing = subprocess.run(command[:3], capture_output=True, text=True)
        self.assertEqual(2, missing.returncode)
        self.assertNotIn("Traceback", missing.stderr)
        self.assertFalse((self.root / "NEVER-EXECUTE-THIS").exists())


if __name__ == "__main__":
    unittest.main()
