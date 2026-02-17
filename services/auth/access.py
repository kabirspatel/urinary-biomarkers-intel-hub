"""MVP access control: shared passcode in secrets."""
import streamlit as st
import hmac

def require_login():
    st.sidebar.header("Private Access")
    expected = st.secrets.get("DASHBOARD_PASSCODE", "")
    if not expected:
        st.sidebar.info("Set DASHBOARD_PASSCODE in secrets to enable login gating.")
        return True  # dev mode

    entered = st.sidebar.text_input("Passcode", type="password")
    ok = bool(entered) and hmac.compare_digest(entered, expected)

    if not ok:
        st.warning("Private section. Enter passcode in the sidebar.")
        st.stop()
    return True
