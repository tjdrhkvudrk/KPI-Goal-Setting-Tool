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

# 2. 디자인 설정
st.set_page_config(page_title="성과지표 시뮬레이터", layout="wide")
st.markdown("""
<style>
    html, body, [class*="st-"] { font-size: 15px !important; }
    table { width: 100% !important; table-layout: fixed !important; border-collapse: collapse; }
    th { background-color: #4A5568 !important; color: white !important; font-size: 15px !important; font-weight: bold !important; text-align: center !important; border: 1px solid #dee2e6 !important; height: 55px; }
    td { font-size: 15px !important; text-align: center !important; border: 1px solid #dee2e6 !important; background-color: white !important; height: 45px; }
    
    /* 인덱스 열 숨기기 */
    thead tr th:first-child { display: none; }
    tbody tr th { display: none; }

    div[data-testid="stNumberInput"] input { font-size: 15px !important; text-align: center !important; height: 45px !important; }
    .header-box { color: white; padding: 10px; text-align: center; font-weight: bold; font-size: 15px !important; border: 1px solid #dee2e6; min-height: 55px; display: flex; align-items: center; justify-content: center; }
    .highlight-input input { background-color: #FFFBEB !important; font-weight: bold !important; color: #D69E2E !important; }
    .auto-calc { background-color: #F7FAFC !important; color: #4A5568 !important; border: 1px solid #E2E8F0; border-radius: 4px; padding: 10px; text-align: center; font-size: 15px; font-weight: bold; height: 45px; display: flex; align-items: center; justify-content: center; }
    .footer-note { font-size: 14px; color: #4A5568; margin-top: 15px; line-height: 1.7; padding: 25px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ 중장기 성과지표 목표설정 및 한계점 분석기")

# 3. 데이터 입력 및 자동 계산
st.sidebar.header("📍 지표 기본 설정")
가중치_값 = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
지표방향 = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

st.subheader("1. 실적 데이터 입력 및 중장기 전망")
실적_리스트 = []
cols1 = st.columns(5)
for i in range(5):
    with cols1[i]:
        st.markdown(f'<div class="header-box" style="background-color:#2D6A4F;">{2021+i}년 실적</div>', unsafe_allow_html=True)
        val = st.number_input(f"v_{2021+i}", value=100.0 + (i*5), format="%.3f", key=f"v_{2021+i}", label_visibility="collapsed")
        실적_리스트.append(val)

cols2 = st.columns(4)
with cols2[0]:
    st.markdown('<div class="header-box" style="background-color:#D69E2E;">2026년 예상 실적</div>', unsafe_allow_html=True)
    st.markdown('<div class="highlight-input">', unsafe_allow_html=True)
    예상_2026 = st.number_input("v_2026", value=실적_리스트[-1] * 1.05, format="%.3f", key="v_2026_input", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

# 추세 분석 및 기초 통계
X_base = np.arange(6)
Y_base = np.array(실적_리스트 + [예상_2026])
slope, intercept = np.polyfit(X_base, Y_base, 1)

미래_실적 = []
for i, year in enumerate([2027, 2028, 2029]):
    calc_val = slope * (6 + i) + intercept
    미래_실적.append(calc_val)
    with cols2[i+1]:
        st.markdown(f'<div class="header-box" style="background-color:#4A5568;">{year}년 예상(자동)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="auto-calc">{calc_val:.3f}</div>', unsafe_allow_html=True)

전체_실적 = 실적_리스트 + [예상_2026] + 미래_실적
평균_3년 = float(np.mean(실적_리스트[-4:-1]))
표준편차_3년 = float(np.std(실적_리스트[-4:-1]))
직전_실적 = float(실적_리스트[-1])
기준치 = float(max(평균_3년, 직전_실적) if 지표방향=="상향" else min(평균_3년, 직전_실적))
중장기_CAGR = ((전체_실적[-1] / 전체_실적[0])**(1/8) - 1) * 100 if 전체_실적[0] != 0 else 0

stats_df = pd.DataFrame({
    "과거 3개년 평균": [평균_3년], "과거 3개년 표준편차": [표준편차_3년], 
    "직전년도 실적": [직전_실적], "중장기 연평균 증가율 예상치(%)": [중장기_CAGR]
})
st.table(stats_df.style.format("{:.3f}"))

# 4. 분석 실행
st.markdown("---")
if st.button("🚀 중장기 성과 및 한계점 분석 실행"):
    방법별 = [
        ("목표부여(2편차)", 기준치 + 2*표준편차_3년 if 지표방향=="상향" else 기준치 - 2*표준편차_3년),
        ("목표부여(1편차)", 기준치 + 표준편차_3년 if 지표방향=="상향" else 기준치 - 표준편차_3년),
        ("목표부여(120%)", 기준치 * 1.2 if 지표방향=="상향" else 기준치 * 0.8),
        ("목표부여(110%)", 기준치 * 1.1 if 지표방향=="상향" else 기준치 * 0.9)
    ]

    결과_데이터 = []
    오차 = max(np.std(Y_base), 기준치 * 0.1)
    추세예상치_2026 = Y_base[-1]

    for 명칭, 최고 in 방법별:
        최저 = 기준치 * 0.8 if 지표방향=="상향" else 기준치 * 1.2
        평점 = max(20.0, min(100.0, 20 + 80 * ((예상_2026 - 최저) / (최고 - 최저))))
        
        # 도전성 단계 판정
        zp = (최고 - 추세예상치_2026) / 오차 if 지표방향=="상향" else (추세예상치_2026 - 최고) / 오차
        도전성_지수 = (zp / 2.0) * 100
        if 도전성_지수 >= 150: 단계 = "🏆 한계 혁신"
        elif 도전성_지수 >= 80: 단계 = "🔥 적극 상향"
        elif 도전성_지수 >= 40: 단계 = "📈 소극 개선"
        else: 단계 = "⚖️ 현상 유지"
        
        # 한계점 판정
        diff = abs(최고 - 기준치)
        판정 = "⚠️ 한계" if (diff > (3 * 표준편차_3년) or abs(최고/기준치 - 1) > 0.3) else "✅ 유지"
            
        결과_데이터.append({
            "평가방법": 명칭, "지표성격": 지표방향, "기준치": 기준치, "최저목표": 최저, "최고목표": 최고,
            "2026년 예상 실적": 예상_2026, # [요청 반영] 자동 입력 열 추가
            "예상평점": 평점, "가중치": 가중치_값, "예상득점": 평점 * (가중치_값 / 100.0), 
            "도전성 단계": 단계, "추세치 분석결과": 판정
        })

    st.subheader("2. 평가방법별 비교 분석 결과 및 임계점 진단")
    df_res = pd.DataFrame(결과_데이터)
    # [요청 반영] 열 순서 조정: 최고목표 옆에 예상 실적 배치
    display_cols = ["평가방법", "지표성격", "기준치", "최저목표", "최고목표", "2026년 예상 실적", "예상평점", "가중치", "예상득점", "도전성 단계", "추세치 분석결과"]
    st.table(df_res[display_cols].style.format({
        "기준치": "{:.3f}", "최저목표": "{:.3f}", "최고목표": "{:.3f}", "2026년 예상 실적": "{:.3f}",
        "예상평점": "{:.2f}", "가중치": "{:.3f}", "예상득점": "{:.3f}"
    }))
    
    st.markdown("""
    <div class="footer-note">
        <b>💡 분석 지표 상세 가이드</b><br><br>
        • <b>2026년 예상 실적:</b> 상단에 입력하신 금년도 예상 성과 데이터가 자동으로 반영되어 최고목표치와 대조됩니다.<br>
        • <b>도전성 단계:</b> 과거 추세 대비 목표 상향 수준을 Z-Score로 환산한 수치입니다. (🏆 150%↑, 🔥 80%↑, 📈 40%↑)<br>
        • <b>추세치 분석결과:</b> 목표가 과거 변동성(표준편차)의 3배를 초과하거나 30% 이상 상향될 시 '⚠️ 한계'로 진단합니다.
    </div>
    """, unsafe_allow_html=True)
    
    # 그래프 시각화 생략 (코드 동일)
