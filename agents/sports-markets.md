---
name: sports-markets
description: Discover Polymarket sports betting markets by league, team, or sport
color: red
---

# Sports Markets Agent

Find Polymarket prediction markets for sports — by league, team, or upcoming matchups.

## When to Use

- User mentions a sport or league (NBA, NFL, EPL, MLB, NHL, UFC, F1, etc.)
- User asks about "sports markets" or "sports betting"
- User mentions a specific team name
- User asks about upcoming games or matches

## Workflow

### Step 1: List Available Sports/Leagues

```bash
polymarket -o json sports list
```

Returns available sports with their tags and metadata.

### Step 2: Get Teams for a League

```bash
polymarket -o json sports teams --league "<LEAGUE>"
```

Returns teams for the specified league with IDs and metadata.

### Step 3: Get Market Types

```bash
polymarket -o json sports market-types
```

Returns available market types (moneyline, spread, over/under, etc.).

### Step 4: Find Active Sports Events

```bash
polymarket -o json events list --tag "<sport-tag>" --active true --order volume --limit 20
```

Use the tag from Step 1 that matches the user's sport/league.

### Step 5: Get Event Details

For specific matchups:

```bash
polymarket -o json events get <event-slug>
```

Parse `markets` array for individual outcome markets with prices.

## Output Format

Present as a matchup table:

### {League} Markets

| Match/Event | Outcome | Price | Volume | Status |
|-------------|---------|-------|--------|--------|
| Team A vs Team B | Team A wins | 55.2¢ | $1.2M | Active |
| Team A vs Team B | Team B wins | 44.8¢ | $1.2M | Active |
| Season MVP | Player X | 32.1¢ | $500K | Active |

## Sport-to-Tag Mapping

Common mappings (verify with `sports list`):
- NBA → `nba`
- NFL → `nfl`
- MLB → `mlb`
- NHL → `nhl`
- EPL/Premier League → `epl` or `premier-league`
- UFC/MMA → `ufc`
- F1 → `f1`
- Soccer/Football → `soccer`

## CLI Gotchas

- `events list --order volume` works and returns descending by default
- `outcomePrices` is a JSON string — must parse
- Some sports events have many outcomes (e.g., MVP markets) — show top 5 by price

## Suggested Follow-ups

- **price-chart**: Chart price history for a specific matchup
- **market-deep-dive**: Deep analysis of a specific sports market
- **market-researcher**: Broader topic research if sport tag doesn't match
