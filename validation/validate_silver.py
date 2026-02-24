import pandas as pd
from pathlib import Path


SILVER_PATH = Path("data/silver/silver_issues.parquet")


def validate_silver():
    if not SILVER_PATH.exists():
        print(f"Arquivo não encontrado: {SILVER_PATH}")
        return

    print("\n===== SILVER STRUCTURE =====")

    # Read parquet
    df = pd.read_parquet(SILVER_PATH)

    # Basic info
    print(f"\nTotal records: {len(df)}")
    print(f"Total columns: {len(df.columns)}")

    print("\nColumns and Data Types:")
    for col in df.columns:
        print(f" - {col}: {df[col].dtype}")

    # Check timezone awareness
    print("\nDatetime Columns Analysis:")
    for col in df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
        print(f" - {col} is timezone-aware (UTC)")

    # Null analysis
    print("\nNull values per column:")
    print(df.isnull().sum())

    # Show sample rows
    print("\nSample records:")
    print(df.head(5))


if __name__ == "__main__":
    validate_silver()
