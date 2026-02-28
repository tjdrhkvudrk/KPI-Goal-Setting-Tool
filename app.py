import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats
import io

# 1. 화면 스타일 및 서식 설정
st.set_page_config(page_title="KPI 목표 시뮬레이터", layout="wide")
st.title("🎯 도전적 목표 설정 및 평점 통합 시뮬레이터")

# 2. 입력부 (사이드바)
with st.sidebar:
    st.header("1. 지표 기본정보 및 도전성")
    biz_name = st.text_input("사업명", value="인체조직 생산사업")
    ind_name = st.text_input("지표명", value="기증자당 혈관 채취 실적")
    weight = st.number_input("가중치", value=5.0)
    direction = st.selectbox("지표 방향", ["상향", "하향", "일반(비대상)"])
    
    # ipywidgets의 stretch_rate 로직 반영
    stretch_rate = st.slider("목표 도전율(%)", 0.0, 20.0, 2.0, help="기준치에 추가할 도전적 가산율입니다.")
    
    st.header("2. 과거 실적 및 예상치")
    hist_years = [2021, 2022, 2023, 2024, 2025]
    y_vals = []
    for i, year in enumerate(hist_years):
        # ipywidgets의 초기값 로직(100 + i*5) 유지
        val = st.number_input(f"{year}년 실적(Y-{5-i})", value=100.0 + (i*5), format="%.3f")
        y_vals.append(val)
    
    current_estimated = st.number_input("당해 예상실적", value=float(y_vals[-1]*1.05))

# 3. 핵심 계산 엔진
Y = np.array(y_vals)
X = np.arange(1, 6)
last_3_avg = np.mean(Y[-3:])
std_dev = np.std(Y, ddof=1)
stretch = stretch_rate / 100

# [기초 기준치 및 도전적 기준치 산정]
if direction == "상향":
    raw_base = max(Y[-1], last_3_avg)
    challenged_base = raw_base * (1 + stretch)
elif direction == "하향":
    raw_base = min(Y[-1], last_3_avg)
    challenged_base = raw_base * (1 - stretch)
else:
    raw_base = Y[-1]
    challenged_base = raw_base

# 4. 7대 평가방법 자동 산출
slope, intercept, _, _, _ = stats.linregress(X, Y)
trend_2026 = intercept + slope * 6

methods = {
    "목표부여(2편차)": challenged_base + (2 * std_dev if direction == "상향" else -2 * std_dev),
    "목표부여(1편차)": challenged_base + (1 * std_dev if direction == "상향" else -1 * std_dev),
    "목표부여(120%)": challenged_base * (1.2 if direction == "상향" else 0.8),
    "목표부여(110%)": challenged_base * (1.1 if direction == "상향" else 0.9),
    "중장기 목표부여": challenged_base * 1.15, # 로드맵 가정치
    "글로벌 실적비교": challenged_base * 1.12, # 우수기관 평균 가정치
    "추세치 평가": trend_2026
}

# 5. 결과 레이아웃 구성
col_main, col_side = st.columns([3, 1])

with col_main:
    st.subheader(f"📊 '{ind_name}' 시뮬레이션 결과 (도전율 {stretch_rate}%)")
    st.write(f"**순수 기준치:** {raw_base:.3f} ➔ **도전적 기준치:** :red[{challenged_base:.3f}]")
    
    # 평가방법별 목표치 표
    res_df = pd.DataFrame({
        "평가방법": methods.keys(),
        "산출 목표치": methods.values(),
        "도전성 성격": ["최상위(2σ) 도전", "상위(1σ) 도전", "정책적 상향(강)", "정책적 상향(약)", "로드맵 기반", "세계 수준", "통계적 추세"]
    })
    st.table(res_df.style.format({"산출 목표치": "{:.3f}"}))

    # 시각화
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist_years, y=Y, name="과거 실적", mode='lines+markers'))
    fig.add_trace(go.Scatter(x=[2026], y=[methods["목표부여(2편차)"]], name="최고목표(2σ)", marker=dict(size=12, color='red', symbol='star')))
    st.plotly_chart(fig, use_container_width=True)

with col_side:
    st.subheader("🚩 도전성 5단계 범주")
    st.markdown("""
    | 단계 | 명칭 | 범위 |
    | :--- | :--- | :--- |
    | <span style='color:green'>5</span> | **한계 혁신** | 100%↑ |
    | <span style='color:blue'>4</span> | **적극 상향** | 50%↑ |
    | <span style='color:orange'>3</span> | **소극 개선** | 25%↑ |
    | <span style='color:gray'>2</span> | **현상 유지** | 0%↑ |
    | <span style='color:red'>1</span> | **하향 설정** | 0%↓ |
    """, unsafe_allow_html=True)
    
    # zp 기반 도전성 판정
    s_resid = np.sqrt(np.sum((Y - (intercept + slope * X))**2) / 3)
    S_val = max(s_resid * np.sqrt(1 + (1/5) + (9/10)), 0.0001)
    zp = (methods["목표부여(2편차)"] - trend_2026) / S_val if direction == "상향" else (trend_2026 - methods["목표부여(2편차)"]) / S_val
    score = (zp / 2.0) * 100

    if score >= 100: status, color = "🏆 한계 혁신", "green"
    elif score >= 50: status, color = "🔥 적극 상향", "blue"
    elif score >= 25: status, color = "📈 소극 개선", "orange"
    elif score >= 0: status, color = "⚖️ 현상 유지", "gray"
    else: status, color = "⚠️ 하향 설정", "red"
    
    st.divider()
    st.write("### 내 도전성 등급")
    st.title(f":{color}[{status.split()[-1]}]")
    st.metric("도전성 지수", f"{score:.1f}%")

# 6. 상세 결과표 및 다운로드 (이미지 91881c 양식 반영)
st.divider()
st.subheader("📅 경영평가 상세 시뮬레이션 결과표")
goal_hi = methods["목표부여(2편차)"]
goal_lo = challenged_base - (2 * std_dev if direction == "상향" else -2 * std_dev)
est_score = np.clip(20 + 80 * ((current_estimated - goal_lo) / (goal_hi - goal_lo)), 20, 100) if direction == "상향" else 100.0

final_df = pd.DataFrame({
    "사업명": [biz_name], "지표명": [ind_name], "지표성격": [direction],
    "기준치": [f"{challenged_base:.3f}"], "최고목표": [f"{goal_hi:.3f}"], "최저목표": [f"{goal_lo:.3f}"],
    "예상평점": [f"{est_score:.2f}"], "예상득점": [f"{(est_score*weight/100):.3f}"]
})
st.dataframe(final_df, use_container_width=True)

# 엑셀 다운로드
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    final_df.to_excel(writer, index=False)
st.download_button("📥 시뮬레이션 결과 엑셀 다운로드", output.getvalue(), "KPI_Result.xlsx")
