import logging
import os
from pathlib import Path

import pandas as pd

from src.utils.env_loader import load_env_file
from src.sla_calculation import (
    calculate_business_hours,
    determine_sla_expected,
    check_sla_met,
)


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)


def read_silver_data(path: Path) -> pd.DataFrame:
    """Read Silver layer data."""
    if not path.exists():
        logger.error("Silver file not found at %s", path)
        raise FileNotFoundError(f"Silver file not found: {path}")

    logger.info("Reading Silver data from %s", path)
    df = pd.read_parquet(path)

    if df.empty:
        logger.warning("Silver dataset is empty.")

    return df


def filter_completed_issues(df: pd.DataFrame) -> pd.DataFrame:
    """Filter only completed issues."""
    logger.info("Filtering completed issues (Done, Resolved).")

    filtered = (
        df[df["status"].isin(["Done", "Resolved"])]
        .copy()
        .reset_index(drop=True)
    )

    logger.info("Filtered dataset contains %s records.", len(filtered))
    return filtered


def calculate_sla(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate SLA metrics."""
    logger.info("Calculating SLA metrics.")

    df = df.copy()

    df["resolution_hours"] = df.apply(
        lambda row: calculate_business_hours(
            row["created_at"],
            row["resolved_at"],
        ),
        axis=1,
    )

    df["sla_expected_hours"] = df["priority"].apply(
        determine_sla_expected
    )

    df["is_sla_met"] = df.apply(
        lambda row: check_sla_met(
            row["resolution_hours"],
            row["sla_expected_hours"],
        ),
        axis=1,
    )

    return df


def save_gold_outputs(
    df: pd.DataFrame,
    gold_path: Path,
    analyst_path: Path,
    type_path: Path,
) -> None:
    """Persist Gold dataset and aggregated reports."""

    # Garantir criação de todas as pastas
    gold_path.parent.mkdir(parents=True, exist_ok=True)
    analyst_path.parent.mkdir(parents=True, exist_ok=True)
    type_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Saving Gold dataset to %s", gold_path)
    df.to_csv(gold_path, index=False)

    logger.info("Generating SLA report by analyst.")
    df_analyst = (
        df.groupby("assignee_name", dropna=False)
        .agg(
            total_issues=("issue_id", "count"),
            avg_sla_hours=("resolution_hours", "mean"),
        )
        .reset_index()
    )

    df_analyst.to_csv(analyst_path, index=False)

    logger.info("Generating SLA report by issue type.")
    df_type = (
        df.groupby("issue_type", dropna=False)
        .agg(
            total_issues=("issue_id", "count"),
            avg_sla_hours=("resolution_hours", "mean"),
        )
        .reset_index()
    )

    df_type.to_csv(type_path, index=False)

    logger.info("Gold layer outputs successfully created.")


def main() -> None:
    """Gold layer execution pipeline."""
    load_env_file()

    silver_path = Path(
        os.getenv(
            "JIRA_SILVER_OUTPUT_PATH",
            "data/silver/silver_issues.parquet",
        )
    )

    gold_path = Path(
        os.getenv(
            "JIRA_GOLD_OUTPUT_PATH",
            "data/gold/gold_sla_issues.csv",
        )
    )

    analyst_path = Path(
        os.getenv(
            "JIRA_GOLD_ANALYST_REPORT_PATH",
            "data/gold/gold_sla_by_analyst.csv",
        )
    )

    type_path = Path(
        os.getenv(
            "JIRA_GOLD_TYPE_REPORT_PATH",
            "data/gold/gold_sla_by_issue_type.csv",
        )
    )

    logger.info("Starting Gold layer pipeline.")

    df = read_silver_data(silver_path)
    df = filter_completed_issues(df)
    df = calculate_sla(df)

    save_gold_outputs(df, gold_path, analyst_path, type_path)

    logger.info("Gold layer pipeline completed successfully.")


if __name__ == "__main__":
    main()
