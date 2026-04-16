"""
components/assets.py
Asset management page — add/delete assets and record monthly values.
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

    st.title(t("assets_title"))
    st.caption(t("assets_subtitle"))
    st.divider()

    # ---- Add New Asset ----------------------------------------------------
    with st.expander(f"➕ {t('add_asset')}", expanded=False):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            new_name = st.text_input(t("asset_name"), key="new_asset_name")
        with col2:
            new_cat = st.selectbox(t("asset_category"),
                                   options=db.ASSET_CATEGORIES, key="new_asset_cat")
        with col3:
            st.markdown("&nbsp;", unsafe_allow_html=True)
            st.markdown("&nbsp;", unsafe_allow_html=True)
            if st.button(t("add"), key="btn_add_asset", use_container_width=True):
                if new_name.strip():
                    db.add_asset(new_name.strip(), new_cat)
                    st.success(t("asset_added"))
                    st.rerun()
                else:
                    st.warning("Please enter an asset name.")

    # ---- Monthly Update Table --------------------------------------------
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
                                      index=default_idx, key="asset_month_sel")

    sel_idx = month_labels.index(selected_label)
    sel_month, sel_year = month_options[sel_idx]

    assets = db.get_assets()
    if not assets:
        st.info(t("no_assets"))
        return

    existing_vals = db.get_asset_values_for_month(sel_month, sel_year)
    prev_m = sel_month - 1 if sel_month > 1 else 12
    prev_y = sel_year if sel_month > 1 else sel_year - 1
    prev_vals = db.get_asset_values_for_month(prev_m, prev_y)

    rows = []
    for a in assets:
        prev_val = prev_vals.get(a["id"], 0.0)
        curr_val = existing_vals.get(a["id"], prev_val)
        rows.append({
            "ID": a["id"],
            t("name"):     a["name"],
            t("category"): a["category"],
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
        use_container_width=True, hide_index=True, key="asset_editor",
    )

    col_save, col_total = st.columns([1, 3])
    with col_save:
        if st.button(f"💾 {t('save')}", key="btn_save_assets", use_container_width=True):
            for i, a in enumerate(assets):
                db.upsert_asset_value(a["id"], sel_month, sel_year,
                                      float(edited.iloc[i][curr_col]))
            st.success(t("asset_saved"))
            st.rerun()
    with col_total:
        total = convert(edited[curr_col].sum(), "RM", currency)
        st.markdown(f"**Total Assets ({selected_label}):** {format_currency(total, currency)}")

    st.divider()

    # ---- Manage Assets (delete) ------------------------------------------
    st.markdown(f"### 🗂 {t('assets_title')}")
    categories = list(dict.fromkeys(a["category"] for a in assets))
    for cat in categories:
        cat_assets = [a for a in assets if a["category"] == cat]
        with st.expander(f"**{cat}** ({len(cat_assets)} items)", expanded=True):
            for a in cat_assets:
                c1, c2 = st.columns([6, 1])
                with c1:
                    st.write(a["name"])
                with c2:
                    if st.button("🗑", key=f"del_asset_{a['id']}", help=t("delete")):
                        db.delete_asset(a["id"])
                        st.success(t("asset_deleted"))
                        st.rerun()
