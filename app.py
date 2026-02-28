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

# 사이드바: 기본 설정
st.sidebar.header("📍 지표 기본 설정")
indicator_name = st.sidebar.text_input("지표명", value="주요사업 성과지표")
weight = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
direction = st.sidebar.selectbox("지표 방향", ["상향", "하향"])
long_term_goal = st.sidebar.number_input("중장기 목표(Y+3)", value=160.000, format="%.3f")

# 메인화면: 실적 입력
st.subheader("1. 실적 데이터 입력")
col1, col2, col3, col4, col5, col6 = st.columns(6)
# format="%.3f"를 추가하여 입력창에서도 소수점 셋째 자리까지 표시되도록 설정
with col1: y5 = st.number_input("Y-5 실적", value=100.000, format="%.3f")
with col2: y4 = st.number_input("Y-4 실적", value=105.000, format="%.3f")
with col3: y3 = st.number_input("Y-3 실적", value=110.000, format="%.3f")
with col4: y2 = st.number_input("Y-2 실적", value=115.000, format="%.3f")
with col5: y1 = st.number_input("Y-1 실적", value=120.000, format="%.3f")
with col6: est = st.number_input("당해 예상실적", value=130.000, format="%.3f")

hist = [y5, y4, y3, y2, y1]

if st.button("🚀 모든 방법론 통합 분석 실행"):
    # 기초 통계 계산
    avg_3y = sum(hist[-3:]) / 3
    std_5y = np.std(hist)
    base = max(hist[-1], avg_3y) if direction == "상향" else min(hist[-1], avg_3y)
    
    # 추세치 및 중장기
    years = np.array([1, 2, 3, 4, 5])
    slope, intercept = np.polyfit(years, hist, 1)
    trend_base = slope * 6 + intercept 
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
        # 평점(Score) 계산
        score = max(20.0, min(100.0, 20 + 80 * (est - lo) / (hi - lo)))
        # 가중치를 곱한 최종 득점
        weighted_score = (score / 100) * weight
        # 도전성(%)
        stretch = abs(hi - base) / base * 100
        
        results.append({
            "방법론": m_name, 
            "최고목표(S)": round(hi, 3), 
            "도전성(%)": round(stretch, 3), 
            "예상평점": round(score, 3),
            "예상득점": round(weighted_score, 3)
        })
    
    df = pd.DataFrame(results)
    
    # 최적 및 최고 난이도 판별
    if direction == "상향":
        most_difficult = df.loc[df['최고목표(S)'].idxmax()]
    else:
        most_difficult = df.loc[df['최고목표(S)'].idxmin()]
    
    # 결과 출력
    st.subheader("2. 방법론별 비교 분석 결과")
    # 표에서 모든 숫자를 소수점 셋째 자리까지 고정 표시
    st.dataframe(df.style.format({
        "최고목표(S)": "{:.3f}",
        "도전성(%)": "{:.3f}%",
        "예상평점": "{:.3f}",
        "예상득점": "{:.3f}"
    }).highlight_max(axis=0, subset=['예상평점']))

    # 시각화
    fig, ax = plt.subplots(figsize=(10, 4))
    bars = ax.bar(df['방법론'], df['최고목표(S)'], color='skyblue')
    ax.axhline(base, color='red', linestyle='--', label=f'기준치({base:.3f})')
    
    # 막대 그래프 상단에 수치 표시
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom')

    ax.set_title("방법론별 S등급 목표치 비교")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # 보고서 논리
    st.subheader("3. 경영평가 보고서용 소명 논리")
    st.info(f"""
    **[도전성 소명 문구]** 본 기관은 {indicator_name} 지표의 목표 설정을 위해 6개 평가 방법론을 시뮬레이션 하였습니다. 
    그 결과, 가장 도전적인 수치를 제시하는 **[{most_difficult['방법론']}]** 방식을 채택하였습니다. 
    이는 기준치({base:.3f}) 대비 **{most_difficult['도전성(%)']:.3f}% 상향**된 **{most_difficult['최고목표(S)']:.3f}**를 S등급 목표로 설정한 것으로, 타 방식 대비 가장 엄격한 목표입니다.
    """)
