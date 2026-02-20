import pandas as pd
from pathlib import Path
import logging

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
GOLD_PATH = Path("data/gold/gold_sla_issues.csv")

# ---------------------------
# Colunas obrigatórias
# ---------------------------
REQUIRED_COLUMNS = [
    "issue_id",
    "issue_type",
    "priority",
    "status",
    "assignee_name",
    "created_at",
    "resolved_at",
    "resolution_hours",
    "sla_expected_hours",
    "is_sla_met"
]

# ---------------------------
# Funções de validação
# ---------------------------
def load_gold() -> pd.DataFrame:
    """Carrega o arquivo Gold e retorna o DataFrame."""
    if not GOLD_PATH.exists():
        raise FileNotFoundError(f"Gold file not found: {GOLD_PATH}")
    df = pd.read_csv(GOLD_PATH, parse_dates=["created_at", "resolved_at"])
    logger.info(f"Gold data loaded: {len(df)} records")
    return df


def validate_columns(df: pd.DataFrame) -> bool:
    """Valida se todas as colunas obrigatórias estão presentes."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        logger.error(f"Missing columns: {missing}")
        return False
    logger.info("Schema validation passed.")
    return True


def validate_types(df: pd.DataFrame) -> bool:
    """Valida tipos de dados das colunas."""
    try:
        pd.to_datetime(df["created_at"])
        pd.to_datetime(df["resolved_at"])
        pd.to_numeric(df["resolution_hours"], errors="raise")
        pd.to_numeric(df["sla_expected_hours"], errors="raise")
        if not pd.api.types.is_bool_dtype(df["is_sla_met"]):
            df["is_sla_met"] = df["is_sla_met"].astype(bool)
        logger.info("Data types validation passed.")
        return True
    except Exception as e:
        logger.error(f"Type validation error: {e}")
        return False


def validate_issue_id(df: pd.DataFrame) -> bool:
    """Verifica se issue_id não é nulo."""
    if df["issue_id"].isna().any():
        logger.error("Found null values in issue_id")
        return False
    logger.info("issue_id validation passed.")
    return True


def preview_gold(df: pd.DataFrame, n: int = 5) -> None:
    """Mostra preview do arquivo Gold."""
    logger.info("\n--- Gold layer preview ---")
    logger.info(f"Total records: {len(df)}")
    logger.info(f"Columns:\n{list(df.columns)}")
    logger.info(f"Data types:\n{df.dtypes}")
    logger.info(f"\nFirst {n} records:\n{df.head(n)}")
    logger.info("--- End of preview ---\n")


# ---------------------------
# Pipeline de validação
# ---------------------------
def run_gold_validation():
    logger.info("Running Gold layer validation...\n")

    df = load_gold()
    preview_gold(df)

    col_ok = validate_columns(df)
    types_ok = validate_types(df)
    id_ok = validate_issue_id(df)

    if all([col_ok, types_ok, id_ok]):
        logger.info("🎉 Gold layer validation completed successfully.")
    else:
        logger.error("❌ Gold layer validation failed.")


if __name__ == "__main__":
    run_gold_validation()
