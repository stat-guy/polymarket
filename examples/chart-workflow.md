# Chart Workflow Example

## Goal

Generate an interactive price chart for a YES/NO outcome using a decimal CLOB token ID.

## Steps

1. Get the market `condition_id` from event or market data.
2. Resolve decimal token IDs:

```bash
polymarket -o json clob market <CONDITION_ID>
```

3. Pick the YES or NO `tokens[].token_id`.
4. Generate the chart:

```bash
python3 scripts/chart.py <DECIMAL_TOKEN_ID> --title "Market Name YES"
```

## Notes

- Token ID must be decimal, not hex.
- The script writes a local HTML file and opens it in your browser.
- If auto-open fails, open the printed file path manually.
