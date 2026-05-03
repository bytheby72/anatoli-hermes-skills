"""
Safe filesystem scanner for Hermes Wiki.
Walks directories, skips secrets, extracts code structure.
READ-ONLY. LOCAL-ONLY. FAIL-CLOSED.
"""

from __future__ import annotations

import ast
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from redaction import (
    is_secret_filename,
    is_confidential_path,
    safe_read_text,
    metadata_only,
)


# ── Scan targets ──
DEFAULT_SCAN_PATHS = [
    "~/.hermes/hermes-agent",
    "~/.hermes/skills",
    "~/.hermes",
    "~/fabric",
]

# ── Extensions to scan for code ──
CODE_EXTENSIONS = {".py", ".sh", ".bash", ".js", ".ts", ".sql"}
META_EXTENSIONS = {".json", ".yaml", ".yml", ".md", ".txt", ".csv"}
SKIP_EXTENSIONS = {".pyc", ".pyo", ".so", ".dylib", ".dll", ".egg", ".whl"}


@dataclass
class FileScan:
    path: str
    metadata: dict
    file_type: str = "unknown"
    functions: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    env_vars: list[str] = field(default_factory=list)
    file_reads: list[str] = field(default_factory=list)
    file_writes: list[str] = field(default_factory=list)
    network_calls: list[str] = field(default_factory=list)
    subprocess_calls: list[str] = field(default_factory=list)
    external_services: list[str] = field(default_factory=list)
    system_mods: list[str] = field(default_factory=list)
    risk_class: str = "LOW"
    content_skipped: bool = False


# ── Pattern detectors ──
NETWORK_RE = re.compile(
    r"(requests\.[a-z]+|urllib\.request|http\.client|httpx|aiohttp|"
    r"socket\.connect|curl\b|wget\b|fetch\b)",
    re.IGNORECASE,
)

SUBPROCESS_RE = re.compile(
    r"(subprocess\.(run|call|Popen|check_output)|os\.system|"
    r"os\.popen|`[^`]+`)",
    re.IGNORECASE,
)

EXTERNAL_SERVICE_RE = re.compile(
    r"(google|gmail|drive|telegram|discord|slack|openrouter|openai|"
    r"anthropic|cloudflare|aws\b|azure|gcp|heroku)",
    re.IGNORECASE,
)

SYSTEM_MOD_RE = re.compile(
    r"(systemctl|crontab|cron\b|service\b|update-rc\.d|chkconfig|"
    r"apt\b|yum\b|pacman|dnf)",
    re.IGNORECASE,
)

FILE_READ_RE = re.compile(
    r"(open\s*\([^)]*['\"]r|read_file\(|Path\(.*\)\.read_text|"
    r"Path\(.*\)\.read_bytes|json\.load|yaml\.safe_load|csv\.reader|"
    r"pandas\.read_)",
    re.IGNORECASE,
)

FILE_WRITE_RE = re.compile(
    r"(open\s*\([^)]*['\"][wa]|write_file\(|Path\(.*\)\.write_text|"
    r"Path\(.*\)\.write_bytes|json\.dump|yaml\.dump|shutil\.(copy|move)|"
    r"os\.rename)",
    re.IGNORECASE,
)


def _extract_python_structure(text: str) -> dict:
    """Parse Python AST for functions, classes, imports."""
    result = {
        "functions": [],
        "classes": [],
        "imports": [],
    }
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return result

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            result["functions"].append(node.name)
        elif isinstance(node, ast.ClassDef):
            result["classes"].append(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                result["imports"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            result["imports"].append(mod)

    return result


def _extract_env_vars(text: str) -> list[str]:
    """Extract environment variable names (not values)."""
    vars_found = set()
    # os.environ.get("VAR") or os.environ["VAR"]
    for m in re.finditer(r'os\.environ(?:\.get)?\s*\(\s*["\']([^"\']+)["\']', text):
        vars_found.add(m.group(1))
    # os.getenv("VAR")
    for m in re.finditer(r'os\.getenv\s*\(\s*["\']([^"\']+)["\']', text):
        vars_found.add(m.group(1))
    return sorted(vars_found)


def _detect_patterns(text: str) -> dict:
    """Detect risky patterns in code text."""
    return {
        "network_calls": list(set(NETWORK_RE.findall(text))),
        "subprocess_calls": list(set(SUBPROCESS_RE.findall(text))),
        "external_services": list(set(EXTERNAL_SERVICE_RE.findall(text))),
        "system_mods": list(set(SYSTEM_MOD_RE.findall(text))),
        "file_reads": list(set(FILE_READ_RE.findall(text))),
        "file_writes": list(set(FILE_WRITE_RE.findall(text))),
    }


def _assign_risk_class(scan: FileScan) -> str:
    """Assign risk class based on detected capabilities."""
    has_network = bool(scan.network_calls or scan.subprocess_calls)
    has_file_read = bool(scan.file_reads)
    has_file_write = bool(scan.file_writes)
    has_external = bool(scan.external_services)
    has_system = bool(scan.system_mods)
    is_conf = is_confidential_path(scan.path)

    if is_conf:
        return "SECRET_OR_UNKNOWN"

    if has_file_read and has_network:
        return "HIGH"

    if has_external or has_system:
        return "MEDIUM"

    if has_file_write or has_network:
        return "MEDIUM"

    if has_file_read:
        return "LOW"

    return "LOW"


def scan_file(path: str | Path) -> FileScan | None:
    """Scan a single file safely. Returns None for unreadable files."""
    p = Path(path)
    meta = metadata_only(p)

    if not meta.get("exists"):
        return None

    ext = p.suffix.lower()
    if ext in SKIP_EXTENSIONS:
        return None

    scan = FileScan(
        path=str(p),
        metadata=meta,
        file_type=ext.lstrip(".") if ext else "unknown",
        content_skipped=meta.get("content_skipped", False),
    )

    if scan.content_skipped:
        scan.risk_class = "SECRET_OR_UNKNOWN"
        return scan

    if ext not in CODE_EXTENSIONS and ext not in META_EXTENSIONS:
        scan.risk_class = _assign_risk_class(scan)
        return scan

    text = safe_read_text(p)
    if text is None:
        scan.content_skipped = True
        scan.risk_class = "SECRET_OR_UNKNOWN"
        return scan

    if ext == ".py":
        py_struct = _extract_python_structure(text)
        scan.functions = py_struct["functions"]
        scan.classes = py_struct["classes"]
        scan.imports = py_struct["imports"]
        scan.env_vars = _extract_env_vars(text)

    patterns = _detect_patterns(text)
    scan.network_calls = patterns["network_calls"]
    scan.subprocess_calls = patterns["subprocess_calls"]
    scan.external_services = patterns["external_services"]
    scan.system_mods = patterns["system_mods"]
    scan.file_reads = patterns["file_reads"]
    scan.file_writes = patterns["file_writes"]
    scan.risk_class = _assign_risk_class(scan)

    return scan


def scan_directory(
    path: str | Path,
    exclude_patterns: Iterable[str] | None = None,
    max_files: int = 10_000,
) -> list[FileScan]:
    """
    Walk directory and scan files safely.
    Skips secret files, respects max_files limit.
    """
    p = Path(path).expanduser()
    exclude = set(exclude_patterns or [])
    results: list[FileScan] = []
    count = 0

    if not p.exists():
        return results

    for root, dirs, files in os.walk(p):
        # Filter out excluded dirs
        dirs[:] = [
            d for d in dirs
            if d not in exclude and not d.startswith(".")
        ]

        for fname in files:
            if count >= max_files:
                break
            fpath = Path(root) / fname
            if is_secret_filename(fpath):
                continue
            scanned = scan_file(fpath)
            if scanned:
                results.append(scanned)
                count += 1

    return results


def scan_all(
    paths: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
) -> list[FileScan]:
    """Scan all default Hermes paths."""
    targets = paths or DEFAULT_SCAN_PATHS
    all_results: list[FileScan] = []
    for tp in targets:
        all_results.extend(scan_directory(tp, exclude))
    return all_results
