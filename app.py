import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import requests

# 1. 한글 폰트 로드 (나눔고딕)
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

# 2. 페이지 설정
st.set_page_config(page_title="경영평가 시뮬레이터", layout="wide")
현재_연도 = 2026
과거_연도_리스트 = [현재_연도 - i for i in range(5, 0, -1)]

# 표 디자인 통합 CSS (가운데 정렬 및 헤더 강조)
st.markdown("""
<style>
    th { background-color: #4A5568 !important; color: white !important; text-align: center !important; }
    td { text-align: center !important; vertical-align: middle !important; }
    .stTable { width: 100%; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ 경영평가 계량지표 통합 시뮬레이터")

# 3. 입력 영역
st.sidebar.header("📍 지표 기본 설정")
지표명 = st.sidebar.text_input("지표명", value="주요사업 성과지표")
가중치_값 = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
지표방향 = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

st.subheader("1. 실적 데이터 입력 및 기초 통계")
입력_열 = st.columns(5)
실적_리스트 = []
for i, 연도 in enumerate(과거_연도_리스트):
    with 입력_열[i]:
        값 = st.number_input(f"{연도}년 실적", value=100.0 + (i*5), format="%.3f", key=f"실적_{i}")
        실적_리스트.append(값)

# 기초 통계 계산
삼개년_평균 = np.mean(실적_리스트[-3:])
직전년도_실적 = 실적_리스트[-1]
표준편차_값 = np.std(실적_리스트)
기준치 = max(삼개년_평균, 직전년도_실적) if 지표방향 == "상향" else min(삼개년_평균, 직전년도_실적)

st.markdown("##### [실적 요약 및 기준치 산정]")
예상실적_입력 = st.number_input("🎯 2026년 최종 예상실적 확정", value=기준치 * 1.05, format="%.3f")

# 1번 표 출력 (숫자 컬럼만 포맷 적용하여 에러 방지)
summary_df = pd.DataFrame({
    "3개년 평균": [삼개년_평균],
    "직전년도 실적": [직전년도_실적],
    "5개년 표준편차": [표준편차_값],
    "당해년도 기준치": [기준치],
    "2026년 예상실적": [예상실적_입력]
})
st.table(summary_df.style.format("{:.3f}"))

# 4. 분석 실행
st.markdown("---")
if st.button("🚀 통합 성과 분석 실행"):
    X = np.array([1, 2, 3, 4, 5])
    Y = np.array(실적_리스트)
    slope, intercept = np.polyfit(X, Y, 1)
    추세치 = slope * 6 + intercept
    오차 = max(np.std(Y), 기준치 * 0.1)
    상향_여부 = (지표방향 == "상향")
    
    방법별 = [
        ("목표부여(2편차)", 기준치 + 2*표준편차_값 if 상향_여부 else 기준치 - 2*표준편차_값),
        ("목표부여(1편차)", 기준치 + 표준편차_값 if 상향_여부 else 기준치 - 표준편차_값),
        ("목표부여(120%)", 기준치 * 1.2 if 상향_여부 else 기준치 * 0.8),
        ("목표부여(110%)", 기준치 * 1.1 if 상향_여부 else 기준치 * 0.9)
    ]

    결과_리스트 = []
    for 명칭, 최고 in 방법별:
        최저 = 기준치 * 0.8 if 상향_여부 else 기준치 * 1.2
        평점 = max(20.0, min(100.0, 20 + 80 * ((예상실적_입력 - 최저) / (최고 - 최저))))
        득점 = 평점 * (가중치_값 / 100.0)
        
        # 도전성 계산
        지수 = (최고 - 추세치) / 오차 if 상향_여부 else (추세치 - 최고) / 오차
        도전성_지수 = (지수 / 2.0) * 100
        단계 = "🏆 한계 혁신" if 도전성_지수 >= 150 else "🔥 적극 상향" if 도전성_지수 >= 80 else "📈 소극 개선" if 도전성_지수 >= 40 else "⚖️ 현상 유지" if 도전성_지수 >= 0 else "⚠️ 하향 설정"
        
        결과_리스트.append({
            "평가방법": 명칭,
            "3개년 평균": 삼개년_평균,
            "직전년 실적": 직전년도_실적,
            "기준치": 기준치,
            "최저목표": 최저,
            "최고목표": 최고,
            "예상평점": 평점,
            "가중치": 가중치_값,
            "예상득점": 득점,
            "도전성 단계": 단계
        })

    # 2번 표 출력
    st.subheader("2. 평가방법별 비교 분석 결과")
    df_res = pd.DataFrame(결과_리스트)
    
    # 숫자 열만 골라서 포맷팅 (에러 방지 핵심)
    num_cols = ["3개년 평균", "직전년 실적", "기준치", "최저목표", "최고목표", "예상평점", "가중치", "예상득점"]
    st.table(df_res.style.format({c: "{:.3f}" for c in num_cols if c not in ["예상평점", "가중치"]}).format({"예상평점": "{:.2f}", "가중치": "{:.2f}"}))

    # 줄표 제거된 깔끔한 설명 박스
    st.markdown("""
    <div style="background-color: #e9ecef; padding: 15px; border-radius: 10px; border-left: 5px solid #4A5568;">
        <strong>💡 도전성 단계 기준 안내</strong><br>
        최고목표가 과거 추세 대비 얼마나 도전적인지 나타내는 지표입니다.<br>
        • <strong>150% 이상</strong>: 🏆 한계 혁신 | • <strong>80% ~ 150%</strong>: 🔥 적극 상향<br>
        • <strong>40% ~ 80%</strong>: 📈 소극 개선 | • <strong>0% ~ 40%</strong>: ⚖️ 현상 유지
    </div>
    """, unsafe_allow_html=True)

    # 3. 그래프 (범례 우측 배치)
    st.subheader("3. 목표 대비 성과 위치 시각화")
    fig, ax = plt.subplots(figsize=(10, 4.5))
    연도_라벨 = [f"{y}년" for y in 과거_연도_리스트] + ["26년(예)"]
    전체_실적 = 실적_리스트 + [예상실적_입력]
    
    ax.plot(연도_라벨[:-1], 실적_리스트, marker='o', color='#2c3e50', linewidth=3, label='과거 실적')
    ax.plot(연도_라벨[-2:], 전체_실적[-2:], marker='D', markersize=10, color='#e74c3c', linestyle='--', linewidth=2, label='26년 예상')

    colors = ['#1abc9c', '#3498db', '#9b59b6', '#f39c12']
    for i, row in df_res.iterrows():
        ax.scatter("26년(예)", row['최고목표'], color=colors[i], s=180, edgecolors='white', zorder=5, label=f"{row['평가방법']} ({row['최고목표']:.2f})")

    ax.axhline(기준치, color='#bdc3c7', linestyle=':', label=f'기준치 ({기준치:.2f})')
    ax.legend(prop=font_prop, loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=False)
    plt.tight_layout()
    st.pyplot(fig)
