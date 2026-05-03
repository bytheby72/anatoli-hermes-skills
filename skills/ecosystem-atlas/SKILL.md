---
name: Ecosystem Atlas
version: 1.0.0
category: research
description: Navigate the Hermes Agent ecosystem - 100+ tools, skills, and integrations. Community-curated directory with RAG-powered search and live trending data.
tags: [ecosystem, discovery, skills, tools, research]
---

# Ecosystem Atlas

Community-curated map of the Hermes Agent ecosystem. Find tools, skills, integrations, and deployment templates. RAG-powered chatbot for natural language discovery.

## When to Activate

- Starting new project - find existing tools before building
- Evaluating alternatives - compare skills by stars, activity, category
- Onboarding new team members - show available capabilities
- Keeping up with ecosystem growth - trending repos, new releases
- Troubleshooting - find community solutions to common problems
- Contributing - identify gaps in ecosystem coverage

## What It Replaces

- Manual GitHub search for Hermes-related projects
- Bookmark lists of tools and skills
- Word-of-mouth discovery of community projects
- Reading dozens of READMEs to understand capabilities

## Architecture

```
hermesatlas.com (Vercel)
    |
    +-- index.html          # Single-page app, no build step
    +-- api/stars.js        # GitHub GraphQL + Redis cache
    +-- api/stars-history.js# 30-day sparkline data
    +-- api/chat.js         # RAG pipeline with streaming
    |
    +-- data/repos.json     # 111 quality-filtered repos
    +-- data/chunks.json    # Pre-computed embeddings (520 chunks)
    |
    +-- research/           # 27 source-of-truth files
    +-- scripts/            # Build chunks, test RAG
```

**Stack:** Vanilla HTML/CSS/JS, Vercel serverless, Redis Cloud, OpenRouter

## Data Structure

### Repo Entry

```json
{
  "name": "hermes-control-interface",
  "owner": "xaspx",
  "description": "Self-hosted web dashboard for Hermes Agent",
  "category": "devops",
  "stars": 234,
  "trending": true,
  "added_at": "2026-03-15",
  "tags": ["dashboard", "web-ui", "monitoring"]
}
```

### Categories (12 total)

| Category | Count | Examples |
|----------|-------|----------|
| devops | 18 | dashboards, deployment, monitoring |
| skills | 22 | skill packs, templates, factories |
| security | 8 | guards, audits, hardening |
| creative | 12 | image gen, music, video |
| data | 10 | scrapers, parsers, analyzers |
| integrations | 15 | platform connectors, APIs |
| mlops | 8 | training, inference, evaluation |
| research | 5 | papers, benchmarks, datasets |
| productivity | 7 | docs, spreadsheets, presentations |
| gaming | 4 | game servers, emulators |
| smart-home | 3 | IoT, home automation |
| misc | 4 | utilities, experiments |

## Features

### Browse
- Filter by category, tags, trending status
- Sort by stars, recent activity, name
- Search by keyword in name/description
- Light/dark mode with OS preference detection

### Trending
- Sparklines showing 30-day star growth
- Weekly star delta badges
- "Featured this week" rotating community pick
- Recently added highlights

### Ask the Atlas (RAG Chatbot)

Natural language queries grounded in 27 research files:

| Query Type | Example |
|------------|---------|
| Capability | "Which skills help with web scraping?" |
| Comparison | "What's the difference between HUD and Dashboard?" |
| Setup | "How do I deploy Hermes on a VPS?" |
| Troubleshooting | "Why is my gateway not starting?" |
| Discovery | "What's new this week?" |

**RAG Pipeline:**
1. Query rewriting (conversation-aware)
2. Hybrid retrieval: BM25 + cosine similarity
3. MMR re-ranking for diversity
4. Streaming response via OpenRouter

**Models:** Gemma 4 31B (primary) -> Gemma 4 26B -> Gemini 3 Flash (fallback)

## Using the Data Locally

```bash
git clone https://github.com/ksimback/hermes-ecosystem.git
cd hermes-ecosystem

# Browse raw data
cat data/repos.json | jq '.[] | select(.category == "devops")'

# Search by tag
cat data/repos.json | jq '.[] | select(.tags | contains(["scraping"]))'

# Check trending
cat data/repos.json | jq '.[] | select(.trending == true)'
```

## API Endpoints (when deployed)

| Endpoint | Purpose | Cache |
|----------|---------|-------|
| `/api/stars?repo=owner/name` | Live star count | Redis, 1hr TTL |
| `/api/stars-history?repo=owner/name` | 30-day history | Redis, daily snapshot |
| `/api/chat` | RAG chatbot | None (streaming) |

## Quality Filtering Criteria

Repos must pass all checks:
- Built for or integrated with Hermes Agent
- Created after July 22, 2025 (Hermes repo creation)
- Not a personal pet project or assignment
- Shows genuine effort and ecosystem value
- Basic security review passed
- README explains purpose and usage

## Integration with Other Skills

- **Skill Factory**: Atlas shows skill gaps - opportunities for auto-generation
- **Agent Dashboard**: Links to Atlas for discovering new skills to install
- **Multi-Agent Orchestrator**: Atlas helps find specialist tools for task decomposition
- **Agent HUD**: Patterns tab correlates with Atlas trending data

## Anti-patterns

- Do NOT treat star count as quality metric - check last commit date, issue response
- Do NOT install every trending skill - evaluate relevance to your domain
- Do NOT ignore security review status - unreviewed repos may have risks
- Do NOT rely solely on RAG chatbot for critical decisions - verify with source repo

## For IEK AI 2026 / Tera / Detector

Relevant categories and repos:

| Need | Category | Search Terms |
|------|----------|--------------|
| Price monitoring | data | scraper, parser, monitoring |
| Excel reports | productivity | spreadsheet, excel, csv |
| Tender analysis | data | butb, tender, procurement |
| Field work plans | productivity | planner, okr, field |
| Competitor intel | data | scraper, price, competitor |
| Multi-agent setup | devops | orchestrator, maestro, kanban |
| Security hardening | security | guard, camel, audit |
| 1C integration | integrations | 1c, accounting, erp |

Workflow:
1. Search Atlas for existing solutions
2. Evaluate: stars, last update, README quality
3. Test in isolated profile
4. If gap found - build and submit to Atlas

## Contributing

Submit repo via GitHub issue:
```
Repo: https://github.com/username/repo-name
Category: data
Tags: [scraper, price-monitoring, belarus]
Why: Parses electrical product catalogs for competitive analysis
```

## Live Site

**https://hermesatlas.com**

- No account needed
- No data collection
- Open source (MIT)
