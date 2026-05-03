#!/usr/bin/env python3
"""Static leak detection: ensure no real identifiers in any public file."""

import sys
import re
from pathlib import Path

FORBIDDEN = ["IEK", "Tera", "Detector", "Piakhouski", "AVS.by", "ankron.by", "e-electric.ru"]
SKIP_DIRS = {"__pycache__", ".git", ".pytest_cache"}
SKIP_FILES = {"test_no_leaks.py", "test_adaptation_map.py"}  # Test files contain forbidden list itself


def scan_for_leaks(root: Path) -> list[dict]:
    leaks = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".md", ".py", ".yaml", ".yml", ".json", ".txt"}:
            continue
        if any(p.name in SKIP_DIRS for p in path.parents):
            continue
        if path.name in SKIP_FILES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for word in FORBIDDEN:
                for match in re.finditer(re.escape(word), text):
                    leaks.append({
                        "file": str(path.relative_to(root)),
                        "word": word,
                        "line": text[:match.start()].count("\n") + 1,
                    })
        except Exception:
            pass
    return leaks


def test_no_leaks_in_skill():
    root = Path(__file__).parent.parent
    leaks = scan_for_leaks(root)
    if leaks:
        for leak in leaks:
            print(f"LEAK: {leak['file']}:{leak['line']} — '{leak['word']}'", file=sys.stderr)
        assert False, f"Found {len(leaks)} forbidden identifiers in public files"


if __name__ == "__main__":
    test_no_leaks_in_skill()
    print("No leaks detected. All forbidden identifiers absent.")
