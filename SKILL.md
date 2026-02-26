---
name: polymarket
description: Research Polymarket prediction markets — look up events, markets, price history, top holders, and generate interactive price charts
argument-hint: <event-or-market-slug-or-url>
user-invocable: true
disable-model-invocation: true
---

# Polymarket Research Skill

Research Polymarket prediction markets: look up events and markets, generate price charts, find top holders, and analyze wallets.

## Prerequisites

- `polymarket` CLI installed and available on `PATH`
- Python 3.9+ (for `scripts/chart.py`)
- Internet access (Polymarket APIs and Plotly CDN)
- A browser available to open generated chart HTML

## Quick Start

Parse the argument to detect event vs market:
- URL contains `/event/` → use `polymarket events get <slug>`
- URL contains `/market/` → use `polymarket markets get <slug>`
- Ambiguous slug → try `polymarket events get <slug>` first; if 404, fall back to `polymarket markets get <slug>`

Extract slug from URL: the last path segment, e.g. `democratic-presidential-nominee-2028` from `https://polymarket.com/event/democratic-presidential-nominee-2028`.

## Workflows

### 1. Look Up an Event

```bash
polymarket -o json events get <slug>
```

Returns event metadata, all outcome markets, condition IDs, and current prices. The `markets` array contains each outcome. `outcomePrices` is a JSON **string** — parse it with `json.loads()`.

### 2. Look Up a Market

```bash
polymarket -o json markets get <slug>
```

Returns a single binary YES/NO market with current price, volume, and liquidity.

### 3. Get Decimal Token ID (required before charting or CLOB queries)

```bash
polymarket -o json clob market <CONDITION_ID>
```

Output contains `tokens` array with `token_id` fields. These are decimal integer strings. Do NOT use hex `0x...` form — CLOB commands require decimal.

To convert from hex if needed:
```bash
python3 -c "print(int('0xYOUR_HEX_HERE', 16))"
```

### 4. Generate Interactive Price Chart

```bash
python3 scripts/chart.py <DECIMAL_TOKEN_ID> --title "Market Name YES"
```

Opens a browser with an interactive Plotly chart with 8 time-window tabs (1H, 6H, 1D, 1W, 1M, 3M, 6M, All). Default view is 1W.

If running from an installed Codex skill path, use:
```bash
python3 ~/.codex/skills/polymarket/scripts/chart.py <DECIMAL_TOKEN_ID> --title "Market Name YES"
```

Example with Gavin Newsom YES (2028 Dem Nom event):
```bash
# Get condition ID from event data, then:
polymarket -o json clob market 0x0f49db97f71c68b1e42a6d16e3de93d85dbf7d4148e3f018eb79e88554be9f75
# Find token_id for YES outcome, then:
python3 scripts/chart.py <TOKEN_ID> --title "Newsom YES"
```

### 5. Top YES/NO Holders

```bash
polymarket -o json data holders <CONDITION_ID>
```

Returns top holders sorted by position size. `outcome_index: 0` = YES holders, `outcome_index: 1` = NO holders.

### 6. Cost Basis for a Wallet

```bash
polymarket -o json data trades <WALLET_ADDRESS> --limit 500
```

Filter by `condition_id` for the market of interest. Then:
- Sum all BUY trades: `total_cost = Σ(size × price)`
- `total_shares = Σ(size)` for BUY trades
- `avg_price = total_cost / total_shares`
- Current value = `shares_held × current_price`
- Win payout = `shares_held × $1.00`
- ROI if wins = `(payout - cost) / cost × 100`

### 7. Wallet Profiling (Infra vs Trader)

Infrastructure/collateral wallets show these signals:
- `data trades` returns empty `[]`
- Only YIELD activity in history
- `avg_price = $0` on all positions (tokens obtained via CTF split, not purchased)
- Identical token amounts across all outcomes of a market
- Very large portfolio value (billions)

Example: `0xa5Ef39C3D3e10d0B270233af41CaC69796B12966` is Polymarket's neg-risk escrow contract (~$11.9B), NOT a bettor.

### 8. Search Markets

```bash
polymarket markets search "<query>" --order volumeNum --limit 20
```

`markets list` always sorts ascending (useless for finding top markets) — use `markets search` instead.

## Critical Gotchas

| Gotcha | Detail |
|--------|--------|
| Wrong command → 404 | URL path is the signal: `/event/` vs `/market/` |
| `outcomePrices` is a JSON string | Must `json.loads()` to parse prices from event data |
| Token IDs must be decimal | NOT hex `0x...`. Use `polymarket clob market <CONDITION_ID>` |
| `--order` is camelCase | `volumeNum` works; `volume_num` causes 422 error |
| Open Interest ≠ face value | In neg-risk markets, OI is current-value-weighted, not YES_tokens × $1 |
| `markets list` is ascending | Use `markets search` to get high-volume markets first |
| Sum of YES prices ≈ 1.01 | Normal — 1% house vig. Not an error. |
| No top-level `get` | Always namespaced: `markets get`, `events get`, etc. |

## Quick Reference

| Goal | Command |
|------|---------|
| Get event | `polymarket -o json events get <slug>` |
| Get market | `polymarket -o json markets get <slug>` |
| Price history (recent) | `polymarket -o json clob price-history --interval max <TOKEN_ID>` |
| Price history (full) | `polymarket -o json clob price-history --interval max --fidelity 5000 <TOKEN_ID>` |
| Top holders | `polymarket -o json data holders <CONDITION_ID>` |
| Wallet trades | `polymarket -o json data trades <WALLET> --limit 500` |
| Portfolio value | `polymarket data value <WALLET>` |
| Open interest | `polymarket data open-interest <CONDITION_ID>` |
| CLOB market info | `polymarket -o json clob market <CONDITION_ID>` |
| Order book | `polymarket clob book <TOKEN_ID>` |
| Search markets | `polymarket markets search "<q>" --order volumeNum` |
| Generate chart | `python3 scripts/chart.py <TOKEN_ID> --title "..."` |
