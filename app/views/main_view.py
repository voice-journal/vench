import streamlit as st
import requests
import pandas as pd
import altair as alt
import time
from datetime import datetime

# --- [1] 감정별 테마 설정 ---
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
    if len(chart_data.columns) < 2: return

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
        .properties(height=200) # 높이 조절
    )
    st.altair_chart(chart, use_container_width=True)

def render_feedback(diary, headers):
    """피드백 모달 및 전송 로직"""
    if diary.get("status") != "COMPLETED": return

    diary_id = diary["id"]
    BACKEND_URL = st.session_state["BACKEND_URL"]
    open_key = f"fb_open_{diary_id}"

    @st.dialog("사용자 피드백")
    def fb_dialog():
        st.write("분석 결과가 도움이 되었나요? 별점과 의견을 남겨주세요 🙏")
        rating = st.slider("별점", 1, 5, 5, key=f"rating_{diary_id}")
        comment = st.text_area("상세 피드백", key=f"comment_{diary_id}")

        if st.button("전송하기", key=f"submit_{diary_id}", type="primary"):
            payload = {
                "diary_id": diary_id,
                "rating": rating,
                "comment": comment.strip() or None
            }
            try:
                res = requests.post(f"{BACKEND_URL}/feedbacks/", json=payload, headers=headers)
                if res.status_code in [200, 201]:
                    st.success("소중한 의견 감사합니다! 🙇")
                    time.sleep(1)
                    st.session_state[open_key] = False
                    st.rerun()
                else:
                    st.error(f"전송 실패 ({res.status_code}): {res.text}")
            except Exception as e:
                st.error(f"서버 연결 오류: {e}")

    if st.button("📝 사용자 피드백 남기기", key=f"btn_fb_{diary_id}"):
        st.session_state[open_key] = True

    if st.session_state.get(open_key, False):
        fb_dialog()

def render_main():
    BACKEND_URL = st.session_state["BACKEND_URL"]
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}

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

    # --- [사이드바] 감정 리포트 ---
    with st.sidebar:
        st.header("📊 나의 감정 리포트")

        # [New] 자동 로딩 시도 (또는 버튼 클릭)
        if st.button("🔄 리포트 새로고침", use_container_width=True):
            try:
                res = requests.get(f"{BACKEND_URL}/reports/weekly", headers=headers)
                if res.status_code == 200:
                    data = res.json() # {"기쁨": 3, "슬픔": 1 ...}
                    if data:
                        st.write("📈 누적 감정 통계")
                        # Dict -> DataFrame
                        df_report = pd.DataFrame(list(data.items()), columns=["감정", "횟수"])
                        df_report.set_index("감정", inplace=True)

                        render_styled_chart(df_report, "#4A90E2")

                        top_emotion = max(data, key=data.get)
                        st.success(f"최근 **'{top_emotion}'** 감정이 가장 많았어요.")
                    else:
                        st.info("아직 데이터가 충분하지 않습니다.")
                else:
                    st.warning("데이터를 불러올 수 없습니다.")
            except Exception as e:
                st.error(f"연결 오류: {e}")

    # --- 메인 기능 (녹음) ---
    st.write("🎤 마이크 버튼을 누르고 오늘 있었던 일을 털어놓으세요.")
    audio_data = st.audio_input("녹음 시작")

    if audio_data:
        if st.button("💾 일기 저장 및 정밀 분석 시작", key="record_btn", type="primary"):
            files = {"file": ("voice_journal.wav", audio_data, "audio/wav")}

            with st.status("🚀 AI가 분석 중입니다...", expanded=True) as status:
                try:
                    res = requests.post(f"{BACKEND_URL}/diaries/", files=files, headers=headers)
                    if res.status_code in [200, 201 ,202]:
                        diary_id = res.json()["id"]

                        # Polling
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.5)
                            progress_bar.progress(min(i + 1, 95))
                            chk = requests.get(f"{BACKEND_URL}/diaries/{diary_id}", headers=headers)
                            if chk.status_code == 200:
                                data = chk.json()
                                if data["status"] == "COMPLETED":
                                    st.session_state["last_diary"] = data
                                    status.update(label="분석 완료!", state="complete", expanded=False)
                                    progress_bar.progress(100)
                                    st.rerun()
                                    break
                                elif data["status"] == "FAILED":
                                    status.update(label="분석 실패", state="error")
                                    st.error("분석 중 오류가 발생했습니다.")
                                    break
                        else:
                            st.error("분석 시간 초과")
                    else:
                        st.error(f"저장 실패: {res.status_code}")
                except Exception as e:
                    st.error(f"연결 오류: {e}")

    # --- [분석 결과 뷰] ---
    if st.session_state["last_diary"] is not None:
        data = st.session_state["last_diary"]
        if data.get("status") == "COMPLETED":
            label = data.get("emotion_label", "평온")
            theme = EMOTION_THEMES.get(label, EMOTION_THEMES["평온"])

            if label == "기쁨": st.snow()
            else: st.toast(f"'{label}' 감정 분석이 완료되었습니다!", icon='✅')

            st.divider()
            col1, col2 = st.columns([1, 1.5])
            with col1:
                st.markdown(f"""
                <div style="padding: 20px; border-radius: 15px; border: 2px solid {theme["color"]}; text-align: center;">
                    <h1 style="margin:0; font-size: 3rem;">{theme["emoji"]}</h1>
                    <h2 style="color: {theme["color"]}; margin-top: 10px;">{label}</h2>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                title = data.get('title') or '오늘의 소중한 기록'
                st.markdown(f"### 📔 {title}")
                st.caption("AI 위로 메시지")
                st.info(f"{theme['msg']}")

                st.markdown("---")
                summary = data.get('summary') or '요약 내용을 생성할 수 없습니다.'
                st.caption("AI가 정리한 오늘의 일기")
                st.success(f"**{summary}**")

                with st.expander("원본 녹음 내용 보기"):
                    st.write(data.get('transcript', ''))

            st.divider()
            render_feedback(data, headers)

    # --- [New] 히스토리 (지난 기록) 섹션 ---
    st.markdown("---")
    st.subheader("📜 지난 기록 모아보기")

    # 히스토리 불러오기 (자동)
    try:
        # limit=5 (최근 5개만)
        hist_res = requests.get(f"{BACKEND_URL}/diaries/?skip=0&limit=5", headers=headers)
        if hist_res.status_code == 200:
            history_list = hist_res.json()["items"]

            if not history_list:
                st.info("아직 저장된 일기가 없습니다. 첫 기록을 남겨보세요!")
            else:
                for item in history_list:
                    # 간단한 카드 형태로 출력
                    emo = item.get("emotion_label", "평온")
                    emoji = EMOTION_THEMES.get(emo, {}).get("emoji", "📄")
                    date_str = item["created_at"][:10] # YYYY-MM-DD
                    title = item.get("title") or "제목 없음"

                    with st.expander(f"{emoji} [{date_str}] {title}"):
                        st.caption(f"감정: {emo}")
                        st.write(item.get("summary") or "내용 없음")
                        # 상세보기 버튼 (누르면 위쪽 메인 뷰에 로드)
                        if st.button("이 기록 다시 보기", key=f"hist_btn_{item['id']}"):
                            st.session_state["last_diary"] = item
                            st.rerun()
        else:
            st.warning("지난 기록을 불러올 수 없습니다.")
    except Exception as e:
        st.error(f"히스토리 로딩 실패: {e}")
