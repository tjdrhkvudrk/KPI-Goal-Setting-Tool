import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats
import io

# 1. 페이지 설정
st.set_page_config(page_title="KPI 시뮬레이터", layout="wide")
st.title("🏛️ 경영평가 KPI 목표설정 및 도전성 시뮬레이터")

# 2. 데이터 입력 (사이드바)
with st.sidebar:
    st.header("📋 지표 및 도전성 설정")
    biz_name = st.text_input("사업명", value="인체조직 생산사업")
    ind_name = st.text_input("지표명", value="기증자당 혈관 채취 실적")
    weight = st.number_input("가중치", value=5.0)
    
    # 지표 성격 3종 선택
    ind_type = st.radio("지표 성격 선택", ["상향지표", "하향지표", "일반(비대상)"])
    is_up = ind_type == "상향지표"
    
    # 도전율 가산 로직 (ipywidgets 로직 반영)
    stretch_rate = st.slider("목표 도전율(%)", 0.0, 20.0, 2.0)
    
    st.header("📈 과거 실적 (5개년)")
    y_vals = []
    for i in range(5, 0, -1):
        val = st.number_input(f"Y-{i} 실적", value=100.0 + (5-i)*5, format="%.3f")
        y_vals.append(val)
    
    current_est = st.number_input("당해 예상실적 (평점용)", value=float(y_vals[-1]*1.05))

# 3. 계산 엔진 (오류 방지를 위해 변수 선행 정의)
Y = np.array(y_vals)
X = np.arange(1, 6)
avg_3yr = np.mean(Y[-3:])
std_val = np.std(Y, ddof=1)

# 기초 기준치 및 도전적 기준치 산정
if ind_type == "상향지표":
    raw_base = max(Y[-1], avg_3yr)
    challenged_base = raw_base * (1 + stretch_rate/100)
elif ind_type == "하향지표":
    raw_base = min(Y[-1], avg_3yr)
    challenged_base = raw_base * (1 - stretch_rate/100)
else:
    raw_base = Y[-1]
    challenged_base = raw_base

# 7대 평가방법 산출
slope, intercept, _, _, _ = stats.linregress(X, Y)
trend_2026 = intercept + slope * 6

m_results = {
    "목표부여(2편차)": challenged_base + (2 * std_val if is_up else -2 * std_val),
    "목표부여(1편차)": challenged_base + (1 * std_val if is_up else -1 * std_val),
    "목표부여(120%)": challenged_base * (1.2 if is_up else 0.8),
    "목표부여(110%)": challenged_base * (1.1 if is_up else 0.9),
    "중장기 목표부여": challenged_base * 1.15,
    "글로벌 실적비교": challenged_base * 1.12,
    "추세치 평가": trend_2026
}

# 4. 결과 출력
col_main, col_side = st.columns([3, 1])

with col_main:
    tab1, tab2 = st.tabs(["🚀 시뮬레이션", "📑 결과표"])
    with tab1:
        st.subheader("🏁 평가방법별 목표치 비교")
        res_df = pd.DataFrame({"평가방법": m_results.keys(), "산출 목표치": m_results.values()})
        st.table(res_df.style.format({"산출 목표치": "{:.3f}"}))
        
        # 그래프 출력
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[2021,2022,2023,2024,2025], y=Y, name="과거 실적", mode='lines+markers'))
        fig.add_trace(go.Scatter(x=[2026], y=[m_results["목표부여(2편차)"]], name="최고목표", marker=dict(size=12, color='red', symbol='star')))
        st.plotly_chart(fig, use_container_width=True)

with col_side:
    st.subheader("🚩 도전성 5단계")
    st.markdown("""
    | 단계 | 명칭 | 범위 |
    | :--- | :--- | :--- |
    | <span style='color:green'>5</span> | **한계 혁신** | 100%↑ |
    | <span style='color:blue'>4</span> | **적극 상향** | 50%↑ |
    | <span style='color:orange'>3</span> | **소극 개선** | 25%↑ |
    | <span style='color:gray'>2</span> | **현상 유지** | 0%↑ |
    | <span style='color:red'>1</span> | **하향 설정** | 0%↓ |
    """, unsafe_allow_html=True)
    
    # 도전성 지수(zp) 계산 및 등급 판정
    s_resid = np.sqrt(np.sum((Y - (intercept + slope * X))**2) / 3)
    S_val = max(s_resid * np.sqrt(1 + (1/5) + (9/10)), 0.0001)
    zp = (m_results["목표부여(2편차)"] - trend_2026) / S_val if is_up else (trend_2026 - m_results["목표부여(2편차)"]) / S_val
    challenge_score = (zp / 2.0) * 100

    if challenge_score >= 100: status, color = "🏆 한계 혁신", "green"
    elif challenge_score >= 50: status, color = "🔥 적극 상향", "blue"
    elif challenge_score >= 25: status, color = "📈 소극 개선", "orange"
    elif challenge_score >= 0: status, color = "⚖️ 현상 유지", "gray"
    else: status, color = "⚠️ 하향 설정", "red"
    
    st.divider()
    st.write("### 내 등급")
    st.title(f":{color}[{status.split()[-1]}]")
    st.metric("도전성 지수", f"{challenge_score:.1f}%")

with tab2:
    st.subheader("📅 상세 결과 리포트")
    goal_hi = m_results["목표부여(2편차)"]
    goal_lo = challenged_base - (2 * std_val if is_up else -2 * std_val)
    # 평점 산식
    if ind_type == "일반(비대상)":
        est_score = 100.0
    else:
        est_score = np.clip(20 + 80 * ((current_est - goal_lo) / (goal_hi - goal_lo)) if is_up else 20 + 80 * ((goal_hi - current_est) / (goal_hi - goal_lo)), 20, 100)
    
    report_df = pd.DataFrame({
        "사업명": [biz_name], "지표명": [ind_name], "기준치": [f"{challenged_base:.3f}"],
        "최고목표": [f"{goal_hi:.3f}"], "예상평점": [f"{est_score:.2f}"], "예상득점": [f"{(est_score*weight/100):.3f}"]
    })
    st.dataframe(report_df, use_container_width=True)
    
    # 엑셀 다운로드
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        report_df.to_excel(writer, index=False)
    st.download_button("📥 엑셀 다운로드", output.getvalue(), "KPI_Result.xlsx")
