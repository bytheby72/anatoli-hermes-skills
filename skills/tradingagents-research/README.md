# TradingAgents Research Skill

Multi-agent LLM architecture research and adaptation toolkit. Read-only. Local-only. No live trading.

## What It Does

Analyzes TradingAgents-style repositories (multi-agent LLM trading systems) and produces adaptation guides for generic monitoring, analytics, and decision-support systems.

## Why It Exists

Trading systems pioneered multi-agent debate architectures. Their patterns -- specialized roles, structured argumentation, confidence thresholds, audit trails -- apply to any domain requiring multi-source analysis with human oversight.

## Core Concepts

**Debate over Voting**

Bad: 4 agents vote, majority wins. No reasoning exposed.
Good: Each agent writes memo with position and evidence. Moderator probes conflicts. Final decision has traceable argumentation.

**Specialized Prompts**

Each agent knows one thing deeply. Fundamental analyst does not touch technical indicators. Risk manager only says "no" or "approved with limits."

**Fail-Closed Risk Layer**

Risk manager can block any decision. No override by other agents. Human reviews blocked decisions.

**Confidence Threshold**

If agents disagree by more than X%, decision blocks until human review. No "best guess" execution.

## Quick Start

```bash
# Clone target repo for analysis
git clone https://github.com/SunsetWolf/TradingAgents.git /tmp/tradingagents-src

# Scan structure
cd /path/to/anatoli-hermes-skills
python3 skills/tradingagents-research/scripts/scan_repo.py /tmp/tradingagents-src

# Generate adaptation report
python3 skills/tradingagents-research/scripts/adaptation_map.py \
  --source /tmp/tradingagents-src \
  --output /tmp/adaptation_report.md
```

## Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| `scan_repo.py` | Repository structure, agents, prompts, execution flow | JSON + markdown summary |
| `extract_prompts.py` | Extract and anonymize system prompts | Markdown with neutral examples |
| `debate_analyzer.py` | Debate rounds, moderator logic, consensus rules | Flow diagram (text) |
| `adaptation_map.py` | Full adaptation report: roles, mechanics, risks, roadmap | Markdown report |
| `risk_checker.py` | Hardcoded keys, real data, cloud defaults, unsafe patterns | Warning list + exit code |

## Role Mapping

| Source Role | Generic Role | Function |
|-------------|-------------|----------|
| Fundamental Analyst | Data Collector | Gather, validate, structure raw data |
| Sentiment Analyst | Market Analyst | External signals, trends, sentiment |
| Technical Analyst | Metrics Analyst | Pattern detection, thresholds, anomalies |
| Risk Manager | Validator | Boundary checks, limits, blocks |
| Moderator | Decision Engine | Consensus or human escalation |
| Execution | Action Dispatcher | Alert, update, flag, ignore |

## Security

- All analysis is read-only
- No API keys, tokens, or credentials in output
- Real data in examples is redacted automatically
- Cloud-only deployment paths are flagged
- Auto-execution without human gate is rejected

## Tests

```bash
cd skills/tradingagents-research
python3 -m pytest tests/ -v
```

Or run directly:
```bash
python3 tests/test_scan_repo.py
python3 tests/test_adaptation_map.py
python3 tests/test_no_leaks.py
```

## License

MIT
