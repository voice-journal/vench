import sys
import os
import streamlit as st
import requests
import time

# [1] Custom CSS: 가로등 조명 및 Noto Sans KR 유지
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

        html, body, [class*="st-"] {
            font-family: 'Noto Sans KR', sans-serif !important;
        }

        /* 배경: 가로등 조명 효과 */
        .stApp {
            background: radial-gradient(circle at 50% -10%, #4A4E69 0%, #22223B 40%, #121212 100%);
            color: #F8F9FA;
        }

        /* 가로등 빛 글로우 */
        .street-light {
            position: fixed;
            top: -150px;
            left: 50%;
            transform: translateX(-50%);
            width: 800px;
            height: 600px;
            background: radial-gradient(circle, rgba(255, 236, 158, 0.12) 0%, rgba(255, 236, 158, 0) 70%);
            pointer-events: none;
            z-index: 0;
        }

        /* 벤치 애니메이션 */
        .floating-bench {
            display: flex;
            justify-content: center;
            font-size: 100px;
            animation: float 4s ease-in-out infinite;
            margin-top: 30px;
            filter: drop-shadow(0 0 25px rgba(255, 236, 158, 0.3));
            z-index: 1;
        }

        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-15px); }
            100% { transform: translateY(0px); }
        }

        .slogan {
            text-align: center;
            color: #E9ECEF;
            font-size: 1.15rem;
            margin-bottom: 30px;
            line-height: 1.7;
            font-weight: 300;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }

        /* 입력창 카드 레이아웃 (투명 유지) */
        .auth-card {
            max-width: 450px;
            margin: 0 auto;
            padding: 10px 0px;
            background: transparent !important;
        }

        /* 입력창 스타일 */
        div.stTextInput > div > div > input {
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px;
            padding: 12px;
        }
        
        label p {
            color: #ADB5BD !important;
            font-size: 0.95rem !important;
        }

        /* 버튼 스타일 */
        .stButton > button {
            width: 100%;
            border-radius: 12px;
            border: none;
            background: linear-gradient(135deg, #FFD166 0%, #F78C6B 100%);
            color: #121212 !important;
            font-weight: 700;
            padding: 14px;
            margin-top: 15px;
        }
        
        .stButton > button:hover {
            box-shadow: 0 8px 25px rgba(255, 209, 102, 0.4);
            color: #121212 !important;
        }

        /* 탭 스타일 */
        .stTabs [data-baseweb="tab-list"] {
            justify-content: center;
            background-color: transparent !important;
        }
        .stTabs [data-baseweb="tab"] {
            color: #6C757D !important;
        }
        .stTabs [aria-selected="true"] {
            color: #FFD166 !important;
            border-bottom-color: #FFD166 !important;
        }
    </style>
    <div class="street-light"></div>
    """, unsafe_allow_html=True)

# [2] API 호출 로직
def login_logic(email, password):
    BACKEND_URL = st.session_state.get("BACKEND_URL", "http://localhost:8000")
    try:
        res = requests.post(
            f"{BACKEND_URL}/auth/login", 
            json={"email": email, "password": password},
            timeout=5
        )
        if res.status_code == 200:
            data = res.json()
            st.session_state["access_token"] = data["access_token"]
            st.session_state["user_email"] = email
            # 성공 시 닉네임 정보가 있다면 세션에 저장 (기존 frontend.py와 호환)
            st.session_state["nickname"] = data.get("nickname", email.split('@')[0])
            st.success("가로등 불빛이 밝아집니다. 환영합니다. ✨")
            time.sleep(1)
            st.rerun()
        else:
            st.error("이메일이나 비밀번호를 다시 확인해 주세요.")
    except Exception as e:
        st.error(f"서버 연결 오류: {e}")

def signup_logic(email, password, nickname):
    BACKEND_URL = st.session_state.get("BACKEND_URL", "http://localhost:8000")
    try:
        # 백엔드 User 모델 규격에 맞춰 전송
        payload = {"email": email, "password": password, "nickname": nickname}
        res = requests.post(
            f"{BACKEND_URL}/auth/signup", 
            json=payload,
            timeout=5
        )
        if res.status_code == 201:
            st.success("이제 당신만의 벤치가 마련되었습니다. 로그인을 진행해 주세요. 🌿")
            time.sleep(1.5)
            st.rerun() # 탭 전환을 유도하기 위해 리런
        else:
            st.error(f"가입에 실패했습니다: {res.text}")
    except Exception as e:
        st.error(f"서버 연결 오류: {e}")

# [3] UI 렌더링 함수
def render_header():
    st.markdown('<div class="floating-bench">🛋️</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="slogan">
        잠시 지친 당신이 언제든 쉬어갈 수 있도록.<br>
        <b>Vench</b>는 이곳에서 당신의 이야기를 기다립니다.
    </div>
    """, unsafe_allow_html=True)

def main():
    inject_custom_css()
    render_header()
    
    _, center_col, _ = st.columns([1, 4, 1])
    
    with center_col:
        tab1, tab2 = st.tabs(["🔒 입장하기", "📝 함께하기"])
        
        with tab1:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            login_email = st.text_input("이메일", key="l_email", placeholder="등록하신 이메일")
            login_pw = st.text_input("비밀번호", key="l_pw", type="password", placeholder="••••••••")
            
            if st.button("벤치에 앉기", key="btn_login"):
                if login_email and login_pw:
                    login_logic(login_email, login_pw)
                else:
                    st.warning("모든 정보를 입력해 주세요.")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            new_email = st.text_input("사용할 이메일", key="s_email", placeholder="email@address.com")
            new_nickname = st.text_input("당신의 이름(닉네임)", key="s_nick", placeholder="어떻게 불러드릴까요?")
            new_pw = st.text_input("비밀번호 설정", key="s_pw", type="password", placeholder="8자 이상")
            new_pw_chk = st.text_input("비밀번호 확인", key="s_pw_chk", type="password")
            
            # 회원가입 버튼 로직 연결
            if st.button("나만의 벤치 만들기", key="btn_signup"):
                if not (new_email and new_nickname and new_pw):
                    st.warning("빈 칸을 모두 채워주세요.")
                elif new_pw != new_pw_chk:
                    st.error("비밀번호 확인이 일치하지 않습니다.")
                else:
                    signup_logic(new_email, new_pw, new_nickname)
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()