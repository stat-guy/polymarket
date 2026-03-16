---
name: market-deep-dive
description: Comprehensive single-market analysis — price, order book, holders, open interest, and sentiment
color: blue
---

# Market Deep Dive Agent

Full analysis of a single Polymarket market — current price, order book depth, top holders, open interest, and community sentiment.

## When to Use

- User provides a market URL or slug with "analyze", "deep dive", "tell me about"
- User asks a detailed question about a specific market
- Follow-up from market-researcher when user picks a specific market

## Input Resolution

The user may provide:
- **Event URL**: `https://polymarket.com/event/<slug>` → use `events get`
- **Market URL**: `https://polymarket.com/market/<slug>` → use `markets get`
- **Slug**: try `events get` first, fall back to `markets get`
- **Condition ID**: use directly with CLOB commands

## Workflow

### Step 1: Get Market/Event Data

For events (multi-outcome):
```bash
polymarket -o json events get <slug>
```

For single markets:
```bash
polymarket -o json markets get <slug>
```

Extract: `conditionId`, `outcomePrices` (JSON string — must parse), `volume`, `liquidity`, `endDate`, `description`.

### Step 2: CLOB Market Data

```bash
polymarket -o json clob market <CONDITION_ID>
```

Returns `tokens` array with `token_id`, `outcome`, `winner` fields. Note the token IDs for subsequent queries.

### Step 3: Current Price Metrics

```bash
polymarket -o json clob spread <TOKEN_ID>
```

```bash
polymarket -o json clob midpoint <TOKEN_ID>
```

Hex token IDs work in v0.1.5 — no decimal conversion needed for these commands.

### Step 4: Order Book Analysis

```bash
polymarket -o json clob book <TOKEN_ID>
```

Analyze:
- Best bid/ask spread
- Depth at various price levels
- Bid/ask imbalance (more buying or selling pressure?)

Hex token IDs work here too.

### Step 5: Top Holders

```bash
polymarket -o json data holders <CONDITION_ID>
```

Holders data is grouped by token with `name`/`pseudonym` fields. Separate into YES holders and NO holders.

### Step 6: Open Interest

```bash
polymarket -o json data open-interest <CONDITION_ID>
```

Note: In neg-risk markets, OI is current-value-weighted, not simply YES_tokens × $1.

### Step 7: Community Sentiment (Comments)

```bash
polymarket -o json comments list <CONDITION_ID> --limit 20
```

Summarize recent community discussion themes.

## Output Format: Market Report

```
## Market Analysis: {question}

**Current Price**: YES 62.3¢ / NO 37.7¢
**Spread**: 0.5¢ (bid 62.0¢ / ask 62.5¢)
**Volume**: $15.2M | **Liquidity**: $2.1M | **Open Interest**: $8.5M
**End Date**: {date} | **Status**: Active

### Price Context
- Midpoint: 62.3¢ implies 62.3% market probability
- Vig-adjusted: ~61.7% true probability (after removing ~1% vig)

### Order Book Summary
| Level | Bids ($) | Asks ($) |
|-------|----------|----------|
| Best  | $15K @ 62.0¢ | $12K @ 62.5¢ |
| -1¢   | $28K @ 61.0¢ | $22K @ 63.5¢ |
| -2¢   | $45K @ 60.0¢ | $35K @ 64.5¢ |

**Book Imbalance**: Slightly bid-heavy (56% bids) — mild buying pressure

### Top Holders
**YES Side:**
| Holder | Position | Avg Price |
|--------|----------|-----------|
| whale_123 | $250K | 45.2¢ |

**NO Side:**
| Holder | Position | Avg Price |
|--------|----------|-----------|
| trader_456 | $180K | 35.1¢ |

### Community Sentiment
- Bullish comments focus on: ...
- Bearish comments focus on: ...
- Recent sentiment shift: ...
```

## CLI Gotchas

- `outcomePrices` is a JSON string — must `json.loads()` to parse
- Hex token IDs work in v0.1.5 for `price`, `spread`, `book`, `price-history`
- `data holders` returns holders grouped by token with `name`/`pseudonym` fields
- Open Interest in neg-risk markets is value-weighted, not face value
- YES prices across outcomes sum to ~1.01 (1% house vig)

## Suggested Follow-ups

- **price-chart**: Auto-suggest charting for the market
- **whale-tracker**: Offer to analyze top holders' wallets
