import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="경평 지표 목표설정 사수", layout="wide")

# 0. 연도 및 초기 세팅
current_year = 2026 # 고정 또는 datetime.now().year
y_list = [current_year - i for i in range(5, 0, -1)]
future_years = [current_year + i for i in range(1, 4)]

st.title(f"🚀 {current_year}년 경영평가 목표설정 지능형 시뮬레이터")
st.info("💡 **도움말**: 이 도구는 숫자를 계산할 뿐만 아니라, 담당자님이 논리적인 목표를 세우도록 가이드를 제공합니다.")

# 1. 과거 실적 입력 섹션
with st.expander("📊 1단계: 과거 5개년 실적 입력 (클릭하여 열기)", expanded=True):
    cols = st.columns(5)
    inputs = []
    for i, y in enumerate(y_list):
        with cols[i]:
            val = st.number_input(f"{y}년 실적", value=100.0 + (i*5), format="%.3f", step=0.001, help=f"{y}년도 결산 실적을 입력하세요.")
            inputs.append(val)

y5, y4, y3, y2, y1 = inputs
hist = [y5, y4, y3, y2, y1]
avg_3y = sum(hist[-3:]) / 3
std_5y = np.std(hist)

# 2. 지표 성격 설정 (사이드바)
st.sidebar.header("🎯 2단계: 지표 성격 진단")
indicator_name = st.sidebar.text_input("지표명", value="주요사업 성과지표")
weight = st.sidebar.number_input("가중치(배점)", value=5.0)
direction = st.sidebar.selectbox("지표 방향", ["상향(실적이 클수록 좋음)", "하향(실적이 작을수록 좋음)"])
indicator_type = st.sidebar.radio(
    "지표의 현재 상태는?",
    ["안정적 성장기(추세 뚜렷)", "정체/성숙기(변동폭 적음)", "신규/변동성 높음(예측 어려움)"]
)

# 기준치 산정
is_up = "상향" in direction
base_val = max(y1, avg_3y) if is_up else min(y1, avg_3y)
base_desc = "전년도 실적" if (is_up and y1 > avg_3y) or (not is_up and y1 < avg_3y) else "직전 3개년 평균"

# 추세 계산
slope, intercept = np.polyfit(np.array([1,2,3,4,5]), hist, 1)
suggested_lt = slope * 8 + intercept

st.sidebar.markdown("---")
st.sidebar.subheader("📍 중장기 목표 가이드")
st.sidebar.write(f"📈 추세 분석 결과 {current_year+3}년 추천치: **{suggested_lt:.3f}**")
long_term_goal = st.sidebar.number_input(f"{current_year+3}년 중장기 목표 설정", value=float(suggested_lt), format="%.3f")

# 3. 역산 시뮬레이션 (What-if)
st.subheader(f"🔍 2단계: 목표-평점 역산 시뮬레이션")
st.write("목표를 정하기 전, **'내가 몇 점을 받고 싶은지'** 먼저 생각해보세요.")
target_score = st.slider("목표 평점(100점 만점) 설정", 20, 100, 90)

# 4. 분석 실행
if st.button("🚀 전체 평가방법 통합 분석 및 가이드 도출"):
    
    # 평가방법 데이터 계산
    trend_base = slope * 6 + intercept
    lt_base = base_val + (long_term_goal - base_val) / 4
    
    methods_raw = [
        ("목표부여(2편차)", base_val + 2*std_5y, base_val - 2*std_5y),
        ("목표부여(1편차)", base_val + 1*std_5y, base_val - 1*std_5y),
        ("목표부여(120%)", base_val * 1.2, base_val * 0.8),
        ("목표부여(110%)", base_val * 1.1, base_val * 0.9),
        ("추세치 평가", trend_base + std_5y, trend_base - std_5y),
        ("중장기 목표부여", lt_base * 1.05, lt_base * 0.95)
    ]
    
    results = []
    for name, hi, lo in methods_raw:
        if not is_up: hi, lo = lo, hi
        
        # 역산: 목표 평점을 받기 위해 필요한 실적 계산
        # score = 20 + 80 * (required - lo) / (hi - lo)
        required_perf = lo + (target_score - 20) * (hi - lo) / 80
        stretch = abs(hi - base_val) / base_val * 100 if base_val != 0 else 0
        
        # 적정성 가이드 (도전성이 5~15% 사이면 Green, 너무 낮으면 Yellow, 너무 높으면 Red)
        status = "🟢 적정" if 5 <= stretch <= 20 else "🟡 보수적" if stretch < 5 else "🔴 과도"
        
        results.append({
            "평가방법": name,
            "S등급 목표치": round(hi, 3),
            "도전성(%)": round(stretch, 2),
            "권장도": status,
            f"{target_score}점 확보 필요실적": round(required_perf, 3)
        })
    
    df = pd.DataFrame(results)
    
    # 결과 출력
    st.subheader("3. 분석 결과 및 목표 설정 가이드")
    st.table(df)
    st.caption("※ **도전성(%)**: |(S목표 - 기준치)| / 기준치 × 100")
    
    # 지표 성격별 추천 로직
    st.success("🎯 **지표 성격에 따른 사수의 추천**")
    if "안정적" in indicator_type:
        st.write(f"현재 지표는 성장세가 뚜렷하므로 **[추세치 평가]**가 가장 논리적입니다. 예상되는 S목표는 **{df.iloc[4]['S등급 목표치']}**입니다.")
    elif "정체" in indicator_type:
        st.write(f"정체기 지표는 과거 편차를 활용한 **[목표부여(1편차)]**가 설득력이 높습니다. S목표 **{df.iloc[1]['S등급 목표치']}**를 검토해보세요.")
    else:
        st.write("변동성이 큰 지표는 미래 비전을 강조하는 **[중장기 목표부여]** 방식이 논란을 피하기 좋습니다.")

    # 그래프
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["평가방법"], y=df["S등급 목표치"], name="S등급 목표", marker_color='lightblue'))
    fig.add_hline(y=base_val, line_dash="dash", line_color="red", annotation_text="기준치")
    fig.update_layout(title="평가방법별 목표치 및 기준치 비교", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
    
    # 5. 참고자료
    st.subheader("📊 참고 데이터 상세")
    cagr = ((y1 / y5) ** (1/4) - 1) * 100 if y5 > 0 else 0
    st.write(f"✅ 과거 5개년 연평균 증가율(CAGR): **{cagr:.2f}%**")
    st.write(f"✅ 현재 적용된 기준치: **{base_val:.3f}** (근거: {base_desc})")
