# Adaptation Checklist

Step-by-step migration from trading-agent architecture to generic monitoring system.

## Phase 0: Analysis (Day 1)

- [ ] Clone TradingAgents repository
- [ ] Run `scan_repo.py` — document structure
- [ ] Run `extract_prompts.py` — extract and anonymize prompts
- [ ] Run `debate_analyzer.py` — understand debate mechanics
- [ ] Run `risk_checker.py` — identify security issues
- [ ] Read source README and architecture docs
- [ ] Map all 4+ agent roles to generic equivalents

## Phase 1: Core Infrastructure (Days 2-3)

- [ ] Set up project structure (6 roles, moderator, dispatcher)
- [ ] Implement inter-agent communication protocol (JSON memos)
- [ ] Build audit logger (every decision saved to fabric/memory)
- [ ] Create confidence scoring module
- [ ] Implement escalation router (human notification)

## Phase 2: Agent Implementation (Days 4-7)

- [ ] Data Collector: HTTP client, caching, validation
- [ ] Market Analyst: trend detection, sentiment scoring
- [ ] Metrics Analyst: threshold detection, anomaly flagging
- [ ] Validator: rule engine, hard limits, block dispatcher
- [ ] Decision Engine: consensus builder, conflict resolver
- [ ] Action Dispatcher: alert sender, database updater

## Phase 3: Debate Mechanics (Days 8-9)

- [ ] Implement round-based debate (3 rounds max)
- [ ] Build moderator logic (conflict detection, clarification requests)
- [ ] Add confidence threshold (0.7 for auto-execute, below = escalate)
- [ ] Create memo format standard (position, evidence, confidence)
- [ ] Test with synthetic data

## Phase 4: Integration (Days 10-11)

- [ ] Wire all agents into single pipeline
- [ ] Add error handling (API failures, timeouts, malformed data)
- [ ] Implement retry logic with exponential backoff
- [ ] Add circuit breaker for external APIs
- [ ] Test end-to-end with mock scenarios

## Phase 5: Security & Hardening (Days 12-13)

- [ ] Run `risk_checker.py` on own codebase
- [ ] Ensure no API keys in code (all in `.env`)
- [ ] Add input validation on all agent inputs
- [ ] Implement rate limiting on external calls
- [ ] Add timeout on all LLM calls
- [ ] Test fail-closed behavior (Validator blocks by default)

## Phase 6: Testing & Documentation (Days 14-15)

- [ ] Unit tests for each agent
- [ ] Integration tests for full pipeline
- [ ] Edge case tests (deadlock, low confidence, API failure)
- [ ] Write setup documentation
- [ ] Write troubleshooting guide
- [ ] Human review of all outputs before any real deployment

## Verification Commands

```bash
# Run all tests
python3 -m pytest tests/ -v

# Check for security issues
python3 scripts/risk_checker.py .

# Test with synthetic data
python3 scripts/run_pipeline.py --mock --verbose

# Verify audit trail
ls -la ~/.hermes/fabric/  # or equivalent
```

## Stop Conditions

Stop and escalate to human if:
- `risk_checker.py` finds critical issues
- Any agent produces inconsistent outputs on same input
- Confidence scores are miscalibrated (test with known cases)
- Validator does not block on obviously bad inputs
- Audit trail is incomplete or missing
