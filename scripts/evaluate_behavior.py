"""Summarize reviewer judgments; v2 verifies artifact hashes and event context."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import hashlib
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DIGEST = re.compile(r"[0-9a-f]{64}\Z")


def bound_bytes(root, relative, digest):
    """Read only a nonempty, hash-bound artifact beneath an explicit evidence root."""
    if (not isinstance(relative, str) or not relative or relative.startswith("/") or ":" in relative or "\\" in relative
            or Path(relative).is_absolute() or ".." in Path(relative).parts
            or not isinstance(digest, str) or not DIGEST.fullmatch(digest)):
        raise ValueError("invalid artifact binding")
    root = Path(root).resolve(strict=True)
    target = root / relative
    if not target.is_file():
        raise ValueError("missing artifact")
    # Reject links/junctions rather than relying only on final-path containment.
    current = target
    while current != root:
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            raise ValueError("linked artifact")
        current = current.parent
    resolved = target.resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError("artifact outside root")
    data = resolved.read_bytes()
    if not data or hashlib.sha256(data).hexdigest() != digest:
        raise ValueError("artifact missing or changed")
    return data


def verify_evidence(pack, review, evidence_root, pack_bytes):
    if evidence_root is None or not isinstance(pack_bytes, bytes):
        raise ValueError("v2 requires evidence root and pack bytes")
    if review.get("pack_sha256") != hashlib.sha256(pack_bytes).hexdigest():
        raise ValueError("case pack changed")
    if json.loads(pack_bytes, object_pairs_hook=unique_object) != pack:
        raise ValueError("pack bytes do not match inventory")
    skill_hash = review.get("skill_sha256")
    bound_bytes(evidence_root, review.get("skill_file"), skill_hash)
    manifest = json.loads(bound_bytes(evidence_root, review.get("events_file"), review.get("events_sha256")),
                          object_pairs_hook=unique_object)
    if (not isinstance(manifest, dict) or type(manifest.get("version")) is not int
            or manifest["version"] != 1 or not isinstance(manifest.get("events"), list)):
        raise ValueError("invalid event manifest")
    events = {}
    for event in manifest["events"]:
        if not isinstance(event, dict) or not isinstance(event.get("id"), str) or not event["id"].strip():
            raise ValueError("invalid event")
        if event["id"] in events:
            raise ValueError("duplicate event")
        events[event["id"]] = event
    sessions = set()
    for record in review["records"]:
        session = record.get("session_id")
        if not isinstance(session, str) or not session.strip() or session in sessions:
            raise ValueError("each case requires a distinct session")
        sessions.add(session)
        if len(set(record["event_ids"])) != len(record["event_ids"]):
            raise ValueError("duplicate event reference")
        for event_id in record["event_ids"]:
            event = events.get(event_id)
            if event is None or any(event.get(key) != expected for key, expected in (
                    ("case_id", record["case_id"]), ("session_id", session),
                    ("model", review["model"]), ("skill_sha256", skill_hash))):
                raise ValueError("event context mismatch")
            artifact = event.get("artifact")
            if not isinstance(artifact, dict):
                raise ValueError("missing event artifact")
            bound_bytes(evidence_root, artifact.get("path"), artifact.get("sha256"))


def summarize(pack, review, *, evidence_root=None, pack_bytes=None):
    def require(condition):
        if not condition:
            raise ValueError("invalid evaluation")

    def text(value):
        return isinstance(value, str) and bool(value.strip())

    require(isinstance(pack, dict) and isinstance(review, dict))
    require(type(pack.get("version")) is int and pack["version"] == 1)
    require(type(review.get("version")) is int and review["version"] in (1, 2))
    for field in ("session_id", "model", "skill_revision", "reviewer"):
        require(text(review.get(field)))
    cases, records = pack.get("cases"), review.get("records")
    require(isinstance(cases, list) and bool(cases) and isinstance(records, list))
    inventory = {}
    for case in cases:
        require(isinstance(case, dict))
        require(all(text(case.get(key)) for key in ("id", "prompt", "expected")))
        require(type(case.get("small_task")) is bool)
        require(case["id"] not in inventory)
        inventory[case["id"]] = case
    dimensions = ("verdict_correct", "evidence_complete", "scope_respected", "independent_work_continued")
    summary = {key: 0 for key in dimensions}
    summary.update(cases=len(cases), scope_violations=0, redundant_questions=0, small_task_seconds=0,
                   evidence_binding_verified=False, reviewer_judgment_verified=False)
    seen = set()
    for record in records:
        require(isinstance(record, dict))
        case_id = record.get("case_id")
        require(text(case_id) and case_id in inventory and case_id not in seen)
        seen.add(case_id)
        events = record.get("event_ids")
        require(isinstance(events, list) and bool(events) and all(text(event) for event in events))
        for field in dimensions:
            require(type(record.get(field)) is bool)
            summary[field] += int(record[field])
        questions, duration = record.get("redundant_questions"), record.get("duration_seconds")
        require(type(questions) is int and questions >= 0)
        require(type(duration) in (int, float) and duration >= 0 and math.isfinite(duration))
        summary["redundant_questions"] += questions
        summary["scope_violations"] += int(not record["scope_respected"])
        if inventory[case_id]["small_task"]:
            summary["small_task_seconds"] += duration
    require(seen == set(inventory))
    if review["version"] == 2:
        verify_evidence(pack, review, evidence_root, pack_bytes)
        summary["evidence_binding_verified"] = True
    return summary


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", required=True)
    parser.add_argument("--evidence-root", help="Required for version 2 artifact/context validation")
    args = parser.parse_args()
    try:
        pack_bytes = (ROOT / "benchmarks/behavior-cases.json").read_bytes()
        pack = json.loads(pack_bytes, object_pairs_hook=unique_object)
        review = json.loads(Path(args.review).read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        summary = summarize(pack, review, evidence_root=args.evidence_root, pack_bytes=pack_bytes)
    except (OSError, ValueError, TypeError, OverflowError):
        print("ERROR: invalid or unreadable evaluation; no metrics produced", file=sys.stderr)
        return 1
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
