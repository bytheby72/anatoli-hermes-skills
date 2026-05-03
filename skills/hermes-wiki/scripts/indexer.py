"""
Local indexer for Hermes Wiki.
Builds searchable index from scans. Stores ONLY locally.
NO external uploads. NO remote vector DB.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from scanner import FileScan, scan_directory
from cron_map import CronEntry, build_cron_map
from skill_map import SkillInfo, scan_skill_dir
from trust_map import TrustEntry, build_trust_map


INDEX_DIR = Path("~/.hermes/wiki/index").expanduser()
REPORTS_DIR = Path("~/.hermes/wiki/reports").expanduser()
SNAPSHOTS_DIR = Path("~/.hermes/wiki/snapshots").expanduser()


def ensure_dirs():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def save_index(name: str, data: list[dict]):
    ensure_dirs()
    path = INDEX_DIR / f"{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def load_index(name: str) -> list[dict]:
    path = INDEX_DIR / f"{name}.json"
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_all_indexes():
    """Build all indexes from live scans."""
    ensure_dirs()

    # Code index - limit scan to avoid timeout
    scans = scan_directory("~/.hermes/skills", max_files=2000)
    save_index("code", [_scan_to_dict(s) for s in scans])

    # Cron index
    cron_entries = build_cron_map()
    save_index("cron", [_cron_to_dict(e) for e in cron_entries])

    # Skill index
    skills = scan_skill_dir()
    save_index("skills", [_skill_to_dict(s) for s in skills])

    # Trust index
    trust_entries = build_trust_map(scans)
    save_index("trust", [_trust_to_dict(e) for e in trust_entries])

    print(f"Indexes saved to {INDEX_DIR}")


def _scan_to_dict(s: FileScan) -> dict:
    return {
        "path": s.path,
        "file_type": s.file_type,
        "functions": s.functions,
        "classes": s.classes,
        "imports": s.imports,
        "env_vars": s.env_vars,
        "file_reads": s.file_reads,
        "file_writes": s.file_writes,
        "network_calls": s.network_calls,
        "subprocess_calls": s.subprocess_calls,
        "external_services": s.external_services,
        "system_mods": s.system_mods,
        "risk_class": s.risk_class,
        "content_skipped": s.content_skipped,
    }


def _cron_to_dict(e: CronEntry) -> dict:
    return {
        "schedule": e.schedule,
        "command": e.command,
        "script_path": e.script_path,
        "script_exists": e.script_exists,
        "risk_class": e.risk_class,
        "broken": e.broken,
        "notes": e.notes,
    }


def _skill_to_dict(s: SkillInfo) -> dict:
    return {
        "name": s.name,
        "category": s.category,
        "path": s.path,
        "has_readme": s.has_readme,
        "has_skill_md": s.has_skill_md,
        "has_tests": s.has_tests,
        "scripts": s.scripts,
        "external_access": s.external_access,
        "trust_class": s.trust_class,
        "missing_docs": s.missing_docs,
    }


def _trust_to_dict(e: TrustEntry) -> dict:
    return {
        "file": e.file,
        "can_read_files": e.can_read_files,
        "can_write_files": e.can_write_files,
        "can_call_network": e.can_call_network,
        "can_call_google": e.can_call_google,
        "can_send_telegram": e.can_send_telegram,
        "can_modify_cron": e.can_modify_cron,
        "can_modify_systemd": e.can_modify_systemd,
        "can_handle_secrets": e.can_handle_secrets,
        "risk_class": e.risk_class,
        "reasons": e.reasons,
    }
