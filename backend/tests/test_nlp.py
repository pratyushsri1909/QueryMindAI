"""
Backend Unit Test for NLP Module (Member 1).
"""

import sys
import os
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.nlp import process_natural_language


class TestNLPIntegration(unittest.TestCase):
    def test_sample_query(self):
        query = "Show students with CGPA above 8.5"
        ir = process_natural_language(query)
        self.assertEqual(ir["intent"], "FILTER")
        self.assertEqual(ir["table"], "students")
        self.assertEqual(ir["conditions"][0]["column"], "cgpa")
        self.assertEqual(ir["conditions"][0]["operator"], ">")
        self.assertEqual(ir["conditions"][0]["value"], 8.5)


if __name__ == "__main__":
    unittest.main()
