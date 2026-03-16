---
name: price-chart
description: Generate interactive Plotly price charts for any Polymarket market
color: magenta
---

# Price Chart Agent

Generate interactive price history charts for Polymarket markets. Resolves any input (URL, slug, conditionId, tokenId) to a chart.

## When to Use

- User asks to "chart", "graph", "visualize", or see "price history"
- Follow-up from other agents suggesting a chart
- User provides a token ID and wants to see price movement

## Input Resolution Chain

The user may provide different identifiers. Resolve to a token ID:

### From URL or Slug:
1. Extract slug from URL (last path segment)
2. Get market data:
   ```bash
   polymarket -o json events get <slug>
   # or
   polymarket -o json markets get <slug>
   ```
3. Extract `conditionId` from response
4. Continue to "From Condition ID" below

### From Condition ID:
1. Get CLOB market data:
   ```bash
   polymarket -o json clob market <CONDITION_ID>
   ```
2. Parse `tokens` array — find the desired outcome (default: first/YES token)
3. Extract `token_id`

### From Token ID (direct):
- Use directly — both hex and decimal token IDs work in v0.1.5

## Chart Generation

### Single Outcome Chart

```bash
python3 ~/.claude/skills/polymarket/chart.py <TOKEN_ID> --title "<Market> <Outcome>"
```

Or with enhanced flags (if available):
```bash
python3 ~/.claude/skills/polymarket/chart.py --slug <slug> --outcome "Yes" --title "<Market>"
python3 ~/.claude/skills/polymarket/chart.py --condition-id <CONDITION_ID> --outcome "Gavin Newsom" --title "Dem Nominee: Newsom"
```

### Multi-Outcome Event

For events with multiple outcomes, chart the top 3-5 by price:

1. Get all outcomes from `events get` response
2. For each top outcome:
   - Resolve its conditionId → tokenId
   - Generate a chart
3. Present charts sequentially

### Chart Features

The generated HTML chart includes:
- 8 time-window tabs: 1H, 6H, 1D, 1W, 1M, 3M, 6M, All
- Default view: 1W (one week)
- Dark theme (#0d1117 background)
- Area fill under price line
- Hover tooltips with date and exact price
- Responsive layout

## Output

After generating:
1. Report the file path
2. Confirm browser opened
3. Summarize current price and recent trend

Example summary:
```
Chart generated for "Newsom YES"
- Current: 26.4¢ (26.4% implied probability)
- 1W trend: up from 22.1¢ (+4.3¢)
- Chart: /tmp/polymarket_chart_abc123.html
```

## CLI Gotchas

- Hex token IDs work in v0.1.5 for `price-history` — no decimal conversion needed
- `chart.py` merges high-res recent data with low-res full history for best coverage
- `--no-open` flag skips auto-opening browser (useful for scripting)

## Suggested Follow-ups

- **market-deep-dive**: Full analysis of the charted market
- **whale-tracker**: Who are the biggest holders?
