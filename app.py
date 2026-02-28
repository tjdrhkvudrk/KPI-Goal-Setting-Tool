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

# 시각적 개선을 위한 CSS
st.markdown("""
<style>
    /* 1. 자동 계산 항목(disabled) 스타일: 배경색 유지 및 검정 글씨 */
    input:disabled {
        -webkit-text-fill-color: #000000 !important;
        color: #000000 !important;
        font-weight: 600 !important;
        background-color: #E8F0FE !important;
        border: 1px solid #adc6ff !important;
        opacity: 1 !important;
    }
    
    /* 2. 직접 입력 항목 스타일: 배경색 없음(흰색), 검정 글씨 */
    .stNumberInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* 3. 대분류 헤더 디자인 (글자 크기 키움) */
    .main-header-box {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: 800; /* 더 굵게 */
        font-size: 1.1em; /* 크기 키움 */
        border: 1px solid #d1d5db;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 60px;
        margin-bottom: 5px;
    }
    
    /* 4. 소분류 라벨 및 제목 라벨 (연도 및 표준편차 글자 크기 키움) */
    .sub-label-text {
        text-align: center;
        font-size: 1.0em; /* 0.9em에서 키움 */
        font-weight: 700; /* 더 굵게 */
        color: #111;
        margin-bottom: 8px;
        height: 25px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* 입력칸 위치 조정 */
    .stNumberInput, .stTextInput {
        margin-top: -5px;
    }
</style>
""", unsafe_allow_html=True)

# 사이드바 설정
st.sidebar.header("📍 지표 기본 설정")
indicator_name = st.sidebar.text_input("지표명", value="주요사업 성과지표")
weight = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
direction = st.sidebar.selectbox("지표 방향", ["상향", "하향"])
long_term_goal = st.sidebar.number_input("중장기 목표(Y+3)", value=160.000, format="%.3f")
global_perf = st.sidebar.number_input("글로벌 실적(비교군 평균)", value=140.000, format="%.3f")

# 1. 실적 데이터 입력 섹션
st.subheader("1. 실적 데이터 입력")

# 대분류 레이아웃
header_cols = st.columns([6, 1, 1, 1])
with header_cols[0]:
    st.markdown('<div class="main-header-box">과거 5개년 실적</div>', unsafe_allow_html=True)
with header_cols[1]:
    st.markdown('<div class="main-header-box">과거 3개년 평균</div>', unsafe_allow_html=True)
with header_cols[2]:
    st.markdown('<div class="main-header-box">기준치</div>', unsafe_allow_html=True)
with header_cols[3]:
    st.markdown('<div class="main-header-box">2026년 예상실적</div>', unsafe_allow_html=True)

# 데이터 입력 행 레이아웃
data_cols = st.columns(9)

# [과거 5개년 실적 입력부]
hist = []
for i, year in enumerate(past_years):
    with data_cols[i]:
        st.markdown(f'<div class="sub-label-text">{year}년</div>', unsafe_allow_html=True)
        val = st.number_input(f"{year}실적", label_visibility="collapsed", value=100.000 + (i*5), format="%.3f", key=f"h_{i}")
        hist.append(val)

# 자동 계산 값 준비
std_5y = np.std(hist)
avg_3y = np.mean(hist[-3:])
last_year_val = hist[-1]
base_val = max(avg_3y, last_year_val) if direction == "상향" else min(avg_3y, last_year_val)

# [자동 계산 및 독립 열 입력부]
with data_cols[5]:
    # 표준편차 라벨 강조 및 글자 크기 확대
    st.markdown('<div class="sub-label-text">5개년 표준편차</div>', unsafe_allow_html=True)
    st.text_input("표준편차", value=f"{std_5y:.3f}", label_visibility="collapsed", disabled=True)

with data_cols[6]:
    st.markdown('<div class="sub-label-text">&nbsp;</div>', unsafe_allow_html=True) 
    st.text_input("3개년평균값", value=f"{avg_3y:.3f}", label_visibility="collapsed", disabled=True)

with data_cols[7]:
    st.markdown('<div class="sub-label-text">&nbsp;</div>', unsafe_allow_html=True)
    st.text_input("기준치값", value=f"{base_val:.3f}", label_visibility="collapsed", disabled=True)

with data_cols[8]:
    st.markdown('<div class="sub-label-text">&nbsp;</div>', unsafe_allow_html=True)
    est = st.number_input("예상실적입력", value=base_val * 1.05, format="%.3f", label_visibility="collapsed")

# --- 분석 실행 및 결과 ---
st.markdown("---")
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

    fig, ax = plt.subplots(figsize=(10, 4))
    x = np.arange(len(df))
    ax.bar(x - 0.2, df['최고목표'], 0.4, label='최고목표', color='skyblue')
    ax.bar(x + 0.2, df['최저목표'], 0.4, label='최저목표', color='lightgrey')
    ax.axhline(base_val, color='red', linestyle='--', label='기준치')
    ax.set_xticks(x)
    ax.set_xticklabels(df['평가방법'], rotation=45)
    ax.legend()
    st.pyplot(fig)
