---
name: Skill Factory
version: 1.0.0
category: meta
description: Meta-skill that observes workflows and auto-generates reusable Hermes skills from live sessions. Turns repeated work into procedural memory.
tags: [meta, automation, skills, learning, knowledge-management]
---

# Skill Factory

Automated skill generation from real work. No manual documentation - the agent watches, detects patterns, and proposes reusable skills.

## When to Activate

- After solving 3+ similar tasks in one session
- When user says "save this", "remember this workflow", "turn into skill"
- Before session end - capture everything repeatable
- When onboarding new agent instances with same domain
- Building team knowledge base for business automation 0026 trade operations

## Core Principle

Every repeated workflow is a skill waiting to be born. Capture it once, reuse forever.

## How It Works

```
Session Activity
    |
    v
Pattern Detection (2+ repetitions OR explicit request)
    |
    v
Skill Proposal (agent asks: generate A/B/C/D?)
    |
    v
File Generation
    ├── SKILL.md  -> ~/.hermes/skills/<category>/<name>/
    └── plugin.py -> ~/.hermes/plugins/
    |
    v
Activation (hermes skills reload)
```

## Trigger Conditions

| Trigger | Example |
|---------|---------|
| Explicit request | "Save this as skill", "Remember how to do this" |
| Repeated pattern | Same 3+ step workflow used twice in session |
| Session wrap-up | User says "done", "that's all" |
| Frustration signal | "I always do this manually..." |
| Slash command | `/skill-factory propose` |

## Commands

| Command | Action |
|---------|--------|
| `/skill-factory propose` | Analyze session, propose top skill now |
| `/skill-factory list` | Skills generated this session |
| `/skill-factory status` | Events tracked, queue size |
| `/skill-factory queue` | Pending pattern proposals |
| `/skill-factory save <name>` | Save last proposal with custom name |
| `/skill-factory clear` | Reset session tracker |

## Skill Generation Format

### SKILL.md Template

```markdown
---
name: <Skill Name>
version: 1.0.0
category: <category>
description: <one-line>
tags: [tag1, tag2]
---

# <Skill Name>

## When to Activate

- Condition 1
- Condition 2

## Workflow

### Phase 1: <Name>

**Steps:**
1. Concrete step
2. Concrete step

**Checks:**
- [ ] Verification point

## Quality Checklist

- [ ] Check 1
- [ ] Check 2

## Examples

### Example 1: <Real scenario from session>

<Concrete commands and output>

## Anti-patterns

- Do NOT <wrong approach>
- Avoid <common mistake>

## Integration

- Works with: <related skill>
```

### plugin.py Template

```python
"""
<Skill Name> Plugin
<Description>

Install: cp <name>.py ~/.hermes/plugins/
Usage:   /<name> [args]
"""

PLUGIN_NAME = "<name>"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "<description>"

def register(hermes):
    @hermes.command(
        name="<name>",
        description="<description>",
        usage="/<name> [args]"
    )
    async def run_skill(ctx, args: str = ""):
        # Step 1: <description>
        # Step 2: <description>
        pass
```

## Naming Rules

| Rule | Good | Bad |
|------|------|-----|
| kebab-case | `price-parser` | `PriceParser` |
| Domain prefix | `valuation-report` | `valuation` |
| Action verb first | `parse-price-list` | `price-list` |
| No versions in name | `tender-scraper` | `tender-scraper-v2` |

## Quality Standards

Generated skills MUST:
- Include at least one real example from triggering session
- Define clear activation conditions
- Stay under 600 lines
- Explain WHY, not just WHAT
- List integration with existing skills

## For business automation 0026 trade operations

Common patterns to capture:
- Price parsing workflows (AVS.by, ankron.by, e-electric.ru)
- 1C report analysis pipeline
- Currency normalization routine
- Competitor displacement analysis
- Field work plan generation (per-employee)
- Tender pattern analysis from BUTB

## Installation

```bash
git clone https://github.com/Romanescu11/hermes-skill-factory.git

cp hermes-skill-factory/skills/skill-factory/SKILL.md \
   ~/.hermes/skills/meta/skill-factory/

cp hermes-skill-factory/plugins/skill_factory.py \
   ~/.hermes/plugins/

hermes skills reload
hermes skills enable skill-factory
```

## Integration with Agent Dashboard

Generated skills appear automatically in:
- Skills Marketplace tab (category grouping)
- Agent detail -> Skills tab (per-profile)
- Update checker (new versions from registry)

## Anti-patterns

- Do NOT generate skills for one-off tasks
- Do NOT create skills without real session examples
- Do NOT skip quality checklist
- Do NOT version in filename (use git for versions)
