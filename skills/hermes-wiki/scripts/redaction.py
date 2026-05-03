"""
Redaction engine for Hermes Wiki.
Ensures no secrets leak into indexes, reports, or stdout.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable

# ── Filename patterns: skip content entirely ──
SECRET_FILENAME_PATTERNS = [
    r"^\.env$",
    r"^\.env\.",
    r"\.env$",
    r"token",
    r"credential",
    r"secret",
    r"private",
    r"^id_rsa",
    r"^id_ed25519",
    r"cookie",
    r"session",
    r"^auth",
    r"\.pem$",
    r"\.p12$",
    r"\.kube",
    r"google_token",
    r"gmail_token",
    r"^\.git",
]

SECRET_FILENAME_RE = re.compile(
    "|".join(f"(?:{p})" for p in SECRET_FILENAME_PATTERNS),
    re.IGNORECASE,
)

# ── Variable name patterns: redact value ──
SECRET_VAR_PATTERNS = [
    r"KEY",
    r"TOKEN",
    r"SECRET",
    r"PASSWORD",
    r"CREDENTIAL",
    r"COOKIE",
    r"SESSION",
    r"PRIVATE",
    r"AUTH",
    r"BEARER",
]

SECRET_VAR_RE = re.compile(
    "|".join(f"(?:{p})" for p in SECRET_VAR_PATTERNS),
    re.IGNORECASE,
)

# ── Confidential path indicators ──
CONFIDENTIAL_PATH_INDICATORS = [
    ".env",
    "secret",
    "private",
    "credential",
    "token",
    "auth",
    "cookie",
    "session",
    "backup",
    "archive",
    "confidential",
    "internal",
]


def is_secret_filename(path: str | Path) -> bool:
    """Return True if file basename matches secret patterns."""
    basename = Path(path).name
    return bool(SECRET_FILENAME_RE.search(basename))


def is_confidential_path(path: str | Path) -> bool:
    """Return True if path contains confidential indicators."""
    path_str = str(path).lower()
    return any(ind in path_str for ind in CONFIDENTIAL_PATH_INDICATORS)


def redact_env_line(line: str) -> str:
    """Redact value side of VAR=VALUE if VAR looks secret."""
    line = line.rstrip("\n\r")
    if "=" not in line or line.strip().startswith("#"):
        return line
    key, _, val = line.partition("=")
    key_stripped = key.strip()
    if SECRET_VAR_RE.search(key_stripped):
        return f"{key_stripped}=\u003cREDACTED\u003e"
    return line


def redact_text(text: str) -> str:
    """Redact secret-looking variable assignments in arbitrary text."""
    lines = text.splitlines()
    return "\n".join(redact_env_line(line) for line in lines)


def safe_read_text(path: str | Path, max_size: int = 1_000_000) -> str | None:
    """
    Read file text only if NOT a secret file.
    Returns None for secret files.
    """
    p = Path(path)
    if is_secret_filename(p):
        return None
    if not p.is_file():
        return None
    if p.stat().st_size > max_size:
        return None
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return None


def safe_read_lines(path: str | Path, max_lines: int = 1000) -> list[str] | None:
    """Read file lines with redaction applied. Returns None for secret files."""
    raw = safe_read_text(path)
    if raw is None:
        return None
    lines = raw.splitlines()
    return [redact_env_line(line) for line in lines[:max_lines]]


def metadata_only(path: str | Path) -> dict:
    """Return safe metadata for ANY file (including secrets)."""
    p = Path(path)
    try:
        st = p.stat()
        return {
            "path": str(p),
            "exists": True,
            "size": st.st_size,
            "mode": oct(st.st_mode)[-3:],
            "owner": st.st_uid,
            "group": st.st_gid,
            "mtime": st.st_mtime,
            "is_secret": is_secret_filename(p),
            "is_confidential": is_confidential_path(p),
            "content_skipped": is_secret_filename(p) or is_confidential_path(p),
        }
    except (OSError, PermissionError):
        return {
            "path": str(p),
            "exists": False,
            "content_skipped": True,
        }
