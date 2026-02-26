# Event Lookup Example

## Goal

Retrieve event metadata and outcome markets from an event slug or URL.

## Example

```bash
polymarket -o json events get democratic-presidential-nominee-2028
```

## What to Look For

- Top-level event metadata (title, status, dates)
- `markets` array for all outcomes
- `conditionId` values for each outcome market
- `outcomePrices` (JSON string; parse before using)

## Common Mistake

Using `markets get` with an event slug returns a 404. Event pages require `events get`.
