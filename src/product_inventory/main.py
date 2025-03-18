#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from crew import ProductInventory

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'query': "LG 185 L 5 Star Inverter Direct-Cool Single Door Refrigerator",
        'path': r"C:\Users\saahil.ali\OneDrive - Accenture\KT Documents\crewAI\image.jpg",
        "file_path": r"C:\Users\priyanka.b.chila\Documents\GenAIML\Downloads\product_details.json",
        "database_connection":r"postgresql:postgres:54321//@localhost:5432/postgres",
        "user_query": "Fetch the data from table",
        "table": "product_details"
    }
    
    try:
        ProductInventory().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        ProductInventory().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        ProductInventory().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    try:
        ProductInventory().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")




if __name__ == "__main__":
        run()