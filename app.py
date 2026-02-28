import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import requests

# 1. 한글 폰트 강제 해결 (온라인 폰트 다운로드 방식)
@st.cache_resource
def load_korean_font():
    # 나눔고딕 폰트 다운로드 경로 (GitHub 저장소 활용)
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
    font_path = "NanumGothic-Bold.ttf"
    
    if not os.path.exists(font_path):
        res = requests.get(font_url)
        with open(font_path, "wb") as f:
            f.write(res.content)
    
    # 폰트 등록
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())
    plt.rc('axes', unicode_minus=False)
    return font_prop

# 폰트 로드 실행
font_prop = load_korean_font()

# 페이지 설정
st.set_page_config(page_title="경영평가 지표 시뮬레이터", layout="wide")

현재_연도 = 2026 
과거_연도_리스트 = [현재_연_ - i for i in range(5, 0, -1)]

st.title("⚖️ 경영평가 계량지표 통합 시뮬레이터")

# 2. 사이드바 설정
st.sidebar.header("📍 지표 기본 설정")
지표명 = st.sidebar.text_input("지표명", value="주요사업 성과지표")
가중치 = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
지표방향 = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

# 3. 실적 데이터 입력
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
if st.button("🚀 통합 성과 분석 실행"):
    # 도전성 계산용 통계
    X = np.array([1, 2, 3, 4, 5])
    Y = np.array(실적_리스트)
    slope, intercept = np.polyfit(X, Y, 1)
    추세치 = slope * 6 + intercept
    오차 = max(np.std(Y), 기준치 * 0.1)

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
        지수 = (최고목표 - 추세치) / 오차 if 상향_여부 else (추세치 - 최고목표) / 오차
        도전성 = (지수 / 2.0) * 100
        단계 = "🏆 한계 혁신" if 도전성 >= 150 else "🔥 적극 상향" if 도전성 >= 80 else "📈 소극 개선" if 도전성 >= 40 else "⚖️ 현상 유지" if 도전성 >= 0 else "⚠️ 하향 설정"
        결과_데이터.append({"평가방법": 명칭, "기준치": 기준치, "최고목표": 최고목표, "예상실적": 예상실적, "도전성 단계": 단계})

    df = pd.DataFrame(결과_데이터)
    
    # 결과 표 (가운데 정렬)
    st.subheader("2. 시뮬레이션 결과 요약")
    st.table(df.style.set_properties(**{'text-align': 'center'}).format({c: "{:.2f}" for c in df.columns if c not in ["평가방법", "도전성 단계"]}))

    # 5. 통합 트렌드 그래프
    st.subheader("3. 목표 대비 실적 위치 통합 분석")
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # 연도 라벨 및 데이터
    연도_라벨 = [f"{y}년" for y in 과거_연도_리스트] + ["2026년(예상)"]
    전체_데이터 = 실적_리스트 + [예상실적]
    
    # 그래프 1: 과거 실적 (진한 선)
    ax.plot(연도_라벨[:-1], 실적_리스트, marker='o', color='#34495e', linewidth=4, label='과거 실적 추이', zorder=3)
    
    # 그래프 2: 예상 실적 (빨간 점선)
    ax.plot(연도_라벨[-2:], 전체_데이터[-2:], marker='D', markersize=12, color='#e74c3c', linestyle='--', linewidth=3, label='2026년 예상실적', zorder=4)

    # 그래프 3: 평가방법별 목표 지점 (색상 점들)
    colors = ['#1abc9c', '#3498db', '#9b59b6', '#f1c40f']
    for i, row in df.iterrows():
        ax.scatter("2026년(예상)", row['최고목표'], color=colors[i], s=250, edgecolors='black', linewidth=2, zorder=5)
        # 텍스트 라벨 (깨짐 방지용 font_prop 적용)
        ax.annotate(f" {row['평가방법']}\n ({row['최고목표']:.2f})", 
                    ("2026년(예상)", row['최고목표']), 
                    xytext=(10, 0), textcoords='offset points',
                    va='center', fontsize=11, fontweight='bold', color=colors[i],
                    fontproperties=font_prop)

    # 기준치 가로선
    ax.axhline(기준치, color='#bdc3c7', linestyle=':', linewidth=2, label=f'기준치 ({기준치:.2f})', zorder=1)
    
    # 타이틀 및 축 설정 (font_prop 적용)
    ax.set_title(f"<{지표명}> 실적 추이 및 목표 수준 분석", fontsize=18, pad=25, fontweight='bold', fontproperties=font_prop)
    ax.set_ylabel("실적 수치", fontsize=13, fontproperties=font_prop)
    ax.grid(True, axis='y', alpha=0.2)
    
    # 범례 및 마감
    ax.legend(prop=font_prop, loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    st.pyplot(fig)

    # 도전성 산출방법 박스 (텍스트로 깔끔하게)
    st.markdown(f"""
    <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6;'>
        <h4 style='margin-top:0;'>💡 한눈에 분석하기</h4>
        <p>1. <b>빨간 점선(◆)</b>: 우리 조직의 현재 예상 실력입니다.</p>
        <p>2. <b>떠 있는 점들</b>: 각 평가방법을 썼을 때 만점을 받기 위해 넘어야 할 '목표'입니다.</p>
        <p style='color: #2c3e50; font-weight:bold;'>➔ 분석 결과: 예상실적(◆)이 목표 점보다 높게 있다면, 해당 평가방법을 선택하는 것이 만점 달성에 가장 유리합니다!</p>
    </div>
    """, unsafe_allow_html=True)
