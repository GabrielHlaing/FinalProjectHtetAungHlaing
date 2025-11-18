import streamlit as st
from models import Transaction, ValidationError
import database
import analytics

'''
 Dummy conversion function (1:1)
 Replace later with real currency_api
'''
def convert_dummy(amount, currency):
    return float(amount)  # no conversion


'''
 Init database
'''
database.init_db()
database.init_settings()

st.title("Backend Testing Interface")


"""
ADD TRANSACTION (Test models + DB)
"""
st.header("Add a Test Transaction")

with st.form("add_form"):
    t_type = st.selectbox("Type", ["Income", "Expense"])
    amount = st.number_input("Amount", min_value=0.0, step=0.1)
    currency = st.selectbox("Currency", ["USD", "MMK", "EUR"])
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


"""
VIEW ALL TRANSACTIONS
"""
st.header("All Transactions in DB")

rows = database.get_all_transactions()
if rows:
    st.table([dict(r) for r in rows])
else:
    st.info("No transactions found.")


"""
ANALYTICS: TOTALS
"""
st.header("Analytics — Totals")

totals = analytics.compute_totals(convert_dummy)
st.write(totals)


"""
ANALYTICS: CATEGORY BREAKDOWN
"""
st.header("Analytics — Category Breakdown")

category_data = analytics.category_breakdown(convert_dummy)
st.write(category_data)


"""
ANALYTICS: MONTHLY SUMMARY
"""
st.header("Analytics — Monthly Summary (Income/Expense per month)")

monthly = analytics.monthly_summary(convert_dummy)
st.write(monthly)


"""
FORECAST
"""
st.header("Forecast Next Month (3-month average)")

forecast = analytics.forecast_next_month(convert_dummy)
st.write(f"Predicted next month net: {forecast}")
