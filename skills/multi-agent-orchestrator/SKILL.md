---
name: Multi-Agent Orchestrator
version: 1.0.0
category: devops
description: Orchestrate multiple Hermes Agent instances for parallel workstreams. Research, analysis, coding, review - each specialist with isolated context and structured handoffs.
tags: [multi-agent, orchestration, parallel, kanban, delegation]
---

# Multi-Agent Orchestrator

Route work to specialist agents. Don't do it yourself. Decompose, assign, track, integrate.

## When to Activate

- Task needs multiple specialists (research + analysis + writing)
- Work must survive crash/restart (long-running, recurring)
- Human may interject at any step
- Subtasks can run in parallel for speed
- Review/iteration cycle expected
- Audit trail matters for compliance

## When NOT to Use

- One-shot reasoning task (3 steps, one domain) - use `delegate_task` directly
- Simple file edit or command execution - do it yourself
- Urgent fix requiring immediate action - skip orchestration overhead

## Architecture

```
User Request
    |
    v
Orchestrator (routing only, no execution)
    |
    +-- kanban_create(T1: researcher) ---------> Specialist A (isolated context)
    +-- kanban_create(T2: researcher) ---------> Specialist B (isolated context)
    |
    v
Dispatcher (auto-promotes when parents done)
    |
    +-- kanban_create(T3: analyst, parents=[T1,T2]) -> Specialist C
    |
    v
kanban_create(T4: writer, parents=[T3]) ---------> Final output
    |
    v
Notify user via gateway
```

## Specialist Roster

| Profile | Does | Workspace | Typical Task |
|---------|------|-----------|--------------|
| `researcher` | Reads sources, gathers facts | `scratch` | Competitor price scraping, market research |
| `analyst` | Synthesizes, ranks, correlates | `scratch` | Price trend analysis, gap identification |
| `writer` | Drafts prose, reports, specs | `scratch` or `dir:` | Commercial reports, field work plans |
| `reviewer` | Reads output, gates approval | `scratch` | Code review, report validation |
| `backend-eng` | Server-side code | `worktree` | API endpoints, data pipelines |
| `frontend-eng` | Client-side code | `worktree` | Dashboards, visualizations |
| `ops` | Scripts, deployments, services | `dir:` | Cron jobs, monitoring, backups |
| `pm` | Specs, acceptance criteria | `scratch` | Feature definitions, OKRs |

## Decomposition Playbook

### Step 1: Understand the Goal

Ask clarifying questions if ambiguous. Cheap to ask; expensive to spawn wrong fleet.

### Step 2: Sketch the Task Graph

Draft the graph before creating anything. Show user for correction.

```
T1  researcher    research: AVS.by price changes (last 30d)
T2  researcher    research: ankron.by price changes (last 30d)
T3  analyst       correlate and flag anomalies          parents: T1, T2
T4  writer        draft price alert memo for sales team   parents: T3
```

### Step 3: Create Tasks with Dependencies

```python
import os

t1 = kanban_create(
    title="research: AVS.by price changes (last 30d)",
    assignee="researcher",
    body="Extract price history for IEK SKUs from AVS.by. Focus on MCB, RCD, contactors. Output: CSV + anomaly list.",
    tenant=os.environ.get("HERMES_TENANT"),
)["task_id"]

t2 = kanban_create(
    title="research: ankron.by price changes (last 30d)",
    assignee="researcher",
    body="Same as T1 but for ankron.by. Same output format.",
)["task_id"]

t3 = kanban_create(
    title="correlate price anomalies across competitors",
    assignee="analyst",
    body="Read T1 and T2 outputs. Find SKUs where both sites moved price in same direction. Flag >10% changes. Output: ranked anomaly table with commercial recommendation.",
    parents=[t1, t2],
)["task_id"]

t4 = kanban_create(
    title="draft price alert memo",
    assignee="writer",
    body="Turn T3 into 1-page memo for sales team. Include: affected SKUs, recommended actions, urgency level. Match tone of previous sales memos.",
    parents=[t3],
)["task_id"]
```

`parents=[...]` gates promotion. Children stay `todo` until all parents `done`, then auto-promote to `ready`.

### Step 4: Complete Orchestrator's Own Task

```python
kanban_complete(
    summary="decomposed into T1-T4: 2 researchers parallel, 1 analyst on correlation, 1 writer on memo",
    metadata={
        "task_graph": {
            "T1": {"assignee": "researcher", "parents": []},
            "T2": {"assignee": "researcher", "parents": []},
            "T3": {"assignee": "analyst", "parents": ["T1", "T2"]},
            "T4": {"assignee": "writer", "parents": ["T3"]},
        },
    },
)
```

### Step 5: Report to User

> Queued 4 tasks:
> - **T1** (researcher): AVS.by price history
> - **T2** (researcher): ankron.by price history, parallel with T1
> - **T3** (analyst): correlation + anomaly detection
> - **T4** (writer): sales memo
>
> Dispatcher starts T1 and T2 now. T3 begins when both finish. Gateway ping on T4 completion. Track with `hermes kanban tail <id>`.

## Common Patterns

### Fan-out + Fan-in
N researchers with no parents, one analyst with all as parents. Classic for data gathering.

### Pipeline with Gates
`pm -> backend-eng -> reviewer`. Each stage `parents=[previous]`. Reviewer blocks or completes.

### Same-Profile Queue
50 tasks, all `translator`, no dependencies. Dispatcher serializes. Worker accumulates experience.

### Human-in-the-Loop
Any task `kanban_block()` to wait for input. Dispatcher respawns after `/unblock`. Comment thread carries full context.

## Workspace Types

| Kind | What | How to Use |
|------|------|------------|
| `scratch` | Fresh tmp dir, auto-GC | Read/write freely; discarded on archive |
| `dir:/path` | Shared persistent dir | Other runs read your output. Use absolute paths only. |
| `worktree` | Git worktree | Run `git worktree add <path> <branch>` first. Commit work here. |

## Worker Lifecycle (Auto-Injected)

Every dispatched worker gets `KANBAN_GUIDANCE` in system prompt:

1. **Orient** - `kanban_show()` current task. Check status (blocked/archived = stop).
2. **Work** - Execute task body. Use only assigned tools.
3. **Heartbeat** - Progress updates for long tasks. Good: "epoch 12/50, loss 0.31". Bad: "still working".
4. **Block or Complete** - `kanban_block(reason)` for human decision. `kanban_complete(summary, metadata)` for handoff.

## Good Handoff Metadata

**Research task:**
```python
kanban_complete(
    summary="3 competing libraries reviewed; vLLM wins throughput, SGLang wins latency",
    metadata={
        "sources_read": 12,
        "recommendation": "vLLM",
        "benchmarks": {"vllm": 1.0, "sglang": 0.87},
    },
)
```

**Code task:**
```python
kanban_complete(
    summary="shipped rate limiter - token bucket, 14 tests pass",
    metadata={
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_run": 14,
        "tests_passed": 14,
    },
)
```

**Review task:**
```python
kanban_complete(
    summary="reviewed PR #123; 2 blocking issues found",
    metadata={
        "findings": [
            {"severity": "critical", "file": "api/search.py", "issue": "raw SQL concat"},
        ],
        "approved": False,
    },
)
```

## Pitfalls

| Mistake | Fix |
|---------|-----|
| Reassignment instead of new task | Reviewer blocks -> create NEW task for original implementer, don't reuse |
| Wrong argument order in links | `kanban_link(parent_id=..., child_id=...)` - parent FIRST |
| Pre-creating whole graph | If T3 shape depends on T1/T2 findings, let T3 plan the rest after reading handoffs |
| Missing tenant | Pass `tenant=os.environ.get("HERMES_TENANT")` on every `kanban_create` |
| Using CLI in containerized workers | Use `kanban_*` tools, not `hermes kanban` CLI (not installed in Docker/Modal) |
| Stale workspace artifacts | `kanban_show()` first; read comment thread for retry context |

## CLI Reference (Human Operator)

```bash
hermes kanban create "title" --assignee researcher [--parent ID]
hermes kanban show ID --json
hermes kanban complete ID --summary "..." --metadata '{...}'
hermes kanban block ID "reason"
hermes kanban tail ID          # follow task progress
```

Use tools from inside agents; CLI is for human operators.

## Integration with Other Skills

- **Agent Dashboard**: Kanban board visible in web UI. Task status, assignees, blockers.
- **Trust Boundary (CaMeL)**: Guard decisions logged as task metadata. Sensitive tool calls in workers are protected.
- **Skill Factory**: Common decomposition patterns auto-generated as reusable skills.

## Anti-patterns

- Do NOT execute work yourself. Route, don't run.
- Do NOT create tasks assigned to yourself. Assign to right specialist.
- Do NOT modify files outside workspace unless task body says so.
- Do NOT use `delegate_task` as substitute for `kanban_create`. `delegate_task` = short subtask inside YOUR run; `kanban_create` = cross-agent handoff that outlives one API loop.
- Do NOT complete unfinished tasks. Block instead.
