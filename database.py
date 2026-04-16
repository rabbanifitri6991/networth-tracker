"""
database.py
All database operations — now powered by Supabase (PostgreSQL).
Uses Row Level Security so every query is automatically scoped
to the currently logged-in user.
"""

from typing import Optional
from supabase_client import get_authed_client

# ---------------------------------------------------------------------------
# Asset categories
# ---------------------------------------------------------------------------

ASSET_CATEGORIES = [
    "Cash & Savings",
    "Investments",
    "Crypto & Gold",
    "Property",
    "EPF / Retirement",
]

LIABILITY_CATEGORIES = [
    "Home Loan",
    "Car Loan",
    "Credit Card",
    "Student Loan (PTPTN)",
]


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------

def get_assets() -> list[dict]:
    client = get_authed_client()
    res = (
        client.table("assets")
        .select("*")
        .order("category")
        .order("name")
        .execute()
    )
    return res.data or []


def add_asset(name: str, category: str) -> str:
    """Returns the new asset's UUID."""
    import streamlit as st
    from supabase_client import get_current_user
    user = get_current_user()
    client = get_authed_client()
    res = client.table("assets").insert({
        "name":     name,
        "category": category,
        "user_id":  user["id"],
    }).execute()
    return res.data[0]["id"]


def delete_asset(asset_id: str) -> None:
    client = get_authed_client()
    client.table("assets").delete().eq("id", asset_id).execute()


def upsert_asset_value(asset_id: str, month: int, year: int, value: float) -> None:
    client = get_authed_client()
    client.table("asset_values").upsert(
        {"asset_id": asset_id, "month": month, "year": year, "value": value},
        on_conflict="asset_id,month,year",
    ).execute()


def get_asset_values_for_month(month: int, year: int) -> dict[str, float]:
    """Returns {asset_id: value} for the given month/year."""
    client = get_authed_client()
    res = (
        client.table("asset_values")
        .select("asset_id, value")
        .eq("month", month)
        .eq("year", year)
        .execute()
    )
    return {r["asset_id"]: float(r["value"]) for r in (res.data or [])}


def get_asset_history() -> list[dict]:
    client = get_authed_client()
    res = (
        client.table("asset_values")
        .select("year, month, value")
        .order("year")
        .order("month")
        .execute()
    )
    # Aggregate in Python
    totals: dict[tuple, float] = {}
    for r in (res.data or []):
        key = (r["year"], r["month"])
        totals[key] = totals.get(key, 0.0) + float(r["value"])
    return [
        {"year": y, "month": m, "total": v}
        for (y, m), v in sorted(totals.items())
    ]


# ---------------------------------------------------------------------------
# Liabilities
# ---------------------------------------------------------------------------

def get_liabilities() -> list[dict]:
    client = get_authed_client()
    res = (
        client.table("liabilities")
        .select("*")
        .order("category")
        .order("name")
        .execute()
    )
    return res.data or []


def add_liability(name: str, category: str) -> str:
    from supabase_client import get_current_user
    user = get_current_user()
    client = get_authed_client()
    res = client.table("liabilities").insert({
        "name":     name,
        "category": category,
        "user_id":  user["id"],
    }).execute()
    return res.data[0]["id"]


def delete_liability(liability_id: str) -> None:
    client = get_authed_client()
    client.table("liabilities").delete().eq("id", liability_id).execute()


def upsert_liability_value(
    liability_id: str, month: int, year: int, value: float
) -> None:
    client = get_authed_client()
    client.table("liability_values").upsert(
        {"liability_id": liability_id, "month": month, "year": year, "value": value},
        on_conflict="liability_id,month,year",
    ).execute()


def get_liability_values_for_month(month: int, year: int) -> dict[str, float]:
    client = get_authed_client()
    res = (
        client.table("liability_values")
        .select("liability_id, value")
        .eq("month", month)
        .eq("year", year)
        .execute()
    )
    return {r["liability_id"]: float(r["value"]) for r in (res.data or [])}


def get_liability_history() -> list[dict]:
    client = get_authed_client()
    res = (
        client.table("liability_values")
        .select("year, month, value")
        .order("year")
        .order("month")
        .execute()
    )
    totals: dict[tuple, float] = {}
    for r in (res.data or []):
        key = (r["year"], r["month"])
        totals[key] = totals.get(key, 0.0) + float(r["value"])
    return [
        {"year": y, "month": m, "total": v}
        for (y, m), v in sorted(totals.items())
    ]


# ---------------------------------------------------------------------------
# Net Worth History (computed in Python)
# ---------------------------------------------------------------------------

def get_networth_history() -> list[dict]:
    """
    Returns [{year, month, assets, liabilities, networth}]
    for every month that has at least one recorded value.
    """
    # Fetch all asset and liability values for this user
    client = get_authed_client()

    asset_res = (
        client.table("asset_values")
        .select("year, month, value")
        .execute()
    )
    liab_res = (
        client.table("liability_values")
        .select("year, month, value")
        .execute()
    )

    asset_by_month: dict[tuple, float] = {}
    for r in (asset_res.data or []):
        k = (r["year"], r["month"])
        asset_by_month[k] = asset_by_month.get(k, 0.0) + float(r["value"])

    liab_by_month: dict[tuple, float] = {}
    for r in (liab_res.data or []):
        k = (r["year"], r["month"])
        liab_by_month[k] = liab_by_month.get(k, 0.0) + float(r["value"])

    all_months = sorted(set(asset_by_month) | set(liab_by_month))

    result = []
    for (year, month) in all_months:
        a = asset_by_month.get((year, month), 0.0)
        l = liab_by_month.get((year, month), 0.0)
        result.append({
            "year":        year,
            "month":       month,
            "assets":      a,
            "liabilities": l,
            "networth":    a - l,
        })
    return result


# ---------------------------------------------------------------------------
# Goals
# ---------------------------------------------------------------------------

def get_goals() -> list[dict]:
    client = get_authed_client()
    res = (
        client.table("goals")
        .select("*")
        .order("created_at")
        .execute()
    )
    return res.data or []


def add_goal(name: str, target_amount: float, deadline: Optional[str] = None) -> str:
    from supabase_client import get_current_user
    user = get_current_user()
    client = get_authed_client()
    res = client.table("goals").insert({
        "name":          name,
        "target_amount": target_amount,
        "deadline":      deadline,
        "user_id":       user["id"],
    }).execute()
    return res.data[0]["id"]


def update_goal_progress(goal_id: str, current_amount: float) -> None:
    client = get_authed_client()
    client.table("goals").update(
        {"current_amount": current_amount}
    ).eq("id", goal_id).execute()


def delete_goal(goal_id: str) -> None:
    client = get_authed_client()
    client.table("goals").delete().eq("id", goal_id).execute()
