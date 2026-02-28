import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(page_title="경영평가 지표 시뮬레이터", layout="wide")

# 현재 연도 기준 설정
current_year = 2026 
past_years = [current_year - i for i in range(5, 0, -1)]  # [2021, 2022, 2023, 2024, 2025]

st.title("⚖️ 경영평가 계량지표 통합 시뮬레이터")

# 사이드바: 기본 설정
st.sidebar.header("📍 지표 기본 설정")
indicator_name = st.sidebar.text_input("지표명", value="주요사업 성과지표")
weight = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
direction = st.sidebar.selectbox("지표 방향", ["상향", "하향"])
long_term_goal = st.sidebar.number_input("중장기 목표(Y+3)", value=160.000, format="%.3f")
global_perf = st.sidebar.number_input("글로벌 실적(비교군 평균)", value=140.000, format="%.3f")

# 1. 실적 데이터 입력 섹션
st.subheader("1. 실적 데이터 입력")

# 디자인을 위한 CSS: 높이 통합 및 중앙 정렬
st.markdown("""
<style>
    .full-height-header {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        border: 1px solid #d1d5db;
        height: 78px; /* 좌측 2단 높이와 유사하게 수동 조정 */
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 10px;
    }
    .group-main-header {
        background-color: #f0f2f6;
        padding: 5px;
        border-radius: 5px 5px 0 0;
        text-align: center;
        font-weight: bold;
        border: 1px solid #d1d5db;
        margin-bottom: 5px;
    }
    .sub-label {
        text-align: center;
        font-size: 0.85em;
        font-weight: bold;
        color: #555;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 메인 레이아웃 구성 (좌측 6칸: 과거5개년 그룹 / 우측 각 1칸씩 독립열)
main_cols = st.columns([6, 1, 1, 1])

# --- [좌측] 과거 5개년 실적 그룹 (2단 구성) ---
with main_cols[0]:
    st.markdown('<div class="group-main-header">과거 5개년 실적</div>', unsafe_allow_html=True)
    sub_cols = st.columns(6)
    hist = []
    for i, year in enumerate(past_years):
        with sub_cols[i]:
            st.markdown(f'<div class="sub-label">{year}년</div>', unsafe_allow_html=True)
            val = st.number_input(f"{year}년", label_visibility="collapsed", value=100.000 + (i*5), format="%.3f", key=f"hist_{i}")
            hist.append(val)
    
    # 통계 자동 계산
    std_5y = np.std(hist)
    avg_3y = np.mean(hist[-3:])
    last_year_val = hist[-1]
    
    with sub_cols[5]:
        st.markdown('<div class="sub-label">5개년 표준편차</div>', unsafe_allow_html=True)
        st.text_input("표준편차", value=f"{std_5y:.3f}", label_visibility="collapsed", disabled=True)

# --- [우측] 독립 열들 (통합 높이 헤더 + 입력창) ---
with main_cols[1]:
    st.markdown('<div class="full-height-header">과거 3개년 평균</div>', unsafe_allow_html=True)
    st.text_input("평균값", value=f"{avg_3y:.3f}", label_visibility="collapsed", disabled=True)

with main_cols[2]:
    # 기준치 결정 로직
    base_val = max(avg_3y, last_year_val) if direction == "상향" else min(avg_3y, last_year_val)
    st.markdown('<div class="full-height-header">기준치</div>', unsafe_allow_html=True)
    st.text_input("기준치값", value=f"{base_val:.3f}", label_visibility="collapsed", disabled=True)

with main_cols[3]:
    st.markdown(f'<div class="full-height-header">{current_year}년 예상실적</div>', unsafe_allow_html=True)
    est = st.number_input("예상실적", value=base_val * 1.05, format="%.3f", label_visibility="collapsed")

# --- 분석 실행 및 결과 ---
if st.button("🚀 모든 평가방법 통합 분석 실행"):
    lt_base = base_val + (long_term_goal - base_val) / 4
    methods = [
        ("목표부여(2편차)", base_val + 2*std_5y, base_val - 2*std_5y),
        ("목표부여(1편차)", base_val + 1*std_5y, base_val - 1*std_5y),
        ("목표부여(120%)", base_val * 1.2, base_val * 0.8),
        ("목표부여(110%)", base_val * 1.1, base_val * 0.9),
        ("중장기 목표부여", lt_base * 1.05, lt_base * 0.95),
        ("글로벌 실적비교", global_perf * 1.05, global_perf * 0.95)
    ]
    
    results = []
    for m_name, hi, lo in methods:
        if direction == "하향": hi, lo = lo, hi
        score = max(20.0, min(100.0, 20 + 80 * (est - lo) / (hi - lo))) if hi != lo else 60.0
        weighted_score = (score / 100) * weight
        results.append({
            "평가방법": m_name, "최고목표": round(hi, 3), "최저목표": round(lo, 3),
            "도전성(%)": round(abs(hi - base_val) / base_val * 100, 3), 
            "예상평점": round(score, 3), "예상득점": round(weighted_score, 3)
        })
    
    df = pd.DataFrame(results)
    st.subheader("2. 평가방법별 비교 분석 결과")
    st.dataframe(df.style.format({k: "{:.3f}" for k in df.columns if k != "평가방법"}).highlight_max(axis=0, subset=['예상평점']), use_container_width=True)

    # 시각화
    fig, ax = plt.subplots(figsize=(10, 4))
    x = np.arange(len(df))
    ax.bar(x - 0.2, df['최고목표'], 0.4, label='최고목표', color='skyblue')
    ax.bar(x + 0.2, df['최저목표'], 0.4, label='최저목표', color='lightgrey')
    ax.axhline(base_val, color='red', linestyle='--', label='기준치')
    ax.set_xticks(x)
    ax.set_xticklabels(df['평가방법'], rotation=45)
    ax.legend()
    st.pyplot(fig)
