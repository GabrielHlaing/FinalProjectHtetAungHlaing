import streamlit as st
import pandas as pd
from datetime import datetime

from core.models import Transaction, ValidationError
from core.database import (
    add_transaction, get_all_transactions,
    delete_transaction, update_transaction
)

def render(multi_currencies):

    st.header("Manage Transactions")

    show_message()

    tabA, tabB, tabC = st.tabs([
        "Add Transaction", "View Transactions", "Edit/Delete"
    ])

    # ------------------------
    # Add Transaction
    # ------------------------
    with tabA:
        st.subheader("Add New Transaction")

        # form reset
        form_key = f"add_form_{st.session_state.get('form_reset', 0)}"

        with st.form(key=form_key):
            t_type = st.selectbox("Type", ["Income", "Expense"])
            amount = st.number_input("Amount", min_value=0.0, step=0.5)
            currency = st.selectbox("Currency", multi_currencies)
            category = st.text_input("Category")
            date = st.date_input("Date")

            submitted = st.form_submit_button("Add Transaction")

            if submitted:
                try:
                    tx = Transaction.create(
                        t_type=t_type, amount=amount, currency=currency,
                        category=category, date_input=str(date)
                    )
                    add_transaction(tx)
                    st.session_state["message"] = ("success", "Transaction added.")
                except ValidationError as e:
                    st.session_state["message"] = ("error", str(e))

                # trigger form reset
                st.session_state["form_reset"] = (
                    st.session_state.get("form_reset", 0) + 1
                )
                st.rerun()

    # ------------------------
    # View Transactions
    # ------------------------
    with tabB:
        st.subheader("All Transactions")

        rows = get_all_transactions()
        if not rows:
            st.info("No transactions yet.")
        else:
            df = pd.DataFrame(rows)
            df.columns = ["ID", "Type", "Amount", "Currency", "Category", "Date"]
            st.dataframe(df, hide_index=True)

    # ------------------------
    # Edit / Delete
    # ------------------------
    with tabC:
        st.subheader("Edit or Delete Transactions")

        rows = get_all_transactions()
        if not rows:
            st.info("No transactions to modify.")
            return

        row_ids = [r["id"] for r in rows]
        selected_id = st.selectbox("Transaction ID", row_ids)
        selected = next(r for r in rows if r["id"] == selected_id)

        # ----- Edit -----
        st.write("### Edit Transaction")

        with st.form(key="edit_form"):
            new_type = st.selectbox(
                "Type", ["Income", "Expense"],
                index=["Income", "Expense"].index(selected["t_type"])
            )
            new_amount = st.number_input(
                "Amount", min_value=0.0, step=0.5, value=float(selected["amount"])
            )
            new_currency = st.selectbox(
                "Currency", multi_currencies,
                index=multi_currencies.index(selected["currency"])
            )
            new_category = st.text_input("Category", selected["category"])
            new_date = st.date_input(
                "Date", datetime.strptime(selected["date"], "%Y-%m-%d")
            )

            edit_ok = st.form_submit_button("Save Changes")

            if edit_ok:
                try:
                    updated = Transaction.create(
                        t_type=new_type, amount=new_amount,
                        currency=new_currency, category=new_category,
                        date_input=str(new_date)
                    )
                    ok = update_transaction(selected_id, updated)
                    if ok:
                        st.session_state["message"] = ("success", "Transaction updated.")
                    else:
                        st.session_state["message"] = ("error", "Transaction failed.")
                except ValidationError as e:
                    st.session_state["message"] = ("error", str(e))

                st.rerun()

        st.divider()

        # ----- Delete -----
        st.write("### Delete Transaction")
        if st.button("Delete Transaction"):
            if delete_transaction(selected_id):
                st.session_state["message"] = ("success", "Transaction deleted.")
            else:
                st.session_state["message"] = ("error", "Delete failed.")
            st.rerun()

# Function for showing flash messages
def show_message():
    # Show flashed message (if any)
    if "message" in st.session_state:
        msg_type, msg_text = st.session_state["message"]
        if msg_type == "success":
            st.success(msg_text)
        elif msg_type == "error":
            st.error(msg_text)
        del st.session_state["message"]   # Remove after showing once