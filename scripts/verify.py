"""Validasi paket lokal dan fixture unittest; tanpa dependensi eksternal."""
from __future__ import annotations

import os
import io
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SKILL = ".agents/skills/asiq/SKILL.md"
REQUIRED = (
    "README.md", "SECURITY.md", "PROVENANCE.md", "LICENSE", SKILL,
    ".agents/skills/asiq/references/requirements-oracles.md",
    ".agents/skills/asiq/references/manual-risk.md",
    ".agents/skills/asiq/references/sdet-ci.md",
    ".agents/skills/asiq/references/performance-reliability.md",
    ".agents/skills/asiq/references/security-evidence.md",
    ".agents/skills/asiq/templates/scenario.md",
    ".agents/skills/asiq/templates/bug.md",
    ".agents/skills/asiq/templates/release-decision.md",
    "scripts/verify.py", "tests/test_verify.py", ".github/workflows/verify.yml",
    "scripts/qa_gate.py", "tests/test_qa_gate.py", "docs/qa-gate.md",
    "labs/stateful_workflow/workflow.py", "labs/stateful_workflow/README.md",
    "tests/test_stateful_workflow.py", "benchmarks/README.md",
    "docs/company-pilot.md", "CHANGELOG.md",
    ".agents/skills/asiq/references/stateful-workflows.md",
    ".agents/skills/asiq/references/dependency-flow-review.md",
    ".agents/skills/asiq/templates/dependency-flow.md",
    "scripts/record_run.py", "tests/test_record_run.py", "docs/record-run.md",
)
EXPECTED_TESTS = 62
MIT_TEXT = """MIT License

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
"""
TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".txt", ".json", ".toml"}
PRIVATE_MARKERS = ("qas" + "kill", "c:" + "/users/" + "asset/", "c:" + "\\users\\" + "asset\\")
LINK = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
LOCAL_PATH = re.compile(r"(?:[a-z]:[\\/](?:users|home)[\\/]|/" + r"home/[^ /\n]+/)", re.I)


def metadata_errors(text: str) -> list[str]:
    """Subset frontmatter: tepat tiga field scalar; bukan parser YAML umum."""
    errors = []
    if not text.startswith("---\n"):
        return ["metadata: pembuka tidak valid"]
    head, separator, body = text[4:].partition("\n---\n")
    if not separator or not body.strip():
        return ["metadata: penutup atau isi hilang"]
    fields = {}
    for line in head.splitlines():
        match = re.fullmatch(r"([a-z]+): (.+)", line)
        if not match:
            errors.append("metadata: format scalar tidak didukung")
            continue
        key, value = match.groups()
        if key in fields:
            errors.append("metadata: field duplikat")
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        fields[key] = value
    if set(fields) != {"name", "description", "version"}:
        errors.append("metadata: field wajib/asing")
    if fields.get("name") != "asiq":
        errors.append("metadata: nama harus asiq")
    description = fields.get("description", "")
    if not (1 <= len(description) <= 60) or not description.endswith("."):
        errors.append("metadata: deskripsi kosong/panjang/tanpa titik")
    if not re.fullmatch(r"\d+\.\d+\.\d+", fields.get("version", "")):
        errors.append("metadata: versi tidak valid")
    return errors


def link_errors(root: Path, source: Path, text: str) -> list[str]:
    errors = []
    for raw in LINK.findall(text):
        target = unquote(raw.strip())
        parts = urlsplit(target)
        if parts.scheme in {"https", "http", "mailto"}:
            continue
        if parts.scheme or parts.netloc or "\\" in target or parts.query:
            errors.append(f"{source.name}: tautan tidak didukung: {raw}")
            continue
        destination = (source.parent / parts.path).resolve() if parts.path else source.resolve()
        if parts.path.startswith("/") or not destination.is_relative_to(root.resolve()):
            errors.append(f"{source.name}: tautan keluar paket: {raw}")
            continue
        if not destination.is_file():
            errors.append(f"{source.name}: tautan hilang: {raw}")
            continue
        if parts.fragment:
            content = destination.read_text(encoding="utf-8")
            headings = re.findall(r"^#{1,6}\s+(.+)$", content, re.MULTILINE)
            slugs = {re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-") for h in headings}
            if parts.fragment not in slugs:
                errors.append(f"{source.name}: anchor hilang: {raw}")
    return errors


def validate_package(root: Path) -> list[str]:
    root = root.resolve()
    errors = []
    for relative in REQUIRED:
        if not (root / relative).is_file():
            errors.append(f"file wajib hilang: {relative}")
    license_path = root / "LICENSE"
    if license_path.is_file():
        try:
            text = license_path.read_text(encoding="utf-8")
            if text.split() != MIT_TEXT.split():
                errors.append("lisensi: wajib teks MIT dengan copyright 2026 bararck")
        except (OSError, UnicodeError) as exc:
            errors.append(f"lisensi tidak terbaca: {type(exc).__name__}")
    paths = []
    def walk_error(exc):
        errors.append(f"direktori tidak terbaca: {type(exc).__name__}")

    for directory, dirs, files in os.walk(root, topdown=True, onerror=walk_error, followlinks=False):
        base = Path(directory)
        dirs[:] = [name for name in dirs
                   if name not in {".git", "__pycache__"} or (base / name).is_symlink()]
        paths.extend(base / name for name in dirs + files)
    for path in sorted(paths):
        if path.is_symlink():
            errors.append(f"symlink tidak diizinkan: {path.relative_to(root)}")
            continue
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"teks tidak terbaca: {path.name}: {type(exc).__name__}")
            continue
        if any(marker in text.lower() for marker in PRIVATE_MARKERS):
            errors.append(f"penanda sumber/path privat: {path.relative_to(root)}")
        if LOCAL_PATH.search(text):
            errors.append(f"path lokal absolut: {path.relative_to(root)}")
        if path.suffix.lower() == ".md":
            try:
                errors.extend(link_errors(root, path, text))
            except (OSError, ValueError, UnicodeError) as exc:
                errors.append(f"tautan tidak dapat diperiksa: {path.name}: {type(exc).__name__}")
        if path == root / SKILL:
            errors.extend(metadata_errors(text))
    return errors


def result_is_clean(result: unittest.TestResult, expected: int) -> bool:
    return (
        expected > 0 and result.testsRun == expected and result.wasSuccessful()
        and not result.skipped and not result.unexpectedSuccesses
        and not result.expectedFailures and not result.errors and not result.failures
        and not result.shouldStop
    )


def negative_is_expected(result: unittest.TestResult) -> bool:
    return (result.testsRun == 9 and len(result.failures) == 8
            and not result.errors and not result.skipped
            and not result.unexpectedSuccesses and not result.expectedFailures
            and not result.shouldStop)


def run_negative_control() -> bool:
    previous = os.environ.get("ASIQ_LAB_IMPLEMENTATION")
    sys.path.insert(0, str(ROOT))
    try:
        os.environ["ASIQ_LAB_IMPLEMENTATION"] = "buggy"
        from labs.stateful_workflow.workflow import BuggyWorkflow
        BuggyWorkflow.shared_jobs.clear()
        suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_stateful_workflow.py")
        result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
        return negative_is_expected(result)
    finally:
        sys.path.pop(0)
        if previous is None:
            os.environ.pop("ASIQ_LAB_IMPLEMENTATION", None)
        else:
            os.environ["ASIQ_LAB_IMPLEMENTATION"] = previous


def main() -> int:
    errors = validate_package(ROOT)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    sys.path.insert(0, str(ROOT))
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    discovered = suite.countTestCases()
    if discovered != EXPECTED_TESTS:
        print(f"ERROR: ditemukan {discovered}, wajib {EXPECTED_TESTS}", file=sys.stderr)
        return 1
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result_is_clean(result, EXPECTED_TESTS):
        print("ERROR: hasil unittest tidak bersih", file=sys.stderr)
        return 1
    if not run_negative_control():
        print("ERROR: negative control tidak menunjukkan kegagalan kontrak yang diharapkan", file=sys.stderr)
        return 1
    print(f"VERIFIED: struktur dan {result.testsRun} test; negative control 8 assertion failures; bukan hasil QA aplikasi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
