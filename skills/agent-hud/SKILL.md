---
name: Agent HUD
version: 1.0.0
category: devops
description: Terminal-based monitoring dashboard for Hermes Agent. Real-time view of memory, sessions, skills, cron jobs, health, and growth trends - all in one TUI.
tags: [monitoring, tui, dashboard, terminal, observability]
---

# Agent HUD

Terminal UI for monitoring Hermes Agent state. No browser needed - runs in any terminal over SSH.

## When to Activate

- SSH into server, need quick agent status without opening browser
- Monitoring multiple agent profiles from terminal
- Checking cron job health, memory capacity, session costs
- Tracking skill growth and corrections over time
- Low-bandwidth or headless environments
- Quick health checks during deployments

## What It Replaces

- `htop` + manual log tailing for agent monitoring
- SQLite queries for session analytics
- `ls ~/.hermes/skills` for skill inventory
- `hermes cron list` for job status
- Spreadsheet tracking of token usage

## Architecture

```
~/.hermes/
    ├── memories/MEMORY.md      <-- Memory collector (categories, capacity)
    ├── memories/USER.md        <-- User profile collector
    ├── state.db                <-- Sessions collector (SQLite)
    ├── skills/                 <-- Skills collector (SKILL.md scan)
    ├── cron/jobs.json          <-- Cron collector
    ├── config.yaml             <-- Config collector
    └── gateway.pid             <-- Health collector

Collectors (parallel, 4 workers)
    |
    v
HUDState (dataclass)
    |
    v
Textual TUI (9 tabs, 4 themes)
```

**Stack:** Python 3.11+, Textual, SQLite3, ThreadPoolExecutor

## Installation

```bash
git clone https://github.com/joeynyc/hermes-hud.git agent-hud
cd agent-hud
python3.11 -m venv venv
source venv/bin/activate
pip install -e .
```

## Usage

```bash
# Interactive TUI
hermes-hud

# Text summary (for scripts)
hermes-hud --text

# Save snapshot for diff tracking
hermes-hud --snapshot

# Neofetch variants
hermes-hud --ai        # AI awakening theme
hermes-hud --br        # Blade Runner theme
hermes-hud --fsociety  # Mr. Robot theme
hermes-hud --anime     # Mewtwo theme
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `1`-`9` | Switch tabs |
| `j` / `k` | Scroll down / up |
| `g` / `G` | Jump top / bottom |
| `r` | Refresh data |
| `q` | Quit |

## Tabs

### 1. Overview
- Agent identity: model, provider, backend
- Memory capacity: used/max, percentage
- Session count, total messages, total tokens
- Skill count, custom vs built-in
- Gateway status

### 2. Dashboard (Memory + Sessions + Skills)
- Memory entries by category (correction, preference, environment, project, todo)
- Daily session stats (last 7/30 days)
- Tool usage frequency
- Recently modified skills

### 3. Cron Jobs
- Job name, schedule, state (scheduled/paused/running)
- Next run time, last run status
- Error count, delivery target

### 4. Projects
- Git repos in `~/projects` (or `HERMES_HUD_PROJECTS_DIR`)
- Languages detected, uncommitted changes
- Last commit age

### 5. Health
- API keys present/missing (auto-discovered from .env)
- Services running: gateway, systemd, llama-server
- State DB size, Hermes dir exists

### 6. Corrections
- Every correction recorded in MEMORY.md
- Category breakdown
- Timeline of learning moments

### 7. Agents
- Live agent processes mapped to tmux panes
- Operator queue: pending approvals, errors
- Jump hints for quick navigation

### 8. Profiles
- All Hermes profiles: model, provider, toolsets
- Per-profile session/message/token counts
- Memory usage, cron job count
- Gateway/server status

### 9. Patterns
- Task clusters (auto-grouped by similarity)
- Repeated prompts (skill candidates)
- Hourly activity heatmap
- Common tool chains

## Data Sources

| Collector | Source | What It Reads |
|-----------|--------|---------------|
| Memory | `~/.hermes/memories/*.md` | Entries, categories, capacity |
| Sessions | `~/.hermes/state.db` | SQLite: sessions, messages, tokens |
| Skills | `~/.hermes/skills/*/SKILL.md` | Frontmatter, modification time |
| Cron | `~/.hermes/cron/jobs.json` | Job definitions, state, history |
| Health | `.env`, `ps`, `systemctl` | API keys, process status |
| Projects | `~/projects` (configurable) | Git repos, languages, commits |
| Patterns | `state.db` + MEMORY.md | Clustering, repetition detection |

## Snapshot and Diff Tracking

```bash
# Save baseline
hermes-hud --snapshot

# Later: compare (built into Diff tab)
# Shows: memory growth, new skills, session delta, token spend
```

Snapshots stored in `~/.hermes/.hud/snapshots.jsonl`.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HERMES_HOME` | `~/.hermes` | Agent data directory |
| `HERMES_HUD_PROJECTS_DIR` | `~/projects` | Git repo scan directory |
| `HERMES_HUD_NOBOOT` | unset | Skip boot animation |

## Themes

| Theme | Palette | Best For |
|-------|---------|----------|
| Neural Awakening | Blue/cyan on black | Default, clean |
| Blade Runner | Amber/pink on black | Warm, low light |
| fsociety | Green on black | Minimal, high contrast |
| Digital Soul | Purple/pink gradients | Visual variety |

Switch via command palette: `ctrl+p`

## Integration with Other Skills

- **Agent Dashboard**: HUD is terminal alternative to web dashboard. Same data, different UI.
- **Skill Factory**: Patterns tab shows repeated prompts - skill candidates.
- **Multi-Agent Orchestrator**: Agents tab tracks live workers, tmux pane mapping.
- **Trust Boundary**: Health tab monitors gateway status and API key presence.

## Anti-patterns

- Do NOT run HUD on production gateway port - it reads data, doesn't serve
- Do NOT use `--snapshot` as backup - it's metrics only, not full state
- Do NOT ignore health tab warnings - missing API keys = silent failures
- Do NOT run without `HERMES_HOME` set if using non-standard path

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "No Hermes data found" | Wrong `HERMES_HOME` | Set env var or symlink |
| Blank panels | state.db locked | Stop gateway, retry |
| Slow refresh | Large state.db | Archive old sessions |
| Missing skills | Skills not in `~/.hermes/skills/` | Check skill install path |
| Theme not applying | Terminal doesn't support truecolor | Use basic theme |

## For IEK AI 2026 / Tera / Detector

Typical monitoring workflow:
```bash
# Daily health check
hermes-hud --text | grep -E "(keys_missing|services_ok|memory_capacity)"

# Weekly growth review
hermes-hud --snapshot
# Compare with last week in Diff tab

# Cron monitoring (price scrapers, report generation)
# Tab 3: check all jobs green, no errors

# Cost tracking
# Tab 2: daily token usage, model breakdown
```
