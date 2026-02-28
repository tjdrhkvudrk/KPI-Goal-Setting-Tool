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

# 2. 디자인 통합 CSS (폰트 15px 고정 및 레이아웃 교정)
st.set_page_config(page_title="경영평가 시뮬레이터", layout="wide")
st.markdown("""
<style>
    th { background-color: #4A5568 !important; color: white !important; font-size: 15px !important; font-weight: bold !important; text-align: center !important; border: 1px solid #dee2e6 !important; }
    td { font-size: 15px !important; font-weight: normal !important; text-align: center !important; border: 1px solid #dee2e6 !important; background-color: white !important; }
    div[data-testid="stNumberInput"] input { font-size: 15px !important; font-weight: normal !important; height: 42px !important; text-align: center !important; }
    .header-box { color: white; padding: 10px; text-align: center; font-weight: bold; font-size: 15px !important; border: 1px solid #dee2e6; min-height: 46px; display: flex; align-items: center; justify-content: center; }
    .highlight-input input { background-color: #FFFBEB !important; font-weight: bold !important; color: #D69E2E !important; border: 1px solid #D69E2E !important; }
    [data-testid="column"] { gap: 0rem !important; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ 경영평가 계량지표 통합 시뮬레이터")

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
        bg_color = "#D69E2E" if i == 5 else "#2D6A4F"
        st.markdown(f'<div class="header-box" style="background-color:{bg_color};">{titles[i]}</div>', unsafe_allow_html=True)
        if i < 5:
            val = st.number_input(f"v_{2021+i}", value=100.0 + (i*5), format="%.3f", label_visibility="collapsed")
            실적_리스트.append(val)
        else:
            st.markdown('<div class="highlight-input">', unsafe_allow_html=True)
            예상실적_입력 = st.number_input("v_2026", value=실적_리스트[-1] * 1.05, format="%.3f", label_visibility="collapsed")
            실적_리스트.append(예상실적_입력)

# 기초 통계 계산 (오류 방지 형변환)
평균_3년 = float(np.mean(실적_리스트[-4:-1]))
직전_실적 = float(실적_리스트[-2])
표준편차_3년 = float(np.std(실적_리스트[-4:-1]))
기준치 = float(max(평균_3년, 직전_실적) if 지표방향=="상향" else min(평균_3년, 직전_실적))

stats_df = pd.DataFrame({
    "3개년 평균": [평균_3년], "직전년도 실적": [직전_실적], "3개년 표준편차": [표준편차_3년], 
    "당해년도 기준치": [기준치], "2026년 예상실적": [예상실적_입력]
})
st.table(stats_df.style.format("{:.3f}"))

# 4. 분석 실행 버튼
st.markdown("---")
if st.button("🚀 통합 성과 분석 실행"):
    st.success("데이터 분석이 완료되었습니다. 하단 결과를 확인하세요.")

    # --- 평가방법별 시뮬레이션 로직 ---
    방법별 = [
        ("목표부여(2편차)", 기준치 + 2*표준편차_3년 if 지표방향=="상향" else 기준치 - 2*표준편차_3년, "#1abc9c"),
        ("목표부여(1편차)", 기준치 + 표준편차_3년 if 지표방향=="상향" else 기준치 - 표준편차_3년, "#3498db"),
        ("목표부여(120%)", 기준치 * 1.2 if 지표방향=="상향" else 기준치 * 0.8, "#9b59b6"),
        ("목표부여(110%)", 기준치 * 1.1 if 지표방향=="상향" else 기준치 * 0.9, "#f39c12")
    ]

    결과_데이터 = []
    for 명칭, 최고, 색상 in 방법별:
        최저 = 기준치 * 0.8 if 지표방향=="상향" else 기준치 * 1.2
        평점 = max(20.0, min(100.0, 20 + 80 * ((예상실적_입력 - 최저) / (최고 - 최저))))
        결과_데이터.append({"평가방법": 명칭, "최저목표": 최저, "최고목표": 최고, "예상평점": 평점, "색상": 색상})

    # [통합 표 출력]
    df_res = pd.DataFrame(결과_데이터)
    st.subheader("2. 평가방법별 비교 분석 결과")
    st.table(df_res[["평가방법", "최저목표", "최고목표", "예상평점"]].style.format({"최저목표": "{:.3f}", "최고목표": "{:.3f}", "예상평점": "{:.2f}"}))

    # [도전성 단계 기준 안내 - image_8e4eba 디자인]
    st.markdown("""
    <div style="background-color: #f8faff; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0;">
        <p style="font-weight: bold; font-size: 15px; margin-bottom: 10px;">🔍 도전성 단계(zp) 판정 기준</p>
        <div style="display: flex; justify-content: space-around; text-align: center; font-size: 13px;">
            <div>🏆 <b>한계 혁신</b><br><span style="color: #94a3b8;">150% 이상</span></div>
            <div>🔥 <b>적격 상향</b><br><span style="color: #94a3b8;">80% ~ 150%</span></div>
            <div>📈 <b>소극 개선</b><br><span style="color: #94a3b8;">40% ~ 80%</span></div>
            <div>⚖️ <b>현상 유지</b><br><span style="color: #94a3b8;">0% ~ 40%</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # [그래프 시각화 - image_8ebf56 디자인]
    st.subheader("3. 실적 추이 및 목표 수준 시각화")
    fig, ax = plt.subplots(figsize=(12, 6))
    연도 = ["'21", "'22", "'23", "'24", "'25", "'26(예)"]
    과거실적 = 실적_리스트[:-1]
    
    # 과거 실적선
    ax.plot(연도[:-1], 과거실적, marker='o', color='#2c3e50', linewidth=3, label='과거 실적')
    # 예상 실적 연결선 (점선)
    ax.plot(연도[-2:], 실적_리스트[-2:], marker='D', markersize=10, color='#e74c3c', linestyle='--', linewidth=2, label='우리 예상실적')
    
    # 목표 부여 지점 (우측 산점도)
    for i, row in df_res.iterrows():
        ax.scatter(연도[-1], row['최고목표'], color=row['색상'], s=200, edgecolors='white', zorder=5)
        ax.text(연도[-1], row['최고목표'], f" {row['평가방법']} ({row['최고목표']:.2f})", va='center', ha='left', fontsize=10, color=row['색상'], fontweight='bold')

    ax.axhline(기준치, color='#bdc3c7', linestyle=':', linewidth=2, label=f'기준치 ({기준치:.2f})')
    ax.legend(prop=font_prop, loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
