import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import requests

# 1. 한글 폰트 로드
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

# 2. 페이지 설정 및 CSS 디자인
st.set_page_config(page_title="경영평가 시뮬레이터", layout="wide")

st.markdown("""
<style>
    /* 테이블 헤더 및 셀 디자인 */
    th { background-color: #4A5568 !important; color: white !important; text-align: center !important; font-size: 15px !important; }
    td { text-align: center !important; vertical-align: middle !important; font-size: 15px !important; }
    
    /* 과거 실적 입력란(작게) */
    div[data-testid="column"]:nth-child(-n+5) input {
        font-size: 14px !important;
        height: 35px !important;
    }
    div[data-testid="column"]:nth-child(-n+5) label p {
        font-size: 13px !important;
        font-weight: normal !important;
    }
    
    /* 2026년 예상 실적 입력란 (강조색상) */
    div[data-testid="column"]:nth-child(6) input {
        background-color: #EBF8FF !important; /* 연한 파란색 */
        border: 2px solid #3182CE !important;
        font-size: 18px !important;
        font-weight: bold !important;
        height: 45px !important;
    }
    div[data-testid="column"]:nth-child(6) label p {
        font-size: 16px !important;
        font-weight: bold !important;
        color: #2B6CB0 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ 경영평가 계량지표 통합 시뮬레이터")

# 3. 실적 데이터 입력 (한 줄 배치)
st.sidebar.header("📍 지표 기본 설정")
가중치_값 = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
지표방향 = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

st.subheader("1. 실적 데이터 입력 및 기초 통계")

# 입력란을 6개 열로 구성 (과거 5년 + 2026년 예상)
입력_열 = st.columns(6)
과거_연도 = [2021, 2022, 2023, 2024, 2025]
실적_리스트 = []

for i, 연도 in enumerate(과거_연도):
    with 입력_열[i]:
        값 = st.number_input(f"{연도} 실적", value=100.0 + (i*5), format="%.3f", key=f"v_{연도}")
        실적_리스트.append(값)

with 입력_열[5]:
    # 2026년 예상 실적 (강조된 입력칸)
    예상실적_입력 = st.number_input("2026년 예상", value=실적_리스트[-1] * 1.05, format="%.3f", key="v_2026")

# --- 통계치 계산 ---
# 5개년 지표
평균_5년 = np.mean(실적_리스트)
표준편차_5년 = np.std(실적_리스트)
CAGR_5년 = ((실적_리스트[-1] / 실적_리스트[0])**(1/4) - 1) * 100 if 실적_리스트[0] != 0 else 0

# 3개년 지표
실적_3년 = 실적_리스트[-3:]
평균_3년 = np.mean(실적_3년)
표준편차_3년 = np.std(실적_3년)
CAGR_3년 = ((실적_3년[-1] / 실적_3년[0])**(1/2) - 1) * 100 if 실적_3년[0] != 0 else 0

# 기준치 산정 (상향 시 max, 하향 시 min)
기준치 = max(평균_3년, 실적_리스트[-1]) if 지표방향 == "상향" else min(평균_3년, 실적_리스트[-1])

# [요청 반영] 재구성된 통계 표
stats_df = pd.DataFrame({
    "과거 5개년 평균": [평균_5년],
    "과거 5개년 표준편차": [표준편차_5년],
    "과거 5개년 연평균 증가율(%)": [CAGR_5년],
    "과거 3개년 평균": [평균_3년],
    "과거 3개년 표준편차": [표준편차_3년],
    "과거 3개년 연평균 증가율(%)": [CAGR_3년]
})
st.table(stats_df.style.format("{:.3f}"))

# 4. 분석 실행
st.markdown("---")
if st.button("🚀 통합 성과 분석 실행"):
    X = np.array([1, 2, 3, 4, 5])
    Y = np.array(실적_리스트)
    slope, intercept = np.polyfit(X, Y, 1)
    추세치 = slope * 6 + intercept
    오차 = max(np.std(Y), 기준치 * 0.1)
    
    방법별 = [
        ("목표부여(2편차)", 기준치 + 2*표준편차_3년 if 지표방향=="상향" else 기준치 - 2*표준편차_3년),
        ("목표부여(1편차)", 기준치 + 표준편차_3년 if 지표방향=="상향" else 기준치 - 표준편차_3년),
        ("목표부여(120%)", 기준치 * 1.2 if 지표방향=="상향" else 기준치 * 0.8),
        ("목표부여(110%)", 기준치 * 1.1 if 지표방향=="상향" else 기준치 * 0.9)
    ]

    결과_데이터 = []
    for 명칭, 최고 in 방법별:
        최저 = 기준치 * 0.8 if 지표방향=="상향" else 기준치 * 1.2
        평점 = max(20.0, min(100.0, 20 + 80 * ((예상실적_입력 - 최저) / (최고 - 최저))))
        득점 = 평점 * (가중치_값 / 100.0)
        
        zp = (최고 - 추세치) / 오차 if 지표방향=="상향" else (추세치 - 최고) / 오차
        도전성_지수 = (zp / 2.0) * 100
        
        if 도전성_지수 >= 150: 단계 = "🏆 한계 혁신"
        elif 도전성_지수 >= 80: 단계 = "🔥 적극 상향"
        elif 도전성_지수 >= 40: 단계 = "📈 소극 개선"
        elif 도전성_지수 >= 0: 단계 = "⚖️ 현상 유지"
        else: 단계 = "⚠️ 하향 설정"
        
        결과_데이터.append({
            "평가방법": 명칭, "평균(3년)": 평균_3년, "직전년 실적": 실적_리스트[-1], "기준치": 기준치,
            "최저목표": 최저, "최고목표": 최고, "예상평점": 평점, "예상득점": 득점, "도전성 단계": 단계
        })

    st.subheader("2. 평가방법별 비교 분석 결과")
    df_res = pd.DataFrame(결과_데이터)
    st.table(df_res.style.format({
        "평균(3년)": "{:.3f}", "직전년 실적": "{:.3f}", "기준치": "{:.3f}",
        "최저목표": "{:.3f}", "최고목표": "{:.3f}", "예상평점": "{:.2f}", "예상득점": "{:.3f}"
    }))

    # 도전성 단계 판정 기준 (한 줄 레이아웃)
    st.markdown("""
    <div style="background-color: #f8faff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-top: 15px;">
        <p style="margin-bottom: 15px;">
            <span style="font-size: 16px; font-weight: bold; color: #2d3748;">🔍 도전성 단계(zp) 판정 기준</span>
            <span style="font-size: 13px; color: #718096; margin-left: 10px;">: 최고목표가 과거 추세 대비 얼마나 도전적인지 판정합니다.</span>
        </p>
        <div style="display: flex; justify-content: space-between; align-items: center; text-align: center;">
            <div style="flex: 1;"><strong>🏆 한계 혁신</strong><br><span style="font-size: 12px; color: #94a3b8;">150% 이상</span></div>
            <div style="width: 1px; height: 30px; background-color: #e2e8f0;"></div>
            <div style="flex: 1;"><strong>🔥 적극 상향</strong><br><span style="font-size: 12px; color: #94a3b8;">80% ~ 150%</span></div>
            <div style="width: 1px; height: 30px; background-color: #e2e8f0;"></div>
            <div style="flex: 1;"><strong>📈 소극 개선</strong><br><span style="font-size: 12px; color: #94a3b8;">40% ~ 80%</span></div>
            <div style="width: 1px; height: 30px; background-color: #e2e8f0;"></div>
            <div style="flex: 1;"><strong>⚖️ 현상 유지</strong><br><span style="font-size: 12px; color: #94a3b8;">0% ~ 40%</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5. 시각화
    st.subheader("3. 실적 추이 및 목표 수준 시각화")
    fig, ax = plt.subplots(figsize=(11, 5))
    연도_축 = ["2021", "2022", "2023", "2024", "2025", "2026(예)"]
    전체_데이터 = 실적_리스트 + [예상실적_입력]
    
    ax.plot(연도_축[:-1], 실적_리스트, marker='o', color='#2c3e50', linewidth=3, label='과거 실적')
    ax.plot(연도_축[-2:], 전체_데이터[-2:], marker='D', markersize=10, color='#e74c3c', linestyle='--', linewidth=2, label='우리 예상실적')
    
    colors = ['#1abc9c', '#3498db', '#9b59b6', '#f39c12']
    for i, row in df_res.iterrows():
        ax.scatter("2026(예)", row['최고목표'], color=colors[i], s=200, edgecolors='white', zorder=5, label=f"{row['평가방법']} ({row['최고목표']:.2f})")
    
    ax.axhline(기준치, color='#bdc3c7', linestyle=':', linewidth=2, label=f'기준치 ({기준치:.2f})')
    ax.legend(prop=font_prop, loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=False)
    plt.tight_layout()
    st.pyplot(fig)
