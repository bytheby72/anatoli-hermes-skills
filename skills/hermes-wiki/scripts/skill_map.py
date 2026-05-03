"""
Skill mapper for Hermes Wiki.
Scans ~/.hermes/skills/ and maps structure, docs, tests, risks.
READ-ONLY. NEVER MODIFIES SKILLS.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from redaction import metadata_only, is_secret_filename


@dataclass
class SkillInfo:
    name: str
    category: str
    path: str
    has_readme: bool
    has_skill_md: bool
    has_tests: bool
    scripts: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    configs: list[str] = field(default_factory=list)
    external_access: bool = False
    local_file_access: bool = False
    secret_risk: bool = False
    trust_class: str = "LOW"
    last_modified: float = 0.0
    missing_docs: list[str] = field(default_factory=list)


def scan_skill_dir(skills_root: str = "~/.hermes/skills") -> list[SkillInfo]:
    """Scan skills directory and build skill map."""
    root = Path(skills_root).expanduser()
    if not root.exists():
        return []

    skills: list[SkillInfo] = []

    for category_dir in root.iterdir():
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue

        for skill_dir in category_dir.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith("."):
                continue

            info = _analyze_skill(skill_dir, category_dir.name)
            skills.append(info)

    return skills


def _analyze_skill(skill_dir: Path, category: str) -> SkillInfo:
    """Analyze a single skill directory."""
    name = skill_dir.name
    has_readme = (skill_dir / "README.md").exists()
    has_skill_md = (skill_dir / "SKILL.md").exists()
    has_tests = (skill_dir / "tests").exists() or any(
        f.suffix == ".py" and "test" in f.name.lower()
        for f in skill_dir.rglob("*")
    )

    scripts = []
    references = []
    configs = []
    external_access = False
    local_file_access = False
    secret_risk = False
    last_modified = 0.0
    missing_docs = []

    if not has_readme:
        missing_docs.append("README.md")
    if not has_skill_md:
        missing_docs.append("SKILL.md")
    if not has_tests:
        missing_docs.append("tests/")

    for fpath in skill_dir.rglob("*"):
        if fpath.is_dir():
            continue
        if is_secret_filename(fpath):
            secret_risk = True
            continue

        try:
            mtime = fpath.stat().st_mtime
            if mtime > last_modified:
                last_modified = mtime
        except (OSError, PermissionError):
            continue

        rel = str(fpath.relative_to(skill_dir))

        if fpath.suffix in {".py", ".sh", ".bash", ".js"}:
            scripts.append(rel)
            # Quick content scan for external access
            try:
                text = fpath.read_text(encoding="utf-8", errors="replace")
                if re.search(r"(requests\.|urllib|http\.client|curl\b|wget\b)", text, re.I):
                    external_access = True
                if re.search(r"(open\(|read_file|write_file|Path\(.*\)\.read|Path\(.*\)\.write)", text, re.I):
                    local_file_access = True
            except (OSError, PermissionError):
                pass

        elif fpath.suffix in {".md", ".txt", ".rst"} and "README" not in fpath.name:
            references.append(rel)

        elif fpath.suffix in {".json", ".yaml", ".yml", ".toml"}:
            configs.append(rel)

    trust_class = _classify_skill_trust(
        external_access, local_file_access, secret_risk, has_tests
    )

    return SkillInfo(
        name=name,
        category=category,
        path=str(skill_dir),
        has_readme=has_readme,
        has_skill_md=has_skill_md,
        has_tests=has_tests,
        scripts=scripts,
        references=references,
        configs=configs,
        external_access=external_access,
        local_file_access=local_file_access,
        secret_risk=secret_risk,
        trust_class=trust_class,
        last_modified=last_modified,
        missing_docs=missing_docs,
    )


def _classify_skill_trust(
    external: bool, local_file: bool, secret_risk: bool, has_tests: bool
) -> str:
    if secret_risk:
        return "SECRET_OR_UNKNOWN"
    if external and local_file:
        return "HIGH"
    if external:
        return "MEDIUM"
    if local_file:
        return "LOW"
    if not has_tests:
        return "MEDIUM"
    return "LOW"


def format_skill_table(skills: list[SkillInfo]) -> str:
    """Format skills as markdown table."""
    lines = [
        "| Skill | Category | README | SKILL.md | Tests | Scripts | External | Trust | Missing |",
        "|-------|----------|--------|----------|-------|---------|----------|-------|---------|",
    ]
    for s in skills:
        readme = "YES" if s.has_readme else "NO"
        skill_md = "YES" if s.has_skill_md else "NO"
        tests = "YES" if s.has_tests else "NO"
        ext = "YES" if s.external_access else "NO"
        missing = ", ".join(s.missing_docs) if s.missing_docs else "-"
        lines.append(
            f"| {s.name} | {s.category} | {readme} | {skill_md} | {tests} | {len(s.scripts)} | {ext} | {s.trust_class} | {missing} |"
        )
    return "\n".join(lines)
