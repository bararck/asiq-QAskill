"""Optional explicit execution facts; not an application QA oracle."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import stat
from pathlib import Path
import subprocess
import sys
import time


def unlinked(path):
    """Check lexical ancestors before resolving; reject all Windows reparse points."""
    absolute = Path(os.path.abspath(path))
    for part in (*reversed(absolute.parents), absolute):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("linked path forbidden")
    return absolute


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, "ERROR: invalid invocation or unsafe context; use --help\n")


def _record(argv=None):
    parser = SafeParser(allow_abbrev=False)
    parser.add_argument("--cwd", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--timeout", required=True, type=float)
    parser.add_argument("--acknowledge-sensitive-output", required=True, action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.command[:1] != ["--"] or len(args.command) < 2:
        parser.error("explicit separator and command required")
    command = args.command[1:]
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("timeout must be finite and positive")
    if any(part.lower().rstrip(" .") == ".git" for part in args.output.parts):
        parser.error("output inside git metadata is forbidden")
    try:
        args.cwd = unlinked(args.cwd)
        args.output = unlinked(args.output)
    except (OSError, ValueError):
        parser.error("unsafe filesystem path")
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=args.cwd,
                              capture_output=True, check=True, timeout=10).stdout.decode().strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                                cwd=args.cwd, capture_output=True, check=True, timeout=10).stdout)
    args.output.mkdir(mode=0o700)
    start = time.monotonic()
    status = "completed"
    with (args.output / "stdout.bin").open("xb") as out, (args.output / "stderr.bin").open("xb") as err:
        try:
            result = subprocess.run(command, cwd=args.cwd, stdout=out, stderr=err,
                                    shell=False, timeout=args.timeout)
            exit_code = result.returncode
        except subprocess.TimeoutExpired:
            status, exit_code = "timeout", 124
        except OSError:
            status, exit_code = "error", 127
    record = {
        "format": "asiq-execution-record-v1",
        "context": {"cwd": str(args.cwd), "source_revision": revision, "dirty": dirty},
        "command": {"argv": command, "exit_code": exit_code,
                    "status": status, "duration_seconds": time.monotonic() - start},
        "streams": {name: {"path": name + ".bin", "sha256": hashlib.sha256(
            (args.output / (name + ".bin")).read_bytes()).hexdigest()}
                    for name in ("stdout", "stderr")},
    }
    with (args.output / "record.json").open("x", encoding="utf-8") as target:
        json.dump(record, target, indent=2)
        target.write("\n")
    return exit_code


def main(argv=None):
    try:
        return _record(argv)
    except (OSError, ValueError, subprocess.SubprocessError):
        print("ERROR: execution evidence could not be recorded safely", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
