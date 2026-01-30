import sys
import os
import streamlit as st

# [1] 프로젝트 루트 경로를 Python Path에 추가 (에러 해결 핵심)
# 현재 파일(frontend.py)의 부모 디렉토리(app)의 부모(루트)를 경로에 추가합니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# [2] 이제 app 패키지를 정상적으로 임포트할 수 있습니다.
try:
    from app.core.config import settings
    from app.views.auth_view import main as render_auth
    from app.views.main_view import render_main
    from app.views.admin_view import main as render_admin
except ImportError as e:
    st.error(f"모듈 임포트 실패: {e}")
    st.stop()

# [1] 페이지 설정
st.set_page_config(page_title="Vench - 마음을 담는 공간", page_icon="🛋️", layout="wide")

# [2] 전역 변수 및 상태 초기화
if "BACKEND_URL" not in st.session_state:
    st.session_state["BACKEND_URL"] = settings.BACKEND_URL

if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

if "user_role" not in st.session_state: # [추가] 유저 역할 상태 관리
    st.session_state["user_role"] = "user"

def main():
    # [3] 라우팅 로직
    # 로그인 하지 않은 경우
    if st.session_state["access_token"] is None:
        try:
            render_auth()
        except Exception as e:
            st.error(f"인증 화면을 불러오는 중 오류가 발생했습니다: {e}")
    
    # 로그인 성공 후
    else:
        # 사이드바 상단에 관리자/사용자 모드 전환 기능 (관리자일 경우만 표시)
        if st.session_state["user_role"] == "ADMIN":
            with st.sidebar:
                st.markdown("### 🛠️ 관리 센터")
                app_mode = st.selectbox("메뉴 선택", ["🎤  Vench", "🛡️ Admin Dashboard"])
                st.divider()
            
            if app_mode == "🛡️ Admin Dashboard":
                render_admin()
            else:
                render_main()
        
        # 일반 사용자일 경우 바로 메인 렌더링
        else:
            render_main()
        # try:
        #     render_main()
        # except Exception as e:
        #     # 토큰 만료 등의 사유로 에러 발생 시 세션 초기화 후 재시도 유도
        #     st.error(f"서비스 화면 렌더링 중 오류 발생: {e}")
        #     if st.button("로그인 화면으로 돌아가기"):
        #         st.session_state["access_token"] = None
        #         st.rerun()

if __name__ == "__main__":
    main()