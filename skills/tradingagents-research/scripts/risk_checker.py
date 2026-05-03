#!/usr/bin/env python3
"""
Security risk checker for multi-agent LLM repositories.
Scans for hardcoded keys, real data, cloud defaults, unsafe patterns.
Read-only. No modifications.
"""

import os
import sys
import re
import ast
from pathlib import Path
from typing import Iterable

# ── Risk patterns ──
RISK_PATTERNS = {
    "api_key": re.compile(r'(api_key|apikey|api_secret|secret_key)\s*=\s*["\'][a-zA-Z0-9_-]{10,}', re.IGNORECASE),
    "token": re.compile(r'(token|access_token|auth_token)\s*=\s*["\'][a-zA-Z0-9_-]{10,}', re.IGNORECASE),
    "password": re.compile(r'(password|passwd|pwd)\s*=\s*["\'][^"\']+', re.IGNORECASE),
    "private_key": re.compile(r'-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----', re.IGNORECASE),
    "aws_key": re.compile(r'AKIA[0-9A-Z]{16}'),
    "github_token": re.compile(r'ghp_[a-zA-Z0-9]{36}'),
    "openai_key": re.compile(r'sk-[a-zA-Z0-9]{20,}'),
    "ip_address": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
    "email": re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
    "url_with_creds": re.compile(r'https?://[^:]+:[^@]+@'),
    "eval_usage": re.compile(r'\beval\s*\(', re.IGNORECASE),
    "exec_usage": re.compile(r'\bexec\s*\(', re.IGNORECASE),
    "subprocess_shell": re.compile(r'subprocess\.(run|call|Popen)\s*\([^)]*shell\s*=\s*True', re.IGNORECASE),
    "hardcoded_path": re.compile(r'/(home|Users|root)/[a-zA-Z0-9_]+', re.IGNORECASE),
}

SAFE_PATHS = {"example", "test", "mock", "fixture", "dummy", "fake"}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", "venv", ".venv"}


def is_safe_file(path: Path) -> bool:
    """Check if file is in test/example directory."""
    parts = {p.lower() for p in path.parts}
    return not parts.isdisjoint(SAFE_PATHS)


def scan_file(pyfile: Path) -> list[dict]:
    """Scan single file for risk patterns."""
    findings = []
    try:
        text = pyfile.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings

    lines = text.splitlines()
    for risk_name, pattern in RISK_PATTERNS.items():
        for lineno, line in enumerate(lines, 1):
            if pattern.search(line):
                # Skip comments and docstrings if possible
                stripped = line.strip()
                if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                    continue
                findings.append({
                    "risk": risk_name,
                    "file": str(pyfile.name),
                    "line": lineno,
                    "snippet": stripped[:100],
                })

    # AST-based checks
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return findings

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check for open() with write mode
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                if node.args and len(node.args) >= 2:
                    mode_arg = node.args[1]
                    if isinstance(mode_arg, ast.Constant) and isinstance(mode_arg.value, str):
                        if "w" in mode_arg.value or "a" in mode_arg.value:
                            findings.append({
                                "risk": "file_write",
                                "file": str(pyfile.name),
                                "line": node.lineno,
                                "snippet": f"open(..., '{mode_arg.value}')",
                            })

    return findings


def scan_repo(repo_path: str) -> dict:
    root = Path(repo_path).expanduser().resolve()
    if not root.exists():
        return {"error": f"Path not found: {root}"}

    all_findings = []
    files_scanned = 0

    for pyfile in root.rglob("*.py"):
        if any(p.name in SKIP_DIRS for p in pyfile.parents):
            continue
        if is_safe_file(pyfile):
            continue
        files_scanned += 1
        findings = scan_file(pyfile)
        all_findings.extend(findings)

    # Categorize
    critical = [f for f in all_findings if f["risk"] in {"api_key", "token", "password", "private_key", "aws_key", "github_token", "openai_key"}]
    high = [f for f in all_findings if f["risk"] in {"eval_usage", "exec_usage", "subprocess_shell", "url_with_creds"}]
    medium = [f for f in all_findings if f["risk"] in {"ip_address", "email", "hardcoded_path"}]
    low = [f for f in all_findings if f["risk"] == "file_write"]

    return {
        "repo_path": str(root),
        "files_scanned": files_scanned,
        "total_findings": len(all_findings),
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
    }


def print_report(report: dict) -> None:
    if "error" in report:
        print(f"ERROR: {report['error']}", file=sys.stderr)
        sys.exit(1)

    print(f"Repository: {report['repo_path']}")
    print(f"Files scanned: {report['files_scanned']}")
    print(f"Total findings: {report['total_findings']}")
    print()

    for level, findings in [("CRITICAL", report["critical"]), ("HIGH", report["high"]), ("MEDIUM", report["medium"]), ("LOW", report["low"])]:
        print(f"=== {level}: {len(findings)} ===")
        for f in findings[:10]:
            print(f"  [{f['risk']}] {f['file']}:{f['line']} — {f['snippet']}")
        if len(findings) > 10:
            print(f"  ... and {len(findings) - 10} more")
        print()

    if report["total_findings"] == 0:
        print("No risks detected.")
    elif len(report["critical"]) > 0:
        print("EXIT: Critical risks found. Review before any adaptation.")
        sys.exit(2)
    elif len(report["high"]) > 0:
        print("WARNING: High risks found. Review recommended.")
        sys.exit(1)
    else:
        print("OK: No critical or high risks.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: risk_checker.py <repo_path>", file=sys.stderr)
        sys.exit(1)

    report = scan_repo(sys.argv[1])
    print_report(report)
