from narrative import OllamaFailureAnalyzer, stage, story

analyzer = OllamaFailureAnalyzer(model="qwen2.5-coder:7b")

with story("Import Customers", failure_analyzer=analyzer):
    with stage("Load CSV"):
        rows = ["alice", "bob"]

    with stage("Validate Data"):
        if not rows:
            raise ValueError("No rows found")

    with stage("Insert Records"):
        raise ValueError("duplicate customer id")
