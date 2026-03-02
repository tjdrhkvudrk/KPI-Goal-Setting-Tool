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
            with open(font_path, "wb") as f: f.write(res.content)
        except: pass
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        font_name = fm.FontProperties(fname=font_path).get_name()
        plt.rc('font', family=font_name)
    plt.rc('axes', unicode_minus=False)
    return font_path

font_file = load_korean_font()
font_prop = fm.FontProperties(fname=font_file) if font_file else None

# 2. CSS 스타일 정의
st.set_page_config(page_title="계량 성과지표 시뮬레이터", layout="wide")
st.markdown("""
<style>
    html, body, [class*="st-"] { font-size: 15px !important; font-family: 'NanumGothic', sans-serif; }
    .sidebar-label { font-size: 16px; font-weight: 800; color: #1A202C; margin-top: 15px; margin-bottom: 8px; display: block; }
    .sidebar-white-box { background-color: white; border-radius: 8px; padding: 12px; border: 1px solid #E2E8F0; margin-bottom: 5px; }
    div[data-testid="stNumberInput"] label, div[data-testid="stTextInput"] label, div[data-testid="stRadio"] > label { display: none !important; }
    .main-header { padding: 10px; color: white; text-align: center; font-weight: bold; margin-bottom: 5px; border-radius: 5px 5px 0 0; }
    .bg-past { background-color: #2D6A4F; }
    .bg-current { background-color: #D69E2E; }
    .bg-future { background-color: #4A5568; }
    .sub-header { background-color: #f1f3f5; padding: 5px; text-align: center; font-size: 13px; font-weight: bold; border: 1px solid #dee2e6; border-top: none; }
    .auto-res { background-color: #F8FAFC; border: 1px solid #dee2e6; height: 42px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; }
    .guide-box { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px; margin-top: 15px; line-height: 1.8; }
    thead tr th { background-color: #4A5568 !important; color: white !important; text-align: center !important; border: 1px solid #E2E8F0; }
    td { text-align: center !important; vertical-align: middle !important; border: 1px solid #E2E8F0; padding: 8px; }
    .merged-cell { background-color: #EDF2F7; font-weight: bold; color: #2D3748; width: 120px; }
    .strong-label { font-size: 20px !important; font-weight: 900 !important; color: #1A365D !important; margin-bottom: 12px; display: block; }
    
    .step-card { border-radius: 10px; padding: 15px; border-left: 5px solid; margin-bottom: 10px; background-color: #FFFFFF; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .step-1 { border-left-color: #E53E3E; } .step-2 { border-left-color: #DD6B20; }
    .step-3 { border-left-color: #38A169; } .step-4 { border-left-color: #A0AEC0; }
    
    /* 상하향 통합 산식 표 스타일 */
    .formula-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; background-color: white; }
    .formula-table th { border: 1px solid #E2E8F0; padding: 8px; text-align: center !important; }
    .formula-table td { border: 1px solid #E2E8F0; padding: 8px; text-align: left !important; }
    .up-col { background-color: #EBF8FF !important; color: #2B6CB0 !important; }
    .down-col { background-color: #FFF5F5 !important; color: #C53030 !important; }
</style>
""", unsafe_allow_html=True)

# 3. 사이드바 제어
with st.sidebar:
    st.markdown('<span class="sidebar-label">📌 지표명
