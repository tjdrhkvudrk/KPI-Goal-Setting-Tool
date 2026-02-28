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

# 2. 디자인 및 표 레이아웃 설정 (15px 통일 및 열 간격 조정)
st.set_page_config(page_title="성과지표 시뮬레이터", layout="wide")
st.markdown("""
<style>
    table { width: 100% !important; table-layout: fixed !important; border-collapse: collapse; }
    th { background-color: #4A5568 !important; color: white !important; font-size: 15px !important; font-weight: bold !important; text-align: center !important; border: 1px solid #dee2e6 !important; }
    td { font-size: 15px !important; text-align: center !important; border: 1px solid #dee2e6 !important; background-color: white !important; height: 40px; }
    /* 구분 열 강조 */
    td:first-child, th:first-child { width: 120px !important; background-color: #EDF2F7 !important; font-weight: bold; }
    
    div[data-testid="stNumberInput"] input { font-size: 15px !important; text-align: center !important; height: 42px !important; }
    .header-box { color: white; padding: 10px; text-align: center; font-weight: bold; font-size: 15px !important; border: 1px solid #dee2e6; min-height: 46px; display: flex; align-items: center; justify-content: center; }
    .highlight-input input { background-color: #FFFBEB !important; font-weight: bold !important; color: #D69E2E !important; border: 1px solid #D69E2E !important; }
    .logic-box { background-color: #F8FAFC; padding: 20px; border: 1px solid #E2E8F0; border-radius: 10px; margin-top: 30px; border-left: 5px solid #4A5568; }
</style>
""", unsafe_allow_html=True)

st.title("🎯 성과지표 목표설정 및 도전성 분석 시뮬레이터")

# 3. 데이터 입력 영역
st.sidebar.header("📍 지표 기본 설정")
가중치_값 = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
지표방향 = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

st.subheader("1. 실적 데이터 입력 및 기초 통계")
cols = st.columns(6)
titles = ["2021년 실적", "2022년 실적", "2023년 실적", "2024년 실적", "2025년 실적", "2026년 예상 실적"]
실적_리스트 = []

for i in range(6):
    with cols[i]:
        bg_color = "#D69E2E" if i == 5 else "#2D6A4F" #
        st.markdown(f'<div class="header-box" style="background-color:{bg_color};">{titles[i]}</div>', unsafe_allow_html=True)
        if i < 5:
            val = st.number_input(f"v_{2021+i}", value=100.0 + (i*5), format="%.3f", label_visibility="collapsed")
            실적_리스트.append(val)
        else:
            st.markdown('<div class="highlight-input">', unsafe_allow_html=True)
            예상실적_입력 = st.number_input("v_2026", value=실적_리스트[-1] * 1.05, format="%.3f", label_visibility="collapsed")
            실적_리스트.append(예상실적_입력)

# 지표 계산
평균_5년 = float(np.mean(실적_리스트[:-1]))
표준편차_5년 = float(np.std(실적_리스트[:-1]))
CAGR_5년 = ((실적_리스트[-2] / 실적_리스트[0])**(1/4) - 1) * 100 if 실적_리스트[0] != 0 else 0
평균_3년 = float(np.mean(실적_리스트[-4:-1]))
표준편차_3년 = float(np.std(실적_리스트[-4:-1]))
CAGR_3년 = ((실적_리스트[-2] / 실적_리스트[-4])**(1/2) - 1) * 100 if 실적_리스트[-4] != 0 else 0
직전_실적 = float(실적_리스트[-2])
기준치 = float(max(평균_3년, 직전_실적) if 지표방향=="상향" else min(평균_3년, 직전_실적))

# 기초 통계 표 (구분 열 생성)
stats_df = pd.DataFrame({
    "과거 5개년 평균": [평균_5년], "과거 5개년 표준편차": [표준편차_5년], "과거 5개년 연평균 증가율(%)": [CAGR_5년],
    "과거 3개년 평균": [평균_3년], "과거 3개년 표준편차": [표준편차_3년], "과거 3개년 연평균 증가율(%)": [CAGR_3년]
}, index=["구분"])
st.table(stats_df.style.format("{:.3f}"))

# 4. 분석 실행
st.markdown("---")
if st.button("🚀 통합 성과 분석 실행"):
    방법별 = [
        ("목표부여(2편차)", 기준치 + 2*표준편차_3년 if 지표방향=="상향" else 기준치 - 2*표준편차_3년, "#1abc9c"),
        ("목표부여(1편차)", 기준치 + 표준편차_3년 if 지표방향=="상향" else 기준치 - 표준편차_3년, "#3498db"),
        ("목표부여(120%)", 기준치 * 1.2 if 지표방향=="상향" else 기준치 * 0.8, "#9b59b6"),
        ("목표부여(110%)", 기준치 * 1.1 if 지표방향=="상향" else 기준치 * 0.9, "#f39c12")
    ]

    # 추세선 계산 (21~25 실적 기반)
    X_axis = np.arange(5)
    Y_axis = np.array(실적_리스트[:-1])
    slope, intercept = np.polyfit(X_axis, Y_axis, 1)
    full_X = np.arange(6)
    trend_line = slope * full_X + intercept
    오차 = max(np.std(Y_axis), 기준치 * 0.1)

    결과_데이터 = []
    for 명칭, 최고, 색상 in 방법별:
        최저 = 기준치 * 0.8 if 지표방향=="상향" else 기준치 * 1.2
        평점 = max(20.0, min(100.0, 20 + 80 * ((예상실적_입력 - 최저) / (최고 - 최저))))
        
        추세예상치 = trend_line[-1]
        zp = (최고 - 추세예상치) / 오차 if 지표방향=="상향" else (추세예상치 - 최고) / 오차
        도전성_지수 = (zp / 2.0) * 100
        if 도전성_지수 >= 150: 단계 = "🏆 한계 혁신"
        elif 도전성_지수 >= 80: 단계 = "🔥 적극 상향"
        elif 도전성_지수 >= 40: 단계 = "📈 소극 개선"
        else: 단계 = "⚖️ 현상 유지"
        
        결과_데이터.append({
            "평가방법": 명칭, "지표성격": 지표방향, "과거 3개년 실적 평균값": 평균_3년,
            "직전년도 실적": 직전_실적, "기준치": 기준치, "최저목표": 최저, "최고목표": 최고,
            "예상평점": 평점, "가중치": 가중치_값, "예상득점": 평점 * (가중치_값 / 100.0), "도전성 단계": 단계, "색상": 색상
        })

    # 결과 표 (구분 열 적용)
    st.subheader("2. 평가방법별 비교 분석 결과")
    df_res = pd.DataFrame(결과_데이터)
    df_res.index = [f"{i+1}" for i in range(len(df_res))]
    df_res.index.name = "구분"
    display_cols = ["평가방법", "지표성격", "과거 3개년 실적 평균값", "직전년도 실적", "기준치", "최저목표", "최고목표", "예상평점", "가중치", "예상득점"]
    st.table(df_res[display_cols].style.format({
        "과거 3개년 실적 평균값": "{:.3f}", "직전년도 실적": "{:.3f}", "기준치": "{:.3f}",
        "최저목표": "{:.3f}", "최고목표": "{:.3f}", "예상평점": "{:.2f}", "가중치": "{:.3f}", "예상득점": "{:.3f}"
    }))

    # 시각화 (추세선 디자인 강화)
    st.subheader("3. 실적 추이 및 목표 수준 시각화")
    fig, ax = plt.subplots(figsize=(10, 5))
    연도_라벨 = ["'21", "'22", "'23", "'24", "'25", "'26(예)"]
    
    # 추세선 (과거구간 연한 실선 + 미래구간 굵은 점선)
    ax.plot(연도_라벨, trend_line, color='#A0AEC0', linestyle='--', linewidth=2, alpha=0.6, label='과거 실적 기반 추세선')
    
    # 과거 실적 (진한 남색)
    ax.plot(연도_라벨[:-1], 실적_리스트[:-1], marker='o', color='#2D3748', linewidth=3, label='과거 실적 실측치')
    
    # 2026 예상 실적 (붉은색 다이아몬드 마커로 강조)
    ax.scatter(연도_라벨[-1], 예상실적_입력, color='#E53E3E', s=250, marker='D', edgecolors='black', zorder=10, label='담당자 입력 예상실적')
    
    for i, row in df_res.iterrows():
        ax.scatter(연도_라벨[-1], row['최고목표'], color=row['색상'], s=150, edgecolors='white', zorder=5, 
                   label=f"{row['평가방법']} ({row['최고목표']:.2f})")

    ax.axhline(기준치, color='#718096', linestyle=':', label=f'당해년도 기준치 ({기준치:.2f})')
    ax.legend(prop=font_prop, loc='center left', bbox_to_anchor=(1.05, 0.5), frameon=False)
    plt.subplots_adjust(right=0.7)
    st.pyplot(fig)

    # 논리 근거 제안
    st.markdown('<div class="logic-box">', unsafe_allow_html=True)
    st.subheader("💡 목표 설정 논리적 근거 제안")
    target_idx = df_res['최고목표'].idxmax() if 지표방향=="상향" else df_res['최고목표'].idxmin()
    best = df_res.iloc[int(target_idx)-1]
    
    st.write(f"본 지표는 과거 실적의 흐름(추세선)과 변동성을 종합적으로 고려한 **{best['평가방법']}** 기준을 적용하였습니다.")
    st.write(f"과거 실적 기반 추세 예상치 대비 **{best['최고목표']:.3f}**를 최종 목표로 설정하여, 단순 실적 개선 수준을 넘어 **{best['도전성 단계']}** 수준의 의욕적인 성과 목표를 수립하였습니다.")
    st.markdown('</div>', unsafe_allow_html=True)
