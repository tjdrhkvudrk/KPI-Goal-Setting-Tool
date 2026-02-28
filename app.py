import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats

# 1. 페이지 설정
st.set_page_config(page_title="경평 목표설정 시뮬레이터", layout="wide")
st.title("🎯 KPI 도전적 목표설정 및 중장기 시뮬레이터")

# 2. 사이드바: 데이터 입력
with st.sidebar:
    st.header("📊 과거 실적 입력")
    y_vals = []
    for i in range(5):
        val = st.number_input(f"{2021+i}년 실적", value=100.0 + (i*5.0), format="%.3f")
        y_vals.append(val)
    
    st.header("⚙️ 지표 설정")
    is_up = st.toggle("상향지표 여부", value=True)
    is_main = st.toggle("주요사업 여부", value=True)
    user_goal = st.number_input("올해(2026) 설정 목표치", value=float(y_vals[-1] * 1.05))

# 3. 계산 엔진
X = np.array([1, 2, 3, 4, 5])
Y = np.array(y_vals)

# A. 추세치 분석
slope, intercept, _, _, _ = stats.linregress(X, Y)
trend_2026 = intercept + slope * 6
# 표준편차 S 산출 (이미지 7 산식 구현)
y_hat = intercept + slope * X
s_resid = np.sqrt(np.sum((Y - y_hat)**2) / (5 - 2))
S_val = s_resid * np.sqrt(1 + (1/5) + ((6 - 3)**2 / np.sum((X - 3)**2)))
zp = (user_goal - trend_2026) / S_val if is_up else (trend_2026 - user_goal) / S_val

# B. 일반/편차 목표부여
base_val = max(Y[-1], np.mean(Y[-3:])) if is_up else min(Y[-1], np.mean(Y[-3:]))
std_val = np.std(Y)
ratio_target = base_val * (1.2 if is_main else 1.1) if is_up else base_val * (0.8 if is_main else 0.9)
sigma_target = base_val + (2 * std_val if is_main else 1 * std_val) if is_up else base_val - (2 * std_val if is_main else 1 * std_val)

# 4. 결과 메인 화면
tab1, tab2, tab3 = st.tabs(["🚀 목표 시뮬레이션", "📝 보고서 텍스트 생성", "🧮 산식 가이드"])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🏁 방법론별 목표치 비교 (객관적 근거)")
        comp_df = pd.DataFrame({
            "평가방법": ["추세치 분석법", "일반 목표부여(비율)", "목표부여(偏差)"],
            "2026 목표치": [trend_2026, ratio_target, sigma_target],
            "근거 지침": ["기준치+표준편차 활용", "최근실적 대비 상향", "과거 변동성 반영"]
        })
        st.table(comp_df.style.format({"2026 목표치": "{:.3f}"}))
        
        # 그래프
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[2021,2022,2023,2024,2025], y=Y, name="과거 실적", mode='lines+markers'))
        future_x = [2026, 2027, 2028]
        future_y = [intercept + slope * i for i in [6, 7, 8]]
        fig.add_trace(go.Scatter(x=future_x, y=future_y, name="향후 추세선", line=dict(dash='dash')))
        fig.add_trace(go.Scatter(x=[2026], y=[user_goal], name="설정 목표치", marker=dict(size=12, color='red')))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🚦 도전성 신호등")
        if zp > 1.0: st.success(f"🟢 도전적 목표 (zp={zp:.2f})")
        elif zp > -0.5: st.warning(f"🟡 보통 수준 (zp={zp:.2f})")
        else: st.error(f"🔴 보수적 목표 (zp={zp:.2f})")
        st.write("**담당자 조언:**")
        st.caption("zp가 1.0 이상이면 과거 추세를 뛰어넘는 도전적 설정으로 평가위원 설득에 유리합니다.")

with tab2:
    st.subheader("📑 보고서용 논리 근거 자동 생성")
    report = f"""[목표 설정 근거]
본 기관은 2026년 목표 설정을 위해 추세치 분석 및 편차법 등 복수의 방법론을 검토하였습니다.
최종적으로 설정한 목표치({user_goal:.3f})는 통계적 추세 분석 결과(zp={zp:.2f}) 과거 성과 개선 흐름을 
상회하는 수치로, 단순한 목표 달성이 아닌 혁신적인 성과 창출 의지를 반영한 도전적인 목표입니다."""
    st.text_area("내용을 복사하여 보고서에 활용하세요", report, height=200)

with tab3:
    st.subheader("🧮 경영평가 주요 산식 (편람 근거)")
    st.markdown("##### 1. 추세치 평가 산식")
    st.latex(r"z_p = \frac{Y_p - Y_s}{S}")
    
    st.markdown("##### 2. 추세치 표준편차(S) 산식")
    st.latex(r"S = \sqrt{\frac{\sum(Y_i - \hat{Y}_i)^2}{n-2} \times \{1 + \frac{1}{n} + \frac{(X_p - \bar{X})^2}{\sum(X_i - \bar{X})^2}\} }")
    
    st.markdown("##### 3. 중장기 단위목표 산식")
    st.latex(r"\alpha = \left| \frac{\text{중장기 목표}(B) - \text{기준목표}(A)}{\text{목표달성기간}(n)} \right|")
    
    st.markdown("##### 4. 목표부여 평점 산식")
    st.latex(r"20 + 80 \times \frac{\text{실적} - \text{최저}}{\text{최고} - \text{최저}}")
