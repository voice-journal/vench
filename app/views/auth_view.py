import streamlit as st
import requests
import time

def render_auth():
    BACKEND_URL = st.session_state["BACKEND_URL"]
    
    st.title("🛋️ Vench")
    st.subheader("번아웃 온 당신, 30초만 털어놓으세요.")
    st.markdown("---")

    tab1, tab2 = st.tabs(["🔑 로그인", "📝 회원가입"])

    # [로그인 탭]
    with tab1:
        email = st.text_input("이메일", key="login_email")
        password = st.text_input("비밀번호", type="password", key="login_pw")
        
        if st.button("로그인", type="primary", use_container_width=True):
            if not email or not password:
                st.error("이메일을 입력해주세요.")
                return

            try:
                res = requests.post(f"{BACKEND_URL}/auth/login", json={"email": email, "password": password})
                if res.status_code == 200:
                    data = res.json()
                    st.session_state["access_token"] = data["access_token"]
                    st.session_state["user_email"] = email
                    # (추후 백엔드에서 role 정보를 준다면 여기에 is_admin 설정 추가)
                    
                    st.success(f"환영합니다! {email}님 🛋️")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(f"로그인 실패: {res.text}")
            except Exception as e:
                st.error(f"서버 연결 오류: {e}")

    # [회원가입 탭]
    with tab2:
        st.write("Vench와 함께 마음을 챙겨보세요.")
        new_email = st.text_input("이메일", key="signup_email")
        new_pw = st.text_input("비밀번호 (8자 이상)", type="password", key="signup_pw")
        new_pw_chk = st.text_input("비밀번호 확인", type="password", key="signup_pw_chk")

        if st.button("회원가입", use_container_width=True):
            if new_pw != new_pw_chk:
                st.error("비밀번호가 일치하지 않습니다.")
                return

            try:
                res = requests.post(f"{BACKEND_URL}/auth/signup", json={"email": new_email, "password": new_pw})
                if res.status_code == 201:
                    st.success("가입 성공! 로그인 탭에서 로그인해주세요.")
                else:
                    st.error(f"가입 실패: {res.text}")
            except Exception as e:
                st.error(f"서버 연결 오류: {e}")