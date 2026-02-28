import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats

# 1. 페이지 설정
st.set_page_config(page_title="경평 목표설정 통합 시뮬레이터", layout="wide")
st.title("🎯 KPI 목표설정 7대 방법론 통합 시뮬레이터")

# 2. 사이드바: 데이터 입력 및 지수 설정
with st.sidebar:
    st.header("📊 기초 데이터 입력")
    hist_years = [2021, 2022, 2023, 2024, 2025]
    y_vals = []
    for y in hist_years:
        val = st.number_input(f"{y}년 실적", value=100.0 + (y-2021)*5.0, format="%.3f")
        y_vals.append(val)
    
    st.header("⚙️ 시뮬레이션 옵션")
    is_up = st.toggle("상향지표 여부 (실적↑ 좋음)", value=True)
    
    st.subheader("📍 중장기/글로벌 기준")
    long_term_goal = st.number_input("중장기 최종 목표치(B)", value=150.0)
    global_top_avg = st.number_input("글로벌 우수기관 평균 실적", value=140.0)
    
    st.header("🎯 내 목표 설정")
    user_goal = st.number_input("2026년 설정 목표치", value=float(y_vals[-1] * 1.05))

# 3. 7대 평가방법론 핵심 엔진
X = np.array([1, 2, 3, 4, 5])
Y = np.array(y_vals)
avg_3yr = np.mean(Y[-3:])
last_val = Y[-1]
base_val = max(last_val, avg_3yr) if is_up else min(last_val, avg_3yr)
std_val = np.std(Y)

# (1) 추세치 분석
slope, intercept, _, _, _ = stats.linregress(X, Y)
trend_2026 = intercept + slope * 6
y_hat = intercept + slope * X
s_resid = np.sqrt(np.sum((Y - y_hat)**2) / (5 - 2))
S_val = s_resid * np.sqrt(1 + (1/5) + ((6 - 3)**2 / np.sum((X - 3)**2)))
zp = (user_goal - trend_2026) / S_val if is_up else (trend_2026 - user_goal) / S_val

# (2) 방법론별 산출
m_2sigma = base_val + (2 * std_val if is_up else -2 * std_val) # 2편차
m_1sigma = base_val + (1 * std_val if is_up else -1 * std_val) # 1편차
m_120 = base_val * (1.2 if is_up else 0.8) # 120%
m_110 = base_val * (1.1 if is_up else 0.9) # 110%
# 중장기 단위목표 산식
m_longterm = base_val + (abs(long_term_goal - base_val) / 5) # 5년 달성 가정
m_global = global_top_avg # 글로벌 실적비교는 원칙적으로 편차법 적용하나 직관적 비교 위해 평균값 제시

# 4. 결과 출력
tab1, tab2, tab3 = st.tabs(["🚀 7대 방법론 비교", "📝 보고서 근거 생성", "🧮 적용 산식 가이드"])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🏁 목표 설정 시뮬레이션 결과")
        comparison_data = {
            "평가방법론": ["목표부여(2편차)", "목표부여(1편차)", "목표부여(120%)", "목표부여(110%)", "중장기 목표부여", "글로벌 실적비교", "추세치 평가"],
            "산출 목표치": [m_2sigma, m_1sigma, m_120, m_110, m_longterm, m_global, trend_2026],
            "도전성 성격": ["매우 도전적(2σ)", "도전적(1σ)", "정책적 상향(대)", "정책적 상향(소)", "로드맵 연계", "글로벌 수준", "통계적 기대치"]
        }
        df = pd.DataFrame(comparison_data)
        st.table(df.style.format({"산출 목표치": "{:.3f}"}))
        
        # 시각화 그래프
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist_years, y=Y, name="과거 실적", mode='lines+markers'))
        fig.add_trace(go.Scatter(x=[2026], y=[user_goal], name="내 설정치", marker=dict(size=15, color='red', symbol='star')))
        for i, row in df.iterrows():
            fig.add_trace(go.Scatter(x=[2026], y=[row["산출 목표치"]], name=row["평가방법론"], mode='markers'))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🚦 현재 목표 진단")
        if zp > 1.0: st.success(f"🟢 매우 도전적 (zp={zp:.2f})")
        elif zp > 0: st.warning(f"🟡 적정 수준 (zp={zp:.2f})")
        else: st.error(f"🔴 보수적 설정 (zp={zp:.2f})")
        st.write(f"**기준치(과거실적):** {base_val:.3f}")
        st.write(f"**표준편차
