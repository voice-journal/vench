import streamlit as st
import requests
import pandas as pd
import altair as alt
import time

def render_styled_chart(df, color):
    """(내부 함수) 차트 그리기"""
    chart_data = df.reset_index()
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
    """(내부 함수) 피드백 모달"""
    if diary.get("status") != "COMPLETED": 
        return
    
    diary_id = diary["id"]
    BACKEND_URL = st.session_state["BACKEND_URL"]

    @st.dialog("사용자 피드백")
    def fb_dialog():
        rating = st.slider("별점", 1, 5, 5, key=f"rating_{diary_id}")
        comment = st.text_area("의견을 남겨주세요", key=f"comment_{diary_id}")
        if st.button("전송", key=f"submit_{diary_id}"):
            res = requests.post(
                f"{BACKEND_URL}/feedbacks/",
                json={"diary_id": diary_id, "rating": rating, "comment": comment},
                headers=headers
            )
            if res.status_code == 201:
                st.success("소중한 의견 감사합니다!")
                st.rerun()
            else:
                st.error("전송 실패")

    if st.button("📝 피드백 남기기", key=f"btn_fb_{diary_id}"):
        fb_dialog()

def render_main():
    BACKEND_URL = st.session_state["BACKEND_URL"]
    # API 호출 시 헤더에 토큰 포함
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}

    # --- 상단바 ---
    c1, c2 = st.columns([8, 2])
    with c1:
        st.title("🛋️ Vench Main")
        st.caption(f"User: {st.session_state['user_email']}")
    with c2:
        if st.button("로그아웃"):
            st.session_state["access_token"] = None
            st.rerun()

    # --- 사이드바 (리포트) ---
    with st.sidebar:
        st.header("📊 나의 감정 리포트")
        if st.button("새로고침"):
            # (백엔드에 주간 리포트 API가 구현되면 호출)
            st.info("준비 중인 기능입니다.")

    # --- 메인 기능 ---
    tab1, tab2 = st.tabs(["🎙️ 녹음하기", "📂 파일 업로드"])
    
    with tab1:
        st.write("오늘 하루는 어땠나요?")
        audio_data = st.audio_input("녹음 시작")
        if audio_data:
            if st.button("분석 시작", type="primary"):
                files = {"file": ("voice.wav", audio_data, "audio/wav")}
                # 1. 업로드
                res = requests.post(f"{BACKEND_URL}/diaries/", files=files, headers=headers)
                if res.status_code == 201:
                    diary_id = res.json()["id"]
                    st.success("업로드 완료! 분석 중...")
                    
                    # 2. 폴링 (Polling)
                    with st.spinner("AI가 분석하고 있어요..."):
                        for _ in range(20): # 최대 10초 대기
                            time.sleep(0.5)
                            chk = requests.get(f"{BACKEND_URL}/diaries/{diary_id}", headers=headers)
                            if chk.status_code == 200:
                                data = chk.json()
                                if data["status"] == "COMPLETED":
                                    st.success("분석 완료!")
                                    st.write(f"**감정**: {data['emotion_label']}")
                                    st.write(f"**요약**: {data['summary']}")
                                    
                                    # 상세 차트
                                    if data.get("emotion_score"):
                                        df = pd.DataFrame(data["emotion_score"]).set_index("label")
                                        render_styled_chart(df, "#4A90E2")
                                    
                                    # 피드백 버튼
                                    render_feedback(data, headers)
                                    break
                                elif data["status"] == "FAILED":
                                    st.error("분석에 실패했습니다.")
                                    break
    
    with tab2:
        st.info("파일 업로드 기능 준비 중")