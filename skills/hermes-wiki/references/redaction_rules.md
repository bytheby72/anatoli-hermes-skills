# Redaction Rules

## Secret Filename Patterns (skip content, metadata only)

Skip if basename matches:
- `.env`
- `*token*`
- `*credential*`
- `*secret*`
- `*private*`
- `id_rsa`
- `id_ed25519`
- `*cookie*`
- `*session*`
- `*auth*`
- `*.pem`
- `*.p12`
- `*.kube`
- `google_token`
- `gmail_token`
- `*key*` (when paired with secret indicators)

## Secret Variable Name Patterns (redact value)

Redact value if name contains:
- `KEY`
- `TOKEN`
- `SECRET`
- `PASSWORD`
- `CREDENTIAL`
- `COOKIE`
- `SESSION`
- `PRIVATE`
- `AUTH`
- `BEARER`

Output format: `VARIABLE_NAME=<REDACTED>`

## Confidential Path Indicators

Paths containing these are classified SECRET_OR_UNKNOWN:
- `.env`
- `secret`
- `private`
- `credential`
- `token`
- `auth`
- `cookie`
- `session`
- `backup`
- `archive`
- `confidential`
- `internal`
