import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(page_title="경영평가 지표 시뮬레이터", layout="wide")

# 현재 연도 기준 설정
current_year = 2026 
past_years = [current_year - i for i in range(5, 0, -1)]

st.title("⚖️ 경영평가 계량지표 통합 시뮬레이터")

# 시각적 개선을 위한 CSS
st.markdown("""
<style>
    input:disabled {
        -webkit-text-fill-color: #000000 !important;
        color: #000000 !important;
        font-weight: 600 !important;
        background-color: #E8F0FE !important;
        border: 1px solid #adc6ff !important;
        opacity: 1 !important;
    }
    .stNumberInput input { background-color: #ffffff !important; color: #000000 !important; }
    .main-header-box {
        background-color: #f0f2f6; padding: 10px; border-radius: 5px;
        text-align: center; font-weight: 800; font-size: 1.1em;
        border: 1px solid #d1d5db; display: flex; align-items: center; justify-content: center;
        height: 60px; margin-bottom: 5px;
    }
    .sub-label-text {
        text-align: center; font-size: 1.0em; font-weight: 700; color: #111;
        margin-bottom: 8px; height: 25px; display: flex; align-items: center; justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# 사이드바 설정
st.sidebar.header("📍 지표 기본 설정")
indicator_name = st.sidebar.text_input("지표명", value="주요사업 성과지표")
weight = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
direction = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

# 1. 실적 데이터 입력 섹션
st.subheader("1. 실적 데이터 입력")

header_cols = st.columns([6, 1, 1, 1])
with header_cols[0]: st.markdown('<div class="main-header-box">과거 5개년 실적</div>', unsafe_allow_html=True)
with header_cols[1]: st.markdown('<div class="main-header-box">과거 3개년 평균</div>', unsafe_allow_html=True)
with header_cols[2]: st.markdown('<div class="main-header-box">기준치</div>', unsafe_allow_html=True)
with header_cols[3]: st.markdown('<div class="main-header-box">2026년 예상실적</div>', unsafe_allow_html=True)

data_cols = st.columns(9)

hist_raw = []
for i, year in enumerate(past_years):
    with data_cols[i]:
        st.markdown(f'<div class="sub-label-text">{year}년</div>', unsafe_allow_html=True)
        val = st.number_input(f"{year}실적", label_visibility="collapsed", value=100.000 + (i*5), format="%.3f", key=f"h_{i}")
        hist_raw.append(val)

valid_hist = [v for v in hist_raw if v > 0]
std_val = np.std(valid_hist) if len(valid_hist) > 1 else 0.000
avg_3y = np.mean(hist_raw[-3:])
last_year_val = hist_raw[-1]
base_val = max(avg_3y, last_year_val) if direction == "상향" else min(avg_3y, last_year_val)

with data_cols[5]:
    st.markdown('<div class="sub-label-text">과거 표준편차</div>', unsafe_allow_html=True)
    st.text_input("표준편차", value=f"{std_val:.3f}", label_visibility="collapsed", disabled=True)
with data_cols[6]:
    st.markdown('<div class="sub-label-text">&nbsp;</div>', unsafe_allow_html=True) 
    st.text_input("평균", value=f"{avg_3y:.3f}", label_visibility="collapsed", disabled=True)
with data_cols[7]:
    st.markdown('<div class="sub-label-text">&nbsp;</div>', unsafe_allow_html=True)
    st.text_input("기준치", value=f"{base_val:.3f}", label_visibility="collapsed", disabled=True)
with data_cols[8]:
    st.markdown('<div class="sub-label-text">&nbsp;</div>', unsafe_allow_html=True)
    est = st.number_input("예상실적", value=base_val * 1.05, format="%.3f", label_visibility="collapsed")

# --- 2. 분석 실행 및 결과 섹션 ---
st.markdown("---")
if st.button("🚀 모든 평가방법 통합 분석 실행"):
    
    # [도전성 지수 zp 계산을 위한 회귀분석 기반 준비]
    X = np.array([1, 2, 3, 4, 5])
    Y = np.array(hist_raw)
    slope, intercept = np.polyfit(X, Y, 1)
    trend_2026 = slope * 6 + intercept
    s_resid = np.sqrt(np.sum((Y - (intercept + slope * X))**2) / 3)
    S_val = max(s_resid * np.sqrt(1 + (1/5) + (9/10)), 0.0001)

    # 평가방법별 최고/최저 목표 산출 로직
    is_up = (direction == "상향")
    if is_up:
        methods_data = [
            ("목표부여(2편차)", base_val + 2*std_val, base_val - 2*std_val),
            ("목표부여(1편차)", base_val + 1*std_val, base_val - 2*std_val),
            ("목표부여(120%)", base_val * 1.200, base_val * 0.800),
            ("목표부여(110%)", base_val * 1.100, base_val * 0.800)
        ]
    else: # 하향 지표
        methods_data = [
            ("목표부여(2편차)", base_val - 2*std_val, base_val + 2*std_val),
            ("목표부여(1편차)", base_val - 1*std_val, base_val + 2*std_val),
            ("목표부여(120%)", base_val * 0.800, base_val * 1.200),
            ("목표부여(110%)", base_val * 0.900, base_val * 1.200)
        ]

    results = []
    for m_name, hi, lo in methods_data:
        # 평점 산식
        if hi == lo:
            score = 60.000
        else:
            score = 20 + 80 * ((est - lo) / (hi - lo))
        
        score = max(20.0, min(100.0, score))
        weighted_score = (score / 100) * weight
        
        # [도전성 5단계 판정 로직]
        zp = (hi - trend_2026) / S_val if is_up else (trend_2026 - hi) / S_val
        challenge_score = (zp / 2.0) * 100

        if challenge_score >= 100: status = "🏆 한계 혁신"
        elif challenge_score >= 50: status = "🔥 적극 상향"
        elif challenge_score >= 25: status = "📈 소극 개선"
        elif challenge_score >= 0: status = "⚖️ 현상 유지"
        else: status = "⚠️ 하향 설정"

        results.append({
            "평가방법": m_name,
            "지표성격": direction,
            "기준치": round(base_val, 3),
            "최고목표": round(hi, 3),
            "최저목표": round(lo, 3),
            "예상실적": round(est, 3),
            "예상평점": round(score, 3),
            "가중치": round(weight, 3),
            "예상득점": round(weighted_score, 3),
            "도전성 단계": status
        })
    
    df = pd.DataFrame(results)
    st.subheader("2. 평가방법별 비교 분석 결과")
    
    st.dataframe(
        df.style.format({
            "기준치": "{:.3f}", "최고목표": "{:.3f}", "최저목표": "{:.3f}", 
            "예상실적": "{:.3f}", "예상평점": "{:.3f}", "가중치": "{:.3f}", "예상득점": "{:.3f}"
        }).highlight_max(axis=0, subset=['예상평점'], color='#D4EDDA'), 
        use_container_width=True
    )

    # 도전성 5단계 각주
    st.markdown("""
    <div style='font-size: 0.85em; color: #555; line-height: 1.6;'>
    * <b>도전성 5단계 기준 안내 (도전성 지수 기반)</b><br>
    &nbsp;&nbsp; 1단계(⚠️ 하향 설정): 도전성 지수 0% 미만 | 2단계(⚖️ 현상 유지): 0% 이상 | 3단계(📈 소극 개선): 25% 이상 | 4단계(🔥 적극 상향): 50% 이상 | 5단계(🏆 한계 혁신): 100% 이상
    </div>
    """, unsafe_allow_html=True)

    # 그래프 시각화
    fig, ax = plt.subplots(figsize=(10, 4))
    x = np.arange(len(df))
    ax.bar(x - 0.2, df['최고목표'], 0.4, label='최고목표', color='skyblue')
    ax.bar(x + 0.2, df['최저목표'], 0.4, label='최저목표', color='lightgrey')
    ax.axhline(base_val, color='red', linestyle='--', label='기준치')
    ax.set_xticks(x)
    ax.set_xticklabels(df['평가방법'], rotation=45)
    ax.legend()
    st.pyplot(fig)

    # 3. 산출 방식 가이드 (주석)
    st.markdown("---")
    st.info("""
    **💡 주요 산식 가이드**
    * **예상평점**: $20 + 80 \\times (예상실적 - 최저목표) / (최고목표 - 최저목표)$
    * **도전성 단계**: 최고목표와 과거 추세치($trend$)의 편차를 표준오차($S$)로 나눈 도전성 지수($zp$)를 기준으로 판정합니다.
    * **특이사항**: 상향 시 최고목표가 높을수록, 하향 시 최고목표가 낮을수록 높은 도전성 단계가 부여됩니다.
    """)
