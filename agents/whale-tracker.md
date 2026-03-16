---
name: whale-tracker
description: Analyze a Polymarket wallet — profile traders, calculate PnL, detect infrastructure wallets
color: green
---

# Whale Tracker Agent

Analyze any Polymarket wallet address to build a trader profile with PnL, positions, and classification.

## When to Use

- User provides a wallet address (0x... 42 characters)
- User asks "who is this trader", "analyze wallet"
- User wants to know about a specific address from holder data

## Workflow

### Step 1: Get Wallet Profile

```bash
polymarket -o json profiles get <WALLET_ADDRESS>
```

Returns username, pseudonym, bio, profile image, and social links.

### Step 2: Portfolio Value

```bash
polymarket -o json data value <WALLET_ADDRESS>
```

Returns total portfolio value in USD.

### Step 3: Trading Volume

```bash
polymarket -o json data traded <WALLET_ADDRESS>
```

Returns total volume traded.

### Step 4: Current Positions

```bash
polymarket -o json data positions <WALLET_ADDRESS>
```

Returns open positions with market details, size, and current value.

### Step 5: Closed Positions

```bash
polymarket -o json data closed-positions <WALLET_ADDRESS>
```

Returns settled positions with realized PnL.

### Step 6: Recent Activity

```bash
polymarket -o json data activity <WALLET_ADDRESS> --limit 50
```

Returns recent trades, deposits, withdrawals.

### Step 7: Detailed Trades (optional, for deep analysis)

```bash
polymarket -o json data trades <WALLET_ADDRESS> --limit 500
```

Returns individual trades with price, size, side, timestamp.

## Infrastructure Wallet Detection

**CRITICAL**: Before presenting results, check for infrastructure wallet signals:

A wallet is likely infrastructure/collateral (NOT a real trader) if:
- `data trades` returns empty `[]`
- Only YIELD activity in history
- `avg_price = $0` on all positions (tokens obtained via CTF split, not purchased)
- Identical token amounts across YES and NO outcomes of same market
- Portfolio value in billions (e.g., >$1B)

**Known infrastructure wallets:**
- `0xa5Ef39C3D3e10d0B270233af41CaC69796B12966` — Polymarket neg-risk escrow contract (~$11.9B)

If infrastructure detected, clearly label: "⚠️ This appears to be an infrastructure/collateral wallet, not a trader."

## Trader Classification

Based on collected data, classify the wallet:

| Classification | Criteria |
|---------------|----------|
| 🐋 Whale | Portfolio value > $1M OR single position > $500K |
| 📈 Active Trader | >50 trades in last 30 days, diverse markets |
| 🎯 Focused | <5 markets but large positions |
| 👤 Casual | <20 trades total, small positions |
| 🏗️ Infrastructure | Matches infrastructure signals above |

## Output Format: Trader Profile Card

```
## Trader Profile: {pseudonym or address}

**Classification**: 🐋 Whale
**Portfolio Value**: $X.XXM
**Total Traded**: $X.XXM
**Open Positions**: N markets

### Top Positions
| Market | Side | Size | Avg Price | Current | PnL |
|--------|------|------|-----------|---------|-----|
| ...    | YES  | $50K | 42.3¢     | 55.1¢   | +$6.4K |

### Recent Activity
- Bought $10K YES on "Market X" at 45¢
- Sold $5K NO on "Market Y" at 62¢

### Win Rate
- Closed positions: X wins / Y total = Z%
```

## CLI Gotchas

- Wallet addresses are 42 characters (0x + 40 hex chars)
- `data holders` returns holders grouped by token with `name`/`pseudonym` fields
- Trades include `side` (BUY/SELL), `price`, `size`, `timestamp`

## Suggested Follow-ups

- **market-deep-dive**: Deep dive into the trader's largest position
- **price-chart**: Chart the market where they have the biggest bet
