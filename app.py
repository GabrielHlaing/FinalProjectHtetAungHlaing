import streamlit as st
import plotly.express as px
import pandas as pd
from models import Transaction, ValidationError
from analytics import compute_totals, monthly_summary, category_breakdown, forecast_next_month
from currency_api import convert_to_base, get_currency_list
from datetime import datetime
from database import (
    init_db, add_transaction, get_all_transactions,
    delete_transaction, update_transaction,
    init_settings, get_setting, set_setting
)

# -----------------------------------------------------
# INITIALIZATION
# -----------------------------------------------------
st.set_page_config(page_title="Money Tracker", layout="wide")

init_db()
init_settings()

CURRENCIES = get_currency_list()
base_currency = get_setting("base_currency")


# -----------------------------------------------------
# Tabs
# -----------------------------------------------------
tab1, tab2, tab3 = st.tabs(["Dashboard", "Transactions", "Settings"])


# -----------------------------------------------------
# TAB 1: DASHBOARD
# -----------------------------------------------------
with tab1:
    st.header("Financial Dashboard")

    totals = compute_totals(convert_to_base)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Income", totals["income"])
    with col2:
        st.metric("Total Expenses", totals["expense"])
    with col3:
        st.metric("Net Balance", totals["net"])

    st.markdown("---")

    # Category Breakdown
    st.subheader("Spending by Category")
    breakdown = category_breakdown(convert_to_base)

    if breakdown:
        df_breakdown = pd.DataFrame({
            "Category": list(breakdown.keys()),
            "Amount": list(breakdown.values())
        })

        fig = px.bar(
            df_breakdown,
            x="Category",
            y="Amount",
            title=f"Category Breakdown (Converted to {base_currency})",
            text="Amount"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for category chart.")

    st.markdown("---")

    # Monthly Summary
    st.subheader("Monthly Income vs Expense")
    monthly = monthly_summary(convert_to_base)

    if monthly:
        months, incomes, expenses = [], [], []
        for m, vals in sorted(monthly.items()):
            months.append(m)
            incomes.append(vals["income"])
            expenses.append(vals["expense"])

        df_monthly = pd.DataFrame({
            "Month": months,
            "Income": incomes,
            "Expense": expenses
        })

        fig2 = px.bar(
            df_monthly,
            x="Month",
            y=["Income", "Expense"],
            barmode="group",
            title="Monthly Income vs Expenses"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Not enough data for monthly summary.")

    st.markdown("---")

    # Net Balance Trend
    st.subheader("Net Balance Over Time")

    if monthly:
        df_net = pd.DataFrame({
            "Month": months,
            "Net Balance": [inc - exp for inc, exp in zip(incomes, expenses)]
        })

        fig3 = px.line(
            df_net,
            x="Month",
            y="Net Balance",
            markers=True,
            title="Net Balance Trend"
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Not enough data for trend chart.")

    st.markdown("---")

    # Forecast
    st.subheader("Next Month Forecast")
    forecast_value = forecast_next_month(convert_to_base)
    st.metric("Forecasted Net Balance", forecast_value)


# -----------------------------------------------------
# TAB 2: TRANSACTIONS CRUD
# -----------------------------------------------------
with tab2:
    st.header("Add or Manage Transactions")

    # Add Transaction
    with st.expander("Add New Transaction"):
        with st.form("add_transaction_form"):
            t_type = st.selectbox("Type", ["Income", "Expense"])
            amount = st.number_input("Amount", min_value=0.0, step=0.5)
            currency = st.selectbox("Currency", CURRENCIES)
            category = st.text_input("Category")
            date = st.date_input("Date")

            submitted = st.form_submit_button("Add Transaction")

            if submitted:
                try:
                    tx = Transaction.create(
                        t_type=t_type,
                        amount=amount,
                        currency=currency,
                        category=category,
                        date_input=str(date)
                    )
                    add_transaction(tx)
                    st.success("Transaction added successfully.")
                    st.rerun()
                except ValidationError as e:
                    st.error(f"Error: {e}")

    # View Transactions
    with st.expander("View Transactions"):
        rows = get_all_transactions()

        if not rows:
            st.info("No transactions yet.")
        else:
            df_display = pd.DataFrame(rows)
            df_display.columns = ["ID", "Type", "Amount", "Currency", "Category", "Date"]
            st.dataframe(df_display, hide_index=True)

    # Edit / Delete
    with st.expander("Edit or Delete Transactions"):
        rows = get_all_transactions()

        if not rows:
            st.info("No transactions to modify.")
        else:
            row_ids = [row["id"] for row in rows]
            selected_id = st.selectbox("Select a transaction ID:", row_ids)
            selected_row = next(r for r in rows if r["id"] == selected_id)

            # Edit
            st.subheader("Edit Transaction")

            with st.form("edit_form"):
                new_type = st.selectbox(
                    "Type",
                    ["Income", "Expense"],
                    index=["Income", "Expense"].index(selected_row["t_type"])
                )

                new_amount = st.number_input(
                    "Amount",
                    min_value=0.0,
                    step=0.5,
                    value=float(selected_row["amount"])
                )

                new_currency = st.selectbox(
                    "Currency",
                    CURRENCIES,
                    index=CURRENCIES.index(selected_row["currency"])
                )

                new_category = st.text_input("Category", selected_row["category"])

                new_date = st.date_input(
                    "Date",
                    datetime.strptime(selected_row["date"], "%Y-%m-%d")
                )

                edit_submitted = st.form_submit_button("Save Changes")

                if edit_submitted:
                    try:
                        tx_updated = Transaction.create(
                            t_type=new_type,
                            amount=new_amount,
                            currency=new_currency,
                            category=new_category,
                            date_input=str(new_date)
                        )
                        ok = update_transaction(selected_id, tx_updated)

                        if ok:
                            st.success("Transaction updated.")
                            st.rerun()
                        else:
                            st.error("Update failed.")

                    except ValidationError as e:
                        st.error(f"Error: {e}")

            # Delete
            st.subheader("Delete Transaction")
            if st.button("Delete Selected Transaction"):
                if delete_transaction(selected_id):
                    st.success("Transaction deleted.")
                    st.rerun()
                else:
                    st.error("Delete failed.")


# -----------------------------------------------------
# TAB 3: SETTINGS
# -----------------------------------------------------
with tab3:
    st.header("Settings")

    # Base Currency
    st.subheader("Base Currency")

    new_base = st.selectbox(
        "Select Base Currency",
        CURRENCIES,
        index=CURRENCIES.index(base_currency)
    )

    if st.button("Save Settings"):
        set_setting("base_currency", new_base)
        st.rerun()

    st.markdown("---")

    # Live Rate Viewer
    st.subheader("Live Exchange Rate")

    from currency_api import get_rate

    compare_currency = st.selectbox("Compare Against", CURRENCIES)

    if compare_currency == base_currency:
        st.info("Select a different currency.")
    else:
        rate = get_rate(base_currency, compare_currency)
        st.metric(
            label=f"1 {compare_currency} equals",
            value=f"{rate:.4f} {base_currency}"
        )

    st.markdown("---")

    st.subheader("About Base Currency")
    st.info("""
    All income and expenses are converted to the base currency.
    Conversion uses the latest live exchange rates from the backend API.
    """)
