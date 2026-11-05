"""Offline execution-recorder contracts using disposable synthetic repositories."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "record_run.py"


class RecordRunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "source"
        self.repo.mkdir()
        self.git("init", "--quiet")
        self.git("config", "user.name", "Synthetic Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        (self.repo / "fixture.txt").write_text("fixture\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "synthetic fixture")
        self.output = self.root / "evidence"

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, check=True,
                              capture_output=True).stdout.decode().strip()

    def run_recorder(self, code, *extra, output=None, acknowledge=True, timeout="5"):
        argv = [sys.executable, "-B", str(SCRIPT), "--cwd", str(self.repo),
                "--output", str(output or self.output), "--timeout", timeout]
        if acknowledge:
            argv.append("--acknowledge-sensitive-output")
        return subprocess.run(argv + ["--", sys.executable, "-B", "-c", code, *extra],
                              capture_output=True, timeout=30,
                              env={**os.environ, "GIT_CEILING_DIRECTORIES": str(self.root.parent)})

    def test_timeout_retains_partial_streams_and_never_retries(self):
        result = self.run_recorder(
            "import sys,time; print('first-attempt', flush=True); time.sleep(10)", timeout="0.3")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.output / "record.json").is_file(), "timeout needs a retained record")
        record = self.record()
        self.assertEqual(record["command"]["status"], "timeout")
        self.assertIsInstance(record["command"]["exit_code"], int)
        self.assertNotEqual(record["command"]["exit_code"], 0)
        self.assertEqual((self.output / "stdout.bin").read_bytes().count(b"first-attempt"), 1)
        self.assertNotIn(b"first-attempt", result.stdout + result.stderr)

    def test_invalid_requests_do_not_execute_or_create_output(self):
        marker = self.repo / "executed"
        code = "from pathlib import Path; Path('executed').touch()"
        cases = [
            {"acknowledge": False},
            {"timeout": "nan"}, {"timeout": "inf"}, {"timeout": "0"},
            {"timeout": "-1"},
            {"output": self.repo / ".git" / "evidence"},
        ]
        for options in cases:
            with self.subTest(options=options):
                result = self.run_recorder(code, **options)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(marker.exists(), "rejected invocation must not execute")
                self.assertFalse(self.output.exists())

    def test_linked_paths_and_ancestors_are_rejected(self):
        linked = self.root / "linked"
        if os.name == "nt":
            subprocess.run(["cmd", "/c", "mklink", "/J", str(linked), str(self.repo)],
                           check=True, capture_output=True)
        else:
            linked.symlink_to(self.repo, target_is_directory=True)
        self.addCleanup(lambda: linked.rmdir() if os.name == "nt" else linked.unlink())
        for target in (linked, linked / "evidence"):
            with self.subTest(target=target):
                result = self.run_recorder("print('not executed')", output=target)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.repo / "evidence").exists())

    def test_start_failure_retains_record_without_sensitive_diagnostics(self):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT),
            "--cwd", str(self.repo), "--output", str(self.output), "--timeout", "5",
            "--acknowledge-sensitive-output", "--", "missing-sensitive-executable"], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.output / "record.json").is_file())
        self.assertEqual(self.record()["command"]["status"], "error")
        self.assertNotIn(b"missing-sensitive-executable", result.stdout + result.stderr)

    def test_nonzero_retained_once_with_dirty_context(self):
        (self.repo / "fixture.txt").write_text("dirty", encoding="utf-8")
        result = self.run_recorder("import sys; print('initial-failure'); sys.exit(7)")
        self.assertEqual(result.returncode, 7)
        record = self.record()
        self.assertTrue(record["context"]["dirty"])
        self.assertEqual(record["command"]["status"], "completed")
        self.assertEqual(record["command"]["exit_code"], 7)
        self.assertEqual((self.output / "stdout.bin").read_bytes().count(b"initial-failure"), 1)
        self.assertNotIn(b"initial-failure", result.stdout + result.stderr)

    def test_existing_output_is_never_overwritten_or_executed(self):
        self.assertEqual(self.run_recorder("print('original')").returncode, 0)
        before = {p.name: p.read_bytes() for p in self.output.iterdir()}
        result = self.run_recorder("from pathlib import Path; Path('executed').touch()")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.repo / "executed").exists())
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.output.iterdir()})

    def test_argv_is_literal_not_shell_and_not_json_input(self):
        literal = 'hello ; echo injected > shell-marker & $(echo expansion) | *'
        result = self.run_recorder("import sys; sys.stdout.write(sys.argv[1])", literal)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.output / "stdout.bin").read_text(), literal)
        self.assertEqual(self.record()["command"]["argv"][-1], literal)
        self.assertFalse((self.repo / "shell-marker").exists())

    def test_cli_requires_separator_command_and_safe_static_errors(self):
        base = [sys.executable, "-B", str(SCRIPT), "--cwd", str(self.repo),
                "--output", str(self.output), "--timeout", "5", "--acknowledge-sensitive-output"]
        for tail in ([], ["--"], ["secret-invalid-option"], ["--unknown-secret"]):
            with self.subTest(tail=tail):
                result = subprocess.run(base + tail, capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.output.exists())
                self.assertNotIn(b"secret", result.stdout + result.stderr)

    def test_non_repository_refuses_without_leaking_paths(self):
        self.repo = self.root
        result = self.run_recorder("print('not executed')")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())
        self.assertNotIn(str(self.root).encode(), result.stdout + result.stderr)
        self.assertNotIn(b"Traceback", result.stderr)

    def test_linked_cwd_is_rejected_before_execution(self):
        linked = self.root / "linked-cwd"
        if os.name == "nt":
            subprocess.run(["cmd", "/c", "mklink", "/J", str(linked), str(self.repo)],
                           check=True, capture_output=True)
        else:
            linked.symlink_to(self.repo, target_is_directory=True)
        self.addCleanup(lambda: linked.rmdir() if os.name == "nt" else linked.unlink())
        self.repo = linked
        result = self.run_recorder("print('not executed')")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())

    def record(self):
        return json.loads((self.output / "record.json").read_text(encoding="utf-8"))

    def test_completed_captures_context_bytes_hashes_without_printing_streams(self):
        result = self.run_recorder("import sys; print('sensitive-out'); print('sensitive-err', file=sys.stderr)")
        self.assertEqual(result.returncode, 0, result.stderr)
        record = self.record()
        self.assertEqual(record["format"], "asiq-execution-record-v1")
        self.assertEqual(record["context"]["source_revision"], self.git("rev-parse", "HEAD"))
        self.assertFalse(record["context"]["dirty"])
        self.assertEqual(record["context"]["cwd"], str(self.repo))
        self.assertEqual(record["command"]["exit_code"], 0)
        self.assertEqual(record["command"]["status"], "completed")
        self.assertGreaterEqual(record["command"]["duration_seconds"], 0)
        self.assertEqual(record["command"]["argv"][:2], [sys.executable, "-B"])
        for stream in ("stdout", "stderr"):
            raw = (self.output / (stream + ".bin")).read_bytes()
            self.assertIn(b"sensitive-", raw)
            self.assertEqual(record["streams"][stream]["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertNotIn(b"sensitive-", result.stdout + result.stderr)
        self.assertNotIn("oracle", record)
        self.assertNotIn("PASS", json.dumps(record))


if __name__ == "__main__":
    unittest.main()
