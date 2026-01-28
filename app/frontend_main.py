import streamlit as st
from app.views.auth_view import render_auth
from app.views.main_view import render_main
from app.views.admin_view import render_admin

# 1. 페이지 기본 설정 (가장 먼저 실행되어야 함)
st.set_page_config(page_title="Vench", page_icon="🛋️", layout="wide")

# 2. 전역 상수 설정
# (Docker 환경 변수나 기본값 사용)
if "BACKEND_URL" not in st.session_state:
    import os
    # .env 로드 (필요시)
    # from dotenv import load_dotenv; load_dotenv()
    st.session_state["BACKEND_URL"] = os.getenv("BACKEND_URL", "http://backend:8000")

# 3. 세션 상태 초기화
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

def main():
    """
    메인 라우팅 로직
    토큰이 없으면 -> 로그인 화면
    토큰이 있으면 -> 메인 화면 (관리자는 관리자 화면 접근 가능)
    """
    if not st.session_state["access_token"]:
        render_auth()
    else:
        # 로그인 상태
        # (선택) 사이드바에서 페이지 이동 메뉴 제공 가능
        if st.session_state["is_admin"]:
            page = st.sidebar.radio("메뉴", ["메인 서비스", "관리자 페이지"])
            if page == "관리자 페이지":
                render_admin()
            else:
                render_main()
        else:
            render_main()

if __name__ == "__main__":
    main()