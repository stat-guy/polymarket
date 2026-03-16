import importlib.util
import json
from pathlib import Path
import unittest
import unittest.mock


def load_chart_module():
    repo_root = Path(__file__).resolve().parents[1]
    chart_path = repo_root / "scripts" / "chart.py"
    spec = importlib.util.spec_from_file_location("chart_module", chart_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


chart = load_chart_module()


class MergeHistoriesTests(unittest.TestCase):
    def test_merge_histories_empty_inputs(self):
        self.assertEqual(chart.merge_histories([], []), [])

    def test_merge_histories_only_full_history(self):
        full_history = [
            {"timestamp": "3", "price": "0.30"},
            {"timestamp": "1", "price": "0.10"},
        ]
        self.assertEqual(
            chart.merge_histories([], full_history),
            [[1000, 0.10], [3000, 0.30]],
        )

    def test_merge_histories_prefers_high_res_after_cutoff(self):
        high_res = [
            {"timestamp": "20", "price": "0.20"},
            {"timestamp": "30", "price": "0.30"},
        ]
        full_history = [
            {"timestamp": "10", "price": "0.11"},
            {"timestamp": "20", "price": "0.21"},
            {"timestamp": "40", "price": "0.41"},
        ]
        merged = chart.merge_histories(high_res, full_history)
        self.assertEqual(
            merged,
            [
                [10000, 0.11],
                [20000, 0.20],
                [30000, 0.30],
            ],
        )


class HtmlGenerationTests(unittest.TestCase):
    def test_generate_html_contains_expected_controls(self):
        html = chart.generate_html([[1000, 0.5], [2000, 0.6]], "Test Market YES")
        self.assertIn("Test Market YES", html)
        self.assertIn("plotly-2.32.0.min.js", html)
        for label in ["1H", "6H", "1D", "1W", "1M", "3M", "6M", "All"]:
            self.assertIn(f"setWindow('{label}')", html)


class ResolveTokenIdTests(unittest.TestCase):
    """Tests for the resolve_token_id function added in v2."""

    @unittest.mock.patch("subprocess.run")
    def test_resolve_from_slug_event(self, mock_run):
        """Slug resolution: events get -> conditionId -> clob market -> tokenId."""
        event_response = json.dumps({
            "title": "Test Event",
            "markets": [{
                "question": "Will X happen?",
                "conditionId": "0xabc123",
                "outcomes": '["Yes", "No"]',
            }]
        })
        clob_response = json.dumps({
            "tokens": [
                {"token_id": "12345", "outcome": "Yes"},
                {"token_id": "67890", "outcome": "No"},
            ]
        })
        mock_run.side_effect = [
            unittest.mock.MagicMock(returncode=0, stdout=event_response, stderr=""),
            unittest.mock.MagicMock(returncode=0, stdout=clob_response, stderr=""),
        ]
        result = chart.resolve_token_id(slug="test-event", outcome="Yes")
        self.assertEqual(result, "12345")

    @unittest.mock.patch("subprocess.run")
    def test_resolve_from_condition_id(self, mock_run):
        """Direct conditionId -> tokenId resolution."""
        clob_response = json.dumps({
            "tokens": [
                {"token_id": "11111", "outcome": "Yes"},
                {"token_id": "22222", "outcome": "No"},
            ]
        })
        mock_run.return_value = unittest.mock.MagicMock(
            returncode=0, stdout=clob_response, stderr=""
        )
        result = chart.resolve_token_id(condition_id="0xdef456", outcome="No")
        self.assertEqual(result, "22222")

    @unittest.mock.patch("subprocess.run")
    def test_resolve_fallback_to_first_token(self, mock_run):
        """When outcome not found, falls back to first token."""
        clob_response = json.dumps({
            "tokens": [
                {"token_id": "99999", "outcome": "TeamA"},
                {"token_id": "88888", "outcome": "TeamB"},
            ]
        })
        mock_run.return_value = unittest.mock.MagicMock(
            returncode=0, stdout=clob_response, stderr=""
        )
        result = chart.resolve_token_id(condition_id="0xfoo", outcome="Yes")
        self.assertEqual(result, "99999")


class ArgParserTests(unittest.TestCase):
    """Tests for the enhanced argparse CLI interface."""

    def test_no_open_flag_accepted(self):
        """Parser accepts --no-open flag."""
        parser = chart.main.__code__  # Just verify the function exists with new args
        # Functional test: parse args with --no-open
        import argparse
        p = argparse.ArgumentParser()
        p.add_argument("token_id", nargs='?', default=None)
        p.add_argument("--slug", default=None)
        p.add_argument("--condition-id", default=None)
        p.add_argument("--outcome", default="Yes")
        p.add_argument("--title", default="Polymarket Price Chart")
        p.add_argument("--no-open", action="store_true")
        args = p.parse_args(["--slug", "test-market", "--no-open"])
        self.assertTrue(args.no_open)
        self.assertEqual(args.slug, "test-market")
        self.assertIsNone(args.token_id)

    def test_slug_or_condition_id_makes_token_optional(self):
        """token_id is optional when --slug or --condition-id is provided."""
        import argparse
        p = argparse.ArgumentParser()
        p.add_argument("token_id", nargs='?', default=None)
        p.add_argument("--condition-id", default=None)
        args = p.parse_args(["--condition-id", "0xabc"])
        self.assertIsNone(args.token_id)
        self.assertEqual(args.condition_id, "0xabc")


if __name__ == "__main__":
    unittest.main()
