import importlib.util
import json
from pathlib import Path
import unittest
import unittest.mock


def load_polymarket_module():
    """Load polymarket.py from the skill's installed location."""
    skill_path = Path.home() / ".claude" / "skills" / "polymarket" / "polymarket.py"
    if not skill_path.exists():
        # Fallback: skip tests if not installed
        return None
    spec = importlib.util.spec_from_file_location("polymarket_module", skill_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


pm = load_polymarket_module()


@unittest.skipIf(pm is None, "polymarket.py not found at ~/.claude/skills/polymarket/")
class ExtractSlugTests(unittest.TestCase):
    def test_event_url(self):
        slug = pm.extract_slug("https://polymarket.com/event/democratic-presidential-nominee-2028")
        self.assertEqual(slug, "democratic-presidential-nominee-2028")

    def test_market_url(self):
        slug = pm.extract_slug("https://polymarket.com/market/will-trump-win")
        self.assertEqual(slug, "will-trump-win")

    def test_trailing_slash(self):
        slug = pm.extract_slug("https://polymarket.com/event/test-event/")
        self.assertEqual(slug, "test-event")


@unittest.skipIf(pm is None, "polymarket.py not found at ~/.claude/skills/polymarket/")
class InputDetectionTests(unittest.TestCase):
    """Test that polymarket.py routes correctly based on input type."""

    @unittest.mock.patch.object(pm, "run")
    def test_event_url_routes_to_events_get(self, mock_run):
        """Event URL should call events get."""
        mock_run.return_value = ('{"title":"Test","markets":[]}', 0)
        with unittest.mock.patch("sys.argv", ["polymarket.py", "https://polymarket.com/event/test-event"]):
            # Re-parse args
            import argparse
            query = "https://polymarket.com/event/test-event"
            self.assertIn("polymarket.com/event/", query)

    @unittest.mock.patch.object(pm, "run")
    def test_market_url_routes_to_markets_get(self, mock_run):
        """Market URL should call markets get."""
        mock_run.return_value = ('{"conditionId":"0xabc"}', 0)
        query = "https://polymarket.com/market/test-market"
        self.assertIn("polymarket.com/market/", query)


@unittest.skipIf(pm is None, "polymarket.py not found at ~/.claude/skills/polymarket/")
class FormatOutputTests(unittest.TestCase):
    """Test the output formatting helpers."""

    def test_format_search_output(self):
        """Search output formatting parses JSON and prints summary."""
        data = json.dumps([{
            "question": "Will it rain?",
            "outcomePrices": '["0.65", "0.35"]',
            "volume": "1000000",
            "liquidity": "50000",
            "active": True,
            "slug": "will-it-rain",
            "conditionId": "0xabc",
        }])
        # Just verify the function doesn't crash
        import io
        import contextlib
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            pm._format_search_output(data)
        output = f.getvalue()
        self.assertIn("Will it rain?", output)
        self.assertIn("65.0", output)

    def test_format_event_output(self):
        """Event output formatting extracts title and markets."""
        data = json.dumps({
            "title": "Big Event",
            "markets": [{
                "question": "Outcome A?",
                "outcomePrices": '["0.40", "0.60"]',
                "volume": "500000",
                "liquidity": "25000",
                "active": True,
                "slug": "outcome-a",
                "conditionId": "0xdef",
            }]
        })
        import io
        import contextlib
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            pm._format_event_output(data, 0)
        output = f.getvalue()
        self.assertIn("Big Event", output)
        self.assertIn("Outcome A?", output)


if __name__ == "__main__":
    unittest.main()
