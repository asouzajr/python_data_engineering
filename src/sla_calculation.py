from typing import Optional, Set
from datetime import datetime
import requests
import pandas as pd


SLA_RULES = {
    "High": 24,
    "Medium": 72,
    "Low": 120,
}


def get_brazilian_holidays(year: int) -> Set[datetime.date]:
    """
    Fetch Brazilian national holidays from public API.

    API used:
    https://brasilapi.com.br/api/feriados/v1/{year}
    """
    url = f"https://brasilapi.com.br/api/feriados/v1/{year}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    holidays_data = response.json()

    holiday_dates = set()

    for item in holidays_data:
        holiday_date = datetime.strptime(
            item["date"],
            "%Y-%m-%d",
        ).date()
        holiday_dates.add(holiday_date)

    return holiday_dates


def calculate_business_hours(
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> Optional[float]:
    """
    Calculate business hours between two timestamps.

    Excludes:
    - Weekends
    - Brazilian national holidays (via public API)
    """
    if pd.isna(start) or pd.isna(end):
        return None

    if not isinstance(start, pd.Timestamp) or not isinstance(
        end,
        pd.Timestamp,
    ):
        return None

    if end < start:
        return None

    start_year = start.year
    end_year = end.year

    holidays_set = set()

    for year in range(start_year, end_year + 1):
        yearly_holidays = get_brazilian_holidays(year)
        holidays_set.update(yearly_holidays)

    total_hours = 0.0
    current = start

    while current < end:
        is_weekday = current.weekday() < 5
        is_holiday = current.date() in holidays_set

        if is_weekday and not is_holiday:
            total_hours += 1

        current += pd.Timedelta(hours=1)

    return total_hours


def determine_sla_expected(priority: str) -> Optional[int]:
    """
    Return expected SLA in hours based on priority.
    """
    if priority == "High":
        return SLA_RULES["High"]
    elif priority == "Medium":
        return SLA_RULES["Medium"]
    elif priority == "Low":
        return SLA_RULES["Low"]
    else:
        return None


def check_sla_met(
    resolution_hours: Optional[float],
    sla_expected: Optional[int],
) -> bool:
    """
    Check whether SLA was met.
    """
    if resolution_hours is None:
        return False

    if sla_expected is None:
        return False

    return resolution_hours <= sla_expected
