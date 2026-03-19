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

## Pre-loaded Context

The following dynamic data is injected at skill load time via `!`command`` shell injection — no tool call needed. Use it directly; do NOT re-fetch the same data with a Bash tool call.

### Environment
- CLI status: !`which polymarket 2>/dev/null && polymarket --version 2>/dev/null || echo "ERROR: polymarket CLI not found on PATH"`
- Current UTC time: !`date -u +"%Y-%m-%dT%H:%M:%SZ"`

If the CLI status shows an error, stop and tell the user to install the `polymarket` CLI before proceeding.

### Sports Tags (for routing)
**Live sports tags:** !`polymarket -o json sports list 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(', '.join(x['sport'] for x in d))"`

Use these tags for sports intent classification and routing to sports-markets agent.

### Trending Events — Top 10 by Volume (for leaderboard/discovery queries)
!`polymarket -o json events list --order volume --active true --limit 10 2>/dev/null | python3 -c "import sys,json; [print(f'{i+1}. {e[\"title\"]} | vol:\${float(e.get(\"volume\",0))/1e6:.1f}M | slug:{e[\"slug\"]}') for i,e in enumerate(json.load(sys.stdin))]"`

### Trending Markets — Top 10 by Volume (individual binary markets)
!`polymarket -o json markets list --order volumeNum --active true --limit 10 2>/dev/null | python3 -c "import sys,json; [print(f'{i+1}. {m[\"question\"]} | vol:\${float(m.get(\"volumeNum\",0))/1e6:.1f}M | slug:{m[\"slug\"]}') for i,m in enumerate(json.load(sys.stdin))]"`

### Top Traders Leaderboard — This Week by PnL
!`polymarket -o json data leaderboard --period week --order-by pnl --limit 10 2>/dev/null | python3 -c "import sys,json; [print(f'{t[\"rank\"]}. {t.get(\"user_name\") or \"anon\"} | PnL:+\${float(t[\"pnl\"]):,.0f} | vol:\${float(t[\"volume\"])/1e6:.1f}M | {t[\"proxy_wallet\"]}') for t in json.load(sys.stdin)]"`

**For leaderboard/trending/popular queries**: use all three sections above directly — skip Steps 1-3 in `leaderboard-discovery.md`. Only run fresh commands if the user asks for a different period (day/month/all) or wants more than 10 results.

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
5. **Sport keywords**: If input mentions any sport, league, or team name, match against the pre-loaded live sports tags above — route to sports-markets
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

## Shell Injection Technique

Claude Code supports `!`command`` syntax in SKILL.md files. When the skill is invoked, Claude Code runs the command and swaps the placeholder with its output — the model only sees the result, not the raw command. This eliminates extra tool-call roundtrips for predictable data fetching.

**When to use:**
- Data that is always fetched at the start of an agent workflow (e.g., sports list for sports routing)
- Lightweight, broadly useful context that improves intent classification
- Any dynamic content the skill depends on that would otherwise require a Bash tool call

**When NOT to use:**
- Heavy data only needed for specific query types (e.g., full leaderboard — only inject if this skill exclusively serves trending queries)
- Data that depends on user-provided arguments (e.g., specific market slugs or wallet addresses)
- Commands that take >1–2s to run (adds latency to every skill invocation)

**Example (from this skill):**

The "Pre-loaded Context" section above uses `!` followed by a backtick-quoted shell command that pipes `polymarket sports list` through python to extract sport tags.

This eliminates the `polymarket sports list` tool call that would otherwise be Step 1 of the sports-markets agent workflow.

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
