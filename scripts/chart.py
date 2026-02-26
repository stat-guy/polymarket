#!/usr/bin/env python3
"""
Polymarket price chart generator.
Usage: python3 chart.py <DECIMAL_TOKEN_ID> [--title "Market Name"]
"""

import argparse
import json
import subprocess
import sys
import tempfile
import webbrowser
from pathlib import Path


def fetch_price_history(token_id: str, fidelity: int = None) -> list:
    """
    Run: polymarket -o json clob price-history --interval max [--fidelity N] <token_id>
    Returns list of {"timestamp": unix_ts, "price": "0.264"} dicts.
    Exits with error message on failure.
    """
    cmd = ["polymarket", "-o", "json", "clob", "price-history", "--interval", "max"]
    if fidelity is not None:
        cmd += ["--fidelity", str(fidelity)]
    cmd.append(str(token_id))

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        print("Error: 'polymarket' CLI not found. Install it first.", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0:
        print(f"Error fetching price history (exit {result.returncode}):", file=sys.stderr)
        print(result.stderr or result.stdout, file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Error: CLI returned non-JSON output:", file=sys.stderr)
        print(result.stdout[:500], file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        print(f"Error: Expected list from price-history, got {type(data).__name__}", file=sys.stderr)
        print(f"Token ID {token_id} may be invalid.", file=sys.stderr)
        sys.exit(1)

    if len(data) == 0:
        print(f"Error: No price history returned for token ID {token_id}.", file=sys.stderr)
        print("Verify the token ID is correct (decimal integer, not hex).", file=sys.stderr)
        sys.exit(1)

    return data


def merge_histories(high_res: list, full_history: list) -> list:
    """
    Merge high-resolution recent data with low-resolution full history.

    Strategy:
    1. Find the earliest timestamp in high_res
    2. Take full_history points BEFORE that cutoff (low-res backdrop)
    3. Append all high_res points
    4. Sort by timestamp

    Returns list of [timestamp_ms, float_price] pairs.
    Handles empty inputs gracefully.
    """
    # Convert helper — CLI returns {"timestamp": ..., "price": ...}
    def to_pair(pt):
        return [int(pt["timestamp"]) * 1000, float(pt["price"])]

    if not high_res and not full_history:
        return []

    if not high_res:
        return sorted([to_pair(pt) for pt in full_history], key=lambda x: x[0])

    if not full_history:
        return sorted([to_pair(pt) for pt in high_res], key=lambda x: x[0])

    # Find earliest high_res timestamp
    min_high_res_t = min(int(pt["timestamp"]) for pt in high_res)

    # Take full_history points before the high_res window
    backdrop = [to_pair(pt) for pt in full_history if int(pt["timestamp"]) < min_high_res_t]

    # All high_res points
    recent = [to_pair(pt) for pt in high_res]

    merged = backdrop + recent
    merged.sort(key=lambda x: x[0])
    return merged


def generate_html(points: list, title: str) -> str:
    """
    Generate a self-contained dark-theme HTML page with an interactive Plotly chart.

    Features:
    - 8 time-window tab buttons: 1H, 6H, 1D, 1W, 1M, 3M, 6M, All
    - Default active tab: 1W
    - Y-axis: 0-1.0 formatted as percentage (e.g., 26.4%)
    - Area fill under the price line
    - Dark GitHub-style theme (#0d1117 background)
    - Plotly.js v2.32.0 from CDN
    """
    points_json = json.dumps(points)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0d1117; color: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; }}
  h1 {{ font-size: 1.25rem; font-weight: 600; margin-bottom: 16px; color: #e6edf3; }}
  .tabs {{ display: flex; gap: 4px; margin-bottom: 12px; flex-wrap: wrap; }}
  .tab-btn {{
    padding: 6px 14px;
    border: 1px solid #30363d;
    border-radius: 6px;
    background: #161b22;
    color: #8b949e;
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.15s;
  }}
  .tab-btn:hover {{ background: #21262d; color: #c9d1d9; border-color: #58a6ff; }}
  .tab-btn.active {{ background: #1f6feb; border-color: #1f6feb; color: #fff; font-weight: 600; }}
  #chart {{ width: 100%; height: 480px; }}
</style>
</head>
<body>
<h1>{title}</h1>
<div class="tabs">
  <button class="tab-btn" onclick="setWindow('1H')">1H</button>
  <button class="tab-btn" onclick="setWindow('6H')">6H</button>
  <button class="tab-btn" onclick="setWindow('1D')">1D</button>
  <button class="tab-btn active" onclick="setWindow('1W')">1W</button>
  <button class="tab-btn" onclick="setWindow('1M')">1M</button>
  <button class="tab-btn" onclick="setWindow('3M')">3M</button>
  <button class="tab-btn" onclick="setWindow('6M')">6M</button>
  <button class="tab-btn" onclick="setWindow('All')">All</button>
</div>
<div id="chart"></div>

<script>
const ALL_POINTS = {points_json};

const WINDOWS = {{
  "1H":  3600 * 1000,
  "6H":  6 * 3600 * 1000,
  "1D":  24 * 3600 * 1000,
  "1W":  7 * 24 * 3600 * 1000,
  "1M":  30 * 24 * 3600 * 1000,
  "3M":  90 * 24 * 3600 * 1000,
  "6M":  180 * 24 * 3600 * 1000,
  "All": null
}};

const layout = {{
  paper_bgcolor: '#0d1117',
  plot_bgcolor: '#0d1117',
  font: {{ color: '#c9d1d9', size: 12 }},
  xaxis: {{
    gridcolor: '#21262d',
    linecolor: '#30363d',
    tickcolor: '#30363d',
    type: 'date',
    showgrid: true,
  }},
  yaxis: {{
    gridcolor: '#21262d',
    linecolor: '#30363d',
    tickcolor: '#30363d',
    range: [0, 1],
    tickformat: '.1%',
    showgrid: true,
  }},
  margin: {{ l: 60, r: 20, t: 20, b: 50 }},
  hovermode: 'x unified',
}};

const config = {{ responsive: true, displayModeBar: false }};

function setWindow(label) {{
  // Update active button
  document.querySelectorAll('.tab-btn').forEach(btn => {{
    btn.classList.toggle('active', btn.textContent === label);
  }});

  const now = Date.now();
  const cutoff = WINDOWS[label] !== null ? now - WINDOWS[label] : 0;
  const filtered = ALL_POINTS.filter(pt => pt[0] >= cutoff);

  if (filtered.length === 0) {{
    // Fall back to all data if window is too narrow
    setWindow('All');
    return;
  }}

  const xs = filtered.map(pt => new Date(pt[0]).toISOString());
  const ys = filtered.map(pt => pt[1]);

  const trace = {{
    x: xs,
    y: ys,
    type: 'scatter',
    mode: 'lines',
    fill: 'tozeroy',
    fillcolor: 'rgba(88, 166, 255, 0.1)',
    line: {{ color: '#58a6ff', width: 2 }},
    hovertemplate: '%{{x|%b %d, %Y %H:%M}}<br>Price: %{{y:.4f}}<extra></extra>',
  }};

  Plotly.react('chart', [trace], layout, config);
}}

// Initialize with 1W view
setWindow('1W');
</script>
</body>
</html>"""
    return html


def main():
    parser = argparse.ArgumentParser(
        description="Generate an interactive Polymarket price chart",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 chart.py 21742633143463906290569050155826241533067272736897614950488156847949938836455
  python3 chart.py 12345678 --title "Candidate YES"
        """
    )
    parser.add_argument("token_id", help="Decimal token ID (NOT hex). Get via: polymarket -o json clob market <CONDITION_ID>")
    parser.add_argument("--title", default="Polymarket Price Chart", help="Chart title (default: 'Polymarket Price Chart')")
    args = parser.parse_args()

    print(f"Fetching price history for token {args.token_id}...")

    print("  Fetching high-resolution data...")
    high_res = fetch_price_history(args.token_id)
    print(f"  Got {len(high_res)} high-res points")

    print("  Fetching full history (fidelity=5000)...")
    full_history = fetch_price_history(args.token_id, fidelity=5000)
    print(f"  Got {len(full_history)} full-history points")

    print("Merging histories...")
    points = merge_histories(high_res, full_history)
    print(f"  Merged: {len(points)} total points")

    print("Generating chart...")
    html = generate_html(points, args.title)

    # Write to temp file
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.html',
        prefix='polymarket_chart_',
        delete=False
    ) as f:
        f.write(html)
        temp_path = f.name

    print(f"Chart saved to: {temp_path}")
    print("Opening in browser...")
    chart_uri = Path(temp_path).resolve().as_uri()
    opened = webbrowser.open_new_tab(chart_uri)
    if not opened:
        print(f"Open this file manually in a browser: {temp_path}")


if __name__ == "__main__":
    main()
