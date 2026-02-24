import json
from pathlib import Path


BRONZE_PATH = Path("data/bronze/bronze_jira_issues.json")


def validate_bronze():
    if not BRONZE_PATH.exists():
        print(f"Arquivo não encontrado: {BRONZE_PATH}")
        return

    with open(BRONZE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("\n===== BRONZE STRUCTURE =====")

    # Root level
    print("\nRoot keys:")
    for key in data.keys():
        print(f" - {key} (type: {type(data[key]).__name__})")

    # Metadata
    metadata = data.get("metadata", {})
    print("\nMetadata:")
    for key, value in metadata.items():
        print(f" - {key}: {value}")

    # Raw data
    raw_data = data.get("raw_data", {})
    project = raw_data.get("project", {})
    issues = raw_data.get("issues", [])

    print("\nProject Info:")
    for key, value in project.items():
        print(f" - {key}: {value}")

    print(f"\nTotal issues: {len(issues)}")

    # Show schema of first issue
    if issues:
        print("\nFields in first issue:")
        for key, value in issues[0].items():
            print(f" - {key} (type: {type(value).__name__})")

        print("\nSample issue:")
        print(json.dumps(issues[0], indent=4))
    else:
        print("Nenhuma issue encontrada.")


if __name__ == "__main__":
    validate_bronze()
