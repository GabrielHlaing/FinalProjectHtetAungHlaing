import streamlit as st
import plotly.express as px
import pandas as pd
from api.currency_api import convert_to_base, get_currency_list
from datetime import datetime
from core.models import Transaction, ValidationError
from core.analytics import compute_totals, monthly_summary, category_breakdown, forecast_next_month
from core.database import (
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

if "message" not in st.session_state:
    st.session_state["message"] = None

st.title("Money Tracker")

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

    # Monthly Summary
    st.subheader("Monthly Income vs Expense")
    monthly = monthly_summary(convert_to_base)

    if monthly:
        months, incomes, expenses = [], [], []
        for m, vals in sorted(monthly.items()):
            # m is "YYYY-MM" -> convert to "Jan 2025"
            formatted = datetime.strptime(m, "%Y-%m").strftime("%b %Y")
            months.append(formatted)

            incomes.append(vals["income"])
            expenses.append(vals["expense"])

        df_monthly = pd.DataFrame({
            "Month": months,
            "Income": incomes,
            "Expense": expenses
        })

        # Custom colors
        color_map = {
            "Income": "green",
            "Expense": "red"
        }

        fig2 = px.bar(
            df_monthly,
            x="Month",
            y=["Income", "Expense"],
            barmode="group",
            title="Monthly Income vs Expenses",
            color_discrete_map=color_map
        )

        fig2.update_layout(
            yaxis_title=f"Amount ({base_currency})",
            xaxis_title="Month",
            bargap=0.25
        )

        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("Not enough data for monthly summary.")

    st.markdown("---")

    # Category Breakdown
    st.subheader("Spending by Category")
    breakdown = category_breakdown(convert_to_base)

    if breakdown:
        categories = list(breakdown.keys())
        amounts = [info["amount"] for info in breakdown.values()]
        types = [info["type"] for info in breakdown.values()]

        # Build DataFrame correctly
        df_breakdown = pd.DataFrame({
            "Category": categories,
            "Amount": amounts,
            "Type": types
        })

        # Colors: green for income, red for expense
        colors = ["green" if t == "Income" else "red" for t in types]

        fig = px.bar(
            df_breakdown,
            x="Category",
            y="Amount",
            title=f"Category Breakdown (Converted to {base_currency})",
            text="Amount",
        )

        # Override bar colors manually
        fig.update_traces(marker_color=colors)

        fig.update_layout(
            yaxis_title=f"Amount ({base_currency})",
            xaxis_title="Category",
            bargap=0.25,
            showlegend=False  # hide the auto legend
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Not enough data for category chart.")

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
    delta = forecast_value - totals["net"]

    st.metric(
        label="Forecasted Net Balance",
        value=f"{forecast_value:,.2f} {base_currency}",
        delta=f"{delta:,.2f} {base_currency}"
    )

# -----------------------------------------------------
# TAB 2: TRANSACTIONS CRUD
# -----------------------------------------------------
with tab2:
    st.header("Manage Transactions")

    # Show persisted messages
    if st.session_state["message"]:
        msg_type, msg_text = st.session_state["message"]
        if msg_type == "success":
            st.success(msg_text)
        elif msg_type == "error":
            st.error(msg_text)
        st.session_state["message"] = None

    # Transaction pages as sub-tabs
    tabA, tabB, tabC = st.tabs(["Add Transaction", "View Transactions", "Edit/Delete"])

    # ---------------------------------------------------------
    # PAGE 1: ADD TRANSACTION
    # ---------------------------------------------------------
    with tabA:

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
                    st.session_state["message"] = ("success", "Transaction added successfully.")
                except ValidationError as e:
                    st.session_state["message"] = ("error", str(e))
                st.rerun()

    # ---------------------------------------------------------
    # PAGE 2: VIEW TRANSACTIONS
    # ---------------------------------------------------------
    with tabB:

        rows = get_all_transactions()

        if not rows:
            st.info("No transactions yet.")
        else:
            df = pd.DataFrame(rows)
            df.columns = ["ID", "Type", "Amount", "Currency", "Category", "Date"]
            st.dataframe(df, hide_index=True)

    # ---------------------------------------------------------
    # PAGE 3: EDIT / DELETE
    # ---------------------------------------------------------
    with tabC:

        rows = get_all_transactions()

        if not rows:
            st.info("No transactions to modify.")
        else:
            row_ids = [row["id"] for row in rows]
            selected_id = st.selectbox("Select a transaction ID", row_ids)

            selected_row = next(r for r in rows if r["id"] == selected_id)

            # Edit Form
            st.markdown("#### Edit Transaction")
            st.caption("Modify the fields below and save changes.")

            with st.form("edit_form"):
                new_type = st.selectbox(
                    "Type",
                    ["Income", "Expense"],
                    index=["Income", "Expense"].index(selected_row["t_type"])
                )
                new_amount = st.number_input(
                    "Amount", min_value=0.0, step=0.5, value=float(selected_row["amount"])
                )
                new_currency = st.selectbox(
                    "Currency", CURRENCIES, index=CURRENCIES.index(selected_row["currency"])
                )
                new_category = st.text_input("Category", selected_row["category"])
                new_date = st.date_input(
                    "Date", datetime.strptime(selected_row["date"], "%Y-%m-%d")
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
                            st.session_state["message"] = ("success", "Transaction updated.")
                        else:
                            st.session_state["message"] = ("error", "Update failed.")
                    except ValidationError as e:
                        st.session_state["message"] = ("error", str(e))
                    st.rerun()

            st.divider()  # break

            # Delete Section
            st.markdown("#### Delete Transaction")
            st.caption("This action cannot be undone.")

            if st.button("Delete Selected Transaction"):
                if delete_transaction(selected_id):
                    st.session_state["message"] = ("success", "Transaction deleted.")
                else:
                    st.session_state["message"] = ("error", "Delete failed.")
                st.rerun()

    st.markdown("---")


# -----------------------------------------------------
# TAB 3: SETTINGS
# -----------------------------------------------------
with tab3:
    st.header("Settings")

    # ------------------------------
    # Base Currency
    # ------------------------------
    st.subheader("Base Currency")

    st.caption(f"Current base currency: **{base_currency}**")

    new_base = st.selectbox(
        "Select Base Currency",
        CURRENCIES,
        index=CURRENCIES.index(base_currency)
    )

    if st.button("Save Settings"):
        set_setting("base_currency", new_base)
        st.rerun()

    st.markdown("---")

    # ------------------------------
    # Live Exchange Rate Viewer
    # ------------------------------
    st.subheader("Live Exchange Rate")

    from api.currency_api import get_rate


    compare_currency = st.selectbox("Compare Against", CURRENCIES)


    if compare_currency == base_currency:
        st.info("Select a different currency to view the rate.")
    else:
        rate = get_rate(base_currency, compare_currency)

        # Display in card style
        st.markdown(
            f"""
            <div style="
                padding:10px;
                border-radius:8px;
                background-color:#F5F5F5;
                color:#000;
                text-align:center;
            ">
                <h3>1 {compare_currency} = {rate:.4f} {base_currency}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ------------------------------
    # About Section
    # ------------------------------
    st.subheader("About Base Currency")
    st.info(
        "All income and expenses are automatically converted to the base currency. "
        "Live exchange rates are fetched from the backend API. "
    )

