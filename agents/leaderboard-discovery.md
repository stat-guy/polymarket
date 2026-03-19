---
name: leaderboard-discovery
description: Find trending markets, top traders, and leaderboard rankings on Polymarket
color: yellow
---

# Leaderboard & Discovery Agent

Find what's trending on Polymarket — top traders, highest volume markets, and leaderboard rankings.

## When to Use

- User asks about "trending", "popular", "hot" markets
- User wants leaderboard or top trader info
- User asks "what's popular on Polymarket"

## Workflow

### Steps 1–3: Pre-loaded — No Tool Calls Needed

The SKILL.md orchestrator pre-injects all three data sources at invocation time:

- **Top Traders (week, by PnL)**: Already in context — includes `proxy_wallet` for whale-tracker follow-ups
- **Trending Events (top 10 by volume)**: Already in context — includes slugs for deep-dive follow-ups
- **Trending Markets (top 10 by volume)**: Already in context — individual binary markets

**Use the pre-loaded data directly to build the discovery report. Skip to Step 4.**

Only run fresh commands if the user requests:
- A different leaderboard period (day/month/all): `polymarket -o json data leaderboard --period <period> --order-by pnl --limit 20`
- More than 10 results: add `--limit 50` to the relevant command
- A different sort order: `--order-by volume` or `--order-by markets_traded`
- Builder/LP leaderboard: `polymarket -o json data builder-leaderboard --limit 20`

Available `--period` values: `day`, `week`, `month`, `all`
Available `--order-by` values: `pnl`, `volume`, `markets_traded`

Note: `--order volumeNum` requires camelCase. `volume_num` causes 422 error.

### Step 4: Build Discovery Report

Present two sections:

**Trending Markets:**

| # | Market | YES Price | Volume | Category |
|---|--------|-----------|--------|----------|
| 1 | Will X happen? | 62.3¢ | $15.2M | Politics |

**Top Traders:**

| # | Trader | PnL | Volume | Markets |
|---|--------|-----|--------|---------|
| 1 | pseudonym | +$125K | $2.1M | 47 |

## Output Format

- Present traders with their `user_name` field (falls back to "anon"); include `proxy_wallet` truncated for reference
- Format PnL with +/- prefix and dollar amounts
- Include volume as dollar amounts
- Rank by the metric the user cares about (default: PnL for traders, volume for markets)

## CLI Gotchas

- `markets list --order volumeNum` — camelCase required
- `events list --order volume` — works, descending default
- Leaderboard returns `name`/`pseudonym` fields for traders

## Suggested Follow-ups

- **whale-tracker**: Analyze a specific top trader's wallet
- **market-deep-dive**: Deep dive into a trending market
- **price-chart**: Chart price history for any trending market
