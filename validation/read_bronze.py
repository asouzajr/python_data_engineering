import json
from pathlib import Path
import pprint

BRONZE_PATH = Path("data/bronze/bronze_jira_issues.json")

with open(BRONZE_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)

print("\n=== TOP LEVEL KEYS ===")
print(data.keys())

print("\n=== FIRST ISSUE SAMPLE ===")
pprint.pprint(data["issues"][0])
