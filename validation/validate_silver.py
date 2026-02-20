import pandas as pd
from pathlib import Path


SILVER_PATH = Path("data/silver/silver_issues.parquet")

REQUIRED_COLUMNS = [
    "issue_id",
    "issue_type",
    "priority",
    "status",
    "assignee_name",
    "created_at",
    "resolved_at"
]


def validate_silver_schema(df: pd.DataFrame) -> None:
    """Validate required columns."""
    
    missing_columns = [
        col for col in REQUIRED_COLUMNS if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    print("✅ Schema validation passed.")


def validate_datetime_types(df: pd.DataFrame) -> None:
    """Validate datetime columns."""

    if not pd.api.types.is_datetime64_any_dtype(df["created_at"]):
        raise TypeError("created_at is not datetime")

    if not pd.api.types.is_datetime64_any_dtype(df["resolved_at"]):
        raise TypeError("resolved_at is not datetime")

    print("✅ Datetime validation passed.")


def validate_no_null_issue_id(df: pd.DataFrame) -> None:
    """Ensure issue_id has no null values."""

    if df["issue_id"].isnull().any():
        raise ValueError("There are null issue_id values.")

    print("✅ issue_id validation passed.")


def run_validation():
    print("Running Silver layer validation...\n")

    if not SILVER_PATH.exists():
        raise FileNotFoundError("Silver file does not exist.")

    df = pd.read_parquet(SILVER_PATH)

    validate_silver_schema(df)
    validate_datetime_types(df)
    validate_no_null_issue_id(df)

    print("\n🎉 Silver layer validation completed successfully.")


if __name__ == "__main__":
    run_validation()
