#!/usr/bin/env python3
"""
Generate adaptation report: map TradingAgents roles to generic monitoring roles.
Output: markdown report with neutral examples only.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# ── Role mapping template ──
ROLE_MAP = {
    "Fundamental Analyst": {
        "generic_name": "Data Collector",
        "function": "Gather raw data from sources: prices, inventory, supplier catalogs",
        "tools": ["HTTP client", "HTML parser", "API wrapper", "Cache layer"],
        "outputs": ["Structured dataset", "Validation flags", "Source timestamps"],
    },
    "Sentiment Analyst": {
        "generic_name": "Market Analyst",
        "function": "External signals: competitor moves, demand trends, seasonality",
        "tools": ["News scraper", "Social monitor", "Trend detector", "NLP classifier"],
        "outputs": ["Sentiment score", "Trend direction", "Anomaly alerts"],
    },
    "Technical Analyst": {
        "generic_name": "Metrics Analyst",
        "function": "Pattern detection: thresholds, anomalies, price corridors",
        "tools": ["Time-series analysis", "Statistical tests", "Visualization", "Alert engine"],
        "outputs": ["Support/resistance levels", "Deviation metrics", "Signal strength"],
    },
    "Risk Manager": {
        "generic_name": "Validator",
        "function": "Boundary checks: limits, sanity checks, fail-closed gates",
        "tools": ["Rule engine", "Limit checker", "Audit logger", "Block dispatcher"],
        "outputs": ["Approve / Block / Escalate", "Risk score", "Limit breach report"],
    },
    "Moderator": {
        "generic_name": "Decision Engine",
        "function": "Consensus builder or human escalation trigger",
        "tools": ["Conflict resolver", "Confidence calculator", "Escalation router"],
        "outputs": ["Final decision with reasoning", "Confidence level", "Audit trail"],
    },
    "Execution": {
        "generic_name": "Action Dispatcher",
        "function": "Route approved decisions to actions",
        "tools": ["Notification sender", "Database updater", "Flag setter", "Log writer"],
        "outputs": ["Alert sent", "Record updated", "Flag raised", "Log entry"],
    },
}


def load_scan_data(repo_path: str) -> dict:
    scan_file = Path("/tmp/tradingagents_scan.json")
    if scan_file.exists():
        return json.loads(scan_file.read_text(encoding="utf-8"))
    return {"repo_path": repo_path, "error": "No scan data found. Run scan_repo.py first."}


def load_debate_data() -> dict:
    debate_file = Path("/tmp/tradingagents_debate.json")
    if debate_file.exists():
        return json.loads(debate_file.read_text(encoding="utf-8"))
    return {}


def generate_report(source_path: str, output_path: str) -> None:
    scan = load_scan_data(source_path)
    debate = load_debate_data()

    lines = []
    lines.append("# Multi-Agent Architecture Adaptation Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().isoformat()}")
    lines.append(f"**Source:** {scan.get('repo_path', source_path)}")
    lines.append(f"**Analyzer:** tradingagents-research skill")
    lines.append("")

    lines.append("## 1. Source Repository Overview")
    lines.append("")
    if "error" in scan:
        lines.append(f"_Error: {scan['error']}_")
    else:
        lines.append(f"- Python files: {scan.get('total_py_files', 'N/A')}")
        lines.append(f"- Total lines: {scan.get('total_lines', 'N/A')}")
        lines.append(f"- Agents: {len(scan.get('agents', []))}")
        lines.append(f"- Prompts: {len(scan.get('prompts', []))}")
        lines.append(f"- Debate modules: {len(scan.get('debate_modules', []))}")
        lines.append(f"- Execution modules: {len(scan.get('execution_modules', []))}")
    lines.append("")

    lines.append("## 2. Role Mapping")
    lines.append("")
    lines.append("| Source Role | Generic Role | Function |")
    lines.append("|-------------|-------------|----------|")
    for src, mapped in ROLE_MAP.items():
        lines.append(f"| {src} | {mapped['generic_name']} | {mapped['function']} |")
    lines.append("")

    lines.append("## 3. Detailed Role Breakdown")
    lines.append("")
    for src, mapped in ROLE_MAP.items():
        lines.append(f"### {mapped['generic_name']} (was: {src})")
        lines.append("")
        lines.append(f"**Function:** {mapped['function']}")
        lines.append("")
        lines.append("**Tools:**")
        for tool in mapped["tools"]:
            lines.append(f"- {tool}")
        lines.append("")
        lines.append("**Outputs:**")
        for out in mapped["outputs"]:
            lines.append(f"- {out}")
        lines.append("")

    lines.append("## 4. Debate Mechanics")
    lines.append("")
    flow = debate.get("flow", {})
    if flow:
        lines.append("| Feature | Detected |")
        lines.append("|---------|----------|")
        for k, v in flow.items():
            lines.append(f"| {k} | {'yes' if v else 'no'} |")
    else:
        lines.append("_No debate data available. Run debate_analyzer.py first._")
    lines.append("")

    lines.append("## 5. Key Adaptation Changes")
    lines.append("")
    lines.append("### Financial Metrics → Business Metrics")
    lines.append("- P/E ratio → Price margin vs market average")
    lines.append("- RSI → Price deviation from 30-day corridor")
    lines.append("- MACD → Trend acceleration in competitor pricing")
    lines.append("")
    lines.append("### Orders → Actions")
    lines.append("- Buy/Sell/Hold → Alert/Update/Flag/Ignore")
    lines.append("- Position sizing → Threshold breach severity")
    lines.append("- Stop-loss → Auto-block limit with human review")
    lines.append("")
    lines.append("### Market Data → Supplier Data")
    lines.append("- Stock prices → Supplier catalog prices")
    lines.append("- Volume → Inventory levels")
    lines.append("- News sentiment → Competitor move detection")
    lines.append("")

    lines.append("## 6. Security & Safety")
    lines.append("")
    lines.append("- All analysis is read-only")
    lines.append("- No API keys in public output")
    lines.append("- Real data redacted automatically")
    lines.append("- Human approval gate before any action")
    lines.append("- Validator can block without override")
    lines.append("")

    lines.append("## 7. Implementation Roadmap")
    lines.append("")
    lines.append("| Phase | Task | Effort |")
    lines.append("|-------|------|--------|")
    lines.append("| 1 | Implement Data Collector with caching | 2-3 days |")
    lines.append("| 2 | Build Market Analyst for competitor tracking | 2-3 days |")
    lines.append("| 3 | Add Metrics Analyst for threshold detection | 1-2 days |")
    lines.append("| 4 | Deploy Validator with fail-closed rules | 1-2 days |")
    lines.append("| 5 | Integrate Decision Engine with escalation | 2-3 days |")
    lines.append("| 6 | Add Action Dispatcher (alerts, updates) | 1-2 days |")
    lines.append("| 7 | End-to-end test with synthetic data | 2-3 days |")
    lines.append("")

    lines.append("## 8. Acceptance Criteria")
    lines.append("")
    lines.append("- [ ] All 6 roles implemented and tested")
    lines.append("- [ ] Debate mechanics produce audit trail")
    lines.append("- [ ] Confidence threshold blocks low-consensus decisions")
    lines.append("- [ ] Validator blocks without explanation (human reviews)")
    lines.append("- [ ] No real data in public examples or tests")
    lines.append("- [ ] Setup time for new developer < 30 minutes")
    lines.append("")

    report = "\n".join(lines)
    Path(output_path).write_text(report, encoding="utf-8")
    print(f"Report saved: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate adaptation report")
    parser.add_argument("--source", required=True, help="Path to analyzed repository")
    parser.add_argument("--output", default="/tmp/adaptation_report.md", help="Output markdown file")
    args = parser.parse_args()

    generate_report(args.source, args.output)
