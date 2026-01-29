import streamlit as st
import requests
import pandas as pd
import altair as alt
import time
import random
import json
from datetime import datetime

# --- [1] 감정별 테마 및 위로 메시지 풀(Pool) 설정 (백업용) ---
EMOTION_THEMES = {
    "기쁨": {
        "emoji": "💛",
        "color": "#FFD700",
        "msgs": ["오늘 하루, 정말 반짝반짝 빛나셨군요! ✨"]
    },
    "슬픔": {
        "emoji": "💧",
        "color": "#1E90FF",
        "msgs": ["괜찮아요. 가끔은 소리 내어 울어도 돼요."]
    },
    "분노": {
        "emoji": "🔥",
        "color": "#FF4500",
        "msgs": ["화나는 감정은 당연한 거예요. 억누르지 마세요."]
    },
    "불안": {
        "emoji": "☁️",
        "color": "#9370DB",
        "msgs": ["지금 이 순간, 당신은 안전합니다."]
    },
    "평온": {
        "emoji": "🌿",
        "color": "#2E8B57",
        "msgs": ["잔잔한 호수 같은 하루였군요. 참 좋습니다."]
    },
}

def render_styled_chart(df, color, is_probability=False):
    """
    차트 그리기 (높이 150px 고정)
    - is_probability=True: Y축을 0~1로 고정 (메인 화면용)
    - is_probability=False: Y축 자동 설정 (사이드바 통계용)
    """
    chart_data = df.reset_index()
    if len(chart_data.columns) < 2: return

    x_col = chart_data.columns[0]
    y_col = chart_data.columns[1]

    # 확률일 때만 0~1 고정
    y_scale = alt.Scale(domain=[0, 1]) if is_probability else alt.Undefined
    tooltip_format = ".1%" if is_probability else "d"

    chart = (
        alt.Chart(chart_data)
        .mark_bar(color=color)
        .encode(
            x=alt.X(f"{x_col}:N", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y(f"{y_col}:Q", title=None, scale=y_scale),
            tooltip=[x_col, alt.Tooltip(f"{y_col}", format=tooltip_format)],
        )
        .properties(height=150)
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
        st.subheader("잠시 쉬어가세요, 당신의 하루를 들어줄게요.")
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

        if "report_data" not in st.session_state:
            st.session_state["report_data"] = None

        if st.button("🔄 리포트 새로고침", use_container_width=True):
            try:
                res = requests.get(f"{BACKEND_URL}/reports/weekly", headers=headers)
                if res.status_code == 200:
                    st.session_state["report_data"] = res.json()
                else:
                    st.warning("데이터를 불러올 수 없습니다.")
            except Exception as e:
                st.error(f"연결 오류: {e}")

        if st.session_state["report_data"]:
            data = st.session_state["report_data"]
            if data:
                st.write("📈 누적 감정 통계")
                df_report = pd.DataFrame(list(data.items()), columns=["감정", "횟수"])
                df_report.set_index("감정", inplace=True)

                # 사이드바 통계는 횟수(False)
                render_styled_chart(df_report, "#4A90E2", is_probability=False)

                top_emotion = max(data, key=data.get)
                st.success(f"최근 **'{top_emotion}'** 감정이 가장 많았어요.")
            else:
                st.info("아직 데이터가 충분하지 않습니다.")

    # --- 메인 기능 (녹음) ---
    st.write("🎤 마이크를 켜고, 그저 편안하게 이야기해 보세요.")
    audio_data = st.audio_input("녹음 시작")

    if audio_data:
        if st.button("💾 일기 저장 및 정밀 분석 시작", key="record_btn", type="primary"):
            files = {"file": ("voice_journal.wav", audio_data, "audio/wav")}

            # [Updated] 상태 메시지 UI 개선
            with st.status("🚀 AI와 연결 중입니다...", expanded=True) as status:
                try:
                    res = requests.post(f"{BACKEND_URL}/diaries/", files=files, headers=headers)
                    if res.status_code in [200, 201, 202]:
                        diary_id = res.json()["id"]

                        # [Updated] 텍스트가 함께 나오는 프로그레스 바 시작
                        progress_text = "분석을 시작합니다..."
                        progress_bar = st.progress(0, text=progress_text)

                        for i in range(100):
                            time.sleep(0.2) # 빠른 반응을 위해 0.5 -> 0.2로 단축

                            # 백엔드 상태 조회
                            chk = requests.get(f"{BACKEND_URL}/diaries/{diary_id}", headers=headers)
                            if chk.status_code == 200:
                                data = chk.json()

                                # [New] 백엔드에서 온 생생한 진행 메시지 표시
                                current_msg = data.get("process_message") or "분석 중..."
                                progress_bar.progress(min(i + 1, 95), text=current_msg)

                                if data["status"] == "COMPLETED":
                                    st.session_state["last_diary"] = data
                                    status.update(label="분석 완료!", state="complete", expanded=False)
                                    progress_bar.progress(100, text="✅ 모든 분석이 끝났습니다!")
                                    time.sleep(0.5)
                                    st.rerun()
                                    break
                                elif data["status"] == "FAILED":
                                    status.update(label="분석 실패", state="error")
                                    st.error(f"오류: {data.get('process_message', '알 수 없는 오류')}")
                                    break
                        else:
                            st.error(f"분석 시간 초과")
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

            # [Updated] AI 위로 메시지 우선 사용 (없으면 랜덤 백업 메시지)
            ai_advice = data.get("advice")
            if not ai_advice:
                ai_advice = random.choice(theme.get("msgs", ["수고했어요."]))

            st.toast(f"분석 완료: 오늘의 감정은 '{label}' 입니다.", icon='✅')

            st.divider()

            col1, col2 = st.columns([1, 1.5])

            with col1:
                st.markdown(f"""
                <div style="padding: 20px; border-radius: 15px; border: 2px solid {theme["color"]}; text-align: center; margin-bottom: 20px;">
                    <h1 style="margin:0; font-size: 3rem;">{theme["emoji"]}</h1>
                    <h2 style="color: {theme["color"]}; margin-top: 10px;">{label}</h2>
                    <p style="color: gray; font-size: 0.8rem; margin-top: 5px;">감정 분석 결과</p>
                </div>
                """, unsafe_allow_html=True)

                # 메인 화면 차트는 확률(True)
                scores_data = data.get("emotion_score")
                if scores_data:
                    try:
                        if isinstance(scores_data, str):
                            scores = json.loads(scores_data)
                        else:
                            scores = scores_data

                        if scores:
                            df_score = pd.DataFrame(scores)
                            df_score.rename(columns={"label": "감정", "score": "점수"}, inplace=True)
                            df_score.set_index("감정", inplace=True)

                            render_styled_chart(df_score, theme["color"], is_probability=True)
                    except Exception as e:
                        print(f"Chart Error: {e}")

            with col2:
                title = data.get('title') or '오늘의 소중한 기록'
                st.markdown(f"### 📔 {title}")

                st.caption("💌 AI 위로의 한마디")
                st.info(f"{ai_advice}")  # [Updated] AI 메시지 표시

                st.markdown("---")
                summary = data.get('summary') or '요약 내용을 생성할 수 없습니다.'
                st.caption("📝 AI가 다듬은 오늘의 일기")
                st.success(f"{summary}")

                with st.expander("원본 녹음 내용 보기"):
                    st.write(data.get('transcript', ''))

            st.divider()
            render_feedback(data, headers)

    # --- 히스토리 섹션 ---
    st.markdown("---")
    st.subheader("📜 지난 기록 모아보기")

    try:
        hist_res = requests.get(f"{BACKEND_URL}/diaries/?skip=0&limit=5", headers=headers)
        if hist_res.status_code == 200:
            history_list = hist_res.json()["items"]

            if not history_list:
                st.info("아직 저장된 일기가 없습니다. 첫 기록을 남겨보세요!")
            else:
                for item in history_list:
                    emo = item.get("emotion_label", "평온")
                    emoji = EMOTION_THEMES.get(emo, {}).get("emoji", "📄")
                    date_str = item["created_at"][:10]
                    title = item.get("title") or "제목 없음"

                    with st.expander(f"{emoji} [{date_str}] {title}"):
                        st.caption(f"감정: {emo}")

                        # [Updated] 히스토리에서도 위로 메시지 확인 가능하도록 추가
                        if item.get("advice"):
                            st.info(f"💌 {item['advice']}")

                        st.write(item.get("summary") or "내용 없음")
                        if st.button("이 기록 다시 보기", key=f"hist_btn_{item['id']}"):
                            st.session_state["last_diary"] = item
                            st.rerun()
        else:
            st.warning("지난 기록을 불러올 수 없습니다.")
    except Exception as e:
        st.error(f"히스토리 로딩 실패: {e}")
