import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
from core.analytics import (
    compute_totals,
    monthly_summary,
    category_breakdown,
    forecast_next_month
)

def render(convert_to_base, base_currency):

    st.header("Financial Dashboard")

    totals = compute_totals(convert_to_base)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", totals["income"])
    col2.metric("Total Expenses", totals["expense"])
    col3.metric("Net Balance", totals["net"])

    st.markdown("---")

    # -----------------------------------------
    # Monthly Summary
    # -----------------------------------------
    st.subheader("Monthly Income vs Expense")
    monthly = monthly_summary(convert_to_base)

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
            title="Monthly Income vs Expense",
            color_discrete_map={"Income": "green", "Expense": "red"}
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
    breakdown = category_breakdown(convert_to_base)

    if breakdown:
        df = pd.DataFrame({
            "Category": list(breakdown.keys()),
            "Amount": [b["amount"] for b in breakdown.values()],
            "Type": [b["type"] for b in breakdown.values()]
        })

        colors = ["green" if t == "Income" else "red" for t in df["Type"]]

        fig = px.bar(
            df,
            x="Category",
            y="Amount",
            text="Amount",
            title=f"Category Breakdown ({base_currency})",
        )

        fig.update_traces(marker_color=colors)
        fig.update_layout(showlegend=False)

        st.plotly_chart(fig, use_container_width=True)

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
            df_net, x="Month", y="Net Balance", markers=True,
            title="Net Balance Trend"
        )

        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Not enough data for trend chart.")

    st.markdown("---")

    # -----------------------------------------
    # Forecast
    # -----------------------------------------
    st.subheader("Next Month Forecast")
    forecast_value = forecast_next_month(convert_to_base)
    delta = forecast_value - totals["net"]

    st.metric(
        label="Forecasted Net Balance",
        value=f"{forecast_value:,.2f} {base_currency}",
        delta=f"{delta:,.2f} {base_currency}"
    )
