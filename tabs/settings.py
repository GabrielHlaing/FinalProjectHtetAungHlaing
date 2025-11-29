# settings.py
import streamlit as st
from api.currency_api import get_rate
from core.database import set_setting

def render(base_currency, multi_currencies):

    st.header("Settings")

    # ---------------------------------
    # Base Currency
    # ---------------------------------
    st.subheader("Base Currency")
    st.caption(f"Current base currency: **{base_currency}**")

    new_base = st.selectbox("Select Base Currency", multi_currencies)

    if st.button("Save Settings"):
        set_setting("base_currency", new_base)
        st.rerun()

    st.markdown("---")

    # ---------------------------------
    # Live Rate Viewer
    # ---------------------------------
    st.subheader("Live Exchange Rate")

    compare = st.selectbox("Compare Against", multi_currencies)

    if compare == base_currency:
        st.info("Select a different currency.")
    else:
        rate = get_rate(base_currency, compare)
        st.metric(
            label=f"1 {compare} equals",
            value=f"{rate:.4f} {base_currency}"
        )

    st.markdown("---")

    st.subheader("About")
    st.info(
        "All amounts are converted into the base currency using live exchange rates from [ExchangeRate Host](https://exchangerate.host/)."
    )
