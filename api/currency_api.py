# currency_api.py

import requests
from api.api_key import EXCHANGE_API_KEY
from core.database import get_setting

# -------------------------------
# In-memory live rate storage
# -------------------------------
LATEST_RATES = {}     # { ("USD", "MMK"): 2100.54 }
CURRENCY_LIST = ["USD", "MMK", "EUR", "JPY", "SGD", "THB", "CNY"]

# Placeholder fallback if API fails
PLACEHOLDER_RATE = 2000.0


def get_currency_list():
    """Return the loaded currency list."""
    return CURRENCY_LIST


# ---------------------------------------------------------
# Fetch a rate using /convert
# ---------------------------------------------------------
def fetch_rate_from_api(base: str, quote: str):
    """
    Fetch live exchange rate using /convert endpoint.
    Converts 1 QUOTE -> BASE.
    """

    if EXCHANGE_API_KEY:
        url = (
            f"https://api.exchangerate.host/convert"
            f"?from={quote}&to={base}&amount=1"
            f"&access_key={EXCHANGE_API_KEY}"
        )
    else:
        url = (
            f"https://api.exchangerate.host/convert"
            f"?from={quote}&to={base}&amount=1"
        )

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("success") and "result" in data:
            return float(data["result"])

    except Exception:
        pass

    return None


# ---------------------------------------------------------
# Unified rate loader (LIVE + in-memory storage)
# ---------------------------------------------------------
def get_rate(base: str, quote: str) -> float:
    """
    Return how much *1 unit of QUOTE* is worth in BASE.
    Example:
        get_rate("USD", "MMK") => 0.00048 (MMK → USD)
        get_rate("MMK", "USD") => 2100.5 (USD → MMK)
    """

    # same currency
    if base == quote:
        return 1.0

    key = (base, quote)

    # Return stored rate if we already fetched it
    if key in LATEST_RATES:
        return LATEST_RATES[key]

    # Fetch live rate
    live_rate = fetch_rate_from_api(base, quote)

    if live_rate is not None:
        LATEST_RATES[key] = live_rate
        return live_rate

    # Fallback
    if base == "USD" and quote == "MMK":
        return 1 / PLACEHOLDER_RATE

    if base == "MMK" and quote == "USD":
        return PLACEHOLDER_RATE

    return 1.0   # generic fallback


# ---------------------------------------------------------
# Convert any currency → base currency
# ---------------------------------------------------------
def convert_to_base(amount: float, from_currency: str) -> float:
    """
    Convert an amount FROM any currency TO the current base currency.
    """

    base = get_setting("base_currency")

    if from_currency == base:
        return amount

    rate = get_rate(base, from_currency)
    return round(amount * rate, 2)
