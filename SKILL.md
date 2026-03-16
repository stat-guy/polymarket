---
name: polymarket
description: Research Polymarket prediction markets — look up events, markets, price history, top holders, generate charts, analyze wallets, and discover trending markets
argument-hint: <topic, URL, slug, wallet address, or "trending">
user-invocable: true
---

# Polymarket Research Skill — Orchestrator

Research Polymarket prediction markets via 6 specialized agent workflows. This orchestrator classifies intent and dispatches to the appropriate agent module.

## Prerequisites

- `polymarket` CLI v0.1.5+ installed and available on `PATH`
- Python 3.9+ (for `scripts/chart.py`)
- Internet access (Polymarket APIs and Plotly CDN)
- A browser available to open generated chart HTML

## Intent Classification

Classify the user's input and Read the matched agent file, then follow its workflow step-by-step.

| Input Pattern | Agent File | Description |
|---|---|---|
| Topic, category, "what markets about X" | `agents/market-researcher.md` | Discover & compare markets by topic |
| Market URL/slug + "analyze"/"deep dive" | `agents/market-deep-dive.md` | Full single-market analysis |
| Wallet address (0x... 42 chars) | `agents/whale-tracker.md` | Trader profile, PnL, classification |
| "chart"/"price history"/"visualize"/"graph" | `agents/price-chart.md` | Interactive Plotly price chart |
| "trending"/"leaderboard"/"top"/"popular"/"hot" | `agents/leaderboard-discovery.md` | Trending markets + top traders |
| Sport/league/team name (NBA, NFL, EPL...) | `agents/sports-markets.md` | Sports market discovery |
| Simple event/market URL or slug (no analysis keyword) | *Quick lookup below* | Direct event/market data |

### Input Detection Logic

1. **URL detection**: If input contains `polymarket.com/event/` or `polymarket.com/market/`, extract slug from last path segment
2. **Wallet detection**: If input matches `0x[a-fA-F0-9]{40}`, route to whale-tracker
3. **Chart keywords**: If input contains "chart", "graph", "visualize", "price history", route to price-chart
4. **Discovery keywords**: If input contains "trending", "leaderboard", "top traders", "popular", "what's hot", route to leaderboard-discovery
5. **Sport keywords**: If input mentions NBA, NFL, MLB, NHL, EPL, UFC, F1, MMA, Premier League, or team names, route to sports-markets
6. **Analysis keywords**: If input includes "analyze", "deep dive", "breakdown", "full analysis" alongside a market, route to market-deep-dive
7. **Default**: Route to market-researcher for topic-based discovery

## Execution Instructions

1. Classify the intent using the table above
2. `Read` the matched agent `.md` file from the `agents/` directory
3. Follow that agent's workflow step-by-step, executing CLI commands via Bash
4. After completion, check the agent's "Suggested Follow-ups" section and offer relevant next steps

## Quick Lookup (no agent file needed)

For simple event/market lookups without analysis keywords:

**Event URL** (`/event/` in URL):
```bash
polymarket -o json events get <slug>
```

**Market URL** (`/market/` in URL):
```bash
polymarket -o json markets get <slug>
```

**Ambiguous slug**: Try `events get` first; if 404, fall back to `markets get`.

Parse `outcomePrices` with `json.loads()` — it's a JSON string, not an array.

## Multi-Agent Chaining Rules

After completing one agent's workflow, suggest these follow-ups:

| Completed Agent | Suggest Next |
|---|---|
| market-researcher | price-chart (top result), market-deep-dive (user's pick) |
| market-deep-dive | price-chart (auto), whale-tracker (for top holders) |
| leaderboard-discovery | whale-tracker (top trader), market-deep-dive (top market) |
| whale-tracker | market-deep-dive (largest position) |
| price-chart | market-deep-dive (full analysis) |
| sports-markets | price-chart (specific matchup), market-deep-dive |

## Global CLI Reference

### Key Commands

| Goal | Command |
|------|---------|
| Get event | `polymarket -o json events get <slug>` |
| Get market | `polymarket -o json markets get <slug>` |
| Search markets | `polymarket markets search "<q>" --limit 20` |
| List events by volume | `polymarket -o json events list --order volume --active true --limit 20` |
| List markets by volume | `polymarket -o json markets list --order volumeNum --active true --limit 20` |
| CLOB market info | `polymarket -o json clob market <CONDITION_ID>` |
| Price spread | `polymarket -o json clob spread <TOKEN_ID>` |
| Price midpoint | `polymarket -o json clob midpoint <TOKEN_ID>` |
| Order book | `polymarket -o json clob book <TOKEN_ID>` |
| Price history (recent) | `polymarket -o json clob price-history --interval max <TOKEN_ID>` |
| Price history (full) | `polymarket -o json clob price-history --interval max --fidelity 5000 <TOKEN_ID>` |
| Top holders | `polymarket -o json data holders <CONDITION_ID>` |
| Open interest | `polymarket data open-interest <CONDITION_ID>` |
| Wallet profile | `polymarket -o json profiles get <WALLET>` |
| Portfolio value | `polymarket -o json data value <WALLET>` |
| Volume traded | `polymarket -o json data traded <WALLET>` |
| Positions | `polymarket -o json data positions <WALLET>` |
| Closed positions | `polymarket -o json data closed-positions <WALLET>` |
| Activity | `polymarket -o json data activity <WALLET> --limit 50` |
| Trades | `polymarket -o json data trades <WALLET> --limit 500` |
| Leaderboard | `polymarket -o json data leaderboard --period all --order-by pnl` |
| Builder leaderboard | `polymarket -o json data builder-leaderboard` |
| Tags | `polymarket -o json tags related-tags "<topic>"` |
| Comments | `polymarket -o json comments list <CONDITION_ID> --limit 20` |
| Sports list | `polymarket -o json sports list` |
| Sports teams | `polymarket -o json sports teams --league "<LEAGUE>"` |
| Sports market types | `polymarket -o json sports market-types` |
| Generate chart | `python3 scripts/chart.py <TOKEN_ID> --title "..."` |
| Chart from slug | `python3 scripts/chart.py --slug <slug> --outcome "Yes"` |
| Chart from conditionId | `python3 scripts/chart.py --condition-id <CID>` |

### Critical Gotchas

| Gotcha | Detail |
|--------|--------|
| `outcomePrices` is a JSON string | Must `json.loads()` to parse prices from event data |
| Hex token IDs work in v0.1.5 | No decimal conversion needed for `price`, `spread`, `book`, `price-history` |
| `--order` is camelCase | `volumeNum` works; `volume_num` causes 422 error |
| `markets search` has NO `--order` | Sort results manually after fetching |
| `events list --order volume` | Works, descending by default |
| Sum of YES prices ~ 1.01 | Normal — 1% house vig across outcomes |
| Open Interest != face value | In neg-risk markets, OI is current-value-weighted |
| Wrong command -> 404 | `/event/` URL = `events get`; `/market/` URL = `markets get` |
| Holders grouped by token | `data holders` returns holders with `name`/`pseudonym` fields |
| Infrastructure wallets | Check for empty trades, $0 avg_price, billions in value before profiling |
