import streamlit as st

from api.currency_api import convert_to_base, get_currency_list
from core.database import init_db, init_settings, get_setting

# Import page modules
from tabs import dashboard, transactions, settings

# ---------------------------------------------
# Initialization
# ---------------------------------------------
st.set_page_config(page_title="Money Tracker", layout="wide")

init_db()
init_settings()

CURRENCIES = get_currency_list()
base_currency = get_setting("base_currency")

if "message" not in st.session_state:
    st.session_state["message"] = None

st.title("Money Tracker")

# ---------------------------------------------
# Main Tabs
# ---------------------------------------------
tab1, tab2, tab3 = st.tabs(["Dashboard", "Transactions", "Settings"])

with tab1:
    dashboard.render(convert_to_base, base_currency)

with tab2:
    transactions.render(convert_to_base, base_currency, CURRENCIES)

with tab3:
    settings.render(convert_to_base, base_currency, CURRENCIES)
