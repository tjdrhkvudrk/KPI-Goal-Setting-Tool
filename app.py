import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform

# 1. 한글 폰트 강제 설정 로직
@st.cache_resource
def install_korean_fonts():
    system_name = platform.system()
    if system_name == "Windows":
        plt.rc('font', family='Malgun Gothic')
    elif system_name == "Darwin": # Mac
        plt.rc('font', family='AppleGothic')
    else: # Linux/Streamlit Cloud
        # 나눔고딕 등 폰트가 없을 경우를 대비해 최대한 기본 폰트 설정
        plt.rc('font', family='NanumGothic')
    
    plt.rc('axes', unicode_minus=False) # 마이너스 기호 깨짐 방지

install_korean_fonts()

# 페이지 설정
st.set_page_config(page_title="경영평가 지표 시뮬레이터", layout="wide")

현재_연도 = 2026 
과거_연도_리스트 = [현재_연도 - i for i in range(5, 0, -1)]

st.title("⚖️ 경영평가 계량지표 통합 시뮬레이터")

# CSS 스타일 (표 가운데 정렬 및 디자인)
st.markdown("""
<style>
    .stTable { width: 100%; }
    .stTable td, .stTable th { text-align: center !important; vertical-align: middle !important; }
    .main-header-box {
        background-color: #f0f2f6; padding: 10px; border-radius: 5px;
        text-align: center; font-weight: 800; border: 1px solid #d1d5db;
        height: 60px; margin-bottom: 5px; display: flex; align-items: center; justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# 2. 사이드바 설정
st.sidebar.header("📍 지표 기본 설정")
지표명 = st.sidebar.text_input("지표명", value="주요사업 성과지표")
가중치 = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
지표방향 = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

# 3. 실적 데이터 입력
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
if st.button("🚀 통합 성과 분석 및 시각화 실행"):
    # 도전성 계산용 통계
    X_축 = np.array([1, 2, 3, 4, 5])
    Y_축 = np.array(실적_리스트)
    기울기, 절편 = np.polyfit(X_축, Y_축, 1)
    미래_추세치 = 기울기 * 6 + 절편
    잔차 = np.sqrt(np.sum((Y_축 - (절편 + 기울기 * X_축))**2) / 3)
    보정_오차 = max(잔차 * np.sqrt(1 + 1/5 + 9/10), 기준치 * 0.1)

    상향_여부 = (지표방향 == "상향")
    표준편차 = np.std(실적_리스트)
    
    방법별_데이터 = [
        ("목표부여(2편차)", 기준치 + 2*표준편차 if 상향_여부 else 기준치 - 2*표준편차),
        ("목표부여(1편차)", 기준치 + 표준편차 if 상향_여부 else 기준치 - 표준편차),
        ("목표부여(120%)", 기준치 * 1.2 if 상향_여부 else 기준치 * 0.8),
        ("목표부여(110%)", 기준치 * 1.1 if 상향_여부 else 기준치 * 0.9)
    ]

    결과_데이터 = []
    for 명칭, 최고목표 in 방법별_데이터:
        지수 = (최고목표 - 미래_추세치) / 보정_오차 if 상향_여부 else (미래_추세치 - 최고목표) / 보정_오차
        도전성 = (지수 / 2.0) * 100
        단계 = "🏆 한계 혁신" if 도전성 >= 150 else "🔥 적극 상향" if 도전성 >= 80 else "📈 소극 개선" if 도전성 >= 40 else "⚖️ 현상 유지" if 도전성 >= 0 else "⚠️ 하향 설정"
        결과_데이터.append({"평가방법": 명칭, "기준치": 기준치, "최고목표": 최고목표, "예상실적": 예상실적, "도전성 단계": 단계})

    df = pd.DataFrame(결과_데이터)
    st.subheader("2. 시뮬레이션 결과 요약")
    st.table(df.style.set_properties(**{'text-align': 'center'}))

    # 5. 통합 트렌드 그래프 (과거+현재+미래목표 통합)
    st.subheader("3. 목표 대비 성과 위치 분석")
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # 1) 과거 실적 영역 (Line)
    연도_라벨 = [f"{y}년" for y in 과거_연도_리스트] + ["2026년(예상)"]
    전체_데이터 = 실적_리스트 + [예상실적]
    ax.plot(연도_라벨[:-1], 실적_리스트, marker='o', color='#34495e', linewidth=3, label='과거 실적 추이', zorder=3)
    
    # 2) 예상 실적 연결 (Dotted Line)
    ax.plot(연도_라벨[-2:], 전체_데이터[-2:], marker='D', markersize=10, color='#e74c3c', linestyle='--', linewidth=3, label='2026년 예상실적', zorder=4)

    # 3) 각 방법별 목표치 표시 (Scatter & Text)
    colors = ['#1abc9c', '#3498db', '#9b59b6', '#f1c40f']
    for i, row in df.iterrows():
        ax.scatter("2026년(예상)", row['최고목표'], color=colors[i], s=200, edgecolors='black', label=f"목표: {row['평가방법']}", zorder=5)
        ax.text("2026년(예상)", row['최고목표'], f"  {row['평가방법']}\n  ({row['최고목표']:.2f})", va='center', fontsize=10, fontweight='bold', color=colors[i])

    # 4) 기준치 가이드라인
    ax.axhline(기준치, color='#95a5a6', linestyle=':', linewidth=2, label=f'기준치 ({기준치:.2f})', zorder=1)
    
    # 그래프 꾸미기
    ax.set_title(f"<{지표명}> 실적 추이 및 방법별 목표 수준 통합 비교", fontsize=16, pad=20, fontweight='bold')
    ax.set_ylabel("지표 수치", fontsize=12)
    ax.grid(True, axis='y', alpha=0.3)
    ax.set_facecolor('#fdfdfd')
    
    # 범례 설정
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), frameon=True)
    
    # 여백 조정 및 출력
    plt.tight_layout()
    st.pyplot(fig)

    # 하단 분석 가이드
    st.info(f"""
    **🔍 한눈에 보는 그래프 분석**
    - **빨간 점선 끝의 다이아몬드(◆)**: 현재 우리가 예상하는 2026년 실적입니다.
    - **떠 있는 유색 점들**: 각 평가방법을 선택했을 때 '만점'을 받기 위해 달성해야 하는 최고목표입니다.
    - **분석**: 예상실적(◆)이 목표 점들보다 **위에(상향지표 기준)** 있다면 해당 방법 선택 시 만점 달성이 매우 유리합니다. 반대로 목표 점들이 너무 높이 있다면 '도전성'은 인정받으나 만점은 어려울 수 있습니다.
    """)
