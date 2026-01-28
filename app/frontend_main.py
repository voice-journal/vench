import sys
import os
import streamlit as st

# [중요] app 폴더를 파이썬 경로에 추가 (모듈 임포트 에러 방지)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 뷰 파일 임포트
from app.views.auth_view import render_auth
from app.views.main_view import render_main
# from app.views.admin_view import render_admin (아직 없으면 주석 처리)

# 1. 페이지 설정 (반드시 가장 먼저!)
st.set_page_config(page_title="Vench", page_icon="🛋️", layout="wide")

# 2. 전역 변수 초기화
if "BACKEND_URL" not in st.session_state:
    st.session_state["BACKEND_URL"] = os.getenv("BACKEND_URL", "http://localhost:8000")

# 3. 테스트용 세션 강제 주입 (로그인 패스)
if "access_token" not in st.session_state:
    st.session_state["access_token"] = "TEST_TOKEN" # 더미 토큰
if "user_email" not in st.session_state:
    st.session_state["nickname"] = "Test User❤️" # 더미 닉네임
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

def main():
    # 로그인 체크 로직을 건너뛰고 바로 메인 화면 렌더링
    try:
        render_main()
    except Exception as e:
        st.error(f"화면 렌더링 중 오류 발생: {e}")

if __name__ == "__main__":
    main()