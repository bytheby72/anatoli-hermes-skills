"""
Load ranker for Hermes Wiki.
Ranks CPU/RAM/disk/log consumers.
READ-ONLY.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass
class LoadEntry:
    category: str
    name: str
    metric: str
    value: str
    rank: int = 0


def _run(cmd: list[str], timeout: int = 10) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout if result.returncode == 0 else ""
    except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
        return ""


def rank_cpu_processes(limit: int = 10) -> list[LoadEntry]:
    text = _run(["ps", "aux", "--sort=-%cpu"])
    entries = []
    for line in text.splitlines()[1:limit+1]:
        parts = line.split()
        if len(parts) >= 11:
            entries.append(LoadEntry(
                category="CPU",
                name=" ".join(parts[10:])[:50],
                metric="cpu_percent",
                value=parts[2],
            ))
    return entries


def rank_ram_processes(limit: int = 10) -> list[LoadEntry]:
    text = _run(["ps", "aux", "--sort=-%mem"])
    entries = []
    for line in text.splitlines()[1:limit+1]:
        parts = line.split()
        if len(parts) >= 11:
            entries.append(LoadEntry(
                category="RAM",
                name=" ".join(parts[10:])[:50],
                metric="mem_percent",
                value=parts[3],
            ))
    return entries


def rank_docker_containers() -> list[LoadEntry]:
    text = _run(["docker", "stats", "--no-stream", "--format", "{{json .}}"])
    entries = []
    for line in text.splitlines():
        try:
            data = json.loads(line)
            entries.append(LoadEntry(
                category="Docker",
                name=data.get("Name", "unknown"),
                metric="cpu/mem",
                value=f"{data.get('CPUPerc', '0%')} / {data.get('MemPerc', '0%')}",
            ))
        except json.JSONDecodeError:
            pass
    return sorted(entries, key=lambda e: float(e.value.split("/")[0].strip().rstrip("%") or 0), reverse=True)


def rank_large_directories(paths: list[str] | None = None, limit: int = 10) -> list[LoadEntry]:
    targets = paths or ["/tmp", "/var/log", "~/.hermes", "~/projects"]
    entries = []
    for tp in targets:
        p = Path(tp).expanduser()
        if not p.exists():
            continue
        text = _run(["du", "-sh", str(p)])
        if text:
            size = text.split()[0]
            entries.append(LoadEntry(
                category="Disk",
                name=str(p),
                metric="size",
                value=size,
            ))
    return sorted(entries, key=lambda e: _parse_size(e.value), reverse=True)[:limit]


def rank_large_logs(limit: int = 10) -> list[LoadEntry]:
    text = _run(["find", "/var/log", "-type", "f", "-size", "+10M"])
    entries = []
    for line in text.splitlines():
        p = Path(line)
        if p.exists():
            size = p.stat().st_size
            entries.append(LoadEntry(
                category="Log",
                name=str(p),
                metric="bytes",
                value=str(size),
            ))
    return sorted(entries, key=lambda e: int(e.value), reverse=True)[:limit]


def rank_failed_systemd() -> list[LoadEntry]:
    text = _run(["systemctl", "--failed", "--no-pager", "--no-legend"])
    entries = []
    for line in text.splitlines():
        parts = line.split()
        if parts:
            entries.append(LoadEntry(
                category="Systemd",
                name=parts[0],
                metric="status",
                value="failed",
            ))
    return entries


def _parse_size(size_str: str) -> float:
    """Parse du -sh size to bytes."""
    size_str = size_str.strip()
    if not size_str:
        return 0
    mult = {"K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}
    unit = size_str[-1].upper()
    if unit in mult:
        try:
            return float(size_str[:-1]) * mult[unit]
        except ValueError:
            return 0
    try:
        return float(size_str)
    except ValueError:
        return 0


def build_load_rank() -> list[LoadEntry]:
    """Build comprehensive load ranking."""
    all_entries = []
    all_entries.extend(rank_cpu_processes())
    all_entries.extend(rank_ram_processes())
    all_entries.extend(rank_docker_containers())
    all_entries.extend(rank_large_directories())
    all_entries.extend(rank_large_logs())
    all_entries.extend(rank_failed_systemd())
    return all_entries


def format_load_table(entries: list[LoadEntry]) -> str:
    lines = [
        "| Category | Name | Metric | Value |",
        "|----------|------|--------|-------|",
    ]
    for e in entries:
        lines.append(f"| {e.category} | {e.name} | {e.metric} | {e.value} |")
    return "\n".join(lines)
