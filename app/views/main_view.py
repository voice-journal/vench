import streamlit as st
import requests
import pandas as pd
import altair as alt
import time

# --- [1] 감정별 테마 설정 (원래 디자인 복구) ---
EMOTION_THEMES = {
    "기쁨": {"emoji": "💛", "msg": "긍정적인 에너지가 가득하네요!", "color": "#FFD700"},
    "슬픔": {"emoji": "💧", "msg": "마음이 무거우셨군요. 따뜻한 차 한 잔 어때요?", "color": "#1E90FF"},
    "분노": {"emoji": "🔥", "msg": "스트레스가 많으셨네요. 잠시 심호흡하세요.", "color": "#FF4500"},
    "불안": {"emoji": "☁️", "msg": "걱정이 많으시군요. 잠시 명상을 해보세요.", "color": "#9370DB"},
    "평온": {"emoji": "🌿", "msg": "차분하고 안정적인 상태입니다.", "color": "#2E8B57"},
}

def render_styled_chart(df, color):
    """차트 그리기"""
    chart_data = df.reset_index()
    if len(chart_data.columns) < 2: 
        return
    
    x_col = chart_data.columns[0]
    y_col = chart_data.columns[1]

    chart = (
        alt.Chart(chart_data)
        .mark_bar(color=color)
        .encode(
            x=alt.X(f"{x_col}:N", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y(f"{y_col}:Q", title=None),
            tooltip=[x_col, y_col],
        )
        .properties(height=300)
    )
    st.altair_chart(chart, use_container_width=True)

def render_feedback(diary, headers):
    """피드백 모달 및 전송 로직"""
    # 완료된 일기만 피드백 가능
    if diary.get("status") != "COMPLETED": return
    
    diary_id = diary["id"]
    BACKEND_URL = st.session_state["BACKEND_URL"]

    # 모달 상태 관리를 위한 키
    open_key = f"fb_open_{diary_id}"

    @st.dialog("사용자 피드백")
    def fb_dialog():
        st.write("분석 결과가 도움이 되었나요? 별점과 의견을 남겨주세요 🙏")
        
        # 입력 폼
        rating = st.slider("별점", 1, 5, 5, key=f"rating_{diary_id}")
        comment = st.text_area("상세 피드백", key=f"comment_{diary_id}")
        
        # 전송 버튼
        if st.button("전송하기", key=f"submit_{diary_id}", type="primary"):
            # ✅ [핵심] 백엔드 Schema(FeedbackCreate)에 맞춰 데이터 구성
            payload = {
                "diary_id": diary_id,  # <-- 이게 꼭 있어야 합니다!
                "rating": rating,
                "comment": comment.strip() or None
            }
            
            try:
                # POST /feedbacks/ (라우터 prefix 확인 필요)
                res = requests.post(
                    f"{BACKEND_URL}/feedbacks/", 
                    json=payload,
                    headers=headers
                )
                
                # 200 OK 또는 201 Created 성공 처리
                if res.status_code in [200, 201]:
                    st.success("소중한 의견 감사합니다! 🙇")
                    time.sleep(1)
                    st.session_state[open_key] = False # 모달 닫기
                    st.rerun() # 화면 갱신
                else:
                    # 에러 상세 메시지 출력 (디버깅용)
                    st.error(f"전송 실패 ({res.status_code}): {res.text}")
            except Exception as e:
                st.error(f"서버 연결 오류: {e}")

    # 피드백 남기기 버튼
    if st.button("📝 사용자 피드백 남기기", key=f"btn_fb_{diary_id}"):
        st.session_state[open_key] = True

    # 모달 띄우기
    if st.session_state.get(open_key, False):
        fb_dialog()

def render_main():
    BACKEND_URL = st.session_state["BACKEND_URL"]
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}

    # 세션 상태 초기화 (main_view 진입 시)
    if "last_diary" not in st.session_state:
        st.session_state["last_diary"] = None

    # --- [상단바] ---
    c1, c2 = st.columns([8, 2])
    with c1:
        st.title("🛋️ Vench")
        st.subheader("번아웃 온 당신, 30초만 털어놓으세요.")
    with c2:
        user_info = st.session_state.get("nickname", st.session_state.get("user_email", "Guest"))
        st.caption(f"User: {user_info}")
        if st.button("로그아웃"):
            st.session_state["access_token"] = None
            st.rerun()
    st.markdown("---")

    # --- [사이드바] 주간 감정 리포트 (복원 완료) ---
    with st.sidebar:
        st.header("📊 나의 감정 리포트")
        if st.button("🔄 리포트 새로고침"):
            try:
                # [수정] 헤더(토큰)를 포함해서 요청해야 내 데이터를 가져올 수 있습니다.
                res = requests.get(f"{BACKEND_URL}/reports/weekly", headers=headers)
                
                if res.status_code == 200:
                    data = res.json()
                    if data:
                        st.write("최근 감정 분포")
                        # 딕셔너리를 DataFrame으로 변환
                        df_weekly = pd.DataFrame(list(data.items()), columns=["감정", "횟수"])
                        df_weekly.set_index("감정", inplace=True)
                        
                        render_styled_chart(df_weekly, "#4A90E2")
                        
                        # 최빈 감정 찾기
                        top_emotion = max(data, key=data.get)
                        st.success(f"최근 **'{top_emotion}'**을(를) 가장 많이 느끼셨네요!")
                    else:
                        st.info("아직 분석된 데이터가 없습니다.")
                elif res.status_code == 404:
                    st.warning("리포트 기능이 아직 서버에 배포되지 않았습니다.")
                else:
                    st.error(f"데이터 불러오기 실패: {res.status_code}")
            except Exception as e:
                st.error(f"연결 오류: {e}")

    # --- 메인 기능 (탭) ---
    tab1, tab2 = st.tabs(["🎙️ 바로 녹음", "📂 파일 업로드"])

    with tab1:
        st.write("🎤 마이크 버튼을 누르고 오늘 있었던 일을 털어놓으세요.")
        audio_data = st.audio_input("녹음 시작")

        if audio_data:
            if st.button("💾 일기 저장 및 정밀 분석 시작", key="record_btn", type="primary"):
                files = {"file": ("voice_journal.wav", audio_data, "audio/wav")}
                
                with st.status("🚀 AI가 분석 중입니다...", expanded=True) as status:
                    try:
                        # 1. 업로드
                        res = requests.post(f"{BACKEND_URL}/diaries/", files=files, headers=headers)
                        
                        if res.status_code in [200, 201]:
                            diary_id = res.json()["id"]
                            
                            # 2. 폴링 (Polling)
                            progress_bar = st.progress(0)
                            for i in range(100): # 약 50초 대기
                                time.sleep(0.5)
                                progress_bar.progress(min(i + 1, 95))

                                chk = requests.get(f"{BACKEND_URL}/diaries/{diary_id}", headers=headers)
                                if chk.status_code == 200:
                                    data = chk.json()
                                    if data["status"] == "COMPLETED":
                                        st.session_state["last_diary"] = data
                                        status.update(label="분석 완료!", state="complete", expanded=False)
                                        progress_bar.progress(100)
                                        st.rerun() # 화면 갱신
                                        break
                                    elif data["status"] == "FAILED":
                                        status.update(label="분석 실패", state="error")
                                        st.error("분석 중 오류가 발생했습니다.")
                                        break
                            else:
                                status.update(label="분석 시간 초과", state="error")
                                st.error("분석 시간이 너무 오래 걸립니다.")
                        else:
                            st.error(f"저장 실패: {res.status_code}")
                    except Exception as e:
                        st.error(f"연결 오류: {e}")

    # --- 분석 결과 렌더링 (UI 복구 완료) ---
    if st.session_state["last_diary"] is not None:
        data = st.session_state["last_diary"]
        # 완료된 상태일 때만 표시
        if data.get("status") == "COMPLETED":
            label = data.get("emotion_label", "평온")
            
            # 테마 가져오기 (없으면 평온 기본값)
            theme = EMOTION_THEMES.get(label, EMOTION_THEMES["평온"])

            if label == "기쁨": 
                st.snow()
            else: 
                st.toast(f"'{label}' 감정 분석이 완료되었습니다!", icon='✅')

            st.divider()

            # 레이아웃 복구 (이모지 카드 + 텍스트)
            col1, col2 = st.columns([1, 1.5])
            with col1:
                st.markdown(f"""
                <div style="padding: 20px; border-radius: 15px; border: 2px solid {theme["color"]}; text-align: center;">
                    <h1 style="margin:0; font-size: 3rem;">{theme["emoji"]}</h1>
                    <h2 style="color: {theme["color"]}; margin-top: 10px;">{label}</h2>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                # 제목
                title = data.get('title') or '오늘의 소중한 기록'
                st.markdown(f"### 📔 {title}")

                # 위로 메시지
                st.caption("AI 위로 메시지")
                st.info(f"{theme['msg']}")

                # 한 줄 요약
                st.markdown("---")
                st.caption("AI 한 줄 요약")
                summary = data.get('summary') or '요약 내용을 생성할 수 없습니다.'
                st.success(f"**{summary}**")

                # 텍스트 원문
                st.caption("인식된 내용")
                st.write(f"_{data.get('transcript', '')}_")

            # 상세 감정 차트
            if data.get("emotion_score"):
                st.write("📊 상세 감정 분포")
                # 리스트 형태 변환 처리
                scores = data["emotion_score"]
                if isinstance(scores, list):
                    df_result = pd.DataFrame(scores).set_index("label")
                else:
                    df_result = pd.DataFrame(list(scores.items()), columns=["label", "score"]).set_index("label")
                
                render_styled_chart(df_result, theme["color"])

            st.divider()
            render_feedback(data, headers)

    with tab2:
        st.info("파일 업로드 기능은 현재 준비 중입니다.")