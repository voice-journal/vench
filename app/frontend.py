import time

import pandas as pd
import requests
import streamlit as st

# 백엔드 주소
BACKEND_URL = "http://backend:8000"

st.set_page_config(page_title="Vench", page_icon="🛋️", layout="wide")  # 넓은 화면 사용

st.title("🛋️ Vench")
st.subheader("번아웃 온 당신, 30초만 털어놓으세요.")
st.markdown("---")

# --- [사이드바] 주간 리포트 영역 ---
with st.sidebar:
    st.header("📊 나의 감정 리포트")
    if st.button("🔄 리포트 새로고침"):
        try:
            # 백엔드에서 통계 데이터 가져오기
            res = requests.get(f"{BACKEND_URL}/reports/weekly")
            if res.status_code == 200:
                data = res.json()  # {'기쁨': 3, '불안': 2 ...}

                if data:
                    st.write("최근 감정 분포")
                    # 데이터프레임 변환
                    df = pd.DataFrame(list(data.items()), columns=["감정", "횟수"])
                    df.set_index("감정", inplace=True)

                    # 도넛 차트 같은 막대 차트 보여주기
                    st.bar_chart(df)

                    # 가장 많이 느낀 감정 찾기
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
    "슬픔": {
        "emoji": "💧",
        "msg": "마음이 무거우셨군요. 따뜻한 차 한 잔 어때요?",
        "color": "#1E90FF",
    },
    "분노": {
        "emoji": "🔥",
        "msg": "스트레스가 많으셨네요. 잠시 심호흡하세요.",
        "color": "#FF4500",
    },
    "불안": {
        "emoji": "☁️",
        "msg": "걱정이 많으시군요. 잠시 명상을 해보세요.",
        "color": "#9370DB",
    },
    "평온": {"emoji": "🌿", "msg": "차분하고 안정적인 상태입니다.", "color": "#2E8B57"},
}

tab1, tab2 = st.tabs(["🎙️ 바로 녹음", "📂 파일 업로드"])

with tab1:
    st.write("🎤 마이크 버튼을 누르고 오늘 있었던 일을 털어놓으세요.")
    audio_data = st.audio_input("녹음 시작")

    if audio_data:
        if st.button(
            "💾 일기 저장 및 정밀 분석 시작", key="record_btn", type="primary"
        ):
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
                                    status.update(
                                        label="분석 완료!",
                                        state="complete",
                                        expanded=False,
                                    )
                                    progress_bar.progress(100)

                                    st.balloons()
                                    st.divider()

                                    label = data["emotion_label"]
                                    theme = EMOTION_THEMES.get(
                                        label, EMOTION_THEMES["평온"]
                                    )

                                    col1, col2 = st.columns([1, 1.5])
                                    with col1:
                                        st.markdown(
                                            f"""
                                        <div style="padding: 20px; border-radius: 15px; border: 2px solid {theme["color"]}; text-align: center;">
                                            <h1 style="margin:0;">{theme["emoji"]}</h1>
                                            <h2 style="color: {theme["color"]};">{label}</h2>
                                        </div>
                                        """,
                                            unsafe_allow_html=True,
                                        )
                                    with col2:
                                        st.caption("AI 위로 메시지")
                                        st.info(f"{theme['msg']}")
                                        st.caption("인식된 내용")
                                        st.write(f"_{data['transcript']}_")

                                    # 상세 차트
                                    if data["emotion_score"]:
                                        df = pd.DataFrame(data["emotion_score"])
                                        df.set_index("label", inplace=True)
                                        st.bar_chart(df, color=theme["color"])
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
