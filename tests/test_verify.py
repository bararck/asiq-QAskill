"""Fixture baru: validator menerima paket sah dan menolak kerusakan terarah."""
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import verify


MIT_FIXTURE = '''MIT License

Copyright (c) 2026 bararck

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


class PackageFixtures(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="asiq-fixture-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for relative in verify.REQUIRED:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# Fixture\n", encoding="utf-8")
        (self.root / "LICENSE").write_text(MIT_FIXTURE, encoding="utf-8")
        self.skill = self.root / verify.SKILL
        self.valid_metadata = (
            '---\nname: asiq\ndescription: "Gunakan untuk QA dan regresi."\n'
            'version: 0.1.0\n---\n# Fixture\n'
        )
        self.skill.write_text(self.valid_metadata, encoding="utf-8")

    def alter(self, relative, text):
        (self.root / relative).write_text(text, encoding="utf-8")

    def errors(self):
        return verify.validate_package(self.root)

    def test_valid_fixture(self):
        self.assertEqual([], self.errors())

    def test_missing_required_file(self):
        (self.root / "SECURITY.md").unlink()
        self.assertTrue(any("file wajib" in e for e in self.errors()))

    def test_metadata_missing_opening(self):
        self.skill.write_text(self.valid_metadata[4:], encoding="utf-8")
        self.assertTrue(verify.metadata_errors(self.skill.read_text(encoding="utf-8")))

    def test_metadata_missing_closing(self):
        self.assertTrue(verify.metadata_errors("---\nname: asiq\n"))

    def test_metadata_wrong_name(self):
        self.assertTrue(verify.metadata_errors(self.valid_metadata.replace("name: asiq", "name: other")))

    def test_metadata_duplicate(self):
        self.assertTrue(verify.metadata_errors(self.valid_metadata.replace("name: asiq", "name: asiq\nname: asiq")))

    def test_metadata_description_over_limit(self):
        self.assertTrue(verify.metadata_errors(self.valid_metadata.replace("Gunakan untuk QA dan regresi.", "x" * 61 + ".")))

    def test_metadata_bad_version(self):
        self.assertTrue(verify.metadata_errors(self.valid_metadata.replace("0.1.0", "next")))

    def test_metadata_empty_body(self):
        self.assertTrue(verify.metadata_errors(self.valid_metadata.replace("# Fixture", "")))

    def test_missing_link(self):
        self.alter("README.md", "[hilang](missing.md)\n")
        self.assertTrue(any("tautan hilang" in e for e in self.errors()))

    def test_valid_relative_link(self):
        self.alter("README.md", "[aman](SECURITY.md)\n")
        self.assertEqual([], self.errors())

    def test_link_escape(self):
        self.alter("README.md", "[keluar](../outside.md)\n")
        self.assertTrue(any("keluar paket" in e for e in self.errors()))

    def test_encoded_link_escape(self):
        self.alter("README.md", "[keluar](%2e%2e/outside.md)\n")
        self.assertTrue(any("keluar paket" in e for e in self.errors()))

    def test_anchor_validation(self):
        self.alter("README.md", "[ada](SECURITY.md#fixture)\n")
        self.assertEqual([], self.errors())
        self.alter("README.md", "[hilang](SECURITY.md#unknown)\n")
        self.assertTrue(any("anchor hilang" in e for e in self.errors()))

    def test_private_path_rejected(self):
        self.alter("README.md", "C:/" + "Users/" + "asset/" + "private\n")
        self.assertTrue(any("privat" in e for e in self.errors()))

    def test_ignores_only_git_and_bytecode_directories(self):
        for relative in (".git", "__pycache__", "source/.git", "source/__pycache__"):
            directory = self.root / relative
            directory.mkdir(parents=True)
            (directory / "invalid.md").write_bytes(b"\xff")
            (directory / "private.py").write_text("/" + "home/person/private", encoding="utf-8")
        self.assertEqual([], self.errors())

    def test_scans_arbitrary_source_directories(self):
        for name in ("source", ".hidden", "vendor", "build"):
            directory = self.root / name
            directory.mkdir()
            (directory / "invalid.md").write_bytes(b"\xff")
        errors = self.errors()
        self.assertEqual(4, sum("teks tidak terbaca" in e for e in errors))

    def test_license_required(self):
        (self.root / "LICENSE").unlink()
        self.assertTrue(any("file wajib hilang: LICENSE" == e for e in self.errors()))

    def test_license_rejects_wrong_owner(self):
        self.alter("LICENSE", MIT_FIXTURE.replace("bararck", "other"))
        self.assertTrue(any("lisensi" in e for e in self.errors()))

    def test_license_rejects_modified_terms(self):
        for text in ("pending\n", MIT_FIXTURE.replace("WITHOUT WARRANTY", "WITH WARRANTY"),
                     MIT_FIXTURE + "\nAdditional restrictions apply.\n"):
            with self.subTest(text=text):
                self.alter("LICENSE", text)
                self.assertTrue(any("lisensi" in e for e in self.errors()))

    def test_license_accepts_whitespace_variation(self):
        self.alter("LICENSE", MIT_FIXTURE.replace("\n", "  \n\n"))
        self.assertEqual([], self.errors())


class GateFixtures(unittest.TestCase):
    def run_inner(self, case):
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(case)
        return unittest.TextTestRunner(stream=io.StringIO()).run(suite)

    def test_gate_accepts_real_success(self):
        class Passing(unittest.TestCase):
            def test_case(self):
                self.assertEqual(2, len("qa"))
        self.assertTrue(verify.result_is_clean(self.run_inner(Passing), 1))

    def test_gate_rejects_zero_and_wrong_count(self):
        empty = unittest.TestResult()
        self.assertFalse(verify.result_is_clean(empty, 0))
        self.assertFalse(verify.result_is_clean(empty, 1))
        empty.testsRun = 1
        self.assertFalse(verify.result_is_clean(empty, 2))

    def test_gate_rejects_stop_on_last_test(self):
        class Stopped(unittest.TestCase):
            def run(self, result=None):
                result = super().run(result)
                result.stop()
                return result

            def test_case(self):
                self.assertTrue(True)

        result = self.run_inner(Stopped)
        self.assertEqual(1, result.testsRun)
        self.assertTrue(result.wasSuccessful())
        self.assertTrue(result.shouldStop)
        self.assertFalse(verify.result_is_clean(result, 1))

    def test_gate_rejects_skip(self):
        class Skipped(unittest.TestCase):
            @unittest.skip("fixture negatif")
            def test_case(self):
                pass
        self.assertFalse(verify.result_is_clean(self.run_inner(Skipped), 1))

    def test_gate_rejects_unexpected_expected_failure_and_errors(self):
        class Unexpected(unittest.TestCase):
            @unittest.expectedFailure
            def test_case(self):
                self.assertTrue(True)
        class Expected(unittest.TestCase):
            @unittest.expectedFailure
            def test_case(self):
                self.fail("fixture negatif")
        class Broken(unittest.TestCase):
            def test_case(self):
                raise RuntimeError("fixture negatif")
        class Failed(unittest.TestCase):
            def test_case(self):
                self.fail("fixture negatif")
        for case in (Unexpected, Expected, Broken, Failed):
            with self.subTest(case=case.__name__):
                self.assertFalse(verify.result_is_clean(self.run_inner(case), 1))


if __name__ == "__main__":
    unittest.main()
