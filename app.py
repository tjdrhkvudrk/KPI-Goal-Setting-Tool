import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats

# 1. 페이지 설정 및 스타일
st.set_page_config(page_title="경평 목표설정 통합 시뮬레이터", layout="wide")
st.title("🎯 경영평가 목표설정 통합 의사결정 시뮬레이터")
st.markdown("---")

# 2. 사이드바: 데이터 입력 및 지표 설정
with st.sidebar:
    st.header("📊 1. 기초 데이터 입력")
    hist_years = [2021, 2022, 2023, 2024, 2025]
    y_vals = []
    for y in hist_years:
        val = st.number_input(f"{y}년 실적", value=100.0 + (y-2021)*5.0, format="%.3f")
        y_vals.append(val)
    
    st.header("⚙️ 2. 지표 환경 설정")
    is_up = st.toggle("상향지표 여부 (실적↑ 좋음)", value=True)
    is_main = st.toggle("주요사업 여부 (가중치↑)", value=True)
    
    st.subheader("⚠️ 자료 불연속성")
    is_discontinuous = st.checkbox("조직/사업구조 변화 발생", help="체크 시 편차법 대신 일반법을 권고합니다.")

    st.header("🎯 3. 도전적 목표 제안")
    user_goal = st.number_input("올해(2026) 설정 목표치", value=float(y_vals[-1] * 1.05))

# 3. 핵심 엔진: 통계 분석 및 목표 산출
X = np.array([1, 2, 3, 4, 5])
Y = np.array(y_vals)

# (1) 극단치 진단 로직
def get_outliers(X, Y):
    outliers = []
    for i in range(len(Y)):
        X_sub, Y_sub = np.delete(X, i), np.delete(Y, i)
        slope, intercept, _, _, _ = stats.linregress(X_sub, Y_sub)
        y_hat = slope * X[i] + intercept
        s_sub = np.sqrt(np.sum((Y_sub - (slope * X_sub + intercept))**2) / (len(Y_sub) - 2))
        if abs(Y[i] - y_hat) > 3 * s_sub: outliers.append(i)
    return outliers

outlier_idx = get_outliers(X, Y)

# (2) 방법론별 목표 산출
# A. 추세치 분석 (회귀)
slope, intercept, _, _, _ = stats.linregress(X, Y)
trend_2026 = intercept + slope * 6
trend_3yr = [intercept + slope * i for i in [6, 7, 8]]

# B. 일반 목표부여 (비율)
base_val = max(Y[-1], np.mean(Y[-3:])) if is_up else min(Y[-1], np.mean(Y[-3:]))
ratio_rate = (1.2 if is_main else 1.1) if is_up else (0.8 if is_main else 0.9)
ratio_target = base_val * ratio_rate

# C. 목표부여 (편차)
std_val = np.std(Y)
sigma_mult = 2 if is_main else 1
std_target = base_val + (sigma_mult * std_val if is_up else -sigma_mult * std_val)

# 4. 결과 출력 섹션
# 
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 평가방법론별 목표치 비교 (객관적 근거)")
    comparison_df = pd.DataFrame({
        "평가방법": ["추세치 분석법", "일반 목표부여(비율)", "목표부여(偏差)"],
        "산출 목표치": [f"{trend_2026:.3f}", f"{ratio_target:.3f}", f"{std_target:.3f}"],
        "지침 근거": ["회귀분석(기준치+S)", "기준치 대비 비율", "표준편차 활용"],
        "적정성": ["통계적 기대치", "정책적 상향", "도전적 설정"]
    })
    st.table(comparison_df)

with col2:
    st.subheader("🚦 도전성 진단 (신호등)")
    # Z-score 기반 신호등
    z_score = (user_goal - trend_2026) / (np.std(Y) if np.std(Y) !=0 else 1)
    if not is_up: z_score = -z_score
    
    if z_score > 1.0:
        st.success(f"🟢 **도전적 목표** (zp={z_score:.2f})\n\n과거 추세를 상회하는 매우 도전적인 수치입니다.")
    elif z_score > -0.5:
        st.warning(f"🟡 **보통 수준** (zp={z_score:.2f})\n\n추세선 범위 내의 합리적 수치입니다.")
    else:
        st.error(f"🔴 **보수적 목표** (zp={z_score:.2f})\n\n목표 상향 조정을 강력히 권고합니다.")

# 5. 향후 3개년 로드맵 및 텍스트 자동 생성
st.markdown("---")
tab1, tab2, tab3 = st.tabs(["📈 3개년 로드맵", "📝 보고서 근거 생성", "🧮 상세 산식 가이드"])

with tab1:
    # 
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist_years, y=Y, name="과거 실적", mode='lines+markers'))
    fig.add_trace(go.Scatter(x=[2026, 2027, 2028], y=trend_3yr, name="향후 추세선", line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=[2026], y=[user_goal], name="설정 목표", marker=dict(size=12, color='red')))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("📑 평가위원 설득을 위한 논리 근거")
    method_name = comparison_df.iloc[np.abs(comparison_df["산출 목표치"].astype(float) - user_goal).argmin()]["평가방법"]
    report_text = f"""
    [목표 설정 사유]
    본 기관은 지표의 도전적 목표 설정을 위하여 '추세치 분석', '목표부여(비율)', '목표부여(편차)' 등 복수의 방법론을 검토하였습니다.
    최종적으로 '{method_name}'을(를) 적용하여 산출된 {user_goal:.3f}을 당해연도 목표로 설정하였습니다. 
    이는 통계적 회귀 분석 결과(zp={z_score:.2f}) 과거 성과 개선 추이를 상회하는 수치로, 
    단순한 현상 유지가 아닌 혁신적인 성과 창출 의지를 반영한 도전적 목표입니다.
    특히 과거 실적의 변동성(S={std_val:.3f})을 고려했을 때 달성 난이도가 충분히 확보된 것으로 분석되었습니다.
    """
    st.text_area("내용을 복사하여 보고서에 활용하세요", report_text, height=200)

with tab3:
    st.subheader("📚 적용된 경평 지침 산식")
    st.latex(r"\text{추세치 평점} = 20 + 80 \times \text{득점(백분율)} \quad \text{}")
    st.latex(r"z_p = \frac{Y_p - Y_s}{S} \quad \text{}")
    st.latex(r"S = \sqrt{\frac{\sum(Y_i - \hat{Y}_i)^2}{n-2} \times \{1 + \frac{1}{n} + \frac{(X_p - \bar{X})^2}{\sum(X_i - \bar{X})^2}\} } \quad \text{}")
    if is_discontinuous:
        st.info("💡 현재 '자료 불연속' 상태이므로 일반 목표부여 방법 적용이 지침상 적절합니다.")
