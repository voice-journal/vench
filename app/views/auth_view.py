import streamlit as st
import requests
import time

# [1] Page Config
st.set_page_config(page_title="Vench - 마음을 담는 공간", page_icon="🛋️", layout="centered")

# [2] Custom CSS: 감성적인 UI 구현
st.markdown("""
<style>
    /* 폰트 설정 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;500&display=swap');
    
    .main {
        background-color: #F8F9FA;
    }

    /* 상단 둥둥 뜨는 이모지 애니메이션 */
    .floating-emoji {
        display: flex;
        justify-content: center;
        font-size: 80px;
        animation: float 3s ease-in-out infinite;
        margin-bottom: 20px;
    }

    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
        100% { transform: translateY(0px); }
    }

    /* 감성 문구 스타일 */
    .slogan {
        font-family: 'Noto+Serif+KR', serif;
        text-align: center;
        color: #555;
        font-size: 1.2rem;
        margin-bottom: 40px;
        line-height: 1.6;
    }

    /* 중앙 정렬 컨테이너 */
    .auth-container {
        max-width: 450px;
        margin: 0 auto;
        padding: 30px;
        background: rgba(255, 255, 255, 0.7);
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }

    /* 입력창 스타일 커스텀 */
    div.stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #E0E0E0;
        padding: 10px 15px;
    }

    /* 버튼 스타일 */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: none;
        background: linear-gradient(135deg, #4A90E2 0%, #63B3ED 100%);
        color: white;
        font-weight: 500;
        padding: 12px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(74, 144, 226, 0.3);
    }
    
    /* 탭 메뉴 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        gap: 20px;
    }
</style>
""", unsafe_allow_html=True)

# [3] State Management
if "BACKEND_URL" not in st.session_state:
    st.session_state["BACKEND_URL"] = "http://localhost:8000"

# [4] UI Components Functions
def render_header():
    """상단 이모지 및 서비스 문구 렌더링"""
    st.markdown('<div class="floating-emoji">🛋️</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="slogan">
        잠시 쉬어가세요, <br>
        당신의 오늘을 마음으로 들어줄게요.
    </div>
    """, unsafe_allow_html=True)

def login_logic(email, password):
    """백엔드 로그인 통신"""
    try:
        res = requests.post(
            f"{st.session_state['BACKEND_URL']}/auth/login", 
            json={"email": email, "password": password},
            timeout=5
        )
        if res.status_code == 200:
            data = res.json()
            st.session_state["access_token"] = data["access_token"]
            st.session_state["user_email"] = email
            st.success("반가워요! 당신의 공간으로 이동합니다. ✨")
            time.sleep(1)
            st.rerun()
        else:
            st.error("이메일이나 비밀번호를 다시 확인해주세요.")
    except Exception as e:
        st.error(f"서버에 연결할 수 없습니다: {e}")

def signup_logic(email, password, nickname):
    """백엔드 회원가입 통신"""
    try:
        # DB 모델과 동기화: email, password, nickname
        payload = {"email": email, "password": password, "nickname": nickname}
        res = requests.post(
            f"{st.session_state['BACKEND_URL']}/auth/signup", 
            json=payload,
            timeout=5
        )
        if res.status_code == 201:
            st.success("Vench의 가족이 되신 걸 환영합니다! 로그인 해주세요. 🌿")
        else:
            st.error(f"가입에 실패했습니다: {res.text}")
    except Exception as e:
        st.error(f"서버에 연결할 수 없습니다: {e}")

# [5] Main Logic
def main():
    render_header()
    
    # 중앙 정렬을 위한 컬럼 배치
    _, center_col, _ = st.columns([1, 4, 1])
    
    with center_col:
        tab1, tab2 = st.tabs(["🔒 로그인", "📝 시작하기"])
        
        with tab1:
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            login_email = st.text_input("이메일", key="l_email", placeholder="example@email.com")
            login_pw = st.text_input("비밀번호", key="l_pw", type="password", placeholder="••••••••")
            
            if st.button("내 방으로 입장하기", key="btn_login"):
                if login_email and login_pw:
                    login_logic(login_email, login_pw)
                else:
                    st.warning("모든 정보를 입력해주세요.")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            new_email = st.text_input("이메일", key="s_email", placeholder="가장 자주 쓰는 이메일")
            new_nickname = st.text_input("닉네임", key="s_nick", placeholder="당신을 어떻게 불러드릴까요?")
            new_pw = st.text_input("비밀번호", key="s_pw", type="password", placeholder="8자 이상 입력해주세요")
            new_pw_chk = st.text_input("비밀번호 확인", key="s_pw_chk", type="password")
            
            if st.button("Vench 시작하기", key="btn_signup"):
                if new_pw != new_pw_chk:
                    st.error("비밀번호가 서로 달라요.")
                elif new_email and new_pw and new_nickname:
                    signup_logic(new_email, new_pw, new_nickname)
                else:
                    st.warning("비어있는 칸이 있는지 확인해주세요.")
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()