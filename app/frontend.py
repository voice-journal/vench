import streamlit as st
import requests
import time
import pandas as pd  # 차트 생성용

# 백엔드 주소 (도커 내부 통신)
BACKEND_URL = "http://backend:8000"

st.set_page_config(page_title="Vench", page_icon="🛋️", layout="centered")

st.title("🛋️ Vench")
st.subheader("번아웃 온 당신, 30초만 털어놓으세요.")
st.markdown("---")

# 🎨 5가지 감정 테마 (이모지, 메시지, 색상)
EMOTION_THEMES = {
    "기쁨": {
        "emoji": "💛",
        "msg": "긍정적인 에너지가 가득하네요! 이 순간을 즐기세요.",
        "color": "#FFD700"
    },
    "슬픔": {
        "emoji": "💧",
        "msg": "마음이 무거우셨군요. 오늘은 따뜻한 차 한 잔 어때요?",
        "color": "#1E90FF"
    },
    "분노": {
        "emoji": "🔥",
        "msg": "스트레스가 많으셨네요. 잠시 심호흡이 필요해 보여요.",
        "color": "#FF4500"
    },
    "불안": {
        "emoji": "☁️",
        "msg": "걱정이 꼬리를 무시는군요. 잠시 명상을 해보는 건 어떨까요?",
        "color": "#9370DB"
    },
    "평온": {
        "emoji": "🌿",
        "msg": "차분하고 안정적인 상태입니다. 지금 흐름이 아주 좋아요.",
        "color": "#2E8B57"
    },
}

# 탭 구성
tab1, tab2 = st.tabs(["🎙️ 바로 녹음", "📂 파일 업로드"])

with tab1:
    st.write("🎤 마이크 버튼을 누르고 오늘 있었던 일을 털어놓으세요.")

    # 1. 녹음 위젯
    audio_data = st.audio_input("녹음 시작")

    if audio_data:
        # 녹음 완료 시 저장 버튼 등장
        if st.button("💾 일기 저장 및 정밀 분석 시작", key="record_btn", type="primary"):

            with st.status("🚀 AI가 당신의 목소리와 감정을 분석 중입니다...", expanded=True) as status:

                # 2. 백엔드로 파일 전송
                files = {"file": ("voice_journal.wav", audio_data, "audio/wav")}
                try:
                    response = requests.post(f"{BACKEND_URL}/diaries", files=files)

                    if response.status_code == 200:
                        diary_id = response.json()["id"]
                        st.write("✅ 서버 전송 완료! 심층 신경망(DeBERTa) 가동 중...")

                        # 3. 결과 Polling (최대 30초 대기 - 모델이 무거워서 넉넉하게)
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.3) # 0.3초 간격
                            progress_bar.progress(min((i + 1), 90)) # 90%까지만 채우고 대기

                            # 백엔드 조회
                            res = requests.get(f"{BACKEND_URL}/diaries/{diary_id}")
                            if res.status_code == 200:
                                data = res.json()
                                if data['status'] == "COMPLETED":
                                    status.update(label="분석 완료!", state="complete", expanded=False)
                                    progress_bar.progress(100)

                                    # 🎉 결과 화면 (펑!)
                                    st.balloons()
                                    st.divider()

                                    # (1) 메인 감정 카드
                                    label = data['emotion_label'] # 예: '불안'
                                    theme = EMOTION_THEMES.get(label, EMOTION_THEMES["평온"])

                                    st.markdown(f"""
                                    <div style="padding: 20px; border-radius: 15px; background-color: #f0f2f6; text-align: center; border: 2px solid {theme['color']};">
                                        <h1 style="margin:0; font-size: 3em;">{theme['emoji']}</h1>
                                        <h2 style="margin:10px 0; color: {theme['color']};">{label}</h2>
                                        <p style="font-size: 1.1em; color: #555;">{theme['msg']}</p>
                                    </div>
                                    """, unsafe_allow_html=True)

                                    st.divider()

                                    # (2) 상세 내용 & 차트
                                    col1, col2 = st.columns([1, 1])

                                    with col1:
                                        st.info(f"🗣 **AI가 인식한 내용:**\n\n{data['transcript']}")

                                    with col2:
                                        st.write("📊 **감정 상세 분포**")
                                        if data['emotion_score']:
                                            # 데이터프레임 변환
                                            df = pd.DataFrame(data['emotion_score'])
                                            # 시각화를 위해 인덱스 설정
                                            df = df.set_index("label")
                                            # 막대 그래프 그리기
                                            st.bar_chart(df, color=theme['color'])
                                    break

                                elif data['status'] == "FAILED":
                                    st.error("분석 중 오류가 발생했습니다. (서버 로그 확인 필요)")
                                    break
                        else:
                            st.warning("분석 시간이 예상보다 오래 걸립니다. (모델 로딩 중일 수 있습니다)")
                    else:
                        st.error(f"저장 실패: {response.status_code}")
                except Exception as e:
                    st.error(f"서버 연결 오류: {e}")

with tab2:
    st.info("파일 업로드 기능은 준비 중입니다. '바로 녹음' 탭을 이용해주세요!")
