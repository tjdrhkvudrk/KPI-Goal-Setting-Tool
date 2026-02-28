import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats

# 페이지 설정
st.set_page_config(page_title="경평 목표설정 의사결정 시뮬레이터", layout="wide")
st.title("🏛️ 경영평가 목표설정 통합 의사결정 지원 도구")

# --- 사이드바: 데이터 입력 ---
with st.sidebar:
    st.header("📊 실적 데이터 입력")
    hist_years = [2021, 2022, 2023, 2024, 2025]
    y_vals = []
    for y in hist_years:
        val = st.number_input(f"{y}년 실적", value=100.0 + (y-2021)*5.0, format="%.3f")
        y_vals.append(val)
    
    st.header("⚙️ 설정")
    is_up = st.toggle("상향지표 여부", value=True)
    is_main = st.toggle("주요사업 여부", value=True)
    user_goal = st.number_input("올해(2026) 설정 목표치", value=float(y_vals[-1] * 1.05))

# --- 핵심 계산 엔진 ---
X = np.array([1, 2, 3, 4, 5])
Y = np.array(y_vals)

# 1. 추세치 분석
slope, intercept, _, _, _ = stats.linregress(X, Y)
trend_2026 = intercept + slope * 6
y_hat = intercept + slope * X
s_resid = np.sqrt(np.sum((Y - y_hat)**2) / (len(Y) - 2))
S_val = s_resid * np.sqrt(1 + (1/5) + ((6 - 3)**2 / np.sum((X - 3)**2))) # 간소화 산식
zp = (user_goal - trend_2026) / S_val if is_up else (trend_2026 - user_goal) / S_val

# 2. 일반 목표부여(비율/편차)
base_val = max(Y[-1], np.mean(Y[-3:])) if is_up else min(Y[-1], np.mean(Y[-3:]))
std_val = np.std(Y)
ratio_target = base_val * (1.2 if is_main else 1.1) if is_up else base_val * (0.8 if is_main else 0.9)
sigma_target = base_val + (2 * std_val if is_main else 1 * std_val) if is_up else base_val - (2 * std_val if is_main else 1 * std_val)

# --- 화면 구성 ---
tab1, tab2, tab3 = st.tabs(["🚀 목표 시뮬레이션", "📝 보고서 텍스트 생성", "🧮 산식 및 지침 가이드"])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🏁 방법론별 올해 목표치 비교")
        comp_df = pd.DataFrame({
            "평가방법": ["추세치 분석", "목표부여(비율)", "목표부여(편차)"],
            "산출 목표치": [trend_2026, ratio_target, sigma_target],
            "도전성 성격": ["통계적 추세 반영", "정책적 상향", "과거 변동성 반영"]
        })
        st.table(comp_df.style.format({"산출 목표치": "{:.3f}"}))
        
        # 중장기 로드맵 그래프
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist_years, y=Y, name="과거 실적", mode='lines+markers'))
        future_x = [2026, 2027, 2028]
        future_y = [intercept + slope * i for i in [6, 7, 8]]
        fig.add_trace(go.Scatter(x=future_x, y=future_y, name="향후 추세선", line=dict(dash='dash')))
        fig.add_trace(go.Scatter(x=[2026], y=[user_goal], name="설정 목표", marker=dict(size=12, color='red')))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🚦 도전성 신호등")
        if zp > 1.0: st.success(f"🟢 도전적 (zp={zp:.2f})")
        elif zp > -0.5: st.warning(f"🟡 보통 (zp={zp:.2f})")
        else: st.error(f"🔴 보수적 (zp={zp:.2f})")
        st.info("※ zp값이 높을수록 과거 추세를 뛰어넘는 도전적인 목표임을 의미합니다.")

with tab2:
    st.subheader("📄 평가위원 설득을 위한 논리 근거")
    method_used = "추세치 분석 및 편차법"
    draft = f"""본 기관은 목표 설정의 객관성과 도전성을 확보하기 위해 복수의 평가방법론을 검토하였습니다.
검토 결과, 가장 도전적인 수치인 {user_goal:.3f}을 2026년 목표로 설정하였습니다. 
이는 통계적 추세 분석(zp={zp:.2f}) 결과, 과거의 개선 속도를 상회하는 수준으로 
단순한 목표 달성이 아닌 지속적인 성과 혁신 의지를 반영한 결과입니다."""
    st.text_area("아래 내용을 복사하여 보고서에 활용하세요:", draft, height=200)

with tab3:
    st.subheader("🧮 주요 평가 산식 가이드")
    st.markdown("##### 1. 추세치 평가 산식")
    st.latex(r"z_p = \frac{Y_p - Y_s}{S} \quad \text{}")
    st.image("image_9c013f.png", caption="추세치 표준편차(S) 산식")
    
    st.markdown("##### 2. 평점 산출 구조")
    st.latex(r"20 + 80 \times \frac{\text{실적} - \text{최저}}{\text{최고} - \text{최저}} \quad \text{}")
    
    st.markdown("##### 3. 중장기 단위목표 산식")
    st.image("image_9c04e4.png", caption="중장기 단위목표(α) 산출법")
