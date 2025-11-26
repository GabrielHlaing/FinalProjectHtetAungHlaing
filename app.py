import streamlit as st

from api.currency_api import convert_to_base, get_currency_list
from core.database import init_db, init_settings, get_setting

# Import page modules
from tabs import authUI, dashboard, transactions, settings

# ---------------------------------------------
# Initialization
# ---------------------------------------------
st.set_page_config(page_title="Money Tracker", layout="wide")

init_db()
init_settings()

CURRENCIES = get_currency_list()
base_currency = get_setting("base_currency")


# -----------------------------------------------------
# Session keys
# -----------------------------------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None
if "auth_mode" not in st.session_state:
    st.session_state["auth_mode"] = "login"  # or 'register'

# If not logged in, show login/register form and stop further rendering
if not st.session_state["user"]:
    authUI.render()
    st.stop()

# -----------------------------------------------------
# After the user is authenticated
# -----------------------------------------------------
current_user = st.session_state["user"]

# Top-right logout button (keeps title centered)
cols = st.columns([6, 3, 1])

with cols[0]:
    st.title("Money Tracker")

with cols[1]:
    st.markdown(f"#### Welcome, `{current_user['username']}`")   # shows username

with cols[2]:
    if st.button("Logout"):
        st.session_state["user"] = None
        st.rerun()


# ---------------------------------------------
# Main Tabs
# ---------------------------------------------
tab1, tab2, tab3 = st.tabs(["Dashboard", "Transactions", "Settings"])

with tab1:
    dashboard.render(convert_to_base, base_currency, current_user)

with tab2:
    transactions.render(CURRENCIES, current_user)

with tab3:
    settings.render(base_currency, CURRENCIES)
