import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. 페이지 설정
st.set_page_config(page_title="경영평가 지표 시뮬레이터", layout="wide")

# 현재 연도 기준 설정 (2026년)
현재_연도 = 2026 
과거_연도_리스트 = [현재_연도 - i for i in range(5, 0, -1)]

st.title("⚖️ 경영평가 계량지표 통합 시뮬레이터")

# 시각적 개선을 위한 스타일 설정
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

# 2. 사이드바 설정
st.sidebar.header("📍 지표 기본 설정")
지표명 = st.sidebar.text_input("지표명", value="주요사업 성과지표")
가중치 = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
지표방향 = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

# 3. 실적 데이터 입력 섹션
st.subheader("1. 실적 데이터 입력")

상단_헤더 = st.columns([6, 1, 1, 1])
with 상단_헤더[0]: st.markdown('<div class="main-header-box">과거 5개년 실적</div>', unsafe_allow_html=True)
with 상단_헤더[1]: st.markdown('<div class="main-header-box">과거 3개년 평균</div>', unsafe_allow_html=True)
with 상단_헤더[2]: st.markdown('<div class="main-header-box">기준치</div>', unsafe_allow_html=True)
with 상단_헤더[3]: st.markdown('<div class="main-header-box">2026년 예상실적</div>', unsafe_allow_html=True)

입력_열 = st.columns(9)

실적_리스트 = []
for i, 연도 in enumerate(과거_연도_리스트):
    with 입력_열[i]:
        st.markdown(f'<div class="sub-label-text">{연도}년</div>', unsafe_allow_html=True)
        값 = st.number_input(f"{연도}실적", label_visibility="collapsed", value=100.000 + (i*5), format="%.3f", key=f"실적_{i}")
        실적_리스트.append(값)

# 기초 계산 로직
유효실적 = [v for v in 실적_리스트 if v > 0]
표준편차 = np.std(유효실적) if len(유효실적) > 1 else 0.000
삼개년_평균 = np.mean(실적_리스트[-3:])
직전년도_실적 = 실적_리스트[-1]
기준치 = max(삼개년_평균, 직전년도_실적) if 지표방향 == "상향" else min(삼개년_평균, 직전년도_실적)

with 입력_열[5]:
    st.markdown('<div class="sub-label-text">과거 표준편차</div>', unsafe_allow_html=True)
    st.text_input("편차표시", value=f"{표준편차:.3f}", label_visibility="collapsed", disabled=True)
with 입력_열[6]:
    st.markdown('<div class="sub-label-text">&nbsp;</div>', unsafe_allow_html=True) 
    st.text_input("평균표시", value=f"{삼개년_평균:.3f}", label_visibility="collapsed", disabled=True)
with 입력_열[7]:
    st.markdown('<div class="sub-label-text">&nbsp;</div>', unsafe_allow_html=True)
    st.text_input("기준치표시", value=f"{기준치:.3f}", label_visibility="collapsed", disabled=True)
with 입력_열[8]:
    st.markdown('<div class="sub-label-text">&nbsp;</div>', unsafe_allow_html=True)
    예상실적 = st.number_input("예상실적입력", value=기준치 * 1.05, format="%.3f", label_visibility="collapsed")

# 4. 분석 실행 및 결과 섹션
st.markdown("---")
if st.button("🚀 모든 평가방법 통합 분석 실행"):
    
    # [도전성 지수 계산을 위한 통계 준비]
    X_축 = np.array([1, 2, 3, 4, 5])
    Y_축 = np.array(실적_리스트)
    기울기, 절편 = np.polyfit(X_축, Y_축, 1)
    미래_추세치 = 기울기 * 6 + 절편
    
    # 보정 로직
    잔차_표준편차 = np.sqrt(np.sum((Y_축 - (절편 + 기울기 * X_축))**2) / 3)
    최소_변동폭 = abs(기준치 * 0.10)
    보정_표준오차 = max(잔차_표준편차 * np.sqrt(1 + (1/5) + (9/10)), 최소_변동폭)

    상향_여부 = (지표방향 == "상향")
    if 상향_여부:
        방법별_데이터 = [
            ("목표부여(2편차)", 기준치 + 2*표준편차, 기준치 - 2*표준편차),
            ("목표부여(1편차)", 기준치 + 1*표준편차, 기준치 - 2*표준편차),
            ("목표부여(120%)", 기준치 * 1.200, 기준치 * 0.800),
            ("목표부여(110%)", 기준치 * 1.100, 기준치 * 0.800)
        ]
    else:
        방법별_데이터 = [
            ("목표부여(2편차)", 기준치 - 2*표준편차, 기준치 + 2*표준편차),
            ("목표부여(1편차)", 기준치 - 1*표준편차, 기준치 + 2*표준편차),
            ("목표부여(120%)", 기준치 * 0.800, 기준치 * 1.200),
            ("목표부여(110%)", 기준치 * 0.900, 기준치 * 1.200)
        ]

    결과_데이터 = []
    for 명칭, 최고, 최저 in 방법별_데이터:
        if 최고 == 최저:
            평점 = 60.000
        else:
            평점 = 20 + 80 * ((예상실적 - 최저) / (최고 - 최저))
        
        평점 = max(20.0, min(100.0, 평점))
        예상득점 = (평점 / 100) * 가중치
        
        # 도전성 지수 계산
        지수 = (최고 - 미래_추세치) / 보정_표준오차 if 상향_여부 else (미래_추세치 - 최고) / 보정_표준오차
        도전성_백분율 = (지수 / 2.0) * 100

        if 도전성_백분율 >= 150: 단계 = "🏆 한계 혁신"
        elif 도전성_백분율 >= 80: 단계 = "🔥 적극 상향"
        elif 도전성_백분율 >= 40: 단계 = "📈 소극 개선"
        elif 도전성_백분율 >= 0: 단계 = "⚖️ 현상 유지"
        else: 단계 = "⚠️ 하향 설정"

        결과_데이터.append({
            "평가방법": 명칭, 
            "지표성격": 지표방향, 
            "3개년 평균": round(삼개년_평균, 3),
            "직전년도 실적": round(직전년도_실적, 3),
            "기준치": round(기준치, 3),
            "최고목표": round(최고, 3), 
            "최저목표": round(최저, 3), 
            "예상실적": round(예상실적, 3),
            "예상평점": round(평점, 3), 
            "가중치": round(가중치, 3), 
            "예상득점": round(예상득점, 3),
            "도전성 단계": 단계
        })
    
    표_데이터 = pd.DataFrame(결과_데이터)
    st.subheader("2. 평가방법별 비교 분석 결과")
    
    st.dataframe(
        표_데이터.style.format({
            "3개년 평균": "{:.3f}", "직전년도 실적": "{:.3f}", "기준치": "{:.3f}", 
            "최고목표": "{:.3f}", "최저목표": "{:.3f}", "예상실적": "{:.3f}", 
            "예상평점": "{:.3f}", "가중치": "{:.3f}", "예상득점": "{:.3f}"
        }).highlight_max(axis=0, subset=['예상평점'], color='#D4EDDA'), 
        use_container_width=True
    )

    # 도전성 기준 및 산출방법 설명 (이전과 동일)
    st.markdown("""
    <div style='background-color: #f9f9f9; padding: 15px; border-radius: 5px; border-left: 5px solid #d1d5db; margin-top: 10px;'>
        <b style='font-size: 0.95em; color: #333;'>🚩 도전성 5단계 판정 기준</b><br>
        <div style='font-size: 0.88em; color: #555; margin-top: 8px; line-height: 1.8;'>
            • <span style='color: #d9534f;'><b>1단계 (⚠️ 하향 설정)</b></span> : 도전성 지수 0% 미만<br>
            • <span style='color: #777;'><b>2단계 (⚖️ 현상 유지)</b></span> : 도전성 지수 0% 이상<br>
            • <span style='color: #f0ad4e;'><b>3단계 (📈 소극 개선)</b></span> : 도전성 지수 40% 이상<br>
            • <span style='color: #0275d8;'><b>4단계 (🔥 적극 상향)</b></span> : 도전성 지수 80% 이상<br>
            • <span style='color: #5cb85c;'><b>5단계 (🏆 한계 혁신)</b></span> : 도전성 지수 150% 이상
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='background-color: #ffffff; padding: 12px; border: 1px solid #e6e9ef; border-radius: 5px; margin-top: 10px;'>
        <p style='font-size: 0.85em; font-weight: bold; color: #444; margin-bottom: 5px;'>🔍 도전성 지수 산출방법</p>
        <p style='font-size: 0.8em; color: #666; line-height: 1.6;'>
            도전성 지수는 과거 5개년 실적의 <b>미래 추세 예측값</b>을 기준으로, 이번에 설정한 <b>최고목표</b>가 얼마나 멀리 떨어져 있는지를 측정합니다.<br><br>
            <b>[계산식]</b><br>
            도전성 지수 = (최고목표 - 미래 추세치) ÷ 표준오차<br><br>
            ※ 과거 실적 변동이 너무 적은 경우, 기준치의 10%를 최소 변동폭으로 적용하여 지수가 과도하게 높게 나오는 것을 방지했습니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 그래프 시각화
    fig, ax = plt.subplots(figsize=(10, 4))
    x = np.arange(len(표_데이터))
    ax.bar(x - 0.2, 표_데이터['최고목표'], 0.4, label='최고목표', color='skyblue')
    ax.bar(x + 0.2, 표_데이터['최저목표'], 0.4, label='최저목표', color='lightgrey')
    ax.axhline(기준치, color='red', linestyle='--', label='기준치')
    ax.set_xticks(x)
    ax.set_xticklabels(표_데이터['평가방법'], rotation=45)
    ax.legend()
    st.pyplot(fig)

    # 하단 산식 가이드
    st.markdown("---")
    st.info("""
    **💡 주요 산식 가이드**
    * 예상평점: 20 + 80 × (예상실적 - 최저목표) ÷ (최고목표 - 최저목표)
    * 예상득점: (예상평점 ÷ 100) × 가중치
    """)
