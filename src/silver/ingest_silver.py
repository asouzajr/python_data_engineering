import pandas as pd
import json
import logging
from pathlib import Path

# ---------------------------
# Logging configuration
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# ---------------------------
# Paths
# ---------------------------
BRONZE_PATH = Path("data/bronze/bronze_jira_issues.json")
SILVER_PATH = Path("data/silver/silver_issues.parquet")


# ---------------------------
# Functions
# ---------------------------
def read_bronze_data() -> pd.DataFrame:
    """Read raw JSON and normalize issues."""
    with open(BRONZE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    df = pd.json_normalize(data["issues"])
    logger.info(f"Raw issues loaded: {len(df)}")
    return df


def transform_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Explode nested lists and select required columns."""

    # Explode assignee list
    df = df.explode("assignee")

    # Explode timestamps list
    df = df.explode("timestamps")

    # Extract internal fields safely
    df["assignee_name"] = df["assignee"].apply(
        lambda x: x.get("name") if isinstance(x, dict) else None
    )
    df["created_at"] = df["timestamps"].apply(
        lambda x: x.get("created_at") if isinstance(x, dict) else None
    )
    df["resolved_at"] = df["timestamps"].apply(
        lambda x: x.get("resolved_at") if isinstance(x, dict) else None
    )

    # Keep only necessary columns
    df_transformed = df[
        [
            "id",
            "issue_type",
            "priority",
            "status",
            "assignee_name",
            "created_at",
            "resolved_at",
        ]
    ].rename(columns={"id": "issue_id"})

    logger.info("Nested fields exploded and columns transformed.")
    return df_transformed


def convert_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert date columns to datetime and drop invalid rows."""
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
    df["resolved_at"] = pd.to_datetime(df["resolved_at"], errors="coerce", utc=True)

    # Remove rows with invalid created_at
    df = df.dropna(subset=["created_at"])
    logger.info("Datetime conversion completed.")
    return df


def save_silver_data(df: pd.DataFrame) -> None:
    """Persist cleaned data to silver layer."""
    SILVER_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(SILVER_PATH, index=False)
    logger.info(f"Silver layer successfully created at {SILVER_PATH}")
    logger.info(f"Final record count: {len(df)}")


# ---------------------------
# Main pipeline
# ---------------------------
def run_silver_pipeline():
    logger.info("Starting Silver layer transformation...")

    df = read_bronze_data()
    df = transform_columns(df)
    df = convert_datetime_columns(df)
    save_silver_data(df)


if __name__ == "__main__":
    run_silver_pipeline()
