"""
Interactive Demonstration Script for Member 1 (NLP Module).
QueryMind AI — Team Integration Contract Version 1.0.
"""

import json
from backend.app.nlp import process_natural_language


def run_demo():
    print("=" * 80)
    print("      QueryMind AI — Member 1 (NLP Module) Demonstration")
    print("      Team Integration Contract Version 1.0 Compliant")
    print("=" * 80)

    mandatory_queries = [
        ("Show all students", "SELECT"),
        ("Show students with CGPA above 8.5", "FILTER"),
        ("Find students from CSE department", "FILTER"),
        ("Show students in descending CGPA order", "ORDER BY"),
        ("Show the top 5 students", "ORDER BY + LIMIT"),
        ("Count all students", "COUNT"),
        ("Find average CGPA", "AVG"),
        ("Show students enrolled in each course", "JOIN"),
        ("Find average CGPA department-wise", "GROUP BY + AVG")
    ]

    for idx, (query, expected_op) in enumerate(mandatory_queries, start=1):
        print(f"\n[Mandatory Test Case {idx} | Expected: {expected_op}]")
        print(f"Query: \"{query}\"")
        ir = process_natural_language(query)
        print("Generated Canonical IR:")
        print(json.dumps(ir, indent=2))

    print("\n" + "=" * 80)
    print("Interactive Mode: Type any natural language query (or 'exit' to quit):")
    print("=" * 80)

    while True:
        try:
            user_input = input("\nEnter query > ").strip()
            if user_input.lower() in ("exit", "quit", "q"):
                print("Exiting demo.")
                break
            if not user_input:
                continue
            ir = process_natural_language(user_input)
            print(json.dumps(ir, indent=2))
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    run_demo()
