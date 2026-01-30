# admin_view.py
from __future__ import annotations

import os
from typing import Any

import altair as alt
import pandas as pd
import requests
import streamlit as st


def _get_json_with_fallback(
    backend_url: str,
    headers: dict,
    paths: list[str],
    params: dict,
) -> Any:
    last_err: Exception | None = None

    for path in paths:
        try:
            r = requests.get(
                f"{backend_url}{path}",
                headers=headers,
                params=params,
                timeout=10,
            )
            if r.status_code == 404:
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e

    raise last_err if last_err else RuntimeError("No endpoint matched")


def get_summary(backend_url: str, headers: dict, params: dict):
    return _get_json_with_fallback(
        backend_url,
        headers,
        ["/feedbacks/summary"],
        params,
    )


def get_categories(backend_url: str, headers: dict, params: dict):
    return _get_json_with_fallback(
        backend_url,
        headers,
        ["/feedbacks/categories"],
        params,
    )


def get_keywords_top(backend_url: str, headers: dict, params: dict):
    return _get_json_with_fallback(
        backend_url,
        headers,
        ["/feedbacks/keywords/top"],
        params,
    )


def get_rows(backend_url: str, headers: dict, params: dict):
    return _get_json_with_fallback(
        backend_url,
        headers,
        ["/feedbacks"],
        params,
    )


def _render_dashboard(
    backend_url: str,
    headers: dict,
    *,
    days: int,
    category: str,
    low_only: bool,
    q: str,
) -> None:
    days_param = 30 if days == 9999 else days

    # --- KPI Summary ---
    try:
        summary = get_summary(backend_url, headers, {"days": days_param})
    except Exception as e:
        st.error(f"요약 API 호출 실패: {e}")
        return

    k1, k2, k3 = st.columns(3)
    k1.metric("전체 피드백 수", f"{summary['total_count']}")
    k2.metric("평균 평점", f"{summary['average_rating']:.2f}")
    k3.metric("저평점 비율(≤2)", f"{summary['low_rating_ratio']*100:.1f}%")

    with st.expander("최근 7일 vs 30일 변화"):
        st.json(summary.get("delta_7_vs_30"))

    st.divider()

    # --- Category distribution ---
    cats = get_categories(backend_url, headers, {"days": days_param})
    df_cat = pd.DataFrame(cats)

    left, right = st.columns([1, 1])

    with left:
        st.subheader("카테고리 분포")
        if not df_cat.empty:
            chart = (
                alt.Chart(df_cat)
                .mark_bar()
                .encode(
                    x=alt.X("category:N", sort="-y", title="category"),
                    y=alt.Y("count:Q", title="count"),
                    tooltip=["category", "count", alt.Tooltip("ratio:Q", format=".2%")],
                )
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("카테고리 데이터가 아직 없어요.")

    with right:
        st.subheader("Rating 분포")
        rows = get_rows(
            backend_url,
            headers,
            {
                "days": days_param,
                "category": None if category in ("ALL", "UNSPECIFIED") else category,
                "low_only": False,
                "q": "",
            },
        )
        df = pd.DataFrame(rows)
        if not df.empty:
            df["rating"] = df["rating"].astype(int)
            dist = df.groupby("rating").size().reset_index(name="count")
            chart2 = alt.Chart(dist).mark_bar().encode(
                x=alt.X("rating:O", title="rating"),
                y=alt.Y("count:Q", title="count"),
                tooltip=["rating", "count"],
            )
            st.altair_chart(chart2, use_container_width=True)
        else:
            st.info("피드백이 아직 없어요.")

    st.divider()

    # --- Top Keywords (Drill-down) ---
    st.subheader("코멘트 키워드 Top N")
    params_kw = {"days": days_param}
    if category not in ("ALL", "UNSPECIFIED"):
        params_kw["category"] = category

    top_kw = get_keywords_top(backend_url, headers, params_kw)
    df_kw = pd.DataFrame(top_kw)
    if not df_kw.empty:
        chart_kw = alt.Chart(df_kw).mark_bar().encode(
            x=alt.X("keyword:N", sort="-y", title="keyword"),
            y=alt.Y("count:Q", title="count"),
            tooltip=["keyword", "count"],
        )
        st.altair_chart(chart_kw, use_container_width=True)
    else:
        st.info("키워드 분석 결과가 아직 없어요(코멘트가 없거나 분석이 진행 중일 수 있어요).")

    st.divider()

    # --- Raw table + CSV ---
    st.subheader("Raw 피드백 (필터/검색/CSV)")
    params_rows = {"days": days_param, "low_only": low_only, "q": q}

    if category == "UNSPECIFIED":
        params_rows["category"] = None
    elif category != "ALL":
        params_rows["category"] = category

    rows = get_rows(backend_url, headers, params_rows)
    df_raw = pd.DataFrame(rows)

    st.dataframe(df_raw, use_container_width=True, height=420)

    csv = df_raw.to_csv(index=False).encode("utf-8-sig")
    st.download_button("CSV 다운로드", data=csv, file_name="feedbacks.csv", mime="text/csv")


def render_admin() -> None:
    BACKEND_URL = st.session_state.get("BACKEND_URL") or os.getenv("BACKEND_URL", "http://backend:8000")
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
    HEADERS = {"X-Admin-Token": ADMIN_TOKEN} if ADMIN_TOKEN else {}

    st.title("🧰 사용자 피드백 대시보드")

    # 상단 액션
    top_l, top_r = st.columns([8, 2])
    with top_r:
        if st.button("← 유저 화면", use_container_width=True):
            st.session_state["view_mode"] = "user"
            st.rerun()

    # --- Filters ---
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    with col1:
        days = st.selectbox(
            "기간",
            [7, 30, 9999],
            index=1,
            format_func=lambda x: "최근 7일" if x == 7 else ("최근 30일" if x == 30 else "전체"),
        )
    with col2:
        category = st.selectbox(
            "카테고리",
            ["ALL", "STT_ACCURACY", "PERFORMANCE", "UX_UI", "BUG", "FEATURE_REQUEST", "OTHER", "UNSPECIFIED"],
            index=0,
        )
    with col3:
        low_only = st.checkbox("저평점만 (≤2)", value=False)
    with col4:
        q = st.text_input("검색 (comment)", value="")

    # ✅ 기존 설계 유지: 필터 만든 뒤 렌더 함수 호출
    _render_dashboard(
        BACKEND_URL,
        HEADERS,
        days=days,
        category=category,
        low_only=low_only,
        q=q,
    )
