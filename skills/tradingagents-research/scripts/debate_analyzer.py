#!/usr/bin/env python3
"""
Debate flow analyzer for multi-agent LLM systems.
Extracts debate rounds, moderator logic, and consensus rules.
Read-only. No execution.
"""

import os
import sys
import re
import json
import ast
from pathlib import Path
from typing import Any


def find_debate_files(repo_path: str) -> list[Path]:
    root = Path(repo_path).expanduser().resolve()
    files = []
    keywords = {"debate", "moderator", "discussion", "consensus", "deliberation"}
    for pyfile in root.rglob("*.py"):
        if "__pycache__" in str(pyfile):
            continue
        if any(k in pyfile.stem.lower() for k in keywords):
            files.append(pyfile)
    return files


def extract_functions(source: str) -> list[dict]:
    """Extract function names and docstrings from Python source."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    funcs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            doc = ast.get_docstring(node) or ""
            funcs.append({
                "name": node.name,
                "docstring": doc[:200] if doc else "",
                "line": node.lineno,
            })
    return funcs


def extract_classes(source: str) -> list[dict]:
    """Extract class names and docstrings."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node) or ""
            classes.append({
                "name": node.name,
                "docstring": doc[:200] if doc else "",
                "line": node.lineno,
            })
    return classes


def search_patterns(source: str) -> dict[str, list[str]]:
    """Search for debate-related code patterns."""
    patterns = {
        "confidence": r'confidence|threshold|score',
        "rounds": r'round|iteration|turn',
        "vote": r'vote|consensus|agree|disagree',
        "block": r'block|reject|deny|fail',
        "escalate": r'escalate|human|manual|review',
        "memo": r'memo|report|argument|position',
    }
    results = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, source, re.IGNORECASE)
        if matches:
            results[key] = len(matches)
    return results


def analyze_file(pyfile: Path) -> dict[str, Any]:
    source = pyfile.read_text(encoding="utf-8", errors="ignore")
    return {
        "file": str(pyfile.name),
        "functions": extract_functions(source),
        "classes": extract_classes(source),
        "patterns": search_patterns(source),
        "lines": len(source.splitlines()),
    }


def print_analysis(analyses: list[dict]) -> None:
    print(f"Debate-related files found: {len(analyses)}\n")
    for a in analyses:
        print(f"=== {a['file']} ({a['lines']} lines) ===")
        print(f"Classes: {len(a['classes'])}")
        for c in a['classes']:
            print(f"  class {c['name']} (line {c['line']})")
            if c['docstring']:
                print(f"    doc: {c['docstring']}")
        print(f"Functions: {len(a['functions'])}")
        for f in a['functions'][:5]:
            print(f"  def {f['name']} (line {f['line']})")
            if f['docstring']:
                print(f"    doc: {f['docstring']}")
        if len(a['functions']) > 5:
            print(f"  ... and {len(a['functions']) - 5} more")
        print(f"Patterns detected: {a['patterns']}")
        print()


def infer_debate_flow(analyses: list[dict]) -> dict:
    """Infer debate flow from code analysis."""
    flow = {
        "has_moderator": any(
            "moderator" in c['name'].lower()
            for a in analyses for c in a['classes']
        ),
        "has_confidence_scoring": any(
            a['patterns'].get('confidence', 0) > 0
            for a in analyses
        ),
        "has_rounds": any(
            a['patterns'].get('rounds', 0) > 0
            for a in analyses
        ),
        "has_voting": any(
            a['patterns'].get('vote', 0) > 0
            for a in analyses
        ),
        "has_escalation": any(
            a['patterns'].get('escalate', 0) > 0
            for a in analyses
        ),
        "has_memos": any(
            a['patterns'].get('memo', 0) > 0
            for a in analyses
        ),
        "total_files": len(analyses),
    }
    return flow


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: debate_analyzer.py <repo_path>", file=sys.stderr)
        sys.exit(1)

    files = find_debate_files(sys.argv[1])
    analyses = [analyze_file(f) for f in files]
    print_analysis(analyses)

    flow = infer_debate_flow(analyses)
    print("=== Inferred Debate Flow ===")
    for k, v in flow.items():
        print(f"  {k}: {v}")

    json_path = Path("/tmp/tradingagents_debate.json")
    json_path.write_text(
        json.dumps({"files": analyses, "flow": flow}, indent=2, default=str),
        encoding="utf-8"
    )
    print(f"\nJSON saved: {json_path}")
