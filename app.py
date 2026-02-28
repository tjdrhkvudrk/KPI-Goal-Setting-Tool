import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats
import io

# 1. 페이지 설정
st.set_page_config(page_title="KPI 목표설정 통합 도구", layout="wide")
st.title("🏛️ 경영평가 KPI 목표설정 및 도전성 통합 시뮬레이터")

# 2. 데이터 입력부 (사이드바)
with st.sidebar:
    st.header("📋 지표 기본 정보")
    biz_name = st.text_input("사업명", value="인체조직 생산사업")
    ind_name = st.text_input("지표명", value="기증자당 혈관 채취 실적")
    weight = st.number_input("가중치", value=5.0)
    
    st.header("📊 실적 데이터 (5개년)")
    hist_years = [2021, 2022, 2023, 2024, 2025]
    y_vals = []
    for y in hist_years:
        val = st.number_input(f"{y}년 실적", value=1.800 + (y-2021)*0.05, format="%.3f")
        y_vals.append(val)
    
    st.header("⚙️ 환경 및 목표")
    is_up = st.toggle("상향지표 여부 (실적↑ 좋음)", value=True)
    user_goal = st.number_input("2026년 설정 목표치", value=float(y_vals[-1] * 1.05))
    long_term_b = st.number_input("중장기 최종 목표(B)", value=float(y_vals[-1] * 1.2))
    global_avg = st.number_input("글로벌 우수기관 평균", value=float(y_vals[-1] * 1.15))

# 3. 핵심 계산 엔진 (Error-Free 로직)
Y = np.array(y_vals)
X = np.array([1, 2, 3, 4, 5])
avg_5yr = np.mean(Y)
std_val = np.std(Y, ddof=1)
base_val = max(Y[-1], np.mean(Y[-3:])) if is_up else min(Y[-1], np.mean(Y[-3:]))

# 추세치 분석 및 ZP 계산
slope, intercept, r_val, p_val, std_err = stats.linregress(X, Y)
trend_2026 = intercept + slope * 6
y_hat = intercept + slope * X
s_resid = np.sqrt(np.sum((Y - y_hat)**2) / (5 - 2))
S_val = max(s_resid * np.sqrt(1 + (1/5) + ((6-3)**2 / np.sum((X-3)**2))), 0.0001)

zp = (user_goal - trend_2026) / S_val if is_up else (trend_2026 - user_goal) / S_val
challenge_score = (zp / 2.0) * 100

# 최고/최저 목표 및 평점 산출
goal_high = base_val + (2 * std_val if is_up else -2 * std_val)
goal_low = base_val - (2 * std_val if is_up else -2 * std_val)
est_score = np.clip(20 + 80 * ((user_goal - goal_low) / (goal_high - goal_low)) if is_up else 20 + 80 * ((goal_high - user_goal) / (goal_high - goal_low)), 20, 100)

# 4. 결과 출력
tab1, tab2, tab3 = st.tabs(["📈 시뮬레이션 결과", "📋 종합 결과표", "📚 산식 가이드"])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🏁 방법론별 목표치 비교")
        methods = {
            "평가방법론": ["목표부여(2편차)", "목표부여(1편차)", "목표부여(120%)", "중장기 목표부여", "글로벌 실적비교", "추세치 평가"],
            "산출 목표치": [goal_high, base_val + std_val, base_val*1.2, base_val + (long_term_b - base_val)/5, global_avg, trend_2026]
        }
        st.table(pd.DataFrame(methods).style.format({"산출 목표치": "{:.3f}"}))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist_years, y=Y, name="과거 실적", mode='lines+markers'))
        fig.add_trace(go.Scatter(x=[2026], y=[user_goal], name="내 설정치", marker=dict(size=12, color='red', symbol='star')))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🚦 도전성 5단계 진단")
        if challenge_score >= 100:
            status, st_func, desc = "🏆 한계 혁신", st.success, "통계적 한계를 돌파한 압도적 성과"
        elif challenge_score >= 50:
            status, st_func, desc = "🔥 적극 상향", st.success, "과거 성과를 뛰어넘는 도전적 설정"
        elif challenge_score >= 25:
            status, st_func, desc = "📈 소극 개선", st.info, "완만한 개선 의지가 반영된 수준"
        elif challenge_score >= 0:
            status, st_func, desc = "⚖️ 현상 유지", st.warning, "과거 추세를 그대로 유지하는 보통 수준"
        else:
            status, st_func, desc = "⚠️ 하향 설정", st.error, "추세보다 낮은 목표로 재검토 권고"
        
        st_func(f"### {status}")
        st.metric("도전성 지수", f"{challenge_score:.1f}%")
        st.write(f"**담당자 조언:** {desc}")

with tab2:
    st.subheader("📅 2026년 경영평가 시뮬레이션 상세 결과표")
    # 이미지 91881c 양식 반영
    report_df = pd.DataFrame({
        "사업명": [biz_name], "지표명": [ind_name], "지표성격": ["상향" if is_up else "하향"],
        "평균실적": [f"{avg_5yr:.3f}"], "표준편차": [f"{std_val:.3f}"], "기준치": [f"{base_val:.3f}"],
        "최고목표": [f"{goal_high:.3f}"], "최저목표": [f"{goal_low:.3f}"], "설정목표": [f"{user_goal:.3f}"],
        "예상평점": [f"{est_score:.2f}"], "가중치": [weight], "예상득점": [f"{(est_score*weight/100):.3f}"]
    })
    st.dataframe(report_df, use_container_width=True)
    
    # 엑셀 다운로드 기능 (xlsxwriter 필수)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        report_df.to_excel(writer, index=False, sheet_name='Result')
    st.download_button(label="📥 시뮬레이션 결과 엑셀 다운로드", data=output.getvalue(), file_name="KPI_Simulation.xlsx")

with tab3:
    st.subheader("🧮 적용 산식 가이드")
    st.latex(r"z_p = \frac{Y_p - Y_s}{S}")
    st.latex(r"S = \sqrt{\frac{\sum(Y_i - \hat{Y_i})^2}{n-2} \times \left[ 1 + \frac{1}{n} + \frac{(X_p - \bar{X})^2}{\sum(X_i - \bar{X})^2} \right]}")
