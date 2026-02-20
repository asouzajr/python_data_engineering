import json
from pathlib import Path

def validate_bronze_file(bronze_path: str):
    """Valida o arquivo Bronze e imprime informações importantes."""
    path = Path(bronze_path)
    if not path.exists():
        print(f"Erro: arquivo não encontrado em {bronze_path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        bronze_data = json.load(f)

    # Checar chaves principais
    keys = list(bronze_data.keys())
    print("Chaves do JSON Bronze:", keys)

    # Checar número de issues
    issues = bronze_data.get("issues", [])
    print("Número de issues:", len(issues))

    # Checar metadados do projeto
    project = bronze_data.get("project", {})
    print("Projeto ID:", project.get("project_id", "N/A"))
    print("Projeto Name:", project.get("project_name", "N/A"))
    print("Extraído em:", project.get("extracted_at", "N/A"))

    # Mostrar primeira issue como exemplo
    if issues:
        print("\nPrimeira issue:")
        print(json.dumps(issues[0], indent=4))
    else:
        print("Nenhuma issue encontrada.")

def main():
    # Caminho relativo a partir da raiz do projeto
    bronze_file = "data/bronze/bronze_jira_issues.json"
    validate_bronze_file(bronze_file)

if __name__ == "__main__":
    main()
