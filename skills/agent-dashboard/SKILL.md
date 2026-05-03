---
name: Agent Dashboard
version: 1.0.0
category: devops
description: Self-hosted web dashboard for managing multiple Hermes Agent instances, sessions, cron jobs, and token analytics from a single pane.
tags: [dashboard, monitoring, multi-agent, web-ui, operations]
---

# Agent Dashboard

Centralized control panel for Hermes Agent fleet. One interface - all profiles, sessions, analytics, file access.

## When to Activate

- Managing 2+ Hermes Agent profiles (e.g., Ara for IEK, Tera for Detector)
- Need real-time monitoring of agent sessions, token usage, costs
- Running scheduled cron jobs and want visual control
- Team access required with role-based permissions
- Remote management without SSH

## What It Replaces

- Manual `hermes` CLI switching between profiles
- `htop` + `tail -f` for monitoring
- Spreadsheet tracking of token costs
- Direct file editing via SSH/nano

## Architecture

```
Browser  <--WebSocket/HTTP-->  Node.js Express Server  <--CLI/PTY-->  Hermes Agent
         |                                          |
         +-- xterm.js terminal                      +-- SQLite (sessions, analytics)
         +-- Dark/Light theme                       +-- bcrypt auth + RBAC
         +-- File explorer (scoped)                 +-- Cron job management
```

**Stack:** Vanilla JS + Vite, Node.js 20+, Express, WebSocket, node-pty, xterm.js, SQLite

## Installation

### Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Node.js   | v18     | v20 LTS     |
| RAM       | 512 MB  | 1 GB        |
| Disk      | 200 MB  | 500 MB      |
| OS        | Linux   | Ubuntu 22.04|

### Quick Start

```bash
git clone https://github.com/xaspx/hermes-control-interface.git agent-dashboard
cd agent-dashboard
npm install

# Configure
cp .env.example .env
# Edit .env:
#   HERMES_CONTROL_PASSWORD=your-secure-password
#   HERMES_CONTROL_SECRET=$(openssl rand -hex 32)

npm run build
npm start
```

Access: `http://localhost:10272`

### Production (systemd)

```ini
# /etc/systemd/system/agent-dashboard.service
[Unit]
Description=Hermes Agent Dashboard
After=network.target

[Service]
Type=simple
User=hermes
WorkingDirectory=/opt/agent-dashboard
ExecStart=/usr/bin/node server.js
Restart=always
Environment=HERMES_CONTROL_PASSWORD=secure-password
Environment=HERMES_CONTROL_SECRET=your-secret

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable agent-dashboard
sudo systemctl start agent-dashboard
```

## Core Features

### 1. Multi-Agent Management

| Action | How |
|--------|-----|
| List profiles | Home -> Agents tab |
| Create profile | Agents -> "New Profile" |
| Clone profile | Agents -> profile menu -> "Clone" |
| Start/Stop gateway | Agents -> toggle or per-agent Gateway tab |
| Set default | Agents -> star icon |

### 2. Chat Interface

- **Tool Call Cards**: Collapsible JSON viewer for each tool execution
- **Session Sidebar**: Resume any past session with one click
- **Session Export**: JSON transcript download
- **Clean Output**: Banner suppression for noise-free responses

### 3. Token Analytics

| Metric | Source |
|--------|--------|
| Sessions count | SQLite query on session metadata |
| Total tokens | Sum of input + output per session |
| Cost by model | `@pydantic/genai-prices` integration |
| Top tools | Frequency analysis of tool_calls table |
| Platform breakdown | CLI vs Telegram vs WhatsApp usage |

Time ranges: Today, 7d, 30d, 90d. Per-profile or combined.

### 4. Cron Job Management

- Create: hourly, daily, weekly, or custom cron expression
- Pause/Resume without deleting
- Run on-demand (immediate execution)
- Edit schedule or command inline
- Next run time display

### 5. File Explorer

- Scoped to `~/.hermes` (configurable via `HERMES_CONTROL_ROOTS`)
- Path traversal prevention
- Split view: tree left, editor right
- Syntax highlighting for YAML, JSON, JS, Python

### 6. RBAC (Role-Based Access Control)

| Role | Permissions |
|------|-------------|
| admin | Full access (20/20 permissions) |
| viewer | Read-only: view agents, sessions, analytics |
| custom | Select from 20 granular permissions |

Critical endpoints (`/api/plugins`, user management) require admin role.

## Security Checklist

Before production deployment:

- [ ] Change default password to 16+ character strong password
- [ ] Generate unique `HERMES_CONTROL_SECRET` (32+ hex chars)
- [ ] Enable HTTPS (reverse proxy with nginx/traefik)
- [ ] Set `Secure` cookie flag (auto-detected)
- [ ] Configure firewall: only trusted IPs to port 10272
- [ ] Review RBAC: minimum permissions per user
- [ ] Enable audit log review (activity log in Maintenance tab)
- [ ] Set up backup schedule (Maintenance -> Backup)

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `HERMES_CONTROL_PASSWORD` | Yes | Login password (bcrypt hashed) |
| `HERMES_CONTROL_SECRET` | Yes | CSRF + session signing secret |
| `PORT` | No | Server port (default: 10272) |
| `HERMES_CONTROL_HOME` | No | Hermes home dir (default: ~/.hermes) |
| `HERMES_CONTROL_ROOTS` | No | File explorer roots (JSON array) |

## Integration with Other Skills

- **Skill Factory**: Generated skills appear in Skills Marketplace tab
- **Hermes HUD**: TUI alternative for terminal-only environments
- **Maestro**: Dashboard manages Maestro-orchestrated multi-agent setups

## Anti-patterns

- Do NOT expose port 10272 directly to internet without HTTPS
- Do NOT use default password in production
- Do NOT grant admin role to viewers
- Do NOT store `HERMES_CONTROL_SECRET` in version control

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Port already in use" | Another HCI instance running | `kill $(lsof -t -i:10272)` |
| Blank page after build | Vite build failed | `npm run build` check for errors |
| Terminal not connecting | node-pty build failed | `npm rebuild` with python3, make, g++ |
| Auth loop | Secret mismatch | Regenerate `HERMES_CONTROL_SECRET`, clear cookies |
| High memory usage | Too many WebSocket connections | Restart service, check concurrent users |
