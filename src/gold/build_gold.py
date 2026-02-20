import pandas as pd
from pathlib import Path
from src.sla_calculation import calculate_business_hours, determine_sla_expected, check_sla_met

SILVER_PATH = Path("data/silver/silver_issues.parquet")
GOLD_PATH = Path("data/gold/gold_sla_issues.csv")
REPORT_ANALYST_PATH = Path("data/gold/gold_sla_by_analyst.csv")
REPORT_TYPE_PATH = Path("data/gold/gold_sla_by_issue_type.csv")

def read_silver_data() -> pd.DataFrame:
    """Lê os dados limpos da camada Silver."""
    return pd.read_parquet(SILVER_PATH)

def filter_completed_issues(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra apenas chamados com status Done ou Resolved."""
    return df[df["status"].isin(["Done", "Resolved"])].copy()

def calculate_sla(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula SLA para cada chamado."""
    df["resolution_hours"] = df.apply(
        lambda row: calculate_business_hours(row["created_at"], row["resolved_at"]),
        axis=1
    )
    df["sla_expected_hours"] = df["priority"].apply(determine_sla_expected)
    df["is_sla_met"] = df.apply(
        lambda row: check_sla_met(row["resolution_hours"], row["sla_expected_hours"]),
        axis=1
    )
    return df

def save_gold_data(df: pd.DataFrame) -> None:
    """Salva a tabela final Gold e relatórios agregados."""
    GOLD_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(GOLD_PATH, index=False)
    print(f"🎯 Gold layer created successfully at {GOLD_PATH}")

    # Relatório SLA médio por analista
    df_analyst = df.groupby("assignee_name").agg(
        total_issues=("issue_id", "count"),
        avg_sla_hours=("resolution_hours", "mean")
    ).reset_index()
    df_analyst.to_csv(REPORT_ANALYST_PATH, index=False)
    print(f"📊 SLA by analyst saved at {REPORT_ANALYST_PATH}")

    # Relatório SLA médio por tipo de chamado
    df_type = df.groupby("issue_type").agg(
        total_issues=("issue_id", "count"),
        avg_sla_hours=("resolution_hours", "mean")
    ).reset_index()
    df_type.to_csv(REPORT_TYPE_PATH, index=False)
    print(f"📊 SLA by issue type saved at {REPORT_TYPE_PATH}")

def run_gold_pipeline():
    print("🚀 Running Gold layer pipeline...")
    df = read_silver_data()
    df = filter_completed_issues(df)
    df = calculate_sla(df)
    save_gold_data(df)
    print("✅ Gold layer pipeline completed successfully.")

if __name__ == "__main__":
    run_gold_pipeline()
