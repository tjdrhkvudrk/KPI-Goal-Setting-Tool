import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats
import io

# 1. 페이지 설정
st.set_page_config(page_title="경평 목표설정 통합 도구", layout="wide")
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
    
    st.header("⚙️ 지표 성격 설정")
    # 3가지 선택지 제공
    ind_type = st.radio("지표 유형 선택", ["상향지표 (실적↑ 좋음)", "하향지표 (실적↓ 좋음)", "일반지표 (평점산식 미적용)"])
    
    st.header("🎯 목표 자동 산출 설정")
    target_logic = st.selectbox("목표치 산출 기준 선택", 
                                ["목표부여(2편차) 기반", "추세치 분석 기반", "중장기 로드맵 기반", "글로벌 평균 기반"])

# 3. 핵심 계산 엔진
Y = np.array(y_vals)
X = np.array([1, 2, 3, 4, 5])
avg_5yr = np.mean(Y)
std_val = np.std(Y, ddof=1)
# 최근실적과 3개년 평균 중 유리한 값 선택
base_val = max(Y[-1], np.mean(Y[-3:])) if "상향" in ind_type else min(Y[-1], np.mean(Y[-3:]))

# 평가방법별 목표치 계산
m_2sig = base_val + (2 * std_val if "상향" in ind_type else -2 * std_val)
slope, intercept, _, _, _ = stats.linregress(X, Y)
trend_2026 = intercept + slope * 6
long_term_goal = base_val * 1.1 # 예시 로직

# 선택된 로직에 따른 목표치 자동 설정
if "2편차" in target_logic:
    auto_goal = m_2sig
elif "추세치" in target_logic:
    auto_goal = trend_2026
else:
    auto_goal = long_term_goal

# 도전성 zp 계산
y_hat = intercept + slope * X
s_resid = np.sqrt(np.sum((Y - y_hat)**2) / (5 - 2))
S_val = max(s_resid * np.sqrt(1 + (1/5) + ((6-3)**2 / np.sum((X-3)**2))), 0.0001)
zp = (auto_goal - trend_2026) / S_val if "상향" in ind_type else (trend_2026 - auto_goal) / S_val
challenge_score = (zp / 2.0) * 100

# 평점 산출 (지표 성격에 따름)
goal_high = m_2sig
goal_low = base_val - (2 * std_val if "상향" in ind_type else -2 * std_val)

if "상향" in ind_type:
    est_score = 20 + 80 * ((auto_goal - goal_low) / (goal_high - goal_low))
elif "하향" in ind_type:
    est_score = 20 + 80 * ((goal_high - auto_goal) / (goal_high - goal_low))
else:
    est_score = 100.0 # 일반지표는 기본 100점 가정

est_score = np.clip(est_score, 20, 100)

# 4. 화면 출력
col_main, col_side = st.columns([3, 1])

with col_main:
    tab1, tab2 = st.tabs(["📈 시뮬레이션 결과", "📋 종합 결과표"])
    
    with tab1:
        st.subheader(f"🏁 평가방법별 산출치 (현재 목표: {auto_goal:.3f})")
        methods_df = pd.DataFrame({
            "평가방법": ["목표부여(2편차)", "목표부여(1편차)", "추세치 분석", "중장기 로드맵"],
            "산출 목표치": [m_2sig, base_val + std_val, trend_2026, long_term_goal]
        })
        st.table(methods_df.style.format({"산출 목표치": "{:.3f}"}))
        
        # 그래프
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist_years, y=Y, name="과거 실적", mode='lines+markers'))
        fig.add_trace(go.Scatter(x=[2026], y=[auto_goal], name="자동 산출 목표", marker=dict(size=12, color='red', symbol='star')))
        st.plotly_chart(fig, use_container_width=True)

with col_side:
    st.subheader("🚩 도전성 범주")
    # 5단계 범주 표시 전용 UI
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
    
    # 내 결과 표시
    if challenge_score >= 100: status, color = "🏆 한계 혁신", "green"
    elif challenge_score >= 50: status, color = "🔥 적극 상향", "blue"
    elif challenge_score >= 25: status, color = "📈 소극 개선", "orange"
    elif challenge_score >= 0: status, color = "⚖️ 현상 유지", "gray"
    else: status, color = "⚠️ 하향 설정", "red"
    
    st.write("### 내 결과")
    st.title(f":{color}[{status.split()[-1]}]")
    st.metric("도전성 지수", f"{challenge_score:.1f}%")

with tab2:
    st.subheader("📅 상세 시뮬레이션 결과표")
    report_df = pd.DataFrame({
        "사업명": [biz_name], "지표명": [ind_name], "지표성격": [ind_type.split()[0]],
        "기준치": [f"{base_val:.3f}"], "최고목표": [f"{goal_high:.3f}"], "산출목표": [f"{auto_goal:.3f}"],
        "예상평점": [f"{est_score:.2f}"], "예상득점": [f"{(est_score*weight/100):.3f}"]
    })
    st.dataframe(report_df, use_container_width=True)
    
    # 엑셀 다운로드
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        report_df.to_excel(writer, index=False, sheet_name='Result')
    st.download_button(label="📥 엑셀 다운로드", data=output.getvalue(), file_name="KPI_Result.xlsx")
