import streamlit as st

from core.auth import register_user, authenticate_user


# -----------------------------------------------------
# Authentication UI (prevents app rendering until logged in)
# -----------------------------------------------------
def render():
    st.header("Please SignIn/Register to Access Money Tracker")

    mode = st.radio("Mode", ["Login", "Register"],
                    index=0 if st.session_state["auth_mode"] == "login" else 1)
    st.session_state["auth_mode"] = "login" if mode == "Login" else "register"

    with st.form(key="auth_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Submit")

        if submit:
            if st.session_state["auth_mode"] == "register":
                ok, err = register_user(username, password)
                if ok:
                    st.success("Account created — you may now log in.")
                    st.session_state["auth_mode"] = "login"
                else:
                    st.error(f"Registration failed: {err}")
            else:
                user = authenticate_user(username, password)
                if user:
                    st.session_state["user"] = user
                    st.rerun()
                else:
                    st.error("Invalid credentials")
