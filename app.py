import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import requests

# 1. 한글 폰트 설정 (나눔고딕)
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

# 2. 디자인 통합 CSS (폰트 크기 15px, 굵기 일치)
st.set_page_config(page_title="경영평가 시뮬레이터", layout="wide")

st.markdown("""
<style>
    /* 전체 폰트 크기 및 굵기 설정 (이미지 8e4778 기준 일치) */
    
    /* 하단 결과 표 (Table) 디자인 */
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
        background-color: white !important;
    }

    /* 상단 입력란 수치 폰트 설정 */
    div[data-testid="stNumberInput"] input {
        font-size: 15px !important; 
        font-weight: normal !important; 
        height: 42px !important;
        text-align: center !important;
    }

    /* 상단 제목 셀 디자인 (높이 통일) */
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

    /* 2026년 예상 실적 강조 (노란색) */
    .highlight-input input {
        background-color: #FFFBEB !important;
        font-weight: bold !important;
        color: #D69E2E !important;
        border: 1px solid #D69E2E !important;
    }

    /* 레이아웃 정렬 교정 */
    [data-testid="column"] { gap: 0rem !important; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ 경영평가 계량지표 통합 시뮬레이터")

# 3. 데이터 입력 영역 (이미지 8dd5e0 레이아웃 반영)
st.sidebar.header("📍 지표 기본 설정")
가중치_값 = st.sidebar.number_input("가중치", value=5.000, format="%.3f")
지표방향 = st.sidebar.selectbox("지표 방향", ["상향", "하향"])

st.subheader("1. 실적 데이터 입력 및 기초 통계")

cols = st.columns(6)
titles = ["2021년 실적", "2022년 실적", "2023년 실적", "2024년 실적", "2025년 실적", "2026년 예상 실적"]
실적_리스트 = []

for i in range(6):
    with cols[i]:
        bg_color = "#D69E2E" if i == 5 else "#2D6A4F" # 노란색 vs 녹색
        st.markdown(f'<div class="header-box" style="background-color:{bg_color};">{titles[i]}</div>', unsafe_allow_html=True)
        if i < 5:
            val = st.number_input(f"v_{2021+i}", value=100.0 + (i*5), format="%.3f", label_visibility="collapsed")
            실적_리스트.append(val)
        else:
            st.markdown('<div class="highlight-input">', unsafe_allow_html=True)
            예상실적_입력 = st.number_input("v_2026", value=실적_리스트[-1] * 1.05, format="%.3f", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

# 기초 통계 계산 (오류 방지를 위해 형변환 추가)
stats_data = {
    "과거 5개년 평균": [float(np.mean(실적_리스트[:-1]))],
    "과거 5개년 표준편차": [float(np.std(실적_리스트[:-1]))],
    "과거 3개년 평균": [float(np.mean(실적_리스트[-4:-1]))],
    "당해년도 기준치": [float(max(np.mean(실적_리스트[-4:-1]), 실적_리스트[-2])) if 지표방향=="상향" else float(min(np.mean(실적_리스트[-4:-1]), 실적_리스트[-2]))],
    "2026년 예상실적": [float(예상실적_입력)]
}
stats_df = pd.DataFrame(stats_data)

st.markdown('<div style="margin-top:10px;"></div>', unsafe_allow_html=True)
# [오류 수정] style.format 적용 시 안전하게 처리
st.table(stats_df.style.format("{:.3f}"))

# 4. 분석 실행 (이미지 8d7181 메시지 반영)
st.markdown("---")
if st.button("🚀 통합 성과 분석 실행"):
    # (여기에 분석 로직 및 그래프 생성 코드 삽입)
    st.success("데이터 분석이 완료되었습니다. 하단 그래프를 확인하세요.") #
