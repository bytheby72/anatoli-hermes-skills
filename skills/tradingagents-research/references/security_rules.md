# Security Rules

What never goes into public files. Fail-closed enforcement.

## Automatic Redaction

The following are replaced with placeholders in all output:

| Pattern | Replacement | Example |
|---------|-------------|---------|
| Stock tickers | [TICKER] | AAPL, TSLA |
| Dollar amounts | [PRICE] | $123.45 |
| Dates | [DATE] | 2024-01-15 |
| URLs | [URL] | https://... |
| Email addresses | [EMAIL] | user@domain.com |
| API keys | [API_KEY] | sk-... |
| Tokens | [TOKEN] | ghp_... |
| IP addresses | [IP] | 192.168.1.1 |
| Real names | [NAME] | John Smith |
| Company names | [COMPANY] | Acme Corp |

## Commit Blockers

These will block commit and alert human:

- Hardcoded API keys or tokens
- Passwords in plain text
- Private keys (RSA, EC, etc.)
- AWS access keys
- Real financial data in examples
- Real customer names or addresses
- Internal network paths (/home/username, /Users/username)

## Allowed in Public Files

- Generic examples ([TICKER], [PRICE])
- Synthetic data (randomized, clearly fake)
- Architecture descriptions (no implementation details)
- Role definitions (no real prompts with keys)
- Flow diagrams (no real endpoints)

## Cloud Policy

| Approach | Status |
|----------|--------|
| Local-only execution | Preferred |
| Self-hosted with VPN | Acceptable |
| Cloud API with encryption review | Requires approval |
| Public cloud with data upload | Blocked |

## Fail-Closed Rules

1. When in doubt, redact.
2. When uncertain, escalate to human.
3. Validator can block without explanation.
4. No auto-execution without human gate.
5. All decisions logged, all logs audited.
