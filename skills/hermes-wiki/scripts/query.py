"""
Local query engine for Hermes Wiki.
Answers questions over local index. No external calls.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from indexer import load_index


def ask(question: str) -> str:
    """Answer a question using local indexes."""
    q = question.lower().strip()

    # Route to appropriate index
    if any(x in q for x in ["cron", "schedule", "job"]):
        return _query_cron(q)
    elif any(x in q for x in ["skill", "plugin"]):
        return _query_skills(q)
    elif any(x in q for x in ["trust", "risk", "external", "network", "api"]):
        return _query_trust(q)
    elif any(x in q for x in ["script", "file", "function", "class", "import", "where"]):
        return _query_code(q)
    elif any(x in q for x in ["server", "load", "cpu", "ram", "process"]):
        return "Run: python3 scripts/hermes_wiki.py server-health"
    elif any(x in q for x in ["cleanup", "garbage", "clean", "free space"]):
        return "Run: python3 scripts/hermes_wiki.py garbage-map"
    else:
        return _query_all(q)


def _query_cron(q: str) -> str:
    entries = load_index("cron")
    results = []
    for e in entries:
        text = f"{e.get('schedule', '')} {e.get('command', '')} {e.get('script_path', '')}"
        if any(term in text.lower() for term in q.split()):
            results.append(e)

    if not results:
        return "No cron entries match your query."

    lines = [f"Found {len(results)} cron entries:", ""]
    for r in results:
        status = "BROKEN" if r.get("broken") else "OK"
        lines.append(f"- [{status}] {r.get('schedule', '?')} -> {r.get('script_path', r.get('command', '?'))}")
        if r.get("notes"):
            lines.append(f"  Notes: {'; '.join(r['notes'])}")
    return "\n".join(lines)


def _query_skills(q: str) -> str:
    entries = load_index("skills")
    results = []
    for e in entries:
        text = f"{e.get('name', '')} {e.get('category', '')} {' '.join(e.get('scripts', []))}"
        if any(term in text.lower() for term in q.split()):
            results.append(e)

    if not results:
        return "No skills match your query."

    lines = [f"Found {len(results)} skills:", ""]
    for r in results:
        ext = "YES" if r.get("external_access") else "NO"
        lines.append(f"- {r.get('name', '?')} ({r.get('category', '?')}) - External: {ext}, Trust: {r.get('trust_class', '?')}")
        if r.get("missing_docs"):
            lines.append(f"  Missing: {', '.join(r['missing_docs'])}")
    return "\n".join(lines)


def _query_trust(q: str) -> str:
    entries = load_index("trust")
    results = []
    for e in entries:
        text = f"{e.get('file', '')} {' '.join(e.get('reasons', []))}"
        if any(term in text.lower() for term in q.split()):
            results.append(e)

    # Also filter by capability if mentioned
    if "network" in q or "api" in q:
        results = [e for e in results if e.get("can_call_network")]
    if "google" in q:
        results = [e for e in results if e.get("can_call_google")]
    if "telegram" in q:
        results = [e for e in results if e.get("can_send_telegram")]
    if "secret" in q:
        results = [e for e in results if e.get("can_handle_secrets")]

    if not results:
        return "No files match your trust query."

    lines = [f"Found {len(results)} files:", ""]
    for r in results[:30]:
        lines.append(f"- {Path(r.get('file', '?')).name} - Risk: {r.get('risk_class', '?')}")
        if r.get("reasons"):
            lines.append(f"  Reasons: {'; '.join(r['reasons'][:3])}")
    return "\n".join(lines)


def _query_code(q: str) -> str:
    entries = load_index("code")
    results = []
    for e in entries:
        text = f"{e.get('path', '')} {' '.join(e.get('functions', []))} {' '.join(e.get('classes', []))} {' '.join(e.get('imports', []))}"
        if any(term in text.lower() for term in q.split()):
            results.append(e)

    if not results:
        return "No code files match your query."

    lines = [f"Found {len(results)} code files:", ""]
    for r in results[:30]:
        lines.append(f"- {r.get('path', '?')} ({r.get('file_type', '?')}) - Risk: {r.get('risk_class', '?')}")
        if r.get("functions"):
            lines.append(f"  Functions: {', '.join(r['functions'][:5])}")
    return "\n".join(lines)


def _query_all(q: str) -> str:
    lines = []
    code = _query_code(q)
    if not code.startswith("No code"):
        lines.append("## Code Matches")
        lines.append(code)
    skills = _query_skills(q)
    if not skills.startswith("No skills"):
        lines.append("\n## Skill Matches")
        lines.append(skills)
    cron = _query_cron(q)
    if not cron.startswith("No cron"):
        lines.append("\n## Cron Matches")
        lines.append(cron)

    if not lines:
        return "No matches found. Try: scan, cron-map, skill-map, trust-map, server-health, garbage-map"
    return "\n".join(lines)
