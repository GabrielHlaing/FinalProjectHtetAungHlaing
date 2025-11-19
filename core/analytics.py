# analytics.py

from typing import Dict, List
from core.database import get_all_transactions


# --------------------------------------------------
# Helper: Convert SQLite rows into Python dictionaries
# --------------------------------------------------
def _rows_to_dicts(rows) -> List[dict]:
    return [dict(row) for row in rows]


# --------------------------------------------------
# Compute total income, expenses, net balance
# --------------------------------------------------
def compute_totals(convert_func) -> Dict[str, float]:
    """
    convert_func(amount, currency) must convert to base currency.

    Returns:
    {
        "income": float,
        "expense": float,
        "net": float
    }
    """
    rows = _rows_to_dicts(get_all_transactions())

    total_income = 0.0
    total_expense = 0.0

    for row in rows:
        converted = convert_func(row["amount"], row["currency"])

        if row["t_type"] == "Income":
            total_income += converted
        else:
            total_expense += converted

    return {
        "income": round(total_income, 2),
        "expense": round(total_expense, 2),
        "net": round(total_income - total_expense, 2)
    }


# --------------------------------------------------
# Breakdown by category
# --------------------------------------------------
def category_breakdown(convert_func) -> Dict[str, float]:
    """
    Returns: {"Food": 150.0, "Salary": 1000.0, ...}
    """
    rows = _rows_to_dicts(get_all_transactions())

    breakdown = {}

    for row in rows:
        converted = convert_func(row["amount"], row["currency"])
        cat = row["category"]

        if cat not in breakdown:
            breakdown[cat] = 0.0

        # Expenses positive, income positive — all mixed for summary
        breakdown[cat] += converted

    return {cat: round(val, 2) for cat, val in breakdown.items()}


# --------------------------------------------------
# Monthly stats (grouping algorithm)
# --------------------------------------------------
def monthly_summary(convert_func) -> Dict[str, Dict[str, float]]:
    """
    Returns a structure like:
    {
        "2025-01": {"income": 1500, "expense": 300},
        "2025-02": {"income": 1400, "expense": 400},
    }
    """
    rows = _rows_to_dicts(get_all_transactions())
    summary = {}

    for row in rows:
        month_key = row["date"][:7]  # "YYYY-MM"
        converted = convert_func(row["amount"], row["currency"])

        if month_key not in summary:
            summary[month_key] = {"income": 0.0, "expense": 0.0}

        if row["t_type"] == "Income":
            summary[month_key]["income"] += converted
        else:
            summary[month_key]["expense"] += converted

    # Round values
    for key in summary:
        summary[key]["income"] = round(summary[key]["income"], 2)
        summary[key]["expense"] = round(summary[key]["expense"], 2)

    return summary


# --------------------------------------------------
# Basic forecast (simple moving average)
# --------------------------------------------------
def forecast_next_month(convert_func, months: int = 3) -> float:
    """
    Predicts next month's net balance using the average
    of the last N months.
    """
    monthly = monthly_summary(convert_func)

    if len(monthly) == 0:
        return 0.0

    # Sort months chronologically
    sorted_keys = sorted(monthly.keys())

    # Take last N months
    recent = sorted_keys[-months:]

    nets = []
    for m in recent:
        nets.append(monthly[m]["income"] - monthly[m]["expense"])

    if len(nets) == 0:
        return 0.0

    return round(sum(nets) / len(nets), 2)

