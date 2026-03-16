# Polymarket

Claude Code skill for researching Polymarket prediction markets via the `polymarket` CLI.

This is an unofficial read-only research skill with an orchestrator + 6 specialized agent architecture for event/market lookup, wallet analysis, price charting, leaderboard discovery, and sports market browsing.

## Architecture

```
SKILL.md (orchestrator)
├── agents/market-researcher.md    — Topic → market comparison tables
├── agents/market-deep-dive.md     — Single market → full analysis report
├── agents/whale-tracker.md        — Wallet → trader profile + PnL
├── agents/price-chart.md          — Any input → interactive Plotly chart
├── agents/leaderboard-discovery.md — Trending markets + top traders
├── agents/sports-markets.md       — League/team → sports market discovery
├── scripts/chart.py               — Chart generator (--slug, --condition-id, --no-open)
└── polymarket.py (skill)          — CLI wrapper with --json, --chart flags
```

The orchestrator SKILL.md classifies user intent and dispatches to the matched agent's workflow. Each agent is a prompt module with step-by-step CLI instructions.

## What It Does

- Discover markets by topic, tag, or category (market-researcher)
- Full single-market analysis with order book, holders, OI, sentiment (market-deep-dive)
- Wallet profiling with PnL, positions, win rate, infrastructure detection (whale-tracker)
- Interactive HTML price charts with 8 time-window tabs (price-chart)
- Trending markets and top trader leaderboards (leaderboard-discovery)
- Sports market discovery by league, team, or matchup (sports-markets)
- Multi-agent chaining: one workflow suggests the next

## Prerequisites

- `polymarket` CLI v0.1.5+ installed and on `PATH`
- Python 3.9+
- Internet access (Polymarket APIs + Plotly CDN)
- A web browser available locally

## Install `polymarket` CLI (macOS/Linux via Homebrew)

```bash
brew tap Polymarket/polymarket-cli https://github.com/Polymarket/polymarket-cli
brew install polymarket
```

Verify: `polymarket --help`

## Install (Claude Code Skill)

```bash
# Clone to Claude Code skills directory
git clone https://github.com/stat-guy/polymarket.git ~/.claude/skills/polymarket
```

Expected files:
- `~/.claude/skills/polymarket/SKILL.md`
- `~/.claude/skills/polymarket/agents/*.md` (6 agent files)
- `~/.claude/skills/polymarket/chart.py`
- `~/.claude/skills/polymarket/polymarket.py`

## Quick Start

Use `/polymarket` with any of these input types:

| Input | Routes To |
|-------|-----------|
| Event URL (`/event/` in URL) | Quick event lookup |
| Market URL (`/market/` in URL) | Quick market lookup |
| Topic ("what markets about AI?") | market-researcher agent |
| Wallet address (0x...) | whale-tracker agent |
| "chart" / "price history" | price-chart agent |
| "trending" / "leaderboard" | leaderboard-discovery agent |
| Sport/league name (NBA, NFL...) | sports-markets agent |
| Market + "analyze" / "deep dive" | market-deep-dive agent |

## Chart Generation

```bash
# From token ID
python3 scripts/chart.py <TOKEN_ID> --title "Market YES"

# From slug (auto-resolves)
python3 scripts/chart.py --slug democratic-presidential-nominee-2028 --outcome "Gavin Newsom"

# From condition ID
python3 scripts/chart.py --condition-id 0xabc123 --outcome No

# Skip browser open
python3 scripts/chart.py --slug my-market --no-open
```

## Examples and Docs

- `examples/event-lookup.md`
- `examples/chart-workflow.md`
- `examples/wallet-analysis.md`
- `docs/installation.md`
- `docs/troubleshooting.md`

## Development

- Unit tests: `python3 -m unittest discover -s tests -p 'test_*.py' -v`
- CI: GitHub Actions workflow in `.github/workflows/ci.yml`

## Important Gotchas (v0.1.5)

- Hex token IDs now work everywhere (price, spread, book, price-history)
- `events list --order volume` works, descending by default
- `markets list --order volumeNum` works (camelCase required; `volume_num` → 422)
- `markets search` has NO `--order` flag — sort results manually
- `outcomePrices` from event output is a JSON string — must `json.loads()`
- YES prices across outcomes sum to ~1.01 (1% house vig)
- Holders data grouped by token with `name`/`pseudonym` fields

## Troubleshooting

- `polymarket: command not found` — Install CLI and ensure it's on PATH
- 404 on lookup — Wrong command: use `events get` for `/event/` URLs, `markets get` for `/market/`
- No price history — Confirm the token ID is valid
- Browser won't open — Open the printed `.html` path manually, or use `--no-open`

## Security / Safety Notes

- This repository does not trade or place orders
- Do not paste private keys or secrets into prompts/commands
- Wallet analysis is for public on-chain activity and may include infrastructure wallets

## Disclaimer

Educational and research use only. Not financial advice. Unofficial Polymarket tooling.

## License

MIT (see `LICENSE`).
