import unittest

from sql_query_optimization import (
    analyze_sql_query,
    detect_cte,
    detect_early_filtering,
    detect_filter_after_join,
    detect_select_star,
    suggest_cte_wrapper,
)


class TestSqlQueryOptimization(unittest.TestCase):
    def test_detect_select_star(self):
        query = "SELECT * FROM transactions t JOIN customers c ON t.customer_id = c.id WHERE t.year = 2024"
        self.assertTrue(detect_select_star(query))

    def test_detect_explicit_columns(self):
        query = "SELECT t.transaction_id, c.customer_name FROM transactions t JOIN customers c ON t.customer_id = c.id"
        self.assertFalse(detect_select_star(query))

    def test_detect_cte(self):
        query = "WITH recent_transactions AS (SELECT transaction_id FROM transactions WHERE year = 2024) SELECT * FROM recent_transactions"
        self.assertTrue(detect_cte(query))

    def test_detect_early_filtering_with_subquery(self):
        query = "SELECT t.transaction_id FROM (SELECT transaction_id FROM transactions WHERE year = 2024) t JOIN customers c ON t.customer_id = c.id"
        self.assertTrue(detect_early_filtering(query))

    def test_detect_filter_after_join(self):
        query = "SELECT t.transaction_id FROM transactions t JOIN customers c ON t.customer_id = c.id WHERE t.year = 2024"
        self.assertTrue(detect_filter_after_join(query))

    def test_analyze_sql_query_recommendations(self):
        query = "SELECT * FROM transactions t JOIN customers c ON t.customer_id = c.id WHERE t.year = 2024"
        report = analyze_sql_query(query)
        self.assertTrue(report["uses_select_star"])
        self.assertTrue(report["has_filter_after_join"])
        self.assertIn("Replace SELECT *", report["recommendations"][0])

    def test_suggest_cte_wrapper(self):
        query = "SELECT t.transaction_id FROM transactions t WHERE t.year = 2024"
        wrapped = suggest_cte_wrapper(query, cte_name="filtered_transactions")
        self.assertIn("WITH filtered_transactions AS", wrapped)


if __name__ == "__main__":
    unittest.main()
