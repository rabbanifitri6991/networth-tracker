"""
components/networth.py
Net worth history charts and breakdown.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

import database as db
from i18n import get_text
from utils.formatters import format_currency, month_label
from utils.currency import convert


def render(lang: str, currency: str) -> None:
    t = lambda key: get_text(key, lang)

    st.title(t("networth_title"))
    st.caption(t("networth_subtitle"))
    st.divider()

    history = db.get_networth_history()
    if not history:
        st.info(t("no_history"))
        return

    labels     = [month_label(r["month"], r["year"]) for r in history]
    nw_vals    = [convert(r["networth"],    "RM", currency) for r in history]
    asset_vals = [convert(r["assets"],      "RM", currency) for r in history]
    liab_vals  = [convert(r["liabilities"], "RM", currency) for r in history]

    # ---- Net Worth Line Chart -------------------------------------------
    st.markdown(f"### 📈 {t('networth_chart')}")
    fig_nw = go.Figure()
    fig_nw.add_trace(go.Scatter(
        x=labels, y=nw_vals, mode="lines+markers",
        line=dict(color="#00d4aa", width=3), marker=dict(size=8),
        fill="tozeroy", fillcolor="rgba(0,212,170,0.08)",
    ))
    fig_nw.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ccc"), xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#2a2a2a"),
        height=360, margin=dict(l=0, r=0, t=20, b=0), hovermode="x unified",
    )
    st.plotly_chart(fig_nw, use_container_width=True)

    # ---- Assets vs Liabilities Bar Chart --------------------------------
    st.markdown(f"### ⚖️ {t('assets_vs_liabilities')}")
    fig_av = go.Figure()
    fig_av.add_trace(go.Bar(x=labels, y=asset_vals,
                            name=t("total_assets"), marker_color="#4e9af1"))
    fig_av.add_trace(go.Bar(x=labels, y=liab_vals,
                            name=t("total_liabilities"), marker_color="#ff6b6b"))
    fig_av.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ccc"), xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#2a2a2a"),
        height=360, margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_av, use_container_width=True)

    # ---- Category Donut (latest month) ----------------------------------
    st.markdown(f"### 🥧 {t('breakdown_by_category')}")
    latest    = history[-1]
    assets    = db.get_assets()
    av_latest = db.get_asset_values_for_month(latest["month"], latest["year"])
    cat_totals: dict[str, float] = {}
    for a in assets:
        cat_totals[a["category"]] = cat_totals.get(a["category"], 0.0) + av_latest.get(a["id"], 0.0)

    if any(v > 0 for v in cat_totals.values()):
        fig_pie = px.pie(
            names=list(cat_totals.keys()),
            values=[convert(v, "RM", currency) for v in cat_totals.values()],
            hole=0.45, color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#ccc"),
            margin=dict(l=0, r=0, t=20, b=0), height=360,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ---- History Table --------------------------------------------------
    st.markdown("### 📋 History Table")
    df = pd.DataFrame({
        "Period":               labels,
        t("total_assets"):      [format_currency(v, currency) for v in asset_vals],
        t("total_liabilities"): [format_currency(v, currency) for v in liab_vals],
        t("nav_networth"):      [format_currency(v, currency) for v in nw_vals],
    })
    st.dataframe(df, use_container_width=True, hide_index=True)
