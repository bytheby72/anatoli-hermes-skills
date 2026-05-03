---
name: tradingagents-research
description: |
  Research and adaptation guide for multi-agent LLM trading architectures.
  Maps TradingAgents (UCLA/MIT) roles to generic monitoring/analytics systems.
  Read-only analysis, no live trading, no real data exposure.
category: research
author: anonymous
tags: [trading, multi-agent, llm, research, adaptation]
version: 1.0.0
---

# TradingAgents Research Skill

## When to Use

- Need to understand multi-agent LLM architectures for decision-making systems
- Adapting trading-agent patterns to price monitoring, analytics, or alerting
- Evaluating debate-based consensus vs monolithic prediction
- Building local-only, privacy-first agent orchestration

## When NOT to Use

- Live trading without human approval gates
- Cloud-hosted data pipelines without encryption review
- Copy-pasting trading strategies without backtesting
- Using real financial data in public examples

## Quick Start

```bash
# 1. Clone target repository for analysis
git clone https://github.com/SunsetWolf/TradingAgents.git /tmp/tradingagents-src

# 2. Run structure scanner
python3 skills/tradingagents-research/scripts/scan_repo.py /tmp/tradingagents-src

# 3. Generate adaptation report
python3 skills/tradingagents-research/scripts/adaptation_map.py \
  --source /tmp/tradingagents-src \
  --output report.md
```

## Architecture Mapping

| TradingAgents Role | Generic Monitoring Role | Core Function |
|-------------------|------------------------|---------------|
| Fundamental Analyst | Data Collector | Gather raw data from sources |
| Sentiment Analyst | Market Analyst | External signals, trends, sentiment |
| Technical Analyst | Metrics Analyst | Pattern detection, thresholds, anomalies |
| Risk Manager | Validator | Boundary checks, limits, fail-closed gates |
| Moderator | Decision Engine | Consensus or escalation to human |
| Execution (Buy/Sell/Hold) | Action Dispatcher | Alert, update, flag, or ignore |

## Key Principles

1. **Debate over voting.** Agents argue, not average. Moderator resolves conflicts.
2. **Specialized prompts.** Each agent has narrow scope, no cross-contamination.
3. **Fail-closed risk layer.** Validator can block any decision. Human reviews blocked decisions.
4. **Audit trail.** Every memo, vote, and decision saved to fabric/memory.
5. **Confidence threshold.** Below X% consensus -- block and escalate.

## File Structure

```
skills/tradingagents-research/
├── SKILL.md                          # This file
├── README.md                         # Human-readable guide
├── scripts/
│   ├── scan_repo.py                  # Repository structure scanner
│   ├── extract_prompts.py            # Prompt extraction and analysis
│   ├── debate_analyzer.py            # Debate flow analysis
│   ├── adaptation_map.py             # Role-to-role mapping generator
│   └── risk_checker.py               # Security and leak detection
├── references/
│   ├── role_templates.md             # Generic prompt templates per role
│   ├── debate_patterns.md            # Debate mechanics and anti-patterns
│   ├── adaptation_checklist.md       # Step-by-step adaptation guide
│   └── security_rules.md             # What never goes public
└── tests/
    ├── test_scan_repo.py             # Scanner tests
    ├── test_adaptation_map.py        # Mapping logic tests
    └── test_no_leaks.py              # Static leak detection
```

## Commands

| Command | Purpose |
|---------|---------|
| `python3 scripts/scan_repo.py PATH` | Scan repository structure, list agents, prompts, execution flow |
| `python3 scripts/extract_prompts.py PATH` | Extract and anonymize all system prompts |
| `python3 scripts/debate_analyzer.py PATH` | Analyze debate rounds, moderator logic, consensus rules |
| `python3 scripts/adaptation_map.py --source PATH --output FILE` | Generate full adaptation report |
| `python3 scripts/risk_checker.py PATH` | Scan for hardcoded keys, real data, cloud defaults |

## Acceptance Criteria

- [ ] Repository scanned and structure documented
- [ ] All 4 agent roles mapped to generic equivalents
- [ ] Debate mechanics extracted and explained
- [ ] Confidence scoring logic understood
- [ ] Security risks identified (keys, real data, cloud deps)
- [ ] Adaptation report generated with neutral examples only
- [ ] No real company names, prices, or identifiers in public output

## References

- `references/role_templates.md` -- Generic prompts per role
- `references/debate_patterns.md` -- How debate works, common failures
- `references/adaptation_checklist.md` -- Step-by-step migration guide
- `references/security_rules.md` -- Redaction and safety rules

## Security Rules

| Violation | Consequence |
|-----------|-------------|
| Real prices in examples | Immediate redaction |
| API keys in output | Block commit, alert human |
| Cloud-only deployment suggested | Flag for review |
| Auto-execution without human gate | Reject, fail-closed |
| Real company names in public files | Rewrite with generic terms |

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Scanner fails on repo | Missing `git` or network | Check `git --version`, verify URL |
| Prompts not found | Non-standard structure | Check `config/`, `agents/`, `prompts/` manually |
| Debate logic unclear | Dynamic generation | Search for `moderator`, `debate`, `consensus` in code |
| Real data in examples | Upstream leak | Run `risk_checker.py`, redact before commit |

## Next Steps

1. Run scanner on target repository
2. Review `references/adaptation_checklist.md`
3. Generate adaptation report
4. Present to human for approval before any implementation
