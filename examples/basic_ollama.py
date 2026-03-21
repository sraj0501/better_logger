import os

from better_logger import OllamaFailureAnalyzer, stage, story

model = os.environ["BETTER_LOGGER_MODEL"]
endpoint = os.getenv("BETTER_LOGGER_ENDPOINT", "http://127.0.0.1:11434/api/generate")
analyzer = OllamaFailureAnalyzer(model=model, endpoint=endpoint)

with story("Import Customers", failure_analyzer=analyzer):
    with stage("Load CSV"):
        rows = ["alice", "bob"]

    with stage("Validate Data"):
        if not rows:
            raise ValueError("No rows found")

    with stage("Insert Records"):
        raise ValueError("duplicate customer id")
