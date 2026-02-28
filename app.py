import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats
import io

# 1. 페이지 설정
st.set_page_config(page_title="KPI 시뮬레이터", layout="wide")
st.title("📊 KPI 목표설정 및 도전성 통합 도구")

# 2. 데이터 입력 (사이드바)
with st.sidebar:
    st.header("📋 기본 정보")
    biz_name = st.text_input("사업명", value="인체조직 생산사업")
    ind_name = st.text_input("지표명", value="기증자당 혈관 채취 실적")
    weight = st.number_input("가중치", value=5.0)
    
    # 지표 방향 선택 (상향/하향/일반)
    ind_type = st.radio("지표 성격", ["상향지표", "하향지표", "일반지표"])
    is_up = ind_type == "상향지표"
    
    # 도전적 가산율 (ipywidgets 로직 반영)
    stretch_rate = st.slider("목표 도전율(%)", 0.0, 20.0, 2.0)
    
    st.header("📈 과거 실적 (5개년)")
    hist_years = [2021, 2022, 2023, 2024, 2025]
    y_vals = []
    for i, y in enumerate(hist_years):
        val = st.number_input(f"{y}년 실적", value=100.0 + (i*5), format="%.3f")
        y_vals.append(val)
    
    current_est = st.number_input("당해 예상실적", value=float(y_vals[-1]*1.05))

# 3. 핵심 계산 엔진
Y = np.array(y_vals)
X = np.arange(1, 6)
std_val = np.std(Y, ddof=1)
avg_3yr = np.mean(Y[-3:])

# 기준치 산정 (최근실적과 3개년 평균 중 유리한 값)
raw_base = max(Y[-1], avg_3yr) if is_up else min(Y[-1], avg_3yr)
challenged_base = raw_base * (1 + stretch_rate/100) if is_up else raw_base * (1 - stretch_rate/100)

# 추세치 분석
slope, intercept, r_val, p_val, std_err = stats.linregress(X, Y)
trend_2026 = intercept + slope * 6

# 7대 평가방법 결과
m_results = {
    "목표부여(2편차)": challenged_base + (2 * std_val if is_up else -2 * std_val),
    "목표부여(1편차)": challenged_base + (1 * std_val if is_up else -1 * std_val),
    "목표부여(120%)": challenged_base * (1.2 if is_up else 0.8),
    "목표부여(110%)": challenged_base * (1.1 if is_up else 0.9),
    "중장기 목표부여": challenged_base * 1.15,
    "글로벌 실적비교": challenged_base * 1.12,
    "추세치 평가": trend_2026
}

# 4. 결과 출력 레이아웃
tab1, tab2 = st.tabs(["🚀 시뮬레이션", "📑 결과 리포트"])

with tab1:
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.subheader("🏁 평가방법별 목표치 비교")
        res_df = pd.DataFrame({
            "평가방법": m_results.keys(),
            "산출 목표치": m_results.values()
        })
        st.table(res_df.style.format({"산출 목표치": "{:.3f}"}))
        
        # 그래프 (NameError 방지를 위해 변수 확실히 정의 후 사용)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist_years, y=Y, name="과거 실적", mode='lines+markers'))
        fig.add_trace(go.Scatter(x=[2026], y=[m_results["목표부여(2편차)"]], name="최고목표", marker=dict(size=12, color='red', symbol='star')))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("🚦 도전성 진단")
        # zp 계산 로직 (SyntaxError 수정됨)
        s_resid = np.sqrt(np.sum((Y - (intercept + slope * X))**2) / 3)
        S_val = max(s_resid * np.sqrt(1 + (1/5) + (9/10)), 0.0001)
        zp = (m_results["목표부여(2편차)"] - trend_2026) / S_val if is_up else (trend_2026 - m_results["목표부여(2편차)"]) / S_val
        
        if zp >= 2.0: status, color = "🏆 한계 혁신", "green"
        elif zp >= 1.0: status, color = "🔥 적극 상향", "blue"
        elif zp >= 0.5: status, color = "📈 소극 개선", "orange"
        elif zp >= 0: status, color = "⚖️ 현상 유지", "gray"
        else: status, color = "⚠️ 하향 설정", "red"
        
        st.success(f"현재 등급: {status}")
        st.metric("도전성 지수(zp)", f"{zp:.3f}")

with tab2:
    st.subheader("📅 2026년 경영평가 상세 시뮬레이션 결과표")
    # 이미지 91881c 양식의 모든 컬럼 반영
    goal_hi = m_results["목표부여(2편차)"]
    goal_lo = challenged_base - (2 * std_val if is_up else -2 * std_val)
    est_score = np.clip(20 + 80 * ((current_est - goal_lo) / (goal_hi - goal_lo)) if is_up else 20 + 80 * ((goal_hi - current_est) / (goal_hi - goal_lo)), 20, 100)
    
    final_report = pd.DataFrame({
        "사업명": [biz_name], "지표명": [ind_name], "지표성격": [ind_type],
        "기준치": [f"{challenged_base:.3f}"], "최고목표": [f"{goal_hi:.3f}"], "최저목표": [f"{goal_lo:.3f}"],
        "예상실적": [f"{current_est:.3f}"], "예상평점": [f"{est_score:.2f}"], "가중치": [weight],
        "예상득점": [f"{(est_score*weight/100):.3f}"]
    })
    st.dataframe(final_report, use_container_width=True)
    
    # 엑셀 다운로드 (xlsxwriter 오류 해결)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        final_report.to_excel(writer, index=False, sheet_name='KPI_Result')
    st.download_button("📥 시뮬레이션 결과 엑셀 다운로드", output.getvalue(), "KPI_Strategy_Result.xlsx")
