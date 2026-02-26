# Troubleshooting

## `polymarket: command not found`

- Install the `polymarket` CLI.
- Ensure the binary is on `PATH`.
- Run `which polymarket` and `polymarket --help`.

## 404 on event/market lookup

Use the command namespace that matches the URL path:

- `/event/` => `polymarket events get <slug>`
- `/market/` => `polymarket markets get <slug>`

## `422` error when searching markets

Use camelCase for ordering:

```bash
polymarket markets search "<query>" --order volumeNum --limit 20
```

## No price history returned

- Confirm you are using a decimal CLOB token ID, not hex.
- Resolve it via:

```bash
polymarket -o json clob market <CONDITION_ID>
```

## Browser does not open automatically

Open the HTML file path printed by `scripts/chart.py` manually in your browser.
