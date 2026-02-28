import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform

# 1. 한글 폰트 설정 (OS별 대응)
def set_korean_font():
    system_name = platform.system()
    if system_name == "Windows":
        plt.rc('font', family='Malgun Gothic')
    elif system_name == "Darwin": # Mac
        plt.rc('font', family='AppleGothic')
    else: # Linux/Docker (Streamlit Cloud 등)
        plt.rc('font', family='NanumGothic')
    plt.rc('axes', unicode_minus=False)

set_korean_font()

# 페이지 설정
st.set_page_config(page_title="경영평가 지표 시뮬레이터", layout="wide")

현재_연도 = 2026 
과거_연도_리스트 = [현재_연도 - i for i in range(5, 0, -1)]

st.title("⚖️ 경영평가 계량지표 통합 시뮬레이터")

# CSS 스타일 (표 가운데 정렬 및 디자인)
st.markdown("""
<style>
    .stDataFrame td, .stDataFrame th { text-align: center !important; }
    .main-header-box {
        background-color: #f0f2f6; padding: 10px; border-radius: 5px;
        text-align: center; font-weight: 800; border: 1px solid #d1d5db;
        height: 60px; margin-bottom: 5px; display: flex; align-items: center; justify-content: center;
    }
    .sub-label-text {
        text-align: center; font-weight: 700; margin-bottom: 8px;
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
        st.markdown(f'<div class="sub-label-text">{연도}년</div>', unsafe_allow_html=True)
        값 = st.number_input(f"{연도}실적", label_visibility="collapsed", value=100.0 + (i*5), format="%.3f", key=f"실적_{i}")
        실적_리스트.append(값)

유효실적 = [v for v in 실적_리스트 if v > 0]
표준편차 = np.std(유효실적) if len(유효실적) > 1 else 0.0
삼개년_평균 = np.mean(실적_리스트[-3:])
직전년도_실적 = 실적_리스트[-1]
기준치 = max(삼개년_평균, 직전년도_실적) if 지표방향 == "상향" else min(삼개년_평균, 직전년도_실적)

with 입력_열[5]:
    st.markdown('<div class="sub-label-text">과거 표준편차</div>', unsafe_allow_html=True)
    st.text_input("편차", value=f"{표준편차:.3f}", label_visibility="collapsed", disabled=True)
with 입력_열[6]:
    st.markdown('<div class="sub-label-text">&nbsp;</div>', unsafe_allow_html=True) 
    st.text_input("평균", value=f"{삼개년_평균:.3f}", label_visibility="collapsed", disabled=True)
with 입력_열[7]:
    st.markdown('<div class="sub-label-text">&nbsp;</div>', unsafe_allow_html=True)
    st.text_input("기준치", value=f"{기준치:.3f}", label_visibility="collapsed", disabled=True)
with 입력_열[8]:
    st.markdown('<div class="sub-label-text">&nbsp;</div>', unsafe_allow_html=True)
    예상실적 = st.number_input("예상실적", value=기준치 * 1.05, format="%.3f", label_visibility="collapsed")

# 4. 분석 실행
st.markdown("---")
if st.button("🚀 모든 평가방법 통합 분석 실행"):
    X_축 = np.array([1, 2, 3, 4, 5])
    Y_축 = np.array(실적_리스트)
    기울기, 절편 = np.polyfit(X_축, Y_축, 1)
    미래_추세치 = 기울기 * 6 + 절편
    잔차_표준편차 = np.sqrt(np.sum((Y_축 - (절편 + 기울기 * X_축))**2) / 3)
    보정_표준오차 = max(잔차_표준편차 * np.sqrt(1 + (1/5) + (9/10)), 기준치 * 0.1)

    상향_여부 = (지표방향 == "상향")
    방법별_데이터 = [
        ("목표부여(2편차)", 기준치 + 2*표준편차, 기준치 - 2*표준편차) if 상향_여부 else ("목표부여(2편차)", 기준치 - 2*표준편차, 기준치 + 2*표준편차),
        ("목표부여(1편차)", 기준치 + 1*표준편차, 기준치 - 2*표준편차) if 상향_여부 else ("목표부여(1편차)", 기준치 - 1*표준편차, 기준치 + 2*표준편차),
        ("목표부여(120%)", 기준치 * 1.2, 기준치 * 0.8) if 상향_여부 else ("목표부여(120%)", 기준치 * 0.8, 기준치 * 1.2),
        ("목표부여(110%)", 기준치 * 1.1, 기준치 * 0.8) if 상향_여부 else ("목표부여(110%)", 기준치 * 0.9, 기준치 * 1.2)
    ]

    결과_데이터 = []
    for 명칭, 최고, 최저 in 방법별_데이터:
        평점 = 60.0 if 최고 == 최저 else 20 + 80 * ((예상실적 - 최저) / (최고 - 최저))
        평점 = max(20.0, min(100.0, 평점))
        지수 = (최고 - 미래_추세치) / 보정_표준오차 if 상향_여부 else (미래_추세치 - 최고) / 보정_표준오차
        도전성 = (지수 / 2.0) * 100
        단계 = "🏆 한계 혁신" if 도전성 >= 150 else "🔥 적극 상향" if 도전성 >= 80 else "📈 소극 개선" if 도전성 >= 40 else "⚖️ 현상 유지" if 도전성 >= 0 else "⚠️ 하향 설정"
        
        결과_데이터.append({"평가방법": 명칭, "3개년 평균": 삼개년_평균, "직전년도 실적": 직전년도_실적, "기준치": 기준치, "최고목표": 최고, "최저목표": 최저, "예상실적": 예상실적, "예상평점": 평점, "도전성 단계": 단계})

    df = pd.DataFrame(결과_데이터)
    st.subheader("2. 평가방법별 비교 분석 결과")
    st.table(df.style.format({c: "{:.3f}" for c in df.columns if c not in ["평가방법", "도전성 단계"]}).set_properties(**{'text-align': 'center'}))

    # 5. 가독성 개선된 그래프 (과거 추이 + 미래 목표)
    st.subheader("3. 실적 추이 및 목표 수준 시각화")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # [추이 그래프: 과거 5년 + 예상실적]
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        연도_라벨 = [f"{y}년" for y in 과거_연도_리스트] + ["2026년(예상)"]
        전체_실적 = 실적_리스트 + [예상실적]
        
        ax1.plot(연도_라벨[:-1], 실적_리스트, marker='o', color='#2c3e50', linewidth=2, label='과거 실적')
        ax1.plot(연도_라벨[-2:], 전체_실적[-2:], marker='D', color='#e74c3c', linestyle='--', linewidth=2, label='예상 추이')
        
        ax1.fill_between(연도_라벨[:-1], 실적_리스트, color='#ecf0f1', alpha=0.3)
        ax1.set_title(f"[{지표명}] 연도별 실적 추이", fontsize=14, pad=15)
        ax1.grid(True, axis='y', linestyle=':', alpha=0.7)
        ax1.legend()
        st.pyplot(fig1)

    with col2:
        # [비교 그래프: 방법별 최고목표 vs 기준치]
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        x = np.arange(len(df))
        bars = ax2.bar(x, df['최고목표'], color='#3498db', alpha=0.8, label='방법별 최고목표', width=0.6)
        ax2.axhline(기준치, color='#e67e22', linestyle='-', linewidth=2, label=f'기준치 ({기준치:.2f})')
        ax2.axhline(예상실적, color='#27ae60', linestyle='--', linewidth=1.5, label=f'예상실적 ({예상실적:.2f})')
        
        ax2.set_xticks(x)
        ax2.set_xticklabels(df['평가방법'], rotation=15)
        ax2.set_title("평가방법별 목표 수준 비교", fontsize=14, pad=15)
        
        # 바 위에 값 표시
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01, f'{height:.2f}', ha='center', va='bottom', fontsize=10)
            
        ax2.legend(loc='upper left', bbox_to_anchor=(1, 1))
        st.pyplot(fig2)

    # 설명 박스
    st.markdown("""
    <div style='background-color: #ffffff; padding: 15px; border: 1px solid #e6e9ef; border-radius: 5px;'>
        <p style='font-size: 0.9em; color: #666;'> 
        <b>💡 그래프 해석 가이드</b><br>
        1. <b>왼쪽 그래프</b>: 과거 5년간의 실제 흐름과 현재 내가 입력한 2026년 예상실적이 어떤 추세에 있는지 보여줍니다.<br>
        2. <b>오른쪽 그래프</b>: 각 평가방법이 제시하는 최고목표 점을 기준치/예상실적과 비교합니다. 최고목표가 예상실적보다 낮아야 만점 달성이 수월합니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
