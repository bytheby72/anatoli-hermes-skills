# Troubleshooting

## Scanner Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Permission denied" | Scanner lacks read access | Run with appropriate user or sudo |
| "Path does not exist" | HERMES_HOME not set | Set HERMES_HOME or use --path |
| "Index corrupt" | Interrupted write | Delete ~/.hermes/wiki/index/ and re-run scan |
| "Out of memory" | Large directory tree | Use --exclude to skip large dirs |

## Query Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| "No results" | Index not built | Run scan first |
| "Too many results" | Broad query | Narrow with file type or path filter |
| "Slow response" | Large index | Use --limit or rebuild with exclusions |

## Server Health Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| "command not found" | Missing system tools | Install procps, systemd, docker |
| "No docker data" | Docker not running | Start docker service |
| "Permission denied" | Need sudo for some metrics | Run with appropriate privileges |

## Report Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Report empty" | No scan data | Run scan first |
| "Secrets in output" | Redaction failed | Check redaction_rules.md, file issue |
| "Too large" | Long history | Use --since to limit time range |
