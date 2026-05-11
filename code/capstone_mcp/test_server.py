# capstone_mcp/test_server.py
"""Tests for the MCP server tools (all 8)."""
from __future__ import annotations

import json
import unittest


class TestGetTask(unittest.TestCase):
    def setUp(self):
        from capstone_mcp.server import get_task
        self.get_task = get_task

    def test_returns_known_task(self):
        result = json.loads(self.get_task("BETA_BINOM_01"))
        self.assertEqual(result["task_id"], "BETA_BINOM_01")
        self.assertIn("numeric_targets", result)
        self.assertIn("tier", result)

    def test_unknown_task_returns_error(self):
        result = json.loads(self.get_task("DOES_NOT_EXIST"))
        self.assertIn("error", result)

    def test_conceptual_task(self):
        result = json.loads(self.get_task("CONCEPTUAL_01"))
        self.assertEqual(result["task_type"], "conceptual")
        self.assertIn("question", result)
        self.assertIn("rubric_keys", result)


class TestListTasks(unittest.TestCase):
    def setUp(self):
        from capstone_mcp.server import list_tasks
        self.list_tasks = list_tasks

    def test_returns_all_by_default(self):
        result = json.loads(self.list_tasks(limit=136))
        self.assertEqual(len(result), 136)

    def test_tier_filter(self):
        result = json.loads(self.list_tasks(tier=1, limit=50))
        self.assertTrue(all(t["tier"] == 1 for t in result))

    def test_difficulty_filter(self):
        result = json.loads(self.list_tasks(difficulty="basic", limit=50))
        self.assertTrue(all(t["difficulty"] == "basic" for t in result))

    def test_task_type_filter_conceptual(self):
        result = json.loads(self.list_tasks(task_type="conceptual", limit=20))
        self.assertEqual(len(result), 10)
        self.assertTrue(all(t.get("task_type") == "conceptual" for t in result))

    def test_limit(self):
        result = json.loads(self.list_tasks(limit=5))
        self.assertEqual(len(result), 5)


class TestScoreResponse(unittest.TestCase):
    def setUp(self):
        from capstone_mcp.server import score_response
        self.score_response = score_response

    def test_perfect_score(self):
        task_id = "BETA_BINOM_01"
        from capstone_mcp.tools.tasks import get_task
        task = get_task(task_id)
        true_vals = [str(round(t["true_value"], 6)) for t in task["numeric_targets"]]
        answer_str = ", ".join(true_vals)
        response = (
            "We use a Beta prior with binomial likelihood assuming iid observations. "
            "The posterior is Beta(alpha, beta).\n"
            f"ANSWER: {answer_str}"
        )
        result = json.loads(self.score_response(task_id, response))
        self.assertIn("final_score", result)
        self.assertIn("pass", result)
        self.assertGreater(result["final_score"], 0.5)

    def test_wrong_answer_low_score(self):
        result = json.loads(self.score_response("BETA_BINOM_01", "I don't know. ANSWER: 99999"))
        self.assertIn("final_score", result)
        self.assertLess(result["final_score"], 0.5)

    def test_score_has_sub_components(self):
        result = json.loads(self.score_response("BETA_BINOM_01", "ANSWER: 0.5"))
        self.assertIn("numeric", result)
        self.assertIn("structure", result)
        self.assertIn("assumptions", result)

    def test_unknown_task_returns_error(self):
        result = json.loads(self.score_response("FAKE_TASK", "ANSWER: 1.0"))
        self.assertIn("error", result)


class TestGetResults(unittest.TestCase):
    def setUp(self):
        from capstone_mcp.server import get_results
        self.get_results = get_results

    def test_returns_results(self):
        result = json.loads(self.get_results())
        self.assertIsInstance(result, list)

    def test_model_filter(self):
        result = json.loads(self.get_results(model_name="chatgpt"))
        self.assertTrue(all(r["model_name"] == "chatgpt" for r in result))

    def test_min_score_filter(self):
        result = json.loads(self.get_results(min_score=0.9))
        self.assertTrue(all(r["final_weighted_score"] >= 0.9 for r in result))

    def test_task_id_filter(self):
        result = json.loads(self.get_results(task_id="BETA_BINOM_01"))
        for r in result:
            self.assertEqual(r["task_id"], "BETA_BINOM_01")


class TestGetSummary(unittest.TestCase):
    def setUp(self):
        from capstone_mcp.server import get_summary
        self.get_summary = get_summary

    def test_group_by_model(self):
        result = json.loads(self.get_summary(group_by="model"))
        self.assertIn("model_aggregates", result)

    def test_group_by_tier(self):
        result = json.loads(self.get_summary(group_by="tier"))
        self.assertIn("by_tier", result)

    def test_group_by_difficulty(self):
        result = json.loads(self.get_summary(group_by="difficulty"))
        self.assertIn("by_difficulty", result)


class TestCompareModels(unittest.TestCase):
    def setUp(self):
        from capstone_mcp.server import compare_models
        self.compare_models = compare_models

    def test_returns_comparison_dict(self):
        result = json.loads(self.compare_models())
        self.assertIn("comparison", result)
        self.assertIn("filters", result)

    def test_task_filter(self):
        result = json.loads(self.compare_models(task_id="BETA_BINOM_01"))
        comparison = result["comparison"]
        for model_data in comparison.values():
            for ts in model_data["task_scores"]:
                self.assertEqual(ts["task_id"], "BETA_BINOM_01")

    def test_tier_filter(self):
        result = json.loads(self.compare_models(tier=1))
        comparison = result["comparison"]
        for model_data in comparison.values():
            for ts in model_data["task_scores"]:
                self.assertEqual(ts["tier"], 1)


class TestGetFailures(unittest.TestCase):
    def setUp(self):
        from capstone_mcp.server import get_failures
        self.get_failures = get_failures

    def test_returns_sorted_failures(self):
        # threshold=1.0 means every task is a "failure"
        result = json.loads(self.get_failures(model_name="chatgpt", threshold=1.0))
        self.assertIsInstance(result, list)
        scores = [r["final_weighted_score"] for r in result]
        self.assertEqual(scores, sorted(scores))

    def test_threshold_zero_returns_empty(self):
        result = json.loads(self.get_failures(model_name="chatgpt", threshold=0.0))
        self.assertEqual(result, [])

    def test_nonexistent_model_empty(self):
        result = json.loads(self.get_failures(model_name="nonexistent_model"))
        self.assertEqual(result, [])

    def test_limit_respected(self):
        result = json.loads(self.get_failures(model_name="chatgpt", threshold=1.0, limit=1))
        self.assertLessEqual(len(result), 1)


class TestRunSingleTask(unittest.TestCase):
    """Tests for run_single_task — uses mock to avoid live API calls."""

    def setUp(self):
        from capstone_mcp.server import run_single_task
        self.run_single_task = run_single_task

    def test_invalid_model_returns_error(self):
        result = json.loads(self.run_single_task("BETA_BINOM_01", "invalid_model_xyz"))
        self.assertIn("error", result)

    def test_unknown_task_returns_error(self):
        result = json.loads(self.run_single_task("NONEXISTENT_TASK", "claude"))
        self.assertIn("error", result)

    def test_result_shape_with_mock(self):
        """Patch the client to return a canned response."""
        from unittest.mock import patch, MagicMock
        mock_client = MagicMock()
        mock_client.query.return_value = {
            "raw_response": "The posterior mean is 0.5714. Beta prior, binomial likelihood, iid. ANSWER: 0.5714",
            "latency_ms": 123.0,
            "input_tokens": 50,
            "output_tokens": 20,
            "error": "",
        }
        with patch("capstone_mcp.tools.scoring.get_client", return_value=mock_client, create=True):
            result = json.loads(self.run_single_task("BETA_BINOM_01", "claude"))
        self.assertIn("final_score", result)
        self.assertIn("raw_response", result)
        self.assertIn("latency_ms", result)
        self.assertAlmostEqual(result["latency_ms"], 123.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
