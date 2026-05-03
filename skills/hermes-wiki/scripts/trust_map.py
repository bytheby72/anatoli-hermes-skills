"""
Trust map builder for Hermes Wiki.
Maps file -> capabilities -> risk class.
FAIL-CLOSED. READ-ONLY.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from scanner import scan_all, FileScan
from redaction import is_confidential_path


@dataclass
class TrustEntry:
    file: str
    can_read_files: bool = False
    can_write_files: bool = False
    can_call_network: bool = False
    can_call_google: bool = False
    can_send_telegram: bool = False
    can_modify_cron: bool = False
    can_modify_systemd: bool = False
    can_handle_secrets: bool = False
    risk_class: str = "LOW"
    reasons: list[str] = field(default_factory=list)


def _detect_google(text: str) -> bool:
    return any(x in text.lower() for x in [
        "google", "gmail", "drive", "sheets", "docs", "workspace"
    ])


def _detect_telegram(text: str) -> bool:
    return any(x in text.lower() for x in [
        "telegram", "bot_token", "chat_id", "telegram_bot"
    ])


def _detect_systemd(text: str) -> bool:
    return "systemctl" in text.lower() or "systemd" in text.lower()


def _detect_cron_mod(text: str) -> bool:
    return any(x in text.lower() for x in [
        "crontab", "cron.add", "cron.remove", "cron.create"
    ])


def _detect_secret_handling(text: str) -> bool:
    return any(x in text.lower() for x in [
        "secret", "credential", "token", "password", "private_key"
    ])


def build_trust_map(scans: list[FileScan] | None = None) -> list[TrustEntry]:
    """Build trust map from file scans."""
    if scans is None:
        scans = scan_all()

    entries: list[TrustEntry] = []

    for scan in scans:
        if scan.content_skipped:
            # For skipped files, we still know metadata
            entry = TrustEntry(
                file=scan.path,
                can_handle_secrets=True,
                risk_class="SECRET_OR_UNKNOWN",
                reasons=["Content skipped - secret or confidential path"],
            )
            entries.append(entry)
            continue

        entry = TrustEntry(file=scan.path)

        # File operations
        if scan.file_reads:
            entry.can_read_files = True
            entry.reasons.append(f"File reads: {len(scan.file_reads)} patterns")

        if scan.file_writes:
            entry.can_write_files = True
            entry.reasons.append(f"File writes: {len(scan.file_writes)} patterns")

        # Network
        if scan.network_calls or scan.subprocess_calls:
            entry.can_call_network = True
            entry.reasons.append(f"Network/subprocess: {len(scan.network_calls + scan.subprocess_calls)} patterns")

        # External services (need text for deeper analysis)
        text = ""
        try:
            p = Path(scan.path)
            if p.exists() and p.stat().st_size < 1_000_000:
                text = p.read_text(encoding="utf-8", errors="replace")
        except (OSError, PermissionError):
            pass

        if text:
            if _detect_google(text):
                entry.can_call_google = True
                entry.reasons.append("Google/Gmail/Drive usage detected")

            if _detect_telegram(text):
                entry.can_send_telegram = True
                entry.reasons.append("Telegram API usage detected")

            if _detect_systemd(text):
                entry.can_modify_systemd = True
                entry.reasons.append("systemctl usage detected")

            if _detect_cron_mod(text):
                entry.can_modify_cron = True
                entry.reasons.append("Cron modification detected")

            if _detect_secret_handling(text):
                entry.can_handle_secrets = True
                entry.reasons.append("Secret-handling code detected")

        # Risk classification
        entry.risk_class = _classify_risk(entry)
        entries.append(entry)

    return entries


def _classify_risk(entry: TrustEntry) -> str:
    if entry.risk_class == "SECRET_OR_UNKNOWN":
        return "SECRET_OR_UNKNOWN"

    if entry.can_handle_secrets and entry.can_call_network:
        return "CRITICAL"

    if entry.can_read_files and entry.can_call_network:
        return "HIGH"

    if entry.can_call_google or entry.can_send_telegram:
        return "HIGH"

    if entry.can_write_files or entry.can_call_network:
        return "MEDIUM"

    if entry.can_modify_cron or entry.can_modify_systemd:
        return "MEDIUM"

    if entry.can_read_files:
        return "LOW"

    return "LOW"


def format_trust_table(entries: list[TrustEntry]) -> str:
    """Format trust map as markdown table."""
    lines = [
        "| File | Read | Write | Net | Google | Telegram | Cron | Systemd | Secrets | Risk |",
        "|------|------|-------|-----|--------|----------|------|---------|---------|------|",
    ]
    for e in entries:
        def _b(v): return "YES" if v else "NO"
        lines.append(
            f"| {Path(e.file).name} | {_b(e.can_read_files)} | {_b(e.can_write_files)} | "
            f"{_b(e.can_call_network)} | {_b(e.can_call_google)} | {_b(e.can_send_telegram)} | "
            f"{_b(e.can_modify_cron)} | {_b(e.can_modify_systemd)} | {_b(e.can_handle_secrets)} | {e.risk_class} |"
        )
    return "\n".join(lines)


def get_high_risk_files(entries: list[TrustEntry]) -> list[TrustEntry]:
    """Return only HIGH and CRITICAL risk files."""
    return [e for e in entries if e.risk_class in ("HIGH", "CRITICAL")]


def get_secret_files(entries: list[TrustEntry]) -> list[TrustEntry]:
    """Return SECRET_OR_UNKNOWN files."""
    return [e for e in entries if e.risk_class == "SECRET_OR_UNKNOWN"]
