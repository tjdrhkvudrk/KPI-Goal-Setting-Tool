import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import requests

# 1. 한글 폰트 및 페이지 설정
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

st.set_page_config(page_title="성과지표 도전적 목표설정 시뮬레이터", layout="wide")

# 2. 디자인 CSS (폰트 15px, 강조 레이아웃)
st.markdown("""
<style>
    th { background-color: #4A5568 !important; color: white !important; font-size: 15px !important; font-weight: bold !important; text-align: center !important; border: 1px solid #dee2e6 !important; }
    td { font-size: 15px !important; font-weight: normal !important; text-align: center !important; border: 1px solid #dee2e6 !important; background-color: white !important; }
    div[data-testid="stNumberInput"] input { font-size: 15px !important; font-weight: normal !important; height: 42px !important; text-align: center !important; }
    .header-box { color: white; padding: 10px; text-align: center; font-weight: bold; font-size: 15px !important; border: 1px solid #dee2e6; min-height: 46px; display: flex; align-items: center; justify-content: center; }
    .highlight-input input { background-color: #FFFBEB !important; font-weight: bold !important; color: #D69E2E !important; border: 1px solid #D69E2E !important; }
    .advice-box { background-color: #F0F7FF; padding: 20px; border-radius: 10px; border-left: 5px solid #2B6CB0; margin: 10px 0; }
    [data-testid="column"] { gap: 0rem !important; }
</style>
""", unsafe_allow_html=True)

st.title("🎯 도전적 성과목표 설정 및 논리 근거 시뮬레이터")
st.info("💡 이 도구는 평가위원에게 제출할 '도전적 목표 설정의 논리적 근거'를 확보하기 위해 설계되었습니다.")

# 3. 데이터 입력 영역
st.sidebar.header("📍 지표 기본 설정")
가중치_값 = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
지표방향 = st.sidebar.selectbox("지표 방향", ["상향(실적 높을수록 좋음)", "하향(수치 낮을수록 좋음)"])
방향_key = "상향" if "상향" in 지표방향 else "하향"

st.subheader("1. 과거 실적 입력 및 기준치 산정")
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

# 통계 계산
평균_3년 = float(np.mean(실적_리스트[-4:-1]))
직전_실적 = float(실적_리스트[-2])
표준편차_3년 = float(np.std(실적_리스트[-4:-1]))
기준치 = float(max(평균_3년, 직전_실적) if 방향_key=="상향" else min(평균_3년, 직전_실적))

# 4. 분석 실행
st.markdown("---")
if st.button("🚀 도전성 분석 및 목표 시뮬레이션 실행"):
    st.success("분석이 완료되었습니다. 아래의 '도전적 목표 설정 근거'를 활용하세요.")

    # 평가방법별 계산
    방법별_설정 = [
        ("표준편차법(2σ)", 기준치 + 2*표준편차_3년 if 방향_key=="상향" else 기준치 - 2*표준편차_3년, "#1abc9c"),
        ("표준편차법(1σ)", 기준치 + 표준편차_3년 if 방향_key=="상향" else 기준치 - 표준편차_3년, "#3498db"),
        ("과거성장률법(120%)", 기준치 * 1.2 if 방향_key=="상향" else 기준치 * 0.8, "#9b59b6"),
        ("과거성장률법(110%)", 기준치 * 1.1 if 방향_key=="상향" else 기준치 * 0.9, "#f39c12")
    ]

    결과_데이터 = []
    X = np.array([1, 2, 3, 4, 5])
    Y = np.array(실적_리스트[:-1])
    slope, intercept = np.polyfit(X, Y, 1)
    추세치 = slope * 6 + intercept
    오차 = max(np.std(Y), 기준치 * 0.1)

    for 명칭, 최고, 색상 in 방법별_설정:
        최저 = 기준치 * 0.8 if 방향_key=="상향" else 기준치 * 1.2
        평점 = max(20.0, min(100.0, 20 + 80 * ((예상실적_입력 - 최저) / (최고 - 최저))))
        
        # 도전성 지수(zp) 계산
        zp = (최고 - 추세치) / 오차 if 방향_key=="상향" else (추세치 - 최고) / 오차
        도전성_지수 = (zp / 2.0) * 100
        
        if 도전성_지수 >= 100: 단계 = "🏆 한계 혁신"
        elif 도전성_지수 >= 60: 단계 = "🔥 적극 상향"
        else: 단계 = "⚖️ 현상 유지"
        
        결과_데이터.append({
            "평가방법": 명칭, "지표성격": 방향_key, "기준치": 기준치, "최저목표": 최저, "최고목표": 최고,
            "예상평점": 평점, "가중치": 가중치_값, "예상득점": 평점 * (가중치_값 / 100.0), "도전성 단계": 단계, "색상": 색상
        })

    df_res = pd.DataFrame(결과_데이터)

    # [핵심 보완 1] 논리적 근거 요약 박스
    st.subheader("📝 평가위원 제출용: 도전적 목표 설정 근거")
    best_option = df_res.loc[df_res['최고목표'].idxmax() if 방향_key=="상향" else df_res['최고목표'].idxmin()]
    
    st.markdown(f"""
    <div class="advice-box">
        <b>[논리적 설정 근거 샘플]</b><br>
        본 지표는 과거 3개년 평균 실적과 직전년도 실적 중 더 높은 <b>{기준치:.3f}</b>를 기준치로 설정하였습니다.<br>
        객관적 목표 설정을 위해 <b>'표준편차법'</b>과 <b>'과거성장률법'</b> 2가지를 비교 분석한 결과, 
        가장 도전적인 수치인 <b>{best_option['평가방법']}</b> 기준인 <b>{best_option['최고목표']:.3f}</b>를 최종 목표로 채택하였습니다.<br>
        이는 과거 추세 대비 도전성 지수가 <b>{best_option['도전성 단계']}</b> 수준으로, 단순 현상 유지를 넘어 적극적인 성과 창출 의지를 반영한 결과입니다.
    </div>
    """, unsafe_allow_html=True)

    # [핵심 보완 2] 표 구성 최적화
    st.subheader("2. 평가방법별 비교 분석 결과")
    display_cols = ["평가방법", "기준치", "최저목표", "최고목표", "예상평점", "가중치", "예상득점", "도전성 단계"]
    st.table(df_res[display_cols].style.format({
        "기준치": "{:.3f}", "최저목표": "{:.3f}", "최고목표": "{:.3f}", "예상평점": "{:.2f}", "가중치": "{:.3f}", "예상득점": "{:.3f}"
    }))

    # [핵심 보완 3] 그래프 레이아웃 (범례 우측 배치)
    st.subheader("3. 목표 설정 도전성 시각화")
    fig, ax = plt.subplots(figsize=(10, 5))
    연도 = ["'21", "'22", "'23", "'24", "'25", "'26(예)"]
    
    ax.plot(연도[:-1], 실적_리스트[:-1], marker='o', color='#2c3e50', linewidth=2.5, label='과거 실적')
    ax.plot(연도[-2:], 실적_리스트[-2:], marker='D', markersize=8, color='#e74c3c', linestyle='--', label='2026년 예상실적')
    
    for i, row in df_res.iterrows():
        ax.scatter(연도[-1], row['최고목표'], color=row['색상'], s=150, edgecolors='white', zorder=5, 
                   label=f"{row['평가방법']}: {row['최고목표']:.2f} ({row['도전성 단계']})")

    ax.axhline(기준치, color='#bdc3c7', linestyle=':', label=f'기준치: {기준치:.2f}')
    ax.legend(prop=font_prop, loc='center left', bbox_to_anchor=(1.05, 0.5), frameon=False)
    plt.subplots_adjust(right=0.7)
    st.pyplot(fig)
