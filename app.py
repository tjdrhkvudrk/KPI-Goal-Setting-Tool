import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats

# 1. 페이지 설정
st.set_page_config(page_title="KPI 목표설정 통합 시뮬레이터", layout="wide")
st.title("🎯 KPI 목표설정 7대 방법론 통합 시뮬레이터")

# 2. 사이드바: 데이터 입력 (변수명 정의 확실히)
with st.sidebar:
    st.header("📊 실적 데이터 입력")
    hist_years = [2021, 2022, 2023, 2024, 2025]
    y_vals = []
    for y in hist_years:
        val = st.number_input(f"{y}년 실적", value=100.0 + (y-2021)*5.0, key=f"y_{y}")
        y_vals.append(val)
    
    st.header("⚙️ 지표 환경 설정")
    is_up = st.toggle("상향지표 여부 (실적↑ 좋음)", value=True)
    long_term_goal = st.number_input("중장기 최종 목표치(B)", value=150.0)
    global_top_avg = st.number_input("글로벌 우수기관 평균 실적", value=140.0)
    
    st.header("🎯 내 목표 설정")
    user_goal = st.number_input("2026년 설정 목표치", value=float(y_vals[-1] * 1.05))

# 3. 핵심 계산 엔진 (7대 방법론)
X = np.array([1, 2, 3, 4, 5])
Y = np.array(y_vals) # NameError 방지를 위해 명확히 정의
avg_3yr = np.mean(Y[-3:])
last_val = Y[-1]
base_val = max(last_val, avg_3yr) if is_up else min(last_val, avg_3yr)
std_val = np.std(Y)

# (1) 추세치 분석 및 zp 산출
slope, intercept, r_val, p_val, std_err = stats.linregress(X, Y)
trend_2026 = intercept + slope * 6
y_hat = intercept + slope * X
s_resid = np.sqrt(np.sum((Y - y_hat)**2) / (5 - 2))
S_val = s_resid * np.sqrt(1 + (1/5) + ((6 - 3)**2 / np.sum((X - 3)**2)))
zp = (user_goal - trend_2026) / S_val if is_up else (trend_2026 - user_goal) / S_val

# (2) 7대 방법론 값 계산
m_2sigma = base_val + (2 * std_val if is_up else -2 * std_val)
m_1sigma = base_val + (1 * std_val if is_up else -1 * std_val)
m_120 = base_val * (1.2 if is_up else 0.8)
m_110 = base_val * (1.1 if is_up else 0.9)
m_longterm = base_val + ((long_term_goal - base_val) / 5) # 중장기
m_global = global_top_avg # 글로벌 실적비교

# 4. 메인 화면 출력
tab1, tab2, tab3 = st.tabs(["🚀 7대 방법론 비교", "📝 보고서 근거 생성", "🧮 적용 산식 가이드"])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🏁 평가방법론별 목표치 비교 시뮬레이션")
        comp_data = {
            "평가방법론": ["목표부여(2편차)", "목표부여(1편차)", "목표부여(120%)", "목표부여(110%)", "중장기 목표부여", "글로벌 실적비교", "추세치 평가"],
            "산출 목표치": [m_2sigma, m_1sigma, m_120, m_110, m_longterm, m_global, trend_2026],
            "도전성 성격": ["최상위(2σ) 도전", "상위(1σ) 도전", "정책적 상향(강)", "정책적 상향(약)", "로드맵 기반", "세계 수준", "통계적 추세"]
        }
        st.table(pd.DataFrame(comp_data).style.format({"산출 목표치": "{:.3f}"}))
        
        # 그래프 시각화 (NameError 해결을 위해 hist_years, Y 명시적 사용)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist_years, y=Y, name="과거 실적", mode='lines+markers'))
        fig.add_trace(go.Scatter(x=[2026], y=[user_goal], name="내 설정치", marker=dict(size=12, color='red', symbol='star')))
        for name, val in zip(comp_data["평가방법론"], comp_data["산출 목표치"]):
            fig.add_trace(go.Scatter(x=[2026], y=[val], name=name, mode='markers'))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🚦 도전성 진단")
        # SyntaxError 해결: f-string 따옴표와 줄바꿈 교정
        if zp > 1.0:
            st.success(f"🟢 도전적 목표 (zp={zp:.2f})")
        elif zp > 0:
            st.warning(f"🟡 보통 수준 (zp={zp:.2f})")
        else:
            st.error(f"🔴 보수적 설정 (zp={zp:.2f})")
        st.write(f"**기준치:** {base_val:.3f}")
        st.write(f"**표준편차(S):** {S_val:.3f}")

with tab2:
    st.subheader("📑 평가위원 설득을 위한 논리 근거")
    report = f"""[목표 설정 근거]
본 기관은 2026년 목표의 객관성과 도전성을 확보하기 위해 7가지 대안 모델을 시뮬레이션하였습니다. 
최종 설정치({user_goal:.3f})는 추세치 분석 결과(zp={zp:.2f}) 과거 성과 개선 흐름을 상회하며, 
중장기 로드맵 및 글로벌 우수기관 수준을 종합적으로 반영한 도전적인 수치입니다."""
    st.text_area("내용을 복사하여 보고서에 활용하세요", report, height=180)

with tab3:
    st.subheader("🧮 경영평가 주요 산식")
    st.markdown("##### 1. 추세치 표준화 지수(zp)")
    st.latex(r"z_p = \frac{Y_p - Y_s}{S}")
    st.markdown("##### 2. 추세치 표준편차(S)")
    st.latex(r"S = \sqrt{\frac{\sum(Y_i - a - bX_i)^2}{n-2} \times \{1 + \frac{1}{n} + \frac{(X_p - \bar{X})^2}{\sum(X_i - \bar{X})^2}\} }")
    st.markdown("##### 3. 중장기 단위목표 산식")
    st.latex(r"\alpha = \left| \frac{B - A}{n} \right|")
