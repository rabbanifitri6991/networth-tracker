"""
components/dashboard.py
Main dashboard — live net worth widget + summary cards + mini chart.
"""

from datetime import datetime
import streamlit as st
import plotly.graph_objects as go

import database as db
from i18n import get_text
from utils.formatters import format_currency, format_change, format_percent, month_label
from utils.currency import convert


def _get_totals(month: int, year: int) -> tuple[float, float]:
    assets      = db.get_assets()
    asset_vals  = db.get_asset_values_for_month(month, year)
    total_a     = sum(asset_vals.get(a["id"], 0.0) for a in assets)

    liabilities = db.get_liabilities()
    liab_vals   = db.get_liability_values_for_month(month, year)
    total_l     = sum(liab_vals.get(l["id"], 0.0) for l in liabilities)

    return total_a, total_l


def _prev_month(month: int, year: int) -> tuple[int, int]:
    if month == 1:
        return 12, year - 1
    return month - 1, year


def render(lang: str, currency: str) -> None:
    t = lambda key: get_text(key, lang)

    now = datetime.now()
    month, year = now.month, now.year

    st.title(t("dashboard_title"))
    st.caption(t("dashboard_subtitle"))
    st.divider()

    total_assets, total_liabilities = _get_totals(month, year)
    networth = total_assets - total_liabilities

    prev_m, prev_y = _prev_month(month, year)
    prev_assets, prev_liabilities = _get_totals(prev_m, prev_y)
    prev_networth = prev_assets - prev_liabilities
    change    = networth - prev_networth
    pct_change = (change / prev_networth) if prev_networth != 0 else 0.0

    # ---- Live Net Worth Widget --------------------------------------------
    st.markdown("### 💰 " + t("live_networth"))
    widget_col, _ = st.columns([2, 3])
    with widget_col:
        nw_display = convert(networth, "RM", currency)
        st.markdown(
            f"""
            <div style="
                background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);
                border-radius:16px; padding:28px 32px;
                border:1px solid #0f3460; text-align:center;">
                <div style="color:#00d4aa;font-size:2.6rem;font-weight:700;">
                    {format_currency(nw_display, currency)}
                </div>
                <div style="color:#{'00d4aa' if change >= 0 else 'ff6b6b'};font-size:1rem;margin-top:6px;">
                    {"▲" if change >= 0 else "▼"} {format_change(convert(change,"RM",currency), currency)} ({format_percent(pct_change)})
                </div>
                <div style="color:#888;font-size:0.85rem;margin-top:4px;">
                    {t("as_of")} {month_label(month, year)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("&nbsp;", unsafe_allow_html=True)

    # ---- Summary Cards ----------------------------------------------------
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"📈 {t('total_assets')}",
                  format_currency(convert(total_assets, "RM", currency), currency))
    with col2:
        st.metric(f"📉 {t('total_liabilities')}",
                  format_currency(convert(total_liabilities, "RM", currency), currency))
    with col3:
        st.metric(f"📊 {t('monthly_change')}",
                  format_currency(convert(networth, "RM", currency), currency),
                  delta=format_change(convert(change, "RM", currency), currency))

    st.divider()

    # ---- Mini Chart -------------------------------------------------------
    history = db.get_networth_history()
    if len(history) >= 2:
        recent = history[-6:]
        labels  = [month_label(r["month"], r["year"]) for r in recent]
        nw_vals = [convert(r["networth"], "RM", currency) for r in recent]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=labels, y=nw_vals,
            mode="lines+markers",
            line=dict(color="#00d4aa", width=3),
            marker=dict(size=8, color="#00d4aa"),
            fill="tozeroy", fillcolor="rgba(0,212,170,0.1)",
        ))
        fig.update_layout(
            title=t("networth_chart"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ccc"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#333"),
            height=300, margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(t("no_history"))
