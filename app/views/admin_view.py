import streamlit as st
import requests

def render_admin():
    BACKEND_URL = st.session_state["BACKEND_URL"]
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}

    st.title("🛡️ Admin Dashboard")
    st.info("관리자 전용 페이지입니다.")