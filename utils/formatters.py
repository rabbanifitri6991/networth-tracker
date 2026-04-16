"""
utils/formatters.py
Number and date formatting helpers.
"""

from datetime import datetime
import calendar

CURRENCY_SYMBOLS: dict[str, str] = {
    "RM":  "RM",
    "USD": "$",
    "JPY": "¥",
    "SGD": "S$",
}


def format_currency(amount: float, currency: str = "RM", decimals: int = 2) -> str:
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    formatted = f"{abs(amount):,.{decimals}f}"
    sign = "-" if amount < 0 else ""
    return f"{sign}{symbol} {formatted}"


def format_change(amount: float, currency: str = "RM") -> str:
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    sign = "+" if amount >= 0 else "-"
    return f"{sign}{symbol} {abs(amount):,.2f}"


def format_percent(value: float, decimals: int = 1) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value * 100:.{decimals}f}%"


def month_label(month: int, year: int) -> str:
    return f"{calendar.month_abbr[month]}-{year}"


def month_name(month: int) -> str:
    return calendar.month_name[month]


def get_month_year_options(n_months: int = 24) -> list[tuple[int, int]]:
    now = datetime.now()
    options = []
    m, y = now.month, now.year
    for _ in range(n_months):
        options.append((m, y))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return options
