"""
Cleanup advisor for Hermes Wiki.
Suggests cleanup actions. NEVER EXECUTES THEM.
All destructive commands marked MANUAL_APPROVAL_REQUIRED.
"""

from __future__ import annotations

from garbage_map import build_garbage_map, GarbageEntry


def build_cleanup_advice() -> list[dict]:
    """Build cleanup advice table."""
    entries = build_garbage_map()
    advice = []
    for e in entries:
        advice.append({
            "candidate": e.candidate,
            "path": e.path,
            "size": e.size,
            "risk_class": e.risk_class,
            "reason": e.reason,
            "check_command": e.check_command,
            "cleanup_command": e.cleanup_command,
            "manual_approval_required": e.manual_approval_required,
        })
    return advice


def format_cleanup_report(advice: list[dict]) -> str:
    lines = [
        "# Cleanup Advisor Report",
        "",
        "**WARNING: This report suggests cleanup commands for MANUAL REVIEW ONLY.**",
        "**NO AUTOMATIC CLEANUP IS PERFORMED.**",
        "",
        "| Candidate | Path | Size | Risk | Reason |",
        "|-----------|------|------|------|--------|",
    ]
    for a in advice:
        lines.append(
            f"| {a['candidate']} | {a['path']} | {a['size']} | {a['risk_class']} | {a['reason']} |"
        )

    lines.extend([
        "",
        "## Check Commands",
        "",
    ])
    for a in advice:
        lines.append(f"### {a['candidate']}: {a['path']}")
        lines.append(f"```bash")
        lines.append(f"# Check:")
        lines.append(a['check_command'])
        lines.append(f"```")

    lines.extend([
        "",
        "## Suggested Cleanup Commands",
        "",
        "**MANUAL_APPROVAL_REQUIRED FOR ALL COMMANDS BELOW**",
        "",
    ])
    for a in advice:
        if a['manual_approval_required']:
            lines.append(f"```bash")
            lines.append(f"# MANUAL_APPROVAL_REQUIRED: {a['candidate']}")
            lines.append(f"# Risk: {a['risk_class']}")
            lines.append(f"# Reason: {a['reason']}")
            lines.append(a['cleanup_command'])
            lines.append(f"```")
            lines.append("")

    return "\n".join(lines)
