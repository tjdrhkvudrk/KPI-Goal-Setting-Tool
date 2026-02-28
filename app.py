import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import requests

# 1. 한글 폰트 설정
@st.cache_resource
def load_korean_font():
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
    font_path = "NanumGothic-Bold.ttf"
    if not os.path.exists(font_path):
        try:
            res = requests.get(font_url)
            with open(font_path, "wb") as f:
                f.write(res.content)
        except: pass
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        font_name = fm.FontProperties(fname=font_path).get_name()
        plt.rc('font', family=font_name)
    plt.rc('axes', unicode_minus=False)
    return font_path

font_file = load_korean_font()
font_prop = fm.FontProperties(fname=font_file) if font_file else None

# 2. CSS 디자인 (가독성 및 정량 근거 강조)
st.set_page_config(page_title="성과지표 시뮬레이터", layout="wide")
st.markdown("""
<style>
    html, body, [class*="st-"] { font-size: 15px !important; font-family: 'NanumGothic', sans-serif; }
    .main-header { padding: 10px; color: white; text-align: center; font-weight: bold; margin-bottom: 5px; border-radius: 5px 5px 0 0; }
    .bg-past { background-color: #2D6A4F; }
    .bg-current { background-color: #D69E2E; }
    .bg-future { background-color: #4A5568; }
    .sub-header { background-color: #f1f3f5; padding: 5px; text-align: center; font-size: 13px; font-weight: bold; border: 1px solid #dee2e6; border-top: none; }
    div[data-testid="stNumberInput"] label { display: none !important; }
    .auto-res { background-color: #F8FAFC; border: 1px solid #dee2e6; height: 42px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; }
    .guide-box { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px; margin-top: 15px; line-height: 1.8; }
    .guide-title { font-weight: bold; color: #2D3748; font-size: 16px; margin-bottom: 10px; display: block; }
    .formula { background-color: #EDF2F7; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-weight: bold; color: #2C5282; }
    thead tr th { background-color: #4A5568 !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; }
    thead tr th:first-child, tbody tr th { display: none; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ 중장기 성과지표 목표설정 및 한계점 분석기")

# 사이드바
가중치_값 = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
지표방향 = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

st.subheader("1. 실적 데이터 및 중장기 전망 입력")

# 3. 데이터 입력 레이아웃
실적_리스트 = []
m_cols = st.columns([5, 1, 3])

with m_cols[0]:
    st.markdown('<div class="main-header bg-past">과거 5개년 실적 (2021~2025)</div>', unsafe_allow_html=True)
    p_cols = st.columns(5)
    for i, year in enumerate(range(2021, 2026)):
        with p_cols[i]:
            st.markdown(f'<div class="sub-header">{year}</div>', unsafe_allow_html=True)
            val = st.number_input(f"p_{year}", value=100.0 + (i*5), format="%.3f", key=f"v_{year}")
            실적_리스트.append(val)

with m_cols[1]:
    st.markdown('<div class="main-header bg-current">2026년 (예상)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">실적 입력</div>', unsafe_allow_html=True)
    예상_2026 = st.number_input("curr_2026", value=실적_리스트[-1] * 1.05, format="%.3f", key="v_2026")

with m_cols[2]:
    st.markdown('<div class="main-header bg-future">중장기 실적 전망 (자동)</div>', unsafe_allow_html=True)
    f_cols = st.columns(3)
    X = np.arange(6)
    Y = np.array(실적_리스트 + [예상_2026])
    slope, intercept = np.polyfit(X, Y, 1)
    미래_전망 = []
    for i, year in enumerate(range(2027, 2030)):
        with f_cols[i]:
            st.markdown(f'<div class="sub-header">{year}</div>', unsafe_allow_html=True)
            f_val = slope * (6 + i) + intercept
            미래_전망.append(f_val)
            st.markdown(f'<div class="auto-res">{f_val:.3f}</div>', unsafe_allow_html=True)

# 통계 주석
avg3, std3 = np.mean(실적_리스트[-3:]), np.std(실적_리스트[-3:])
avg5, std5 = np.mean(실적_리스트), np.std(실적_리스트)

st.markdown(f"""
<div class="guide-box">
    <span class="guide-title">📑 실적 분석 참고내용</span>
    • <b>과거 3개년 실적 분석결과:</b> 평균 {avg3:.3f}, 표준편차 {std3:.3f}, 연평균 증가율 {((실적_리스트[-1]/실적_리스트[-3])**(1/2)-1)*100:.2f}%<br>
    • <b>과거 5개년 실적 분석결과:</b> 평균 {avg5:.3f}, 표준편차 {std5:.3f}, 연평균 증가율 {((실적_리스트[-1]/실적_리스트[0])**(1/4)-1)*100:.2f}%
</div>
""", unsafe_allow_html=True)

# 4. 분석 실행 및 정량 근거 가이드
st.markdown("---")
if st.button("🚀 중장기 성과 및 한계점 분석 실행"):
    기준치 = float(max(avg3, 실적_리스트[-1]) if 지표방향=="상향" else min(avg3, 실적_리스트[-1]))
    방법별 = [
        ("목표부여(2편차)", 기준치 + 2*std3 if 지표방향=="상향" else 기준치 - 2*std3),
        ("목표부여(1편차)", 기준치 + std3 if 지표방향=="상향" else 기준치 - std3),
        ("목표부여(120%)", 기준치 * 1.2 if 지표방향=="상향" else 기준치 * 0.8),
        ("목표부여(110%)", 기준치 * 1.1 if 지표방향=="상향" else 기준치 * 0.9)
    ]

    결과_데이터 = []
    오차 = max(np.std(Y), 기준치 * 0.1)
    
    for 명칭, 최고 in 방법별:
        최저 = 기준치 * 0.8 if 지표방향=="상향" else 기준치 * 1.2
        평점 = max(20.0, min(100.0, 20 + 80 * ((예상_2026 - 최저) / (최고 - 최저))))
        # 정량적 근거 산출 (Z-Score)
        z_score = (최고 - 예상_2026) / 오차 if 지표방향=="상향" else (예상_2026 - 최고) / 오차
        도전성_지수 = (z_score / 2.0) * 100
        단계 = "🏆 한계 혁신" if 도전성_지수 >= 150 else "🔥 적극 상향" if 도전성_지수 >= 80 else "📈 소극 개선" if 도전성_지수 >= 40 else "⚖️ 현상 유지"
        판정 = "⚠️ 한계" if (abs(최고 - 기준치) > (3 * std3) or abs(최고/기준치 - 1) > 0.3) else "✅ 유지"
        
        결과_데이터.append({
            "평가방법": 명칭, "지표성격": 지표방향, "기준치": 기준치, "최고목표": 최고,
            "예상평점": 평점, "가중치": 가중치_값, "예상득점": 평점 * (가중치_값 / 100.0), 
            "도전성 단계": 단계, "추세치 분석결과": 판정, "Z-Score": round(z_score, 3)
        })

    st.subheader("2. 평가방법별 비교 분석 결과 및 임계점 진단")
    st.table(pd.DataFrame(결과_데이터).style.format({
        "기준치": "{:.3f}", "최고목표": "{:.3f}", "예상평점": "{:.2f}", "가중치": "{:.3f}", "예상득점": "{:.3f}"
    }))

    # [중요] 정량적 근거 가이드 섹션
    st.markdown("""
    <div class="guide-box">
        <span class="guide-title">💡 도전성 단계 판정의 정량적 근거 (Quantitative Basis)</span>
        본 분석기는 목표치의 도전성을 판단하기 위해 <b>Z-Score(표준점수)</b> 모델을 사용합니다.<br>
        • <b>산출식:</b> <span class="formula">도전성 지수 = {(목표치 - 예상실적) / 과거변동성(σ)} / 2.0 × 100</span><br><br>
        <b>[정량적 등급 기준]</b><br>
        • 🏆 <b>한계 혁신 (150%↑)</b>: 목표치가 예상 실적보다 표준편차의 3배(<span class="formula">3σ</span>) 이상 높은 경우 (통계적 발생 확률 0.3% 미만)<br>
        • 🔥 <b>적극 상향 (80%~150%)</b>: 목표치가 과거 변동폭의 1.6배~3배 수준으로, 공격적인 성장이 필요한 경우<br>
        • 📈 <b>소극 개선 (40%~80%)</b>: 목표치가 과거 변동 범위 내에 존재하며, 일반적인 추세를 유지하는 경우<br>
        • ⚖️ <b>현상 유지 (40%↓)</b>: 목표치가 예상 실적과 유사하거나 과거 평균 수준에 머무르는 경우
    </div>
    """, unsafe_allow_html=True)

    # 그래프 시뮬레이션
    st.subheader("3. 2029년 중장기 전망 및 목표 수준 시뮬레이션")
    fig, ax = plt.subplots(figsize=(11, 5))
    연도_축 = [f"'{y-2000}" for y in range(2021, 2030)]
    ax.plot(연도_축, slope * np.arange(9) + intercept, color='#CBD5E0', linestyle='--', label='중장기 추세선')
    ax.plot(연도_축[:5], Y[:5], marker='o', color='#2D6A4F', linewidth=2.5, label='과거 실적')
    ax.scatter(연도_축[5], 예상_2026, color='#D69E2E', s=200, marker='D', zorder=10, label='2026 예상')
    for i, row in pd.DataFrame(결과_데이터).iterrows():
        ax.scatter(연도_축[5], row['최고목표'], s=120, edgecolors='black', label=f"{row['평가방법']}")
    ax.legend(prop=font_prop, loc='upper left', bbox_to_anchor=(1.0, 1.0))
    st.pyplot(fig)
