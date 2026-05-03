"""
Server intelligence for Hermes Wiki.
Collects system health, load ranking, garbage map.
READ-ONLY. NEVER MODIFIES SYSTEM.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable


@dataclass
class ServerHealth:
    hostname: str = "unknown"
    uptime: str = "unknown"
    load_avg: list[float] = field(default_factory=list)
    cpu_count: int = 0
    ram_total_mb: int = 0
    ram_used_mb: int = 0
    ram_free_mb: int = 0
    swap_total_mb: int = 0
    swap_used_mb: int = 0
    disk_mounts: list[dict] = field(default_factory=list)
    inode_usage: list[dict] = field(default_factory=list)
    top_cpu_processes: list[dict] = field(default_factory=list)
    top_ram_processes: list[dict] = field(default_factory=list)
    failed_systemd_services: list[str] = field(default_factory=list)
    docker_containers: list[dict] = field(default_factory=list)
    docker_disk_usage: dict = field(default_factory=dict)
    journalctl_size_mb: float = 0.0
    listening_ports: list[dict] = field(default_factory=list)
    crontab_summary: str = ""


def _run(cmd: list[str], timeout: int = 10) -> str:
    """Run shell command safely. Returns empty string on failure."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout if result.returncode == 0 else ""
    except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
        return ""


def collect_server_health() -> ServerHealth:
    """Collect comprehensive server health data."""
    health = ServerHealth()

    # Hostname
    health.hostname = _run(["hostname"]).strip() or "unknown"

    # Uptime
    health.uptime = _run(["uptime", "-p"]).strip() or _run(["uptime"]).strip() or "unknown"

    # Load average
    load_text = _run(["cat", "/proc/loadavg"])
    if load_text:
        parts = load_text.split()
        if len(parts) >= 3:
            health.load_avg = [float(parts[0]), float(parts[1]), float(parts[2])]

    # CPU count
    cpu_info = _run(["nproc"])
    if cpu_info:
        try:
            health.cpu_count = int(cpu_info.strip())
        except ValueError:
            pass

    # RAM
    mem_info = _run(["cat", "/proc/meminfo"])
    if mem_info:
        mem_total = 0
        mem_avail = 0
        swap_total = 0
        swap_free = 0
        for line in mem_info.splitlines():
            if line.startswith("MemTotal:"):
                mem_total = int(line.split()[1]) // 1024
            elif line.startswith("MemAvailable:"):
                mem_avail = int(line.split()[1]) // 1024
            elif line.startswith("SwapTotal:"):
                swap_total = int(line.split()[1]) // 1024
            elif line.startswith("SwapFree:"):
                swap_free = int(line.split()[1]) // 1024
        health.ram_total_mb = mem_total
        health.ram_used_mb = mem_total - mem_avail
        health.ram_free_mb = mem_avail
        health.swap_total_mb = swap_total
        health.swap_used_mb = swap_total - swap_free

    # Disk usage
    df_text = _run(["df", "-h"])
    for line in df_text.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 6:
            health.disk_mounts.append({
                "filesystem": parts[0],
                "size": parts[1],
                "used": parts[2],
                "available": parts[3],
                "use_percent": parts[4],
                "mount": parts[5],
            })

    # Inode usage
    df_i_text = _run(["df", "-i"])
    for line in df_i_text.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 6:
            health.inode_usage.append({
                "filesystem": parts[0],
                "inodes": parts[1],
                "iused": parts[2],
                "ifree": parts[3],
                "iuse_percent": parts[4],
                "mount": parts[5],
            })

    # Top CPU processes
    ps_text = _run(["ps", "aux", "--sort=-%cpu"])
    for line in ps_text.splitlines()[1:11]:
        parts = line.split()
        if len(parts) >= 11:
            health.top_cpu_processes.append({
                "user": parts[0],
                "pid": parts[1],
                "cpu": parts[2],
                "mem": parts[3],
                "command": " ".join(parts[10:])[:60],
            })

    # Top RAM processes
    ps_ram_text = _run(["ps", "aux", "--sort=-%mem"])
    for line in ps_ram_text.splitlines()[1:11]:
        parts = line.split()
        if len(parts) >= 11:
            health.top_ram_processes.append({
                "user": parts[0],
                "pid": parts[1],
                "cpu": parts[2],
                "mem": parts[3],
                "command": " ".join(parts[10:])[:60],
            })

    # Failed systemd services
    failed_text = _run(["systemctl", "--failed", "--no-pager", "--no-legend"])
    for line in failed_text.splitlines():
        parts = line.split()
        if parts:
            health.failed_systemd_services.append(parts[0])

    # Docker containers
    docker_ps = _run(["docker", "ps", "-a", "--format", "{{json .}}"])
    for line in docker_ps.splitlines():
        try:
            health.docker_containers.append(json.loads(line))
        except json.JSONDecodeError:
            pass

    # Docker disk usage
    docker_df = _run(["docker", "system", "df"])
    health.docker_disk_usage["raw"] = docker_df

    # Journalctl size
    journal_size = _run(["journalctl", "--disk-usage"])
    if journal_size:
        m = re.search(r"(\d+(?:\.\d+)?)\s*([KMGT]?)B", journal_size)
        if m:
            val = float(m.group(1))
            unit = m.group(2)
            mult = {"K": 1/1024, "M": 1, "G": 1024, "T": 1024*1024, "": 1/1024/1024}
            health.journalctl_size_mb = val * mult.get(unit, 1)

    # Listening ports
    ss_text = _run(["ss", "-tlnp"])
    for line in ss_text.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 6:
            health.listening_ports.append({
                "state": parts[0],
                "recv_q": parts[1],
                "send_q": parts[2],
                "local": parts[3],
                "peer": parts[4],
                "process": " ".join(parts[5:]),
            })

    # Crontab summary
    crontab = _run(["crontab", "-l"])
    lines = [l for l in crontab.splitlines() if l.strip() and not l.strip().startswith("#")]
    health.crontab_summary = f"{len(lines)} active entries"

    return health


def format_health_markdown(health: ServerHealth) -> str:
    """Format server health as markdown report."""
    lines = [
        "# Server Health Report",
        f"**Generated:** {datetime.now().isoformat()}",
        f"**Hostname:** {health.hostname}",
        "",
        "## System",
        f"- **Uptime:** {health.uptime}",
        f"- **Load Average:** {', '.join(str(x) for x in health.load_avg)}",
        f"- **CPU Cores:** {health.cpu_count}",
        "",
        "## Memory",
        f"- **RAM:** {health.ram_used_mb}MB / {health.ram_total_mb}MB used",
        f"- **Swap:** {health.swap_used_mb}MB / {health.swap_total_mb}MB used",
        "",
        "## Disk Usage",
        "| Filesystem | Size | Used | Avail | Use% | Mount |",
        "|------------|------|------|-------|------|-------|",
    ]
    for d in health.disk_mounts:
        lines.append(
            f"| {d['filesystem']} | {d['size']} | {d['used']} | {d['available']} | {d['use_percent']} | {d['mount']} |"
        )

    lines.extend([
        "",
        "## Top CPU Processes",
        "| PID | CPU% | MEM% | Command |",
        "|-----|------|------|---------|",
    ])
    for p in health.top_cpu_processes:
        lines.append(f"| {p['pid']} | {p['cpu']} | {p['mem']} | {p['command']} |")

    lines.extend([
        "",
        "## Top RAM Processes",
        "| PID | CPU% | MEM% | Command |",
        "|-----|------|------|---------|",
    ])
    for p in health.top_ram_processes:
        lines.append(f"| {p['pid']} | {p['cpu']} | {p['mem']} | {p['command']} |")

    if health.failed_systemd_services:
        lines.extend(["", "## Failed Systemd Services", ""])
        for svc in health.failed_systemd_services:
            lines.append(f"- {svc}")
    else:
        lines.extend(["", "## Failed Systemd Services", "None detected", ""])

    lines.extend([
        "",
        "## Docker",
        f"- **Containers:** {len(health.docker_containers)} total",
        f"- **Journal Size:** {health.journalctl_size_mb:.1f} MB",
        "",
        "## Listening Ports",
        "| State | Local | Process |",
        "|-------|-------|---------|",
    ])
    for p in health.listening_ports[:20]:
        lines.append(f"| {p['state']} | {p['local']} | {p['process']} |")

    return "\n".join(lines)
