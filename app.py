import streamlit as st
import pandas as pd
import numpy as np
import io
from scipy import stats

# 1. 페이지 설정
st.set_page_config(page_title="경평 지표 시뮬레이터", layout="wide")
st.title("📊 경영평가 계량지표 추정실적 및 시뮬레이션")

# 2. 사이드바: 데이터 입력
with st.sidebar:
    st.header("📋 지표 기본 정보")
    biz_name = st.text_input("사업명", value="인체조직 생산사업")
    indicator_name = st.text_input("지표명", value="기증자당 혈관 채취 실적")
    weight = st.number_input("가중치", value=5.0)
    
    st.header("📊 과거 5개년 실적")
    hist_years = [2021, 2022, 2023, 2024, 2025]
    y_vals = []
    for y in hist_years:
        val = st.number_input(f"{y}년 실적", value=1.800 + (y-2021)*0.05, format="%.3f")
        y_vals.append(val)
    
    is_up = st.toggle("상향지표 (실적↑ 좋음)", value=True)
    user_goal = st.number_input("2026년 설정 목표치", value=float(y_vals[-1] * 1.05))

# 3. 계산 엔진
Y = np.array(y_vals)
avg_5yr = np.mean(Y)
std_val = np.std(Y, ddof=1)
last_val = Y[-1]
base_val = max(last_val, np.mean(Y[-3:])) if is_up else min(last_val, np.mean(Y[-3:]))

# 추세치 분석 (zp 및 한계 혁신 진단용)
X = np.array([1, 2, 3, 4, 5])
slope, intercept, _, _, _ = stats.linregress(X, Y)
trend_2026 = intercept + slope * 6
y_hat = intercept + slope * X
s_resid = np.sqrt(np.sum((Y - y_hat)**2) / (5 - 2))
S_val = max(s_resid * np.sqrt(1 + (1/5) + ((6-3)**2 / np.sum((X-3)**2))), 0.0001)
zp = (user_goal - trend_2026) / S_val if is_up else (trend_2026 - user_goal) / S_val
challenge_score = (zp / 2.0) * 100

# 목표부여 편차 산식에 따른 최고/최저치
goal_high = base_val + (2 * std_val if is_up else -2 * std_val)
goal_low = base_val - (2 * std_val if is_up else -2 * std_val)

# 예상 평점 계산 (목표부여 평점 산식 적용)
if is_up:
    est_score = 20 + 80 * ((user_goal - goal_low) / (goal_high - goal_low))
else:
    est_score = 20 + 80 * ((goal_high - user_goal) / (goal_high - goal_low))
est_score = np.clip(est_score, 20, 100)

# 4. 시뮬레이션 결과 표 생성 (이미지 양식 반영)
st.subheader("✅ 2026년 시뮬레이션 결과 요약")

result_data = {
    "구분": ["데이터값"],
    "사업명": [biz_name],
    "지표명": [indicator_name],
    "지표성격": ["상향지표" if is_up else "하향지표"],
    "과거5년평균": [f"{avg_5yr:.3f}"],
    "표준편차": [f"{std_val:.3f}"],
    "기준치": [f"{base_val:.3f}"],
    "최고목표(2σ)": [f"{goal_high:.3f}"],
    "최저목표": [f"{goal_low:.3f}"],
    "설정목표": [f"{user_goal:.3f}"],
    "예상평점": [f"{est_score:.2f}"],
    "가중치": [weight],
    "예상득점": [f"{(est_score * weight / 100):.3f}"]
}
df_result = pd.DataFrame(result_data)
st.dataframe(df_result, use_container_width=True)

# 5. 파일 다운로드 및 복사 기능
col1, col2 = st.columns(2)
with col1:
    # 엑셀 다운로드 기능
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_result.to_excel(writer, index=False, sheet_name='시뮬레이션결과')
    st.download_button(
        label="📥 엑셀 파일로 다운로드",
        data=output.getvalue(),
        file_name=f"{biz_name}_시뮬레이션.xlsx",
        mime="application/vnd.ms-excel"
    )

with col2:
    # 도전성 진단 (결정된 5단계)
    if challenge_score >= 100:
        status, color = "한계 혁신", "green"
    elif challenge_score >= 50:
        status, color = "적극 상향", "blue"
    elif challenge_score >= 25:
        status, color = "소극 개선", "orange"
    elif challenge_score >= 0:
        status, color = "현상 유지", "gray"
    else:
        status, color = "하향 설정", "red"
    
    st.markdown(f"**현재 도전성 등급:** :{color}[**{status}**] (지수: {challenge_score:.1f}%)")

# 6. 상세 비교 탭
tab1, tab2 = st.tabs(["📊 7대 방법론 상세 비교", "📚 산식 근거"])
with tab1:
    # 7대 방법론을 포함한 확장 표
    methods = {
        "방법론": ["목표부여(2편차)", "목표부여(1편차)", "목표부여(120%)", "추세치 분석"],
        "산출값": [goal_high, base_val + std_val, base_val*1.2, trend_2026]
    }
    st.table(pd.DataFrame(methods))
