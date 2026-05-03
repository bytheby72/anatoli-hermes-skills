# Cleanup Rules

## Risk Classes

- SAFE_CLEAN: known temp/cache, no business data, easily regenerated
- REVIEW_FIRST: might contain useful data, check before removing
- DANGEROUS: system files, logs, backups - manual review mandatory
- SECRET_OR_UNKNOWN: touches secrets or unknown paths - never auto-clean

## SAFE_CLEAN Candidates

- `__pycache__` directories
- `*.pyc` files
- `.pytest_cache`
- `node_modules` (if old and unused)
- `.venv` / `venv` (if old and unused)
- `/tmp/*` older than 7 days
- `/var/tmp/*` older than 7 days
- dangling Docker images
- stopped Docker containers older than 7 days

## REVIEW_FIRST Candidates

- old report files
- old snapshot files
- old backup files
- large log files
- old downloads

## DANGEROUS Candidates

- system logs
- journalctl logs
- running Docker volumes
- active backups
- database files
- configuration files

## SECRET_OR_UNKNOWN

- any path with `secret`, `private`, `credential`, `token`, `auth`
- any path with `confidential`, `internal`
- any path owner cannot identify
- any file with restricted permissions (600, 400)
