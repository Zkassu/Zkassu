import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Load examples for prompt testing
examples = [json.loads(line) for line in open("data/amharic_examples.jsonl", encoding="utf-8")]

# Filter by category for targeted testing
praise_examples = [e for e in examples if e["category"] == "praise"]

# Use in few-shot prompting
few_shot_prompt = "\n".join([
    f"Comment: {e['comment']}\nReply: {e['reply']}"
    for e in examples[:5]  # Top 5 examples
])

if __name__ == "__main__":
    print(f"Loaded {len(examples)} examples")
    print(f"Found {len(praise_examples)} praise examples")
    print("\nFew-shot prompt preview:\n")
    print(few_shot_prompt)
