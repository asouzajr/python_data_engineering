import pandas as pd
import sys
from pathlib import Path


SILVER_PATH = Path("data/silver/silver_issues.parquet")


def validate_silver(issue_id: str | None = None):
    if not SILVER_PATH.exists():
        print(f"Arquivo não encontrado: {SILVER_PATH}")
        return

    print("\n===== SILVER INSPECTION =====")

    df = pd.read_parquet(SILVER_PATH)

    print(f"\nTotal records: {len(df)}")
    print(f"Total columns: {len(df.columns)}")

    print("\nColumns and Data Types:")
    for col in df.columns:
        print(f" - {col}: {df[col].dtype}")

    print("\nDatetime Columns Analysis:")
    for col in df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
        print(f" - {col} is timezone-aware (UTC)")

    print("\nNull values per column:")
    print(df.isnull().sum())

    # 🔎 Issue-specific inspection
    if not issue_id:
        issue_id = input("\nDigite o issue_id para buscar (ou pressione Enter para sair): ").strip()

    if not issue_id:
        print("\nNenhum issue_id informado. Execução finalizada.")
        return

    print(f"\nSearching for issue_id = {issue_id}...")

    filtered_df = df[df["issue_id"] == issue_id]

    if filtered_df.empty:
        print(f"Issue {issue_id} not found in Silver layer.")
        return

    print(f"\nIssue {issue_id} found!")
    print(f"Number of records for this issue: {len(filtered_df)}")

    print("\nFiltered records:")
    print(filtered_df)


if __name__ == "__main__":
    issue_id_arg = sys.argv[1] if len(sys.argv) > 1 else None
    validate_silver(issue_id_arg)
