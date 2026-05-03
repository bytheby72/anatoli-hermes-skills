#!/usr/bin/env python3
"""
Repository structure scanner for multi-agent LLM systems.
Read-only. No network calls. No data modification.
"""

import os
import sys
import json
from pathlib import Path
from typing import Iterable

# ── Config ──
AGENT_DIRS = {"agents", "agent", "src/agents", "core/agents"}
PROMPT_DIRS = {"prompts", "prompt", "src/prompts", "config/prompts"}
DEBATE_FILES = {"debate", "moderator", "discussion", "consensus"}
EXEC_FILES = {"execution", "executor", "trade", "action"}
CONFIG_FILES = {"config", "settings", "env"}

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", "venv", ".venv"}


def find_dirs(root: Path, names: set[str]) -> list[Path]:
    """Find directories matching any of the given names."""
    found = []
    for path in root.rglob("*"):
        if path.is_dir() and path.name in names and not any(p.name in SKIP_DIRS for p in path.parents):
            found.append(path)
    return found


def find_files(root: Path, patterns: set[str]) -> list[Path]:
    """Find files whose stem contains any of the patterns."""
    found = []
    for path in root.rglob("*.py"):
        if any(p in path.stem.lower() for p in patterns):
            if not any(p.name in SKIP_DIRS for p in path.parents):
                found.append(path)
    return found


def count_lines(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
    except Exception:
        return 0


def scan_repo(repo_path: str) -> dict:
    root = Path(repo_path).expanduser().resolve()
    if not root.exists():
        return {"error": f"Path not found: {root}"}

    result = {
        "repo_path": str(root),
        "total_py_files": 0,
        "total_lines": 0,
        "agents": [],
        "prompts": [],
        "debate_modules": [],
        "execution_modules": [],
        "config_modules": [],
        "readme_found": False,
        "requirements_found": False,
    }

    for path in root.rglob("*.py"):
        if any(p.name in SKIP_DIRS for p in path.parents):
            continue
        result["total_py_files"] += 1
        result["total_lines"] += count_lines(path)

    result["readme_found"] = (root / "README.md").exists() or (root / "README.rst").exists()
    result["requirements_found"] = (root / "requirements.txt").exists()

    for d in find_dirs(root, AGENT_DIRS):
        for f in d.glob("*.py"):
            result["agents"].append({"file": str(f.relative_to(root)), "lines": count_lines(f)})

    for d in find_dirs(root, PROMPT_DIRS):
        for f in d.glob("*"):
            if f.is_file():
                result["prompts"].append({"file": str(f.relative_to(root)), "size": f.stat().st_size})

    for f in find_files(root, DEBATE_FILES):
        result["debate_modules"].append(str(f.relative_to(root)))

    for f in find_files(root, EXEC_FILES):
        result["execution_modules"].append(str(f.relative_to(root)))

    for f in find_files(root, CONFIG_FILES):
        result["config_modules"].append(str(f.relative_to(root)))

    return result


def print_summary(data: dict) -> None:
    if "error" in data:
        print(f"ERROR: {data['error']}", file=sys.stderr)
        sys.exit(1)

    print(f"Repository: {data['repo_path']}")
    print(f"Python files: {data['total_py_files']}")
    print(f"Total lines: {data['total_lines']}")
    print(f"README: {'yes' if data['readme_found'] else 'no'}")
    print(f"requirements.txt: {'yes' if data['requirements_found'] else 'no'}")
    print()

    print(f"Agents found: {len(data['agents'])}")
    for a in data["agents"]:
        print(f"  - {a['file']} ({a['lines']} lines)")
    print()

    print(f"Prompts found: {len(data['prompts'])}")
    for p in data["prompts"]:
        print(f"  - {p['file']} ({p['size']} bytes)")
    print()

    print(f"Debate modules: {len(data['debate_modules'])}")
    for m in data["debate_modules"]:
        print(f"  - {m}")
    print()

    print(f"Execution modules: {len(data['execution_modules'])}")
    for m in data["execution_modules"]:
        print(f"  - {m}")
    print()

    print(f"Config modules: {len(data['config_modules'])}")
    for m in data["config_modules"]:
        print(f"  - {m}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: scan_repo.py <repo_path>", file=sys.stderr)
        sys.exit(1)

    data = scan_repo(sys.argv[1])
    print_summary(data)

    # Also write JSON for downstream tools
    json_path = Path("/tmp/tradingagents_scan.json")
    json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"\nJSON saved: {json_path}")
