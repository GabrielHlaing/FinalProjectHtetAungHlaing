import streamlit as st
from models import Transaction, ValidationError
import database
import analytics
import currency_api

# --------------------------------------------
# Initialize DB + settings
# --------------------------------------------
database.init_db()
database.init_settings()

st.title("Backend Testing Interface (With Currency API)")


# ======================================================
# 1. ADD TRANSACTION (Test models + DB)
# ======================================================
st.header("Add a Test Transaction")

with st.form("add_form"):
    t_type = st.selectbox("Type", ["Income", "Expense"])
    amount = st.number_input("Amount", min_value=0.0, step=0.1)
    currency = st.selectbox("Currency", currency_api.get_currency_list())
    category = st.text_input("Category")
    date_input = st.date_input("Date")

    submitted = st.form_submit_button("Add Transaction")

    if submitted:
        try:
            t = Transaction.create(
                t_type=t_type,
                amount=float(amount),
                currency=currency,
                category=category,
                date_input=str(date_input)
            )
            row_id = database.add_transaction(t)
            st.success(f"Inserted with ID {row_id}")

        except ValidationError as e:
            st.error(f"Validation error: {e}")


# ======================================================
# 2. VIEW ALL TRANSACTIONS
# ======================================================
st.header("All Transactions in DB")

rows = database.get_all_transactions()
if rows:
    st.table([dict(r) for r in rows])
else:
    st.info("No transactions found.")


# ======================================================
# 3. BASE CURRENCY SETTINGS
# ======================================================
st.header("Currency Conversion Testing")

current_base = database.get_setting("base_currency")
st.write(f"Current base currency: **{current_base}**")

new_base = st.selectbox("Change Base Currency", currency_api.get_currency_list())

if st.button("Save Base Currency"):
    database.set_setting("base_currency", new_base)
    st.success(f"Base currency set to {new_base}")


# Helper wrapper around currency_api
def convert_live(amount, currency):
    return currency_api.convert_to_base(amount, currency)


# ======================================================
# 4. ANALYTICS — TOTALS
# ======================================================
st.header("Analytics — Totals (Converted to Base Currency)")

totals = analytics.compute_totals(convert_live)
st.write(totals)


# ======================================================
# 5. CATEGORY BREAKDOWN
# ======================================================
st.header("Analytics — Category Breakdown")

category_data = analytics.category_breakdown(convert_live)
st.write(category_data)


# ======================================================
# 6. MONTHLY SUMMARY
# ======================================================
st.header("Analytics — Monthly Summary (Income/Expense per Month)")

monthly = analytics.monthly_summary(convert_live)
st.write(monthly)


# ======================================================
# 7. FORECAST (Uses last 3 months)
# ======================================================
st.header("Forecast Next Month (3-month average)")

forecast = analytics.forecast_next_month(convert_live)
st.write(f"Predicted next month net: {forecast}")
