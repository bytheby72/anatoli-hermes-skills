---
name: Hermes Wiki
version: 1.0.0
category: devops
description: Local read-only intelligence scanner for Hermes Agent and server. Maps code, skills, cron jobs, trust boundaries, server health, and cleanup candidates. No external uploads. Fail-closed.
tags: [diagnostics, security, monitoring, local-only, read-only]
---

# Hermes Wiki

Local X-ray for Hermes Agent and server. Read-only. Local-only. Fail-closed.

## Purpose

Understand what lives on the system without modifying anything:
- Code structure and capabilities
- Installed skills and their gaps
- Cron jobs and broken paths
- File trust boundaries (who can read/write/send)
- Server health and load
- Garbage accumulation
- Safe cleanup candidates

## When to Use

- Auditing system before changes
- Onboarding new workspace
- Troubleshooting broken cron jobs
- Finding security risks in scripts
- Planning cleanup
- Understanding skill dependencies
- Before deploying new automation

## When NOT to Use

- Do NOT use for real-time monitoring (use Agent HUD or Dashboard)
- Do NOT use as backup tool
- Do NOT use to modify files (read-only)
- Do NOT use on production without testing on staging first
- Do NOT use to extract secrets (explicitly blocked)

## Safety Rules

1. READ-ONLY: No file modifications, no deletions, no writes
2. LOCAL-ONLY: No cloud uploads, no remote APIs, no external embeddings
3. FAIL-CLOSED: Skip anything suspicious rather than risk exposure
4. SECRET-SAFE: Skip `.env`, tokens, keys, credentials entirely
5. NO AUTO-CLEANUP: All destructive commands require manual approval
6. REDACTION: Secret variable names printed as `<REDACTED>`

## Confidential Data Rules

- No real company names in public files
- No personal names in public files
- No real business data in examples
- No secrets in any output
- Synthetic examples only
- Generic documentation only

## Commands

| Command | Phase | Purpose |
|---------|-------|---------|
| `scan` | 1 | Build local indexes from filesystem |
| `cron-map` | 2 | Map cron jobs, detect broken paths |
| `skill-map` | 3 | Map skills, find missing docs/tests |
| `trust-map` | 4 | Classify files by capability and risk |
| `server-health` | 5 | CPU, RAM, disk, systemd, docker |
| `load-rank` | 6 | Rank top consumers |
| `garbage-map` | 7 | Find cleanup candidates |
| `cleanup-advisor` | 8 | Suggest cleanup with check commands |
| `ask "question"` | 9 | Query local index |
| `report` | 10 | Generate markdown report |
| `snapshot` | 11 | Save state for diff tracking |

## Inputs

- Filesystem paths: `~/.hermes/`, `~/projects/`, etc.
- Crontab: user and system
- System state: `/proc`, `ps`, `df`, `systemctl`, `docker`

## Outputs

- Local indexes: `~/.hermes/wiki/index/*.json`
- Reports: `~/.hermes/wiki/reports/report_*.md`
- Snapshots: `~/.hermes/wiki/snapshots/snapshot_*.json`
- stdout: markdown tables and summaries

## Failure Modes

| Failure | Behavior |
|---------|----------|
| Permission denied | Skip file, log warning |
| Secret file detected | Skip content, metadata only |
| Large file | Skip content, metadata only |
| Command not found | Skip section, continue |
| Index missing | Prompt to run scan first |
| No matches | Return "No matches found" |

## Acceptance Criteria

- [x] Scanner walks target dirs safely
- [x] Secret files skipped automatically
- [x] Sensitive env vars redacted
- [x] Python structure extracted (functions, classes, imports)
- [x] Network calls detected
- [x] File operations detected
- [x] Cron jobs mapped with broken path detection
- [x] Skills mapped with missing docs/tests detection
- [x] Trust boundaries classified
- [x] Server health collected
- [x] Load ranked
- [x] Garbage mapped with risk classes
- [x] Cleanup advisor suggests only, never executes
- [x] Query mode works over local index
- [x] Report generates locally
- [x] No destructive actions in any script
- [x] No secrets printed in output
- [x] No real company/personal names in public files

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| "No index found" | Run `scan` first |
| Permission denied | Run with appropriate user |
| Empty output | Check HERMES_HOME or use --path |
| Slow scan | Use --exclude for large dirs |

## Examples

### Scan workspace
```bash
python3 scripts/hermes_wiki.py scan
```

### Find broken cron jobs
```bash
python3 scripts/hermes_wiki.py cron-map
```

### Query capabilities
```bash
python3 scripts/hermes_wiki.py ask "Which scripts call external APIs?"
```

### Full report
```bash
python3 scripts/hermes_wiki.py report --save --include-server
```

## Integration

- Agent Dashboard: Reports visible in Files tab
- Agent HUD: Server health complements TUI monitoring
- Trust Boundary: Trust map feeds into security audit
- Skill Factory: Skill gaps identified for auto-generation

## Anti-patterns

- Do NOT run on untrusted systems
- Do NOT share reports containing path information
- Do NOT use as substitute for proper backup
- Do NOT ignore SECRET_OR_UNKNOWN classifications
- Do NOT auto-approve cleanup suggestions
