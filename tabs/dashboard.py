# dashboard.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from core.analytics import (
    compute_totals,
    monthly_summary,
    category_breakdown,
    forecast_next_month
)

def render(convert_to_base, base_currency, current_user):

    st.header("Financial Dashboard")

    user_id = current_user["id"]

    # All analytics now scoped by user
    totals = compute_totals(convert_to_base, user_id=user_id)

    col1, col2, col3 = st.columns(3)
    col1.metric(f"Total Income ({base_currency})", totals["income"])
    col2.metric(f"Total Expenses ({base_currency})", totals["expense"])
    col3.metric(f"Net Balance ({base_currency})", totals["net"])

    st.markdown("---")

    # -----------------------------------------
    # Monthly Summary
    # -----------------------------------------
    st.subheader("Monthly Income vs Expense")
    monthly = monthly_summary(convert_to_base, user_id=user_id)

    if monthly:
        months, incomes, expenses = [], [], []

        for m, vals in sorted(monthly.items()):
            formatted = datetime.strptime(m, "%Y-%m").strftime("%b %Y")
            months.append(formatted)
            incomes.append(vals["income"])
            expenses.append(vals["expense"])

        df = pd.DataFrame({
            "Month": months,
            "Income": incomes,
            "Expense": expenses
        })

        fig = px.bar(
            df,
            x="Month",
            y=["Income", "Expense"],
            barmode="group",
            title=f"Monthly Income vs Expense ({base_currency})",
            color_discrete_map={"Income": "green", "Expense": "red"},
            text_auto = ".2f"
        )

        fig.update_layout(
            yaxis_title=f"Amount ({base_currency})",
            bargap=0.25
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for monthly summary.")

    st.markdown("---")

    # -----------------------------------------
    # Category Breakdown
    # -----------------------------------------
    st.subheader("Spending by Category")
    breakdown = category_breakdown(convert_to_base, user_id=user_id)

    if breakdown:
        df = pd.DataFrame({
            "Category": list(breakdown.keys()),
            "Amount": [b["amount"] for b in breakdown.values()],
            "Type": [b["type"] for b in breakdown.values()]
        })

        colors = ["green" if t == "Income" else "red" for t in df["Type"]]

        fig2 = px.bar(
            df,
            x="Category",
            y="Amount",
            text="Amount",
            title=f"Category Breakdown ({base_currency})",
            text_auto=".2f"
        )

        fig2.update_traces(marker_color=colors)

        fig2.update_layout(
            yaxis_title=f"Amount ({base_currency})",
            bargap=0.25,
            showlegend = False
        )


        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Not enough data for category breakdown.")

    st.markdown("---")

    # -----------------------------------------
    # Net Balance Trend
    # -----------------------------------------
    st.subheader("Net Balance Over Time")

    if monthly:
        df_net = pd.DataFrame({
            "Month": months,
            "Net Balance": [i - e for i, e in zip(incomes, expenses)]
        })

        fig3 = px.line(
            df_net,
            x="Month",
            y="Net Balance",
            markers=True,
            title=f"Net Balance Trend ({base_currency})"
        )

        fig3.update_layout(
            yaxis_title=f"Net Balance ({base_currency})",
            bargap=0.25
        )

        # Add labels above points
        fig3.update_traces(
            text=df_net["Net Balance"].apply(lambda v: f"{v:.2f}"),
            textposition="top center",
            mode="lines+markers+text"
        )

        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Not enough data for trend chart.")

    st.markdown("---")

    # -----------------------------------------
    # Forecast
    # -----------------------------------------
    st.subheader("Next Month Forecast")

    forecast_value = forecast_next_month(convert_to_base, user_id=user_id)
    delta = forecast_value - totals["net"]

    st.metric(
        label="Forecasted Net Balance",
        value=f"{forecast_value:,.2f} {base_currency}",
        delta=f"{delta:,.2f} {base_currency}"
    )
