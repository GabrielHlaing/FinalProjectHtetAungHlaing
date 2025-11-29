import streamlit as st
import pandas as pd
from datetime import datetime

from core.models import Transaction, ValidationError
from core.database import (
    add_transaction,
    get_transactions_for_user,
    update_transaction_for_user,
    delete_transaction_for_user,
)

# ------------------------------------------------------
# FLASH MESSAGE HANDLER
# ------------------------------------------------------
def show_message():
    """Display success/error message once."""
    if "message" in st.session_state:
        msg_type, msg_text = st.session_state["message"]

        if msg_type == "success":
            st.success(msg_text)
        elif msg_type == "error":
            st.error(msg_text)

        # Ensure it is removed immediately
        del st.session_state["message"]


# ------------------------------------------------------
# MAIN RENDER FUNCTION
# ------------------------------------------------------
def render(multi_currencies, current_user):
    """
    multi_currencies  → list of currencies
    current_user      → dict: {"id": ..., "username": ...}
    """

    user_id = current_user["id"]

    st.header("Manage Transactions")

    # Show all flash messages
    show_message()

    tabA, tabB, tabC = st.tabs(
        ["Add Transaction", "View Transactions", "Edit/Delete"]
    )

    # ======================================================
    # ADD TRANSACTION
    # ======================================================
    with tabA:
        st.subheader("Add New Transaction")

        # unique key for form reset
        form_key = f"add_form_reset_{st.session_state.get('form_reset', 0)}"

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
                        t_type=t_type,
                        amount=amount,
                        currency=currency,
                        category=category,
                        date_input=str(date),
                    )
                    add_transaction(tx, user_id)
                    st.session_state["message"] = ("success", "Transaction added.")
                except ValidationError as e:
                    st.session_state["message"] = ("error", str(e))

                # trigger reset
                st.session_state["form_reset"] = (
                    st.session_state.get("form_reset", 0) + 1
                )
                st.rerun()

    # ======================================================
    # VIEW TRANSACTIONS
    # ======================================================
    with tabB:
        st.subheader("All Transactions")

        rows = get_transactions_for_user(user_id)

        if not rows:
            st.info("No transactions yet.")
        else:
            df = pd.DataFrame(rows)
            df.columns = ["ID", "Type", "Amount", "Currency", "Category", "Date", "User"]
            st.dataframe(df.drop(columns=["User"]), hide_index=True)

    # ======================================================
    # EDIT / DELETE TRANSACTIONS
    # ======================================================
    with tabC:
        st.subheader("Edit or Delete Transactions")

        rows = get_transactions_for_user(user_id)

        if not rows:
            st.info("No transactions to modify.")
            return

        row_ids = [r["id"] for r in rows]
        selected_id = st.selectbox("Transaction ID", row_ids)
        selected = next(r for r in rows if r["id"] == selected_id)

        # -----------------------------
        # EDIT TRANSACTION
        # -----------------------------
        st.markdown("### Edit Transaction")

        with st.form(key="edit_form"):
            new_type = st.selectbox(
                "Type",
                ["Income", "Expense"],
                index=["Income", "Expense"].index(selected["t_type"]),
            )

            new_amount = st.number_input(
                "Amount",
                min_value=0.0,
                step=0.5,
                value=float(selected["amount"]),
            )

            new_currency = st.selectbox(
                "Currency",
                multi_currencies,
                index=multi_currencies.index(selected["currency"]),
            )

            new_category = st.text_input("Category", selected["category"])

            new_date = st.date_input(
                "Date", datetime.strptime(selected["date"], "%Y-%m-%d")
            )

            edit_ok = st.form_submit_button("Save Changes")

            if edit_ok:
                try:
                    updated = Transaction.create(
                        t_type=new_type,
                        amount=new_amount,
                        currency=new_currency,
                        category=new_category,
                        date_input=str(new_date),
                    )

                    ok = update_transaction_for_user(
                        selected_id, updated, user_id
                    )

                    st.session_state["message"] = (
                        ("success", "Transaction updated.")
                        if ok
                        else ("error", "Update failed.")
                    )

                except ValidationError as e:
                    st.session_state["message"] = ("error", str(e))

                st.rerun()

        st.divider()

        # -----------------------------
        # DELETE TRANSACTION
        # -----------------------------
        st.markdown("### Delete Transaction")

        if st.button("Delete Transaction"):
            ok = delete_transaction_for_user(selected_id, user_id)

            st.session_state["message"] = (
                ("success", "Transaction deleted.")
                if ok
                else ("error", "Delete failed.")
            )

            st.rerun()
