import time
import altair as alt
import pandas as pd
import requests
import streamlit as st

# 백엔드 컨테이너 서비스 이름 또는 URL 설정
BACKEND_URL = "http://backend:8000"

st.set_page_config(page_title="Vench", page_icon="🛋️", layout="wide")

# ✅ 세션 상태 초기화: 분석 결과 유지 및 모달 제어용
if "last_diary" not in st.session_state:
    st.session_state["last_diary"] = None

def render_styled_chart(df, color):
    """감정 분석 결과를 시각화하는 차트 함수"""
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

st.title("🛋️ Vench")
st.subheader("번아웃 온 당신, 30초만 털어놓으세요.")
st.markdown("---")

def render_feedback(diary: dict):
    """사용자 피드백을 위한 다이얼로그 렌더링"""
    if diary.get("status") not in ("COMPLETED", "READY"):
        return

    diary_id = diary["id"]
    open_key = f"fb_open_{diary_id}"

    @st.dialog("사용자 피드백")
    def fb_dialog():
        st.write("분석 결과가 도움이 되었나요? 별점과 의견을 남겨주세요 🙏")
        rating = st.slider("별점", 1, 5, 5, key=f"rating_{diary_id}")
        comment = st.text_area("상세 피드백", key=f"comment_{diary_id}")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("전송하기", type="primary", key=f"submit_{diary_id}"):
                res = requests.post(
                    f"{BACKEND_URL}/diaries/{diary_id}/feedback",
                    json={"rating": rating, "comment": comment.strip() or None},
                    timeout=10,
                )
                if res.status_code == 200:
                    st.success("피드백이 저장되었습니다 🙏")
                    st.session_state[open_key] = False
                    st.rerun()
                else:
                    st.error(f"오류 발생: {res.status_code}")

        with c2:
            if st.button("닫기", key=f"close_{diary_id}"):
                st.session_state[open_key] = False
                st.rerun()

    if st.button("📝 사용자 피드백 남기기", key=f"fb_btn_{diary_id}"):
        st.session_state[open_key] = True

    if st.session_state.get(open_key, False):
        fb_dialog()

# --- [사이드바] 주간 감정 리포트 ---
with st.sidebar:
    st.header("📊 나의 감정 리포트")
    if st.button("🔄 리포트 새로고침"):
        try:
            res = requests.get(f"{BACKEND_URL}/reports/weekly")
            if res.status_code == 200:
                data = res.json()
                if data:
                    st.write("최근 감정 분포")
                    df_weekly = pd.DataFrame(list(data.items()), columns=["감정", "횟수"])
                    df_weekly.set_index("감정", inplace=True)
                    render_styled_chart(df_weekly, "#4A90E2")
                    top_emotion = max(data, key=data.get)
                    st.success(f"최근 **'{top_emotion}'**을(를) 가장 많이 느끼셨네요!")
                else:
                    st.info("아직 분석된 데이터가 없습니다.")
            else:
                st.error("데이터를 불러오지 못했습니다.")
        except Exception as e:
            st.error(f"연결 오류: {e}")

# 감정별 테마 설정
EMOTION_THEMES = {
    "기쁨": {"emoji": "💛", "msg": "긍정적인 에너지가 가득하네요!", "color": "#FFD700"},
    "슬픔": {"emoji": "💧", "msg": "마음이 무거우셨군요. 따뜻한 차 한 잔 어때요?", "color": "#1E90FF"},
    "분노": {"emoji": "🔥", "msg": "스트레스가 많으셨네요. 잠시 심호흡하세요.", "color": "#FF4500"},
    "불안": {"emoji": "☁️", "msg": "걱정이 많으시군요. 잠시 명상을 해보세요.", "color": "#9370DB"},
    "평온": {"emoji": "🌿", "msg": "차분하고 안정적인 상태입니다.", "color": "#2E8B57"},
}

tab1, tab2 = st.tabs(["🎙️ 바로 녹음", "📂 파일 업로드"])

with tab1:
    st.write("🎤 마이크 버튼을 누르고 오늘 있었던 일을 털어놓으세요.")
    audio_data = st.audio_input("녹음 시작")

    if audio_data:
        if st.button("💾 일기 저장 및 정밀 분석 시작", key="record_btn", type="primary"):
            with st.status("🚀 AI가 분석 중입니다...", expanded=True) as status:
                files = {"file": ("voice_journal.wav", audio_data, "audio/wav")}
                try:
                    response = requests.post(f"{BACKEND_URL}/diaries", files=files)
                    if response.status_code == 200:
                        diary_id = response.json()["id"]

                        # 폴링(Polling)을 통해 분석 완료 대기
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.5)
                            progress_bar.progress(min(i + 1, 95))

                            res = requests.get(f"{BACKEND_URL}/diaries/{diary_id}")
                            if res.status_code == 200:
                                data = res.json()
                                if data["status"] == "COMPLETED":
                                    st.session_state["last_diary"] = data
                                    status.update(label="분석 완료!", state="complete", expanded=False)
                                    progress_bar.progress(100)
                                    break
                                elif data["status"] == "FAILED":
                                    st.error("분석 실패")
                                    break
                        else:
                            st.error("분석 시간 초과")
                    else:
                        st.error(f"저장 실패: {response.status_code}")
                except Exception as e:
                    st.error(f"연결 오류: {e}")

    # --- 분석 결과 렌더링 영역 ---
    if st.session_state["last_diary"] is not None:
        data = st.session_state["last_diary"]
        if data.get("status") == "COMPLETED":
            label = data["emotion_label"]
            if label == "기쁨": st.snow()
            else: st.toast(f"'{label}' 감정 분석이 완료되었습니다!", icon='✅')

            st.divider()
            theme = EMOTION_THEMES.get(label, EMOTION_THEMES["평온"])

            col1, col2 = st.columns([1, 1.5])
            with col1:
                st.markdown(f"""
                <div style="padding: 20px; border-radius: 15px; border: 2px solid {theme["color"]}; text-align: center;">
                    <h1 style="margin:0;">{theme["emoji"]}</h1>
                    <h2 style="color: {theme["color"]};">{label}</h2>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                # 📔 AI 자동 생성 제목 [Seongryul's Feature]
                st.markdown(f"### 📔 {data.get('title') or '오늘의 소중한 기록'}")

                st.caption("AI 위로 메시지")
                st.info(f"{theme['msg']}")

                # ✨ AI 한 줄 요약 [Seongryul's Feature]
                st.markdown("---")
                st.caption("AI 한 줄 요약")
                st.success(f"**{data.get('summary') or '요약 내용을 생성할 수 없습니다.'}**")

                st.caption("인식된 내용")
                st.write(f"_{data.get('transcript', '')}_")

            if data.get("emotion_score"):
                st.write("📊 상세 감정 분포")
                df_result = pd.DataFrame(data["emotion_score"])
                df_result.set_index("label", inplace=True)
                render_styled_chart(df_result, theme["color"])

            st.divider()
            render_feedback(data)

with tab2:
    st.info("파일 업로드 기능은 현재 준비 중입니다.")
