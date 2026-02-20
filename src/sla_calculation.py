import pandas as pd
from datetime import datetime
import holidays

# Define SLA esperado por prioridade (em horas)
SLA_RULES = {
    "High": 24,
    "Medium": 72,
    "Low": 120
}

def calculate_business_hours(start: pd.Timestamp, end: pd.Timestamp) -> float:
    """Calcula horas úteis entre duas datas, excluindo finais de semana e feriados nacionais."""
    if pd.isna(start) or pd.isna(end):
        return None
    
    # Feriados do Brasil
    br_holidays = holidays.Brazil(years=[start.year, end.year])
    
    total_hours = 0
    current = start
    while current < end:
        if current.weekday() < 5 and current.date() not in br_holidays:
            total_hours += 1
        current += pd.Timedelta(hours=1)
    
    return total_hours

def determine_sla_expected(priority: str) -> int:
    """Retorna o SLA esperado baseado na prioridade."""
    return SLA_RULES.get(priority, None)

def check_sla_met(resolution_hours: float, sla_expected: int) -> bool:
    """Indica se o SLA foi atendido."""
    if resolution_hours is None or sla_expected is None:
        return False
    return resolution_hours <= sla_expected
