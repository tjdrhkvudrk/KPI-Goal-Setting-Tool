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

# 2. 페이지 설정 및 레이아웃 교정 CSS
st.set_page_config(page_title="경영평가 시뮬레이터", layout="wide")

st.markdown("""
<style>
    /* 1. 하단 결과 표 디자인 (이미지 8dd5e0 기준) */
    th { background-color: #4A5568 !important; color: white !important; text-align: center !important; font-size: 15px !important; border: 1px solid #dee2e6 !important; }
    td { text-align: center !important; vertical-align: middle !important; font-size: 15px !important; border: 1px solid #dee2e6 !important; }

    /* 2. 입력 위젯 강제 한 줄 정렬 및 높이 고정 */
    [data-testid="column"] {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    
    /* 3. 입력 수치 글씨 크기를 하단 표(15px)와 완벽 일치 */
    div[data-testid="stNumberInput"] input {
        text-align: center !important;
        font-size: 15px !important; 
        height: 42px !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 0px !important;
        padding: 0px !important;
    }

    /* 4. 2026년 예상 실적 입력칸 강조 (연한 노란색 배경) */
    .highlight-input input {
        background-color: #FFFBEB !important;
        border: 1px solid #F6AD55 !important;
        font-weight: bold !important;
    }

    /* 5. 헤더 박스 디자인 (높이 통일로 줄어긋남 방지) */
    .header-box {
        color: white; 
        padding: 10px 5px; 
        text-align: center; 
        font-weight: bold; 
        font-size: 14px;
        border: 1px solid #dee2e6;
        min-height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ 경영평가 계량지표 통합 시뮬레이터")

# 3. 데이터 입력 영역
st.sidebar.header("📍 지표 기본 설정")
가중치_값 = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
지표방향 = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

st.subheader("1. 실적 데이터 입력 및 기초 통계")

# 입력 표 구성 (강제 정렬을 위해 padding 제거한 columns 사용)
cols = st.columns(6)
titles = ["2021년 실적", "2022년 실적", "2023년 실적", "2024년 실적", "2025년 실적", "2026년 예상 실적"]
실적_리스트 = []

for i in range(6):
    with cols[i]:
        # [요청 반영] 헤더 색상: 21~25년 녹색, 26년 노란색
        bg_color = "#D69E2E" if i == 5 else "#2D6A4F" # 노란색(#D69E2E) vs 녹색
        st.markdown(f'<div class="header-box" style="background-color:{bg_color};">{titles[i]}</div>', unsafe_allow_html=True)
        
        # [요청 반영] 모든 셀의 글씨 크기(15px) 및 높이 고정
        if i < 5:
            val = st.number_input(f"v_{2021+i}", value=100.0 + (i*5), format="%.3f", label_visibility="collapsed")
            실적_리스트.append(val)
        else:
            # 2026년 예상 실적 (노란색 강조 배경)
            st.markdown('<div class="highlight-input">', unsafe_allow_html=True)
            예상실적_입력 = st.number_input("v_2026", value=실적_리스트[-1] * 1.05, format="%.3f", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

# --- 통계치 계산 ---
평균_5년 = np.mean(실적_리스트)
표준편차_5년 = np.std(실적_리스트)
CAGR_5년 = ((실적_리스트[-1] / 실적_리스트[0])**(1/4) - 1) * 100 if 실적_리스트[0] != 0 else 0

실적_3년 = 실적_리스트[-3:]
평균_3년 = np.mean(실적_3년)
표준편차_3년 = np.std(실적_3년)
CAGR_3년 = ((실적_3년[-1] / 실적_3년[0])**(1/2) - 1) * 100 if 실적_3년[0] != 0 else 0

기준치 = max(평균_3년, 실적_리스트[-1]) if 지표방향 == "상향" else min(평균_3년, 실적_리스트[-1])

# 기초 통계 표 (이미지 8dd5e0 디자인 반영)
st.markdown('<div style="margin-top:10px;"></div>', unsafe_allow_html=True)
stats_df = pd.DataFrame({
    "과거 5개년 평균": [평균_5년], "과거 5개년 표준편차": [표준편차_5년], "과거 5개년 연평균 증가율(%)": [CAGR_5년],
    "과거 3개년 평균": [평균_3년], "과거 3개년 표준편차": [표준편차_3년], "과거 3개년 연평균 증가율(%)": [CAGR_3년]
})
st.table(stats_df.style.format("{:.3f}"))

# 4. 분석 실행 및 시각화 (기존 로직 동일)
st.markdown("---")
if st.button("🚀 통합 성과 분석 실행"):
    # ... (중략: 기존 분석 및 그래프 로직)
    st.info("분석이 완료되었습니다. 하단 결과를 확인하세요.")
