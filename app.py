import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(page_title="경영평가 지표 시뮬레이터", layout="wide")

st.title("⚖️ 경영평가 계량지표 통합 시뮬레이터")
st.markdown("""
이 도구는 과거 실적을 기반으로 **6가지 평가방법**을 비교하고, 
가장 도전적인 목표치를 제안하여 담당자의 논리 수립을 돕습니다.
""")

# 메인화면: 실적 데이터 입력
st.subheader("1. 과거 실적 데이터 입력 (Y-5 ~ Y-1)")
col1, col2, col3, col4, col5 = st.columns(5)
with col1: y5 = st.number_input("Y-5 실적", value=100.000, format="%.3f", step=0.001)
with col2: y4 = st.number_input("Y-4 실적", value=105.000, format="%.3f", step=0.001)
with col3: y3 = st.number_input("Y-3 실적", value=110.000, format="%.3f", step=0.001)
with col4: y2 = st.number_input("Y-2 실적", value=115.000, format="%.3f", step=0.001)
with col5: y1 = st.number_input("Y-1 실적", value=120.000, format="%.3f", step=0.001)

hist = [y5, y4, y3, y2, y1]
years = np.array([1, 2, 3, 4, 5])
slope, intercept = np.polyfit(years, hist, 1)

# [수정 포인트] 명칭 변경: 중장기 목표치(3년 후 추정 목표치)
suggested_lt_goal = slope * 8 + intercept

# 사이드바: 기본 설정
st.sidebar.header("📍 지표 및 목표 설정")
indicator_name = st.sidebar.text_input("지표명", value="주요사업 성과지표")
weight = st.sidebar.number_input("가중치", value=5.0)
direction = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

st.sidebar.markdown(f"---")
# 요청하신 문구로 수정되었습니다.
st.sidebar.write(f"💡 **중장기 목표치(3년 후 추정 목표치): {suggested_lt_goal:.3f}**")
long_term_goal = st.sidebar.number_input("중장기 목표 설정", value=float(suggested_lt_goal), format="%.3f", step=0.001)

# 당해 예상실적 입력
st.markdown("---")
st.subheader("2. 올해(당해) 예상 실적")
est = st.number_input("당해 연도 예상 실적(평가 대상)", value=slope * 6 + intercept, format="%.3f", step=0.001)

if st.button("🚀 모든 방법론 통합 분석 실행"):
    # 기초 통계 계산
    avg_3y = sum(hist[-3:]) / 3
    std_5y = np.std(hist)
    base = max(hist[-1], avg_3y) if direction == "상향" else min(hist[-1], avg_3y)
    
    # 추세치 (Y+1 시점)
    trend_base = slope * 6 + intercept 
    # 중장기 기반 당해 목표 산식
    lt_base = base + (long_term_goal - base) / 4

    # 6종 방법론 리스트
    methods = [
        ("목표부여(2편차)", base + 2*std_5y, base - 2*std_5y),
        ("목표부여(1편차)", base + 1*std_5y, base - 1*std_5y),
        ("목표부여(120%)", base * 1.2, base * 0.8),
        ("목표부여(110%)", base * 1.1, base * 0.9),
        ("추세치 평가", trend_base + std_5y, trend_base - std_5y),
        ("중장기 목표부여", lt_base * 1.05, lt_base * 0.95)
    ]
    
    results = []
    for m_name, hi, lo in methods:
        if direction == "하향": hi, lo = lo, hi
        denom = (hi - lo) if (hi - lo) != 0 else 1
        score = max(20.0, min(100.0, 20 + 80 * (est - lo) / denom))
        stretch = abs(hi - base) / base * 100 if base != 0 else 0
        results.append({"방법론": m_name, "최고목표(S)": round(hi, 3), "도전성(%)": round(stretch, 1), "예상평점": round(score, 2)})
    
    df = pd.DataFrame(results)
    
    if direction == "상향":
        most_difficult = df.loc[df['최고목표(S)'].idxmax()]
    else:
        most_difficult = df.loc[df['최고목표(S)'].idxmin()]
    
    st.subheader("3. 방법론별 비교 분석 결과")
    st.dataframe(df.style.format({"최고목표(S)": "{:.3f}"}).highlight_max(axis=0, subset=['예상평점']))

    # 시각화
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(df['방법론'], df['최고목표(S)'], color='skyblue')
    ax.axhline(base, color='red', linestyle='--', label=f'기준치({base:.3f})')
    ax.set_title("방법론별 S등급 목표치 비교")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    st.subheader("4. 경영평가 보고서용 소명 논리")
    st.info(f"""
    **[도전성 소명 문구]** 본 기관은 {indicator_name} 지표의 목표 설정을 위해 6개 평가 방법론을 시뮬레이션 하였습니다. 
    과거 5개년 실적 추세를 반영한 중장기 목표치({long_term_goal:.3f})를 연계하여 산출한 결과, 
    가장 도전적인 수치를 제시하는 **[{most_difficult['방법론']}]** 방식을 채택하였습니다. 
    이는 기준치 대비 **{most_difficult['도전성(%)']}% 상향**된 수준으로, 타 방식 대비 가장 엄격한 목표입니다.
    """)
