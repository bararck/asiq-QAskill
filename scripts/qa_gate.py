"""Gate opsional bukti QA aplikasi; stdlib, read-only, tanpa eksekusi command."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys


class Invalid(ValueError):
    """Kesalahan validasi dengan pesan statis, bukan isi input."""


def require(condition, message="schema: field atau tipe tidak valid"):
    if not condition:
        raise Invalid(message)


def fields(value, names):
    require(type(value) is dict and set(value) == set(names.split()))


def text(value):
    require(type(value) is str and bool(value.strip()))


def ids(value):
    require(type(value) is list and bool(value))
    for item in value:
        require(type(item) is str and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", item))
    require(len(value) == len(set(value)), "inventory: ID duplikat")
    return set(value)


def context(value):
    fields(value, "source_revision build_id environment config_sha256")
    for item in value.values():
        text(item)
    require(re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value["source_revision"]))
    digest(value["config_sha256"])


def digest(value):
    require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value))


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "json: key duplikat")
        result[key] = value
    return result


def load(data):
    return json.loads(data.decode("utf-8"), object_pairs_hook=unique_pairs,
                      parse_constant=lambda _: require(False, "json: konstanta tidak valid"))


def unlinked_path(path):
    """Periksa path leksikal dan semua ancestor sebelum resolve/open."""
    absolute = Path(os.path.abspath(path))
    for component in (*reversed(absolute.parents), absolute):
        info = component.lstat()
        require(not stat.S_ISLNK(info.st_mode) and not (
            getattr(info, "st_file_attributes", 0) & 0x400),
            "artifact: symlink/reparse point tidak diizinkan")
    return absolute


def artifact_digest(root, relative):
    text(relative)
    parts = relative.split("/")
    require(all(re.fullmatch(r"[A-Za-z0-9_-][A-Za-z0-9_.-]*", part)
                and part not in (".", "..") and not part.endswith(".") for part in parts),
            "artifact: path relatif tidak aman")
    root = unlinked_path(root)
    require(root.is_dir(), "artifact: root bukan direktori")
    target = unlinked_path(root.joinpath(*parts))
    require(target.resolve().is_relative_to(root.resolve()), "artifact: keluar root")
    require(stat.S_ISREG(target.lstat().st_mode), "artifact: bukan file reguler")
    with target.open("rb") as stream:
        require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), "artifact: bukan file reguler")
        result = hashlib.file_digest(stream, "sha256").hexdigest()
    unlinked_path(target)
    return result


def validate(ledger, baseline, baseline_bytes, evidence_root):
    fields(baseline, "version context requirements risks scenarios")
    fields(ledger, "version baseline_sha256 context scenarios counts")
    for document in (baseline, ledger):
        require(type(document["version"]) is int and document["version"] == 1)
        context(document["context"])
        require(type(document["scenarios"]) is list and document["scenarios"])
    require(ledger["context"] == baseline["context"], "context: tidak cocok")
    digest(ledger["baseline_sha256"])
    require(ledger["baseline_sha256"] == hashlib.sha256(baseline_bytes).hexdigest(),
            "baseline: digest tidak cocok")
    requirements, risks = ids(baseline["requirements"]), ids(baseline["risks"])
    covered_req, covered_risk = set(), set()
    for scenario in baseline["scenarios"]:
        fields(scenario, "id requirement_ids risk_ids")
        req, risk = ids(scenario["requirement_ids"]), ids(scenario["risk_ids"])
        require(req <= requirements and risk <= risks, "trace: ID asing")
        covered_req |= req
        covered_risk |= risk
    require(covered_req == requirements and covered_risk == risks, "trace: cakupan hilang")
    baseline_ids = ids([s["id"] for s in baseline["scenarios"]])
    for scenario in ledger["scenarios"]:
        fields(scenario, "id selected gap attempts")
    require(ids([s["id"] for s in ledger["scenarios"]]) == baseline_ids,
            "inventory: ID hilang atau asing")
    counts = dict(total=len(baseline_ids), selected=0, passed=0, failed=0, not_run=0)
    for scenario in ledger["scenarios"]:
        require(type(scenario["selected"]) is bool and type(scenario["gap"]) is str)
        require(type(scenario["attempts"]) is list)
        counts["selected"] += int(scenario["selected"])
        if not scenario["selected"] or not scenario["attempts"]:
            text(scenario["gap"])
            require(not scenario["attempts"])
            counts["not_run"] += 1
            continue
        require(scenario["gap"] == "")
        for attempt in scenario["attempts"]:
            fields(attempt, "id context status command oracle artifacts resolves fix")
        ids([a["id"] for a in scenario["attempts"]])
        unresolved = set()
        for attempt in scenario["attempts"]:
            context(attempt["context"])
            require(attempt["context"] == ledger["context"], "attempt: context tidak cocok")
            require(attempt["status"] in ("PASS", "FAIL"))
            command, oracle = attempt["command"], attempt["oracle"]
            fields(command, "argv exit_code status")
            require(type(command["argv"]) is list and bool(command["argv"]))
            for arg in command["argv"]:
                text(arg)
            require(type(command["exit_code"]) is int)
            require(command["status"] in ("completed", "timeout", "error"))
            fields(oracle, "expected observed verified")
            text(oracle["expected"])
            text(oracle["observed"])
            require(type(oracle["verified"]) is bool)
            if attempt["status"] == "PASS":
                require(command["status"] == "completed" and command["exit_code"] == 0
                        and oracle["verified"], "attempt: PASS tanpa oracle/command terverifikasi")
            require(type(attempt["artifacts"]) is list and bool(attempt["artifacts"]))
            paths = set()
            for artifact in attempt["artifacts"]:
                fields(artifact, "path sha256")
                text(artifact["path"])
                require(artifact["path"] not in paths, "artifact: path duplikat")
                paths.add(artifact["path"])
                digest(artifact["sha256"])
                require(artifact_digest(evidence_root, artifact["path"]) == artifact["sha256"],
                        "artifact: digest tidak cocok")
            require(type(attempt["resolves"]) is list and type(attempt["fix"]) is str)
            if attempt["resolves"]:
                resolved = ids(attempt["resolves"])
                text(attempt["fix"])
                require(attempt["status"] == "PASS" and resolved <= unresolved,
                        "history: retest bukan referensi FAIL sebelumnya")
                unresolved -= resolved
            else:
                require(attempt["fix"] == "", "history: fix tanpa retest link")
            if attempt["status"] == "FAIL":
                unresolved.add(attempt["id"])
        clean = not unresolved and scenario["attempts"][-1]["status"] == "PASS"
        counts["passed" if clean else "failed"] += 1
    fields(ledger["counts"], "total selected passed failed not_run")
    require(all(type(v) is int and v >= 0 for v in ledger["counts"].values()))
    require(ledger["counts"] == counts, "counts: tidak cocok")
    require(counts["passed"] == counts["total"], "gate: ada gap atau FAIL")


def validate_files(ledger_path: Path, baseline_path: Path, evidence_root: Path) -> list[str]:
    """Validasi fail-closed; diagnostik tidak mengandung data/path dari input."""
    try:
        baseline_bytes = Path(baseline_path).read_bytes()
        validate(load(Path(ledger_path).read_bytes()), load(baseline_bytes),
                 baseline_bytes, Path(evidence_root))
    except Invalid as exc:
        return [str(exc)]
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, RecursionError):
        return ["input: JSON, file, atau struktur tidak valid"]
    return []


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, "ERROR: argumen CLI tidak valid; gunakan --help\n")


def main(argv=None):
    parser = SafeParser(description="Gate bukti QA aplikasi (read-only)", allow_abbrev=False)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--evidence-root", required=True, type=Path)
    args = parser.parse_args(argv)
    errors = validate_files(args.ledger, args.baseline, args.evidence_root)
    for error in errors:
        print("ERROR: " + error, file=sys.stderr)
    if not errors:
        print("PASS: ledger konsisten; bukan bukti autentisitas")
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
