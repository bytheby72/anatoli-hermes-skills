# Anatoli Hermes Skills

> Production-ready skill packs for IEK AI 2026, Tera, and Detector operations.
> Curated, battle-tested, privacy-first.

## Skills

| Skill | Category | Purpose |
|-------|----------|---------|
| [Agent Dashboard](skills/agent-dashboard/) | devops | Self-hosted web dashboard for multi-agent management |
| [Skill Factory](skills/skill-factory/) | meta | Auto-generate reusable skills from live sessions |
| [Trust Boundary](skills/trust-boundary/) | security | Runtime guard against prompt injection (CaMeL) |
| [Multi-Agent Orchestrator](skills/multi-agent-orchestrator/) | devops | Parallel specialist agents with structured handoffs |
| [Agent HUD](skills/agent-hud/) | devops | Terminal TUI monitoring for Hermes Agent state |
| [Ecosystem Atlas](skills/ecosystem-atlas/) | research | Community-curated map of 100+ tools and skills |

## Quick Start

```bash
git clone https://github.com/anatoli-piakhouski/anatoli-hermes-skills.git
cd anatoli-hermes-skills

# Install Agent Dashboard skill
cp skills/agent-dashboard/SKILL.md ~/.hermes/skills/devops/agent-dashboard/

# Install Skill Factory skill
cp skills/skill-factory/SKILL.md ~/.hermes/skills/meta/skill-factory/

hermes skills reload
```

## Philosophy

- **Local-first**: All tools run on your infrastructure
- **Privacy-first**: No data leaves your network
- **Actionable**: Concrete steps, not vague guidance
- **Integrated**: Skills reference each other, form ecosystem

## License

MIT
