"""
Unit and Integration Test Suite for Member 1 (NLP Engine).
Evaluates intent classification accuracy, entity extraction, and IR structure compliance.
"""

import unittest
import json
from nlp_engine import NLPEngine


class TestNLPEngine(unittest.TestCase):

    def setUp(self):
        self.engine = NLPEngine()

    def test_example_from_project_specification(self):
        """
        Tests the primary project requirement:
        User input: 'Show all students having CGPA greater than 8.5'
        Expected: intent: FILTER, table: students, column: cgpa, operator: >, value: 8.5
        """
        query = "Show all students having CGPA greater than 8.5"
        ir = self.engine.process_query(query)

        self.assertEqual(ir["intent"], "FILTER")
        self.assertEqual(ir["table"], "students")
        self.assertIn("cgpa", ir["columns"])
        self.assertEqual(len(ir["conditions"]), 1)
        self.assertEqual(ir["conditions"][0]["column"], "cgpa")
        self.assertEqual(ir["conditions"][0]["operator"], ">")
        self.assertEqual(ir["conditions"][0]["value"], 8.5)

    def test_count_intent(self):
        """Tests COUNT intent queries."""
        query = "How many students are enrolled in the college?"
        ir = self.engine.process_query(query)

        self.assertEqual(ir["intent"], "COUNT")
        self.assertEqual(ir["table"], "students")

    def test_top_n_sort_intent(self):
        """Tests SORT intent and top N limits."""
        query = "Show top 5 courses by credits"
        ir = self.engine.process_query(query)

        self.assertEqual(ir["intent"], "SORT")
        self.assertEqual(ir["table"], "courses")
        self.assertEqual(ir["limit"], 5)
        self.assertIsNotNone(ir["order_by"])
        self.assertEqual(ir["order_by"]["direction"], "DESC")

    def test_aggregation_average(self):
        """Tests mathematical AGGREGATION queries."""
        query = "Calculate average CGPA of students"
        ir = self.engine.process_query(query)

        self.assertEqual(ir["intent"], "AGGREGATION")
        self.assertEqual(ir["table"], "students")
        self.assertIn("aggregation", ir)
        self.assertEqual(ir["aggregation"]["function"], "AVG")

    def test_synonym_resolution(self):
        """Tests domain synonyms (e.g. 'pupils' -> 'students', 'marks' -> 'cgpa')."""
        query = "Display all pupils with marks greater than 9"
        ir = self.engine.process_query(query)

        self.assertEqual(ir["table"], "students")
        self.assertEqual(ir["conditions"][0]["column"], "cgpa")
        self.assertEqual(ir["conditions"][0]["operator"], ">")
        self.assertEqual(ir["conditions"][0]["value"], 9)

    def test_empty_query_exception(self):
        """Tests empty query handling."""
        with self.assertRaises(ValueError):
            self.engine.process_query("   ")


if __name__ == "__main__":
    unittest.main()
