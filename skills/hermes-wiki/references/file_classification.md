# File Classification

## By Extension

| Extension | Type | Scan Content | Notes |
|-----------|------|--------------|-------|
| `.py` | Python | Yes | Extract functions, classes, imports, calls |
| `.sh` | Bash | Yes | Extract commands, paths, redirects |
| `.bash` | Bash | Yes | Same as `.sh` |
| `.json` | JSON | Metadata only | Structure, keys. Skip values if secret keys |
| `.yaml` | YAML | Metadata only | Structure, keys. Skip values if secret keys |
| `.yml` | YAML | Metadata only | Same as `.yaml` |
| `.md` | Markdown | Yes | Extract headers, links, code blocks |
| `.txt` | Text | Metadata only | Size, line count |
| `.csv` | CSV | Metadata only | Column headers, row count |
| `.sql` | SQL | Yes | Extract tables, operations |
| `.js` | JavaScript | Yes | Extract functions, requires, fetch calls |
| `.ts` | TypeScript | Yes | Same as `.js` |
| `.html` | HTML | Metadata only | Links, forms |
| `.css` | CSS | No | Skip content |
| `.log` | Log | Tail only | Last 50 lines, redact secrets |
| `.pid` | PID | Metadata only | Process ID |
| `.db` | Database | Metadata only | Size, tables (if SQLite) |
| `.sqlite` | SQLite | Metadata only | Same as `.db` |
| `.sqlite3` | SQLite | Metadata only | Same as `.db` |
| `.env` | Secrets | **NO** | Metadata only: exists, size, permissions |
| `.key` | Secrets | **NO** | Metadata only |
| `.pem` | Secrets | **NO** | Metadata only |
| `.p12` | Secrets | **NO** | Metadata only |
| `.kube` | Secrets | **NO** | Metadata only |

## By Path Pattern

| Pattern | Classification | Action |
|---------|---------------|--------|
| `*/secrets/*` | SECRET | Metadata only |
| `*/private/*` | SECRET | Metadata only |
| `*/credentials/*` | SECRET | Metadata only |
| `*/.env*` | SECRET | Metadata only |
| `*/token*` | SECRET | Metadata only |
| `*/auth*` | SECRET | Metadata only |
| `*/backup/*` | REVIEW | Metadata + age |
| `*/archive/*` | REVIEW | Metadata + age |
| `*/tmp/*` | TEMP | Full scan if safe |
| `*/cache/*` | CACHE | Full scan if safe |
| `*/logs/*` | LOG | Tail only |
| `*/reports/*` | REPORT | Metadata + structure |
| `*/skills/*` | SKILL | Full scan |
| `*/scripts/*` | SCRIPT | Full scan |
| `*/tests/*` | TEST | Full scan |
| `*/docs/*` | DOC | Full scan |
| `*/config/*` | CONFIG | Metadata + keys |
