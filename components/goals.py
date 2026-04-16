"""
components/goals.py
Financial goals tracker.
"""

import streamlit as st

import database as db
from i18n import get_text
from utils.formatters import format_currency
from utils.currency import convert


def render(lang: str, currency: str) -> None:
    t = lambda key: get_text(key, lang)

    st.title(t("goals_title"))
    st.caption(t("goals_subtitle"))
    st.divider()

    # ---- Add New Goal ----------------------------------------------------
    with st.expander(f"➕ {t('add_goal')}", expanded=False):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        with col1:
            goal_name  = st.text_input(t("goal_name"), key="new_goal_name")
        with col2:
            target_amt = st.number_input(t("target_amount") + " (RM)",
                                         min_value=0.0, step=1000.0, key="new_goal_target")
        with col3:
            deadline   = st.date_input(t("deadline"), key="new_goal_deadline", value=None)
        with col4:
            st.markdown("&nbsp;", unsafe_allow_html=True)
            st.markdown("&nbsp;", unsafe_allow_html=True)
            if st.button(t("add"), key="btn_add_goal", use_container_width=True):
                if goal_name.strip() and target_amt > 0:
                    db.add_goal(goal_name.strip(), target_amt,
                                deadline.isoformat() if deadline else None)
                    st.success(t("goal_added"))
                    st.rerun()
                else:
                    st.warning("Please enter a goal name and target amount.")

    # ---- Goal Cards ------------------------------------------------------
    goals = db.get_goals()
    if not goals:
        st.info(t("no_goals"))
        return

    for g in goals:
        current  = float(g["current_amount"])
        target   = float(g["target_amount"])
        pct      = min(current / target, 1.0) if target > 0 else 0.0
        achieved = pct >= 1.0

        with st.container():
            col_info, col_actions = st.columns([5, 2])
            with col_info:
                emoji = "✅" if achieved else "🎯"
                deadline_str = f"  —  _{g['deadline']}_" if g.get("deadline") else ""
                st.markdown(f"**{emoji} {g['name']}**{deadline_str}")

                bar_color = "#00d4aa" if achieved else "#4e9af1"
                st.markdown(
                    f"""
                    <div style="margin:6px 0 2px 0;">
                        <div style="background:#2a2a2a;border-radius:8px;height:18px;overflow:hidden;">
                            <div style="width:{pct*100:.1f}%;background:{bar_color};height:100%;border-radius:8px;"></div>
                        </div>
                        <div style="display:flex;justify-content:space-between;font-size:.82rem;color:#aaa;margin-top:4px;">
                            <span>{format_currency(convert(current,"RM",currency), currency)}</span>
                            <span>{pct*100:.1f}%</span>
                            <span>{format_currency(convert(target,"RM",currency), currency)}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if achieved:
                    st.success(t("achieved"), icon="🎉")

            with col_actions:
                new_current = st.number_input(
                    t("current_amount") + " (RM)",
                    min_value=0.0, value=current, step=500.0,
                    key=f"goal_current_{g['id']}",
                )
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(t("save"), key=f"goal_save_{g['id']}", use_container_width=True):
                        db.update_goal_progress(g["id"], new_current)
                        st.success(t("goal_updated"))
                        st.rerun()
                with c2:
                    if st.button("🗑", key=f"goal_del_{g['id']}", use_container_width=True):
                        db.delete_goal(g["id"])
                        st.success(t("goal_deleted"))
                        st.rerun()

        st.divider()
