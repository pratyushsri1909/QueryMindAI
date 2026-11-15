"""
Mandatory Test Suite for Member 1 (NLP Module)
Strictly adheres to Section 9 of Team Integration Contract Version 1.0.
"""

import unittest
from backend.app.nlp import process_natural_language


class TestMember1NLPModule(unittest.TestCase):
    """Verifies all mandatory test cases from Integration Contract Section 9."""

    def test_01_show_all_students(self):
        """Query: 'Show all students' -> Expected: SELECT"""
        query = "Show all students"
        ir = process_natural_language(query)

        self.assertEqual(ir["intent"], "SELECT")
        self.assertEqual(ir["table"], "students")
        self.assertIn("name", ir["columns"])
        self.assertEqual(ir["conditions"], [])
        self.assertEqual(ir["joins"], [])
        self.assertEqual(ir["aggregations"], [])
        self.assertEqual(ir["group_by"], [])
        self.assertEqual(ir["order_by"], [])
        self.assertIsNone(ir["limit"])

    def test_02_show_students_cgpa_above_8_5(self):
        """Query: 'Show students with CGPA above 8.5' -> Expected: FILTER"""
        query = "Show students with CGPA above 8.5"
        ir = process_natural_language(query)

        self.assertEqual(ir["intent"], "FILTER")
        self.assertEqual(ir["table"], "students")
        self.assertIn("name", ir["columns"])
        self.assertIn("cgpa", ir["columns"])
        self.assertEqual(len(ir["conditions"]), 1)
        self.assertEqual(ir["conditions"][0]["column"], "cgpa")
        self.assertEqual(ir["conditions"][0]["operator"], ">")
        self.assertEqual(ir["conditions"][0]["value"], 8.5)
        self.assertEqual(ir["joins"], [])
        self.assertEqual(ir["aggregations"], [])
        self.assertEqual(ir["group_by"], [])
        self.assertEqual(ir["order_by"], [])
        self.assertIsNone(ir["limit"])

    def test_03_find_students_from_cse_department(self):
        """Query: 'Find students from CSE department' -> Expected: FILTER"""
        query = "Find students from CSE department"
        ir = process_natural_language(query)

        self.assertEqual(ir["intent"], "FILTER")
        self.assertEqual(ir["table"], "students")
        self.assertEqual(len(ir["conditions"]), 1)
        self.assertEqual(ir["conditions"][0]["column"], "department")
        self.assertEqual(ir["conditions"][0]["operator"], "=")
        self.assertEqual(ir["conditions"][0]["value"], "CSE")

    def test_04_show_students_descending_cgpa_order(self):
        """Query: 'Show students in descending CGPA order' -> Expected: ORDER BY"""
        query = "Show students in descending CGPA order"
        ir = process_natural_language(query)

        self.assertEqual(ir["intent"], "SELECT")
        self.assertEqual(ir["table"], "students")
        self.assertEqual(len(ir["order_by"]), 1)
        self.assertEqual(ir["order_by"][0]["column"], "cgpa")
        self.assertEqual(ir["order_by"][0]["direction"], "DESC")
        self.assertIsNone(ir["limit"])

    def test_05_show_top_5_students(self):
        """Query: 'Show the top 5 students' -> Expected: ORDER BY + LIMIT"""
        query = "Show the top 5 students"
        ir = process_natural_language(query)

        self.assertEqual(ir["intent"], "SELECT")
        self.assertEqual(ir["table"], "students")
        self.assertEqual(len(ir["order_by"]), 1)
        self.assertEqual(ir["order_by"][0]["column"], "cgpa")
        self.assertEqual(ir["order_by"][0]["direction"], "DESC")
        self.assertEqual(ir["limit"], 5)

    def test_06_count_all_students(self):
        """Query: 'Count all students' -> Expected: COUNT (AGGREGATE)"""
        query = "Count all students"
        ir = process_natural_language(query)

        self.assertEqual(ir["intent"], "AGGREGATE")
        self.assertEqual(ir["table"], "students")
        self.assertEqual(len(ir["aggregations"]), 1)
        self.assertEqual(ir["aggregations"][0]["function"], "COUNT")
        self.assertEqual(ir["aggregations"][0]["column"], "*")

    def test_07_find_average_cgpa(self):
        """Query: 'Find average CGPA' -> Expected: AVG (AGGREGATE)"""
        query = "Find average CGPA"
        ir = process_natural_language(query)

        self.assertEqual(ir["intent"], "AGGREGATE")
        self.assertEqual(ir["table"], "students")
        self.assertEqual(len(ir["aggregations"]), 1)
        self.assertEqual(ir["aggregations"][0]["function"], "AVG")
        self.assertEqual(ir["aggregations"][0]["column"], "cgpa")

    def test_08_show_students_enrolled_in_each_course(self):
        """Query: 'Show students enrolled in each course' -> Expected: JOIN"""
        query = "Show students enrolled in each course"
        ir = process_natural_language(query)

        self.assertEqual(ir["intent"], "SELECT")
        self.assertEqual(ir["table"], "students")
        self.assertEqual(len(ir["joins"]), 1)
        self.assertEqual(ir["joins"][0]["table"], "enrollments")
        self.assertEqual(ir["joins"][0]["type"], "INNER")
        self.assertEqual(ir["joins"][0]["left_column"], "students.student_id")
        self.assertEqual(ir["joins"][0]["right_column"], "enrollments.student_id")

    def test_09_find_average_cgpa_department_wise(self):
        """Query: 'Find average CGPA department-wise' -> Expected: GROUP BY + AVG"""
        query = "Find average CGPA department-wise"
        ir = process_natural_language(query)

        self.assertEqual(ir["intent"], "AGGREGATE")
        self.assertEqual(ir["table"], "students")
        self.assertEqual(len(ir["aggregations"]), 1)
        self.assertEqual(ir["aggregations"][0]["function"], "AVG")
        self.assertEqual(ir["group_by"], ["department"])

    def test_10_unsupported_or_empty_query_error(self):
        """Verifies structured error response for empty or invalid query."""
        ir = process_natural_language("  ")
        self.assertFalse(ir.get("success", True))
        self.assertEqual(ir["error"]["code"], "UNSUPPORTED_QUERY")


if __name__ == "__main__":
    unittest.main()
