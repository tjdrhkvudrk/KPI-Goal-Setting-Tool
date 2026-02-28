import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="경영평가 지표 시뮬레이터", layout="wide")

# 현재 연도 기준 설정 (2026년)
current_year = datetime.now().year
past_years = [current_year - i for i in range(5, 0, -1)]  # [2021, 2022, 2023, 2024, 2025]

st.title("⚖️ 경영평가 계량지표 통합 시뮬레이터")
st.markdown(f"""
이 도구는 **{current_year}년** 경영평가를 위해 과거 실적을 기반으로 **7가지 평가방법**을 비교하고, 
가장 도전적인 목표치를 제안하여 담당자의 논리 수립을 돕습니다.
""")

# 사이드바: 기본 설정
st.sidebar.header("📍 지표 기본 설정")
indicator_name = st.sidebar.text_input("지표명", value="주요사업 성과지표")
weight = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
direction = st.sidebar.selectbox("지표 방향", ["상향", "하향"])
long_term_goal = st.sidebar.number_input("중장기 목표(Y+3)", value=160.000, format="%.3f")
global_perf = st.sidebar.number_input("글로벌 실적(비교군 평균)", value=140.000, format="%.3f")

# 1. 실적 데이터 입력 섹션
st.subheader("1. 실적 데이터 입력")

# 상단 헤더 행 (과거 5개년 실적 통합 헤더 스타일 구현)
st.markdown("""
<style>
    .header-box {
        background-color: #f0f2f6;
        padding: 5px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 5px;
    }
</style>
<div class="header-box">과거 5개년 실적</div>
""", unsafe_allow_html=True)

# 열 구성: 과거 5개년(5) + 표준편차(1) + 3개년 평균(1) + 기준치(1) + 당해예상(1) = 총 9개 열
cols = st.columns(9)

# 실적 입력 (2021~2025)
hist = []
for i, year in enumerate(past_years):
    with cols[i]:
        val = st.number_input(f"{year}년", value=100.000 + (i*5), format="%.3f")
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

# 계산된 통계치 출력 (수정 불가형태)
with cols[5]:
    st.text_input("5개년 표준편차", value=f"{std_5y:.3f}", disabled=True)
with cols[6]:
    st.text_input("3개년 평균", value=f"{avg_3y:.3f}", disabled=True)
with cols[7]:
    st.text_input("기준치", value=f"{base_val:.3f}", disabled=True)

# 당해연도 예상실적 기입
with cols[8]:
    est = st.number_input(f"{current_year}년 예상실적", value=base_val * 1.05, format="%.3f")

if st.button("🚀 모든 평가방법 통합 분석 실행"):
    # 추세치 계산
    years_idx = np.array([1, 2, 3, 4, 5])
    slope, intercept = np.polyfit(years_idx, hist, 1)
    trend_base = slope * 6 + intercept 
    
    # 중장기 목표치 계산 (Y+3 목표로 향하는 선형 단계)
    lt_base = base_val + (long_term_goal - base_val) / 4

    # 7종 평가방법 리스트
    methods = [
        ("목표부여(2편차)", base_val + 2*std_5y, base_val - 2*std_5y),
        ("목표부여(1편차)", base_val + 1*std_5y, base_val - 1*std_5y),
        ("목표부여(120%)", base_val * 1.2, base_val * 0.8),
        ("목표부여(110%)", base_val * 1.1, base_val * 0.9),
        ("중장기 목표부여", lt_base * 1.05, lt_base * 0.95),
        ("글로벌 실적비교", global_perf * 1.05, global_perf * 0.95),
        ("추세치 평가", trend_base + std_5y, trend_base - std_5y)
    ]
    
    results = []
    for m_name, hi, lo in methods:
        if direction == "하향": hi, lo = lo, hi
        # 평점(Score) 계산
        score = max(20.0, min(100.0, 20 + 80 * (est - lo) / (hi - lo)))
        # 가중치를 곱한 최종 득점
        weighted_score = (score / 100) * weight
        # 도전성(%)
        stretch = abs(hi - base_val) / base_val * 100
        
        results.append({
            "평가방법": m_name, 
            "최고목표(S)": round(hi, 3), 
            "도전성(%)": round(stretch, 3), 
            "예상평점": round(score, 3),
            "예상득점": round(weighted_score, 3)
        })
    
    df = pd.DataFrame(results)
    
    # 최적 및 최고 난이도 판별
    most_difficult = df.loc[df['최고목표(S)'].idxmax()] if direction == "상향" else df.loc[df['최고목표(S)'].idxmin()]
    
    # 결과 출력
    st.subheader("2. 평가방법별 비교 분석 결과")
    st.dataframe(df.style.format({
        "최고목표(S)": "{:.3f}",
        "도전성(%)": "{:.3f}%",
        "예상평점": "{:.3f}",
        "예상득점": "{:.3f}"
    }).highlight_max(axis=0, subset=['예상평점']), use_container_width=True)

    # 시각화
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(df['평가방법'], df['최고목표(S)'], color='skyblue')
    ax.axhline(base_val, color='red', linestyle='--', label=f'기준치({base_val:.3f})')
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height, f'{height:.3f}', ha='center', va='bottom', fontsize=9)

    ax.set_title("평가방법별 S등급 목표치 비교")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # 보고서 논리
    st.subheader("3. 경영평가 보고서용 소명 논리")
    st.info(f"""
    **[도전성 소명 문구]** 본 기관은 {indicator_name} 지표의 목표 설정을 위해 {len(methods)}개 평가방법을 시뮬레이션 하였습니다. 
    그 결과, 가장 도전적인 수치를 제시하는 **[{most_difficult['평가방법']}]** 방식을 채택하였습니다. 
    이는 기준치({base_val:.3f}) 대비 **{most_difficult['도전성(%)']:.3f}% 상향**된 **{most_difficult['최고목표(S)']:.3f}**를 S등급 목표로 설정한 것으로, 타 방식 대비 가장 엄격한 목표입니다.
    """)
