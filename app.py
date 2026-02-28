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

# 디자인을 위한 CSS
st.markdown("""
<style>
    .main-header {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        border: 1px solid #d1d5db;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .sub-header {
        background-color: #ffffff;
        padding: 5px;
        text-align: center;
        font-size: 0.9em;
        font-weight: bold;
        border-bottom: 1px solid #d1d5db;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 첫 번째 줄: 제목 행
head_col1, head_col2, head_col3, head_col4 = st.columns([6, 1, 1, 1])

with head_col1:
    st.markdown('<div class="main-header">과거 5개년 실적</div>', unsafe_allow_html=True)
with head_col2:
    st.markdown('<div class="main-header">과거 3개년 평균</div>', unsafe_allow_html=True)
with head_col3:
    st.markdown('<div class="main-header">기준치</div>', unsafe_allow_html=True)
with head_col4:
    st.markdown('<div class="main-header">2026년 예상실적</div>', unsafe_allow_html=True)

# 두 번째 줄: 데이터 입력 행
cols = st.columns(9)

# 과거 5개년 실적 입력 (0~4번 컬럼)
hist = []
for i, year in enumerate(past_years):
    with cols[i]:
        st.markdown(f'<div class="sub-header">{year}년</div>', unsafe_allow_html=True)
        val = st.number_input(f"{year}년 실적", label_visibility="collapsed", value=100.000 + (i*5), format="%.3f")
        hist.append(val)

# 통계 자동 계산
std_5y = np.std(hist)
avg_3y = np.mean(hist[-3:])
last_year_val = hist[-1]

# 기준치 결정 로직
if direction == "상향":
    base_val = max(avg_3y, last_year_val)
else:
    base_val = min(avg_3y, last_year_val)

# 과거 5개년 실적 범주의 마지막: 표준편차 (5번 컬럼)
with cols[5]:
    st.markdown('<div class="sub-header">5개년 표준편차</div>', unsafe_allow_html=True)
    st.text_input("표준편차", value=f"{std_5y:.3f}", label_visibility="collapsed", disabled=True)

# 독립 열들 데이터 표시 (6, 7, 8번 컬럼)
with cols[6]:
    st.text_input("평균값", value=f"{avg_3y:.3f}", label_visibility="collapsed", disabled=True)
with cols[7]:
    st.text_input("기준치값", value=f"{base_val:.3f}", label_visibility="collapsed", disabled=True)
with cols[8]:
    est = st.number_input("예상실적입력", value=base_val * 1.05, format="%.3f", label_visibility="collapsed")

# 분석 실행 버튼
if st.button("🚀 모든 평가방법 통합 분석 실행"):
    lt_base = base_val + (long_term_goal - base_val) / 4

    methods = [
        ("목표부여(2편차)", base_val + 2*std_5y, base_val - 2*std_5y),
        ("목표부여(1편차)", base_val + 1*std_5y, base_val - 1*std_5y),
        ("목표부여(120%)", base_val * 1.200, base_val * 0.800),
        ("목표부여(110%)", base_val * 1.100, base_val * 0.900),
        ("중장기 목표부여", lt_base * 1.050, lt_base * 0.950),
        ("글로벌 실적비교", global_perf * 1.050, global_perf * 0.950)
    ]
    
    results = []
    for m_name, hi, lo in methods:
        if direction == "하향": hi, lo = lo, hi
        score = max(20.0, min(100.0, 20 + 80 * (est - lo) / (hi - lo))) if hi != lo else 60.0
        weighted_score = (score / 100) * weight
        stretch = abs(hi - base_val) / base_val * 100
        
        results.append({
            "평가방법": m_name, "최고목표": round(hi, 3), "최저목표": round(lo, 3),
            "도전성(%)": round(stretch, 3), "예상평점": round(score, 3), "예상득점": round(weighted_score, 3)
        })
    
    df = pd.DataFrame(results)
    most_difficult = df.loc[df['최고목표'].idxmax()] if direction == "상향" else df.loc[df['최고목표'].idxmin()]
    
    st.subheader("2. 평가방법별 비교 분석 결과")
    st.dataframe(df.style.format({
        "최고목표": "{:.3f}", "최저목표": "{:.3f}", "도전성(%)": "{:.3f}%", "예상평점": "{:.3f}", "예상득점": "{:.3f}"
    }).highlight_max(axis=0, subset=['예상평점']), use_container_width=True)

    fig, ax = plt.subplots(figsize=(10, 4))
    x_axis = np.arange(len(df['평가방법']))
    ax.bar(x_axis - 0.2, df['최고목표'], 0.4, label='최고목표', color='skyblue')
    ax.bar(x_axis + 0.2, df['최저목표'], 0.4, label='최저목표', color='lightgrey')
    ax.axhline(base_val, color='red', linestyle='--', label=f'기준치({base_val:.3f})')
    ax.set_xticks(x_axis)
    ax.set_xticklabels(df['평가방법'], rotation=45)
    ax.legend()
    st.pyplot(fig)

    st.subheader("3. 경영평가 보고서용 소명 논리")
    st.info(f"**[도전성 소명 문구]** 본 기관은 {indicator_name} 지표의 목표 설정을 위해 6개 평가방법을 시뮬레이션 하였습니다. 가장 도전적인 수치를 제시하는 **[{most_difficult['평가방법']}]** 방식을 채택하였으며, 이는 기준치({base_val:.3f}) 대비 **{most_difficult['도전성(%)']:.3f}% 상향**된 수준입니다.")
