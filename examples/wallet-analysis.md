# Wallet Analysis Example

## Goal

Use wallet trade history to estimate cost basis and current position value.

## Fetch Trades

```bash
polymarket -o json data trades <WALLET_ADDRESS> --limit 500
```

## Workflow

1. Filter trades to the target `condition_id`.
2. Separate BUY and SELL activity as needed.
3. Compute:
- `total_cost = sum(size * price)` across BUYs
- `total_shares = sum(size)` across BUYs
- `avg_price = total_cost / total_shares`
- `current_value = shares_held * current_price`
- `win_payout = shares_held * 1.00`

## Caveat

Large wallets can be infrastructure/escrow wallets rather than traders. Check for empty `trades`, yield-only activity, and identical positions across outcomes.
