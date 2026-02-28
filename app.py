import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import requests

# 1. 한글 폰트 완벽 해결 (폰트 파일 다운로드 및 강제 지정)
@st.cache_resource
def load_korean_font():
    # 고해상도 한글 폰트 다운로드 (나눔고딕)
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
    font_path = "NanumGothic-Bold.ttf"
    
    if not os.path.exists(font_path):
        try:
            res = requests.get(font_url)
            with open(font_path, "wb") as f:
                f.write(res.content)
        except:
            pass # 실패 시 기본 폰트 사용

    if os.path.exists(font_path):
        # 폰트 매니저에 등록
        fm.fontManager.addfont(font_path)
        font_name = fm.FontProperties(fname=font_path).get_name()
        plt.rc('font', family=font_name)
    
    plt.rc('axes', unicode_minus=False) # 기호 깨짐 방지
    return font_path

# 실행
font_file = load_korean_font()
font_prop = fm.FontProperties(fname=font_file) if font_file else None

# 2. 페이지 설정 및 변수 선언 (오타 수정됨 ✅)
st.set_page_config(page_title="경영평가 지표 시뮬레이터", layout="wide")

현재_연도 = 2026 
# 에러가 났던 부분: 현재_연_ -> 현재_연도로 수정
과거_연도_리스트 = [현재_연도 - i for i in range(5, 0, -1)]

st.title("⚖️ 경영평가 계량지표 통합 시뮬레이터")

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

# 4. 분석 실행 및 통합 그래프
st.markdown("---")
if st.button("🚀 통합 성과 분석 및 그래프 생성"):
    # 통계 계산
    X = np.array([1, 2, 3, 4, 5])
    Y = np.array(실적_리스트)
    slope, intercept = np.polyfit(X, Y, 1)
    추세치 = slope * 6 + intercept
    오차 = max(np.std(Y), 기준치 * 0.1)
    표준편차 = np.std(실적_리스트)
    상향_여부 = (지표방향 == "상향")
    
    방법별_데이터 = [
        ("목표부여(2편차)", 기준치 + 2*표준편차 if 상향_여부 else 기준치 - 2*표준편차),
        ("목표부여(1편차)", 기준치 + 표준편차 if 상향_여부 else 기준치 - 표준편차),
        ("목표부여(120%)", 기준치 * 1.2 if 상향_여부 else 기준치 * 0.8),
        ("목표부여(110%)", 기준치 * 1.1 if 상향_여부 else 기준치 * 0.9)
    ]

    df = pd.DataFrame([{"평가방법": m, "최고목표": v} for m, v in 방법별_데이터])
    
    # 5. 한눈에 이해하는 통합 그래프
    st.subheader("2. 실적 추이 및 목표 수준 통합 비교")
    fig, ax = plt.subplots(figsize=(12, 7))
    
    연도_라벨 = [f"{y}년" for y in 과거_연도_리스트] + ["2026년(예상)"]
    전체_실적 = 실적_리스트 + [예상실적]
    
    # 실적 추이 (남색 선)
    ax.plot(연도_라벨[:-1], 실적_리스트, marker='o', color='#2c3e50', linewidth=4, label='과거 실적', zorder=3)
    # 예상 실적 (빨간 점선)
    ax.plot(연도_라벨[-2:], 전체_실적[-2:], marker='D', markersize=12, color='#e74c3c', linestyle='--', linewidth=3, label='우리 예상실적', zorder=4)

    # 평가방법별 목표 지점들 (색상 동그라미)
    colors = ['#1abc9c', '#3498db', '#9b59b6', '#f39c12']
    for i, row in df.iterrows():
        ax.scatter("2026년(예상)", row['최고목표'], color=colors[i], s=250, edgecolors='white', linewidth=2, zorder=5)
        # 폰트 깨짐 방지를 위해 fontproperties 적용
        ax.text("2026년(예상)", row['최고목표'], f"   {row['평가방법']} ({row['최고목표']:.2f})", 
                va='center', fontweight='bold', color=colors[i], fontproperties=font_prop)

    ax.axhline(기준치, color='#bdc3c7', linestyle=':', label='기준치')
    ax.set_title(f"<{지표명}> 통합 성과 분석", fontsize=18, pad=25, fontproperties=font_prop)
    ax.grid(True, axis='y', alpha=0.2)
    ax.legend(prop=font_prop, loc='upper left', bbox_to_anchor=(1, 1))
    
    st.pyplot(fig)

    # 6. 분석 결과 가이드
    st.success(f"현재 2026년 예상실적({예상실적:.2f})을 기준으로, 목표 점들보다 높게 위치할수록 만점 달성이 쉬워집니다!")
