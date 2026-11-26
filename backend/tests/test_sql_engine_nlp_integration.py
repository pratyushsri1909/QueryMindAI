"""Integration tests connecting Member 1's actual NLP module with Member 2's SQL Engine."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.nlp import process_natural_language
from backend.app.sql_engine import process_ir


class TestSQLEngineNLPIntegration(unittest.TestCase):
    """End-to-end integration tests between NLP Module (Member 1) and SQL Engine (Member 2)."""

    def test_01_nlp_show_all_students(self):
        """NLP Query: 'Show all students' -> SQL Engine."""
        query = "Show all students"
        ir = process_natural_language(query)
        res = process_ir(ir)

        self.assertTrue(res["success"], f"Failed for query '{query}': {res}")
        self.assertIn("SELECT", res["generated_sql"])
        self.assertIn("FROM students", res["generated_sql"])
        self.assertEqual(res["params"], {})

    def test_02_nlp_show_students_cgpa_above_8_5(self):
        """NLP Query: 'Show students with CGPA above 8.5' -> SQL Engine."""
        query = "Show students with CGPA above 8.5"
        ir = process_natural_language(query)
        res = process_ir(ir)

        self.assertTrue(res["success"], f"Failed for query '{query}': {res}")
        self.assertIn("FROM students WHERE students.cgpa > :p0", res["generated_sql"])
        self.assertEqual(res["params"], {"p0": 8.5})

    def test_03_nlp_find_students_from_cse_department(self):
        """NLP Query: 'Find students from CSE department' -> SQL Engine."""
        query = "Find students from CSE department"
        ir = process_natural_language(query)
        res = process_ir(ir)

        self.assertTrue(res["success"], f"Failed for query '{query}': {res}")
        self.assertIn("FROM students WHERE students.department = :p0", res["generated_sql"])
        self.assertEqual(res["params"], {"p0": "CSE"})

    def test_04_nlp_show_students_descending_cgpa_order(self):
        """NLP Query: 'Show students in descending CGPA order' -> SQL Engine."""
        query = "Show students in descending CGPA order"
        ir = process_natural_language(query)
        res = process_ir(ir)

        self.assertTrue(res["success"], f"Failed for query '{query}': {res}")
        self.assertIn("ORDER BY students.cgpa DESC", res["generated_sql"])

    def test_05_nlp_show_the_top_5_students(self):
        """NLP Query: 'Show the top 5 students' -> SQL Engine."""
        query = "Show the top 5 students"
        ir = process_natural_language(query)
        res = process_ir(ir)

        self.assertTrue(res["success"], f"Failed for query '{query}': {res}")
        self.assertIn("ORDER BY students.cgpa DESC", res["generated_sql"])
        self.assertIn("LIMIT 5", res["generated_sql"])

    def test_06_nlp_count_all_students(self):
        """NLP Query: 'Count all students' -> SQL Engine."""
        query = "Count all students"
        ir = process_natural_language(query)
        res = process_ir(ir)

        self.assertTrue(res["success"], f"Failed for query '{query}': {res}")
        self.assertIn("SELECT COUNT(*) AS total_count FROM students", res["generated_sql"])

    def test_07_nlp_find_average_cgpa(self):
        """NLP Query: 'Find average CGPA' -> SQL Engine."""
        query = "Find average CGPA"
        ir = process_natural_language(query)
        res = process_ir(ir)

        self.assertTrue(res["success"], f"Failed for query '{query}': {res}")
        self.assertIn("SELECT AVG(students.cgpa) AS average_cgpa FROM students", res["generated_sql"])

    def test_08_nlp_show_students_enrolled_in_each_course_multihop(self):
        """NLP Query: 'Show students enrolled in each course' -> SQL Engine (2-hop JOIN)."""
        query = "Show students enrolled in each course"
        ir = process_natural_language(query)
        res = process_ir(ir)

        self.assertTrue(res["success"], f"Failed for query '{query}': {res}")
        self.assertIn("SELECT students.name, courses.course_name FROM students", res["generated_sql"])
        self.assertIn("INNER JOIN enrollments ON students.student_id = enrollments.student_id", res["generated_sql"])
        self.assertIn("INNER JOIN courses ON enrollments.course_id = courses.course_id", res["generated_sql"])

    def test_09_nlp_find_average_cgpa_department_wise(self):
        """NLP Query: 'Find average CGPA department-wise' -> SQL Engine (GROUP BY + AVG)."""
        query = "Find average CGPA department-wise"
        ir = process_natural_language(query)
        res = process_ir(ir)

        self.assertTrue(res["success"], f"Failed for query '{query}': {res}")
        self.assertIn("GROUP BY students.department", res["generated_sql"])
        self.assertIn("AVG(students.cgpa) AS average_cgpa", res["generated_sql"])

    def test_10_nlp_multiple_conditions_compound_query(self):
        """NLP Query: 'Find students with CGPA above 8.0 and department CSE' -> SQL Engine."""
        query = "Find students with CGPA above 8.0 and department CSE"
        ir = process_natural_language(query)
        res = process_ir(ir)

        self.assertTrue(res["success"], f"Failed for query '{query}': {res}")
        self.assertIn("WHERE", res["generated_sql"])
        self.assertIn("students.cgpa > :p", res["generated_sql"])
        self.assertIn("students.department = :p", res["generated_sql"])
        # Verify both parameters are bound
        param_vals = set(res["params"].values())
        self.assertIn(8.0, param_vals)
        self.assertIn("CSE", param_vals)

    def test_11_nlp_out_of_domain_entity_handling(self):
        """NLP Query with unrecognized entity: 'Show all rockets launched into orbit'."""
        query = "Show all rockets launched into orbit"
        ir = process_natural_language(query)
        self.assertFalse(ir.get("success", True))
        # Passing this failure IR into process_ir must yield a clean structured error
        res = process_ir(ir)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"]["code"], "ENTITY_NOT_FOUND")

    def test_12_nlp_empty_query_handling(self):
        """NLP Query with empty string -> returns UNSUPPORTED_QUERY error."""
        query = "   "
        ir = process_natural_language(query)
        self.assertFalse(ir.get("success", True))
        res = process_ir(ir)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"]["code"], "UNSUPPORTED_QUERY")

    def test_13_nlp_show_top_students_ordered_by_cgpa(self):
        """NLP Query: 'Show top students ordered by CGPA' -> ORDER BY students.cgpa DESC."""
        query = "Show top students ordered by CGPA"
        ir = process_natural_language(query)
        res = process_ir(ir)

        self.assertTrue(res["success"], f"Failed for query '{query}': {res}")
        self.assertIn("ORDER BY students.cgpa DESC", res["generated_sql"])

    def test_14_nlp_enrollments_avg_does_not_target_varchar_grade(self):
        """Ensure AVG on enrollments does not generate invalid AVG(enrollments.grade)."""
        query = "Find average enrollment grade"
        ir = process_natural_language(query)
        assert not any(
            agg.get("function") == "AVG" and agg.get("column") == "grade"
            for agg in ir.get("aggregations", [])
        )


if __name__ == "__main__":
    unittest.main()
