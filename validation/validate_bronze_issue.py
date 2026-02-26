import json
import sys
from pathlib import Path


BRONZE_PATH = Path("data/bronze/bronze_jira_issues.json")


def validate_bronze(issue_id: str | None = None):
    if not BRONZE_PATH.exists():
        print(f"Arquivo não encontrado: {BRONZE_PATH}")
        return

    with open(BRONZE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    metadata = data.get("metadata", {})
    raw_data = data.get("raw_data", {})
    issues = raw_data.get("issues", [])

    print("\n===== BRONZE INSPECTION =====")
    print(f"Ingested at: {metadata.get('ingested_at')}")
    print(f"Total issues available: {len(issues)}")

    if not issue_id:
        issue_id = input("\nDigite o issue_id para buscar: ").strip()

    target_issue = next(
        (issue for issue in issues if issue.get("id") == issue_id),
        None
    )

    if not target_issue:
        print(f"Issue {issue_id} not found.")
        return

    print(f"\nIssue {issue_id} found!")
    print(json.dumps(target_issue, indent=4))


if __name__ == "__main__":
    issue_id_arg = sys.argv[1] if len(sys.argv) > 1 else None
    validate_bronze(issue_id_arg)
