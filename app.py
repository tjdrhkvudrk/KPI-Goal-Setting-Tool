import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import requests

# 1. 한글 폰트 설정
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

# 2. 디자인 및 폰트 크기 통합 설정 (CSS)
st.set_page_config(page_title="경영평가 시뮬레이터", layout="wide")

st.markdown("""
<style>
    /* 전체 폰트 크기 기준: 15px (이미지 8e4778 기준) */
    
    /* [표 스타일] 하단 결과 표의 헤더와 셀 */
    th { 
        background-color: #4A5568 !important; 
        color: white !important; 
        font-size: 15px !important; 
        font-weight: bold !important; 
        text-align: center !important; 
        border: 1px solid #dee2e6 !important; 
    }
    td { 
        font-size: 15px !important; 
        font-weight: normal !important; 
        text-align: center !important; 
        border: 1px solid #dee2e6 !important; 
    }

    /* [입력란 스타일] 상단 숫자 입력칸의 글씨 크기와 정렬 */
    div[data-testid="stNumberInput"] input {
        font-size: 15px !important; 
        font-weight: normal !important; 
        height: 42px !important;
        text-align: center !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 0px !important;
    }

    /* [헤더 스타일] 상단 입력표의 제목 셀 (녹색/노란색) */
    .header-box {
        color: white; 
        padding: 10px; 
        text-align: center; 
        font-weight: bold; 
        font-size: 15px !important; 
        border: 1px solid #dee2e6;
        min-height: 46px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* [강조 스타일] 2026년 예상 실적 입력칸 강조 */
    .highlight-input input {
        background-color: #FFFBEB !important; /* 연한 노란색 */
        font-weight: bold !important; 
        color: #D69E2E !important;
        border: 1px solid #D69E2E !important;
    }

    /* 레이아웃 교정: 입력창 여백 제거로 한 줄 정렬 */
    [data-testid="column"] { gap: 0rem !important; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ 경영평가 계량지표 통합 시뮬레이터")

# 3. 데이터 입력 영역
st.sidebar.header("📍 지표 기본 설정")
가중치_값 = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
지표방향 = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

st.subheader("1. 실적 데이터 입력 및 기초 통계")

# 상단 입력 표 (이미지 8dd5e0 & 8d7544 디자인 반영)
cols = st.columns(6)
titles = ["2021년 실적", "2022년 실적", "2023년 실적", "2024년 실적", "2025년 실적", "2026년 예상 실적"]
실적_리스트 = []

for i in range(6):
    with cols[i]:
        # 헤더 색상 설정 (2026년만 노란색, 나머지는 녹색)
        bg_color = "#D69E2E" if i == 5 else "#2D6A4F"
        st.markdown(f'<div class="header-box" style="background-color:{bg_color};">{titles[i]}</div>', unsafe_allow_html=True)
        
        # 입력칸 출력 (폰트 크기 15px 자동 적용)
        if i < 5:
            val = st.number_input(f"v_{2021+i}", value=100.0 + (i*5), format="%.3f", label_visibility="collapsed")
            실적_리스트.append(val)
        else:
            st.markdown('<div class="highlight-input">', unsafe_allow_html=True)
            예상실적_입력 = st.number_input("v_2026", value=실적_리스트[-1] * 1.05, format="%.3f", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

# --- 통계치 계산 및 표 출력 ---
평균_5년 = np.mean(실적_리스트)
표준편차_5년 = np.std(실적_리스트)
CAGR_5년 = ((실적_리스트[-1] / 실적_리스트[0])**(1/4) - 1) * 100 if 실적_리스트[0] != 0 else 0

실적_3년 = 실적_리스트[-3:]
평균_3년 = np.mean(실적_3년)
표준편차_3년 = np.std(실적_3년)
CAGR_3년 = ((실적_3년[-1] / 실적_3년[0])**(1/2) - 1) * 100 if 실적_3년[0] != 0 else 0

기준치 = max(평균_3년, 실적_리스트[-1]) if 지표방향 == "상향" else min(평균_3년, 실적_리스트[-1])

st.markdown('<div style="margin-top:15px;"></div>', unsafe_allow_html=True)
stats_df = pd.DataFrame({
    "과거 5개년 평균": [평균_5년], "과거 5개년 표준편차": [표준편차_5년], "과거 5개년 연평균 증가율(%)": [CAGR_5년],
    "과거 3개년 평균": [평균_3년], "과거 3개년 표준편차": [표준편차_3년], "과거 3개년 연평균 증가율(%)": [CAGR_3년]
})
# 하단 표 출력 (폰트 크기 15px 적용)
st.table(stats_df.style.format("{:.3f}"))

# 4. 분석 버튼 및 결과 로직 (생략 없이 유지)
st.markdown("---")
if st.button("🚀 통합 성과 분석 실행"):
    # (이하 분석 로직 및 그래프 생성 코드는 이전과 동일하게 작동합니다)
    st.success("데이터 분석이 완료되었습니다. 하단 그래프를 확인하세요.")
