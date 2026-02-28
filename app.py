import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats
import io

# 1. 페이지 설정
st.set_page_config(page_title="경평 목표설정 통합 시뮬레이터", layout="wide")
st.title("🏛️ 경영평가 KPI 목표설정 & 전략적 조언 도구")

# 2. 데이터 입력부 (사이드바)
with st.sidebar:
    st.header("📋 지표 기본 정보")
    biz_name = st.text_input("사업명", value="인체조직 생산사업")
    ind_name = st.text_input("지표명", value="기증자당 혈관 채취 실적")
    weight = st.number_input("가중치", value=5.0)
    
    st.header("📊 실적 데이터 (5개년)")
    hist_years = [2021, 2022, 2023, 2024, 2025]
    y_vals = []
    for i, y in enumerate(hist_years):
        # ipywidgets의 초기값 로직 반영
        val = st.number_input(f"{y}년 실적 (Y-{5-i})", value=100.0 + (i*5), format="%.3f")
        y_vals.append(val)
    
    st.header("⚙️ 지표 성격 및 도전성")
    ind_type = st.radio("지표 유형", ["상향지표 (실적↑ 좋음)", "하향지표 (실적↓ 좋음)", "일반지표 (평점산식 미적용)"])
    
    # ipywidgets의 stretch_rate 반영 [도전적 가산율]
    stretch_rate = st.slider("목표 도전율(%)", min_value=0.0, max_value=20.0, step=0.5, value=2.0)
    current_est = st.number_input("당해 예상실적 (평점 계산용)", value=float(y_vals[-1]*1.05))

# 3. 핵심 계산 엔진
Y = np.array(y_vals)
X = np.arange(1, 6)
avg_3yr = np.mean(Y[-3:])
std_val = np.std(Y, ddof=1)
is_up = "상향" in ind_type

# 기초 기준치 산정 (최근실적 vs 3개년 평균 중 유리한 쪽)
raw_base = max(Y[-1], avg_3yr) if is_up else min(Y[-1], avg_3yr)

# 도전율 반영된 기준치 (Challenged Base) - 주신 코드 로직 반영
stretch_factor = stretch_rate / 100
challenged_base = raw_base * (1 + stretch_factor) if is_up else raw_base * (1 - stretch_factor)

# 4. 7대 평가방법 자동 산출
slope, intercept, _, _, _ = stats.linregress(X, Y)
trend_2026 = intercept + slope * 6

m_results = {
    "목표부여(2편차)": challenged_base + (2 * std_val if is_up else -2 * std_val),
    "목표부여(1편차)": challenged_base + (1 * std_val if is_up else -1 * std_val),
    "목표부여(120%)": challenged_base * (1.2 if is_up else 0.8),
    "목표부여(110%)": challenged_base * (1.1 if is_up else 0.9),
    "중장기 목표부여": challenged_base * 1.15, # 로드맵 가정치
    "글로벌 실적비교": challenged_base * 1.12, # 글로벌 평균 가정치
    "추세치 평가": trend_2026
}

# 도전성 지수(zp) 계산
y_hat = intercept + slope * X
s_resid = np.sqrt(np.sum((Y - y_hat)**2) / (5 - 2))
S_val = max(s_resid * np.sqrt(1 + (1/5) + ((6-3)**2 / np.sum((X-3)**2))), 0.0001)
# 7대 방법 중 현재 '추세치 평가'를 기준으로 도전성 측정
zp = (m_results["목표부여(2편차)"] - trend_2026) / S_val if is_up else (trend_2026 - m_results["목표부여(2편차)"]) / S_val
challenge_score = (zp / 2.0) * 100

# 5. 화면 레이아웃
col_main, col_side = st.columns([3, 1])

with col_main:
    tab1, tab2, tab3 = st.tabs(["📊 시뮬레이션 결과", "📋 종합 결과표", "📚 산식 가이드"])
    
    with tab1:
        st.subheader(f"✅ 7대 평가방법별 목표 산출 (도전율 {stretch_rate}%)")
        res_df = pd.DataFrame({
            "평가방법": m_results.keys(),
            "산출 목표치": m_results.values(),
            "성격": ["최고목표(2σ)", "상위목표(1σ)", "강력상향(120%)", "일반상향(110%)", "로드맵기반", "세계수준", "통계적추세"]
        })
        st.table(res_df.style.format({"산출 목표치": "{:.3f}"}))
        
        # 주신 코드의 전략 조언 로직 반영
        st.info("💡 **전략 조언:** 도전성을 부여했을 때, 표준편차가 큰 지표는 '편차 방식'이, 데이터가 안정적인 지표는 '비율(110/120%) 방식'이 평점 방어에 유리할 수 있습니다.")
        
        # 시각화
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist_years, y=Y, name="과거 실적", mode='lines+markers'))
        fig.add_trace(go.Scatter(x=[2026], y=[m_results["목표부여(2편차)"]], name="최고 목표치(2σ)", marker=dict(size=12, color='red', symbol='star')))
        st.plotly_chart(fig, use_container_width=True)

with col_side:
    st.subheader("🚩 도전성 범주")
    st.markdown("""
    | 단계 | 명칭 | 범위 |
    | :--- | :--- | :--- |
    | <span style='color:green'>5단계</span> | **한계 혁신** | 100%↑ |
    | <span style='color:blue'>4단계</span> | **적극 상향** | 50%↑ |
    | <span style='color:orange'>3단계</span> | **소극 개선** | 25%↑ |
    | <span style='color:gray'>2단계</span> | **현상 유지** | 0%↑ |
    | <span style='color:red'>1단계</span> | **하향 설정** | 0%↓ |
    """)
    st.divider()
    
    # 등급 판정
    if challenge_score >= 100: status, color = "🏆 한계 혁신", "green"
    elif challenge_score >= 50: status, color = "🔥 적극 상향", "blue"
    elif challenge_score >= 25: status, color = "📈 소극 개선", "orange"
    elif challenge_score >= 0: status, color = "⚖️ 현상 유지", "gray"
    else: status, color = "⚠️ 하향 설정", "red"
    
    st.write("### 현재 등급")
    st.title(f":{color}[{status.split()[-1]}]")
    st.metric("도전성 지수", f"{challenge_score:.1f}%")

with tab2:
    st.subheader("📅 상세 시뮬레이션 결과표 (이미지 양식)")
    # 주신 평점 산식 반영
    goal_hi = m_results["목표부여(2편차)"]
    goal_lo = challenged_base - (2 * std_val if is_up else -2 * std_val)
    
    if "일반" in ind_type:
        est_score = 100.0
    else:
        est_score = 20 + 80 * ((current_est - goal_lo) / (goal_hi - goal_lo)) if is_up else 20 + 80 * ((goal_hi - current_est) / (goal_hi - goal_low))
    est_score = np.clip(est_score, 20, 100)

    final_report = pd.DataFrame({
        "사업명": [biz_name], "지표명": [ind_name], "지표성격": [ind_type.split()[0]],
        "기준치": [f"{challenged_base:.3f}"], "최고목표": [f"{goal_hi:.3f}"], "최저목표": [f"{goal_low:.3f}"],
        "예상실적": [f"{current_est:.3f}"], "예상평점": [f"{est_score:.2f}"], "가중치": [weight],
        "예상득점": [f"{(est_score*weight/100):.3f}"]
    })
    st.dataframe(final_report, use_container_width=True)
    
    # 엑셀 다운로드 (xlsxwriter)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        final_report.to_excel(writer, index=False, sheet_name='Result')
    st.download_button(label="📥 시뮬레이션 결과 엑셀 다운로드", data=output.getvalue(), file_name="KPI_Strategy_Result.xlsx")
