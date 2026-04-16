"""
components/liabilities.py
Liabilities management page.
"""

from datetime import datetime
import streamlit as st
import pandas as pd

import database as db
from i18n import get_text
from utils.formatters import format_currency, month_label, get_month_year_options
from utils.currency import convert


def render(lang: str, currency: str) -> None:
    t = lambda key: get_text(key, lang)

    st.title(t("liabilities_title"))
    st.caption(t("liabilities_subtitle"))
    st.divider()

    # ---- Add New Liability -----------------------------------------------
    with st.expander(f"➕ {t('add_liability')}", expanded=False):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            new_name = st.text_input(t("liability_name"), key="new_liab_name")
        with col2:
            new_cat = st.selectbox(t("liability_category"),
                                   options=db.LIABILITY_CATEGORIES, key="new_liab_cat")
        with col3:
            st.markdown("&nbsp;", unsafe_allow_html=True)
            st.markdown("&nbsp;", unsafe_allow_html=True)
            if st.button(t("add"), key="btn_add_liab", use_container_width=True):
                if new_name.strip():
                    db.add_liability(new_name.strip(), new_cat)
                    st.success(t("liability_added"))
                    st.rerun()
                else:
                    st.warning("Please enter a liability name.")

    # ---- Monthly Update --------------------------------------------------
    st.markdown(f"### 📅 {t('monthly_update')}")
    st.caption(t("monthly_update_subtitle"))

    month_options = get_month_year_options(24)
    month_labels  = [month_label(m, y) for m, y in month_options]
    now = datetime.now()
    default_idx = next(
        (i for i, (m, y) in enumerate(month_options) if m == now.month and y == now.year), 0
    )

    col_sel, _ = st.columns([2, 5])
    with col_sel:
        selected_label = st.selectbox(t("month"), options=month_labels,
                                      index=default_idx, key="liab_month_sel")

    sel_idx = month_labels.index(selected_label)
    sel_month, sel_year = month_options[sel_idx]

    liabilities = db.get_liabilities()
    if not liabilities:
        st.info(t("no_liabilities"))
        return

    existing_vals = db.get_liability_values_for_month(sel_month, sel_year)
    prev_m = sel_month - 1 if sel_month > 1 else 12
    prev_y = sel_year if sel_month > 1 else sel_year - 1
    prev_vals = db.get_liability_values_for_month(prev_m, prev_y)

    rows = []
    for l in liabilities:
        prev_val = prev_vals.get(l["id"], 0.0)
        curr_val = existing_vals.get(l["id"], prev_val)
        rows.append({
            "ID": l["id"],
            t("name"):     l["name"],
            t("category"): l["category"],
            month_label(prev_m, prev_y):        prev_val,
            month_label(sel_month, sel_year):   curr_val,
        })

    df       = pd.DataFrame(rows)
    prev_col = month_label(prev_m, prev_y)
    curr_col = month_label(sel_month, sel_year)

    edited = st.data_editor(
        df.drop(columns=["ID"]),
        column_config={
            "ID": None,
            prev_col: st.column_config.NumberColumn(prev_col, disabled=True, format="%.2f"),
            curr_col: st.column_config.NumberColumn(curr_col, min_value=0.0, format="%.2f"),
        },
        use_container_width=True, hide_index=True, key="liab_editor",
    )

    col_save, col_total = st.columns([1, 3])
    with col_save:
        if st.button(f"💾 {t('save')}", key="btn_save_liab", use_container_width=True):
            for i, l in enumerate(liabilities):
                db.upsert_liability_value(l["id"], sel_month, sel_year,
                                          float(edited.iloc[i][curr_col]))
            st.success(t("liability_saved"))
            st.rerun()
    with col_total:
        total = convert(edited[curr_col].sum(), "RM", currency)
        st.markdown(f"**Total Liabilities ({selected_label}):** {format_currency(total, currency)}")

    st.divider()

    # ---- Manage Liabilities (delete) ------------------------------------
    st.markdown(f"### 🗂 {t('liabilities_title')}")
    categories = list(dict.fromkeys(l["category"] for l in liabilities))
    for cat in categories:
        cat_items = [l for l in liabilities if l["category"] == cat]
        with st.expander(f"**{cat}** ({len(cat_items)} items)", expanded=True):
            for l in cat_items:
                c1, c2 = st.columns([6, 1])
                with c1:
                    st.write(l["name"])
                with c2:
                    if st.button("🗑", key=f"del_liab_{l['id']}", help=t("delete")):
                        db.delete_liability(l["id"])
                        st.success(t("liability_deleted"))
                        st.rerun()
