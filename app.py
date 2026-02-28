import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(page_title="경영평가 지표 시뮬레이터", layout="wide")

# 현재 연도 기준 설정 (2026년)
current_year = 2026 
past_years = [current_year - i for i in range(5, 0, -1)]

st.title("⚖️ 경영평가 계량지표 통합 시뮬레이터")

# 시각적 개선을 위한 CSS
st.markdown("""
<style>
    input:disabled {
        -webkit-text-fill-color: #000000 !important;
        color: #000000 !important;
        font-weight: 600 !important;
        background-color: #E8F0FE !important;
        border: 1px solid #adc6ff !important;
        opacity: 1 !important;
    }
    .stNumberInput input { background-color: #ffffff !important; color: #000000 !important; }
    .main-header-box {
        background-color: #f0f2f6; padding: 10px; border-radius: 5px;
        text-align: center; font-weight: 800; font-size: 1.1em;
        border: 1px solid #d1d5db; display: flex; align-items: center; justify-content: center;
        height: 60px; margin-bottom: 5px;
    }
    .sub-label-text {
        text-align: center; font-size: 1.0em; font-weight: 700; color: #111;
        margin-bottom: 8px; height: 25px; display: flex; align-items: center; justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# 사이드바 설정 (중장기 목표 입력 삭제)
st.sidebar.header("📍 지표 기본 설정")
indicator_name = st.sidebar.text_input("지표명", value="주요사업 성과지표")
weight = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
direction = st.sidebar.selectbox("지표 방향", ["상향", "하향"])
global_perf = st.sidebar.number_input("글로벌 실적(비교군 평균)", value=140.000, format="%.3f")

# 1. 실적 데이터 입력 섹션
st.subheader("1. 실적 데이터 입력")

header_cols = st.columns([6, 1, 1, 1])
with header_cols[0]: st.markdown('<div class="main-header-box">과거 5개년 실적</div>', unsafe_allow_html=True)
with header_cols[1]: st.markdown('<div class="main-header-box">과거 3개년 평균</div>', unsafe_allow_html=True)
with header_cols[2]: st.markdown('<div class="main-header-box">기준치</div>', unsafe_allow_html=True)
with header_cols[3]: st.markdown('<div class="main-header-box">2026년 예상실적</div>', unsafe_allow_html=True)

data_cols = st.columns(9)

hist_raw = []
for i, year in enumerate(past_years):
    with data_cols[i]:
        st.markdown(f'<div class="sub-label-text">{year}년</div>', unsafe_allow_html=True)
        val = st.number_input(f"{year}실적", label_visibility="collapsed", value=100.000 + (i*5), format="%.3f", key=f"h_{i}")
        hist_raw.append(val)

valid_hist = [v for v in hist_raw if v > 0]
std_val = np.std(valid_hist) if len(valid_hist) > 1 else 0.000
avg_3y = np.mean(hist_raw[-3:])
last_year_val = hist_raw[-1]
base_val = max(avg_3y, last_year_val) if direction == "상향" else min(avg_3y, last_year_val)

with data_cols[5]:
    st.markdown('<div class="sub-label-text">과거 표준편차</div>', unsafe_allow_html=True)
    st.text_input("표준편차", value=f"{std_val:.3f}", label_visibility="collapsed", disabled=True)
with data_cols[6]:
    st.markdown('<div class="sub-label-text">&nbsp;</div>', unsafe_allow_html=True) 
    st.text_input("평균", value=f"{avg_3y:.3f}", label_visibility="collapsed", disabled=True)
with data_cols[7]:
    st.markdown('<div class="sub-label-text">&nbsp;</div>', unsafe_allow_html=True)
    st.text_input("기준치", value=f"{base_val:.3f}", label_visibility="collapsed", disabled=True)
with data_cols[8]:
    st.markdown('<div class="sub-label-text">&nbsp;</div>', unsafe_allow_html=True)
    est = st.number_input("예상실적", value=base_val * 1.05, format="%.3f", label_visibility="collapsed")

# --- 분석 실행 ---
st.markdown("---")
if st.button("🚀 모든 평가방법 통합 분석 실행"):
    
    if direction == "상향":
        methods_data = [
            ("목표부여(2편차)", base_val + 2*std_val, base_val - 2*std_val),
            ("목표부여(1편차)", base_val + 1*std_val, base_val - 2*std_val),
            ("목표부여(120%)", base_val * 1.200, base_val * 0.800),
            ("목표부여(110%)", base_val * 1.100, base_val * 0.800),
            ("글로벌 실적비교", global_perf, base_val - 2*std_val)
        ]
    else: # 하향 지표
        methods_data = [
            ("목표부여(2편차)", base_val - 2*std_val, base_val + 2*std_val),
            ("목표부여(1편차)", base_val - 1*std_val, base_val + 2*std_val),
            ("목표부여(120%)", base_val * 0.800, base_val * 1.200),
            ("목표부여(110%)", base_val * 0.900, base_val * 1.200),
            ("글로벌 실적비교", global_perf, base_val + 2*std_val)
        ]

    results = []
    for m_name, hi, lo in methods_data:
        # 평점 산식: 20 + 80 * {(실적-최저)/(최고-최저)}
        if hi == lo:
            score = 60.000
        else:
            score = 20 + 80 * ((est - lo) / (hi - lo))
        
        score = max(20.0, min(100.0, score))
        weighted_score = (score / 100) * weight
        stretch = abs(hi - base_val) / base_val * 100
        
        results.append({
            "평가방법": m_name, "최고목표": round(hi, 3), "최저목표": round(lo, 3),
            "도전성(%)": round(stretch, 3), "예상평점": round(score, 3), "예상득점": round(weighted_score, 3)
        })
    
    df = pd.DataFrame(results)
    st.subheader("2. 평가방법별 비교 분석 결과")
    st.dataframe(df.style.format({k: "{:.3f}" for k in df.columns if k != "평가방법"}).highlight_max(axis=0, subset=['예상평점']), use_container_width=True)

    # 그래프 시각화
    fig, ax = plt.subplots(figsize=(10, 4))
    x = np.arange(len(df))
    ax.bar(x - 0.2, df['최고목표'], 0.4, label='최고목표', color='skyblue')
    ax.bar(x + 0.2, df['최저목표'], 0.4, label='최저목표', color='lightgrey')
    ax.axhline(base_val, color='red', linestyle='--', label='기준치')
    ax.set_xticks(x)
    ax.set_xticklabels(df['평가방법'], rotation=45)
    ax.legend()
    st.pyplot(fig)
