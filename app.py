import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="경평 지표 목표설정 상세 시뮬레이터", layout="wide")

# 2. 연도 설정 (2026년 기준)
current_year = 2026 
y_list = [current_year - i for i in range(5, 0, -1)]
future_years = [current_year + i for i in range(1, 4)]

st.title(f"📊 {current_year}년 경영평가 지표 목표설정 상세 시뮬레이터")
st.markdown("과거 실적과 기준치를 바탕으로 **최고/최저 목표치를 자동 산출**하며, 보고서용 상세 데이터를 제공합니다.")

# 3. 실적 입력
with st.expander("📂 1단계: 과거 5개년 실적 데이터 입력", expanded=True):
    cols = st.columns(5)
    inputs = []
    for i, y in enumerate(y_list):
        with cols[i]:
            val = st.number_input(f"{y}년 실적", value=100.000 + (i*5), format="%.3f", step=0.001)
            inputs.append(val)

hist = inputs
avg_3y = sum(hist[-3:]) / 3
std_5y = np.std(hist)

# 4. 사이드바 설정
st.sidebar.header("⚙️ 지표 기본 설정")
indicator_name = st.sidebar.text_input("지표명", value="주요사업 성과지표")
weight = st.sidebar.number_input("가중치(배점)", value=5.0)
direction = st.sidebar.selectbox("지표 방향", ["상향(실적↑ 좋음)", "하향(실적↓ 좋음)"])
is_up = "상향" in direction

# 기준치 산정 (전년도 vs 3개평균)
y1 = hist[-1]
if is_up:
    base_val = max(y1, avg_3y)
    base_desc = "전년도 실적" if y1 > avg_3y else "직전 3개년 평균"
else:
    base_val = min(y1, avg_3y)
    base_desc = "전년도 실적" if y1 < avg_3y else "직전 3개년 평균"

# 추세 및 중장기
slope, intercept = np.polyfit(np.array([1,2,3,4,5]), hist, 1)
suggested_lt = slope * 8 + intercept
st.sidebar.markdown("---")
long_term_goal = st.sidebar.number_input(f"{current_year+3}년 중장기 목표", value=float(suggested_lt), format="%.3f")

# 5. 분석 실행
if st.button("🚀 상세 분석 결과 생성"):
    
    # 평가방법별 산출 로직
    trend_base = slope * 6 + intercept # 당해 추세치
    lt_step = (long_term_goal - base_val) / 4
    lt_target = base_val + lt_step # 당해 중장기 분할 목표
    
    # [방법명, 최고(S), 최저(D)]
    raw_calc = [
        ("목표부여(2편차)", base_val + 2*std_5y, base_val - 2*std_5y),
        ("목표부여(1편차)", base_val + 1*std_5y, base_val - 1*std_5y),
        ("목표부여(120%)", base_val * 1.2, base_val * 0.8),
        ("목표부여(110%)", base_val * 1.1, base_val * 0.9),
        ("추세치 평가", trend_base + std_5y, trend_base - std_5y),
        ("중장기 목표부여", lt_target, lt_target) # 단일 목표 예시
    ]
    
    processed_results = []
    for name, s_val, d_val in raw_calc:
        # 하향 지표일 경우 S와 D의 수치를 반전
        hi = s_val if is_up else d_val
        lo = d_val if is_up else s_val
        
        # 도전성 산출
        stretch = abs(hi - base_val) / base_val * 100 if base_val != 0 else 0
        
        # 목표치 통합 표시 (최고와 최저가 같으면 하나만 표시)
        if round(hi, 3) == round(lo, 3):
            target_display = f"{hi:.3f} (단일)"
        else:
            target_display = f"{lo:.3f} ~ {hi:.3f}"
            
        processed_results.append({
            "평가방법": name,
            "기준치": f"{base_val:.3f}",
            "최고목표(S)": round(hi, 3),
            "최저목표(D)": round(lo, 3),
            "목표 구간/수치": target_display,
            "도전성(%)": f"{stretch:.2f}%"
        })
    
    df = pd.DataFrame(processed_results)
    
    # 6. 결과 출력
    st.subheader(f"3. {current_year}년 평가방법별 목표 산출 상세표")
    st.table(df[['평가방법', '기준치', '최고목표(S)', '최저목표(D)', '목표 구간/수치', '도전성(%)']])
    
    st.info(f"💡 **기준치 산출 근거**: 현재 지표는 **{base_desc}**({base_val:.3f})를 기준치로 자동 채택하였습니다.")
    
    # 시각화 (막대/오차막대 그래프)
    fig = go.Figure()
    # 최고 목표 막대
    fig.add_trace(go.Bar(
        x=df["평가방법"], y=df["최고목표(S)"],
        name="최고목표(S)", marker_color='indianred'
    ))
    # 최저 목표 막대
    fig.add_trace(go.Bar(
        x=df["평가방법"], y=df["최저목표(D)"],
        name="최저목표(D)", marker_color='lightsalmon'
    ))
    fig.add_hline(y=base_val, line_dash="dash", line_color="black", annotation_text="기준치")
    fig.update_layout(title="평가방법별 목표 구간 비교", barmode='group', template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # 7. 참고자료 표 (요청하신 상세 통계)
    st.subheader("📊 참고자료: 산출 기초 통계")
    cagr = ((hist[-1] / hist[0]) ** (1/4) - 1) * 100
    
    stat_df = pd.DataFrame({
        "항목": ["5개년 연평균 증가율(CAGR)", "직전 3개년 평균", "직전 3개년 표준편차", "당해연도 추세치", "1년 후 예측", "2년 후 예측", "3년 후 중장기"],
        "수치": [f"{cagr:.2f}%", f"{avg_3y:.3f}", f"{np.std(hist[-3:]):.3f}", f"{slope*6+intercept:.3f}", f"{slope*7+intercept:.3f}", f"{slope*8+intercept:.3f}", f"{long_term_goal:.3f}"]
    })
    st.dataframe(stat_df, use_container_width=True)
