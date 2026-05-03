# Hermes Wiki

Local X-ray for Hermes Agent and server. Read-only diagnostics. No external uploads.

## What It Does

Answers questions:
- Where is the code?
- Which script does what?
- Which cron job is broken?
- Which file can read documents?
- Which file can send data outside?
- What loads the server?
- Where is garbage accumulated?
- What can be considered for cleanup?
- Which check commands to run?

## Safety Rules

- **READ-ONLY by default** - never modifies files
- **LOCAL-ONLY** - no cloud, no remote DB, no external uploads
- **FAIL-CLOSED** - skips anything suspicious
- **NO SECRETS** - skips `.env`, tokens, keys, credentials
- **NO AUTO-CLEANUP** - suggests only, marks all destructive commands as MANUAL_APPROVAL_REQUIRED

## Quick Start

```bash
cd skills/hermes-wiki/scripts

# Build indexes
python3 hermes_wiki.py scan

# Query
python3 hermes_wiki.py ask "Which scripts call external APIs?"
python3 hermes_wiki.py ask "Which cron jobs are broken?"

# Maps
python3 hermes_wiki.py cron-map
python3 hermes_wiki.py skill-map
python3 hermes_wiki.py trust-map

# Server diagnostics
python3 hermes_wiki.py server-health
python3 hermes_wiki.py load-rank
python3 hermes_wiki.py garbage-map
python3 hermes_wiki.py cleanup-advisor

# Report
python3 hermes_wiki.py report --save --include-server
```

## Commands

| Command | Purpose |
|---------|---------|
| `scan` | Walk filesystem, build local indexes |
| `cron-map` | Map cron jobs, detect broken paths |
| `skill-map` | Map installed skills, find missing docs/tests |
| `trust-map` | Classify files by capability and risk |
| `server-health` | CPU, RAM, disk, systemd, docker summary |
| `load-rank` | Rank top consumers |
| `garbage-map` | Find cleanup candidates |
| `cleanup-advisor` | Suggest cleanup with check commands |
| `ask "question"` | Query local index |
| `report` | Generate markdown report |
| `snapshot` | Save state for diff tracking |

## Risk Classes

| Class | Meaning |
|-------|---------|
| LOW | Read-only, no network |
| MEDIUM | File write OR network, no secrets |
| HIGH | Reads files AND has network |
| CRITICAL | Handles secrets AND can send externally |
| SECRET_OR_UNKNOWN | Skipped file or confidential path |

## Cleanup Risk Classes

| Class | Action |
|-------|--------|
| SAFE_CLEAN | Known temp/cache, easily regenerated |
| REVIEW_FIRST | Might contain useful data |
| DANGEROUS | System files, logs, backups |
| SECRET_OR_UNKNOWN | Never auto-clean |

## Storage

All data stored locally only:
- `~/.hermes/wiki/index/` - searchable indexes
- `~/.hermes/wiki/reports/` - generated reports
- `~/.hermes/wiki/snapshots/` - state snapshots

## Tests

```bash
cd skills/hermes-wiki/tests
python3 test_redaction.py
python3 test_secret_skipping.py
python3 test_cron_map.py
python3 test_trust_map.py
python3 test_cleanup_classification.py
python3 test_no_destructive_actions.py
```

## Requirements

- Python 3.9+
- Standard library only (no pip install needed)
- Linux/macOS

## License

MIT
