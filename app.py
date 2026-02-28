import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import requests

# 1. 한글 폰트 완벽 로드 (나눔고딕)
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

# 2. 기본 설정
st.set_page_config(page_title="경영평가 지표 시뮬레이터", layout="wide")
현재_연도 = 2026
과거_연도_리스트 = [현재_연도 - i for i in range(5, 0, -1)]

st.title("⚖️ 경영평가 계량지표 통합 시뮬레이터")

# CSS 스타일 (표 디자인 및 가운데 정렬)
st.markdown("""
<style>
    .stTable { width: 100%; }
    .stTable td, .stTable th { text-align: center !important; vertical-align: middle !important; }
    /* 첫 번째 열(평가방법) 강조 */
    .stTable td:first-child { font-weight: bold; background-color: #f8f9fa; }
    /* 헤더 강조 */
    .stTable th { background-color: #4A5568 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 입력 UI
st.sidebar.header("📍 지표 기본 설정")
지표명 = st.sidebar.text_input("지표명", value="주요사업 성과지표")
가중치 = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
지표방향 = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

st.subheader("1. 실적 데이터 입력")
입력_열 = st.columns(9)
실적_리스트 = []
for i, 연도 in enumerate(과거_연도_리스트):
    with 입력_열[i]:
        st.write(f"**{연도}년**")
        값 = st.number_input(f"{연도}실적", label_visibility="collapsed", value=100.0 + (i*5), format="%.3f", key=f"실적_{i}")
        실적_리스트.append(값)

삼개년_평균 = np.mean(실적_리스트[-3:])
직전년도_실적 = 실적_리스트[-1]
기준치 = max(삼개년_평균, 직전년도_실적) if 지표방향 == "상향" else min(삼개년_평균, 직전년도_실적)

with 입력_열[6]: st.write("**평균**"); st.info(f"{삼개년_평균:.2f}")
with 입력_열[7]: st.write("**기준치**"); st.success(f"{기준치:.2f}")
with 입력_열[8]: st.write("**26년 예상**"); 예상실적 = st.number_input("예상", value=기준치 * 1.05, format="%.3f", label_visibility="collapsed")

# 4. 분석 실행
st.markdown("---")
if st.button("🚀 통합 성과 분석 및 시뮬레이션 실행"):
    # 통계 계산 (도전성 지수용)
    X = np.array([1, 2, 3, 4, 5])
    Y = np.array(실적_리스트)
    slope, intercept = np.polyfit(X, Y, 1)
    추세치 = slope * 6 + intercept
    오차 = max(np.std(Y), 기준치 * 0.1)
    
    표준편차 = np.std(실적_리스트)
    상향_여부 = (지표방향 == "상향")
    
    방법별_설정 = [
        ("목표부여(2편차)", 기준치 + 2*표준편차 if 상향_여부 else 기준치 - 2*표준편차),
        ("목표부여(1편차)", 기준치 + 표준편차 if 상향_여부 else 기준치 - 표준편차),
        ("목표부여(120%)", 기준치 * 1.2 if 상향_여부 else 기준치 * 0.8),
        ("목표부여(110%)", 기준치 * 1.1 if 상향_여부 else 기준치 * 0.9)
    ]

    결과_데이터 = []
    for 명칭, 최고목표 in 방법별_설정:
        # 평점 계산 (최저목표는 기준치 혹은 적정 하한선으로 가정)
        최저목표 = 기준치 * 0.8 if 상향_여부 else 기준치 * 1.2
        평점 = 20 + 80 * ((예상실적 - 최저목표) / (최고목표 - 최저목표))
        평점 = max(20.0, min(100.0, 평점))
        
        # 도전성 계산
        지수 = (최고목표 - 추세치) / 오차 if 상향_여부 else (추세치 - 최고목표) / 오차
        도전성 = (지수 / 2.0) * 100
        단계 = "🏆 한계 혁신" if 도전성 >= 150 else "🔥 적극 상향" if 도전성 >= 80 else "📈 소극 개선" if 도전성 >= 40 else "⚖️ 현상 유지" if 도전성 >= 0 else "⚠️ 하향 설정"
        
        결과_데이터.append({
            "평가방법": 명칭,
            "지표성격": 지표방향,
            "3개년 평균": 삼개년_평균,
            "직전년도 실적": 직전년도_실적,
            "기준치": 기준치,
            "최고목표": 최고목표,
            "예상실적": 예상실적,
            "예상평점": 평점,
            "도전성 단계": 단계
        })

    df = pd.DataFrame(결과_데이터)

    # [복원된 부분] 2. 평가방법별 비교 분석 결과 표
    st.subheader("2. 평가방법별 비교 분석 결과")
    st.table(df.style.format({
        "3개년 평균": "{:.3f}", "직전년도 실적": "{:.3f}", "기준치": "{:.3f}", 
        "최고목표": "{:.3f}", "예상실적": "{:.3f}", "예상평점": "{:.2f}"
    }).set_properties(**{'text-align': 'center'}))

    # 3. 실적 추이 및 목표 수준 시각화
    st.subheader("3. 목표 대비 성과 위치 분석")
    
    # 그래프 사이즈 조정 및 범례 공간 확보
    fig, ax = plt.subplots(figsize=(10, 5))
    
    연도_라벨 = [f"{y}년" for y in 과거_연도_리스트] + ["2026년(예)"]
    전체_실적 = 실적_리스트 + [예상실적]
    
    ax.plot(연도_라벨[:-1], 실적_리스트, marker='o', color='#2c3e50', linewidth=3, label='과거 5개년 실적 추이', zorder=3)
    ax.plot(연도_라벨[-2:], 전체_실적[-2:], marker='D', markersize=10, color='#e74c3c', linestyle='--', linewidth=2, label='2026년 조직 예상실적', zorder=4)

    colors = ['#1abc9c', '#3498db', '#9b59b6', '#f39c12']
    for i, row in df.iterrows():
        label_text = f"{row['평가방법']} 만점기준 ({row['최고목표']:.2f})"
        ax.scatter("2026년(예)", row['최고목표'], color=colors[i], s=180, edgecolors='white', linewidth=1.5, label=label_text, zorder=5)

    ax.axhline(기준치, color='#bdc3c7', linestyle=':', linewidth=2, label=f'당해년도 설정 기준치 ({기준치:.2f})', zorder=1)
    
    ax.grid(True, axis='y', alpha=0.2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 범례 설정 (우측 바깥쪽)
    ax.legend(prop=font_prop, loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=False, labelspacing=1.2)
    
    plt.tight_layout()
    st.pyplot(fig)

    st.info(f"💡 현재 예상실적({예상실적:.2f})이 각 방법의 '만점기준' 점들보다 높은 위치에 있을수록 해당 방법 채택 시 고득점이 유리합니다.")
