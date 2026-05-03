"""
Garbage map for Hermes Wiki.
Finds cleanup candidates, assigns risk classes.
NEVER DELETES ANYTHING. READ-ONLY.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable


@dataclass
class GarbageEntry:
    candidate: str
    path: str
    size: str
    last_modified: str
    risk_class: str
    reason: str
    check_command: str
    cleanup_command: str
    manual_approval_required: bool = True


SAFE_TEMP_PATTERNS = [
    "__pycache__", "*.pyc", ".pytest_cache",
    "*.egg-info", "build", "dist", ".tox",
]

REVIEW_PATTERNS = [
    "*.log", "*.bak", "*.old", "*.tmp",
    "report_*", "snapshot_*", "backup_*",
]

DANGEROUS_PATTERNS = [
    "/var/log", "/var/lib", "/etc",
    ".git", ".gnupg",
]

SECRET_PATTERNS = [
    "secret", "private", "credential", "token",
    "auth", "cookie", "session", "confidential",
]


def _run(cmd: list[str], timeout: int = 30) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
        return ""


def _classify_path(path: str) -> str:
    p_lower = path.lower()
    for pat in SECRET_PATTERNS:
        if pat in p_lower:
            return "SECRET_OR_UNKNOWN"
    for pat in DANGEROUS_PATTERNS:
        if p_lower.startswith(pat) or pat in p_lower:
            return "DANGEROUS"
    for pat in REVIEW_PATTERNS:
        if pat.replace("*", "") in p_lower:
            return "REVIEW_FIRST"
    for pat in SAFE_TEMP_PATTERNS:
        if pat.replace("*", "") in p_lower:
            return "SAFE_CLEAN"
    # Old temp files
    if "/tmp/" in p_lower or "/var/tmp/" in p_lower:
        return "REVIEW_FIRST"
    return "REVIEW_FIRST"


def _parse_size(size_str: str) -> str:
    return size_str.strip().split()[0] if size_str.strip() else "unknown"


def find_pycache(root: str = "~") -> list[GarbageEntry]:
    entries = []
    root_p = Path(root).expanduser()
    text = _run(["find", str(root_p), "-type", "d", "-name", "__pycache__"])
    for line in text.splitlines()[:50]:
        if not line.strip():
            continue
        p = Path(line.strip())
        size = _run(["du", "-sh", str(p)])
        entries.append(GarbageEntry(
            candidate="pycache_dir",
            path=str(p),
            size=_parse_size(size),
            last_modified=datetime.fromtimestamp(p.stat().st_mtime).isoformat() if p.exists() else "unknown",
            risk_class="SAFE_CLEAN",
            reason="Python cache, easily regenerated",
            check_command=f"du -sh {p}",
            cleanup_command=f"find {p.parent} -type d -name __pycache__ -exec rm -rf {{}} +",
            manual_approval_required=True,
        ))
    return entries


def find_old_tmp(days: int = 7) -> list[GarbageEntry]:
    entries = []
    cutoff = datetime.now() - timedelta(days=days)
    for tmp_dir in ["/tmp", "/var/tmp"]:
        text = _run(["find", tmp_dir, "-type", "f", "-atime", f"+{days}"])
        for line in text.splitlines()[:30]:
            if not line.strip():
                continue
            p = Path(line.strip())
            try:
                mtime = datetime.fromtimestamp(p.stat().st_mtime)
                size = _run(["du", "-sh", str(p)])
                risk = "SAFE_CLEAN" if mtime < cutoff else "REVIEW_FIRST"
                entries.append(GarbageEntry(
                    candidate="old_temp_file",
                    path=str(p),
                    size=_parse_size(size),
                    last_modified=mtime.isoformat(),
                    risk_class=risk,
                    reason=f"Temp file not accessed in {days} days",
                    check_command=f"ls -la {p}",
                    cleanup_command=f"rm -f {p}",
                    manual_approval_required=True,
                ))
            except (OSError, PermissionError):
                continue
    return entries


def find_docker_garbage() -> list[GarbageEntry]:
    entries = []
    # Dangling images
    dangling = _run(["docker", "images", "-f", "dangling=true", "-q"])
    if dangling.strip():
        count = len(dangling.strip().splitlines())
        entries.append(GarbageEntry(
            candidate="dangling_docker_images",
            path="docker images",
            size="unknown",
            last_modified="unknown",
            risk_class="SAFE_CLEAN",
            reason=f"{count} dangling images, not referenced by any tag",
            check_command="docker images -f dangling=true",
            cleanup_command="docker image prune -f",
            manual_approval_required=True,
        ))
    # Stopped containers
    stopped = _run(["docker", "ps", "-a", "-f", "status=exited", "-q"])
    if stopped.strip():
        count = len(stopped.strip().splitlines())
        entries.append(GarbageEntry(
            candidate="stopped_docker_containers",
            path="docker containers",
            size="unknown",
            last_modified="unknown",
            risk_class="REVIEW_FIRST",
            reason=f"{count} stopped containers",
            check_command="docker ps -a -f status=exited",
            cleanup_command="docker container prune -f",
            manual_approval_required=True,
        ))
    return entries


def find_large_logs(min_size_mb: int = 100) -> list[GarbageEntry]:
    entries = []
    text = _run(["find", "/var/log", "-type", "f", "-size", f"+{min_size_mb}M"])
    for line in text.splitlines()[:20]:
        if not line.strip():
            continue
        p = Path(line.strip())
        try:
            size = p.stat().st_size
            entries.append(GarbageEntry(
                candidate="large_log_file",
                path=str(p),
                size=f"{size // (1024*1024)}MB",
                last_modified=datetime.fromtimestamp(p.stat().st_mtime).isoformat(),
                risk_class="DANGEROUS",
                reason="Large log file, may be needed for debugging",
                check_command=f"ls -la {p}",
                cleanup_command=f"# MANUAL: truncate or rotate {p}",
                manual_approval_required=True,
            ))
        except (OSError, PermissionError):
            continue
    return entries


def find_broken_symlinks(root: str = "~") -> list[GarbageEntry]:
    entries = []
    root_p = Path(root).expanduser()
    text = _run(["find", str(root_p), "-xtype", "l"])
    for line in text.splitlines()[:30]:
        if not line.strip():
            continue
        p = Path(line.strip())
        entries.append(GarbageEntry(
            candidate="broken_symlink",
            path=str(p),
            size="0",
            last_modified="unknown",
            risk_class="SAFE_CLEAN",
            reason="Broken symlink, target does not exist",
            check_command=f"ls -la {p}",
            cleanup_command=f"rm {p}",
            manual_approval_required=True,
        ))
    return entries


def find_old_node_modules(root: str = "~") -> list[GarbageEntry]:
    entries = []
    root_p = Path(root).expanduser()
    text = _run(["find", str(root_p), "-type", "d", "-name", "node_modules"])
    for line in text.splitlines()[:20]:
        if not line.strip():
            continue
        p = Path(line.strip())
        try:
            mtime = datetime.fromtimestamp(p.stat().st_mtime)
            age_days = (datetime.now() - mtime).days
            size = _run(["du", "-sh", str(p)])
            risk = "REVIEW_FIRST" if age_days < 30 else "SAFE_CLEAN"
            entries.append(GarbageEntry(
                candidate="node_modules",
                path=str(p),
                size=_parse_size(size),
                last_modified=mtime.isoformat(),
                risk_class=risk,
                reason=f"node_modules, age {age_days} days",
                check_command=f"du -sh {p} && ls -la {p}/.. | head",
                cleanup_command=f"rm -rf {p}",
                manual_approval_required=True,
            ))
        except (OSError, PermissionError):
            continue
    return entries


def build_garbage_map() -> list[GarbageEntry]:
    """Build complete garbage map from all sources."""
    entries = []
    entries.extend(find_pycache())
    entries.extend(find_old_tmp())
    entries.extend(find_docker_garbage())
    entries.extend(find_large_logs())
    entries.extend(find_broken_symlinks())
    entries.extend(find_old_node_modules())
    return entries


def format_garbage_table(entries: list[GarbageEntry]) -> str:
    lines = [
        "| Candidate | Path | Size | Risk | Reason | Check Command | Cleanup Command | Approval |",
        "|-----------|------|------|------|--------|---------------|-----------------|----------|",
    ]
    for e in entries:
        approval = "REQUIRED" if e.manual_approval_required else "OPTIONAL"
        lines.append(
            f"| {e.candidate} | {e.path} | {e.size} | {e.risk_class} | {e.reason} | "
            f"`{e.check_command}` | `{e.cleanup_command}` | {approval} |"
        )
    return "\n".join(lines)
