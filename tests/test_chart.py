import importlib.util
from pathlib import Path
import unittest


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


if __name__ == "__main__":
    unittest.main()
