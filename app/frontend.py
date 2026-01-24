import streamlit as st
import requests
import os

st.set_page_config(page_title="Vench", page_icon="🛋️")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.title("🛋️ Vench")
st.markdown("### 번아웃 온 당신, 30초만 털어놓으세요.")

# 탭으로 기능 분리
tab1, tab2 = st.tabs(["🔴 바로 녹음", "📁 파일 업로드"])
audio_data = None

with tab1:
    st.write("마이크 버튼을 누르고 말씀하세요.")
    recorded_audio = st.audio_input("녹음 시작")
    if recorded_audio:
        audio_data = ("mic.wav", recorded_audio, "audio/wav")

with tab2:
    uploaded_file = st.file_uploader("파일 선택", type=["mp3", "m4a", "wav", "webm"])
    if uploaded_file:
        audio_data = (uploaded_file.name, uploaded_file, uploaded_file.type)

# 분석 버튼
if audio_data and st.button("🚀 감정 분석 시작", use_container_width=True):
    with st.spinner("AI가 분석 중입니다..."):
        try:
            files = {"file": audio_data}
            res = requests.post(f"{BACKEND_URL}/diaries", files=files)
            if res.status_code == 200:
                st.success("분석이 시작되었습니다!")
                st.json(res.json())
            else:
                st.error(f"서버 에러: {res.text}")
        except Exception as e:
            st.error(f"연결 실패: {e}")
