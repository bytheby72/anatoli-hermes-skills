#!/usr/bin/env python3
"""
Extract and anonymize system prompts from multi-agent repositories.
Replaces real tickers, prices, and company names with generic placeholders.
"""

import os
import sys
import re
import json
from pathlib import Path

# ── Redaction patterns ──
REDACT_PATTERNS = [
    (r'\b[A-Z]{1,5}\b', '[TICKER]'),           # Stock tickers
    (r'\$\d+\.?\d*', '[PRICE]'),               # Dollar amounts
    (r'\b\d{4}-\d{2}-\d{2}\b', '[DATE]'),     # Dates
    (r'https?://[^\s\"\']+', '[URL]'),        # URLs
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]'),
    (r'sk-[a-zA-Z0-9]{20,}', '[API_KEY]'),    # OpenAI-style keys
    (r'ghp_[a-zA-Z0-9]{36}', '[TOKEN]'),       # GitHub tokens
]

SKIP_FILES = {".py", ".js", ".ts", ".json", ".yaml", ".yml"}


def redact(text: str) -> str:
    for pattern, replacement in REDACT_PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text


def extract_prompts(repo_path: str) -> list[dict]:
    root = Path(repo_path).expanduser().resolve()
    prompts = []

    prompt_dirs = ["prompts", "prompt", "src/prompts", "config/prompts", "agents"]
    for subdir in prompt_dirs:
        pdir = root / subdir
        if not pdir.exists():
            continue
        for f in pdir.rglob("*"):
            if f.is_file() and f.suffix not in SKIP_FILES:
                try:
                    raw = f.read_text(encoding="utf-8", errors="ignore")
                    cleaned = redact(raw)
                    prompts.append({
                        "source_file": str(f.relative_to(root)),
                        "raw_length": len(raw),
                        "cleaned_length": len(cleaned),
                        "content_preview": cleaned[:500] + "..." if len(cleaned) > 500 else cleaned,
                    })
                except Exception as e:
                    prompts.append({
                        "source_file": str(f.relative_to(root)),
                        "error": str(e),
                    })

    # Also search for prompt strings in Python files
    prompt_vars = ["system_prompt", "user_prompt", "prompt_template", "SYSTEM_MESSAGE"]
    for pyfile in root.rglob("*.py"):
        if "__pycache__" in str(pyfile):
            continue
        try:
            text = pyfile.read_text(encoding="utf-8", errors="ignore")
            for var in prompt_vars:
                for match in re.finditer(rf'{var}\s*=\s*(?:\"\"\"|\'\'\'|\"|\')(.*?)(?:\"\"\"|\'\'\'|\"|\')', text, re.DOTALL):
                    content = match.group(1)
                    cleaned = redact(content)
                    prompts.append({
                        "source_file": str(pyfile.relative_to(root)),
                        "variable": var,
                        "content_preview": cleaned[:500] + "..." if len(cleaned) > 500 else cleaned,
                    })
        except Exception:
            pass

    return prompts


def print_prompts(prompts: list[dict]) -> None:
    print(f"Prompts found: {len(prompts)}\n")
    for i, p in enumerate(prompts, 1):
        print(f"--- Prompt {i} ---")
        print(f"File: {p.get('source_file', 'unknown')}")
        if "variable" in p:
            print(f"Variable: {p['variable']}")
        if "error" in p:
            print(f"ERROR: {p['error']}")
        else:
            print(f"Preview:\n{p.get('content_preview', 'N/A')}")
        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: extract_prompts.py <repo_path>", file=sys.stderr)
        sys.exit(1)

    prompts = extract_prompts(sys.argv[1])
    print_prompts(prompts)

    json_path = Path("/tmp/tradingagents_prompts.json")
    json_path.write_text(json.dumps(prompts, indent=2, default=str), encoding="utf-8")
    print(f"JSON saved: {json_path}")
