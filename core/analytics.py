# analytics.py

from typing import Dict, List
from core.database import get_transactions_for_user


# --------------------------------------------------
# Helper: Convert SQLite rows into Python dictionaries
# --------------------------------------------------
def _rows_to_dicts(rows) -> List[dict]:
    return [dict(row) for row in rows]


# --------------------------------------------------
# Compute total income, expenses, net balance
# --------------------------------------------------
def compute_totals(convert_func, user_id: int) -> Dict[str, float]:
    """
    convert_func(amount, currency) must convert to base currency.

    Returns totals for ONLY this user.
    """
    rows = _rows_to_dicts(get_transactions_for_user(user_id))

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
def category_breakdown(convert_func, user_id: int):
    """
    Returns breakdown for categories for this user only.
    {
        "Food": {"amount": 150.0, "type": "Expense"},
        "Salary": {"amount": 1000.0, "type": "Income"},
    }
    """
    rows = _rows_to_dicts(get_transactions_for_user(user_id))

    breakdown = {}

    for row in rows:
        converted = convert_func(row["amount"], row["currency"])
        cat = row["category"]
        t_type = row["t_type"]

        if cat not in breakdown:
            breakdown[cat] = {"amount": 0.0, "type": t_type}

        breakdown[cat]["amount"] += converted

    # Round results
    for cat in breakdown:
        breakdown[cat]["amount"] = round(breakdown[cat]["amount"], 2)

    return breakdown


# --------------------------------------------------
# Monthly stats (grouping algorithm)
# --------------------------------------------------
def monthly_summary(convert_func, user_id: int) -> Dict[str, Dict[str, float]]:
    """
    Returns month → income/expense for this user:
    {
        "2025-01": {"income": 1500, "expense": 300},
        "2025-02": {"income": 1400, "expense": 400},
    }
    """
    rows = _rows_to_dicts(get_transactions_for_user(user_id))
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

    # Round
    for m in summary:
        summary[m]["income"] = round(summary[m]["income"], 2)
        summary[m]["expense"] = round(summary[m]["expense"], 2)

    return summary


# --------------------------------------------------
# Forecast (simple average of last N months)
# --------------------------------------------------
def forecast_next_month(convert_func, user_id: int, months: int = 3) -> float:
    """
    Predicts next month's net balance using average
    of last N months for THIS user only.
    """
    monthly = monthly_summary(convert_func, user_id)

    if len(monthly) == 0:
        return 0.0

    sorted_keys = sorted(monthly.keys())
    recent = sorted_keys[-months:]

    nets = [
        monthly[m]["income"] - monthly[m]["expense"]
        for m in recent
    ]

    if not nets:
        return 0.0

    return round(sum(nets) / len(nets), 2)
