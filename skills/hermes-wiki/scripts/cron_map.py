"""
Cron job mapper for Hermes Wiki.
Reads crontab safely, maps commands to scripts, detects broken paths.
READ-ONLY. NEVER MODIFIES CRONTAB.
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass
class CronEntry:
    schedule: str
    command: str
    script_path: str | None
    script_exists: bool
    owner: str = "unknown"
    logs_referenced: list[str] = field(default_factory=list)
    risk_class: str = "LOW"
    broken: bool = False
    notes: list[str] = field(default_factory=list)


CRON_RE = re.compile(
    r"^\s*([^#\s].*?)\s+([^#\s].+)$"
)

SPECIAL_RE = re.compile(
    r"^\s*@(\w+)\s+(.+)$"
)


def _extract_script_path(command: str) -> str | None:
    """Try to find a script path in a cron command."""
    # Look for python script paths
    for m in re.finditer(r'(\S+\.py)', command):
        return m.group(1)
    # Look for shell script paths
    for m in re.finditer(r'(\S+\.sh)', command):
        return m.group(1)
    # Look for absolute paths
    for m in re.finditer(r'(/\S+)', command):
        p = m.group(1)
        if Path(p).exists() or Path(p).parent.exists():
            return p
    return None


def _check_script_exists(path: str | None) -> bool:
    if not path:
        return False
    p = Path(path).expanduser()
    return p.exists() and p.is_file()


def _detect_logs(command: str) -> list[str]:
    logs = []
    for m in re.finditer(r'>>?\s*(\S+\.log)', command):
        logs.append(m.group(1))
    return logs


def _assign_risk(command: str) -> str:
    cmd_lower = command.lower()
    if any(x in cmd_lower for x in ['rm ', 'mkfs', 'dd ', 'format', 'fdisk']):
        return "DANGEROUS"
    if 'sudo' in cmd_lower or 'su -' in cmd_lower:
        return "HIGH"
    if any(x in cmd_lower for x in ['curl', 'wget', 'python', 'node']):
        return "MEDIUM"
    return "LOW"


def read_crontab(user: str | None = None) -> list[CronEntry]:
    """Read system or user crontab safely."""
    entries: list[CronEntry] = []
    cmd = ["crontab", "-l"]
    if user:
        cmd = ["sudo", "crontab", "-l", "-u", user]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return entries
        lines = result.stdout.splitlines()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return entries

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        schedule = ""
        command = ""

        # Try special syntax @daily, @hourly etc.
        m = SPECIAL_RE.match(line)
        if m:
            schedule = f"@{m.group(1)}"
            command = m.group(2)
        else:
            # Standard 5-field cron
            parts = line.split()
            if len(parts) >= 6:
                schedule = " ".join(parts[:5])
                command = " ".join(parts[5:])
            elif len(parts) >= 2:
                schedule = parts[0]
                command = " ".join(parts[1:])
            else:
                continue

        script_path = _extract_script_path(command)
        script_exists = _check_script_exists(script_path)
        logs = _detect_logs(command)
        risk = _assign_risk(command)
        broken = bool(script_path and not script_exists)

        notes = []
        if broken:
            notes.append(f"BROKEN_PATH: {script_path} not found")
        if not script_path:
            notes.append("NO_SCRIPT_DETECTED")

        entries.append(CronEntry(
            schedule=schedule,
            command=command,
            script_path=script_path,
            script_exists=script_exists,
            logs_referenced=logs,
            risk_class=risk,
            broken=broken,
            notes=notes,
        ))

    return entries


def read_system_cron_dirs() -> list[CronEntry]:
    """Read /etc/cron.d, /etc/cron.daily, etc."""
    entries: list[CronEntry] = []
    cron_dirs = ["/etc/cron.d", "/etc/cron.daily", "/etc/cron.hourly",
                 "/etc/cron.weekly", "/etc/cron.monthly"]

    for cron_dir in cron_dirs:
        p = Path(cron_dir)
        if not p.exists():
            continue
        for fpath in p.iterdir():
            if fpath.name.startswith("."):
                continue
            if fpath.is_file():
                # For cron.d files, parse as crontab
                if cron_dir == "/etc/cron.d":
                    try:
                        text = fpath.read_text(encoding="utf-8", errors="replace")
                        for line in text.splitlines():
                            line = line.strip()
                            if not line or line.startswith("#"):
                                continue
                            parts = line.split()
                            if len(parts) >= 7:
                                schedule = " ".join(parts[:5])
                                command = " ".join(parts[6:])
                                script_path = _extract_script_path(command)
                                script_exists = _check_script_exists(script_path)
                                entries.append(CronEntry(
                                    schedule=schedule,
                                    command=command,
                                    script_path=script_path,
                                    script_exists=script_exists,
                                    broken=bool(script_path and not script_exists),
                                    notes=["SYSTEM_CRON_D"] if not (script_path and not script_exists) else [f"BROKEN_PATH: {script_path}"],
                                    risk_class=_assign_risk(command),
                                ))
                    except (OSError, PermissionError):
                        continue
                else:
                    # For cron.daily etc, the file itself is the script
                    entries.append(CronEntry(
                        schedule=cron_dir.split("/")[-1],
                        command=str(fpath),
                        script_path=str(fpath),
                        script_exists=True,
                        notes=["SYSTEM_CRON_DIR"],
                        risk_class="MEDIUM",
                    ))

    return entries


def build_cron_map() -> list[CronEntry]:
    """Build complete cron map from all sources."""
    entries = []
    entries.extend(read_crontab())
    entries.extend(read_system_cron_dirs())
    return entries


def format_cron_table(entries: list[CronEntry]) -> str:
    """Format cron entries as markdown table."""
    lines = [
        "| Schedule | Script | Exists | Risk | Broken | Notes |",
        "|----------|--------|--------|------|--------|-------|",
    ]
    for e in entries:
        script = e.script_path or "N/A"
        exists = "YES" if e.script_exists else "NO"
        broken = "YES" if e.broken else "NO"
        notes = "; ".join(e.notes) if e.notes else "-"
        lines.append(
            f"| {e.schedule} | {script} | {exists} | {e.risk_class} | {broken} | {notes} |"
        )
    return "\n".join(lines)
