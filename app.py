import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats
import io

# 1. 페이지 레이아웃 설정
st.set_page_config(page_title="KPI 목표 통합 시뮬레이터", layout="wide")
st.title("📊 경영평가 KPI 목표설정 & 전략 시뮬레이터")

# 2. 사이드바: 입력 데이터 및 설정
with st.sidebar:
    st.header("📋 지표 및 도전성 설정")
    biz_name = st.text_input("사업명", value="인체조직 생산사업")
    ind_name = st.text_input("지표명", value="기증자당 혈관 채취 실적")
    weight = st.number_input("가중치", value=5.0)
    
    # 지표 유형 3가지 선택
    ind_type = st.radio("지표 유형", ["상향지표 (실적↑ 좋음)", "하향지표 (실적↓ 좋음)", "일반지표 (산식 미적용)"])
    is_up = "상향" in ind_type
    
    # 도전율 설정 (ipywidgets 로직 반영)
    stretch_rate = st.slider("목표 도전율(%)", 0.0, 20.0, 2.0)
    
    st.header("📈 과거 5개년 실적")
    y_vals = []
    for i in range(5, 0, -1):
        val = st.number_input(f"Y-{i} 실적", value=100.0 + (5-i)*5, format="%.3f")
        y_vals.append(val)
    
    current_est = st.number_input("당해 예상실적 (평점용)", value=float(y_vals[-1]*1.05))

# 3. 핵심 계산 로직
Y = np.array(y_vals)
X = np.arange(1, 6)
avg_3yr = np.mean(Y[-3:])
std_val = np.std(Y, ddof=1)

# 도전적 기준치 산정
if "상향" in ind_type:
    raw_base = max(Y[-1], avg_3yr)
    challenged_base = raw_base * (1 + stretch_rate/100)
elif "하향" in ind_type:
    raw_base = min(Y[-1], avg_3yr)
    challenged_base = raw_base * (1 - stretch_rate/100)
else:
    raw_base = Y[-1]
    challenged_base = raw_base

# 7대 평가방법 목표치 자동 산출
slope, intercept, _, _, _ = stats.linregress(X, Y)
trend_2026 = intercept + slope * 6

m_results = {
    "평가방법": ["목표부여(2편차)", "목표부여(1편차)", "목표부여(120%)", "목표부여(110%)", "중장기 목표부여", "글로벌 실적비교", "추세치 평가"],
    "산출 목표치": [
        challenged_base + (2 * std_val if is_up else -2 * std_val),
        challenged_base + (1 * std_val if is_up else -1 * std_val),
        challenged_base * (1.2 if is_up else 0.8),
        challenged_base * (1.1 if is_up else 0.9),
        challenged_base * 1.15,
        challenged_base * 1.12,
        trend_2026
    ]
}
df_methods = pd.DataFrame(m_results)

# 4. 화면 레이아웃 구성 (메인 vs 우측 범주)
col_main, col_legend = st.columns([3, 1])

with col_main:
    tab1, tab2 = st.tabs(["🚀 시뮬레이션 결과", "📑 상세 결과표"])
    
    with tab1:
        st.subheader(f"✅ 평가방법별 목표 산출 (도전율 {stretch_rate}%)")
        st.table(df_methods.style.format({"산출 목표치": "{:.3f}"}))
        
        # 추세 그래프
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[2021,2022,2023,2024,2025], y=Y, name="과거 실적", mode='lines+markers'))
        fig.add_trace(go.Scatter(x=[2026], y=[m_results["산출 목표치"][0]], name="최고목표(2σ)", marker=dict(size=12, color='red', symbol='star')))
        st.plotly_chart(fig, use_container_width=True)

with col_legend:
    st.subheader("🚩 도전성 범주")
    st.markdown("""
    | 단계 | 명칭 | 범위 |
    | :--- | :--- | :--- |
    | <span style='color:green'>5</span> | **한계 혁신** | 100%↑ |
    | <span style='color:blue'>4</span> | **적극 상향** | 50%↑ |
    | <span style='color:orange'>3</span> | **소극 개선** | 25%↑ |
    | <span style='color:gray'>2</span> | **현상 유지** | 0%↑ |
    | <span style='color:red'>1</span> | **하향 설정** | 0%↓ |
    """, unsafe_allow_html=True)
    
    # 도전성 지수(zp) 기반 등급 판정
    s_resid = np.sqrt(np.sum((Y - (intercept + slope * X))**2) / 3)
    S_val = max(s_resid * np.sqrt(1 + (1/5) + (9/10)), 0.0001)
    zp = (m_results["산출 목표치"][0] - trend_2026) / S_val if is_up else (trend_2026 - m_results["산출 목표치"][0]) / S_val
    challenge_score = (zp / 2.0) * 100

    if challenge_score >= 100: status, color = "🏆 한계 혁신", "green"
    elif challenge_score >= 50: status, color = "🔥 적극 상향", "blue"
    elif challenge_score >= 25: status, color = "📈 소극 개선", "orange"
    elif challenge_score >= 0: status, color = "⚖️ 현상 유지", "gray"
    else: status, color = "⚠️ 하향 설정", "red"
    
    st.divider()
    st.write("### 내 도전성 등급")
    st.title(f":{color}[{status.split()[-1]}]")
    st.metric("도전성 지수", f"{challenge_score:.1f}%")

with tab2:
    st.subheader("📅 경영평가 시뮬레이션 최종 결과표")
    # 이미지 91881c 양식 반영
    goal_hi = m_results["산출 목표치"][0]
    goal_lo = challenged_base - (2 * std_val if is_up else -2 * std_val)
    
    if "일반" in ind_type: est_score = 100.0
    else: est_score = np.clip(20 + 80 * ((current_est - goal_lo) / (goal_hi - goal_lo)) if is_up else 20 + 80 * ((goal_hi - current_est) / (goal_hi - goal_lo)), 20, 100)
    
    report_df = pd.DataFrame({
        "사업명": [biz_name], "지표명": [ind_name], "지표성격": [ind_type.split()[0]],
        "기준치": [f"{challenged_base:.3f}"], "최고목표": [f"{goal_hi:.3f}"], "최저목표": [f"{goal_lo:.3f}"],
        "예상평점": [f"{est_score:.2f}"], "가중치": [weight], "예상득점": [f"{(est_score*weight/100):.3f}"]
    })
    st.dataframe(report_df, use_container_width=True)
    
    # 데이터 복사 및 다운로드
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        report_df.to_excel(writer, index=False)
    st.download_button("📥 엑셀 결과 다운로드", output.getvalue(), "KPI_Sim_Result.xlsx")
