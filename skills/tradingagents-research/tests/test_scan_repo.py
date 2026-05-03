#!/usr/bin/env python3
"""Tests for scan_repo.py."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from scan_repo import scan_repo, find_dirs, find_files


def test_find_dirs():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "agents").mkdir()
        (root / "src" / "agents").mkdir(parents=True)
        (root / "other").mkdir()

        found = find_dirs(root, {"agents"})
        assert len(found) == 2
        assert any("src" in str(f) for f in found)


def test_find_files():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "debate.py").write_text("# debate")
        (root / "moderator.py").write_text("# moderator")
        (root / "other.py").write_text("# other")

        found = find_files(root, {"debate", "moderator"})
        assert len(found) == 2


def test_scan_repo_structure():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "README.md").write_text("# Test")
        (root / "requirements.txt").write_text("requests")
        (root / "agents").mkdir(parents=True, exist_ok=True)
        (root / "agents" / "fundamental.py").write_text("print('fundamental')", encoding="utf-8")
        (root / "agents" / "technical.py").write_text("print('technical')", encoding="utf-8")
        (root / "prompts").mkdir(parents=True, exist_ok=True)
        (root / "prompts" / "system.txt").write_text("You are an agent.", encoding="utf-8")

        result = scan_repo(str(root))
        assert "error" not in result
        assert result["total_py_files"] == 2
        assert result["readme_found"] is True
        assert result["requirements_found"] is True
        assert len(result["agents"]) == 2
        assert len(result["prompts"]) == 1


if __name__ == "__main__":
    test_find_dirs()
    test_find_files()
    test_scan_repo_structure()
    print("All scan_repo tests passed.")
