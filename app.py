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

# 2. 디자인 및 열 간격 최적화 CSS
st.set_page_config(page_title="성과지표 시뮬레이터", layout="wide")
st.markdown("""
<style>
    /* 표의 열 간격을 균등하게 배분 (table-layout: fixed) */
    table { width: 100% !important; table-layout: fixed !important; }
    th, td { 
        font-size: 15px !important; 
        text-align: center !important; 
        border: 1px solid #dee2e6 !important; 
        word-break: keep-all !important; /* 텍스트가 길어도 열 너비 유지 */
    }
    th { background-color: #4A5568 !important; color: white !important; font-weight: bold !important; }
    td { background-color: white !important; }
    
    div[data-testid="stNumberInput"] input { font-size: 15px !important; text-align: center !important; height: 42px !important; }
    .header-box { color: white; padding: 10px; text-align: center; font-weight: bold; font-size: 15px !important; border: 1px solid #dee2e6; min-height: 46px; display: flex; align-items: center; justify-content: center; }
    .highlight-input input { background-color: #FFFBEB !important; font-weight: bold !important; color: #D69E2E !important; border: 1px solid #D69E2E !important; }
    .logic-box { background-color: #F8FAFC; padding: 20px; border: 1px solid #E2E8F0; border-radius: 10px; margin-top: 30px; }
    [data-testid="column"] { gap: 0rem !important; }
</style>
""", unsafe_allow_html=True)

st.title("🎯 성과지표 목표설정 및 도전성 분석 시뮬레이터")

# 3. 데이터 입력 및 기초 통계 (요청 사항 반영)
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
# [요청 반영] 과거 3개년 연평균 증가율 추가
CAGR_3년 = ((실적_리스트[-2] / 실적_리스트[-4])**(1/2) - 1) * 100 if 실적_리스트[-4] != 0 else 0
직전_실적 = float(실적_리스트[-2])
기준치 = float(max(평균_3년, 직전_실적) if 지표방향=="상향" else min(평균_3년, 직전_실적))

# [요청 반영] 당해년도 기준치 삭제 및 연평균 증가율 포함
stats_df = pd.DataFrame({
    "과거 5개년 평균": [평균_5년], "과거 5개년 표준편차": [표준편차_5년], "과거 5개년 연평균 증가율(%)": [CAGR_5년],
    "과거 3개년 평균": [평균_3년], "과거 3개년 표준편차": [표준편차_3년], "과거 3개년 연평균 증가율(%)": [CAGR_3년]
})
st.table(stats_df.style.format("{:.3f}"))

# 4. 분석 실행 및 결과
st.markdown("---")
if st.button("🚀 통합 성과 분석 실행"):
    # "완료되었습니다" 문구 삭제 [요청 반영]

    방법별 = [
        ("목표부여(2편차)", 기준치 + 2*표준편차_3년 if 지표방향=="상향" else 기준치 - 2*표준편차_3년, "#1abc9c"),
        ("목표부여(1편차)", 기준치 + 표준편차_3년 if 지표방향=="상향" else 기준치 - 표준편차_3년, "#3498db"),
        ("목표부여(120%)", 기준치 * 1.2 if 지표방향=="상향" else 기준치 * 0.8, "#9b59b6"),
        ("목표부여(110%)", 기준치 * 1.1 if 지표방향=="상향" else 기준치 * 0.9, "#f39c12")
    ]

    결과_데이터 = []
    X_vals = np.array([1, 2, 3, 4, 5])
    Y_vals = np.array(실적_리스트[:-1])
    slope, intercept = np.polyfit(X_vals, Y_vals, 1)
    추세치 = slope * 6 + intercept
    오차 = max(np.std(Y_vals), 기준치 * 0.1)

    for 명칭, 최고, 색상 in 방법별:
        최저 = 기준치 * 0.8 if 지표방향=="상향" else 기준치 * 1.2
        평점 = max(20.0, min(100.0, 20 + 80 * ((예상실적_입력 - 최저) / (최고 - 최저))))
        
        # 도전성 판정 기준
        zp = (최고 - 추세치) / 오차 if 지표방향=="상향" else (추세치 - 최고) / 오차
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

    df_res = pd.DataFrame(결과_데이터)

    st.subheader("2. 평가방법별 비교 분석 결과")
    display_cols = ["평가방법", "지표성격", "과거 3개년 실적 평균값", "직전년도 실적", "기준치", "최저목표", "최고목표", "예상평점", "가중치", "예상득점"]
    st.table(df_res[display_cols].style.format({
        "과거 3개년 실적 평균값": "{:.3f}", "직전년도 실적": "{:.3f}", "기준치": "{:.3f}",
        "최저목표": "{:.3f}", "최고목표": "{:.3f}", "예상평점": "{:.2f}", "가중치": "{:.3f}", "예상득점": "{:.3f}"
    }))

    st.subheader("3. 실적 추이 및 목표 수준 시각화")
    fig, ax = plt.subplots(figsize=(10, 5))
    연도_라벨 = ["'21", "'22", "'23", "'24", "'25", "'26(예)"]
    
    ax.plot(연도_라벨[:-1], 실적_리스트[:-1], marker='o', color='#2c3e50', linewidth=2.5, label='과거 실적')
    ax.plot(연도_라벨[-2:], 실적_리스트[-2:], marker='D', markersize=8, color='#e74c3c', linestyle='--', label='2026년 예상실적')
    
    for i, row in df_res.iterrows():
        ax.scatter(연도_라벨[-1], row['최고목표'], color=row['색상'], s=150, edgecolors='white', zorder=5, 
                   label=f"{row['평가방법']} ({row['최고목표']:.2f})")

    ax.axhline(기준치, color='#bdc3c7', linestyle=':', label=f'기준치 ({기준치:.2f})')
    ax.legend(prop=font_prop, loc='center left', bbox_to_anchor=(1.05, 0.5), frameon=False)
    
    # [오류 수정] plt.subplots_adjust(right=0.7)로 괄호 오타 수정
    plt.subplots_adjust(right=0.7)
    st.pyplot(fig)

    st.markdown('<div class="logic-box">', unsafe_allow_html=True)
    st.subheader("💡 목표 설정 논리적 근거 제안")
    target_idx = df_res['최고목표'].idxmax() if 지표방향=="상향" else df_res['최고목표'].idxmin()
    best = df_res.loc[target_idx]
    
    st.write(f"본 지표는 과거 실적의 변동성을 고려한 **{best['평가방법']}** 기준을 적용하였습니다.")
    st.write(f"과거 3개년 평균과 직전년도 실적 중 높은 수치인 **{기준치:.3f}**를 기준치로 삼고, 이에 통계적 편차를 적용한 **{best['최고목표']:.3f}**를 최종 목표로 설정함으로써 **{best['도전성 단계']}** 수준의 도전성을 확보하였습니다.")
    st.markdown('</div>', unsafe_allow_html=True)
