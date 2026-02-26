import pandas as pd
import json
import logging
import os
from pathlib import Path

from src.utils.env_loader import load_env_file


# ---------------------------
# Logging configuration (ISO 8601)
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

logger = logging.getLogger(__name__)


def read_bronze_data(bronze_path: Path) -> pd.DataFrame:
    """
    Read Bronze JSON file and normalize issues.
    """

    logger.info("Reading Bronze file from %s", bronze_path)

    if not bronze_path.exists():
        logger.error("Bronze file not found: %s", bronze_path)
        raise FileNotFoundError(f"Bronze file not found: {bronze_path}")

    with bronze_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if "raw_data" not in data or "issues" not in data["raw_data"]:
        logger.error("Invalid Bronze structure: 'raw_data.issues' not found")
        raise KeyError(
            "Invalid Bronze structure: 'raw_data.issues' not found"
        )

    df = pd.json_normalize(data["raw_data"]["issues"])
    logger.info("Raw issues loaded: %s", len(df))

    return df


def transform_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Explode nested fields and select relevant columns.
    """

    logger.info("Transforming nested fields...")

    if "assignee" not in df.columns or "timestamps" not in df.columns:
        raise KeyError("Expected columns 'assignee' or 'timestamps' missing")

    df = df.explode("assignee")
    df = df.explode("timestamps")

    df["assignee_name"] = df["assignee"].apply(
        lambda x: x.get("name") if isinstance(x, dict) else None
    )

    df["created_at"] = df["timestamps"].apply(
        lambda x: x.get("created_at") if isinstance(x, dict) else None
    )

    df["resolved_at"] = df["timestamps"].apply(
        lambda x: x.get("resolved_at") if isinstance(x, dict) else None
    )

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

    logger.info("Columns transformed successfully.")

    return df_transformed


def convert_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert date columns to UTC datetime format.
    """

    logger.info("Converting datetime columns to UTC...")

    df["created_at"] = pd.to_datetime(
        df["created_at"], errors="coerce", utc=True
    )

    df["resolved_at"] = pd.to_datetime(
        df["resolved_at"], errors="coerce", utc=True
    )

    initial_count = len(df)
    df = df.dropna(subset=["created_at"])
    final_count = len(df)

    logger.info(
        "Datetime conversion completed. Dropped %s invalid rows.",
        initial_count - final_count
    )

    return df


def save_silver_data(df: pd.DataFrame, silver_path: Path) -> None:
    """
    Persist transformed data to Silver layer.
    """

    logger.info("Saving Silver file to %s", silver_path)

    silver_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(silver_path, index=False)

    logger.info("Silver layer created successfully.")
    logger.info("Final record count: %s", len(df))


def run_silver_pipeline() -> None:
    """
    Execute Silver layer transformation pipeline.
    """

    load_env_file()

    bronze_path = Path(
        os.getenv(
            "JIRA_BRONZE_OUTPUT_PATH",
            "data/bronze/bronze_jira_issues.json"
        )
    )

    silver_path = Path(
        os.getenv(
            "JIRA_SILVER_OUTPUT_PATH",
            "data/silver/silver_issues.parquet"
        )
    )

    logger.info("Starting Silver layer transformation process.")

    df = read_bronze_data(bronze_path)
    df = transform_columns(df)
    df = convert_datetime_columns(df)
    save_silver_data(df, silver_path)

    logger.info("Silver pipeline finished successfully.")


if __name__ == "__main__":
    run_silver_pipeline()
