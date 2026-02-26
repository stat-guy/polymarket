# polymarket

Codex skill for researching Polymarket prediction markets via the `polymarket` CLI.

This is an unofficial read-only research skill for event/market lookup, token ID discovery, holder analysis, wallet trade analysis workflows, and interactive price charts.

## What It Does

- Look up Polymarket events and outcome markets
- Look up individual binary markets
- Convert from `condition_id` context to decimal CLOB `token_id`
- Generate interactive HTML price charts with time-window tabs
- Find top YES/NO holders for a market
- Analyze wallet trades for cost-basis workflows
- Document common Polymarket CLI gotchas

## Prerequisites

- Codex local skills support
- `polymarket` CLI installed and on `PATH`
- Python 3.9+
- Internet access (Polymarket APIs + Plotly CDN used by chart HTML)
- A web browser available locally

## Install (Codex Skill)

Clone this repository and place it in your Codex skills directory so the folder name is exactly `polymarket`:

```bash
git clone https://github.com/stat-guy/polymarket.git ~/.codex/skills/polymarket
```

Expected files:

- `~/.codex/skills/polymarket/SKILL.md`
- `~/.codex/skills/polymarket/scripts/chart.py`

## Quick Start

Use the skill with:

- An event URL (contains `/event/`)
- A market URL (contains `/market/`)
- An event slug
- A market slug

The skill routes to:

- `polymarket events get <slug>` for events
- `polymarket markets get <slug>` for markets

If a slug is ambiguous, try event lookup first and fall back to market lookup on 404.

## Core Workflows

### 1. Event Lookup

```bash
polymarket -o json events get <slug>
```

Use this to retrieve event metadata and the `markets` array (outcomes). Note that `outcomePrices` is a JSON string and must be parsed.

### 2. Market Lookup

```bash
polymarket -o json markets get <slug>
```

Returns a single binary market with price/volume/liquidity fields.

### 3. Get Decimal Token ID (Required for CLOB queries and charting)

```bash
polymarket -o json clob market <CONDITION_ID>
```

Read `tokens[].token_id` from the output. Use the decimal token ID, not hex.

### 4. Generate Interactive Price Chart

From the repo root (or installed skill path):

```bash
python3 scripts/chart.py <DECIMAL_TOKEN_ID> --title "Market Name YES"
```

The script:

- Fetches recent high-resolution price history
- Fetches a full-history series (`--fidelity 5000`)
- Merges them into one timeline
- Writes an HTML file
- Opens it in your browser

Chart UI includes tabs for `1H`, `6H`, `1D`, `1W`, `1M`, `3M`, `6M`, and `All`.

### 5. Top Holders

```bash
polymarket -o json data holders <CONDITION_ID>
```

- `outcome_index: 0` = YES
- `outcome_index: 1` = NO

### 6. Wallet Trade Analysis / Cost Basis Workflow

```bash
polymarket -o json data trades <WALLET_ADDRESS> --limit 500
```

Filter trades by `condition_id`, then compute:

- Total cost: `sum(size * price)` over BUY trades
- Total shares: `sum(size)`
- Average price: `total_cost / total_shares`
- Current value: `shares_held * current_price`
- Win payout: `shares_held * 1.00`

## Important Gotchas

- Use `events get` vs `markets get` based on URL path (`/event/` vs `/market/`)
- `outcomePrices` from event output is a JSON string
- Token IDs for CLOB commands must be decimal, not hex
- `markets search` is more useful than `markets list` for top-volume discovery
- `--order` uses camelCase (`volumeNum`)

## Troubleshooting

- `polymarket: command not found`
  - Install the `polymarket` CLI and ensure it is on `PATH`.
- 404 on lookup
  - You likely used `events get` for a market slug (or vice versa).
- `Error: No price history returned`
  - Confirm the token ID is a decimal CLOB token ID.
- Browser does not open automatically
  - Open the printed local `.html` path manually.

## Security / Safety Notes

- This repository does not trade or place orders.
- Do not paste private keys or secrets into prompts/commands.
- Wallet analysis is for public on-chain activity and may include infrastructure wallets.

## Disclaimer

Educational and research use only. Not financial advice. Unofficial Polymarket tooling.

## License

MIT (see `LICENSE`).
