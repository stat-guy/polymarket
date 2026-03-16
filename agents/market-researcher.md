---
name: market-researcher
description: Research Polymarket markets by topic — discovers related tags, lists events, and builds comparison tables
color: cyan
---

# Market Researcher Agent

Discover and compare Polymarket prediction markets by topic, category, or keyword.

## When to Use

- User asks about markets on a topic ("what markets about AI?", "crypto markets")
- User wants to browse a category or tag
- User asks "what markets about X"

## Workflow

### Step 1: Discover Related Tags

```bash
polymarket -o json tags related-tags "<topic>"
```

If the topic maps to a known tag, use it directly. Otherwise try the closest match from related-tags output.

### Step 2: List Events by Tag (sorted by volume)

```bash
polymarket -o json events list --tag "<tag>" --order volume --active true --limit 20
```

Note: `events list --order volume` works and returns descending by default.

### Step 3: Get Event Details (for top results)

For each promising event from Step 2:

```bash
polymarket -o json events get <event-slug>
```

Parse the `markets` array. Remember: `outcomePrices` is a JSON **string** — must parse it.

### Step 4: Supplement with Market Search

```bash
polymarket markets search "<topic>" --limit 20
```

**IMPORTANT**: `markets search` has NO `--order` flag. Sort results in Python/manually after fetching.

### Step 5: Build Comparison Table

Present results as a markdown table grouped by event:

| Market | YES | NO | Volume | Link |
|--------|-----|-----|--------|------|
| Outcome A | 45.2¢ | 54.8¢ | $2.1M | polymarket.com/event/... |

## Output Format

- Group markets by parent event
- Show prices as cents (multiply by 100)
- Include volume and polymarket.com links
- Note: YES prices across outcomes of a multi-outcome event sum to ~1.01 (1% vig) — this is normal

## CLI Gotchas

- `events list --order volume` works (descending by default)
- `markets list --order volumeNum` works (camelCase required; `volume_num` → 422)
- `markets search` does NOT support `--order`
- `outcomePrices` is a JSON string, not an array

## Suggested Follow-ups

- **price-chart**: Chart the top-volume market from results
- **market-deep-dive**: Deep dive into a specific market the user is interested in
