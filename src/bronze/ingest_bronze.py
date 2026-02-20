import json
import os
from pathlib import Path

def read_json_file(file_path: str) -> dict:
    """Read JSON file from local path."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_bronze_file(data: dict, output_path: str) -> None:
    """Save raw JSON data into bronze layer."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def main():
    input_path = "resources/jira_issues_raw.json"
    output_path = "data/bronze/bronze_jira_issues.json"

    # Ler o JSON
    data = read_json_file(input_path)  # <-- aqui data é definido

    # Validação simples
    if "issues" not in data or not isinstance(data["issues"], list) or len(data["issues"]) == 0:
        print("Warning: JSON vazio ou sem a chave 'issues'. Nada será salvo.")
        return

    # Criar bronze_data com metadados
    bronze_data = {
        "project": data.get("project", {}),
        "issues": data["issues"]
    }

    # Salvar arquivo Bronze
    save_bronze_file(bronze_data, output_path)
    print("Bronze layer created successfully.")

if __name__ == "__main__":
    main()
