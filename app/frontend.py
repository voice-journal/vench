import time
import altair as alt
import pandas as pd
import requests
import streamlit as st

# 백엔드 주소 (팀원들이 로컬에서 돌릴 경우 localhost로 수정 필요할 수 있음)
BACKEND_URL = "http://backend:8000"

st.set_page_config(page_title="Vench", page_icon="🛋️", layout="wide")

# 1. [가독성 개선] 차트 레이블을 가로로 고정하는 헬퍼 함수
def render_styled_chart(df, color):
    chart_data = df.reset_index()
    # 컬럼명이 'label', '감정', 'index' 등 무엇이든 첫 번째와 두 번째 컬럼을 사용
    x_col = chart_data.columns[0]
    y_col = chart_data.columns[1]

    chart = (
        alt.Chart(chart_data)
        .mark_bar(color=color)
        .encode(
            x=alt.X(f"{x_col}:N", title=None, axis=alt.Axis(labelAngle=0)), # 글자 각도 0도 고정!
            y=alt.Y(f"{y_col}:Q", title=None),
            tooltip=[x_col, y_col],
        )
        .properties(height=300)
    )
    st.altair_chart(chart, use_container_width=True)

st.title("🛋️ Vench")
st.subheader("번아웃 온 당신, 30초만 털어놓으세요.")
st.markdown("---")

# --- [사이드바] 주간 리포트 영역 ---
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
                    render_styled_chart(df_weekly, "#4A90E2") # 가로 레이블 적용

                    top_emotion = max(data, key=data.get)
                    st.success(f"최근 **'{top_emotion}'**을(를) 가장 많이 느끼셨네요!")
                else:
                    st.info("아직 분석된 데이터가 없습니다.")
            else:
                st.error("데이터를 불러오지 못했습니다.")
        except Exception as e:
            st.error(f"연결 오류: {e}")
    else:
        st.info("버튼을 눌러 내 감정 통계를 확인하세요.")

# --- 메인 기능 영역 ---
EMOTION_THEMES = {
    "기쁨": {"emoji": "💛", "msg": "긍정적인 에너지가 가득하네요!", "color": "#FFD700"},
    "슬픔": {"emoji": "💧", "msg": "마음이 무거우셨군요. 따뜻한 차 한 잔 어때요?", "color": "#1E90FF"},
    "분너": {"emoji": "🔥", "msg": "스트레스가 많으셨네요. 잠시 심호흡하세요.", "color": "#FF4500"},
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
                        st.write("✅ 서버 전송 완료! 분석 중...")

                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.5)
                            progress_bar.progress(min(i + 1, 95))

                            res = requests.get(f"{BACKEND_URL}/diaries/{diary_id}")
                            if res.status_code == 200:
                                data = res.json()
                                if data["status"] == "COMPLETED":
                                    status.update(label="분석 완료!", state="complete", expanded=False)
                                    progress_bar.progress(100)

                                    # 2. [탈-유치 업그레이드] 감정별 세련된 효과 적용
                                    label = data["emotion_label"]
                                    if label == "기쁨":
                                        st.snow() # 기쁨은 차분하고 예쁜 눈 효과
                                    else:
                                        st.toast(f"'{label}' 감정 분석이 완료되었습니다!", icon='✅') # 나머지는 깔끔한 토스트

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
                                        st.caption("AI 위로 메시지")
                                        st.info(f"{theme['msg']}")
                                        st.caption("인식된 내용")
                                        st.write(f"_{data['transcript']}_")

                                    # 3. [가독성 개선] 메인 분석 결과 가로 레이블 차트
                                    if data["emotion_score"]:
                                        st.write("📊 상세 감정 분석 결과")
                                        df_result = pd.DataFrame(data["emotion_score"])
                                        df_result.set_index("label", inplace=True)
                                        render_styled_chart(df_result, theme["color"])
                                    break
                                elif data["status"] == "FAILED":
                                    st.error("분석 실패")
                                    break
                        else:
                            st.error("시간 초과")
                    else:
                        st.error("저장 실패")
                except Exception as e:
                    st.error(f"에러: {e}")

with tab2:
    st.info("준비 중입니다.")
