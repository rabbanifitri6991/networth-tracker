"""
utils/currency.py
Currency conversion utilities.
XE.com integration ready — see comments below to enable live rates.
"""

import os
from dotenv import load_dotenv

load_dotenv()

XE_ACCOUNT_ID = os.getenv("XE_ACCOUNT_ID", "")
XE_API_KEY    = os.getenv("XE_API_KEY", "")
XE_API_URL    = "https://xecdapi.xe.com/v1/convert_from.json"

SUPPORTED_CURRENCIES = ["RM", "USD", "JPY", "SGD"]

STATIC_RATES: dict[str, float] = {
    "RM":  1.0,
    "USD": 0.2232,
    "JPY": 33.80,
    "SGD": 0.2990,
}


def get_rate(from_currency: str = "RM", to_currency: str = "USD") -> float:
    if from_currency == to_currency:
        return 1.0
    # Uncomment to enable live XE.com rates:
    # if XE_ACCOUNT_ID and XE_API_KEY:
    #     try:
    #         import requests
    #         resp = requests.get(XE_API_URL,
    #             auth=(XE_ACCOUNT_ID, XE_API_KEY),
    #             params={"from": from_currency, "to": to_currency, "amount": 1},
    #             timeout=5)
    #         resp.raise_for_status()
    #         return resp.json()["to"][0]["mid"]
    #     except Exception:
    #         pass
    from_to_rm   = 1.0 / STATIC_RATES.get(from_currency, 1.0)
    rm_to_target = STATIC_RATES.get(to_currency, 1.0)
    return from_to_rm * rm_to_target


def convert(amount: float, from_currency: str = "RM", to_currency: str = "USD") -> float:
    return amount * get_rate(from_currency, to_currency)


def is_live_rates_enabled() -> bool:
    return bool(XE_ACCOUNT_ID and XE_API_KEY)
