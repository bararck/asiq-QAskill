"""Inspect installed skill files only; no runner invocation or installation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import subprocess
import shutil

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / ".agents/skills/asiq/references/skill-routing.json"
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def probe_runtime(argv, marker):
    try:
        result = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                                shell=False, timeout=8)
    except FileNotFoundError:
        return {"status": "MISSING", "exit_code": None}
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "exit_code": None}
    except (OSError, UnicodeError):
        return {"status": "ERROR", "exit_code": None}
    output = result.stdout + result.stderr
    status = "ERROR" if result.returncode else "READY" if marker in output else "INVALID_OUTPUT"
    return {"status": status, "exit_code": result.returncode,
            "output_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest()}


def check_runtimes():
    # Fixed probes only: commands are never taken from SKILL.md or JSON.
    git = shutil.which("git")
    bash = shutil.which("bash")
    if sys.platform == "win32" and git:
        git_bash = Path(git).parent / "bash.exe"
        if git_bash.is_file():
            bash = str(git_bash)
    probes = {"git": probe_runtime([git or "git", "--version"], "git version"),
              "node": probe_runtime([shutil.which("node") or "node", "--version"], "v"),
              "graphify": probe_runtime([shutil.which("graphify") or "graphify", "--version"], "graphify"),
              "bash": probe_runtime([bash or "bash", "--version"], "GNU bash")}
    preamble = Path.home() / ".codex/skills/gstack/bin/gstack-skill-start"
    probes["gstack_preamble_syntax"] = (probe_runtime([bash or "bash", "-n", str(preamble)], "")
                                         if preamble.is_file() else {"status": "MISSING", "exit_code": None})
    return {"coverage": "version-and-syntax-only", "probes": probes}


def inspect_skills(catalog, roots):
    if not isinstance(catalog, dict) or type(catalog.get("version")) is not int or catalog["version"] != 1:
        raise ValueError("invalid catalog version")
    routes = catalog.get("routes")
    if not isinstance(routes, list) or not routes:
        raise ValueError("empty catalog")
    seen = set()
    for route in routes:
        if not isinstance(route, dict):
            raise ValueError("invalid route")
        for field in ("id", "purpose", "fallback"):
            if not isinstance(route.get(field), str) or not route[field].strip():
                raise ValueError("missing route field")
        if route["id"] in seen:
            raise ValueError("duplicate route")
        seen.add(route["id"])
        candidates = route.get("candidates")
        if (not isinstance(candidates, list) or not candidates
                or any(not isinstance(name, str) or not NAME.fullmatch(name) for name in candidates)
                or len(set(candidates)) != len(candidates)):
            raise ValueError("invalid candidate")
    skill_roots = list(dict.fromkeys(Path(root).resolve() for root in roots))
    result = []
    for route in routes:
        item = {"id": route["id"], "status": "MISSING", "selected": None,
                "sha256": None, "runtime": "NOT_CHECKED", "fallback": route["fallback"]}
        for name in route["candidates"]:
            relative_paths = [Path(name) / "SKILL.md"]
            if name.startswith("gstack-"):
                relative_paths.append(Path("gstack") / name.removeprefix("gstack-") / "SKILL.md")
            for root in skill_roots:
                for relative in relative_paths:
                    target = root / relative
                    try:
                        if not target.resolve().is_relative_to(root):
                            item["status"] = "UNSAFE_PATH"
                            continue
                        if not target.is_file():
                            continue
                        content = target.read_bytes()
                        if not content.decode("utf-8-sig").strip():
                            item["status"] = "UNREADABLE"
                            continue
                        item.update(status="FOUND", selected=name,
                                    sha256=hashlib.sha256(content).hexdigest())
                        break
                    except (OSError, UnicodeError, RuntimeError):
                        item["status"] = "UNREADABLE"
                if item["selected"]:
                    break
            if item["selected"]:
                break
        result.append(item)
    return {"version": 1, "routes": result}


def default_roots():
    home = Path.home()
    roots = [Path.cwd() / ".agents/skills", home / ".codex/skills", home / ".agents/skills"]
    # Versioned Superpowers cache is a skill root, not the active Python environment.
    cache = home / ".codex/plugins/cache/openai-api-curated/superpowers"
    if cache.is_dir():
        roots.extend(sorted(cache.glob("*/skills"), reverse=True))
    return roots


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", help="Explicit skill root; repeat for multiple roots")
    parser.add_argument("--check-runtime", action="store_true", help="Run fixed, bounded version/syntax probes")
    args = parser.parse_args()
    try:
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        report = inspect_skills(catalog, args.root if args.root is not None else default_roots())
        if args.check_runtime:
            report["runtime_checks"] = check_runtimes()
    except (OSError, ValueError, RuntimeError):
        print("ERROR: skill catalog or roots could not be inspected", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
