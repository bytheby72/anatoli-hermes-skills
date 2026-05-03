# Debate Mechanics and Anti-Patterns

## How Debate Works (Good)

### Round 1: Position Statements

Each agent writes independent memo:
- Position (buy/sell/hold or alert/update/ignore)
- Evidence (data points, sources)
- Confidence (0.0 - 1.0)

### Round 2: Cross-Examination

Moderator identifies conflicts:
- Agent A says "trend up", Agent B says "trend down"
- Moderator asks both to justify with specific data points
- Agents can revise positions based on new evidence

### Round 3: Consensus Building

- If all agents agree within delta: finalize decision
- If disagreement persists: calculate weighted confidence
- If confidence below threshold: escalate to human

### Final: Decision with Audit Trail

```
Decision: UPDATE
Confidence: 0.82
Supporting: Data Collector (0.9), Metrics Analyst (0.85)
Dissenting: Market Analyst (0.6 — weak signal)
Reasoning: Price deviation confirmed by 2 independent sources.
           Market signal weak but not contradictory.
Action: Update price record, notify manager.
```

## Anti-Patterns (Bad)

### Voting Without Reasoning

Bad:
```
Agent 1: BUY
Agent 2: BUY
Agent 3: SELL
Result: BUY (majority wins)
```

Why bad: No understanding of why. Agent 3 may have critical risk data.

### Monolithic Prediction

Bad: One LLM gets all data, outputs decision.

Why bad: No specialization, no conflict detection, no audit trail.

### Override by Confidence

Bad: Highest confidence agent wins automatically.

Why bad: Confidence can be miscalibrated. Risk Manager with low confidence may have critical block.

### Infinite Debate

Bad: No round limit, agents argue forever.

Why bad: Wastes tokens, delays decisions, no resolution.

### No Escalation Path

Bad: System must always produce decision.

Why bad: Forces "best guess" in uncertain situations. Human review needed for edge cases.

## Confidence Calibration

| Confidence | Meaning | Action |
|-----------|---------|--------|
| 0.9 - 1.0 | Strong consensus | Execute automatically |
| 0.7 - 0.89 | Moderate consensus | Execute with logging |
| 0.5 - 0.69 | Weak consensus | Escalate to human |
| 0.0 - 0.49 | No consensus | Block, human review required |

## Moderator Rules

1. Never has own position — only facilitates
2. Can request additional data from any agent
3. Can force early escalation if deadlock detected
4. Logs all interactions for audit
5. Cannot override Validator block
