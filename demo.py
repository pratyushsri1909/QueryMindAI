"""
Interactive Demo & Execution Script for Member 1 (NLP Engine).
QueryMind AI: Natural Language to SQL Assistant.
"""

import json
from nlp_engine import NLPEngine


def run_demo():
    print("=" * 70)
    print("   QueryMind AI — Member 1 (NLP Engine) Live Demonstration")
    print("=" * 70)

    engine = NLPEngine()

    sample_queries = [
        "Show all students having CGPA greater than 8.5",
        "How many students are enrolled?",
        "Show top 5 courses by credits",
        "What is the average CGPA of all students?",
        "Display departments with building block 'A'",
        "List pupils with marks at least 9.0"
    ]

    for idx, query in enumerate(sample_queries, start=1):
        print(f"\n[Test Case {idx}]")
        print(f"Natural Language Query: \"{query}\"")
        try:
            ir_result = engine.process_query(query)
            print("Generated Intermediate Representation (IR JSON):")
            print(json.dumps(ir_result, indent=2))
        except Exception as e:
            print(f"Error processing query: {e}")

    print("\n" + "=" * 70)
    print("Interactive Mode: Type your own English query below (or 'exit' to quit):")
    print("=" * 70)

    while True:
        try:
            user_input = input("\nEnter query > ").strip()
            if user_input.lower() in ("exit", "quit", "q"):
                print("Exiting NLP Engine demo.")
                break
            if not user_input:
                continue
            ir_result = engine.process_query(user_input)
            print(json.dumps(ir_result, indent=2))
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
        except Exception as err:
            print(f"Error: {err}")


if __name__ == "__main__":
    run_demo()
