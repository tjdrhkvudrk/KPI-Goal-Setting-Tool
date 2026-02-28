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
st.set_page_config(page_title="경영평가 지표 시뮬레이터", layout="wide")
현재_연도 = 2026
과거_연도_리스트 = [현재_연도 - i for i in range(5, 0, -1)]

st.title("⚖️ 경영평가 계량지표 통합 시뮬레이터")

# 공통 표 디자인 CSS (가운데 정렬 및 헤더 강조)
st.markdown("""
<style>
    .reportview-container .main .block-container { max-width: 1200px; }
    .stTable, table { width: 100%; border-collapse: collapse; }
    th { background-color: #4A5568 !important; color: white !important; text-align: center !important; font-size: 13px; }
    td { text-align: center !important; vertical-align: middle !important; font-size: 14px; border: 1px solid #dee2e6; }
    tr:nth-child(even) { background-color: #f8f9fa; }
</style>
""", unsafe_allow_html=True)

# 3. 사이드바 설정
st.sidebar.header("📍 지표 기본 설정")
지표명 = st.sidebar.text_input("지표명", value="주요사업 성과지표")
가중치 = st.sidebar.number_input("가중치(Weight)", value=5.000, format="%.3f")
지표방향 = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

# 4. 실적 데이터 입력부
st.subheader("1. 실적 데이터 입력 및 기초 통계")

# 입력란을 위한 컬럼 배치
입력_열 = st.columns(6)
실적_리스트 = []
for i, 연도 in enumerate(과거_연도_리스트):
    with 입력_열[i if i < 6 else i-6]:
        값 = st.number_input(f"{연도}년 실적", value=100.0 + (i*5), format="%.3f", key=f"실적_{i}")
        실적_리스트.append(값)

# 통계치 계산
삼개년_평균 = np.mean(실적_리스트[-3:])
직전년도_실적 = 실적_리스트[-1]
표준편차 = np.std(실적_리스트)
기준치 = max(삼개년_평균, 직전년도_실적) if 지표방향 == "상향" else min(삼개년_평균, 직전년도_실적)

# [복원/디자인 일치] 1번 표: 실적 요약 및 기준치 산정 표
st.markdown("##### [실적 요약 및 기준치 산정]")
입력_요약_df = pd.DataFrame({
    "구분": ["데이터"],
    "3개년 평균": [삼개년_평균],
    "직전년도 실적": [직전년도_실적],
    "5개년 표준편차": [표준편차],
    "당해년도 기준치": [기준치],
    "2026년 예상실적": [기준치 * 1.05] # 초기값
})
# 사용자가 수정할 수 있도록 예상실적만 별도 입력 처리
예상실적 = st.number_input("🎯 2026년 최종 예상실적 확정", value=기준치 * 1.05, format="%.3f")
입력_요약_df["2026년 예상실적"] = 예상실적

st.table(입력_요약_df.style.format("{:.3f}").set_properties(**{'text-align': 'center'}))

# 5. 분석 실행
st.markdown("---")
if st.button("🚀 통합 성과 분석 실행"):
    # 도전성 지수용 통계
    X = np.array([1, 2, 3, 4, 5])
    Y = np.array(실적_리스트)
    slope, intercept = np.polyfit(X, Y, 1)
    추세치 = slope * 6 + intercept
    오차 = max(np.std(Y), 기준치 * 0.1)
    상향_여부 = (지표방향 == "상향")
    
    방법별_설정 = [
        ("목표부여(2편차)", 기준치 + 2*표준편차 if 상향_여부 else 기준치 - 2*표준편차),
        ("목표부여(1편차)", 기준치 + 표준편차 if 상향_여부 else 기준치 - 표준편차),
        ("목표부여(120%)", 기준치 * 1.2 if 상향_여부 else 기준치 * 0.8),
        ("목표부여(110%)", 기준치 * 1.1 if 상향_여부 else 기준치 * 0.9)
    ]

    결과_데이터 = []
    for 명칭, 최고목표 in 방법별_설정:
        최저목표 = 기준치 * 0.8 if 상향_여부 else 기준치 * 1.2
        평점 = 20 + 80 * ((예상실적 - 최저목표) / (최고목표 - 최저목표))
        평점 = max(20.0, min(100.0, 평점))
        득점 = 평점 * (가중치 / 100.0)
        
        지수 = (최고목표 - 추세치) / 오차 if 상향_여부 else (추세치 - 최고목표) / 오차
        도전성 = (지수 / 2.0) * 100
        단계 = "🏆 한계 혁신" if 도전성 >= 150 else "🔥 적극 상향" if 도전성 >= 80 else "📈 소극 개선" if 도전성 >= 40 else "⚖️ 현상 유지" if 도전성 >= 0 else "⚠️ 하향 설정"
        
        결과_데이터.append({
            "평가방법": 명칭,
            "3개년 평균": 삼개년_평균,
            "직전년 실적": 직전년도_실적,
            "기준치": 기준치,
            "최저목표": 최저목표,
            "최고목표": 최고목표,
            "예상평점": 평점,
            "가중치": 가중치,
            "예상득점": 득점,
            "도전성 단계": 단계
        })

    df = pd.DataFrame(결과_데이터)

    # [복원/디자인 일치] 2. 평가방법별 비교 분석 결과 표
    st.subheader("2. 평가방법별 비교 분석 결과")
    st.table(df.style.format({
        "3개년 평균": "{:.3f}", "직전년 실적": "{:.3f}", "기준치": "{:.3f}", 
        "최저목표": "{:.3f}", "최고목표": "{:.3f}", "예상평점": "{:.2f}", 
        "가중치": "{:.2f}", "예상득점": "{:.3f}"
    }))
    
    # 도전성 단계 설명
    st.markdown("""
    <div style='background-color: #f1f3f5; padding: 12px; border-radius: 8px; font-size: 13px; color: #495057; border: 1px solid #dee2e6;'>
        <b>💡 도전성 단계 설명:</b> 최고목표가 과거 추세치(Trend) 대비 얼마나 멀리 설정되었는지 측정합니다. (높을수록 만점 달성이 어렵지만 도전적임)
    </div>
    """, unsafe_allow_html=True)

    # 3. 통합 시각화 그래프 (디자인 유지)
    st.subheader("3. 목표 대비 성과 위치 시각화")
    fig, ax = plt.subplots(figsize=(10, 4.5))
    
    연도_라벨 = [f"{y}년" for y in 과거_연도_리스트] + ["26년(예)"]
    전체_실적 = 실적_리스트 + [예상실적]
    
    ax.plot(연도_라벨[:-1], 실적_리스트, marker='o', color='#2c3e50', linewidth=3, label='과거 실적')
    ax.plot(연도_라벨[-2:], 전체_실적[-2:], marker='D', markersize=10, color='#e74c3c', linestyle='--', linewidth=2, label='26년 예상')

    colors = ['#1abc9c', '#3498db', '#9b59b6', '#f39c12']
    for i, row in df.iterrows():
        ax.scatter("26년(예)", row['최고목표'], color=colors[i], s=180, edgecolors='white', zorder=5, label=f"{row['평가방법']} 만점 ({row['최고목표']:.2f})")

    ax.axhline(기준치, color='#bdc3c7', linestyle=':', label=f'기준치 ({기준치:.2f})')
    ax.grid(True, axis='y', alpha=0.2)
    ax.legend(prop=font_prop, loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=False)
    
    plt.tight_layout()
    st.pyplot(fig)
