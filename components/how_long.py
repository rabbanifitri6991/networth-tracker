"""
components/how_long.py
"How Long Will Money Last?" calculator.
"""

import math
import streamlit as st
import plotly.graph_objects as go

from i18n import get_text
from utils.formatters import format_currency
from utils.currency import convert


def _months_to_depletion(principal: float, monthly_expense: float,
                          annual_return_pct: float) -> float | None:
    if monthly_expense <= 0:
        return None
    r = annual_return_pct / 100 / 12
    if r == 0:
        return principal / monthly_expense
    if r * principal >= monthly_expense:
        return None
    ratio = (r * principal) / monthly_expense
    if ratio >= 1:
        return None
    return -math.log(1 - ratio) / math.log(1 + r)


def render(lang: str, currency: str) -> None:
    t = lambda key: get_text(key, lang)

    st.title(t("how_long_title"))
    st.caption(t("how_long_subtitle"))
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        savings_rm = st.number_input(t("savings_to_use") + " (RM)",
                                     min_value=0.0, value=100_000.0, step=1_000.0)
    with col2:
        expense_rm = st.number_input(t("monthly_expense") + " (RM)",
                                     min_value=0.0, value=3_000.0, step=100.0)
    with col3:
        annual_return = st.number_input(t("expected_return"),
                                        min_value=0.0, max_value=50.0, value=4.0, step=0.5)

    if st.button(t("calculate"), type="primary"):
        n = _months_to_depletion(savings_rm, expense_rm, annual_return)

        if n is None:
            st.success(t("result_forever"))
        else:
            years  = int(n // 12)
            months = int(n % 12)
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("⏳ Duration",
                          f"{years} {t('result_years')} {months} {t('result_months')}")
            with c2:
                st.metric("📅 Total Months", f"~{int(n)} months")

            # Runway chart
            st.markdown("#### Savings Runway")
            balance  = savings_rm
            monthly_r = annual_return / 100 / 12
            balances = [balance]
            for _ in range(min(int(n) + 2, 600)):
                balance = balance * (1 + monthly_r) - expense_rm
                if balance < 0:
                    balances.append(0)
                    break
                balances.append(balance)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(len(balances))),
                y=[convert(b, "RM", currency) for b in balances],
                mode="lines", line=dict(color="#4e9af1", width=2),
                fill="tozeroy", fillcolor="rgba(78,154,241,0.1)",
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ccc"),
                xaxis=dict(title="Months", showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#2a2a2a"),
                height=320, margin=dict(l=0, r=0, t=20, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)
