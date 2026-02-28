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

# 4. 분석 및 시각화
if st.button("🚀 통합 성과 분석 실행"):
    # 통계 계산
    표준편차 = np.std(실적_리스트)
    상향_여부 = (지표방향 == "상향")
    
    방법별_데이터 = [
        ("목표부여(2편차)", 기준치 + 2*표준편차 if 상향_여부 else 기준치 - 2*표준편차),
        ("목표부여(1편차)", 기준치 + 표준편차 if 상향_여부 else 기준치 - 표준편차),
        ("목표부여(120%)", 기준치 * 1.2 if 상향_여부 else 기준치 * 0.8),
        ("목표부여(110%)", 기준치 * 1.1 if 상향_여부 else 기준치 * 0.9)
    ]
    df = pd.DataFrame([{"평가방법": m, "최고목표": v} for m, v in 방법별_데이터])

    st.subheader("2. 분석 결과 시각화")
    
    # 그래프 사이즈 조정 (기존의 2/3 수준으로 축소 및 범례 공간 확보)
    fig, ax = plt.subplots(figsize=(10, 5)) # 전체 크기 축소
    
    연도_라벨 = [f"{y}년" for y in 과거_연도_리스트] + ["2026년(예)"]
    전체_실적 = 실적_리스트 + [예상실적]
    
    # 실적 선 그래프
    ax.plot(연도_라벨[:-1], 실적_리스트, marker='o', color='#2c3e50', linewidth=3, label='과거 5개년 실적 추이', zorder=3)
    ax.plot(연도_라벨[-2:], 전체_실적[-2:], marker='D', markersize=10, color='#e74c3c', linestyle='--', linewidth=2, label='2026년 조직 예상실적', zorder=4)

    # 목표 지점 (Scatter)
    colors = ['#1abc9c', '#3498db', '#9b59b6', '#f39c12']
    for i, row in df.iterrows():
        label_text = f"{row['평가방법']} 만점기준 ({row['최고목표']:.2f})"
        ax.scatter("2026년(예)", row['최고목표'], color=colors[i], s=180, edgecolors='white', linewidth=1.5, label=label_text, zorder=5)

    # 기준치 가로선
    ax.axhline(기준치, color='#bdc3c7', linestyle=':', linewidth=2, label=f'당해년도 설정 기준치 ({기준치:.2f})', zorder=1)
    
    # 그래프 디테일 (제목 제거)
    ax.grid(True, axis='y', alpha=0.2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 범례 설정 (우측 바깥쪽으로 배치, 한 줄로 길게 설명되도록)
    ax.legend(prop=font_prop, loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=False, labelspacing=1.2)
    
    plt.tight_layout()
    st.pyplot(fig)

    # 요약 표 출력
    st.markdown("---")
    st.write("**[참고] 평가방법별 목표치 요약**")
    st.dataframe(df.set_index('평가방법').T, use_container_width=True)
