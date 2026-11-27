"""Probe tests use controlled subprocess outcomes, without browser/network access."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import skill_doctor


class RuntimeProbeTests(unittest.TestCase):
    def test_exit_zero_without_expected_marker_is_not_ready(self):
        with patch.object(skill_doctor.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "unrelated", "")):
            self.assertEqual("INVALID_OUTPUT", skill_doctor.probe_runtime(["tool", "--version"], "expected")["status"])

    def test_success_requires_marker_and_retains_exit(self):
        with patch.object(skill_doctor.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "graphify 1.0", "")) as run:
            result = skill_doctor.probe_runtime(["tool", "--version"], "graphify")
            self.assertEqual("READY", result["status"])
            self.assertEqual(0, result["exit_code"])
            self.assertFalse(run.call_args.kwargs["shell"])
            self.assertEqual(8, run.call_args.kwargs["timeout"])

    def test_nonzero_is_error_without_leaking_output(self):
        with patch.object(skill_doctor.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "secret-example", "")):
            result = skill_doctor.probe_runtime(["tool"], "expected")
            self.assertEqual("ERROR", result["status"])
            self.assertNotIn("secret-example", str(result))

    def test_missing_executable_is_missing(self):
        with patch.object(skill_doctor.subprocess, "run", side_effect=FileNotFoundError):
            self.assertEqual("MISSING", skill_doctor.probe_runtime(["tool"], "expected")["status"])

    def test_timeout_is_not_retried(self):
        with patch.object(skill_doctor.subprocess, "run", side_effect=subprocess.TimeoutExpired(["tool"], 8)) as run:
            self.assertEqual("TIMEOUT", skill_doctor.probe_runtime(["tool"], "expected")["status"])
            self.assertEqual(1, run.call_count)

    def test_permission_error_is_distinct_from_missing(self):
        with patch.object(skill_doctor.subprocess, "run", side_effect=PermissionError):
            self.assertEqual("ERROR", skill_doctor.probe_runtime(["tool"], "expected")["status"])


if __name__ == "__main__":
    unittest.main()
